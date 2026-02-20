#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ignores.txt 기능 출력 테스트
"""

# 샘플 패턴과 제거 통계 생성
patterns = [
    "흐르는 강물처럼",
    "문학사",
    "저작권 © 2024",
    "All Rights Reserved"
]

removal_stats = {
    "흐르는 강물처럼": 15,
    "문학사": 12,
    "저작권 © 2024": 8,
    "All Rights Reserved": 5
}

# 출력 테스트
print("\n" + "="*60)
print("[2단계] 텍스트 전처리 및 분할")
print("="*60)

if patterns:
    print(f"\n📝 제외 패턴 목록 (ignores.txt):")
    print("-" * 60)
    for i, pattern in enumerate(patterns, 1):
        display_pattern = pattern if len(pattern) <= 50 else pattern[:47] + "..."
        print(f"  {i}. '{display_pattern}'")
    print("-" * 60)
    print(f"총 {len(patterns)}개 패턴 적용\n")
    
    # 제거 결과 출력
    if removal_stats:
        print("🗑️  제거된 반복 문장:")
        print("-" * 60)
        total_removed = 0
        for pattern, count in removal_stats.items():
            display_pattern = pattern if len(pattern) <= 40 else pattern[:37] + "..."
            print(f"  • '{display_pattern}': {count}회 제거")
            total_removed += count
        print("-" * 60)
        print(f"✓ 총 {total_removed}개 반복 문장 제거됨\n")
    else:
        print("ℹ️  제거된 문장 없음 (패턴이 텍스트에 없음)\n")
else:
    print("ℹ️  ignores.txt 파일 없음 - 모든 텍스트 유지\n")

print("📊 텍스트 청크 분할 중...")
print(f"✓ 총 41개의 청크로 분할되었습니다.\n")

print("\n" + "="*60)
print("출력 테스트 완료!")
print("="*60)
