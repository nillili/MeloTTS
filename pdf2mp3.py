import fitz  # PyMuPDF
import re, sys, os
import gc
import torch
import logging
import datetime
import psutil  # 시스템 리소스 모니터링
import traceback
#from gtts import gTTS
from melo.api import TTS

# 전역 TTS 모델 인스턴스 (싱글톤 패턴)
_tts_model = None

# 로깅 설정
def setup_logging(log_file='pdf2mp3.log'):
    """
    상세한 로깅 설정
    파일과 콘솔에 동시 출력
    """
    # 로거 생성
    logger = logging.getLogger('pdf2mp3')
    logger.setLevel(logging.DEBUG)
    
    # 기존 핸들러 제거 (중복 방지)
    logger.handlers.clear()
    
    # 파일 핸들러 (상세 로그)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # 콘솔 핸들러 (간단한 로그)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 로거 초기화
logger = setup_logging()

def log_memory_status(location=""):
    """
    현재 메모리 상태를 로그에 기록
    """
    try:
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        mem_percent = process.memory_percent()
        
        # 시스템 전체 메모리
        virtual_mem = psutil.virtual_memory()
        
        log_msg = f"[MEMORY {location}] "
        log_msg += f"프로세스: {mem_info.rss / 1024 / 1024:.1f}MB ({mem_percent:.1f}%), "
        log_msg += f"시스템: {virtual_mem.used / 1024 / 1024:.1f}MB / {virtual_mem.total / 1024 / 1024:.1f}MB "
        log_msg += f"({virtual_mem.percent:.1f}% 사용)"
        
        logger.debug(log_msg)
        
        # 메모리 사용률이 90% 이상이면 경고
        if virtual_mem.percent > 90:
            logger.warning(f"⚠️  시스템 메모리 부족! {virtual_mem.percent:.1f}% 사용 중")
            
    except Exception as e:
        logger.error(f"메모리 상태 확인 오류: {e}")

def force_memory_cleanup():
    """
    강제 메모리 정리
    """
    logger.debug("[CLEANUP] 메모리 정리 시작")
    log_memory_status("BEFORE_CLEANUP")
    
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    
    log_memory_status("AFTER_CLEANUP")
    logger.debug("[CLEANUP] 메모리 정리 완료")

def get_tts_model(lang='KR', device='cpu'):
    """
    TTS 모델을 싱글톤 패턴으로 관리
    한 번만 로딩하고 재사용하여 메모리 절약
    """
    global _tts_model
    if _tts_model is None:
        # 모델 로딩 전 메모리 정리
        logger.info("TTS 모델 로딩 전 메모리 정리")
        force_memory_cleanup()
        
        print(f"TTS 모델 로딩 중... (언어: {lang}, 디바이스: {device})")
        print("⚠️  메모리가 부족한 경우 시간이 걸릴 수 있습니다...")
        logger.info(f"TTS 모델 로딩 중 (언어: {lang}, 디바이스: {device})")
        log_memory_status("BEFORE_TTS_INIT")
        _tts_model = TTS(language=lang, device=device)
        logger.info("TTS 모델 인스턴스 생성 완료")
        log_memory_status("AFTER_TTS_INIT")
        print("TTS 모델 로딩 완료!")
        
        # 로딩 후에도 메모리 정리
        logger.info("TTS 모델 로딩 후 메모리 정리")
        force_memory_cleanup()
    else:
        logger.debug("기존 TTS 모델 재사용")
    return _tts_model

def release_tts_model():
    """
    TTS 모델을 메모리에서 완전히 해제
    """
    global _tts_model
    if _tts_model is not None:
        logger.info("TTS 모델 메모리 해제 중")
        log_memory_status("BEFORE_MODEL_DELETE")
        del _tts_model
        _tts_model = None
        gc.collect()
        torch.cuda.empty_cache()  # GPU 사용 시를 위해
        logger.info("TTS 모델 메모리 해제 완료")
        log_memory_status("AFTER_MODEL_DELETE")
        print("TTS 모델 메모리 해제 완료")
    else:
        logger.debug("해제할 TTS 모델 없음")

