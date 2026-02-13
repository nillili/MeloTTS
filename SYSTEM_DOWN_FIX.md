# PDF2MP3 v2.3 최종 사용 가이드

## 🎯 28번째 청크에서 시스템 다운 문제 해결

### 문제 상황
- 프로그램 실행 중 28번째 청크 처리 시 시스템이 다운됨
- "죽었음(Killed)" 메시지 없이 갑자기 시스템 전체가 멈춤

### ✅ 해결 방안 (v2.3)

## 🆕 v2.3 주요 개선사항

### 1. 상세 로깅 기능 추가
- **자동 로그 파일 생성**: `pdf2mp3.log`
- **시스템 다운 후에도 로그 보존**: 디스크에 즉시 기록
- **20개 이상의 메모리 체크포인트**
  - 각 단계별 메모리 상태 기록
  - 각 청크 처리 전후 메모리 기록
  - BERT 모델 로드/해제 시점 기록
  - TTS 변환 전후 메모리 기록

### 2. 메모리 상태 자동 추적
```
[MEMORY START] 프로세스: 120.5MB, 시스템: 850.3MB / 987.0MB (86.1%)
[MEMORY BEFORE_CHUNK_28] 프로세스: 380.2MB, 시스템: 920.5MB / 987.0MB (93.3%)
[WARNING] ⚠️  시스템 메모리 부족! 93.3% 사용 중
```

### 3. 청크별 세부 로그
- 파일 읽기 시작/완료
- TTS 변환 시작/완료
- BERT 모델 로드 시점
- 메모리 정리 시점

## 🚀 사용 방법

### 1단계: 최신 코드 업데이트
```bash
cd ~/work/MeloTTS
git pull origin main
```

### 2단계: 백그라운드 실행 + 로그 모니터링
```bash
# 터미널 1: 프로그램 실행
conda activate melo
./run_pdf2mp3.sh 열세번째1.pdf

# 터미널 2: 실시간 로그 확인
tail -f pdf2mp3.log

# 또는 메모리 상태만 확인
tail -f pdf2mp3.log | grep MEMORY

# 또는 경고/오류만 확인
tail -f pdf2mp3.log | grep -E "WARNING|ERROR"
```

### 3단계: 시스템 다운 후 로그 분석
시스템 재부팅 후:
```bash
cd ~/work/MeloTTS

# 로그 파일 확인
cat pdf2mp3.log

# 마지막 처리된 청크 확인
tail -n 100 pdf2mp3.log | grep "청크.*완료"

# 메모리 상태 확인
grep "MEMORY" pdf2mp3.log | tail -n 20

# 28번 청크 관련 로그만 확인
grep "청크 28\|CHUNK_28" pdf2mp3.log
```

### 4단계: 중단된 지점부터 재시작
로그에서 마지막 완료 청크가 27번이었다면:
```bash
conda activate melo
python pdf2mp3.py 열세번째1.pdf 28
```

## 📊 로그 분석 예시

### 정상 패턴
```
[INFO] 청크 27/41 처리 시작
[MEMORY BEFORE_CHUNK_27] 프로세스: 350.0MB, 시스템: 880.0MB / 987.0MB (89.2%)
[DEBUG] 파일 읽기: sptxt_27.txt
[INFO] MP3 생성 시작: 열세번째1_27.mp3
[MEMORY BEFORE_TTS_CHUNK_27] 프로세스: 360.0MB, 시스템: 890.0MB / 987.0MB (90.2%)
[DEBUG] TTS 변환 시작: 1950 문자
[DEBUG] 문장 분할 완료: 15개 문장
[DEBUG] 문장 1 BERT 로드 중...
[DEBUG] 문장 1 추론 완료
...
[INFO] 파일 저장 완료: 열세번째1_27.mp3
[INFO] 청크 27 완료
[MEMORY AFTER_CLEANUP_CHUNK_27] 프로세스: 355.0MB, 시스템: 885.0MB / 987.0MB (89.7%)
```

### 문제 발생 패턴
```
[INFO] 청크 27 완료
[MEMORY AFTER_CLEANUP_CHUNK_27] 프로세스: 380.0MB, 시스템: 920.5MB / 987.0MB (93.3%)
[WARNING] ⚠️  시스템 메모리 부족! 93.3% 사용 중
[INFO] 청크 28/41 처리 시작
[MEMORY BEFORE_CHUNK_28] 프로세스: 385.0MB, 시스템: 945.2MB / 987.0MB (95.8%)
[DEBUG] 파일 읽기: sptxt_28.txt
[INFO] MP3 생성 시작: 열세번째1_28.mp3
[MEMORY BEFORE_TTS_CHUNK_28] 프로세스: 390.0MB, 시스템: 952.0MB / 987.0MB (96.5%)
[DEBUG] TTS 변환 시작: 1850 문자
[DEBUG] 문장 분할 완료: 12개 문장
[DEBUG] 문장 1 BERT 로드 중...
→ 여기서 로그 끊김 (시스템 다운)
```

## 🔧 문제 해결 방법

### 방법 1: Swap 메모리 추가 (가장 효과적)
시스템에 여유 공간이 있다면 swap 추가:
```bash
# 512MB swap 파일 생성
sudo fallocate -l 512M /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 적용
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 확인
free -h
```

