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
                # 안전한 progress_callback 래퍼 생성
                def safe_progress_callback(value, message, **kwargs):
                    try:
                        # 함수 시그니처 확인
                        import inspect
                        sig = inspect.signature(progress_callback)
                        param_count = len(sig.parameters)
                        
                        if param_count >= 5:  # 새로운 파라미터를 받을 수 있는 경우
                            progress_callback(
                                value, 
                                message,
                                download_details=kwargs.get('download_details', ''),
                                processing_details=kwargs.get('processing_details', ''),
                                tech_details=kwargs.get('tech_details', '')
                            )
                        elif param_count >= 3:  # 기본 파라미터만 받는 경우
                            progress_callback(value, message, kwargs.get('download_details', ''))
                        else:  # 기존 방식 (2개 파라미터)
                            progress_callback(value, message)
                    except Exception as e:
                        print(f"Progress callback error: {e}")
                        # 기본 방식으로 폴백
                        try:
                            progress_callback(value, message)
                        except:
                            pass
                
                safe_progress_callback(10, "Starting download... / 다운로드 시작...")
                
                def progress_hook(d):
                    try:
                        if d['status'] == 'downloading':
                            # 상세한 다운로드 정보 수집
                            download_info = {}
                            
                            if 'total_bytes' in d and d['total_bytes']:
                                downloaded = d['downloaded_bytes']
                                total = d['total_bytes']
                                percent = (downloaded / total) * 40
                                
                                # 파일 크기 포맷팅
                                def format_bytes(bytes_val):
                                    for unit in ['B', 'KB', 'MB', 'GB']:
                                        if bytes_val < 1024:
                                            return f"{bytes_val:.1f}{unit}"
                                        bytes_val /= 1024
                                    return f"{bytes_val:.1f}TB"
                                
                                download_info['size'] = f"{format_bytes(downloaded)}/{format_bytes(total)}"
                                download_info['percent'] = f"{(downloaded/total)*100:.1f}%"
                                
                                # 다운로드 속도
                                if 'speed' in d and d['speed']:
                                    speed = format_bytes(d['speed']) + "/s"
                                    download_info['speed'] = speed
                                
                                # ETA 계산
                                if 'eta' in d and d['eta']:
                                    eta_seconds = d['eta']
                                    if eta_seconds < 60:
                                        eta_str = f"{eta_seconds:.0f}s"
                                    else:
                                        minutes = eta_seconds // 60
                                        seconds = eta_seconds % 60
                                        eta_str = f"{minutes:.0f}m{seconds:.0f}s"
                                    download_info['eta'] = eta_str
                                
                                # 상세 정보가 있는 progress_callback 호출
                                status_msg = f"Downloading: {download_info['percent']}"
                                if 'speed' in download_info:
                                    status_msg += f" at {download_info['speed']}"
                                if 'eta' in download_info:
                                    status_msg += f" ETA {download_info['eta']}"
                                
                                safe_progress_callback(
                                    10 + percent, 
                                    status_msg + " / 다운로드 중",
                                    download_details=f"{download_info['size']} ({download_info.get('speed', 'N/A')}, ETA: {download_info.get('eta', 'N/A')})",
                                    tech_details=f"Downloaded: {format_bytes(downloaded)}, Speed: {download_info.get('speed', 'Unknown')}"
                                )
                                
                            elif '_percent_str' in d:
                                percent_str = d['_percent_str'].strip('%')
                                try:
                                    percent = float(percent_str) * 0.4
                                    safe_progress_callback(
                                        10 + percent, 
                                        f"Downloading: {percent_str}% / 다운로드 중: {percent_str}%",
                                        download_details=f"Progress: {percent_str}%"
                                    )
                                except:
                                    safe_progress_callback(25, "Downloading... / 다운로드 중...")
                        elif d['status'] == 'finished':
                            filename = d.get('filename', 'video')
                            safe_progress_callback(
                                50, 
                                "Download completed! / 다운로드 완료!",
                                download_details=f"File saved: {os.path.basename(filename)}",
                                processing_details="Preparing for text extraction / 텍스트 추출 준비"
                            )
                    except Exception as e:
                        print(f"Progress callback error: {e}")
                        # 에러 발생 시 기본 메시지
                        if hasattr(progress_callback, '__call__'):
                            try:
                                safe_progress_callback(25, f"Downloading... / 다운로드 중... (Error: {str(e)})")
                            except:
                                pass
                
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
                                # 클라우드 환경에서는 MoviePy 없이 파일 존재만 확인
                                try:
                                    from moviepy.editor import VideoFileClip
                                    with VideoFileClip(selected_file) as test_clip:
                                        if test_clip.duration and test_clip.duration > 0:
                                            print(f"Success with strategy {strategy_num}!")
                                            return selected_file
                                except ImportError:
                                    # MoviePy 없으면 파일 존재와 크기만 확인
                                    if os.path.exists(selected_file) and os.path.getsize(selected_file) > 1000:
                                        print(f"Success with strategy {strategy_num} (no MoviePy validation)!")
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
                # 안전한 progress_callback 래퍼
                def safe_callback(value, message, **kwargs):
                    try:
                        import inspect
                        sig = inspect.signature(progress_callback)
                        param_count = len(sig.parameters)
                        
                        if param_count >= 5:
                            progress_callback(value, message, 
                                            download_details=kwargs.get('download_details', ''),
                                            processing_details=kwargs.get('processing_details', ''),
                                            tech_details=kwargs.get('tech_details', ''))
                        elif param_count >= 3:
                            progress_callback(value, message, kwargs.get('download_details', ''))
                        else:
                            progress_callback(value, message)
                    except:
                        try:
                            progress_callback(value, message)
                        except:
                            pass
                
                safe_callback(5, "Validating URL... / URL 검증 중...")
            
            # YouTube 정보 가져오기
            youtube_info = self.get_youtube_info(url)
            if not youtube_info:
                raise Exception("Failed to get YouTube video info / YouTube 영상 정보를 가져올 수 없습니다")
            
            # 영상 다운로드 (safe_callback 전달)
            downloaded_file = self.download_youtube_video(url, safe_callback)
            
            if progress_callback:
                safe_callback(55, "Processing downloaded video... / 다운로드된 영상 처리 중...", 
                            processing_details="Preparing for audio extraction / 오디오 추출 준비")
            
            # 다운로드된 파일을 로컬 비디오 처리 메서드로 처리 (safe_callback 전달)
            result = self.process_local_video_with_info(downloaded_file, language, save_transcript, safe_callback)
            
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
            # MoviePy 우선 시도
            try:
                from moviepy.editor import VideoFileClip
                with VideoFileClip(file_path) as video:
                    return {
                        'duration': video.duration,
                        'fps': video.fps,
                        'size': (video.w, video.h)
                    }
            except ImportError:
                # MoviePy 없으면 기본 정보만 반환
                import os
                return {
                    'duration': None,
                    'fps': 30,  # 기본값
                    'size': (1920, 1080)  # 기본값
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
                # 안전한 progress_callback 래퍼
                def safe_local_callback(value, message, **kwargs):
                    try:
                        import inspect
                        sig = inspect.signature(progress_callback)
                        param_count = len(sig.parameters)
                        
                        if param_count >= 5:
                            progress_callback(value, message, 
                                            download_details=kwargs.get('download_details', ''),
                                            processing_details=kwargs.get('processing_details', ''),
                                            tech_details=kwargs.get('tech_details', ''))
                        elif param_count >= 3:
                            progress_callback(value, message, kwargs.get('processing_details', ''))
                        else:
                            progress_callback(value, message)
                    except:
                        try:
                            progress_callback(value, message)
                        except:
                            pass
                
                safe_local_callback(60, "Extracting audio... / 오디오 추출 중...", 
                                  processing_details="Using MoviePy for audio extraction")
            
            # 오디오 추출 (MoviePy 우선, 없으면 FFmpeg 직접 사용)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                temp_audio_path = tmp_audio.name
            
            try:
                # MoviePy 우선 시도
                try:
                    from moviepy.editor import VideoFileClip
                    with VideoFileClip(file_path) as video:
                        audio = video.audio
                        audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                        audio.close()
                except ImportError:
                    # MoviePy 없으면 FFmpeg 직접 사용
                    import subprocess
                    ffmpeg_cmd = [
                        'ffmpeg', '-i', file_path, 
                        '-vn',  # 비디오 스트림 제거
                        '-acodec', 'pcm_s16le',  # WAV 포맷
                        '-ar', '16000',  # 샘플링 레이트
                        '-ac', '1',  # 모노
                        '-y',  # 덮어쓰기
                        temp_audio_path
                    ]
                    
                    result = subprocess.run(ffmpeg_cmd, 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=300)  # 5분 타임아웃
                    
                    if result.returncode != 0:
                        raise Exception(f"FFmpeg failed: {result.stderr}")
                    
                    print("Audio extracted using FFmpeg (MoviePy not available)")
                
                # AI 모델 로딩 완료 - 간단한 진행률 업데이트만
                if progress_callback:
                    safe_local_callback(65, "")
                
                # Whisper로 텍스트 변환 (실시간 진행률 포함)
                transcribe_options = {
                    "task": "transcribe",
                    "verbose": True,  # 진행률 표시 활성화
                    "fp16": False  # 안정성 개선
                }
                
                if language:
                    transcribe_options["language"] = language
                
                # 실시간 진행률 모니터링을 위한 래퍼
                import sys
                import io
                from contextlib import redirect_stdout, redirect_stderr
                
                # 고급 진행률 캡처용 클래스
                class ProgressCapture:
                    def __init__(self, callback=None):
                        self.callback = callback
                        self.buffer = ""
                        self.last_progress = 65
                        self.start_time = None
                        import time
                        self.start_time = time.time()
                        
                    def write(self, text):
                        if text and text.strip():
                            self.buffer += text
                            
                            if self.callback:
                                import re
                                import time
                                
                                # 1. 기본 진행률 패턴 (예: "45%|████")
                                progress_match = re.search(r'(\d+)%', text)
                                if progress_match:
                                    percent = int(progress_match.group(1))
                                    # 65%에서 85% 사이로 매핑
                                    mapped_percent = 65 + (percent * 0.2)
                                    self.last_progress = mapped_percent
                                    
                                    # 상태 메시지 기본값
                                    status_msg = f"AI processing: {percent}% / AI 처리중: {percent}%"
                                    processing_details = f"Whisper AI: {percent}%"
                                    tech_details = f"Progress: {percent}/100"
                                    
                                    self.callback(mapped_percent, status_msg, processing_details=processing_details, tech_details=tech_details)
                                
                                # 2. 상세 시간/프레임 정보 패턴 (예: "[00:45<00:30, 2954.12frames/s]")
                                time_pattern = r'\[(\d{2}:\d{2})<(\d{2}:\d{2}),\s*([\d.]+)frames/s\]'
                                time_match = re.search(time_pattern, text)
                                if time_match:
                                    elapsed_time = time_match.group(1)  # 00:45
                                    remaining_time = time_match.group(2)  # 00:30
                                    frame_rate = float(time_match.group(3))  # 2954.12
                                    
                                    # 시간 기반 진행률 계산
                                    def parse_time(time_str):
                                        minutes, seconds = map(int, time_str.split(':'))
                                        return minutes * 60 + seconds
                                    
                                    elapsed_seconds = parse_time(elapsed_time)
                                    remaining_seconds = parse_time(remaining_time)
                                    
                                    if elapsed_seconds + remaining_seconds > 0:
                                        time_progress = elapsed_seconds / (elapsed_seconds + remaining_seconds)
                                        # 65%~85% 범위로 매핑
                                        mapped_percent = 65 + (time_progress * 20)
                                        self.last_progress = mapped_percent
                                        
                                        # 상세 정보 구성
                                        status_msg = f"AI processing: {time_progress*100:.1f}% / AI 처리중: {time_progress*100:.1f}%"
                                        processing_details = f"Time: {elapsed_time} elapsed, {remaining_time} remaining"
                                        tech_details = f"Speed: {frame_rate:.1f} frames/s, Total time: {elapsed_seconds + remaining_seconds}s"
                                        
                                        self.callback(mapped_percent, status_msg, processing_details=processing_details, tech_details=tech_details)
                                
                                # 3. 완료 상태 감지 (예: "[01:23<00:00, 2954.12frames/s]")
                                completed_pattern = r'\[(\d{2}:\d{2})<00:00,\s*([\d.]+)frames/s\]'
                                completed_match = re.search(completed_pattern, text)
                                if completed_match:
                                    total_time = completed_match.group(1)
                                    final_frame_rate = float(completed_match.group(2))
                                    
                                    # 거의 완료 상태로 설정
                                    self.last_progress = 84
                                    status_msg = "AI processing: 99% (finalizing) / AI 처리: 99% (마무리중)"
                                    processing_details = f"Completed in {total_time}, finalizing results"
                                    tech_details = f"Final speed: {final_frame_rate:.1f} frames/s"
                                    
                                    self.callback(84, status_msg, processing_details=processing_details, tech_details=tech_details)
                                
                                # 4. 언어 감지 정보
                                if 'Detected language:' in text:
                                    lang_match = re.search(r'Detected language:\s*(\w+)', text)
                                    if lang_match:
                                        detected_lang = lang_match.group(1)
                                        status_msg = f"Language detected: {detected_lang} / 언어 감지: {detected_lang}"
                                        processing_details = f"Language: {detected_lang}"
                                        tech_details = f"Language detection completed: {detected_lang}"
                                        
                                        self.callback(self.last_progress, status_msg, processing_details=processing_details, tech_details=tech_details)
                                
                                # 5. 성공/완료 메시지
                                if 'Success with strategy' in text:
                                    strategy_match = re.search(r'Success with strategy (\d+)', text)
                                    if strategy_match:
                                        strategy_num = strategy_match.group(1)
                                        status_msg = f"Download successful with strategy {strategy_num} / 전략 {strategy_num}로 다운로드 성공"
                                        processing_details = f"Download strategy {strategy_num} worked"
                                        tech_details = f"Used download strategy: {strategy_num}"
                                        
                                        # 현재 진행률 유지하면서 메시지만 업데이트
                                        self.callback(self.last_progress, status_msg, processing_details=processing_details, tech_details=tech_details)
                                
                                # 6. 전체 처리 시간 계산 및 표시
                                current_time = time.time()
                                if self.start_time:
                                    elapsed_total = current_time - self.start_time
                                    minutes = int(elapsed_total // 60)
                                    seconds = int(elapsed_total % 60)
                                    
                                    # 긴 처리에 대한 사용자 피드백
                                    if elapsed_total > 30:  # 30초 이상 처리 시
                                        if hasattr(self, '_last_time_update') and current_time - self._last_time_update < 5:
                                            pass  # 5초마다 업데이트
                                        else:
                                            self._last_time_update = current_time
                                            tech_details = f"Total processing time: {minutes}m {seconds}s"
                                            
                        sys.__stdout__.write(text)
                        
                    def flush(self):
                        sys.__stdout__.flush()
                
                # 안전한 progress_callback을 ProgressCapture에 전달 (safe_local_callback을 사용)
                
                # 진행률 캡처 설정 (safe_local_callback 사용)
                progress_capture = ProgressCapture(safe_local_callback)
                
                try:
                    # stdout 리다이렉트하여 Whisper 출력 캡처
                    with redirect_stdout(progress_capture):
                        result = model.transcribe(temp_audio_path, **transcribe_options)
                except Exception as e:
                    # 리다이렉트 실패 시 기본 방식으로 처리
                    print(f"Progress capture failed, using default method: {e}")
                    transcribe_options["verbose"] = False  # 에러 방지
                    result = model.transcribe(temp_audio_path, **transcribe_options)
                
                # 진행률 업데이트
                if progress_callback:
                    detected_lang = result.get("language", "unknown")
                    safe_local_callback(85, f"Transcription completed! Language: {detected_lang} / 텍스트 변환 완료! 언어: {detected_lang}", 
                                      processing_details=f"Final result: {detected_lang}", 
                                      tech_details="Transcription 100% complete")
                
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