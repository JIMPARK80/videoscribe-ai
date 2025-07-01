# 🎬 Video to Text Converter - Web Version

AI-powered video transcription service that converts video files to text using OpenAI Whisper.

## ✨ Features

- 🤖 **AI-Powered**: Uses OpenAI Whisper for high-accuracy transcription
- 🌐 **Multi-language**: Supports Korean, English, Japanese, Chinese, and auto-detection
- ⚡ **Fast Processing**: GPU acceleration when available
- 📱 **Web-based**: No installation required, works on any device
- 🆓 **Free Service**: Completely free to use
- 📝 **Editable Results**: Edit transcribed text before downloading

## 🚀 How to Use

1. **Select Model**: Choose AI model size (tiny=fastest, small=most accurate)
2. **Select Language**: Choose target language or use auto-detect
3. **Upload Video**: Select your video file (up to 200MB)
4. **Convert**: Click "Convert to Text" and wait for processing
5. **Download**: Edit text if needed and download the result

## 📋 Supported Formats

- **Video**: MP4, AVI, MOV, MKV, FLV, WMV, WEBM
- **Maximum file size**: 2GB
- **Languages**: Korean, English, Japanese, Chinese, and more

## 💻 Local Development

### Prerequisites
- Python 3.8+
- FFmpeg installed

### Installation
```bash
git clone <repository-url>
cd video-to-text-converter
pip install -r requirements_web.txt
```

### Run Locally
```bash
streamlit run web_app.py
```

## 🌐 Live Demo

Visit the live demo at: [Your deployment URL]

## 🔧 Technical Details

- **AI Model**: OpenAI Whisper
- **Framework**: Streamlit
- **Processing**: Server-side GPU/CPU
- **Languages**: Python

## 📞 Support

If you encounter any issues, please create an issue in this repository.

## 📄 License

This project is open source and available under the MIT License.

---

Made with ❤️ using OpenAI Whisper and Streamlit 