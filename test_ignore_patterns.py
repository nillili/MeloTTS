#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ignores.txt 기능 테스트 스크립트
"""

import sys
import os

# pdf2mp3 모듈 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf2mp3 import load_ignore_patterns, remove_ignore_patterns

def test_load_ignore_patterns():
    """ignores.txt 로딩 테스트"""
    print("=" * 60)
    print("테스트 1: ignores.txt 로딩")
    print("=" * 60)
    
    # 테스트 파일 생성
    test_file = 'test_ignores.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("# 테스트 주석\n")
        f.write("흐르는 강물처럼\n")
        f.write("\n")  # 빈 줄
        f.write("문학사\n")
        f.write("# 또 다른 주석\n")
        f.write("저작권\n")
    
    patterns = load_ignore_patterns(test_file)
    print(f"로드된 패턴 수: {len(patterns)}")
    for i, p in enumerate(patterns, 1):
        print(f"  {i}. '{p}'")
    
    # 정리
    os.remove(test_file)
    
    assert len(patterns) == 3, "3개 패턴이 로드되어야 함"
    print("✅ 테스트 1 통과\n")


def test_remove_ignore_patterns():
    """패턴 제거 테스트"""
    print("=" * 60)
    print("테스트 2: 패턴 제거")
    print("=" * 60)
    
    test_text = """
    흐르는 강물처럼
    문학사
    
    첫 번째 본문 내용입니다.
    이것은 중요한 내용입니다.
    
    흐르는 강물처럼
    문학사
    
    두 번째 본문 내용입니다.
    
    흐르는 강물처럼
    저작권 © 2024
    """
    
    patterns = ["흐르는 강물처럼", "문학사", "저작권"]
    
    cleaned_text, removed_count = remove_ignore_patterns(test_text, patterns)
    
    print(f"원본 길이: {len(test_text)} 문자")
    print(f"정리 후: {len(cleaned_text)} 문자")
    print(f"제거된 패턴 수: {removed_count}개")
    print("\n정리된 텍스트:")
    print("-" * 60)
    print(cleaned_text)
    print("-" * 60)
    
    # 검증
    assert "흐르는 강물처럼" not in cleaned_text, "흐르는 강물처럼이 제거되어야 함"
    assert "문학사" not in cleaned_text, "문학사가 제거되어야 함"
    assert "첫 번째 본문" in cleaned_text, "본문은 유지되어야 함"
    assert "두 번째 본문" in cleaned_text, "본문은 유지되어야 함"
    assert removed_count >= 3, "최소 3개 이상 제거되어야 함"
    
    print("✅ 테스트 2 통과\n")


def test_case_insensitive():
    """대소문자 무관 테스트"""
    print("=" * 60)
    print("테스트 3: 대소문자 무관")
    print("=" * 60)
    
    test_text = """
    Copyright © 2024
    COPYRIGHT
    copyright
    CoPyRiGhT
    
    본문 내용
    """
    
    patterns = ["copyright"]
    
    cleaned_text, removed_count = remove_ignore_patterns(test_text, patterns)
    
    print(f"제거된 패턴 수: {removed_count}개")
    print("\n정리된 텍스트:")
    print("-" * 60)
    print(cleaned_text)
    print("-" * 60)
    
    # 검증
    assert "copyright" not in cleaned_text.lower(), "모든 copyright 변형이 제거되어야 함"
    assert "본문" in cleaned_text, "본문은 유지되어야 함"
    assert removed_count >= 4, "최소 4개 이상 제거되어야 함"
    
    print("✅ 테스트 3 통과\n")


def test_special_characters():
    """특수문자 포함 패턴 테스트"""
    print("=" * 60)
    print("테스트 4: 특수문자 포함 패턴")
    print("=" * 60)
    
    test_text = """
    저작권 © 2024
    본문 내용
    All Rights Reserved (C)
    """
    
    patterns = ["저작권 © 2024", "All Rights Reserved (C)"]
    
    cleaned_text, removed_count = remove_ignore_patterns(test_text, patterns)
    
    print(f"제거된 패턴 수: {removed_count}개")
    print("\n정리된 텍스트:")
    print("-" * 60)
    print(cleaned_text)
    print("-" * 60)
    
    # 검증
    assert "저작권 ©" not in cleaned_text, "저작권 정보가 제거되어야 함"
    assert "All Rights Reserved" not in cleaned_text, "권리 정보가 제거되어야 함"
    assert "본문" in cleaned_text, "본문은 유지되어야 함"
    
    print("✅ 테스트 4 통과\n")


def test_empty_patterns():
    """빈 패턴 리스트 테스트"""
    print("=" * 60)
    print("테스트 5: 빈 패턴 리스트")
    print("=" * 60)
    
    test_text = "원본 텍스트 내용"
    patterns = []
    
    cleaned_text, removed_count = remove_ignore_patterns(test_text, patterns)
    
    print(f"제거된 패턴 수: {removed_count}개")
    
    # 검증
    assert cleaned_text == test_text, "텍스트가 변경되지 않아야 함"
    assert removed_count == 0, "제거된 패턴이 없어야 함"
    
    print("✅ 테스트 5 통과\n")


def test_korean_text():
    """한글 텍스트 전체 테스트"""
    print("=" * 60)
    print("테스트 6: 실제 시나리오 (한글)")
    print("=" * 60)
    
    test_text = """
    열세 번째 이야기
    출판사명
    
    제1장
    
    긴 여름이 지나가고 있었습니다.
    마을에는 평화가 찾아왔습니다.
    
    열세 번째 이야기
    출판사명
    
    제2장
    
    가을이 왔습니다.
    단풍이 아름다웠습니다.
    
    열세 번째 이야기
    페이지 3
    """
    
    patterns = ["열세 번째 이야기", "출판사명", "페이지"]
    
    cleaned_text, removed_count = remove_ignore_patterns(test_text, patterns)
    
    print(f"원본 길이: {len(test_text)} 문자")
    print(f"정리 후: {len(cleaned_text)} 문자")
    print(f"제거된 패턴 수: {removed_count}개")
    print(f"감소율: {(1 - len(cleaned_text)/len(test_text))*100:.1f}%")
    print("\n정리된 텍스트:")
    print("-" * 60)
    print(cleaned_text)
    print("-" * 60)
    
    # 검증
    assert "열세 번째" not in cleaned_text, "책 제목이 제거되어야 함"
    assert "출판사명" not in cleaned_text, "출판사명이 제거되어야 함"
    assert "긴 여름" in cleaned_text, "본문 내용은 유지되어야 함"
    assert "가을이 왔습니다" in cleaned_text, "본문 내용은 유지되어야 함"
    assert removed_count >= 4, "최소 4개 이상 제거되어야 함"
    
    print("✅ 테스트 6 통과\n")


def main():
    """모든 테스트 실행"""
    print("\n")
    print("🧪 ignores.txt 기능 테스트 시작")
    print("\n")
    
    try:
        test_load_ignore_patterns()
        test_remove_ignore_patterns()
        test_case_insensitive()
        test_special_characters()
        test_empty_patterns()
        test_korean_text()
        
        print("=" * 60)
        print("🎉 모든 테스트 통과!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
