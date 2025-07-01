# Video File to Text Extractor / 비디오 파일 텍스트 추출기

A powerful Python application that extracts text (transcription) from video files using OpenAI's Whisper AI with GPU acceleration support.

OpenAI의 Whisper AI와 GPU 가속을 지원하는 강력한 Python 애플리케이션으로 비디오 파일에서 텍스트(전사)를 추출합니다.

## Features / 기능

- 🎥 Extract text from local video files / 로컬 비디오 파일에서 텍스트 추출
- 🚀 **GPU acceleration support** (CUDA) / GPU 가속 지원 (CUDA)
- 🌍 Support for multiple languages with auto-detection / 자동 감지 기능이 있는 다국어 지원
- 🖥️ Beautiful GUI and CLI interfaces / 아름다운 GUI 및 CLI 인터페이스
- 📊 **Real-time video info display** (duration, language, word count) / 실시간 비디오 정보 표시 (길이, 언어, 단어수)
- 💾 Save transcripts with timestamps / 타임스탬프가 포함된 전사본 저장
- 🤖 Multiple AI model sizes for different accuracy/speed trade-offs / 정확도/속도 절충을 위한 다양한 AI 모델 크기
- ⚡ Optimized for RTX/GTX series GPUs / RTX/GTX 시리즈 GPU에 최적화

## Installation / 설치

### Prerequisites / 전제 조건

- Python 3.8 or higher / Python 3.8 이상
- FFmpeg (for audio/video processing) / FFmpeg (오디오/비디오 처리용)

### FFmpeg Installation / FFmpeg 설치

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your PATH environment variable
4. Or use Chocolatey: `choco install ffmpeg`

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Python Dependencies / Python 의존성

```bash
pip install -r requirements.txt
```

## Usage / 사용법

### Command Line Interface (CLI)

#### Local Video File / 로컬 비디오 파일
```bash
python video_to_text.py "/path/to/your/video.mp4"
```

#### Advanced Options / 고급 옵션
```bash
# Specify language / 언어 지정
python video_to_text.py "video.mp4" --language ko

# Use different model size with GPU / GPU와 다른 모델 크기 사용
python video_to_text.py "video.mp4" --model large

# Force CPU usage (disable GPU) / CPU 사용 강제 (GPU 비활성화)
python video_to_text.py "video.mp4" --cpu

# Include timestamps / 타임스탬프 포함
python video_to_text.py "video.mp4" --timestamps

# Don't save transcript file / 전사본 파일 저장 안함
python video_to_text.py "video.mp4" --no-save
```

### Graphical User Interface (GUI)

```bash
python gui_app.py
```

The GUI provides an easy-to-use interface where you can:
- Select local video files with file browser
- Choose the AI model size with performance indicators
- Select the language (or use auto-detection)
- Enable/disable GPU acceleration
- **View real-time video information** (duration, detected language, word count)
- View the extracted text with syntax highlighting
- Save the transcript to a file

GUI는 다음과 같은 사용하기 쉬운 인터페이스를 제공합니다:
- 파일 브라우저로 로컬 비디오 파일 선택
- 성능 지표가 있는 AI 모델 크기 선택
- 언어 선택 (또는 자동 감지 사용)
- GPU 가속 활성화/비활성화
- **실시간 비디오 정보 표시** (길이, 감지된 언어, 단어수)
- 구문 강조 기능이 있는 추출된 텍스트 보기
- 전사본을 파일로 저장

## Model Sizes / 모델 크기

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny  | 39 MB | Fastest | Lowest |
| base  | 74 MB | Fast | Good |
| small | 244 MB | Medium | Better |
| medium| 769 MB | Slow | High |
| large | 1550 MB | Slowest | Highest |

## Supported Languages / 지원 언어

The application supports automatic language detection and manual specification for:
- Korean (ko) / 한국어
- English (en) / 영어
- Japanese (ja) / 일본어
- Chinese (zh) / 중국어
- Spanish (es) / 스페인어
- French (fr) / 프랑스어
- German (de) / 독일어
- And many more... / 그 외 다수...

## Supported Video Formats / 지원 비디오 형식

- MP4
- AVI
- MOV
- MKV
- FLV
- WMV
- WEBM
- And more formats supported by FFmpeg / FFmpeg에서 지원하는 더 많은 형식

## Examples / 예제

### CLI Examples / CLI 예제

```bash
# Basic usage / 기본 사용법
python video_to_text.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Korean language video / 한국어 영상
python video_to_text.py "https://www.youtube.com/watch?v=VIDEO_ID" --language ko

# High accuracy model / 고정확도 모델
python video_to_text.py "my_video.mp4" --model large

# Multiple options / 여러 옵션
python video_to_text.py "lecture.mp4" --model medium --language en --no-save
```

## Troubleshooting / 문제 해결

### Common Issues / 일반적인 문제

1. **FFmpeg not found / FFmpeg를 찾을 수 없음**
   - Make sure FFmpeg is installed and added to PATH
   - FFmpeg가 설치되어 있고 PATH에 추가되었는지 확인

2. **YouTube download fails / YouTube 다운로드 실패**
   - Check if the URL is valid / URL이 유효한지 확인
   - Some videos may be restricted / 일부 영상은 제한될 수 있음

3. **Out of memory error / 메모리 부족 오류**
   - Use a smaller model size (tiny or base) / 더 작은 모델 크기 사용 (tiny 또는 base)
   - Close other applications / 다른 애플리케이션 종료

4. **Slow processing / 처리 속도 느림**
   - Use GPU if available (requires CUDA setup) / GPU 사용 (CUDA 설정 필요)
   - Use smaller model for faster processing / 빠른 처리를 위해 작은 모델 사용

## Requirements / 요구사항

- Python 3.8+
- 4GB+ RAM (8GB+ recommended for larger models) / 4GB+ RAM (큰 모델의 경우 8GB+ 권장)
- Internet connection for YouTube videos / YouTube 영상용 인터넷 연결
- FFmpeg for audio/video processing / 오디오/비디오 처리용 FFmpeg

## License / 라이센스

This project is open source and available under the MIT License.

이 프로젝트는 오픈 소스이며 MIT 라이센스 하에 제공됩니다.

## Contributing / 기여

Contributions are welcome! Please feel free to submit a Pull Request.

기여를 환영합니다! 언제든지 Pull Request를 제출해 주세요. 