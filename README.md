# PDF2MP3 v2.5 - 반복 문장 제거 기능 추가

PDF 파일의 텍스트(한글)를 추출하여 음성(MP3)으로 변환하는 프로그램입니다.

## 🆕 v2.5 주요 기능

### 🎯 반복 문장 자동 제거 (NEW!)
- **ignores.txt 파일 지원**: 제거할 문장을 파일로 관리
- **자동 제거**: 회사명, 책 제목, 저작권 정보 등 반복 문장 제거
- **대소문자 무관**: 대소문자 구분 없이 매칭
- **간편한 설정**: 한 줄에 하나씩 입력만 하면 됨
- **제거 통계 표시**: 몇 개의 반복 문장이 제거되었는지 실시간 표시

### ✨ 배치 변환 모드 (v2.4)
- **폴더 단위 자동 변환**: 폴더 내 모든 PDF를 한 번에 처리
- **스마트 재시작**: 변환 완료된 파일은 자동으로 스킵
- **같은 폴더에 저장**: MP3 파일은 원본 PDF와 같은 위치에 저장
- **견고한 오류 처리**: 특정 파일 실패 시에도 다음 파일 계속 진행

### 📝 상세 로깅 (v2.3)
- **시스템 다운 후 분석**: `pdf2mp3.log` 파일로 상세 추적
- **20개 이상의 메모리 체크포인트**: 각 단계별 메모리 상태 기록
- **실시간 모니터링**: `tail -f pdf2mp3.log`로 진행 상황 확인

### 💾 메모리 최적화 (v2.0~v2.2)
- **파일 기반 청크 처리**: 메모리 사용량 58% 감소 (1.2GB → 500MB)
- **TTS 모델 싱글톤**: 한 번만 로드하여 재사용
- **명시적 메모리 해제**: 각 청크 처리 후 자동 정리

## 🚀 빠른 시작

### 설치
```bash
git clone https://github.com/nillili/MeloTTS.git
cd MeloTTS
conda activate melo  # 또는 환경 생성
pip install -r requirements.txt
```

### 사용법

#### 🎯 반복 문장 제거 (NEW!)
```bash
# 1. ignores.txt 파일 생성
nano ignores.txt

# 2. 제거할 문장 입력 (한 줄에 하나씩)
흐르는 강물처럼
문학사
저작권

# 3. 일반적인 방법으로 변환
./run_pdf2mp3.sh document.pdf
```

#### 📁 배치 변환 (폴더 전체)
```bash
./run_pdf2mp3.sh ./pdf
```

#### 📄 단일 파일 변환
```bash
./run_pdf2mp3.sh document.pdf
```

#### 🔄 중단 후 재시작
```bash
# 특정 청크부터 시작
./run_pdf2mp3.sh document.pdf 10
```

## 📖 상세 가이드

### 기본 사용
- **[QUICK_START.md](QUICK_START.md)**: 빠른 시작 가이드
- **[HOW_TO_USE.md](HOW_TO_USE.md)**: 전체 사용 방법
- **[IGNORE_PATTERNS_GUIDE.md](IGNORE_PATTERNS_GUIDE.md)**: 반복 문장 제거 가이드 (NEW!)

### 배치 변환
- **[BATCH_CONVERT_GUIDE.md](BATCH_CONVERT_GUIDE.md)**: 폴더 단위 일괄 변환 가이드
- **[BATCH_ANALYSIS_REPORT.md](BATCH_ANALYSIS_REPORT.md)**: 실제 운영 테스트 결과

### 문제 해결
- **[SYSTEM_DOWN_FIX.md](SYSTEM_DOWN_FIX.md)**: 시스템 다운 문제 해결
- **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)**: 로그 분석 방법
- **[URGENT_FIX.md](URGENT_FIX.md)**: 긴급 수정 사항
- **[FINAL_FIX.md](FINAL_FIX.md)**: torchaudio 오류 해결

### 메모리 최적화
- **[MEMORY_OPTIMIZATION.md](MEMORY_OPTIMIZATION.md)**: 메모리 최적화 상세 가이드

## 💡 사용 예시

### 예시 1: 반복 문장 제거 (NEW!)
```bash
# ignores.txt 파일 생성
cat > ignores.txt << EOF
흐르는 강물처럼
문학사
저작권 © 2024
EOF

# 변환 실행
./run_pdf2mp3.sh book.pdf

# 출력:
# ============================================================
# [2단계] 텍스트 전처리 및 분할
# ============================================================
# 
# 📝 제외 패턴 목록 (ignores.txt):
# ------------------------------------------------------------
#   1. '흐르는 강물처럼'
#   2. '문학사'
#   3. '저작권 © 2024'
# ------------------------------------------------------------
# 총 3개 패턴 적용
# 
# 🗑️  제거된 반복 문장:
# ------------------------------------------------------------
#   • '흐르는 강물처럼': 15회 제거
#   • '문학사': 12회 제거
#   • '저작권 © 2024': 8회 제거
# ------------------------------------------------------------
# ✓ 총 35개 반복 문장 제거됨
```

