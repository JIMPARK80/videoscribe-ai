#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def main():
    print("=== VideoToTextConverter 시작 테스트 ===")
    print(f"Python 버전: {sys.version}")
    print(f"실행 경로: {os.getcwd()}")
    print(f"스크립트 경로: {os.path.dirname(os.path.abspath(__file__))}")
    
    # PyInstaller 환경 체크
    if hasattr(sys, '_MEIPASS'):
        print(f"PyInstaller 번들 경로: {sys._MEIPASS}")
        print(f"번들 내용: {os.listdir(sys._MEIPASS)}")
    else:
        print("개발 모드에서 실행 중")
    
    print("\n=== 라이브러리 임포트 테스트 ===")
    
    # 기본 라이브러리
    try:
        import tkinter as tk
        print("✅ tkinter 임포트 성공")
    except Exception as e:
        print(f"❌ tkinter 임포트 실패: {e}")
        return
    
    try:
        import threading
        print("✅ threading 임포트 성공")
    except Exception as e:
        print(f"❌ threading 임포트 실패: {e}")
        return
    
    # AI 라이브러리
    try:
        import torch
        print(f"✅ torch 임포트 성공 (버전: {torch.__version__})")
        print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
    except Exception as e:
        print(f"❌ torch 임포트 실패: {e}")
        return
    
    try:
        import whisper
        print(f"✅ whisper 임포트 성공")
    except Exception as e:
        print(f"❌ whisper 임포트 실패: {e}")
        return
    
    try:
        import moviepy.editor
        print("✅ moviepy 임포트 성공")
    except Exception as e:
        print(f"❌ moviepy 임포트 실패: {e}")
        return
    
    print("\n=== GUI 시작 테스트 ===")
    try:
        root = tk.Tk()
        root.title("빌드 테스트 성공!")
        root.geometry("400x200")
        
        label = tk.Label(root, text="모든 라이브러리가 정상적으로 로드되었습니다!\n이 창이 보이면 빌드 성공!", 
                        font=("Arial", 12), justify="center")
        label.pack(expand=True)
        
        def close_app():
            print("GUI 테스트 완료")
            root.destroy()
        
        close_btn = tk.Button(root, text="닫기", command=close_app)
        close_btn.pack(pady=10)
        
        print("GUI 창을 표시합니다...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ GUI 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("=== 모든 테스트 완료 ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        input("Enter 키를 눌러 종료...") 