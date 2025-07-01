"""
FFmpeg 경로 설정 모듈
FFmpeg Path Configuration Module
"""

import os
import sys
from pathlib import Path


def setup_ffmpeg_path():
    """FFmpeg 경로를 설정합니다 / Setup FFmpeg path"""
    
    # 현재 스크립트 위치 기준으로 bin 폴더 경로 찾기
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 번들된 실행파일인 경우
        base_path = Path(sys._MEIPASS)
    else:
        # 개발 모드인 경우
        base_path = Path(__file__).parent.parent
    
    ffmpeg_path = base_path / "bin" / "ffmpeg.exe"
    
    if ffmpeg_path.exists():
        # MoviePy 설정에 FFmpeg 경로 추가
        try:
            import moviepy.config as config
            config.FFMPEG_BINARY = str(ffmpeg_path)
            
            # 환경변수에도 추가 (추가 보장)
            bin_dir = str(base_path / "bin")
            current_path = os.environ.get('PATH', '')
            if bin_dir not in current_path:
                os.environ['PATH'] = f"{bin_dir};{current_path}"
                
        except ImportError:
            pass  # moviepy가 아직 import되지 않은 경우
    
    return ffmpeg_path.exists()


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path) 