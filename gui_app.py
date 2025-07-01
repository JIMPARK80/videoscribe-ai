import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from video_to_text import VideoToTextConverter

class VideoToTextGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video File to Text Extractor / 비디오 파일 텍스트 추출기")
        self.root.geometry("800x600")
        
        # Initialize converter (will be loaded when needed)
        self.converter = None
        
        self.create_widgets()
    
    def create_widgets(self):
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
        input_frame = ttk.LabelFrame(main_frame, text="Video File Selection / 비디오 파일 선택", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Label(input_frame, text="Select Video File / 비디오 파일 선택:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(input_frame, textvariable=self.file_var, width=50)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 5))
        
        browse_btn = ttk.Button(input_frame, text="Browse / 찾기", command=self.browse_file)
        browse_btn.grid(row=0, column=2, pady=(0, 5))
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Options / 옵션", padding="10")
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
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Extract Text / 텍스트 추출", 
                                     command=self.start_processing, style="Accent.TButton")
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready / 준비됨")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=3)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results / 결과", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Video info frame
        info_frame = ttk.Frame(results_frame)
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
        
        # Text area with scrollbar
        self.result_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Save button
        self.save_btn = ttk.Button(results_frame, text="Save Transcript / 텍스트 저장", 
                                  command=self.save_transcript, state="disabled")
        self.save_btn.grid(row=2, column=0, pady=(10, 0))
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Video File / 영상 파일 선택",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_var.set(filename)
    
    def start_processing(self):
        # Get input
        file_path = self.file_var.get().strip()
        
        if not file_path:
            messagebox.showerror("Error / 오류", "Please select a video file.\n비디오 파일을 선택해주세요.")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error / 오류", f"File not found: {file_path}\n파일을 찾을 수 없습니다: {file_path}")
            return
        
        # Reset info display
        self.duration_var.set("--:--:--")
        self.language_detected_var.set("Processing...")
        self.word_count_var.set("0")
        
        # Disable process button and start progress
        self.process_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.progress.start()
        self.result_text.delete(1.0, tk.END)
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_video, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def process_video(self, file_path):
        try:
            # Initialize converter if not already done
            if self.converter is None:
                self.root.after(0, lambda: self.status_var.set("Loading AI model... AI 모델 로딩중..."))
                # Extract model name from the display text (e.g., "base (🏃 빠름, ⭐⭐ 좋은정확도)" -> "base")
                model_display = self.model_var.get()
                model_name = model_display.split(" (")[0] if " (" in model_display else model_display
                use_gpu = self.use_gpu_var.get()
                self.converter = VideoToTextConverter(model_size=model_name, use_gpu=use_gpu)
            
            # Get video duration first
            self.root.after(0, lambda: self.status_var.set("Reading video info... 영상 정보 읽는중..."))
            video_info = self.converter.get_video_info(file_path)
            
            if video_info and video_info.get('duration'):
                duration = int(video_info['duration'])
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.root.after(0, lambda: self.duration_var.set(duration_str))
            
            # Get language setting
            language = self.language_var.get() if self.language_var.get() != "auto" else None
            
            # Process local video file
            self.root.after(0, lambda: self.status_var.set("Processing video file... 영상 파일 처리중..."))
            result = self.converter.process_local_video_with_info(file_path, language=language, save_transcript=False)
            
            # Update UI with results
            if result and result.get('transcript'):
                transcript = result['transcript']
                detected_language = result.get('detected_language', 'Unknown')
                word_count = len(transcript.split()) if transcript else 0
                
                # Update info display
                self.root.after(0, lambda: self.language_detected_var.set(detected_language.upper()))
                self.root.after(0, lambda: self.word_count_var.set(f"{word_count:,}"))
                
                self.root.after(0, lambda: self.show_results(transcript))
            else:
                self.root.after(0, lambda: self.show_error("Failed to extract text from video.\n영상에서 텍스트 추출에 실패했습니다."))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}\n오류: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def show_results(self, transcript):
        self.progress.stop()
        self.process_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.status_var.set("Completed! / 완료!")
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, transcript)
        
        messagebox.showinfo("Success / 성공", "Text extraction completed!\n텍스트 추출이 완료되었습니다!")
    
    def show_error(self, error_msg):
        self.progress.stop()
        self.process_btn.config(state="normal")
        self.status_var.set("Error / 오류")
        
        messagebox.showerror("Error / 오류", error_msg)
    
    def save_transcript(self):
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

def main():
    root = tk.Tk()
    app = VideoToTextGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 