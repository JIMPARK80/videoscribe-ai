"""
GUI 애플리케이션 메인 런처
GUI Application Main Launcher
"""

import tkinter as tk

# 모듈 임포트
from src.ffmpeg_setup import setup_ffmpeg_path
from src.gui_interface import VideoToTextGUI

# FFmpeg 경로 설정 실행
setup_ffmpeg_path()


def main():
    """메인 애플리케이션 실행"""
    root = tk.Tk()
    app = VideoToTextGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 