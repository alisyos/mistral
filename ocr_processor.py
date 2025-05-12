import os
import tempfile
import base64
import json
import requests
from pdf2image import convert_from_path

# Mistral API 엔드포인트
MISTRAL_API_ENDPOINT = "https://api.mistral.ai/v1"

def process_document(file_path, file_extension, mistral_api_key):
    """
    이미지 또는 PDF 파일을 OCR 처리합니다.
    
    Args:
        file_path (str): 처리할 파일 경로
        file_extension (str): 파일 확장자 (.pdf, .jpg, .png 등)
        mistral_api_key (str): Mistral API 키
    
    Returns:
        str: OCR 결과 텍스트
    """
    if file_extension.lower() == '.pdf':
        # PDF 파일 처리
        return process_file_with_ocr(file_path, "application/pdf", mistral_api_key)
    elif file_extension.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        # 이미지 파일 처리
        return process_file_with_ocr(file_path, "image/jpeg", mistral_api_key)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {file_extension}")

def process_image(image_path, mistral_api_key):
    """
    단일 이미지를 OCR 처리합니다. (Legacy 함수)
    
    Args:
        image_path (str): 이미지 파일 경로
        mistral_api_key (str): Mistral API 키
    
    Returns:
        str: OCR 결과 텍스트
    """
    return process_file_with_ocr(image_path, "image/jpeg", mistral_api_key)

def process_pdf(pdf_path, mistral_api_key):
    """
    PDF 파일을 OCR 처리합니다. (Legacy 함수)
    
    Args:
        pdf_path (str): PDF 파일 경로
        mistral_api_key (str): Mistral API 키
    
    Returns:
        str: 모든 페이지의 OCR 결과를 결합한 텍스트
    """
    return process_file_with_ocr(pdf_path, "application/pdf", mistral_api_key)

def process_file_with_ocr(file_path, mime_type, mistral_api_key):
    """
    파일을 Mistral OCR API를 사용하여 처리합니다.
    
    Args:
        file_path (str): 파일 경로
        mime_type (str): MIME 타입 ("image/jpeg" 또는 "application/pdf")
        mistral_api_key (str): Mistral API 키
    
    Returns:
        str: OCR 결과 텍스트
    """
    try:
        print(f"Mistral OCR 처리 시작: {os.path.basename(file_path)}")
        
        # 파일을 base64로 인코딩
        with open(file_path, "rb") as file:
            file_data = file.read()
            file_base64 = base64.b64encode(file_data).decode('utf-8')
        
        # 파일 유형에 따라 다른 처리
        if mime_type == "application/pdf":
            # PDF 파일
            document_type = "document_url"
            file_url = f"data:application/pdf;base64,{file_base64}"
        elif mime_type.startswith("image/"):
            # 이미지 파일
            document_type = "image_url"
            file_url = f"data:{mime_type};base64,{file_base64}"
        else:
            raise ValueError(f"지원하지 않는 MIME 타입입니다: {mime_type}")
        
        # OCR API 요청 준비
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {mistral_api_key}"
        }
        
        # 요청 페이로드 구성
        payload = {
            "model": "mistral-ocr-latest",
            "document": {
                "type": document_type
            }
        }
        
        # 파일 유형에 따라 URL 필드 설정
        if document_type == "document_url":
            payload["document"]["document_url"] = file_url
        else:
            payload["document"]["image_url"] = file_url
        
        # OCR API 호출
        print(f"OCR API 호출 중...")
        
        response = requests.post(
            f"{MISTRAL_API_ENDPOINT}/ocr",
            headers=headers,
            json=payload
        )
        
        # 응답 확인
        if response.status_code != 200:
            print(f"OCR API 오류: {response.status_code}, {response.text}")
            return f"OCR API 응답 오류: {response.status_code}, {response.text}"
        
        # 응답 처리
        try:
            ocr_result = response.json()
            print(f"OCR 응답: {ocr_result}")
            
            # 텍스트 추출
            if "text" in ocr_result and ocr_result["text"]:
                # 단일 텍스트 필드
                return ocr_result["text"]
            elif "pages" in ocr_result and ocr_result["pages"]:
                # 여러 페이지 처리
                pages_text = []
                for i, page in enumerate(ocr_result["pages"]):
                    if "markdown" in page and page["markdown"]:
                        pages_text.append(f"--- 페이지 {i+1} ---\n{page['markdown']}")
                    elif "text" in page and page["text"]:
                        pages_text.append(f"--- 페이지 {i+1} ---\n{page['text']}")
                
                if pages_text:
                    return "\n\n".join(pages_text)
                
            return "OCR 처리는 완료되었지만 텍스트를 추출할 수 없습니다."
        
        except Exception as e:
            print(f"OCR 결과 처리 중 오류: {str(e)}")
            return f"OCR 처리는 완료되었지만 결과 파싱 중 오류가 발생했습니다: {str(e)}"
        
    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {str(e)}")
        
        if "model which does not have" in str(e):
            return f"OCR 모델 오류: 모델이 지원되지 않거나 결제 플랜이 활성화되지 않았습니다. 오류: {str(e)}"
        elif "404" in str(e):
            return f"OCR API 오류: API 엔드포인트가 존재하지 않습니다. 오류: {str(e)}"
        else:
            return f"OCR 처리 중 오류가 발생했습니다: {str(e)}" 