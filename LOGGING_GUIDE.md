# PDF2MP3 로깅 가이드

## 📝 개요
프로그램 실행 중 상세한 로그를 파일에 기록하여, 시스템 다운 후에도 원인을 분석할 수 있습니다.

## 🔍 로그 기능

### 1. 로그 파일 위치
```
pdf2mp3.log
```
프로그램 실행 디렉토리에 자동으로 생성됩니다.

### 2. 로그 레벨
- **DEBUG**: 상세한 디버그 정보 (파일에만 기록)
  - 메모리 상태
  - 각 단계별 처리 상황
  - BERT 모델 로드
  - 문장별 처리 상황
  
- **INFO**: 일반 정보 (콘솔과 파일 모두)
  - 단계별 진행 상황
  - 청크 처리 상태
  - 완료 메시지

- **WARNING**: 경고 (콘솔과 파일 모두)
  - 메모리 사용률 90% 이상
  
- **ERROR**: 오류 (콘솔과 파일 모두)
  - 예외 발생
  - 파일 찾기 실패
  - 변환 오류

### 3. 메모리 모니터링
로그에는 다음 시점의 메모리 상태가 기록됩니다:

#### 전체 프로세스
- `START`: 프로그램 시작
- `BEFORE_PDF_EXTRACT`: PDF 추출 전
- `AFTER_PDF_EXTRACT`: PDF 추출 후
- `BEFORE_TEXT_PROCESS`: 텍스트 전처리 전
- `AFTER_TEXT_SPLIT`: 텍스트 분할 후
- `BEFORE_SAVE_CHUNKS`: 청크 저장 전
- `BEFORE_DELETE_CHUNKS`: 청크 삭제 전
- `BEFORE_TTS_LOAD`: TTS 모델 로드 전
- `AFTER_TTS_LOAD`: TTS 모델 로드 후
- `ALL_DONE`: 모든 작업 완료
- `ERROR_STATE`: 오류 발생 시
- `BEFORE_RELEASE`: 모델 해제 전
- `AFTER_RELEASE`: 모델 해제 후

#### 각 청크 처리
- `BEFORE_CHUNK_{i}`: 청크 i 처리 시작 전
- `BEFORE_TTS_CHUNK_{i}`: 청크 i TTS 변환 전
- `AFTER_TTS_CHUNK_{i}`: 청크 i TTS 변환 후
- `AFTER_CLEANUP_CHUNK_{i}`: 청크 i 메모리 정리 후

#### TTS 세부 동작
- `BEFORE_TTS_INIT`: TTS 모델 초기화 전
- `AFTER_TTS_INIT`: TTS 모델 초기화 후
- `BEFORE_TTS_CALL`: TTS 변환 호출 전
- `AFTER_TTS_CALL`: TTS 변환 호출 후
- `BEFORE_MODEL_DELETE`: 모델 삭제 전
- `AFTER_MODEL_DELETE`: 모델 삭제 후

### 4. 로그 포맷
```
2026-02-13 01:45:23 [DEBUG] [MEMORY START] 프로세스: 120.5MB (12.2%), 시스템: 850.3MB / 987.0MB (86.1% 사용)
2026-02-13 01:45:25 [INFO] [1단계] PDF 텍스트 추출 시작
2026-02-13 01:45:30 [INFO] 추출된 텍스트 길이: 65432 문자
2026-02-13 01:45:35 [INFO] [2단계] 텍스트 전처리 시작
2026-02-13 01:45:40 [DEBUG] [MEMORY AFTER_TEXT_SPLIT] 프로세스: 180.2MB (18.3%), 시스템: 880.5MB / 987.0MB (89.2% 사용)
2026-02-13 01:45:40 [INFO] 총 41개의 청크로 분할
...
2026-02-13 01:50:15 [WARNING] ⚠️  시스템 메모리 부족! 92.5% 사용 중
2026-02-13 01:50:18 [ERROR] ❌ 치명적 오류 발생: Killed
```

## 🚀 사용 방법

### 실시간 로그 확인
```bash
# 프로그램을 백그라운드로 실행
./run_pdf2mp3.sh 열세번째1.pdf &

# 실시간 로그 확인 (다른 터미널에서)
tail -f pdf2mp3.log

# 메모리 관련 로그만 확인
tail -f pdf2mp3.log | grep MEMORY

# 경고/오류만 확인
tail -f pdf2mp3.log | grep -E "WARNING|ERROR"
```

### 시스템 다운 후 로그 분석
시스템이 다운되어도 로그 파일은 디스크에 남아있습니다.

```bash
# 로그 파일 전체 확인
cat pdf2mp3.log

# 마지막 50줄 확인
tail -n 50 pdf2mp3.log

# 오류 부분만 추출
grep -A 5 -B 5 "ERROR" pdf2mp3.log

# 메모리 상태 추적
grep "MEMORY" pdf2mp3.log

# 특정 청크 처리 로그 확인
grep "청크 28" pdf2mp3.log

# 메모리 부족 경고 확인
grep "메모리 부족" pdf2mp3.log
```

