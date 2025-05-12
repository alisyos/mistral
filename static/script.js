document.addEventListener('DOMContentLoaded', function() {
    const ocrForm = document.getElementById('ocrForm');
    const fileInput = document.getElementById('fileInput');
    const apiKeyInput = document.getElementById('apiKey');
    const submitBtn = document.getElementById('submitBtn');
    const resultSection = document.getElementById('resultSection');
    const resultText = document.getElementById('resultText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const copyBtn = document.getElementById('copyBtn');

    // API 키 로컬 스토리지에서 불러오기
    const savedApiKey = localStorage.getItem('mistral_api_key');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // 폼 제출 처리
    ocrForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // 입력 검증
        if (!fileInput.files.length) {
            alert('파일을 선택해주세요.');
            return;
        }
        
        if (!apiKeyInput.value.trim()) {
            alert('Mistral API 키를 입력해주세요.');
            return;
        }
        
        // API 키 저장
        localStorage.setItem('mistral_api_key', apiKeyInput.value);
        
        // 로딩 상태 표시
        submitBtn.disabled = true;
        resultText.textContent = '';
        resultSection.style.display = 'flex';
        loadingSpinner.style.display = 'block';
        
        try {
            // FormData 객체 생성
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('mistral_api_key', apiKeyInput.value);
            
            // OCR API 호출
            const response = await fetch('/ocr', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`서버 오류: ${response.status}`);
            }
            
            const data = await response.json();
            
            // 결과 표시
            resultText.textContent = data.result;
            loadingSpinner.style.display = 'none';
            
        } catch (error) {
            console.error('OCR 처리 중 오류:', error);
            resultText.textContent = `오류 발생: ${error.message}`;
            loadingSpinner.style.display = 'none';
        } finally {
            submitBtn.disabled = false;
        }
    });
    
    // 클립보드에 복사 기능
    copyBtn.addEventListener('click', function() {
        const textToCopy = resultText.textContent;
        
        if (!textToCopy) {
            alert('복사할 텍스트가 없습니다.');
            return;
        }
        
        // 텍스트 복사 기능
        navigator.clipboard.writeText(textToCopy)
            .then(() => {
                // 복사 성공 표시
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '복사 완료!';
                
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('클립보드 복사 실패:', err);
                alert('클립보드 복사에 실패했습니다.');
            });
    });
    
    // 파일 입력 변경 시 파일명 표시
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            const fileSize = (this.files[0].size / (1024 * 1024)).toFixed(2);
            
            // 파일 크기 제한 (20MB)
            if (this.files[0].size > 20 * 1024 * 1024) {
                alert('파일 크기는 20MB 이하여야 합니다.');
                this.value = '';
                return;
            }
            
            this.nextElementSibling.textContent = `선택된 파일: ${fileName} (${fileSize}MB)`;
        } else {
            this.nextElementSibling.textContent = '지원 형식: JPG, PNG, PDF, BMP, TIFF';
        }
    });
}); 