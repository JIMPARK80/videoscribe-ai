@echo off
chcp 65001 >nul
title 🎬 Video to Text Converter - Local Setup

echo.
echo ████████████████████████████████████████████████
echo 🎬 Video to Text Converter - 로컬 설치
echo ████████████████████████████████████████████████
echo.

:: Python 설치 확인
echo 🔍 Python 설치 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Python이 설치되지 않았습니다!
    echo.
    echo 📥 Python 설치 방법:
    echo    1. https://python.org/downloads/ 방문
    echo    2. Python 3.8+ 다운로드 및 설치
    echo    3. 설치 시 "Add Python to PATH" 반드시 체크
    echo    4. 재부팅 후 다시 실행
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% 설치됨

:: pip 업그레이드
echo.
echo 🔧 pip 업그레이드 중...
python -m pip install --upgrade pip --quiet

:: 가상환경 확인 및 생성
if not exist "venv" (
    echo.
    echo 📦 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
)

:: 가상환경 활성화
echo.
echo 🚀 가상환경 활성화 중...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상환경 활성화 실패
    pause
    exit /b 1
)

:: 의존성 설치
echo.
echo 📚 필요한 라이브러리 설치 중... (시간이 걸릴 수 있습니다)
echo    💡 처음 설치 시 2-5분 소요됩니다
echo.

if exist "config\requirements.txt" (
    pip install -r config\requirements.txt --quiet
) else (
    echo ❌ config\requirements.txt 파일을 찾을 수 없습니다
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo ❌ 라이브러리 설치 실패
    echo.
    echo 🔧 문제 해결 방법:
    echo    1. 인터넷 연결 확인
    echo    2. 관리자 권한으로 실행
    echo    3. 바이러스 백신 일시 해제
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 모든 라이브러리 설치 완료!

:: GPU 확인 (선택사항)
echo.
echo 🎮 GPU 가속 확인 중...
python -c "import torch; print('✅ GPU 사용 가능:', torch.cuda.is_available())" 2>nul
if errorlevel 1 (
    echo ⚠️  GPU 확인 실패 (CPU 모드로 실행됨)
)

:: 애플리케이션 실행
echo.
echo 🎬 Video to Text Converter 실행 중...
echo.
echo ████████████████████████████████████████████████
echo 📱 웹브라우저가 자동으로 열립니다
echo 🛑 종료하려면 이 창에서 Ctrl+C 누르세요
echo ████████████████████████████████████████████████
echo.

streamlit run streamlit_app.py

echo.
echo 👋 애플리케이션이 종료되었습니다
pause 