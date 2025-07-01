import os
import sys
import subprocess
import tempfile
import whisper
import yt_dlp
from moviepy.editor import VideoFileClip
from pathlib import Path
import argparse
import shutil
import logging
import warnings

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Whisper FP16 경고 숨기기
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class VideoToTextConverter:
    def __init__(self, model_size="base", use_gpu=True):
        """
        Initialize the converter with Whisper model
        
        Args:
            model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            use_gpu (bool): Whether to use GPU if available
        """
        import torch
        
        # Check GPU availability
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        
        if self.device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"🚀 Using GPU: {gpu_name} ({gpu_memory:.1f}GB)")
            print(f"🚀 GPU 사용: {gpu_name} ({gpu_memory:.1f}GB)")
        else:
            print("💻 Using CPU (no GPU available or disabled)")
            print("💻 CPU 사용 (GPU 없음 또는 비활성화)")
        
        print("Loading Whisper model... 로딩중...")
        try:
            self.model = whisper.load_model(model_size, device=self.device)
            print(f"Whisper {model_size} model loaded successfully on {self.device.upper()}!")
            print(f"Whisper {model_size} 모델이 {self.device.upper()}에서 로딩 완료!")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            print(f"Whisper 모델 로딩 오류: {e}")
            raise
    
    def get_video_info(self, video_path):
        """
        Get video information without processing
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            dict: Video information (duration, etc.)
        """
        try:
            from moviepy.editor import VideoFileClip
            
            if not os.path.exists(video_path):
                return None
            
            video = VideoFileClip(video_path)
            info = {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size
            }
            video.close()
            return info
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def download_youtube_audio(self, url, output_path=None):
        """
        Download audio from YouTube video
        
        Args:
            url (str): YouTube video URL
            output_path (str): Path to save the audio file
            
        Returns:
            tuple: (audio_file_path, title) or (None, None) if failed
        """
        if output_path is None:
            output_path = tempfile.mkdtemp()
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,  # 불필요한 출력 줄이기
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading audio from: {url}")
                print(f"오디오 다운로드 중: {url}")
                
                # Get video info
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                print(f"Video title: {title}")
                print(f"영상 제목: {title}")
                # Format duration as HH:MM:SS
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                print(f"Duration: {duration_str}")
                print(f"재생시간: {duration_str}")
                
                # Check if video is too long (optional warning)
                if duration > 3600:  # 1 hour
                    print("Warning: Video is longer than 1 hour. Transcription may take a while.")
                    print("경고: 1시간 이상의 영상입니다. 변환에 시간이 오래 걸릴 수 있습니다.")
                
                # Download
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(output_path):
                    if file.endswith('.wav'):
                        return os.path.join(output_path, file), title
                
                # If no .wav file found, look for other audio formats
                for file in os.listdir(output_path):
                    if any(file.endswith(ext) for ext in ['.mp3', '.m4a', '.webm']):
                        return os.path.join(output_path, file), title
                
                # If no audio file found at all
                print("No audio file was downloaded. This may be due to YouTube restrictions.")
                print("오디오 파일이 다운로드되지 않았습니다. YouTube 제한 때문일 수 있습니다.")
                return None, title
                        
        except Exception as e:
            print(f"Error downloading YouTube video: {e}")
            print(f"YouTube 영상 다운로드 오류: {e}")
            return None, None
    
    def extract_audio_from_video(self, video_path, output_path=None):
        """
        Extract audio from local video file
        
        Args:
            video_path (str): Path to the video file
            output_path (str): Path to save the extracted audio
            
        Returns:
            str: Path to the extracted audio file or None if failed
        """
        if output_path is None:
            output_path = tempfile.mkdtemp()
        
        try:
            print(f"Extracting audio from: {video_path}")
            print(f"오디오 추출 중: {video_path}")
            
            # Check if video file exists and is readable
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            video = VideoFileClip(video_path)
            
            # Check if video has audio
            if video.audio is None:
                print("Warning: No audio track found in video")
                print("경고: 영상에 오디오 트랙이 없습니다")
                video.close()
                return None
            
            # Format duration as HH:MM:SS
            duration = int(video.duration)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"Video duration: {duration_str}")
            print(f"영상 길이: {duration_str}")
            
            audio_filename = os.path.join(output_path, "extracted_audio.wav")
            video.audio.write_audiofile(audio_filename, verbose=False, logger=None)
            video.close()
            
            return audio_filename
            
        except Exception as e:
            print(f"Error extracting audio: {e}")
            print(f"오디오 추출 오류: {e}")
            return None
    
    def transcribe_audio(self, audio_path, language=None):
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_path (str): Path to the audio file
            language (str): Language code (e.g., 'ko', 'en', 'ja')
            
        Returns:
            dict: Transcription result with text and segments or None if failed
        """
        try:
            print("Transcribing audio... 음성을 텍스트로 변환중...")
            
            # Check if audio file exists
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Get file size for progress indication
            file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
            print(f"Audio file size: {file_size:.2f} MB")
            print(f"오디오 파일 크기: {file_size:.2f} MB")
            
            # Transcribe with Whisper
            if language:
                result = self.model.transcribe(audio_path, language=language)
            else:
                result = self.model.transcribe(audio_path)
            
            # Detected language info
            detected_language = result.get('language', 'unknown')
            print(f"Detected language: {detected_language}")
            print(f"감지된 언어: {detected_language}")
            print("Transcription completed! 변환 완료!")
            
            return result
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            print(f"텍스트 변환 오류: {e}")
            return None
    
    def save_transcript_with_timestamps(self, result, output_file, video_info=None):
        """
        Save transcript with timestamps to file
        
        Args:
            result (dict): Whisper transcription result
            output_file (str): Output file path
            video_info (dict): Optional video information
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if video_info:
                    f.write(f"Video: {video_info.get('title', 'Unknown')}\n")
                    if 'url' in video_info:
                        f.write(f"URL: {video_info['url']}\n")
                    if 'file_path' in video_info:
                        f.write(f"File: {video_info['file_path']}\n")
                
                f.write(f"Language: {result.get('language', 'unknown')}\n")
                f.write("="*70 + "\n\n")
                
                # Full transcript
                f.write("FULL TRANSCRIPT:\n")
                f.write("-"*50 + "\n")
                f.write(result['text'] + "\n\n")
                
                # Timestamped segments
                f.write("TIMESTAMPED TRANSCRIPT:\n")
                f.write("-"*50 + "\n")
                
                for segment in result.get('segments', []):
                    start_time = segment['start']
                    end_time = segment['end']
                    text = segment['text'].strip()
                    
                    # Format timestamps
                    start_min, start_sec = divmod(int(start_time), 60)
                    end_min, end_sec = divmod(int(end_time), 60)
                    
                    f.write(f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}] {text}\n")
            
            print(f"Detailed transcript saved to: {output_file}")
            print(f"상세 텍스트 파일 저장됨: {output_file}")
            
        except Exception as e:
            print(f"Error saving transcript: {e}")
            print(f"텍스트 파일 저장 오류: {e}")
    
    def process_youtube_video(self, url, language=None, save_transcript=True, include_timestamps=False):
        """
        Process YouTube video: download and transcribe
        
        Args:
            url (str): YouTube video URL
            language (str): Language code for transcription
            save_transcript (bool): Whether to save transcript to file
            include_timestamps (bool): Whether to include timestamps in transcript
            
        Returns:
            str: Transcribed text or None if failed
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Download audio
            audio_path, title = self.download_youtube_audio(url, temp_dir)
            if not audio_path:
                return None
            
            # Transcribe
            result = self.transcribe_audio(audio_path, language)
            if not result:
                return None
            
            transcript = result['text']
            
            # Save transcript if requested
            if save_transcript and title:
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:100]  # Limit filename length
                
                if include_timestamps:
                    transcript_file = f"{safe_title}_transcript_detailed.txt"
                    video_info = {'title': title, 'url': url}
                    self.save_transcript_with_timestamps(result, transcript_file, video_info)
                else:
                    transcript_file = f"{safe_title}_transcript.txt"
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(f"Video: {title}\n")
                        f.write(f"URL: {url}\n")
                        f.write(f"Language: {result.get('language', 'unknown')}\n")
                        f.write("="*70 + "\n\n")
                        f.write(transcript)
                    
                    print(f"Transcript saved to: {transcript_file}")
                    print(f"텍스트 파일 저장됨: {transcript_file}")
            
            return transcript
            
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")
    
    def process_local_video(self, video_path, language=None, save_transcript=True, include_timestamps=False):
        """
        Process local video file: extract audio and transcribe
        
        Args:
            video_path (str): Path to local video file
            language (str): Language code for transcription
            save_transcript (bool): Whether to save transcript to file
            include_timestamps (bool): Whether to include timestamps in transcript
            
        Returns:
            str: Transcribed text or None if failed
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extract audio
            audio_path = self.extract_audio_from_video(video_path, temp_dir)
            if not audio_path:
                return None
            
            # Transcribe
            result = self.transcribe_audio(audio_path, language)
            if not result:
                return None
            
            transcript = result['text']
            
            # Save transcript if requested
            if save_transcript:
                video_name = Path(video_path).stem
                
                if include_timestamps:
                    transcript_file = f"{video_name}_transcript_detailed.txt"
                    video_info = {'file_path': video_path}
                    self.save_transcript_with_timestamps(result, transcript_file, video_info)
                else:
                    transcript_file = f"{video_name}_transcript.txt"
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(f"Video File: {video_path}\n")
                        f.write(f"Language: {result.get('language', 'unknown')}\n")
                        f.write("="*70 + "\n\n")
                        f.write(transcript)
                    
                    print(f"Transcript saved to: {transcript_file}")
                    print(f"텍스트 파일 저장됨: {transcript_file}")
            
            return transcript
            
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")
    
    def process_local_video_with_info(self, video_path, language=None, save_transcript=True, include_timestamps=False, progress_callback=None):
        """
        Process local video file and return detailed information
        
        Args:
            video_path (str): Path to local video file
            language (str): Language code for transcription
            save_transcript (bool): Whether to save transcript to file
            include_timestamps (bool): Whether to include timestamps in transcript
            progress_callback (callable): Function to call with progress updates (value, message)
            
        Returns:
            dict: Detailed result with transcript, detected language, etc.
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Extract audio (progress: 40-60%)
            if progress_callback:
                progress_callback(40, "Extracting audio from video... 비디오에서 오디오 추출중...")
            
            audio_path = self.extract_audio_from_video(video_path, temp_dir)
            if not audio_path:
                return None
            
            if progress_callback:
                progress_callback(60, "Audio extracted successfully 오디오 추출 완료")
            
            # Transcribe (progress: 60-85%)
            if progress_callback:
                progress_callback(65, "Starting AI transcription... AI 텍스트 변환 시작...")
            
            result = self.transcribe_audio(audio_path, language)
            if not result:
                return None
            
            if progress_callback:
                progress_callback(85, "Transcription completed 텍스트 변환 완료")
            
            transcript = result['text']
            detected_language = result.get('language', 'unknown')
            
            # Calculate statistics
            word_count = len(transcript.split()) if transcript else 0
            char_count = len(transcript) if transcript else 0
            
            # Save transcript if requested
            if save_transcript:
                video_name = Path(video_path).stem
                
                if include_timestamps:
                    transcript_file = f"{video_name}_transcript_detailed.txt"
                    video_info = {'file_path': video_path}
                    self.save_transcript_with_timestamps(result, transcript_file, video_info)
                else:
                    transcript_file = f"{video_name}_transcript.txt"
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(f"Video File: {video_path}\n")
                        f.write(f"Language: {detected_language}\n")
                        f.write(f"Words: {word_count:,}\n")
                        f.write(f"Characters: {char_count:,}\n")
                        f.write("="*70 + "\n\n")
                        f.write(transcript)
                    
                    print(f"Transcript saved to: {transcript_file}")
                    print(f"텍스트 파일 저장됨: {transcript_file}")
            
            return {
                'transcript': transcript,
                'detected_language': detected_language,
                'word_count': word_count,
                'char_count': char_count,
                'segments': result.get('segments', [])
            }
            
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract text from YouTube videos or local video files")
    parser.add_argument("input", help="YouTube URL or path to local video file")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--language", help="Language code (e.g., ko, en, ja)")
    parser.add_argument("--no-save", action="store_true", help="Don't save transcript to file")
    parser.add_argument("--timestamps", action="store_true", help="Include timestamps in transcript")
    parser.add_argument("--cpu", action="store_true", help="Force CPU usage (disable GPU)")
    
    args = parser.parse_args()
    
    try:
        # Initialize converter
        converter = VideoToTextConverter(model_size=args.model, use_gpu=not args.cpu)
        
        # Process input
        if args.input.startswith(('http://', 'https://', 'www.')):
            print("Processing YouTube video... YouTube 영상 처리중...")
            transcript = converter.process_youtube_video(
                args.input, 
                language=args.language, 
                save_transcript=not args.no_save,
                include_timestamps=args.timestamps
            )
        else:
            if not os.path.exists(args.input):
                print(f"Error: File not found: {args.input}")
                print(f"오류: 파일을 찾을 수 없습니다: {args.input}")
                return 1
            
            print("Processing local video file... 로컬 영상 파일 처리중...")
            transcript = converter.process_local_video(
                args.input, 
                language=args.language, 
                save_transcript=not args.no_save,
                include_timestamps=args.timestamps
            )
        
        if transcript:
            print("\n" + "="*70)
            print("TRANSCRIPT / 변환된 텍스트:")
            print("="*70)
            print(transcript)
            return 0
        else:
            print("Failed to extract text from video.")
            print("영상에서 텍스트 추출에 실패했습니다.")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        print("\n사용자에 의해 작업이 취소되었습니다.")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"예상치 못한 오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())