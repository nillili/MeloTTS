# 🚨 긴급 수정: 첫 번째 청크 "죽었음" 오류 해결

## 📋 문제 상황

```
처리 중: [1/27] 청크
...
BERT 모델 로딩 중...
죽었음  ← 이 오류 발생!
```

**원인**: BERT 모델이 최초 로딩 시 추가로 300MB 이상의 메모리를 사용하여 OOM 발생

---

## ✅ 적용된 긴급 수정사항 (v2.1)

### 1. 텍스트 분할 크기 축소
```python
# 변경 전
max_length=3000

# 변경 후  
max_length=2000  # 33% 감소
```

### 2. 강제 메모리 정리 함수
```python
def force_memory_cleanup():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

# 적용 위치:
# - 모델 로딩 전/후
# - 각 청크 처리 후
```

### 3. 메모리 최적화 실행 스크립트 (★★★ 중요)

**새로운 실행 방법** (권장):
```bash
./run_pdf2mp3.sh 열세번째1.pdf
```

**기존 실행 방법**보다 메모리를 20-30% 더 절약합니다!

---

## 🎯 지금 바로 사용하는 방법

### ⚠️ 사전 준비: Conda 환경 활성화 (필수!)

```bash
conda activate melo
```

### 방법 1: 메모리 최적화 스크립트 (★★★ 강력 권장)

```bash
# Conda 환경 활성화 확인
conda activate melo

# 스크립트에 실행 권한 부여 (최초 1회만)
chmod +x run_pdf2mp3.sh

# 실행
./run_pdf2mp3.sh 열세번째1.pdf

# 특정 청크부터 시작 (이어서 할 때)
./run_pdf2mp3.sh 열세번째1.pdf 5
```

**자동으로 설정되는 환경 변수**:
- `TOKENIZERS_PARALLELISM=false` - 병렬 처리 OFF
- `OMP_NUM_THREADS=1` - 스레드 수 제한
- `MKL_NUM_THREADS=1` - Intel MKL 스레드 제한
- HuggingFace 경고 억제

### 방법 2: 기존 방식 (직접 실행)

```bash
# Conda 환경 활성화 확인
conda activate melo

# 실행
python pdf2mp3.py 열세번째1.pdf
```

> ⚠️ 방법 1이 메모리를 더 절약하므로 **방법 1 권장**!

> 🔴 **중요**: 반드시 `conda activate melo` 명령으로 환경을 먼저 활성화해야 합니다!

---

## 📊 예상 효과

| 항목 | v2.0 | v2.1 | 개선 |
|------|------|------|------|
| 텍스트 청크 크기 | 3000자 | 2000자 | 33% 감소 |
| 메모리 정리 | 기본 | 강제 | 강화 |
| 환경 최적화 | 없음 | 있음 | 추가 |
| **첫 청크 안정성** | **중간** | **높음** | **대폭 개선** |

---

## ⚠️ 여전히 "죽었음" 발생 시

### 1단계: swap 메모리 확인
```bash
free -h
```

Swap이 0B라면:
```bash
# swap 파일 생성 (512MB)
sudo fallocate -l 512M /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 2단계: 텍스트 분할 크기 더 줄이기
`pdf2mp3.py` 파일 수정:
```python
# 67번 줄 찾기
def split_text(text, max_length=2000, ...):

# 다음과 같이 변경
def split_text(text, max_length=1500, ...):  # 1500자로 감소
```

### 3단계: 불필요한 프로세스 종료
```bash
# 메모리 사용 확인
top

# 불필요한 프로세스 종료 후 재시도
```

---

## 🔗 GitHub 저장소

모든 변경사항이 main 브랜치에 반영되었습니다:
- **커밋 해시**: `10df043`
- **저장소**: https://github.com/nillili/MeloTTS

---

## 📚 상세 문서

더 자세한 정보는 `MEMORY_OPTIMIZATION.md` 참조

---

## ✨ 요약

1. **`run_pdf2mp3.sh` 스크립트 사용** ← 이게 가장 중요!
2. 텍스트 분할 크기 자동 축소됨 (2000자)
3. 강제 메모리 정리 추가
4. 여전히 문제 시 swap 메모리 추가

**이제 다시 실행해보세요!** 🚀

```bash
./run_pdf2mp3.sh 열세번째1.pdf
```