### 예시 2: 단일 PDF 변환
```bash
conda activate melo
./run_pdf2mp3.sh 열세번째1.pdf

# 생성 파일:
# - 열세번째1_00.mp3
# - 열세번째1_01.mp3
# - ...
```

### 예시 3: 폴더 내 모든 PDF 변환
```bash
# PDF 파일들이 있는 폴더
ls pdf/
# → 열세번째1.pdf, 열세번째2.pdf, 학습자료.pdf

./run_pdf2mp3.sh ./pdf

# 결과:
# pdf/열세번째1_00.mp3, 열세번째1_01.mp3, ...
# pdf/열세번째2_00.mp3, 열세번째2_01.mp3, ...
# pdf/학습자료_00.mp3, 학습자료_01.mp3, ...
```

### 예시 4: 중단 후 재시작
```bash
# 처음 실행 (28번 청크에서 시스템 다운)
./run_pdf2mp3.sh 열세번째1.pdf

# 로그 확인
tail -n 100 pdf2mp3.log | grep "청크.*완료"
# → 마지막: "청크 27 완료"

# 28번부터 재시작
./run_pdf2mp3.sh 열세번째1.pdf 28
```

### 예시 5: 배치 재시작 (스마트 스킵)
```bash
# 첫 실행 (열세번째1.pdf 완료 후 시스템 다운)
./run_pdf2mp3.sh ./pdf

# 재시작 (같은 명령)
./run_pdf2mp3.sh ./pdf
# → 열세번째1.pdf 자동 스킵
# → 열세번째2.pdf부터 계속
```

## 🔧 고급 기능

### 실시간 로그 모니터링
```bash
# 터미널 1
./run_pdf2mp3.sh ./pdf

# 터미널 2
tail -f pdf2mp3.log | grep MEMORY
```

### 백그라운드 실행
```bash
nohup ./run_pdf2mp3.sh ./pdf > batch.log 2>&1 &
tail -f batch.log
```

### GPU 사용
```bash
# 배치
./run_pdf2mp3.sh ./pdf cuda

# 단일 파일
./run_pdf2mp3.sh document.pdf 0 cuda
```

## 📊 버전 히스토리

| 버전 | 날짜 | 주요 개선사항 | 메모리 사용량 |
|------|------|---------------|---------------|
| v2.5 | 2026-02-15 | 반복 문장 제거 기능 (`ignores.txt`) | ~500MB |
| v2.4 | 2026-02-14 | 배치 변환 기능, 스마트 재시작 | ~500MB |
| v2.3 | 2026-02-13 | 상세 로깅, 20개 체크포인트 | ~500MB |
| v2.2 | 2026-02-13 | 파일 기반 청크 처리 | ~500MB |
| v2.1 | 2026-02-13 | 첫 청크 메모리 최적화 | ~700MB |
| v2.0 | 2026-02-13 | 싱글톤 TTS 모델 | ~900MB |
| v1.0 | - | 초기 버전 | >1.2GB |

## 🛠️ 시스템 요구사항

- **Python**: 3.9+
- **메모리**: 최소 1GB (권장 2GB+)
- **디스크**: PDF 크기의 10배 이상 권장
- **OS**: Linux, macOS (Windows WSL)

## 📦 주요 의존성

- PyMuPDF (fitz): PDF 텍스트 추출
- MeloTTS: 한국어 음성 합성
- torch: 딥러닝 프레임워크
- psutil: 메모리 모니터링

## ⚠️ 문제 해결

### "죽었음(Killed)" 오류
1. Swap 메모리 추가 (512MB)
2. 청크 크기 축소 (`max_length=2000 → 1500`)
3. 로그 확인: `grep "MEMORY" pdf2mp3.log`

자세한 내용: [SYSTEM_DOWN_FIX.md](SYSTEM_DOWN_FIX.md)

### torchaudio 오류
`AttributeError: 'NoneType' object has no attribute 'format'`

해결: [FINAL_FIX.md](FINAL_FIX.md) 참조 (v2.2.3에서 해결됨)

### 메모리 부족
- Swap 추가
- 청크 크기 축소
- 다른 프로세스 종료

자세한 내용: [URGENT_FIX.md](URGENT_FIX.md)

## 🤝 기여

이슈 및 Pull Request 환영합니다!

## 📄 라이선스

이 프로젝트는 MeloTTS 프로젝트를 기반으로 합니다.

## 🔗 링크

- **GitHub**: https://github.com/nillili/MeloTTS
- **원본 MeloTTS**: https://github.com/myshell-ai/MeloTTS

## 📧 문의

이슈 탭에서 문의해주세요.

---

**최신 버전**: v2.4 (2026-02-14)  
**최신 커밋**: `0fb8171`