## 🔧 로그 분석 팁

### 1. 시스템 다운 시점 확인
```bash
# 마지막으로 처리된 청크 확인
tail -n 100 pdf2mp3.log | grep "청크.*완료"
```

### 2. 메모리 증가 추세 확인
```bash
# 메모리 상태만 추출하여 확인
grep "MEMORY.*프로세스" pdf2mp3.log | tail -n 20
```

### 3. BERT 모델 로딩 확인
```bash
# BERT 로딩 관련 로그
grep -i "bert" pdf2mp3.log
```

### 4. 특정 청크에서 문제 발생 시
```bash
# 청크 28 관련 모든 로그 확인
grep "CHUNK_28\|청크 28" pdf2mp3.log
```

## 📊 로그로 확인할 수 있는 정보

### 메모리 누수 패턴
```
# 메모리가 계속 증가하는 패턴
[MEMORY AFTER_CLEANUP_CHUNK_0] 프로세스: 350.0MB
[MEMORY AFTER_CLEANUP_CHUNK_1] 프로세스: 380.0MB
[MEMORY AFTER_CLEANUP_CHUNK_2] 프로세스: 410.0MB
[MEMORY AFTER_CLEANUP_CHUNK_3] 프로세스: 440.0MB
→ 메모리 정리가 제대로 안 되고 있음
```

### 정상적인 메모리 패턴
```
# 각 청크 처리 후 메모리가 비슷하게 유지
[MEMORY AFTER_CLEANUP_CHUNK_0] 프로세스: 350.0MB
[MEMORY AFTER_CLEANUP_CHUNK_1] 프로세스: 355.0MB
[MEMORY AFTER_CLEANUP_CHUNK_2] 프로세스: 352.0MB
[MEMORY AFTER_CLEANUP_CHUNK_3] 프로세스: 358.0MB
→ 정상적으로 메모리 정리되고 있음
```

### 시스템 다운 직전 상태
```
[INFO] 청크 27 완료
[MEMORY AFTER_CLEANUP_CHUNK_27] 시스템: 920.5MB / 987.0MB (93.3% 사용)
[WARNING] ⚠️  시스템 메모리 부족! 93.3% 사용 중
[INFO] 청크 28/41 처리 시작
[MEMORY BEFORE_CHUNK_28] 시스템: 945.2MB / 987.0MB (95.8% 사용)
[DEBUG] 파일 읽기: sptxt_28.txt
[INFO] MP3 생성 시작: 열세번째1_28.mp3
[MEMORY BEFORE_TTS_CHUNK_28] 시스템: 952.0MB / 987.0MB (96.5% 사용)
[DEBUG] TTS 변환 시작: 1850 문자 -> 열세번째1_28.mp3
[DEBUG] 문장 분할 완료: 12개 문장
[DEBUG] 문장 1 BERT 로드 중...
→ 여기서 시스템 다운 (BERT 로드 시 메모리 부족)
```

## 💡 문제 해결

### 1. 특정 청크에서 반복 실패
로그에서 청크 번호 확인 후:
```bash
# 해당 청크부터 재시작
python pdf2mp3.py 열세번째1.pdf 28
```

### 2. 메모리 부족으로 인한 다운
```bash
# 로그에서 메모리 사용률 확인
grep "메모리 부족" pdf2mp3.log

# 대응 방안
# 1) Swap 메모리 추가
# 2) 청크 크기 축소 (pdf2mp3.py의 max_length를 2000 → 1500으로)
# 3) 다른 프로세스 종료
```

### 3. BERT 모델 로딩 실패
```bash
# BERT 관련 오류 확인
grep -i "bert.*error\|bert.*fail" pdf2mp3.log
```

## 📁 로그 파일 관리

### 로그 파일 초기화
```bash
# 이전 로그 삭제 (새로 시작)
rm pdf2mp3.log

# 또는 백업 후 삭제
mv pdf2mp3.log pdf2mp3_$(date +%Y%m%d_%H%M%S).log
```

### 로그 파일 크기 확인
```bash
ls -lh pdf2mp3.log
```

### 로그 압축 보관
```bash
# 장기 보관용 압축
gzip pdf2mp3.log
# 압축 해제
gunzip pdf2mp3.log.gz
```

## 🎯 중요 포인트

1. **로그는 자동으로 기록됩니다**
   - 별도 설정 불필요
   - 프로그램 실행과 동시에 로그 생성

2. **시스템 다운 후에도 로그는 남습니다**
   - 디스크에 즉시 기록
   - 재부팅 후 분석 가능

3. **메모리 상태가 핵심**
   - `MEMORY` 로그를 중점적으로 확인
   - 90% 이상이면 위험 신호

4. **청크 번호 추적**
   - 어느 청크에서 멈췄는지 확인
   - 해당 청크부터 재시작 가능

## 버전
- v2.3 (2026-02-13)
- 상세 로깅 기능 추가
- 메모리 모니터링 강화
- 시스템 다운 후 분석 지원