### 방법 2: 청크 크기 축소
`pdf2mp3.py` 파일 수정:
```python
# 약 273번째 줄 (split_text 함수)
def split_text(text, max_length=1500, ...  # 2000 → 1500으로 변경
```

### 방법 3: 다른 프로세스 종료
```bash
# 메모리 사용량 확인
top

# 불필요한 프로세스 종료
# (Chrome, 브라우저, 기타 애플리케이션 등)
```

### 방법 4: 청크 단위 처리
전체를 한 번에 처리하지 말고 10개씩 나눠서:
```bash
# 0-10번 청크
python pdf2mp3.py 열세번째1.pdf 0

# 시스템 재부팅 (메모리 정리)

# 11-20번 청크
python pdf2mp3.py 열세번째1.pdf 11

# 시스템 재부팅

# 21-30번 청크
python pdf2mp3.py 열세번째1.pdf 21

# ... 이런 식으로 진행
```

## 📋 체크리스트

### 실행 전
- [ ] 최신 코드 업데이트 (`git pull origin main`)
- [ ] Conda 환경 활성화 (`conda activate melo`)
- [ ] 로그 모니터링 준비 (`tail -f pdf2mp3.log`)
- [ ] 시스템 메모리 확인 (`free -h`)

### 실행 중
- [ ] 실시간 로그 확인 중
- [ ] 메모리 사용률 90% 미만 유지 확인
- [ ] 경고 메시지 발생 시 대응 준비

### 시스템 다운 후
- [ ] 로그 파일 확인 (`cat pdf2mp3.log`)
- [ ] 마지막 완료 청크 번호 확인
- [ ] 메모리 부족 경고 있었는지 확인
- [ ] Swap 추가 또는 청크 크기 조정
- [ ] 중단 지점부터 재시작

## 🎓 로그 분석 명령어 모음

```bash
# 전체 로그 확인
cat pdf2mp3.log

# 마지막 50줄
tail -n 50 pdf2mp3.log

# 실시간 모니터링
tail -f pdf2mp3.log

# 메모리 상태만 추출
grep "MEMORY" pdf2mp3.log

# 경고/오류만 추출
grep -E "WARNING|ERROR" pdf2mp3.log

# 특정 청크 관련 로그
grep "청크 28\|CHUNK_28" pdf2mp3.log

# 마지막 완료 청크 확인
tail -n 100 pdf2mp3.log | grep "청크.*완료"

# 메모리 사용률 추세
grep "MEMORY.*시스템" pdf2mp3.log | tail -n 20

# 오류 전후 5줄씩 확인
grep -A 5 -B 5 "ERROR" pdf2mp3.log

# BERT 로드 시점 확인
grep -i "bert.*로드" pdf2mp3.log
```

## 📚 관련 문서

- **LOGGING_GUIDE.md**: 로깅 기능 상세 가이드
- **QUICK_START.md**: 빠른 시작 가이드
- **HOW_TO_USE.md**: 사용 방법 전체 가이드
- **URGENT_FIX.md**: 긴급 수정 가이드
- **MEMORY_OPTIMIZATION.md**: 메모리 최적화 가이드
- **FINAL_FIX.md**: 최종 수정 사항

## 🔍 예상 원인 및 해결

### 원인 1: BERT 모델 로드 시 메모리 부족
**증상**: 로그에 "BERT 로드 중..." 이후 끊김  
**해결**: Swap 추가 또는 청크 크기 축소

### 원인 2: 메모리 누수
**증상**: 청크 처리마다 메모리 계속 증가  
**해결**: 이미 v2.0~v2.3에서 해결됨 (확인: 메모리 로그 패턴)

### 원인 3: 시스템 전체 메모리 부족
**증상**: 90% 이상 메모리 사용률  
**해결**: 다른 프로세스 종료, Swap 추가, 청크 단위 처리

## 💡 Pro Tips

1. **첫 실행부터 로그 확인**
   ```bash
   # 한 번에 실행 + 모니터링
   ./run_pdf2mp3.sh 열세번째1.pdf & tail -f pdf2mp3.log
   ```

2. **메모리 부족 경고 시 즉시 중단**
   - `Ctrl+C`로 중단
   - Swap 추가 후 재시작

3. **로그 파일 백업**
   ```bash
   # 다음 실행 전 로그 백업
   cp pdf2mp3.log pdf2mp3_$(date +%Y%m%d_%H%M%S).log
   ```

4. **청크별 일시정지**
   - 스크립트 수정하여 10개마다 일시정지 추가
   - 메모리 정리 시간 확보

## 버전 정보
- **v2.3** (2026-02-13) - 상세 로깅 기능 추가
- **v2.2.3** (2026-02-13) - PYTHONOPTIMIZE 문제 해결
- **v2.2** (2026-02-13) - 파일 기반 청크 처리
- **v2.1** (2026-02-13) - 첫 청크 메모리 최적화
- **v2.0** (2026-02-13) - 싱글톤 TTS 모델

## GitHub
https://github.com/nillili/MeloTTS

최신 커밋: `1ae3c3d` (v2.3)
