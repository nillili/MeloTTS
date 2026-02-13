#!/bin/bash

# Conda 환경 Python 찾기 (우선순위)
# 1. 현재 활성화된 conda 환경의 python
# 2. conda가 설치되어 있지만 환경이 비활성화된 경우 경고
# 3. 시스템 python3

PYTHON_CMD=""

# 방법 1: which python으로 현재 활성화된 python 찾기
if command -v python &> /dev/null; then
    PYTHON_PATH=$(which python)
    # conda 환경의 python인지 확인 (경로에 conda, anaconda, miniconda 포함)
    if [[ "$PYTHON_PATH" == *"conda"* ]] || [[ "$PYTHON_PATH" == *"anaconda"* ]] || [[ "$PYTHON_PATH" == *"miniconda"* ]]; then
        PYTHON_CMD="python"
        if [ -n "$CONDA_DEFAULT_ENV" ]; then
            echo "✓ Conda 환경 감지: $CONDA_DEFAULT_ENV"
        else
            echo "✓ Conda Python 감지: $PYTHON_PATH"
        fi
    fi
fi

# 방법 2: CONDA_DEFAULT_ENV 변수 확인
if [ -z "$PYTHON_CMD" ] && [ -n "$CONDA_DEFAULT_ENV" ]; then
    PYTHON_CMD="python"
    echo "✓ Conda 환경 감지: $CONDA_DEFAULT_ENV"
fi

# 방법 3: conda가 있지만 환경이 비활성화된 경우
if [ -z "$PYTHON_CMD" ] && command -v conda &> /dev/null; then
    echo "⚠️  Conda가 설치되어 있지만 환경이 활성화되지 않았습니다."
    echo ""
    echo "다음 명령으로 먼저 환경을 활성화해주세요:"
    echo "  conda activate melo"
    echo ""
    echo "또는 직접 실행:"
    echo "  python pdf2mp3.py $@"
    echo ""
    exit 1
fi

# 방법 4: 시스템 python3 사용 (최후의 수단)
if [ -z "$PYTHON_CMD" ]; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo "⚠️  시스템 Python3 사용 (Conda 환경 권장)"
    else
        echo "❌ Python을 찾을 수 없습니다."
        exit 1
    fi
fi

# 메모리 최적화 환경 변수 설정
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Python 메모리 최적화 (PYTHONOPTIMIZE 제거 - torchaudio 충돌 방지)
# export PYTHONOPTIMIZE=2  # 주석 처리: torchaudio docstring 오류 발생
export PYTHONDONTWRITEBYTECODE=1

# HuggingFace 캐시 경고 억제
export HF_HUB_DISABLE_SYMLINKS_WARNING=1

echo "============================================================"
echo "PDF2MP3 메모리 최적화 모드로 실행"
echo "============================================================"
echo "환경 변수 설정 완료:"
echo "  - PyTorch 메모리 최적화: ON"
echo "  - 병렬 처리: OFF (메모리 절약)"
echo "  - 스레드 수: 1 (메모리 절약)"
echo "  - Python 명령: $PYTHON_CMD"
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "  - Conda 환경: $CONDA_DEFAULT_ENV"
fi
echo "============================================================"
echo

$PYTHON_CMD pdf2mp3.py "$@"
