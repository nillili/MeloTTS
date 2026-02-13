#!/bin/bash

# Conda 환경 자동 감지 및 활성화
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "✓ Conda 환경 감지: $CONDA_DEFAULT_ENV"
    PYTHON_CMD="python"
elif command -v conda &> /dev/null; then
    # Conda가 설치되어 있지만 환경이 활성화되지 않은 경우
    echo "⚠️  Conda 환경이 활성화되지 않았습니다."
    echo "다음 명령으로 먼저 환경을 활성화해주세요:"
    echo "  conda activate melo"
    echo ""
    echo "또는 직접 실행:"
    echo "  python pdf2mp3.py $@"
    exit 1
else
    # Conda가 없는 경우 python3 사용
    PYTHON_CMD="python3"
fi

# 메모리 최적화 환경 변수 설정
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Python 메모리 최적화
export PYTHONOPTIMIZE=2
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
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "  - Conda 환경: $CONDA_DEFAULT_ENV"
fi
echo "============================================================"
echo

$PYTHON_CMD pdf2mp3.py "$@"
