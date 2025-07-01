import streamlit as st
import tempfile
import os
import torch
import whisper
from moviepy.editor import VideoFileClip
import time

# 페이지 설정 / Page Configuration
st.set_page_config(
    page_title="🎬 Video to Text Converter",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시된 모델 로딩 / Load Cached Model
@st.cache_resource
def load_whisper_model(model_name):
    return whisper.load_model(model_name)

# 사이드바 설정 / Sidebar Configuration  
with st.sidebar:
    st.title("⚙️ Settings / 설정")
    
    # 모델 선택 / Model Selection
    model_options = {
        "tiny": "🚀 Tiny (매우빠름, 기본정확도) / Very Fast, Basic Accuracy",
        "base": "⚡ Base (빠름, 좋은정확도) / Fast, Good Accuracy", 
        "small": "🐌 Small (보통, 높은정확도) / Normal, High Accuracy"
    }
    
    selected_model = st.selectbox(
        "AI Model Size / AI 모델 크기:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=1  # base 모델을 기본으로 설정
    )
    
    # 언어 선택 / Language Selection
    language_options = {
        "auto": "🌐 Auto Detect / 자동감지",
        "ko": "🇰🇷 Korean / 한국어",
        "en": "🇺🇸 English / 영어", 
        "ja": "🇯🇵 Japanese / 일본어",
        "zh": "🇨🇳 Chinese / 중국어"
    }
    
    selected_language = st.selectbox(
        "Language / 언어:",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x]
    )
    
    # GPU 정보 표시 / GPU Information Display
    if torch.cuda.is_available():
        st.success(f"🚀 GPU Available: {torch.cuda.get_device_name(0)}")
    else:
        st.info("💻 Using CPU Mode")

# 메인 페이지 / Main Page
st.title("🎬 Video to Text Converter")
st.markdown("### AI-powered video transcription service / AI 기반 비디오 텍스트 변환 서비스")

# 파일 업로드 / File Upload
uploaded_file = st.file_uploader(
    "Choose a video file / 비디오 파일을 선택하세요",
    type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'],
    help="Maximum file size: 2GB / 최대 파일 크기: 2GB"
)

if uploaded_file is not None:
    # 파일 정보 표시 / Display File Info
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / (1024*1024):.1f} MB"
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.json(file_details)
    
    # 변환 버튼 / Convert Button
    if st.button("🚀 Convert to Text / 텍스트 변환", type="primary", use_container_width=True):
        
        # 진행률 표시 / Progress Display
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 임시 파일 저장 / Save Temporary File
            status_text.text("📁 Saving uploaded file... / 업로드된 파일 저장 중...")
            progress_bar.progress(10)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_video_path = tmp_file.name
            
            # 비디오 정보 추출 / Extract Video Info
            status_text.text("📹 Analyzing video... / 비디오 분석 중...")
            progress_bar.progress(20)
            
            with VideoFileClip(temp_video_path) as video:
                duration_seconds = video.duration
                duration_formatted = f"{int(duration_seconds//60):02d}:{int(duration_seconds%60):02d}"
                fps = video.fps
                resolution = f"{video.w}x{video.h}"
            
            # 비디오 정보 표시 / Display Video Info
            with col2:
                video_info = {
                    "Duration": duration_formatted,
                    "Resolution": resolution,
                    "FPS": f"{fps:.1f}"
                }
                st.json(video_info)
            
            # Whisper 모델 로딩 / Load Whisper Model
            status_text.text(f"🤖 Loading {selected_model} model... / {selected_model} 모델 로딩 중...")
            progress_bar.progress(30)
            
            model = load_whisper_model(selected_model)
            
            # 오디오 추출 / Extract Audio
            status_text.text("🎵 Extracting audio... / 오디오 추출 중...")
            progress_bar.progress(50)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                temp_audio_path = tmp_audio.name
            
            with VideoFileClip(temp_video_path) as video:
                audio = video.audio
                audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                audio.close()
            
            # 텍스트 변환 / Text Conversion
            status_text.text("🔄 Converting speech to text... / 음성을 텍스트로 변환 중...")
            progress_bar.progress(70)
            
            # Whisper 옵션 설정 / Whisper Options
            transcribe_options = {
                "language": None if selected_language == "auto" else selected_language,
                "task": "transcribe"
            }
            
            result = model.transcribe(temp_audio_path, **transcribe_options)
            
            # 완료 / Complete
            progress_bar.progress(100)
            status_text.text("✅ Conversion completed! / 변환 완료!")
            
            # 결과 표시 / Display Results
            st.success("🎉 Transcription completed successfully! / 텍스트 변환이 성공적으로 완료되었습니다!")
            
            # 변환된 텍스트 / Converted Text
            st.subheader("📝 Transcribed Text / 변환된 텍스트")
            
            transcript_text = result["text"].strip()
            
            # 텍스트 영역 / Text Area
            edited_text = st.text_area(
                "Edit the text if needed / 필요시 텍스트를 편집하세요:",
                value=transcript_text,
                height=300,
                help="You can edit the transcribed text before downloading / 다운로드 전에 변환된 텍스트를 편집할 수 있습니다"
            )
            
            # 통계 정보 / Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration / 길이", duration_formatted)
            with col2:
                detected_lang = result.get("language", "Unknown")
                st.metric("Language / 언어", detected_lang.upper())
            with col3:
                word_count = len(edited_text.split())
                st.metric("Words / 단어수", word_count)
            
            # 다운로드 버튼 / Download Button
            st.download_button(
                label="📥 Download Text File / 텍스트 파일 다운로드",
                data=edited_text,
                file_name=f"{uploaded_file.name.split('.')[0]}_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            # 임시 파일 정리 / Clean up temporary files
            try:
                os.unlink(temp_video_path)
                os.unlink(temp_audio_path)
            except:
                pass
                
        except Exception as e:
            st.error(f"❌ Error occurred: {str(e)} / 오류가 발생했습니다: {str(e)}")
            progress_bar.progress(0)
            status_text.text("❌ Conversion failed / 변환 실패")
            
            # 임시 파일 정리 / Clean up temporary files
            try:
                if 'temp_video_path' in locals():
                    os.unlink(temp_video_path)
                if 'temp_audio_path' in locals():
                    os.unlink(temp_audio_path)
            except:
                pass

# 사용법 안내 / Usage Instructions
with st.expander("📖 How to use / 사용 방법"):
    st.markdown("""
    ### English:
    1. **Select Model**: Choose AI model size (tiny=fastest, small=most accurate)
    2. **Select Language**: Choose target language or use auto-detect
    3. **Upload Video**: Click "Browse files" and select your video file
    4. **Convert**: Click "Convert to Text" button and wait for processing
    5. **Download**: Edit text if needed and download the result
    
    ### 한국어:
    1. **모델 선택**: AI 모델 크기 선택 (tiny=최고속도, small=최고정확도)
    2. **언어 선택**: 대상 언어 선택 또는 자동 감지 사용
    3. **비디오 업로드**: "파일 선택" 클릭하여 비디오 파일 선택
    4. **변환**: "텍스트 변환" 버튼 클릭 후 처리 완료까지 대기
    5. **다운로드**: 필요시 텍스트 편집 후 결과 다운로드
    
    **Supported formats**: MP4, AVI, MOV, MKV, FLV, WMV, WEBM
    **Maximum file size**: 2GB
    """)

# 푸터 / Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🎬 Video to Text Converter v1.0 | Powered by OpenAI Whisper & Streamlit</p>
        <p>💡 Free service for everyone! / 모두를 위한 무료 서비스!</p>
    </div>
    """, 
    unsafe_allow_html=True
) 