import fitz  # PyMuPDF
import re, sys, os
import gc
import torch
#from gtts import gTTS
from melo.api import TTS

# 전역 TTS 모델 인스턴스 (싱글톤 패턴)
_tts_model = None

def force_memory_cleanup():
    """
    강제 메모리 정리
    """
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

def get_tts_model(lang='KR', device='cpu'):
    """
    TTS 모델을 싱글톤 패턴으로 관리
    한 번만 로딩하고 재사용하여 메모리 절약
    """
    global _tts_model
    if _tts_model is None:
        # 모델 로딩 전 메모리 정리
        force_memory_cleanup()
        
        print(f"TTS 모델 로딩 중... (언어: {lang}, 디바이스: {device})")
        print("⚠️  메모리가 부족한 경우 시간이 걸릴 수 있습니다...")
        _tts_model = TTS(language=lang, device=device)
        print("TTS 모델 로딩 완료!")
        
        # 로딩 후에도 메모리 정리
        force_memory_cleanup()
    return _tts_model

def release_tts_model():
    """
    TTS 모델을 메모리에서 완전히 해제
    """
    global _tts_model
    if _tts_model is not None:
        del _tts_model
        _tts_model = None
        gc.collect()
        torch.cuda.empty_cache()  # GPU 사용 시를 위해
        print("TTS 모델 메모리 해제 완료")

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
    # PDF에서 텍스트 추출
    print("\n[1단계] PDF에서 텍스트 추출 중...")
    text = pdf_to_text(pdf_path)
    if not text:
        print("PDF 파일에서 텍스트를 추출하지 못했습니다.")
        return
    
    # 텍스트 전처리 및 분할
    print("[2단계] 텍스트 전처리 및 분할 중...")
    text = switch_txt(text)
    sp_txt = split_text(text)
    
    total_chunks = len(sp_txt)
    print(f"✓ 총 {total_chunks}개의 청크로 분할되었습니다.")
    
    # 단계 2: 모든 청크를 파일로 저장 (메모리 해제를 위해)
    print(f"\n[3단계] 모든 청크를 파일로 저장 중...")
    for i, chunk_text in enumerate(sp_txt):
        chunk_filename = f"sptxt_{i}.txt"
        save_text_to_file(chunk_text, chunk_filename, silent=True)
    print(f"✓ {total_chunks}개의 텍스트 파일 저장 완료")
    
    # 메모리에서 청크 리스트 제거
    del sp_txt
    del text
    force_memory_cleanup()
    print("✓ 메모리에서 텍스트 데이터 해제 완료")
    
    # 단계 3: TTS 모델 로딩
    print(f"\n[4단계] TTS 모델 로딩 중...")
    try:
        model = get_tts_model(lang=lang, device=device)
        speaker_ids = model.hps.data.spk2id
        speed = 1.25
        
        # 단계 4: 파일을 하나씩 읽어서 MP3 생성
        print(f"\n[5단계] MP3 파일 생성 시작 (시작 번호: {start_num})")
        print("=" * 60)
        
        for i in range(start_num, total_chunks):
            print(f"\n▶ 처리 중: [{i+1}/{total_chunks}] 청크")
            
            # 파일에서 텍스트 읽기
            chunk_filename = f"sptxt_{i}.txt"
            try:
                with open(chunk_filename, 'r', encoding='utf-8') as f:
                    chunk_text = f.read()
            except FileNotFoundError:
                print(f"⚠️  파일을 찾을 수 없습니다: {chunk_filename}")
                continue
            
            # MP3 파일명 생성
            mp3_file_name = f"{mp3_path}_{i:02d}.mp3"
            
            # 음성 변환
            print(f"  - 음성 변환 중...")
            text_to_mp3_optimized(model, speaker_ids, chunk_text, mp3_file_name, speed, lang)
            
            # 처리 완료
            print(f"  ✓ 완료: {mp3_file_name}")
            
            # 청크 텍스트 메모리 해제
            del chunk_text
            
            # 각 청크 처리 후 메모리 정리
            force_memory_cleanup()
            
        print("\n" + "=" * 60)
        print("✓ 모든 MP3 파일 생성 완료!")
            
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 모든 작업 완료 후 모델 해제
        release_tts_model()
        print("\n[최종] 모든 작업이 완료되었습니다.")

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
        model.tts_to_file(text, speaker_ids[lang], mp3_path, speed=speed, quiet=True)
    except Exception as e:
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

def switch_txt(text):
    clean_text = re.sub(r'[<>《》=ㅅ;&ㅁㅇㄴ|+#$@}ㅆ{ㄱㄹㅂㅊㄷㅈ]', '', text)
    return clean_text


# 사용 예시
# pdf_path = '2025061401.pdf'  # PDF 파일 경로
# mp3_path = 'output_01.mp3'   # 생성될 MP3 파일 경로
# file_name = input("파일명:")


if len(sys.argv) > 1:
    filepath = sys.argv[1]
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

    print(f"=" * 60)
    print(f"PDF to MP3 변환 시작")
    print(f"=" * 60)
    print(f"입력 파일: {filepath}")
    print(f"출력 이름: {name}")
    print(f"시작 번호: {start_num}")
    print(f"디바이스: {device}")
    print(f"=" * 60)
    
    pdf_to_mp3(filepath, name, start_num, lang='KR', device=device)

