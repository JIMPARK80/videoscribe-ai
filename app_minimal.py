import streamlit as st
import tempfile
import os
import torch
import whisper

st.set_page_config(
    page_title="🎬 Video to Text Converter",
    page_icon="🎬",
    layout="wide"
)

@st.cache_resource
def load_whisper_model(model_name):
    return whisper.load_model(model_name)

# 사이드바
with st.sidebar:
    st.title("⚙️ Settings")
    
    model_options = {
        "tiny": "🚀 Tiny (Fastest)",
        "base": "⚡ Base (Balanced)", 
        "small": "🎯 Small (Most Accurate)"
    }
    
    selected_model = st.selectbox(
        "AI Model Size:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=1
    )
    
    language_options = {
        "auto": "🌐 Auto Detect",
        "ko": "🇰🇷 Korean",
        "en": "🇺🇸 English",
        "ja": "🇯🇵 Japanese",
        "zh": "🇨🇳 Chinese"
    }
    
    selected_language = st.selectbox(
        "Language:",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x]
    )
    
    # GPU 정보
    if torch.cuda.is_available():
        st.success("🚀 GPU Available")
    else:
        st.info("💻 CPU Mode")

# 메인 인터페이스
st.title("🎬 Video to Text Converter")
st.markdown("### AI-powered video transcription service")

uploaded_file = st.file_uploader(
    "Choose an audio or video file",
    type=['mp3', 'wav', 'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'm4a', 'aac'],
    help="Maximum file size: 2GB"
)

if uploaded_file is not None:
    # 파일 정보
    file_size_mb = uploaded_file.size / (1024*1024)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📁 **File:** {uploaded_file.name}")
        st.info(f"📊 **Size:** {file_size_mb:.1f} MB")
    
    with col2:
        st.info(f"🤖 **Model:** {model_options[selected_model]}")
        st.info(f"🌐 **Language:** {language_options[selected_language]}")
    
    # 변환 버튼
    if st.button("🚀 Start Conversion", type="primary", use_container_width=True):
        
        # 진행률 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 파일 저장
            status_text.text("📁 Processing uploaded file...")
            progress_bar.progress(20)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name
            
            # 모델 로딩
            status_text.text(f"🤖 Loading {selected_model} model...")
            progress_bar.progress(40)
            
            model = load_whisper_model(selected_model)
            
            # 음성 인식
            status_text.text("🔄 Converting speech to text...")
            progress_bar.progress(60)
            
            # Whisper 옵션
            transcribe_options = {
                "task": "transcribe",
                "verbose": False
            }
            
            if selected_language != "auto":
                transcribe_options["language"] = selected_language
            
            # 변환 실행
            result = model.transcribe(temp_file_path, **transcribe_options)
            
            # 완료
            progress_bar.progress(100)
            status_text.text("✅ Conversion completed!")
            
            # 결과 표시
            st.success("🎉 Transcription completed successfully!")
            
            # 텍스트 결과
            st.subheader("📝 Transcribed Text")
            
            transcript_text = result["text"].strip()
            
            if transcript_text:
                # 편집 가능한 텍스트
                edited_text = st.text_area(
                    "Edit the transcribed text:",
                    value=transcript_text,
                    height=250,
                    help="You can edit the text before downloading"
                )
                
                # 통계
                word_count = len(edited_text.split())
                char_count = len(edited_text)
                detected_lang = result.get("language", "unknown")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🗣️ Language", detected_lang.upper())
                with col2:
                    st.metric("📝 Words", word_count)
                with col3:
                    st.metric("🔤 Characters", char_count)
                
                # 다운로드 버튼
                st.download_button(
                    label="📥 Download Text File",
                    data=edited_text,
                    file_name=f"{uploaded_file.name.split('.')[0]}_transcript.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            else:
                st.warning("⚠️ No speech detected in the file. Please check if the file contains audio.")
            
            # 임시 파일 정리
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
        except Exception as e:
            st.error(f"❌ Error occurred: {str(e)}")
            st.error("Please try with a different file or model size.")
            progress_bar.progress(0)
            status_text.text("❌ Conversion failed")
            
            # 오류 시에도 파일 정리
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass

# 사용법 안내
with st.expander("📖 How to Use"):
    st.markdown("""
    ### Quick Start Guide:
    
    1. **🎵 Upload File**: Choose your audio or video file (up to 2GB)
    2. **🤖 Select Model**: 
       - **Tiny**: Fastest processing, good for testing
       - **Base**: Balanced speed and accuracy (recommended)
       - **Small**: Highest accuracy, slower processing
    3. **🌐 Choose Language**: Select target language or use auto-detection
    4. **🚀 Convert**: Click "Start Conversion" and wait for processing
    5. **📝 Edit & Download**: Review, edit if needed, and download your transcript
    
    ### Supported Formats:
    **Audio**: MP3, WAV, M4A, AAC  
    **Video**: MP4, AVI, MOV, MKV, FLV, WMV, WEBM
    
    ### Tips:
    - Clear audio gives better results
    - Longer files take more time to process
    - Use GPU mode for faster processing when available
    """)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎬 <strong>Video to Text Converter v1.0</strong></p>
    <p>Powered by OpenAI Whisper & Streamlit | Free service for everyone!</p>
</div>
""", unsafe_allow_html=True) 