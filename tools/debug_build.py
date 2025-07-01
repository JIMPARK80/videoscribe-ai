import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import traceback
import subprocess
import shutil

# PyInstaller 디버그 정보
def get_debug_info():
    """Get system debug information"""
    info = []
    info.append(f"Python version: {sys.version}")
    info.append(f"Platform: {sys.platform}")
    info.append(f"Current working directory: {os.getcwd()}")
    
    # PyInstaller 환경 체크
    if hasattr(sys, '_MEIPASS'):
        info.append(f"PyInstaller bundle detected: {sys._MEIPASS}")
        info.append(f"Bundle contents: {os.listdir(sys._MEIPASS)}")
    else:
        info.append("Running in development mode")
    
    # FFmpeg 체크
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        info.append(f"FFmpeg found: {ffmpeg_path}")
    else:
        info.append("FFmpeg NOT found in PATH")
    
    return "\n".join(info)

class DebugVideoToTextGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Debug Video to Text - 디버그 모드")
        self.root.geometry("900x700")
        
        self.create_widgets()
        
        # 시작할 때 디버그 정보 표시
        self.show_debug_info()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        ttk.Label(main_frame, text="Debug Mode - 디버그 모드", 
                 font=("Arial", 16, "bold")).grid(row=0, column=0, pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Video File:").grid(row=0, column=0, sticky=tk.W)
        self.file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_var).grid(row=0, column=1, 
                                                              sticky=(tk.W, tk.E), 
                                                              padx=(10, 10))
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_file).grid(row=0, column=2)
        
        # Test buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="1. Test Imports", 
                  command=self.test_imports).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="2. Test FFmpeg", 
                  command=self.test_ffmpeg).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="3. Test Whisper", 
                  command=self.test_whisper).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="4. Test Video", 
                  command=self.test_video_processing).grid(row=0, column=3, padx=(5, 0))
        
        # Debug output
        ttk.Label(main_frame, text="Debug Output:").grid(row=3, column=0, sticky=tk.W)
        self.debug_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=25)
        self.debug_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def log(self, message):
        """Add message to debug output"""
        self.debug_text.insert(tk.END, f"{message}\n")
        self.debug_text.see(tk.END)
        self.root.update()
    
    def show_debug_info(self):
        """Show system debug information"""
        self.log("=== SYSTEM DEBUG INFO ===")
        self.log(get_debug_info())
        self.log("\n" + "="*50 + "\n")
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_var.set(filename)
    
    def test_imports(self):
        """Test importing all required libraries"""
        self.log("=== TESTING IMPORTS ===")
        
        libraries = [
            ("os", "os"),
            ("sys", "sys"), 
            ("tempfile", "tempfile"),
            ("shutil", "shutil"),
            ("pathlib", "pathlib"),
            ("whisper", "whisper"),
            ("moviepy", "moviepy.editor"),
            ("yt_dlp", "yt_dlp"),
            ("torch", "torch"),
            ("torchaudio", "torchaudio")
        ]
        
        for name, module in libraries:
            try:
                __import__(module)
                self.log(f"✅ {name}: OK")
            except Exception as e:
                self.log(f"❌ {name}: FAILED - {e}")
        
        self.log("")
    
    def test_ffmpeg(self):
        """Test FFmpeg availability"""
        self.log("=== TESTING FFMPEG ===")
        
        # Check system PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            self.log(f"✅ FFmpeg found in PATH: {ffmpeg_path}")
            
            # Test FFmpeg version
            try:
                result = subprocess.run([ffmpeg_path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                version_line = result.stdout.split('\n')[0]
                self.log(f"✅ FFmpeg version: {version_line}")
            except Exception as e:
                self.log(f"❌ FFmpeg version check failed: {e}")
        else:
            self.log("❌ FFmpeg NOT found in system PATH")
        
        # Check moviepy can find FFmpeg
        try:
            from moviepy.config import FFMPEG_BINARY
            self.log(f"📁 MoviePy FFmpeg path: {FFMPEG_BINARY}")
        except Exception as e:
            self.log(f"❌ MoviePy FFmpeg config error: {e}")
        
        # Test creating a VideoFileClip
        try:
            from moviepy.editor import VideoFileClip
            self.log("✅ VideoFileClip import: OK")
        except Exception as e:
            self.log(f"❌ VideoFileClip import failed: {e}")
        
        self.log("")
    
    def test_whisper(self):
        """Test Whisper model loading"""
        self.log("=== TESTING WHISPER ===")
        
        try:
            import whisper
            self.log("✅ Whisper import: OK")
            
            # Check available models
            models = whisper.available_models()
            self.log(f"📋 Available models: {models}")
            
            # Try loading tiny model
            self.log("🔄 Loading tiny model...")
            model = whisper.load_model("tiny")
            self.log("✅ Tiny model loaded successfully!")
            
            # Check model device
            device = next(model.parameters()).device
            self.log(f"🖥️ Model device: {device}")
            
        except Exception as e:
            self.log(f"❌ Whisper test failed: {e}")
            self.log(f"Full error: {traceback.format_exc()}")
        
        self.log("")
    
    def test_video_processing(self):
        """Test actual video processing"""
        file_path = self.file_var.get().strip()
        
        if not file_path:
            self.log("❌ Please select a video file first")
            return
        
        if not os.path.exists(file_path):
            self.log(f"❌ File not found: {file_path}")
            return
        
        self.log("=== TESTING VIDEO PROCESSING ===")
        self.log(f"📁 Video file: {file_path}")
        
        try:
            # Test video file info
            from moviepy.editor import VideoFileClip
            self.log("🔄 Loading video file...")
            
            video = VideoFileClip(file_path)
            self.log(f"✅ Video loaded successfully!")
            self.log(f"📏 Duration: {video.duration:.2f} seconds")
            self.log(f"📐 Resolution: {video.size}")
            self.log(f"🎬 FPS: {video.fps}")
            
            # Check audio
            if video.audio is None:
                self.log("❌ No audio track found in video")
            else:
                self.log("✅ Audio track found")
            
            video.close()
            
            # Test audio extraction
            self.log("🔄 Testing audio extraction...")
            import tempfile
            
            temp_dir = tempfile.mkdtemp(prefix='debug_test_')
            self.log(f"📁 Temp directory: {temp_dir}")
            
            try:
                video = VideoFileClip(file_path)
                if video.audio:
                    audio_path = os.path.join(temp_dir, "test_audio.wav")
                    video.audio.write_audiofile(audio_path, verbose=False, logger=None)
                    
                    if os.path.exists(audio_path):
                        size = os.path.getsize(audio_path) / 1024 / 1024
                        self.log(f"✅ Audio extracted successfully! Size: {size:.2f} MB")
                        os.remove(audio_path)
                    else:
                        self.log("❌ Audio file was not created")
                else:
                    self.log("❌ No audio to extract")
                
                video.close()
                
            except Exception as e:
                self.log(f"❌ Audio extraction failed: {e}")
                self.log(f"Full error: {traceback.format_exc()}")
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            self.log(f"❌ Video processing test failed: {e}")
            self.log(f"Full error: {traceback.format_exc()}")
        
        self.log("")

def main():
    root = tk.Tk()
    app = DebugVideoToTextGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 