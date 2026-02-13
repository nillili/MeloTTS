import PyPDF2
from melo.api import TTS
import os

def extract_text_from_pdf(pdf_path):
    """
    PDF 파일에서 텍스트를 추출합니다.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text: # 빈 페이지가 아니면 추가
                    text += page_text + "\n" # 페이지 구분용 개행 추가
    except PyPDF2.errors.PdfReadError:
        print(f"오류: '{pdf_path}' 파일이 손상되었거나 유효한 PDF 파일이 아닙니다.")
        return ""
    except FileNotFoundError:
        print(f"오류: '{pdf_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return ""
    except Exception as e:
        print(f"PDF 텍스트 추출 중 예상치 못한 오류 발생: {e}")
        return ""
    return text

def convert_pdf_to_audio_with_melo(pdf_path, output_wav_path, speed=1.0, device='cpu'):
    """
    PDF 파일에서 텍스트를 추출하여 MeloTTS로 음성 파일(WAV)을 생성합니다.
    """
    print(f"'{pdf_path}'에서 텍스트를 추출하는 중...")
    extracted_text = extract_text_from_pdf(pdf_path)

    if not extracted_text.strip():
        print("PDF에서 추출된 유효한 텍스트가 없습니다. 음성 변환을 건너뜝니다.")
        return False

    print("MeloTTS 모델을 로드하는 중...")
    try:
        model = TTS(language='KR', device=device)
        speaker_ids = model.hps.data.spk2id
    except Exception as e:
        print(f"MeloTTS 모델 로드 중 오류 발생: {e}")
        print("MeloTTS 설치 및 모델 다운로드 상태를 확인해주세요.")
        print("예: 'pip install melo' 및 'melo.api' 임포트 확인")
        return False

    print(f"추출된 텍스트를 음성으로 변환하여 '{output_wav_path}'에 저장하는 중...")
    try:
        # MeloTTS는 긴 텍스트를 한 번에 처리하기 어려울 수 있으므로,
        # 적절한 길이로 텍스트를 분할하여 처리하는 로직을 추가할 수 있습니다.
        # 여기서는 간단하게 전체 텍스트를 전달합니다.
        # 실제 사용 시 문장 단위 분할이 필요할 수 있습니다.
        model.tts_to_file(extracted_text, speaker_ids['KR'], output_wav_path, speed=speed)
        print(f"'{output_wav_path}' 파일이 성공적으로 생성되었습니다.")
        return True
    except Exception as e:
        print(f"음성 변환 중 오류 발생: {e}")
        print("MeloTTS가 너무 긴 텍스트를 처리하지 못하는 경우일 수 있습니다.")
        print("텍스트를 더 작은 덩어리로 나누어 시도해보세요.")
        return False

if __name__ == "__main__":
    # --- 설정 부분 ---
    input_pdf_file = "sample_korean_melo.pdf" # 변환할 PDF 파일명
    output_audio_file = "output_melo_korean.wav" # 저장될 음성 파일명
    tts_speed = 1.0 # 음성 속도 (1.0이 기본)
    tts_device = 'cpu' # 'cpu' 또는 'cuda:0' (GPU 사용 시)

    # --- 테스트용 PDF 파일 생성 (한글 텍스트 포함) ---
    # 실제 PDF 파일이 있다면 이 부분을 건너뛰고 input_pdf_file을 실제 파일명으로 설정하세요.
    # reportlab은 한글 폰트 설정이 복잡하여 여기서는 포함하지 않습니다.
    # 워드 프로세서(예: 한글, MS Word)로 생성된 한글 PDF 파일을 사용하는 것을 권장합니다.
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        # ReportLab의 기본 폰트는 한글을 지원하지 않으므로, 이 텍스트는 추출 시 깨질 수 있습니다.
        # 실제 사용 시에는 미리 한글이 포함된 PDF를 준비해주세요.
        sample_text_for_pdf = "안녕하세요. MeloTTS를 이용한 PDF 음성 변환 테스트입니다. 이 텍스트가 잘 들리기를 바랍니다."
        c = canvas.Canvas(input_pdf_file, pagesize=letter)
        c.setFont("Helvetica", 12) # 한글 폰트가 아니므로 PDF에서 텍스트 추출 시 문제가 될 수 있습니다.
        c.drawString(100, 750, sample_text_for_pdf)
        c.save()
        print(f"테스트용 PDF 파일 '{input_pdf_file}' 생성 완료. (주의: 한글 폰트 문제로 추출 오류 가능성 있음)")
    except ImportError:
        print("ReportLab이 설치되어 있지 않아 샘플 PDF를 생성할 수 없습니다.")
        print("직접 한글 PDF 파일을 준비하여 '{input_pdf_file}' 경로에 넣어주세요.")
    except Exception as e:
        print(f"테스트용 PDF 생성 중 오류 발생: {e}")

    # --- PDF를 음성으로 변환 ---
    success = convert_pdf_to_audio_with_melo(input_pdf_file, output_audio_file, speed=tts_speed, device=tts_device)

    if success:
        print("\n변환 완료: 생성된 오디오 파일을 확인해주세요.")
    else:
        print("\n오디오 변환에 실패했습니다. 위의 오류 메시지를 확인해주세요.")
