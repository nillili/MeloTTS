# 🚀 빠른 시작 가이드

## ✅ 최종 수정 완료! (v2.2.2)

**문제 해결**: `run_pdf2mp3.sh` 스크립트가 이제 Conda 환경의 Python을 **자동으로 정확하게 감지**합니다!

**개선**: `which python` 명령으로 현재 활성화된 Python을 직접 확인하여 사용합니다.

---

## 📋 실행 방법 (3단계만!)

### 1단계: 최신 코드 가져오기

```bash
cd ~/work/MeloTTS
git pull origin main
```

### 2단계: Conda 환경 활성화 ⭐ **필수!**

```bash
conda activate melo
```

### 3단계: 실행!

```bash
./run_pdf2mp3.sh 열세번째1.pdf
```

---

## 🔍 Python 자동 감지 확인

스크립트 실행 시 다음과 같이 Python 정보가 표시됩니다:

```bash
$ conda activate melo
$ ./run_pdf2mp3.sh 열세번째1.pdf

✓ Conda Python 감지: /home/hong/miniconda3/envs/melo/bin/python
============================================================
PDF2MP3 메모리 최적화 모드로 실행
============================================================
환경 변수 설정 완료:
  - PyTorch 메모리 최적화: ON
  - 병렬 처리: OFF (메모리 절약)
  - 스레드 수: 1 (메모리 절약)
  - Python 명령: python  ← 올바른 Python 사용!
  - Conda 환경: melo
============================================================
```

---

## 🧪 작동 확인 방법

스크립트가 올바른 Python을 사용하는지 확인:

```bash
# 1. Conda 환경 활성화
conda activate melo

# 2. 현재 Python 경로 확인
which python
# 출력 예: /home/hong/miniconda3/envs/melo/bin/python

# 3. 스크립트 실행 시 같은 Python 사용 확인
./run_pdf2mp3.sh 열세번째1.pdf
# "✓ Conda Python 감지: ..." 메시지에서 같은 경로 표시되는지 확인
```

---

## 🎯 실행 시 보이는 화면

```bash
$ conda activate melo
$ ./run_pdf2mp3.sh 열세번째1.pdf

✓ Conda 환경 감지: melo
============================================================
PDF2MP3 메모리 최적화 모드로 실행
============================================================
환경 변수 설정 완료:
  - PyTorch 메모리 최적화: ON
  - 병렬 처리: OFF (메모리 절약)
  - 스레드 수: 1 (메모리 절약)
  - Conda 환경: melo
============================================================

============================================================
PDF to MP3 변환 시작
============================================================
입력 파일: 열세번째1.pdf
출력 이름: 열세번째1
시작 번호: 0
디바이스: cpu
============================================================

[1단계] PDF에서 텍스트 추출 중...

[2단계] 텍스트 전처리 및 분할 중...
✓ 총 41개의 청크로 분할되었습니다.

[3단계] 모든 청크를 파일로 저장 중...
✓ 41개의 텍스트 파일 저장 완료
✓ 메모리에서 텍스트 데이터 해제 완료

[4단계] TTS 모델 로딩 중...
⚠️  메모리가 부족한 경우 시간이 걸릴 수 있습니다...
TTS 모델 로딩 완료!

[5단계] MP3 파일 생성 시작 (시작 번호: 0)
============================================================

▶ 처리 중: [1/41] 청크
  - 음성 변환 중...
  ✓ 완료: 열세번째1_00.mp3
...
```

---

## ⚠️ Conda 환경을 활성화하지 않으면?

스크립트가 자동으로 감지하고 안내합니다:

```bash
$ ./run_pdf2mp3.sh 열세번째1.pdf

⚠️  Conda 환경이 활성화되지 않았습니다.
다음 명령으로 먼저 환경을 활성화해주세요:
  conda activate melo

또는 직접 실행:
  python pdf2mp3.py 열세번째1.pdf
```

---

## 🔧 중단 후 이어서 실행

```bash
conda activate melo

# 5번 청크부터 다시 시작 (0부터 시작이므로 6번째 청크)
./run_pdf2mp3.sh 열세번째1.pdf 5
```

---

## 📂 생성되는 파일

### 텍스트 파일 (중간 파일)
```
sptxt_0.txt
sptxt_1.txt
...
sptxt_40.txt
```

### MP3 파일 (최종 결과)
```
열세번째1_00.mp3
열세번째1_01.mp3
...
열세번째1_40.mp3
```

---

## 💡 메모리 사용량 (v2.2)

| 처리 방식 | 메모리 사용 |
|----------|------------|
| 이전 (메모리 보관) | ~900 MB |
| **현재 (파일 기반)** | **~500 MB** ✨ |

**개선**: 41개 청크를 메모리에 보관하지 않고 파일로 저장!

---

## ⚠️ 여전히 문제가 발생하면?

### 문제 1: 스크립트가 잘못된 Python 사용

**증상**: `./run_pdf2mp3.sh` 실행 시 모듈을 찾을 수 없다는 오류

**해결**:
```bash
# 방법 A: 직접 python 명령 사용 (가장 확실)
conda activate melo
python pdf2mp3.py 열세번째1.pdf

# 방법 B: 스크립트 디버그
conda activate melo
which python  # 올바른 경로 확인
./run_pdf2mp3.sh 열세번째1.pdf  # Python 경로가 일치하는지 확인
```

### 문제 2: "죽었음(Killed)" 오류

**해결책 1: Swap 메모리 추가 (가장 효과적)**

```bash
sudo fallocate -l 512M /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h  # 확인
```

**해결책 2: 청크 크기 축소**

`pdf2mp3.py` 파일 수정:
```python
def split_text(text, max_length=1500, ...):  # 2000 → 1500
```

### 문제 3: 환경 감지가 안 됨

**해결**: 직접 Python 지정
```bash
conda activate melo
python pdf2mp3.py 열세번째1.pdf  # 이 방법이 가장 확실!
```

---

## 📚 상세 문서

- **HOW_TO_USE.md** - 전체 사용 가이드
- **URGENT_FIX.md** - 긴급 문제 해결
- **MEMORY_OPTIMIZATION.md** - 메모리 최적화 상세

---

## ✨ 체크리스트

- [x] Conda 환경 자동 감지
- [x] 파일 기반 청크 처리 (메모리 절약)
- [x] 메모리 최적화 환경 변수 설정
- [x] 중단 후 재개 가능
- [x] 상세한 진행 상황 표시

---

## 🎉 이제 실행하세요!

```bash
cd ~/work/MeloTTS
git pull origin main
conda activate melo
./run_pdf2mp3.sh 열세번째1.pdf
```

**완료!** 🚀
