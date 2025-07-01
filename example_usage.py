"""
Example usage of VideoToTextConverter
VideoToTextConverter 사용 예제
"""

from video_to_text import VideoToTextConverter

def example_youtube_video():
    """
    Example: Extract text from a YouTube video
    예제: YouTube 영상에서 텍스트 추출
    """
    print("=== YouTube Video Example / YouTube 영상 예제 ===")
    
    # Initialize converter with base model
    # base 모델로 변환기 초기화
    converter = VideoToTextConverter(model_size="base")
    
    # Example YouTube URL (replace with your own)
    # 예제 YouTube URL (본인의 URL로 교체하세요)
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Process the video
    # 영상 처리
    transcript = converter.process_youtube_video(
        url=youtube_url,
        language="en",  # or "ko" for Korean / 한국어의 경우 "ko"
        save_transcript=True
    )
    
    if transcript:
        print("Transcript extracted successfully!")
        print("텍스트 추출 성공!")
        print(f"Length: {len(transcript)} characters")
        print(f"길이: {len(transcript)} 글자")
    else:
        print("Failed to extract transcript")
        print("텍스트 추출 실패")

def example_local_video():
    """
    Example: Extract text from a local video file
    예제: 로컬 비디오 파일에서 텍스트 추출
    """
    print("\n=== Local Video Example / 로컬 비디오 예제 ===")
    
    # Initialize converter with small model for faster processing
    # 빠른 처리를 위해 small 모델로 변환기 초기화
    converter = VideoToTextConverter(model_size="small")
    
    # Example local video file path (replace with your own)
    # 예제 로컬 비디오 파일 경로 (본인의 파일 경로로 교체하세요)
    video_file = "my_video.mp4"  # Change this to your video file path
    
    # Check if file exists
    # 파일 존재 확인
    import os
    if not os.path.exists(video_file):
        print(f"File not found: {video_file}")
        print(f"파일을 찾을 수 없음: {video_file}")
        print("Please replace 'my_video.mp4' with your actual video file path")
        print("'my_video.mp4'를 실제 비디오 파일 경로로 교체해주세요")
        return
    
    # Process the video
    # 영상 처리
    transcript = converter.process_local_video(
        video_path=video_file,
        language=None,  # Auto-detect language / 언어 자동 감지
        save_transcript=True
    )
    
    if transcript:
        print("Transcript extracted successfully!")
        print("텍스트 추출 성공!")
        print(f"Length: {len(transcript)} characters")
        print(f"길이: {len(transcript)} 글자")
    else:
        print("Failed to extract transcript")
        print("텍스트 추출 실패")

def example_batch_processing():
    """
    Example: Process multiple videos
    예제: 여러 영상 처리
    """
    print("\n=== Batch Processing Example / 배치 처리 예제 ===")
    
    # Initialize converter once for efficiency
    # 효율성을 위해 변환기를 한 번만 초기화
    converter = VideoToTextConverter(model_size="tiny")  # Use tiny for speed
    
    # List of videos to process
    # 처리할 영상 목록
    videos = [
        # Add your YouTube URLs or local file paths here
        # 여기에 YouTube URL 또는 로컬 파일 경로를 추가하세요
        # "https://www.youtube.com/watch?v=VIDEO_ID1",
        # "https://www.youtube.com/watch?v=VIDEO_ID2",
        # "video1.mp4",
        # "video2.mp4",
    ]
    
    if not videos:
        print("No videos to process. Add URLs or file paths to the 'videos' list.")
        print("처리할 영상이 없습니다. 'videos' 목록에 URL 또는 파일 경로를 추가하세요.")
        return
    
    for i, video in enumerate(videos, 1):
        print(f"\nProcessing video {i}/{len(videos)}: {video}")
        print(f"영상 처리 중 {i}/{len(videos)}: {video}")
        
        try:
            if video.startswith(('http://', 'https://')):
                # YouTube video
                transcript = converter.process_youtube_video(video, save_transcript=True)
            else:
                # Local video file
                transcript = converter.process_local_video(video, save_transcript=True)
            
            if transcript:
                print(f"✓ Success: {len(transcript)} characters extracted")
                print(f"✓ 성공: {len(transcript)} 글자 추출됨")
            else:
                print("✗ Failed to extract transcript")
                print("✗ 텍스트 추출 실패")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            print(f"✗ 오류: {e}")

if __name__ == "__main__":
    print("VideoToTextConverter Examples")
    print("VideoToTextConverter 예제")
    print("="*50)
    
    # Run examples
    # 예제 실행
    try:
        # Uncomment the examples you want to run
        # 실행하고 싶은 예제의 주석을 제거하세요
        
        # example_youtube_video()
        # example_local_video()
        # example_batch_processing()
        
        print("\nTo run examples, uncomment the function calls above.")
        print("예제를 실행하려면 위의 함수 호출 주석을 제거하세요.")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        print("사용자에 의해 프로세스가 중단됨")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print(f"예상치 못한 오류: {e}") 