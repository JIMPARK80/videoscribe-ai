@echo off
echo YouTube Video to Text Extractor - Installation Script
echo YouTube 영상 텍스트 추출기 - 설치 스크립트
echo.

echo Checking Python installation...
echo Python 설치 확인중...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo 오류: Python이 설치되지 않았거나 PATH에 없습니다
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
echo Python 의존성 설치중...
pip install -r requirements.txt

echo.
echo Installation completed!
echo 설치 완료!
echo.
echo To run the GUI application: python gui_app.py
echo GUI 애플리케이션 실행: python gui_app.py
echo.
echo To run CLI version: python video_to_text.py [URL_OR_FILE_PATH]
echo CLI 버전 실행: python video_to_text.py [URL_OR_FILE_PATH]
echo.
pause 