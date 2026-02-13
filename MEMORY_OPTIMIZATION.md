# PDF2MP3 메모리 최적화 개선 사항

## 문제점 분석

### 기존 문제
- **"죽었음(Killed)" 오류**: OOM(Out Of Memory) Killer에 의한 프로세스 강제 종료
- **1GB 제한 환경**에서 메모리 부족 현상 발생
- 가끔씩 처리 중 프로그램이 예기치 않게 종료

### 원인 분석
1. **TTS 모델 중복 로딩** (가장 심각)
   - 각 청크마다 새로운 TTS 모델 인스턴스 생성 (300-500MB)
   - 이전 모델이 완전히 해제되기 전에 새 모델 로딩
   
2. **오디오 데이터 누적**
   - audio_list에 모든 오디오 세그먼트 저장
   - 메모리에 계속 누적되어 크기 증가

3. **불완전한 메모리 해제**
   - 중간 변수들이 적시에 삭제되지 않음
   - CPU 모드에서 torch.cuda.empty_cache()는 무의미

## 해결 방법

### 1. 싱글톤 패턴 적용 (pdf2mp3.py)

```python
# 전역 TTS 모델 인스턴스 (싱글톤 패턴)
_tts_model = None

def get_tts_model(lang='KR', device='cpu'):
    """
    TTS 모델을 싱글톤 패턴으로 관리
    한 번만 로딩하고 재사용하여 메모리 절약
    """
    global _tts_model
    if _tts_model is None:
        print(f"TTS 모델 로딩 중... (언어: {lang}, 디바이스: {device})")
        _tts_model = TTS(language=lang, device=device)
        print("TTS 모델 로딩 완료!")
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
        torch.cuda.empty_cache()
        print("TTS 모델 메모리 해제 완료")
```

**효과**: 
- 모델을 한 번만 로딩하여 300-500MB 메모리 절약
- 각 청크 처리 시 기존 모델 재사용

### 2. 개선된 변환 함수 (pdf2mp3.py)

```python
def text_to_mp3_optimized(model, speaker_ids, text, mp3_path, speed=1.25, lang='KR'):
    """
    최적화된 텍스트-음성 변환 함수
    이미 로딩된 모델을 재사용하여 메모리 절약
    """
    try:
        model.tts_to_file(text, speaker_ids[lang], mp3_path, speed=speed, quiet=True)
    except Exception as e:
        print(f"음성 변환 중 오류 발생: {e}")
        raise
```

**효과**: 
- 모델 인스턴스를 파라미터로 전달받아 재사용
- 불필요한 모델 생성 방지

### 3. 메모리 해제 강화 (melo/api.py)

```python
# 루프 내 명시적 삭제
audio_list.append(audio)
del audio  # 명시적 삭제

# 최종 메모리 정리
if torch.cuda.is_available():
    torch.cuda.empty_cache()

audio = self.audio_numpy_concat(audio_list, sr=self.hps.data.sampling_rate, speed=speed)

# audio_list 메모리 해제
del audio_list

# 파일 저장 후 메모리 해제
if output_path is not None:
    soundfile.write(output_path, audio, self.hps.data.sampling_rate, format=format)
    del audio
```

**효과**: 
- 사용 후 즉시 변수 삭제
- 불필요한 메모리 점유 최소화

### 4. 향상된 에러 처리 (pdf2mp3.py)

```python
try:
    # TTS 모델을 한 번만 로딩 (메모리 최적화)
    model = get_tts_model(lang=lang, device=device)
    speaker_ids = model.hps.data.spk2id
    
    for i, c_text in enumerate(sp_txt[start_num:], start=start_num):
        # ... 처리 ...
        gc.collect()
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
finally:
    # 모든 작업 완료 후 모델 해제
    release_tts_model()
    print("\n모든 작업이 완료되었습니다.")
```

**효과**: 
- 예외 발생 시에도 모델 메모리 해제 보장
- 프로그램 종료 전 리소스 정리

## 예상 효과

### 메모리 사용량 비교

| 항목 | 기존 | 개선 후 | 절감 |
|------|------|---------|------|
| 모델 로딩 | 청크당 300-500MB | 한 번만 300-500MB | 최대 90% |
| 오디오 누적 | 100-200MB | 100-200MB | 동일 |
| 중간 변수 | ~50MB | ~20MB | 60% |
| **총합** | **900MB~1.2GB** | **500MB~800MB** | **30-40%** |

### 안정성 향상
- ✅ OOM Killer 발동 가능성 대폭 감소
- ✅ 긴 PDF 처리 시 안정성 향상
- ✅ 리소스 정리 보장

## 사용 방법

### 방법 1: 메모리 최적화 스크립트 사용 (권장)

```bash
# 메모리 최적화 모드로 실행
./run_pdf2mp3.sh document.pdf

# 특정 청크부터 시작
./run_pdf2mp3.sh document.pdf 5

# GPU 사용 (선택사항)
./run_pdf2mp3.sh document.pdf 0 cuda
```

### 방법 2: 직접 실행 (기존 방법)

```bash
# 기본 사용
python3 pdf2mp3.py document.pdf

# 특정 청크부터 시작
python3 pdf2mp3.py document.pdf 5

# GPU 사용 (선택사항)
python3 pdf2mp3.py document.pdf 0 cuda
```

## 추가 개선 사항 (v2.1)

1. **텍스트 분할 크기 조정**
   - 3000자 → 2000자로 감소
   - 메모리 부족 환경에 최적화

2. **강제 메모리 정리 함수**
   - `force_memory_cleanup()` 추가
   - 모델 로딩 전/후 메모리 정리
   - 각 청크 처리 후 메모리 정리

3. **메모리 최적화 실행 스크립트**
   - `run_pdf2mp3.sh` 추가
   - 환경 변수 자동 설정
   - 병렬 처리 OFF (메모리 절약)
   - 스레드 수 제한 (메모리 절약)

4. **requirements.txt 추가**
   - 의존성 패키지 명시
   - 버전 관리 용이

5. **에러 메시지 개선**
   - 진행 상황 표시 강화
   - 문제 발생 시 상세한 정보 제공

6. **코드 문서화**
   - 각 함수에 Docstring 추가
   - 매개변수 설명 포함

## 테스트 방법

```bash
# 메모리 최적화 테스트
python3 test_memory_optimization.py

# 실제 PDF 변환 테스트
python3 pdf2mp3.py test/sample.pdf
```

## 주의사항

1. **1GB 미만 환경**: 여전히 메모리 부족 가능
   - 해결: `run_pdf2mp3.sh` 스크립트 사용 (환경 변수 자동 설정)
   - 또는: 텍스트 분할 크기 줄이기 (현재 2000자로 설정됨)
   
2. **매우 긴 PDF**: 수백 페이지의 경우 주의 필요
   - 해결: 청크 단위로 나눠서 처리
   
3. **첫 번째 청크 실행 시 "죽었음" 발생**
   - 원인: BERT 모델 최초 로딩 시 메모리 부족
   - 해결: `run_pdf2mp3.sh` 사용 또는 swap 메모리 증가

4. **GPU 사용 시**: VRAM 상태 모니터링 권장
   - `nvidia-smi`로 확인

## 버전 정보

- **최적화 전**: v1.0 (메모리 누수 문제)
- **최적화 후**: v2.0 (싱글톤 패턴 + 메모리 관리 강화)
- **추가 최적화**: v2.1 (텍스트 분할 축소 + 강제 메모리 정리 + 실행 스크립트)
- **날짜**: 2026-02-13

---

**작성자**: GenSpark AI Developer
**프로젝트**: PDF to MP3 Converter
