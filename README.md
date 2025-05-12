# Mistral OCR 서비스

이 프로젝트는 Mistral API를 활용하여 이미지와 PDF 파일에서 OCR(광학 문자 인식)을 수행하는 웹 애플리케이션입니다. 기본 OCR 결과를 Mistral API를 통해 개선하여 더 정확한 텍스트 추출을 제공합니다.

## 주요 기능

- 다양한 이미지 형식(JPG, PNG, BMP, TIFF) 지원
- PDF 파일 처리 (모든 페이지를 개별적으로 OCR 처리)
- Mistral AI를 통한 OCR 결과 품질 개선
- 원본 레이아웃 보존 (테이블, 들여쓰기, 번호 매기기 등)
- 결과 복사 및 저장 기능

## 설치 방법

### 사전 요구사항

- Python 3.8 이상
- Tesseract OCR 엔진
- Poppler (PDF 처리용)

### Tesseract OCR 설치

#### Windows
1. [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki) 다운로드 및 설치
2. 환경 변수에 Tesseract 경로 추가 (예: `C:\Program Files\Tesseract-OCR`)

#### macOS
```bash
brew install tesseract
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get install tesseract-ocr
```

### Poppler 설치

#### Windows
[Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) 다운로드 및 환경 변수 설정

#### macOS
```bash
brew install poppler
```

#### Linux
```bash
sudo apt-get install poppler-utils
```

### 프로젝트 설치

1. 저장소 클론
```bash
git clone https://github.com/yourusername/mistral-ocr.git
cd mistral-ocr
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### Mistral API 키 설정

Mistral API 키는 다음 두 가지 방법으로 설정할 수 있습니다:

1. **config.py 파일에 API 키 저장 (권장)**
   - 프로젝트 루트 디렉토리에 `config.py` 파일 생성 또는 편집
   - 다음 형식으로 API 키 추가:
   ```python
   MISTRAL_API_KEY = "your_api_key_here"
   ```
   - 이 파일은 `.gitignore`에 포함되어 있어 실수로 API 키가 공개되는 것을 방지합니다.

2. **웹 인터페이스에서 API 키 입력**
   - OCR 처리 시 웹 인터페이스에서 API 키를 직접 입력할 수도 있습니다.
   - 이 경우 API 키는 일시적으로만 사용되며 저장되지 않습니다.

## 사용 방법

1. 서버 실행
```bash
python main.py
```

2. 웹 브라우저에서 접속
```
http://localhost:8000
```

3. 이미지 또는 PDF 파일 업로드 및 처리
   - `config.py`에 API 키가 설정되어 있다면, 추가 입력 없이 자동 처리됩니다.
   - 또는 웹 인터페이스에서 API 키를 직접 입력할 수 있습니다.

## 참고사항

- 대용량 PDF 파일은 처리 시간이 오래 걸릴 수 있습니다.
- Mistral API는 사용량에 따라 비용이 발생할 수 있습니다.
- 개인정보가 포함된 문서 처리 시 주의하세요.

## 라이선스

MIT 라이선스

## 문의 및 기여

이슈나 기여는 GitHub 저장소를 통해 제출해주세요. 