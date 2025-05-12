from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
import tempfile
import shutil
import logging
import time
import markdown2
from io import BytesIO
import pypdf
from typing import List, Optional
from ocr_processor import process_document
from config import MISTRAL_API_KEY

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mistral OCR 서비스")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 출력 디렉토리도 정적 파일로 제공
os.makedirs("output", exist_ok=True)
app.mount("/output", StaticFiles(directory="output"), name="output")

@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    mistral_api_key: Optional[str] = Form(None),
    output_format: Optional[str] = Form("text")  # 'text' 또는 'html'
):
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
    
    try:
        # 파일 확장자 가져오기
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # API 키 설정 - 사용자 제공 또는 기본값 사용
        api_key = mistral_api_key if mistral_api_key else MISTRAL_API_KEY
        logger.debug(f"Using API key: {api_key[:5]}...")
        
        # OCR 처리
        result = process_document(temp_file_path, file_extension, api_key)
        
        # 응답 데이터 로깅
        logger.debug(f"OCR 결과: {result[:200] if isinstance(result, str) else result}")
        
        # HTML 출력이 요청된 경우
        if output_format == "html":
            try:
                # 결과를 HTML로 변환
                output_path = create_html_from_text(result, file.filename)
                
                # 파일 확장자 확인
                if output_path.endswith('.html'):
                    # HTML 파일 URL 생성 (브라우저에서 열기 위해)
                    file_name = os.path.basename(output_path)
                    file_url = f"/output/{file_name}"
                    
                    # HTML로 redirect (브라우저에서 바로 열릴 수 있도록)
                    html_content = f"""
                    <html>
                        <head>
                            <meta http-equiv="refresh" content="0;url={file_url}">
                        </head>
                        <body>
                            <p>OCR 결과를 여는 중입니다. 자동으로 리디렉션되지 않으면 <a href="{file_url}">여기</a>를 클릭하세요.</p>
                        </body>
                    </html>
                    """
                    return HTMLResponse(content=html_content)
                elif output_path.endswith('.pdf'):
                    return FileResponse(
                        path=output_path,
                        filename=f"OCR_{os.path.splitext(file.filename)[0]}.pdf",
                        media_type="application/pdf"
                    )
                else:
                    # 텍스트 파일로 대체
                    return FileResponse(
                        path=output_path,
                        filename=f"OCR_{os.path.splitext(file.filename)[0]}.txt",
                        media_type="text/plain"
                    )
            except Exception as e:
                logger.error(f"출력 파일 처리 중 오류: {str(e)}", exc_info=True)
                # 오류 발생 시 텍스트 결과로 대체
                return JSONResponse(content={"result": result, "error": "HTML/PDF 생성 실패: " + str(e)})
        else:
            # 텍스트 결과 반환
            return JSONResponse(content={"result": result})
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 임시 파일 삭제
        os.unlink(temp_file_path)

def create_html_from_text(text_content, original_filename):
    """
    OCR 결과 텍스트를 구조화된 HTML로 변환합니다.
    
    Args:
        text_content (str): 변환할 텍스트 내용
        original_filename (str): 원본 파일명
    
    Returns:
        str: 생성된 HTML 파일 경로
    """
    try:
        # 출력 디렉토리 생성
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 파일명 생성 (타임스탬프 포함)
        timestamp = int(time.time())
        base_filename = os.path.splitext(os.path.basename(original_filename))[0]
        
        # HTML 파일 생성
        html_filename = f"OCR_{base_filename}_{timestamp}.html"
        html_path = os.path.join(output_dir, html_filename)
        
        # 마크다운을 HTML로 변환
        html_content = markdown2.markdown(text_content)
        
        # 완전한 HTML 문서 생성
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>OCR 결과: {base_filename}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
                
                body {{
                    font-family: 'Noto Sans KR', Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    color: #333;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-top: 20px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f9fa;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    white-space: pre-wrap;
                    font-family: 'Noto Sans KR', monospace;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 20px 0;
                }}
                code {{
                    background-color: #f8f9fa;
                    padding: 2px 4px;
                    border-radius: 4px;
                    font-family: monospace;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    padding-left: 16px;
                    margin-left: 0;
                    color: #666;
                }}
                .timestamp {{
                    color: #888;
                    font-size: 0.8em;
                    margin-top: 20px;
                }}
                .original-text {{
                    margin-top: 30px;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>OCR 결과: {base_filename}</h1>
                <div>
                    {html_content}
                </div>
                <div class="original-text">
                    <h2>원본 텍스트</h2>
                    <pre>{text_content}</pre>
                </div>
                <p class="timestamp">생성 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        # HTML 파일 저장
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        # 텍스트 파일도 저장 (백업)
        txt_filename = f"OCR_{base_filename}_{timestamp}.txt"
        txt_path = os.path.join(output_dir, txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
            
        logger.info(f"텍스트 파일 생성: {txt_path}")
        logger.info(f"HTML 파일 생성: {html_path}")
        
        # HTML 파일 URL 생성
        html_url = f"/output/{html_filename}"
        
        # HTML 파일 경로 반환
        return html_path
        
    except Exception as e:
        # 오류 발생 시 텍스트 파일로 저장
        logger.error(f"HTML 생성 중 오류 발생: {str(e)}", exc_info=True)
        
        # 출력 디렉토리 생성
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 텍스트 파일로 저장
        timestamp = int(time.time())
        base_filename = os.path.splitext(os.path.basename(original_filename))[0]
        txt_filename = f"OCR_{base_filename}_{timestamp}.txt"
        txt_path = os.path.join(output_dir, txt_filename)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return txt_path

@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    # 인덱스 페이지 제공
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    logger.info("Starting OCR service")
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True) 