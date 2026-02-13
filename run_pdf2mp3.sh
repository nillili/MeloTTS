#!/bin/bash

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
echo "============================================================"
echo

python3 pdf2mp3.py "$@"
