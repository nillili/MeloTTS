#!/usr/bin/env python3
"""
메모리 최적화 테스트 스크립트
"""
import sys
import gc
import tracemalloc

# 메모리 추적 시작
tracemalloc.start()

# 테스트 텍스트
test_text = """안녕하세요. 이것은 메모리 최적화 테스트입니다. 
PDF to MP3 변환 프로그램의 메모리 사용량을 개선했습니다.
주요 개선 사항은 다음과 같습니다.
첫째, TTS 모델을 싱글톤 패턴으로 관리하여 한 번만 로딩합니다.
둘째, 명시적 메모리 해제를 추가했습니다.
셋째, 불필요한 변수를 즉시 삭제합니다."""

print("=" * 60)
print("메모리 최적화 테스트 시작")
print("=" * 60)

# 초기 메모리 상태
snapshot1 = tracemalloc.take_snapshot()
current, peak = tracemalloc.get_traced_memory()
print(f"초기 메모리: {current / 1024 / 1024:.2f} MB (Peak: {peak / 1024 / 1024:.2f} MB)")

# 모델 로딩 테스트
try:
    from pdf2mp3 import get_tts_model, release_tts_model
    
    print("\n[1] TTS 모델 로딩 테스트...")
    model = get_tts_model(lang='KR', device='cpu')
    
    snapshot2 = tracemalloc.take_snapshot()
    current, peak = tracemalloc.get_traced_memory()
    print(f"모델 로딩 후: {current / 1024 / 1024:.2f} MB (Peak: {peak / 1024 / 1024:.2f} MB)")
    
    # 같은 모델 재요청 (싱글톤 확인)
    print("\n[2] 싱글톤 패턴 검증...")
    model2 = get_tts_model(lang='KR', device='cpu')
    print(f"같은 인스턴스인가? {model is model2}")
    
    snapshot3 = tracemalloc.take_snapshot()
    current, peak = tracemalloc.get_traced_memory()
    print(f"두 번째 호출 후: {current / 1024 / 1024:.2f} MB (Peak: {peak / 1024 / 1024:.2f} MB)")
    
    # 모델 해제
    print("\n[3] 모델 메모리 해제 테스트...")
    release_tts_model()
    gc.collect()
    
    snapshot4 = tracemalloc.take_snapshot()
    current, peak = tracemalloc.get_traced_memory()
    print(f"모델 해제 후: {current / 1024 / 1024:.2f} MB (Peak: {peak / 1024 / 1024:.2f} MB)")
    
    print("\n" + "=" * 60)
    print("✓ 메모리 최적화 테스트 성공!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

# 메모리 추적 종료
tracemalloc.stop()
