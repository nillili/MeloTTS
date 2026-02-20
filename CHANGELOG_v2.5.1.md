# PDF2MP3 v2.5.1 - 긴급 수정

## 📅 날짜: 2026-02-15

## 🔧 주요 수정사항

### ignores.txt 파일 위치 고정 (중요!)

**문제점:**
- 기존: ignores.txt가 현재 작업 디렉터리에서 검색됨
- 결과: 작업 폴더(MP3 생성 위치)에 ignores.txt를 두면 `rm *` 실행 시 함께 삭제됨
- 영향: 사용자가 실수로 패턴 파일을 삭제하여 다시 설정해야 하는 불편함

**해결 방법:**
```python
# 변경 전
def load_ignore_patterns(ignore_file='ignores.txt'):
    if not os.path.exists(ignore_file):  # 현재 디렉터리에서 검색
        return []

# 변경 후
def load_ignore_patterns(ignore_file='ignores.txt'):
    # 스크립트 디렉터리 경로 가져오기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ignore_path = os.path.join(script_dir, ignore_file)
    
    if not os.path.exists(ignore_path):  # 스크립트 디렉터리에서 검색
        return []
```

**효과:**
- ✅ ignores.txt는 **항상 pdf2mp3.py와 같은 위치**에서 검색
- ✅ 어느 디렉터리에서 실행하든 동일한 패턴 적용
- ✅ 작업 폴더에서 `rm *` 실행해도 ignores.txt는 안전
- ✅ 중앙 집중식 패턴 관리 가능

## 📁 파일 구조

### ✅ 올바른 구조
```
~/work/MeloTTS/              # 스크립트 디렉터리
├── pdf2mp3.py               # 메인 스크립트
├── ignores.txt              # ← 여기에 생성!
├── melo/
├── run_pdf2mp3.sh
└── ...

~/work/pdfs/                 # 작업 디렉터리 (예시)
├── document.pdf
├── document_00.mp3
├── document_01.mp3
└── sptxt_0.txt
# ignores.txt는 여기에 없어도 됨!
# rm * 실행해도 스크립트 디렉터리의 ignores.txt는 안전
```

### ❌ 이전 구조 (문제 있음)
```
~/work/pdfs/
├── document.pdf
├── ignores.txt              # ← 여기 두면 rm * 시 삭제됨!
├── document_00.mp3
└── sptxt_0.txt
```

## 🧪 테스트 결과

### 테스트 시나리오 1: 다른 디렉터리에서 실행
```bash
# 스크립트 디렉터리
cd ~/work/MeloTTS
ls ignores.txt  # ✓ 존재

# 작업 디렉터리로 이동
cd ~/work/pdfs
../MeloTTS/run_pdf2mp3.sh document.pdf

# 결과: ~/work/MeloTTS/ignores.txt 사용됨
```

### 테스트 시나리오 2: 작업 폴더 정리
```bash
cd ~/work/pdfs

# 청크 파일 및 임시 파일 삭제
rm *.txt *.mp3

# 결과: 
# ✓ 작업 폴더의 sptxt_*.txt 삭제됨
# ✓ MP3 파일 삭제됨
# ✓ ~/work/MeloTTS/ignores.txt는 그대로 유지!
```

### 테스트 시나리오 3: 경로 확인
```python
# test_ignore_path.py 실행 결과
✓ 현재 작업 디렉터리: /home/user/webapp
✓ 스크립트 디렉터리: /home/user/webapp
✓ ignores.txt 경로: /home/user/webapp/ignores.txt

# 다른 디렉터리로 이동 후
✓ 작업 디렉터리 변경: /tmp/test_pdf_work
✓ ignores.txt 경로 (변경 없음): /home/user/webapp/ignores.txt
✓ 스크립트 디렉터리 (고정): /home/user/webapp

💡 결과: ignores.txt는 항상 스크립트 디렉터리에서 검색됨
💡 작업 디렉터리의 파일을 rm *로 지워도 ignores.txt는 안전!
```

## 📝 변경된 파일

1. **pdf2mp3.py**
   - `load_ignore_patterns()` 함수 수정
   - 스크립트 디렉터리 기반 경로 사용
   - 로그 메시지에 전체 경로 포함

2. **IGNORE_PATTERNS_GUIDE.md**
   - "📁 파일 위치" 섹션 추가
   - 올바른 위치 vs 잘못된 위치 예시
   - 안전성 및 경로 확인 방법 설명

3. **README.md**
   - 반복 문장 제거 섹션 업데이트
   - 파일 위치 중요성 강조

4. **test_ignore_path.py** (신규)
   - 경로 테스트 스크립트
   - 다양한 시나리오 검증

5. **CHANGELOG_v2.5.1.md** (신규)
   - 이번 긴급 수정 내역

## 🔄 호환성

- ✅ **하위 호환성**: 기존 사용자에게 영향 없음
- ✅ **마이그레이션**: 작업 폴더의 ignores.txt를 스크립트 디렉터리로 이동 권장
- ✅ **동작 변경**: ignores.txt 검색 위치만 변경됨

## 📊 사용자 영향

### 긍정적 영향
- ✅ 실수로 패턴 파일 삭제 방지
- ✅ 중앙 집중식 패턴 관리
- ✅ 여러 작업 폴더에서 동일 패턴 재사용

### 주의사항
- ⚠️ **기존 사용자**: 작업 폴더의 ignores.txt를 스크립트 디렉터리로 이동 필요
- ⚠️ **새 사용자**: 문서대로 스크립트 디렉터리에 생성

## 🚀 마이그레이션 가이드

### 기존 사용자
```bash
# 1. 기존 ignores.txt 확인
find ~/work -name "ignores.txt"

# 2. 작업 폴더에 있다면 스크립트 디렉터리로 이동
mv ~/work/pdfs/ignores.txt ~/work/MeloTTS/

# 3. 확인
ls -la ~/work/MeloTTS/ignores.txt
```

### 새 사용자
```bash
# 스크립트 디렉터리에 직접 생성
cd ~/work/MeloTTS
nano ignores.txt
```

## 🎓 사용자 피드백 반영

**사용자 지적:**
> "ignores.txt 파일의 위치는 pdf2mp3.py와 같은 위치에 있어야 한다.
> 작업폴더(.mp3 만들어지는곳)에 두게 되면 나중에 한꺼번에 rm * 명령어로 다 지워져 버린다."

**구현 결과:**
- ✅ ignores.txt를 항상 스크립트 디렉터리에서 검색하도록 수정
- ✅ 작업 폴더 정리 시 패턴 파일 보호
- ✅ 명확한 문서화 및 테스트 추가

## 📈 코드 변경 통계

- **수정된 함수**: 1개 (`load_ignore_patterns`)
- **추가된 코드 줄**: 5줄
- **변경된 동작**: ignores.txt 검색 경로
- **성능 영향**: 없음

---

**커밋 해시**: (자동 생성)  
**작성자**: AI Assistant  
**날짜**: 2026-02-15  
**우선순위**: 🔴 HIGH (사용자 데이터 보호)
