"""최종 출력 형식 테스트"""
import sys
import os

# 현재 디렉터리를 PYTHONPATH에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf2mp3 import load_ignore_patterns, remove_ignore_patterns

def test_final_output():
    """최종 사용자가 보게 될 출력 형식 테스트"""
    
    # 1. 프로그램 시작 시 - 제외 패턴 목록 표시
    print("=" * 60)
    print("[2단계] 텍스트 전처리 및 분할")
    print("=" * 60)
    print()
    
    patterns = load_ignore_patterns('ignores.txt')
    
    if patterns:
        print("📝 제외 패턴 목록 (ignores.txt):")
        print("-" * 60)
        for i, pattern in enumerate(patterns, 1):
            print(f"  {i}. '{pattern}'")
        print("-" * 60)
        print(f"총 {len(patterns)}개 패턴 적용")
        print()
    else:
        print("ℹ️  ignores.txt 파일이 없거나 비어있습니다.")
        print("   반복 문장 제거 기능이 비활성화됩니다.")
        print()
    
    # 2. 패턴 제거 후 - 제거 통계 표시
    test_text = """
    흐르는 강물처럼
    이것은 본문입니다.
    문학사
    또 다른 본문입니다.
    저작권 © 2024
    흐르는 강물처럼
    마지막 본문입니다.
    문학사
    All Rights Reserved
    """
    
    if patterns:
        cleaned_text, total_removed = remove_ignore_patterns(test_text, patterns)
        
        if total_removed > 0:
            print("🗑️  제거된 반복 문장:")
            print("-" * 60)
            # 개별 통계는 로그에 이미 출력됨
            print(f"✓ 총 {total_removed}개 반복 문장 제거됨")
            print()
    
    # 3. 청크 분할 정보
    print(f"📊 총 41개 청크로 분할됨")
    print()

if __name__ == '__main__':
    test_final_output()
