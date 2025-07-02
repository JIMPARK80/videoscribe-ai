"""
비디오 텍스트 변환기 모듈
Video to Text Converter Module
"""

import os
import tempfile
import re


class VideoToTextConverter:
    """비디오 파일에서 텍스트를 추출하는 클래스"""
    
    def __init__(self, model_size="base", use_gpu=True):
        """
        초기화
        
        Args:
            model_size (str): Whisper 모델 크기 (tiny, base, small, medium, large)
            use_gpu (bool): GPU 사용 여부
        """
        self.model_size = model_size
        self.use_gpu = use_gpu
        self.model = None
    
    def _load_model(self):
        """Whisper 모델을 로드합니다"""
        if self.model is None:
            import whisper
            import torch
            
            # GPU 설정
            if self.use_gpu and torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
            
            self.model = whisper.load_model(self.model_size, device=device)
        return self.model
    
    def is_youtube_url(self, url):
        """
        YouTube URL인지 확인합니다
        
        Args:
            url (str): 확인할 URL
            
        Returns:
            bool: YouTube URL 여부
        """
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
            r'(?:https?://)?(?:www\.)?m\.youtube\.com/watch\?v=[\w-]+'
        ]
        return any(re.match(pattern, url.strip()) for pattern in youtube_patterns)
    
    def get_youtube_info(self, url):
        """
        YouTube 영상 정보를 가져옵니다
        
        Args:
            url (str): YouTube URL
            
        Returns:
            dict: 영상 정보 (title, duration, uploader)
        """
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown')
                }
        except Exception as e:
            print(f"Error getting YouTube info: {e}")
            return None
    
    def download_youtube_video(self, url, progress_callback=None):
        """
        YouTube 영상을 다운로드합니다
        
        Args:
            url (str): YouTube URL
            progress_callback (function): 진행률 콜백 함수
            
        Returns:
            str: 다운로드된 파일 경로
        """
        try:
            import yt_dlp
            import random
            
            # 임시 디렉토리 생성
            temp_dir = tempfile.mkdtemp()
            
            # 다양한 User-Agent 목록 (봇 차단 우회)
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
            ]
            
            # yt-dlp 설정 개선 (고급 봇 차단 우회)
            ydl_opts = {
                # 포맷 선택 - 더 관대한 설정
                'format': 'best[height<=480]/best[ext=mp4]/best[height<=720]/worst[ext=mp4]/worst',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                
                # 고급 우회 설정
                'http_headers': {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'DNT': '1',
                    'Connection': 'close',
                    'Upgrade-Insecure-Requests': '1',
                },
                
                # 요청 설정
                'socket_timeout': 30,
                'retries': 5,
                'fragment_retries': 5,
                'skip_unavailable_fragments': True,
                'keep_fragments': False,
                'buffersize': 1024,
                
                # YouTube 특화 설정
                'youtube_include_dash_manifest': False,
                'youtube_skip_dash_manifest': True,
                
                # 기타 우회 설정
                'no_check_certificate': True,
                'prefer_insecure': False,
                'ignoreerrors': False,
                'geo_bypass': True,
                'age_limit': 99,
            }
            
            if progress_callback:
                progress_callback(10, "Starting download... / 다운로드 시작...")
                
                def progress_hook(d):
                    try:
                        if d['status'] == 'downloading':
                            if 'total_bytes' in d and d['total_bytes']:
                                percent = (d['downloaded_bytes'] / d['total_bytes']) * 40
                                progress_callback(10 + percent, f"Downloading: {percent:.1f}% / 다운로드 중: {percent:.1f}%")
                            elif '_percent_str' in d:
                                percent_str = d['_percent_str'].strip('%')
                                try:
                                    percent = float(percent_str) * 0.4
                                    progress_callback(10 + percent, f"Downloading: {percent_str}% / 다운로드 중: {percent_str}%")
                                except:
                                    progress_callback(25, "Downloading... / 다운로드 중...")
                        elif d['status'] == 'finished':
                            progress_callback(50, "Download completed! / 다운로드 완료!")
                    except Exception as e:
                        print(f"Progress callback error: {e}")
                
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # 다중 시도 전략
            download_strategies = [
                # 전략 1: 최신 설정
                ydl_opts.copy(),
                
                # 전략 2: 더 낮은 품질 우선
                {**ydl_opts, 'format': 'worst[ext=mp4]/worst'},
                
                # 전략 3: 모든 포맷 허용
                {**ydl_opts, 'format': 'best/worst'},
                
                # 전략 4: 기본 설정
                {
                    'format': 'mp4/best',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
            ]
            
            last_error = None
            
            for strategy_num, strategy_opts in enumerate(download_strategies, 1):
                try:
                    if progress_callback:
                        progress_callback(5 + strategy_num * 2, f"Trying strategy {strategy_num}/4... / 전략 {strategy_num}/4 시도 중...")
                    
                    with yt_dlp.YoutubeDL(strategy_opts) as ydl:
                        # 영상 정보 먼저 추출
                        info = ydl.extract_info(url, download=False)
                        title = info.get('title', 'video')
                        
                        # 사용 가능한 포맷 확인
                        formats = info.get('formats', [])
                        if not formats:
                            continue
                        
                        # 비디오 포맷 필터링 (storyboard 제외)
                        video_formats = [
                            f for f in formats 
                            if f.get('vcodec') != 'none' 
                            and f.get('ext') not in ['mhtml', 'html'] 
                            and 'storyboard' not in f.get('format_note', '').lower()
                            and f.get('protocol') != 'mhtml'
                        ]
                        
                        if not video_formats:
                            print(f"Strategy {strategy_num}: No valid video formats found")
                            continue
                        
                        print(f"Strategy {strategy_num}: Found {len(video_formats)} valid formats")
                        
                        # 파일명 정리
                        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:50]
                        safe_title = re.sub(r'[^\w\s-]', '', safe_title).strip()
                        
                        # 다운로드 경로 설정
                        strategy_opts['outtmpl'] = os.path.join(temp_dir, f'{safe_title}.%(ext)s')
                        
                        # 다운로드 실행
                        with yt_dlp.YoutubeDL(strategy_opts) as ydl_download:
                            ydl_download.download([url])
                        
                        # 다운로드된 파일 검증
                        downloaded_files = []
                        for filename in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, filename)
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path)
                                if file_size > 1024:  # 1KB 이상
                                    _, ext = os.path.splitext(filename.lower())
                                    if ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv']:
                                        downloaded_files.append((file_path, file_size))
                        
                        if downloaded_files:
                            # 가장 큰 파일 선택
                            downloaded_files.sort(key=lambda x: x[1], reverse=True)
                            selected_file = downloaded_files[0][0]
                            
                            # 파일이 실제 비디오인지 검증
                            try:
                                from moviepy.editor import VideoFileClip
                                with VideoFileClip(selected_file) as test_clip:
                                    if test_clip.duration and test_clip.duration > 0:
                                        print(f"Success with strategy {strategy_num}!")
                                        return selected_file
                            except Exception as e:
                                print(f"Strategy {strategy_num}: Video validation failed: {e}")
                                continue
                        
                        print(f"Strategy {strategy_num}: No valid files downloaded")
                        
                except Exception as e:
                    last_error = e
                    print(f"Strategy {strategy_num} failed: {e}")
                    continue
            
            # 모든 전략 실패
            raise Exception(f"All download strategies failed. Last error: {last_error}")
                
        except Exception as e:
            error_msg = str(e)
            if "HTTP Error 403" in error_msg:
                raise Exception("YouTube access forbidden. This video might be region-blocked or have anti-bot protection. Try a different video. / YouTube 접근이 금지되었습니다. 이 영상은 지역 차단되었거나 봇 차단이 적용되었을 수 있습니다. 다른 영상을 시도해보세요.")
            elif "Video unavailable" in error_msg:
                raise Exception("Video is unavailable or private. / 비디오를 사용할 수 없거나 비공개입니다.")
            elif "Sign in to confirm your age" in error_msg:
                raise Exception("Age-restricted video. Cannot download without login. / 연령 제한 비디오입니다. 로그인 없이 다운로드할 수 없습니다.")
            elif "No valid video formats" in error_msg:
                raise Exception("This video cannot be downloaded due to YouTube restrictions. Try a different, less popular video. / YouTube 제한으로 인해 이 영상을 다운로드할 수 없습니다. 덜 인기 있는 다른 영상을 시도해보세요.")
            else:
                print(f"Error downloading YouTube video: {e}")
                raise Exception(f"Download failed: {error_msg} / 다운로드 실패: {error_msg}")
    
    def process_youtube_video(self, url, language=None, save_transcript=False, progress_callback=None):
        """
        YouTube 영상을 다운로드하고 텍스트를 추출합니다
        
        Args:
            url (str): YouTube URL
            language (str): 언어 코드 (예: 'ko', 'en'), None이면 자동 감지
            save_transcript (bool): 텍스트 파일로 저장 여부
            progress_callback (function): 진행률 콜백 함수
            
        Returns:
            dict: 추출 결과 (transcript, detected_language, segments, youtube_info)
        """
        downloaded_file = None
        try:
            # YouTube URL 검증
            if not self.is_youtube_url(url):
                raise ValueError("Invalid YouTube URL / 유효하지 않은 YouTube URL입니다")
            
            if progress_callback:
                progress_callback(5, "Validating URL... / URL 검증 중...")
            
            # YouTube 정보 가져오기
            youtube_info = self.get_youtube_info(url)
            if not youtube_info:
                raise Exception("Failed to get YouTube video info / YouTube 영상 정보를 가져올 수 없습니다")
            
            # 영상 다운로드
            downloaded_file = self.download_youtube_video(url, progress_callback)
            
            if progress_callback:
                progress_callback(55, "Processing downloaded video... / 다운로드된 영상 처리 중...")
            
            # 다운로드된 파일을 로컬 비디오 처리 메서드로 처리
            result = self.process_local_video_with_info(downloaded_file, language, save_transcript, progress_callback)
            
            # YouTube 정보 추가
            result['youtube_info'] = youtube_info
            
            return result
            
        except Exception as e:
            print(f"Error processing YouTube video: {e}")
            raise e
        finally:
            # 임시 파일 정리
            if downloaded_file and os.path.exists(downloaded_file):
                try:
                    # 파일이 있는 디렉토리 전체 삭제
                    import shutil
                    temp_dir = os.path.dirname(downloaded_file)
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    print(f"Warning: Failed to cleanup temporary files: {cleanup_error}")

    def get_video_info(self, file_path):
        """
        비디오 파일 정보를 가져옵니다
        
        Args:
            file_path (str): 비디오 파일 경로
            
        Returns:
            dict: 비디오 정보 (duration, fps, size)
        """
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(file_path) as video:
                return {
                    'duration': video.duration,
                    'fps': video.fps,
                    'size': (video.w, video.h)
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def process_local_video_with_info(self, file_path, language=None, save_transcript=False, progress_callback=None):
        """
        비디오 파일을 처리하여 텍스트를 추출합니다
        
        Args:
            file_path (str): 비디오 파일 경로
            language (str): 언어 코드 (예: 'ko', 'en'), None이면 자동 감지
            save_transcript (bool): 텍스트 파일로 저장 여부
            progress_callback (function): 진행률 콜백 함수
            
        Returns:
            dict: 추출 결과 (transcript, detected_language, segments)
        """
        try:
            # 모델 로드
            model = self._load_model()
            
            # 진행률 업데이트
            if progress_callback:
                progress_callback(60, "Extracting audio... / 오디오 추출 중...")
            
            # MoviePy를 사용하여 오디오 추출
            from moviepy.editor import VideoFileClip
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                temp_audio_path = tmp_audio.name
            
            try:
                with VideoFileClip(file_path) as video:
                    audio = video.audio
                    audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                    audio.close()
                
                # 진행률 업데이트
                if progress_callback:
                    progress_callback(65, "Starting transcription... / 텍스트 변환 시작...")
                
                # Whisper로 텍스트 변환
                transcribe_options = {
                    "task": "transcribe",
                    "verbose": False
                }
                
                if language:
                    transcribe_options["language"] = language
                
                result = model.transcribe(temp_audio_path, **transcribe_options)
                
                # 진행률 업데이트
                if progress_callback:
                    progress_callback(85, "Transcription completed! / 텍스트 변환 완료!")
                
                # 결과 반환
                transcript_result = {
                    'transcript': result["text"].strip(),
                    'detected_language': result.get("language", "unknown"),
                    'segments': result.get("segments", [])
                }
                
                # 파일 저장 옵션
                if save_transcript and transcript_result['transcript']:
                    self._save_transcript_file(file_path, transcript_result['transcript'])
                
                return transcript_result
                
            finally:
                # 임시 오디오 파일 정리
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error processing video: {e}")
            raise e
    
    def _save_transcript_file(self, video_path, transcript):
        """텍스트를 파일로 저장합니다"""
        try:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            transcript_path = f"{video_name}_transcript.txt"
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            print(f"Transcript saved to: {transcript_path}")
            return transcript_path
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return None 