def pdf_to_text(pdf_path):
    # PDF 파일에서 텍스트 추출
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
    return text

def save_text_to_file(text_content, filename="abc.txt", silent=False):
    """
    주어진 텍스트 내용을 지정된 파일로 저장합니다.

    Args:
        text_content (str): 파일에 저장할 텍스트 내용.
        filename (str, optional): 텍스트를 저장할 파일 이름. 기본값은 "abc.txt"입니다.
        silent (bool, optional): True면 성공 메시지를 출력하지 않음. 기본값은 False입니다.
    """
    try:
        # 'w' 모드로 파일을 엽니다.
        # 'w'는 쓰기 모드이며, 파일이 이미 존재하면 내용을 덮어씁니다.
        # 파일이 존재하지 않으면 새로 생성합니다.
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_content)
        if not silent:
            print(f"'{filename}' 파일에 텍스트가 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"파일을 저장하는 중 오류가 발생했습니다: {e}")


def pdf_to_mp3(pdf_path, mp3_path, start_num=0, lang='KR', device='cpu'):
    """
    PDF에서 텍스트를 추출한 후 MP3로 저장
    메모리 효율성을 위해:
    1. 청크를 먼저 모두 파일로 저장
    2. 파일을 하나씩 읽어서 MP3 생성
    3. 메모리에 모든 청크를 보관하지 않음
    """
    logger.info("="*60)
    logger.info(f"PDF to MP3 변환 시작: {pdf_path}")
    logger.info(f"출력: {mp3_path}, 시작: {start_num}, 언어: {lang}, 디바이스: {device}")
    logger.info("="*60)
    log_memory_status("START")
    
    # PDF에서 텍스트 추출
    print("\n[1단계] PDF에서 텍스트 추출 중...")
    logger.info("[1단계] PDF 텍스트 추출 시작")
    log_memory_status("BEFORE_PDF_EXTRACT")
    text = pdf_to_text(pdf_path)
    log_memory_status("AFTER_PDF_EXTRACT")
    if not text:
        logger.error("PDF 파일에서 텍스트를 추출하지 못했습니다.")
        print("PDF 파일에서 텍스트를 추출하지 못했습니다.")
        return
    
    logger.info(f"추출된 텍스트 길이: {len(text)} 문자")
    
    # 텍스트 전처리 및 분할
    print("\n" + "="*60)
    print("[2단계] 텍스트 전처리 및 분할")
    print("="*60)
    logger.info("[2단계] 텍스트 전처리 시작")
    log_memory_status("BEFORE_TEXT_PROCESS")
    
    # 특수문자 정리
    text = switch_txt(text)
    logger.info("텍스트 정리 완료")
    
    # ignores.txt에서 반복 문장 제거
    ignore_patterns = load_ignore_patterns('ignores.txt')
    if ignore_patterns:
        print(f"\n📝 제외 패턴 목록 (ignores.txt):")
        print("-" * 60)
        for i, pattern in enumerate(ignore_patterns, 1):
            # 패턴이 너무 길면 줄임
            display_pattern = pattern if len(pattern) <= 50 else pattern[:47] + "..."
            print(f"  {i}. '{display_pattern}'")
        print("-" * 60)
        print(f"총 {len(ignore_patterns)}개 패턴 적용\n")
        
        logger.info(f"ignores.txt 적용: {len(ignore_patterns)}개 패턴")
        
        # 패턴 제거 실행
        text, removal_stats = remove_ignore_patterns(text, ignore_patterns)
        
        # 제거 결과 출력
        if removal_stats:
            print("🗑️  제거된 반복 문장:")
            print("-" * 60)
            total_removed = 0
            for pattern, count in removal_stats.items():
                display_pattern = pattern if len(pattern) <= 40 else pattern[:37] + "..."
                print(f"  • '{display_pattern}': {count}회 제거")
                total_removed += count
            print("-" * 60)
            print(f"✓ 총 {total_removed}개 반복 문장 제거됨\n")
            logger.info(f"총 {total_removed}개 반복 문장 제거됨")
        else:
            print("ℹ️  제거된 문장 없음 (패턴이 텍스트에 없음)\n")
            logger.info("패턴과 일치하는 문장 없음")
    else:
        print("ℹ️  ignores.txt 파일 없음 - 모든 텍스트 유지\n")
        logger.info("ignores.txt 파일 없음")
    
    # 청크 분할
    print("📊 텍스트 청크 분할 중...")
    sp_txt = split_text(text)
    log_memory_status("AFTER_TEXT_SPLIT")
    
    total_chunks = len(sp_txt)
    logger.info(f"총 {total_chunks}개의 청크로 분할")
    print(f"✓ 총 {total_chunks}개의 청크로 분할되었습니다.\n")
    
    # 단계 2: 모든 청크를 파일로 저장 (메모리 해제를 위해)
    print(f"\n[3단계] 모든 청크를 파일로 저장 중...")
    logger.info("[3단계] 청크 파일 저장 시작")
    log_memory_status("BEFORE_SAVE_CHUNKS")
    for i, chunk_text in enumerate(sp_txt):
        chunk_filename = f"sptxt_{i}.txt"
        save_text_to_file(chunk_text, chunk_filename, silent=True)
        if i % 10 == 0:  # 10개마다 로그
            logger.debug(f"청크 {i}/{total_chunks} 저장 완료")
    logger.info(f"{total_chunks}개의 텍스트 파일 저장 완료")
    print(f"✓ {total_chunks}개의 텍스트 파일 저장 완료")
    
    # 메모리에서 청크 리스트 제거
    logger.info("청크 리스트를 메모리에서 해제")
    log_memory_status("BEFORE_DELETE_CHUNKS")
    del sp_txt
    del text
    force_memory_cleanup()
    logger.info("텍스트 데이터 메모리 해제 완료")
    print("✓ 메모리에서 텍스트 데이터 해제 완료")
    
    # 단계 3: TTS 모델 로딩
    print(f"\n[4단계] TTS 모델 로딩 중...")
    logger.info("[4단계] TTS 모델 로딩 시작")
    log_memory_status("BEFORE_TTS_LOAD")
    try:
        model = get_tts_model(lang=lang, device=device)
        logger.info("TTS 모델 로딩 완료")
        log_memory_status("AFTER_TTS_LOAD")
        speaker_ids = model.hps.data.spk2id
        speed = 1.25
        
        # 단계 4: 파일을 하나씩 읽어서 MP3 생성
        print(f"\n[5단계] MP3 파일 생성 시작 (시작 번호: {start_num})")
        logger.info(f"[5단계] MP3 생성 시작 (총 {total_chunks}개, 시작: {start_num})")
        print("=" * 60)
        
        for i in range(start_num, total_chunks):
            logger.info(f"\n{'='*60}")
            logger.info(f"청크 {i+1}/{total_chunks} 처리 시작")
            log_memory_status(f"BEFORE_CHUNK_{i}")
            print(f"\n▶ 처리 중: [{i+1}/{total_chunks}] 청크")
            
            # 파일에서 텍스트 읽기
            chunk_filename = f"sptxt_{i}.txt"
            try:
                logger.debug(f"파일 읽기: {chunk_filename}")
                with open(chunk_filename, 'r', encoding='utf-8') as f:
                    chunk_text = f.read()
                logger.debug(f"청크 텍스트 길이: {len(chunk_text)} 문자")
            except FileNotFoundError:
                logger.error(f"파일을 찾을 수 없습니다: {chunk_filename}")
                print(f"⚠️  파일을 찾을 수 없습니다: {chunk_filename}")
                continue
            
            # MP3 파일명 생성
            mp3_file_name = f"{mp3_path}_{i:02d}.mp3"
            logger.info(f"MP3 생성 시작: {mp3_file_name}")
            
            # 음성 변환
            print(f"  - 음성 변환 중...")
            log_memory_status(f"BEFORE_TTS_CHUNK_{i}")
            try:
                text_to_mp3_optimized(model, speaker_ids, chunk_text, mp3_file_name, speed, lang)
                logger.info(f"MP3 생성 완료: {mp3_file_name}")
                log_memory_status(f"AFTER_TTS_CHUNK_{i}")
            except Exception as tts_error:
                logger.error(f"TTS 변환 오류 (청크 {i}): {tts_error}")
                logger.error(traceback.format_exc())
                raise
            
            # 처리 완료
            print(f"  ✓ 완료: {mp3_file_name}")
            
            # 청크 텍스트 메모리 해제
            logger.debug("청크 텍스트 메모리 해제")
            del chunk_text
            
            # 각 청크 처리 후 메모리 정리
            logger.debug("청크 처리 후 메모리 정리")
            force_memory_cleanup()
            logger.info(f"청크 {i+1} 완료")
            log_memory_status(f"AFTER_CLEANUP_CHUNK_{i}")
            
        print("\n" + "=" * 60)
        print("✓ 모든 MP3 파일 생성 완료!")
        logger.info("="*60)
        logger.info("모든 MP3 파일 생성 완료")
        log_memory_status("ALL_DONE")
            
    except Exception as e:
        logger.error(f"\n❌ 치명적 오류 발생: {e}")
        logger.error(traceback.format_exc())
        log_memory_status("ERROR_STATE")
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 모든 작업 완료 후 모델 해제
        logger.info("TTS 모델 해제 시작")
        log_memory_status("BEFORE_RELEASE")
        release_tts_model()
        logger.info("TTS 모델 해제 완료")
        log_memory_status("AFTER_RELEASE")
        print("\n[최종] 모든 작업이 완료되었습니다.")
        logger.info("[최종] 프로그램 종료")

def text_to_mp3_optimized(model, speaker_ids, text, mp3_path, speed=1.25, lang='KR'):
    """
    최적화된 텍스트-음성 변환 함수
    이미 로딩된 모델을 재사용하여 메모리 절약
    
    Args:
        model: 이미 로딩된 TTS 모델 인스턴스
        speaker_ids: 스피커 ID 딕셔너리
        text: 변환할 텍스트
        mp3_path: 저장할 MP3 파일 경로
        speed: 재생 속도
        lang: 언어 코드
    """
    try:
        logger.debug(f"TTS 변환 시작: {len(text)} 문자 -> {mp3_path}")
        log_memory_status("BEFORE_TTS_CALL")
        model.tts_to_file(text, speaker_ids[lang], mp3_path, speed=speed, quiet=True)
        log_memory_status("AFTER_TTS_CALL")
        logger.debug(f"TTS 변환 완료: {mp3_path}")
    except Exception as e:
        logger.error(f"음성 변환 중 오류 발생: {e}")
        logger.error(traceback.format_exc())
        print(f"음성 변환 중 오류 발생: {e}")
        raise

def text_to_mp3(text, mp3_path, lang):
    """
    기존 호환성을 위한 레거시 함수
    (사용 권장하지 않음 - text_to_mp3_optimized 사용 권장)
    """
    speed = 1.25
    device = 'cpu'
    
    model = TTS(language='KR', device=device)
    speaker_ids = model.hps.data.spk2id
    
    model.tts_to_file(text, speaker_ids['KR'], mp3_path, speed=speed)

def split_text(text, max_length=2000, split_pattern=r'니다\.|습니다\.|었다\.|한다\.|였다\.'):
    """
    긴 텍스트를 지정된 최대 길이 이내에서 문장 끝을 기준으로 분리합니다.

    Args:
        text (str): 분리할 원본 텍스트.
        max_length (int): 각 청크의 최대 길이.
        split_pattern (str): 문장 끝을 나타내는 정규 표현식 패턴.
                             '니다.' 또는 '다.' 등 한글 문장의 종결 어미를 포함합니다.
                             마지막에 '\s'를 추가하여 공백으로도 분리될 수 있도록 합니다.

    Returns:
        list: 분리된 텍스트 청크를 담은 리스트.
    """
    chunks = []
    current_chunk = []
    current_length = 0

    # 문장을 분리하되, 분리 기준이 되는 구분자도 함께 유지
    # re.split은 구분자를 제거하므로, re.finditer를 사용하거나
    # lookbehind/lookahead assertion을 활용하여 구분자를 포함하도록 처리
    # 여기서는 간단히 구분자로 분리 후 다시 합치는 방식을 사용
    
    # 문장 단위로 우선 분리 (구분자를 포함하여 분리)
    # 긍정형 후방 탐색을 사용하여 구분자를 포함
    sentences = re.split(f'({split_pattern})', text)

    # re.split이 빈 문자열을 만들 수 있으므로 필터링
    sentences = [s for s in sentences if s]

    # 분리된 문장들을 다시 합쳐서 청크 생성
    for i in range(0, len(sentences), 2): # 문장과 구분자가 번갈아 나오므로 2칸씩 점프
        sentence_part = sentences[i]
        delimiter = sentences[i+1] if i+1 < len(sentences) else ''
        
        # 현재 문장(구분자 포함)의 길이
        segment = sentence_part + delimiter
        segment_length = len(segment)

        # 현재 청크에 추가했을 때 max_length를 초과하는지 확인
        if current_length + segment_length <= max_length:
            current_chunk.append(segment)
            current_length += segment_length
        else:
            # max_length를 초과하면 현재까지의 청크를 저장하고 새 청크 시작
            if current_chunk: # 현재 청크가 비어있지 않으면 저장
                chunks.append("".join(current_chunk).strip())
            
            # 새 청크에 현재 문장 추가
            current_chunk = [segment]
            current_length = segment_length

            # 만약 단일 문장 자체가 max_length를 초과하는 경우 (매우 긴 문장)
            # 이 경우에는 어쩔 수 없이 max_length에서 강제 분리해야 합니다.
            # 이 시나리오를 처리하는 고급 로직이 필요할 수 있으나,
            # 여기서는 편의상 그대로 넣어두고, 필요시 `split_long_segment` 함수 등을 추가합니다.
            if segment_length > max_length:
                # 단일 문장이 max_length를 초과하면 강제로 분할
                print(f"경고: {segment_length} 길이의 단일 문장이 최대 길이({max_length})를 초과하여 강제 분할될 수 있습니다.")
                # 이 부분을 재귀적으로 처리하거나, 단순 잘라내기 로직 추가
                # 여기서는 일단 그대로 current_chunk에 넣고 다음 반복에서 처리되도록 함
                # (실제로는 이럴 경우 해당 segment를 max_length로 자르고 나머지를 다음으로 넘기는 로직이 필요)
                # 간략화를 위해 현재는 단일 긴 문장이 그대로 들어갈 수 있음을 알림.
                # 실제 배포 시에는 더 견고한 처리가 필요함.
                # 예를 들어, 이 segment 자체를 max_length 단위로 쪼개는 보조 함수 호출

    # 마지막 남은 청크 저장
    if current_chunk:
        chunks.append("".join(current_chunk).strip())

    # 만약 split_pattern에 해당하지 않는, 매우 긴 연속된 텍스트가 있으면
    # 해당 텍스트는 max_length를 초과하여 청크에 포함될 수 있습니다.
    # 이를 방지하려면 `split_pattern`에 공백 문자나 다른 최소한의 분리 기준을 추가하거나,
    # `segment_length > max_length` 케이스에서 강제 분할 로직을 더 강화해야 합니다.
    # 현재 split_pattern에 '\s'를 추가하여 어느 정도 공백 기준으로도 분리되도록 했습니다.

    # 최종적으로 각 청크가 max_length를 초과하지 않는지 확인하는 방어 코드
    final_chunks = []
    for chunk in chunks:
        while len(chunk) > max_length:
            # 13000자 근처에서 마지막 "니다."를 찾기
            # 뒤에서부터 검색하여 가장 적절한 분리점 찾기
            
            # max_length 근처의 윈도우에서 '니다.' 찾기
            search_window_start = max(0, max_length - 500) # 13000자에서 500자 앞부터 검색
            search_window_end = min(len(chunk), max_length + 50) # 13000자에서 50자 뒤까지 검색 (넉넉하게)

            sub_string = chunk[search_window_start:search_window_end]
            
            # 뒤에서부터 문장 종결 패턴 찾기
            # re.finditer를 역순으로 찾아 가장 마지막에 나오는 패턴 사용
            best_split_idx = -1
            found_match_length = 0
            
            # 패턴을 역순으로 찾기 위해, 문자열을 뒤집고 패턴도 뒤집어서 검색
            reversed_sub_string = sub_string[::-1]
            reversed_split_pattern = split_pattern[::-1] # 패턴도 뒤집기

            # 단순 패턴 뒤집기는 복잡하므로, 여기서는 원래 패턴으로 search_window 내에서 마지막 일치 항목 찾기
            # 13000자 언저리에서 가장 마지막으로 발견되는 '니다.' 등의 패턴을 찾음
            matches = list(re.finditer(split_pattern, sub_string))
            
            temp_split_point = -1 # sub_string 내에서의 인덱스
            
            for m in reversed(matches):
                # m.end()는 패턴 끝 다음 인덱스
                # 실제 청크 내의 인덱스는 search_window_start + m.end()
                actual_end_index_in_chunk = search_window_start + m.end()
                
                # 이 분리점이 max_length보다 작거나 같으면서 (너무 길어지지 않게),
                # 그리고 최소 길이(예: max_length - 1000)보다는 큰 지점
                # 이 조건은 복잡해질 수 있으니, 간단히 max_length 근처에서 찾도록.
                
                if actual_end_index_in_chunk <= max_length + 10: # 13000자 + 10자 이내 허용
                     temp_split_point = actual_end_index_in_chunk
                     break # 뒤에서부터 찾았으므로 가장 적합한 마지막 지점

            if temp_split_point != -1:
                # 찾은 분리점에서 자르기
                final_chunks.append(chunk[:temp_split_point].strip())
                chunk = chunk[temp_split_point:].strip()
            else:
                # 적절한 '니다.' 패턴을 찾지 못했다면, max_length에서 강제 분할
                final_chunks.append(chunk[:max_length].strip())
                chunk = chunk[max_length:].strip()
        
        # 남은 최종 청크 추가
        if chunk:
            final_chunks.append(chunk.strip())

    return final_chunks

def load_ignore_patterns(ignore_file='ignores.txt'):
    """
    ignores.txt 파일에서 제거할 문장 패턴 로드
    
    Args:
        ignore_file (str): 무시할 패턴이 저장된 파일 경로
        
    Returns:
        list: 제거할 문장 리스트 (빈 리스트면 파일 없음)
    """
    if not os.path.exists(ignore_file):
        logger.debug(f"ignores.txt 파일 없음: {ignore_file}")
        return []
    
    patterns = []
    try:
        with open(ignore_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 빈 줄이나 주석은 무시
                if line and not line.startswith('#'):
                    patterns.append(line)
        
        if patterns:
            logger.info(f"ignores.txt 로드 완료: {len(patterns)}개 패턴")
            for i, pattern in enumerate(patterns, 1):
                logger.debug(f"  패턴 {i}: '{pattern}'")
        else:
            logger.info("ignores.txt 파일이 비어있음")
            
    except Exception as e:
        logger.error(f"ignores.txt 읽기 오류: {e}")
        return []
    
    return patterns


def remove_ignore_patterns(text, patterns):
    """
    텍스트에서 지정된 패턴 제거
    
    Args:
        text (str): 원본 텍스트
        patterns (list): 제거할 문장 리스트
        
    Returns:
        tuple: (정리된 텍스트, 제거 통계 딕셔너리)
    """
    if not patterns:
        return text, {}
    
    original_text = text
    removal_stats = {}  # 패턴별 제거 횟수
    total_removed = 0
    
    for pattern in patterns:
        # 패턴을 정규식으로 이스케이프 (특수문자 처리)
        escaped_pattern = re.escape(pattern)
        
        # 대소문자 구분 없이, 전후 공백 무시하고 매칭
        # \s*는 공백 0개 이상을 의미
        regex_pattern = r'\s*' + escaped_pattern + r'\s*'
        
        # 매칭된 횟수 카운트
        matches = re.findall(regex_pattern, text, re.IGNORECASE)
        match_count = len(matches)
        
        if match_count > 0:
            removal_stats[pattern] = match_count
            total_removed += match_count
            logger.debug(f"패턴 '{pattern}' 제거: {match_count}회")
        
        # 패턴 제거
        text = re.sub(regex_pattern, '', text, flags=re.IGNORECASE)
    
    if total_removed > 0:
        logger.info(f"총 {total_removed}개 반복 문장 제거됨")
        logger.debug(f"텍스트 길이: {len(original_text)} → {len(text)} ({len(original_text) - len(text)} 문자 감소)")
    
    return text, removal_stats


def switch_txt(text):
    clean_text = re.sub(r'[<>《》=ㅅ;&ㅁㅇㄴ|+#$@}ㅆ{ㄱㄹㅂㅊㄷㅈ]', '', text)
    return clean_text


def is_pdf_converted(pdf_path):
    """
    PDF 파일이 이미 MP3로 변환되었는지 확인
    청크 0번 파일(sptxt_0.txt 또는 *_00.mp3)이 존재하면 변환된 것으로 간주
    
    Args:
        pdf_path (str): PDF 파일 경로
        
    Returns:
        bool: 변환 완료 여부
    """
    pdf_dir = os.path.dirname(pdf_path) or '.'
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 체크할 파일들
    check_files = [
        os.path.join(pdf_dir, f"{base_name}_00.mp3"),  # 첫 번째 MP3 파일
        os.path.join(pdf_dir, "sptxt_0.txt")  # 첫 번째 텍스트 청크
    ]
    
    # 하나라도 존재하면 변환된 것으로 간주
    for check_file in check_files:
        if os.path.exists(check_file):
            logger.info(f"이미 변환됨: {pdf_path} (확인 파일: {check_file})")
            return True
    
    return False


def find_pdf_files(directory):
    """
    디렉토리에서 변환되지 않은 PDF 파일 목록 반환
    
    Args:
        directory (str): 검색할 디렉토리 경로
        
    Returns:
        list: 변환되지 않은 PDF 파일 경로 리스트
    """
    if not os.path.isdir(directory):
        logger.error(f"디렉토리가 아닙니다: {directory}")
        return []
    
    pdf_files = []
    
    # 디렉토리 내 모든 PDF 파일 찾기
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            
            # 이미 변환된 파일인지 확인
            if not is_pdf_converted(pdf_path):
                pdf_files.append(pdf_path)
                logger.info(f"변환 대기: {pdf_path}")
            else:
                logger.info(f"변환 완료(스킵): {pdf_path}")
    
    return sorted(pdf_files)  # 파일명 정렬


def batch_convert_pdfs(directory, lang='KR', device='cpu'):
    """
    디렉토리 내의 모든 미변환 PDF를 MP3로 배치 변환
    
    Args:
        directory (str): PDF 파일들이 있는 디렉토리
        lang (str): 언어 코드 (기본값: 'KR')
        device (str): 디바이스 (기본값: 'cpu')
    """
    logger.info("="*60)
    logger.info(f"배치 변환 시작: {directory}")
    logger.info("="*60)
    
    print("\n" + "="*60)
    print(f"📁 배치 변환 모드")
    print("="*60)
    print(f"대상 디렉토리: {directory}")
    print(f"언어: {lang}, 디바이스: {device}")
    print("="*60 + "\n")
    
    # 변환할 PDF 파일 목록 수집
    pdf_files = find_pdf_files(directory)
    
    if not pdf_files:
        print("⚠️  변환할 PDF 파일이 없습니다.")
        print("   - 이미 모든 파일이 변환되었거나")
        print("   - 디렉토리에 PDF 파일이 없습니다.")
        logger.info("변환할 PDF 없음")
        return
    
    total_files = len(pdf_files)
    print(f"✓ 변환 대상: {total_files}개 파일\n")
    logger.info(f"총 {total_files}개 PDF 파일 변환 예정")
    
    # 각 PDF 파일 변환
    success_count = 0
    failed_files = []
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        base_name = os.path.splitext(filename)[0]
        pdf_dir = os.path.dirname(pdf_path)
        
        print("\n" + "="*60)
        print(f"📄 [{idx}/{total_files}] {filename}")
        print("="*60)
        logger.info(f"[{idx}/{total_files}] 변환 시작: {pdf_path}")
        
        try:
            # 출력 경로는 PDF와 같은 디렉토리에 저장
            # 현재 작업 디렉토리를 PDF 디렉토리로 변경
            original_dir = os.getcwd()
            os.chdir(pdf_dir)
            
            logger.info(f"작업 디렉토리 변경: {pdf_dir}")
            
            # MP3 변환 (상대 경로 사용)
            pdf_to_mp3(filename, base_name, start_num=0, lang=lang, device=device)
            
            # 원래 디렉토리로 복귀
            os.chdir(original_dir)
            
            success_count += 1
            print(f"\n✅ [{idx}/{total_files}] 완료: {filename}")
            logger.info(f"[{idx}/{total_files}] 변환 완료: {pdf_path}")
            
        except Exception as e:
            # 원래 디렉토리로 복귀
            os.chdir(original_dir)
            
            failed_files.append((filename, str(e)))
            print(f"\n❌ [{idx}/{total_files}] 실패: {filename}")
            print(f"   오류: {e}")
            logger.error(f"[{idx}/{total_files}] 변환 실패: {pdf_path}")
            logger.error(f"오류 내용: {e}")
            logger.error(traceback.format_exc())
            
            # 실패해도 다음 파일 계속 처리
            continue
    
    # 최종 결과 출력
    print("\n" + "="*60)
    print("📊 배치 변환 완료")
    print("="*60)
    print(f"✓ 성공: {success_count}/{total_files}")
    if failed_files:
        print(f"✗ 실패: {len(failed_files)}/{total_files}")
        print("\n실패한 파일:")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")
    print("="*60)
    
    logger.info("="*60)
    logger.info(f"배치 변환 완료: 성공 {success_count}/{total_files}")
    if failed_files:
        logger.warning(f"실패: {len(failed_files)}개")
        for filename, error in failed_files:
            logger.warning(f"  - {filename}: {error}")
    logger.info("="*60)


# 사용 예시
# pdf_path = '2025061401.pdf'  # PDF 파일 경로
# mp3_path = 'output_01.mp3'   # 생성될 MP3 파일 경로
# file_name = input("파일명:")


if len(sys.argv) > 1:
    filepath = sys.argv[1]
    
    # 디렉토리인지 파일인지 확인
    if os.path.isdir(filepath):
        # 디렉토리 배치 처리 모드
        device = 'cpu'
        if len(sys.argv) > 2:
            device = sys.argv[2]  # 예: 'cuda' 또는 'cuda:0'
        
        batch_convert_pdfs(filepath, lang='KR', device=device)
        
    else:
        # 단일 파일 처리 모드
        if len(sys.argv) > 2:
            start_num = int(sys.argv[2])
        else: 
            start_num = 0
        
        # 디바이스 설정 (선택적 파라미터)
        device = 'cpu'
        if len(sys.argv) > 3:
            device = sys.argv[3]  # 예: 'cuda' 또는 'cuda:0'

        filename = os.path.basename(filepath)
        name, _ = os.path.splitext(filename) 
        
        # 파일이 위치한 디렉토리로 이동
        file_dir = os.path.dirname(filepath) or '.'
        original_dir = os.getcwd()
        os.chdir(file_dir)

        print(f"=" * 60)
        print(f"PDF to MP3 변환 시작")
        print(f"=" * 60)
        print(f"입력 파일: {filepath}")
        print(f"출력 이름: {name}")
        print(f"시작 번호: {start_num}")
        print(f"디바이스: {device}")
        print(f"=" * 60)
        
        pdf_to_mp3(filename, name, start_num, lang='KR', device=device)
        
        # 원래 디렉토리로 복귀
        os.chdir(original_dir)
else:
    print("사용법:")
    print("  단일 파일: python pdf2mp3.py <pdf파일> [시작번호] [디바이스]")
    print("  배치 처리: python pdf2mp3.py <디렉토리> [디바이스]")
    print()
    print("예시:")
    print("  python pdf2mp3.py document.pdf")
    print("  python pdf2mp3.py document.pdf 5")
    print("  python pdf2mp3.py document.pdf 0 cuda")
    print("  python pdf2mp3.py ./pdf")
    print("  python pdf2mp3.py ./pdf cpu")


