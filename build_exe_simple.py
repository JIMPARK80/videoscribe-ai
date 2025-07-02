"""
초보자를 위한 실행파일(.exe) 생성 스크립트
간단한 더블클릭으로 실행 가능한 파일을 만듭니다.
"""

import os
import sys
import subprocess

def create_exe():
    """실행파일 생성"""
    print("🎬 Video to Text Converter - 실행파일 생성 중...")
    print("=" * 50)
    
    # PyInstaller 설치 확인
    try:
        import PyInstaller
        print("✅ PyInstaller 설치됨")
    except ImportError:
        print("📦 PyInstaller 설치 중...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller 설치 완료")
    
    # 실행파일 빌드 명령어
    build_command = [
        "pyinstaller",
        "--onefile",                    # 하나의 실행파일로 생성
        "--windowed",                   # 콘솔 창 숨김
        "--name=VideoToText",           # 실행파일 이름
        "--icon=assets/Youtube_text.ico",  # 아이콘
        "--add-data=src;src",           # src 폴더 포함
        "--add-data=config;config",     # config 폴더 포함
        "--add-data=bin;bin",          # bin 폴더 포함
        "--hidden-import=whisper",      # 숨겨진 import
        "--hidden-import=torch",
        "--hidden-import=yt_dlp",
        "--hidden-import=moviepy",
        "streamlit_app.py"
    ]
    
    print("🔨 실행파일 빌드 중... (5-10분 소요)")
    print("💡 이 과정은 시간이 걸립니다. 기다려주세요!")
    
    try:
        subprocess.run(build_command, check=True)
        print("\n🎉 실행파일 생성 완료!")
        print("📁 위치: dist/VideoToText.exe")
        print("💡 이 파일을 다른 컴퓨터에서도 사용할 수 있습니다!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 빌드 실패: {e}")
        print("💡 다시 시도하거나 관리자 권한으로 실행해보세요.")

if __name__ == "__main__":
    create_exe() 