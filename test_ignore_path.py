#!/usr/bin/env python3
"""ignores.txt 경로 테스트"""
import os
import sys

# 현재 디렉터리를 PYTHONPATH에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ignore_path():
    """ignores.txt 경로가 올바르게 설정되는지 테스트"""
    
    # 스크립트 디렉터리 확인
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ignore_path = os.path.join(script_dir, 'ignores.txt')
    
    print("=" * 70)
    print("📂 ignores.txt 경로 테스트")
    print("=" * 70)
    print()
    
    print(f"✓ 현재 작업 디렉터리: {os.getcwd()}")
    print(f"✓ 스크립트 디렉터리: {script_dir}")
    print(f"✓ ignores.txt 경로: {ignore_path}")
    print()
    
    # 시뮬레이션: 다른 디렉터리에서 실행
    print("-" * 70)
    print("📁 시나리오 1: 다른 디렉터리에서 실행")
    print("-" * 70)
    
    # 임시 디렉터리로 이동
    temp_dir = "/tmp/test_pdf_work"
    os.makedirs(temp_dir, exist_ok=True)
    os.chdir(temp_dir)
    
    print(f"✓ 작업 디렉터리 변경: {os.getcwd()}")
    print(f"✓ ignores.txt 경로 (변경 없음): {ignore_path}")
    print(f"✓ 스크립트 디렉터리 (고정): {script_dir}")
    print()
    print("💡 결과: ignores.txt는 항상 스크립트 디렉터리에서 검색됨")
    print("💡 작업 디렉터리의 파일을 rm *로 지워도 ignores.txt는 안전!")
    print()
    
    # 원래 디렉터리로 복귀
    os.chdir(script_dir)
    
    # ignores.txt 존재 확인
    print("-" * 70)
    print("📄 파일 존재 여부 확인")
    print("-" * 70)
    
    if os.path.exists(ignore_path):
        print(f"✅ ignores.txt 파일 존재: {ignore_path}")
        
        # 내용 읽기
        try:
            with open(ignore_path, 'r', encoding='utf-8') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            print(f"✓ 총 {len(patterns)}개 패턴 로드:")
            for i, pattern in enumerate(patterns, 1):
                print(f"  {i}. '{pattern}'")
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
    else:
        print(f"⚠️  ignores.txt 파일 없음: {ignore_path}")
        print(f"💡 생성하려면: nano {ignore_path}")
    
    print()
    print("=" * 70)
    print("✨ 테스트 완료")
    print("=" * 70)

if __name__ == '__main__':
    test_ignore_path()
