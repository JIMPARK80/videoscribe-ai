"""
비디오 텍스트 변환기 모듈
Video to Text Converter Module
"""

import os
import tempfile


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