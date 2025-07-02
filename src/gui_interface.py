"""
GUI 인터페이스 모듈
GUI Interface Module
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os

from .converter import VideoToTextConverter
from .ffmpeg_setup import get_resource_path


class VideoToTextGUI:
    """비디오 텍스트 변환 GUI 클래스"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Video File to Text Extractor / 비디오 파일 텍스트 추출기")
        self.root.geometry("800x600")
        
        # Window icon
        self._load_icon()
        
        # Initialize converter (will be loaded when needed)
        self.converter = None
        
        self.create_widgets()
    
    def _load_icon(self):
        """아이콘 로드"""
        try:
            icon_path = get_resource_path("assets/Youtube_text.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                print(f"Icon loaded: {icon_path}")
            else:
                print(f"Icon not found: {icon_path}")
        except Exception as e:
            print(f"Failed to load icon: {e}")
    
    def create_widgets(self):
        """GUI 위젯들을 생성합니다"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Video File to Text Converter", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        self._create_input_section(main_frame)
        
        # Options section
        self._create_options_section(main_frame)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Extract Text / 텍스트 추출", 
                                     command=self.start_processing, style="Accent.TButton")
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Progress section
        self._create_progress_section(main_frame)
        
        # Results section
        self._create_results_section(main_frame)
    
    def _create_input_section(self, parent):
        """입력 섹션 생성"""
        input_frame = ttk.LabelFrame(parent, text="Video Input / 비디오 입력", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Input type selection (Radio buttons)
        self.input_type = tk.StringVar(value="file")
        
        type_frame = ttk.Frame(input_frame)
        type_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        file_radio = ttk.Radiobutton(type_frame, text="📁 Local Video File / 로컬 비디오 파일", 
                                    variable=self.input_type, value="file", command=self.on_input_type_change)
        file_radio.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        url_radio = ttk.Radiobutton(type_frame, text="🎬 YouTube URL / 유튜브 링크", 
                                   variable=self.input_type, value="url", command=self.on_input_type_change)
        url_radio.grid(row=0, column=1, sticky=tk.W)
        
        # File selection section
        self.file_section = ttk.Frame(input_frame)
        self.file_section.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.file_section.columnconfigure(1, weight=1)
        
        ttk.Label(self.file_section, text="Select Video File / 비디오 파일 선택:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_section, textvariable=self.file_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 5))
        
        self.browse_btn = ttk.Button(self.file_section, text="Browse / 찾기", command=self.browse_file)
        self.browse_btn.grid(row=0, column=2, pady=(0, 5))
        
        # URL input section
        self.url_section = ttk.Frame(input_frame)
        self.url_section.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.url_section.columnconfigure(1, weight=1)
        
        ttk.Label(self.url_section, text="YouTube URL / 유튜브 링크:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.url_section, textvariable=self.url_var, width=50,
                                  font=("Arial", 9))
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 5))
        
        self.validate_btn = ttk.Button(self.url_section, text="Validate / 검증", command=self.validate_url)
        self.validate_btn.grid(row=0, column=2, pady=(0, 5))
        
        # URL placeholder text
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=...")
        self.url_entry.bind("<FocusIn>", self.on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self.on_url_focus_out)
        self.url_entry.config(foreground="gray")
        
        # URL validation result
        self.url_status_var = tk.StringVar(value="")
        self.url_status_label = ttk.Label(self.url_section, textvariable=self.url_status_var, font=("Arial", 8))
        self.url_status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(2, 0))
        
        # Initially show file section
        self.on_input_type_change()
    
    def _create_options_section(self, parent):
        """옵션 섹션 생성"""
        options_frame = ttk.LabelFrame(parent, text="Options / 옵션", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Model size
        ttk.Label(options_frame, text="Model Size:").grid(row=0, column=0, sticky=tk.W)
        self.model_var = tk.StringVar(value="base")
        model_options = [
            "tiny (🚀 매우빠름, ⭐ 기본정확도)",
            "base (🏃 빠름, ⭐⭐ 좋은정확도)", 
            "small (🚶 보통, ⭐⭐⭐ 더좋음)",
            "medium (🐌 느림, ⭐⭐⭐⭐ 높음)",
            "large (🐌🐌 매우느림, ⭐⭐⭐⭐⭐ 최고)"
        ]
        model_combo = ttk.Combobox(options_frame, textvariable=self.model_var, 
                                  values=model_options,
                                  state="readonly", width=35)
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        model_combo.set("base (🏃 빠름, ⭐⭐ 좋은정확도)")
        
        # Language
        ttk.Label(options_frame, text="Language:").grid(row=0, column=2, sticky=tk.W)
        self.language_var = tk.StringVar()
        language_combo = ttk.Combobox(options_frame, textvariable=self.language_var,
                                     values=["auto", "ko", "en", "ja", "zh", "es", "fr", "de"],
                                     state="readonly", width=15)
        language_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        language_combo.set("auto")
        
        # GPU option
        self.use_gpu_var = tk.BooleanVar(value=True)
        gpu_checkbox = ttk.Checkbutton(options_frame, text="Use GPU / GPU 사용", 
                                      variable=self.use_gpu_var)
        gpu_checkbox.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def _create_progress_section(self, parent):
        """진행률 섹션 생성"""
        # Progress bar with percentage
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', maximum=100)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Progress percentage label
        self.progress_var = tk.StringVar(value="0%")
        ttk.Label(progress_frame, textvariable=self.progress_var, width=8).grid(row=0, column=1)
        
        # Progress details text area
        progress_details_frame = ttk.LabelFrame(parent, text="Progress Details / 진행 상황", padding="5")
        progress_details_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_details_frame.columnconfigure(0, weight=1)
        
        # Progress steps display - reduced height for single step
        self.progress_text = tk.Text(progress_details_frame, height=3, wrap=tk.WORD, 
                                   state='disabled', font=("Arial", 10, "bold"))
        self.progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Initialize progress text
        self.update_progress_text("Ready to start processing / 처리 시작 준비됨")
        
        # Status label (simplified)
        self.status_var = tk.StringVar(value="Ready / 준비됨")
        status_label = ttk.Label(parent, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=3)
    
    def _create_results_section(self, parent):
        """결과 섹션 생성"""
        results_frame = ttk.LabelFrame(parent, text="Results / 결과", padding="10")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        parent.rowconfigure(7, weight=1)
        
        # Video info frame
        self._create_video_info_frame(results_frame)
        
        # Text results
        self.result_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=10)
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Save button
        self.save_btn = ttk.Button(results_frame, text="Save Transcript / 텍스트 저장", 
                                  command=self.save_transcript, state="disabled")
        self.save_btn.grid(row=2, column=0, pady=(10, 0))
    
    def _create_video_info_frame(self, parent):
        """비디오 정보 프레임 생성"""
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # Video duration
        ttk.Label(info_frame, text="Duration / 영상길이:").grid(row=0, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar(value="--:--:--")
        ttk.Label(info_frame, textvariable=self.duration_var, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        # Detected language
        ttk.Label(info_frame, text="Language / 감지언어:").grid(row=0, column=2, sticky=tk.W)
        self.language_detected_var = tk.StringVar(value="Unknown")
        ttk.Label(info_frame, textvariable=self.language_detected_var, font=("Arial", 9, "bold")).grid(row=0, column=3, sticky=tk.W, padx=(10, 20))
        
        # Word count
        ttk.Label(info_frame, text="Words / 단어수:").grid(row=0, column=4, sticky=tk.W)
        self.word_count_var = tk.StringVar(value="0")
        ttk.Label(info_frame, textvariable=self.word_count_var, font=("Arial", 9, "bold")).grid(row=0, column=5, sticky=tk.W, padx=(10, 0))
    
    def on_input_type_change(self):
        """입력 타입 변경 시 호출"""
        if self.input_type.get() == "file":
            # 파일 섹션 표시, URL 섹션 숨김
            for widget in self.file_section.winfo_children():
                widget.grid()
            for widget in self.url_section.winfo_children():
                widget.grid_remove()
        else:
            # URL 섹션 표시, 파일 섹션 숨김
            for widget in self.file_section.winfo_children():
                widget.grid_remove()
            for widget in self.url_section.winfo_children():
                widget.grid()
    
    def on_url_focus_in(self, event):
        """URL 입력 필드 포커스 시"""
        if self.url_var.get() == "https://www.youtube.com/watch?v=...":
            self.url_var.set("")
            self.url_entry.config(foreground="black")
    
    def on_url_focus_out(self, event):
        """URL 입력 필드 포커스 해제 시"""
        if not self.url_var.get().strip():
            self.url_var.set("https://www.youtube.com/watch?v=...")
            self.url_entry.config(foreground="gray")
    
    def validate_url(self):
        """YouTube URL 검증"""
        url = self.url_var.get().strip()
        if not url or url == "https://www.youtube.com/watch?v=...":
            self.url_status_var.set("❌ Please enter a YouTube URL / YouTube URL을 입력하세요")
            return False
        
        # Initialize converter if needed
        if not self.converter:
            self.converter = VideoToTextConverter()
        
        if self.converter.is_youtube_url(url):
            try:
                # Try to get video info
                info = self.converter.get_youtube_info(url)
                if info:
                    duration_str = f"{int(info['duration']//60)}:{int(info['duration']%60):02d}" if info['duration'] else "Unknown"
                    self.url_status_var.set(f"✅ Valid: {info['title'][:40]}... ({duration_str})")
                    return True
                else:
                    self.url_status_var.set("❌ Failed to get video info / 영상 정보를 가져올 수 없습니다")
                    return False
            except Exception as e:
                self.url_status_var.set(f"❌ Error: {str(e)[:50]}...")
                return False
        else:
            self.url_status_var.set("❌ Invalid YouTube URL format / 유효하지 않은 YouTube URL 형식")
            return False
    
    def browse_file(self):
        """파일 선택 대화상자"""
        filename = filedialog.askopenfilename(
            title="Select Video File / 비디오 파일 선택",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_var.set(filename)
    
    def start_processing(self):
        """비디오 처리 시작"""
        # Check input type and validate
        if self.input_type.get() == "file":
            file_path = self.file_var.get().strip()
            if not file_path:
                messagebox.showerror("Error", "Please select a video file first.\n먼저 비디오 파일을 선택해주세요.")
                return
            
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "Selected file does not exist.\n선택한 파일이 존재하지 않습니다.")
                return
        else:
            url = self.url_var.get().strip()
            if not url or url == "https://www.youtube.com/watch?v=...":
                messagebox.showerror("Error", "Please enter a YouTube URL first.\n먼저 YouTube URL을 입력해주세요.")
                return
            
            # Validate URL before processing
            if not self.validate_url():
                messagebox.showerror("Error", "Invalid YouTube URL. Please check the URL.\n유효하지 않은 YouTube URL입니다. URL을 확인해주세요.")
                return
        
        # Reset info display
        self.duration_var.set("--:--:--")
        self.language_detected_var.set("Processing...")
        self.word_count_var.set("0")
        
        # Reset and start progress
        self.progress['value'] = 0
        self.progress_var.set("0%")
        self.clear_progress_text()
        self.update_progress_text("🚀 Starting video processing / 영상 처리 시작")
        
        # Disable process button and start progress
        self.process_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.result_text.delete(1.0, tk.END)
        
        # Start processing in a separate thread
        if self.input_type.get() == "file":
            file_path = self.file_var.get().strip()
            thread = threading.Thread(target=self.process_video, args=(file_path, "file"))
        else:
            url = self.url_var.get().strip()
            thread = threading.Thread(target=self.process_video, args=(url, "url"))
        
        thread.daemon = True
        thread.start()
    
    def update_progress_text(self, message):
        """진행률 텍스트 업데이트 - 현재 단계만 표시"""
        self.progress_text.config(state='normal')
        self.progress_text.delete(1.0, tk.END)  # Clear previous content
        self.progress_text.insert(1.0, f"• {message}")
        self.progress_text.config(state='disabled')
    
    def clear_progress_text(self):
        """진행률 텍스트 지우기"""
        self.progress_text.config(state='normal')
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.config(state='disabled')
    
    def update_progress(self, value, status):
        """진행률 바 및 상태 업데이트"""
        self.progress['value'] = value
        self.progress_var.set(f"{value}%")
        self.status_var.set(status)
        
        # Add detailed progress steps - show current step only
        progress_steps = {
            5: "📹 Step 1/6: Reading video information / 영상 정보 읽는중...",
            10: "✅ Step 1/6: Video info loaded / 영상 정보 로딩 완료",
            15: "🤖 Step 2/6: Loading AI model / AI 모델 로딩중...",
            25: "✅ Step 2/6: AI model loaded / AI 모델 로딩 완료", 
            30: "⚙️ Step 3/6: Preparing audio extraction / 오디오 추출 준비중...",
            40: "🎵 Step 4/6: Extracting audio from video / 비디오에서 오디오 추출중...",
            60: "✅ Step 4/6: Audio extraction completed / 오디오 추출 완료",
            65: "🔄 Step 5/6: Starting AI transcription / AI 텍스트 변환 시작...",
            85: "✅ Step 5/6: Transcription completed / 텍스트 변환 완료",
            90: "📝 Step 6/6: Finalizing results / 결과 정리중...",
            100: "🎉 Step 6/6: All completed! / 모든 단계 완료!"
        }
        
        if value in progress_steps:
            self.update_progress_text(progress_steps[value])
    
    def process_video(self, input_path, input_type):
        """비디오 파일/URL 처리 (백그라운드 스레드)"""
        try:
            # Step 1: Initialize (0-10%)
            if input_type == "file":
                self.root.after(0, lambda: self.update_progress(5, "Reading video info... 영상 정보 읽는중..."))
                video_info = self.converter.get_video_info(input_path) if self.converter else None
                
                if video_info and video_info.get('duration'):
                    duration = int(video_info['duration'])
                    hours = duration // 3600
                    minutes = (duration % 3600) // 60
                    seconds = duration % 60
                    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    self.root.after(0, lambda: self.duration_var.set(duration_str))
            else:
                self.root.after(0, lambda: self.update_progress(5, "Validating YouTube URL... YouTube URL 검증 중..."))
            
            self.root.after(0, lambda: self.update_progress(10, "Initialization completed... 초기화 완료"))
            
            # Step 2: Initialize converter if not already done (10-25%)
            if self.converter is None:
                self.root.after(0, lambda: self.update_progress(15, "Loading AI model... AI 모델 로딩중..."))
                # Extract model name from the display text
                model_display = self.model_var.get()
                model_name = model_display.split(" (")[0] if " (" in model_display else model_display
                use_gpu = self.use_gpu_var.get()
                
                # Safe model loading for PyInstaller builds
                try:
                    self.converter = VideoToTextConverter(model_size=model_name, use_gpu=use_gpu)
                    self.root.after(0, lambda: self.update_progress(25, "AI model loaded AI 모델 로딩 완료"))
                except Exception as e:
                    error_msg = f"Failed to load AI model: {str(e)}\nAI 모델 로딩 실패: {str(e)}"
                    self.root.after(0, lambda: self.show_error(error_msg))
                    return
            
            # Get language setting
            language = self.language_var.get() if self.language_var.get() != "auto" else None
            
            # Create progress callback function
            def progress_callback(value, message):
                self.root.after(0, lambda: self.update_progress(value, message))
            
            # Process based on input type
            if input_type == "file":
                result = self.converter.process_local_video_with_info(
                    input_path, 
                    language=language, 
                    save_transcript=False, 
                    progress_callback=progress_callback
                )
            else:
                result = self.converter.process_youtube_video(
                    input_path,
                    language=language,
                    save_transcript=False,
                    progress_callback=progress_callback
                )
                
                # Display YouTube video information
                if result and 'youtube_info' in result:
                    yt_info = result['youtube_info']
                    if yt_info['duration']:
                        duration_seconds = yt_info['duration']
                        hours = int(duration_seconds // 3600)
                        minutes = int((duration_seconds % 3600) // 60)
                        seconds = int(duration_seconds % 60)
                        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        self.root.after(0, lambda: self.duration_var.set(duration_str))
            
            # Step 5: Finalizing (90-100%)
            self.root.after(0, lambda: self.update_progress(90, "Finalizing results... 결과 정리중..."))
            
            # Update UI with results
            if result and result.get('transcript'):
                transcript = result['transcript']
                detected_language = result.get('detected_language', 'Unknown')
                word_count = len(transcript.split()) if transcript else 0
                
                # Update info display
                self.root.after(0, lambda: self.language_detected_var.set(detected_language.upper()))
                self.root.after(0, lambda: self.word_count_var.set(f"{word_count:,}"))
                
                # Complete progress
                self.root.after(0, lambda: self.update_progress(100, "Completed! 완료!"))
                self.root.after(0, lambda: self.show_results(transcript))
            else:
                self.root.after(0, lambda: self.show_error("Failed to extract text from video.\n영상에서 텍스트 추출에 실패했습니다."))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}\n오류: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def show_results(self, transcript):
        """결과 표시"""
        self.progress['value'] = 100
        self.progress_var.set("100%")
        self.process_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.status_var.set("Completed! / 완료!")
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, transcript)
        
        messagebox.showinfo("Success / 성공", "Text extraction completed!\n텍스트 추출이 완료되었습니다!")
    
    def show_error(self, error_msg):
        """오류 표시"""
        self.progress['value'] = 0
        self.progress_var.set("0%")
        self.process_btn.config(state="normal")
        self.status_var.set("Error / 오류")
        self.update_progress_text("❌ Error occurred / 오류 발생")
        
        messagebox.showerror("Error / 오류", error_msg)
    
    def save_transcript(self):
        """텍스트 저장"""
        transcript = self.result_text.get(1.0, tk.END).strip()
        if not transcript:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Transcript / 텍스트 저장",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                messagebox.showinfo("Success / 성공", f"Transcript saved to: {filename}\n텍스트가 저장되었습니다: {filename}")
            except Exception as e:
                messagebox.showerror("Error / 오류", f"Failed to save file: {e}\n파일 저장 실패: {e}") 