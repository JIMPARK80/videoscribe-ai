import streamlit as st
import tempfile
import os
import torch
import whisper

# 모듈 임포트
from src.ffmpeg_setup import setup_ffmpeg_path
from src.converter import VideoToTextConverter

# FFmpeg 경로 설정 실행
setup_ffmpeg_path()

# 환경 감지 / Environment Detection
def get_environment_config():
    """환경에 따른 설정 반환 / Return config based on environment"""
    # 다양한 클라우드 환경 감지 방법
    cloud_indicators = [
        os.getenv('STREAMLIT_SHARING_MODE'),  # Streamlit Cloud
        'streamlit.app' in os.getenv('SERVER_NAME', ''),  # Streamlit Cloud
        os.getenv('CODESPACE_NAME'),  # GitHub Codespaces
        os.getenv('GITPOD_WORKSPACE_ID'),  # Gitpod
        os.getenv('RAILWAY_ENVIRONMENT'),  # Railway
        'herokuapp.com' in os.getenv('SERVER_NAME', ''),  # Heroku
        os.path.exists('/app'),  # Docker container
        not os.path.exists('D:\\'),  # Windows 로컬 드라이브 없음
    ]
    
    if any(cloud_indicators):
        return {
            "max_file_size_mb": 200,
            "max_file_display": "200MB",
            "environment": "☁️ Cloud Environment"
        }
    else:
        return {
            "max_file_size_mb": 2048,  # 2GB
            "max_file_display": "2GB", 
            "environment": "🏠 Local Environment"
        }

# 현재 테마 감지 함수 / Current Theme Detection Function
def get_current_theme():
    """현재 설정된 테마를 반환합니다 / Return current theme setting"""
    config_path = ".streamlit/config.toml"
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 배경색으로 테마 판단
                if 'backgroundColor = "#FFFFFF"' in content:
                    return "light"
                elif 'backgroundColor = "#0E1117"' in content:
                    return "dark"
        return "light"  # 기본값
    except:
        return "light"

# 테마 설정 함수 / Theme Configuration Function
def update_theme_config(theme_type):
    """테마 설정을 업데이트합니다 / Update theme configuration"""
    config_path = ".streamlit/config.toml"
    
    # 테마별 설정
    themes = {
        "light": {
            "primaryColor": "#FF6B6B",
            "backgroundColor": "#FFFFFF", 
            "secondaryBackgroundColor": "#F0F2F6",
            "textColor": "#262730"
        },
        "dark": {
            "primaryColor": "#00D4FF",  # 시원한 파란색
            "backgroundColor": "#0E1117",  # 깊은 다크
            "secondaryBackgroundColor": "#1E1E1E",  # 더 진한 회색
            "textColor": "#FFFFFF"  # 순백색 텍스트
        },
        "midnight": {
            "primaryColor": "#4ECDC4",  # 민트 그린
            "backgroundColor": "#1A1A2E",  # 미드나이트 블루
            "secondaryBackgroundColor": "#16213E",  # 더 진한 미드나이트
            "textColor": "#E0E0E0"  # 부드러운 흰색
        },
        "neon": {
            "primaryColor": "#FF00FF",  # 마젠타 네온
            "backgroundColor": "#000000",  # 순수 검정
            "secondaryBackgroundColor": "#1A1A1A",  # 짙은 회색
            "textColor": "#00FF00"  # 네온 그린 텍스트
        }
    }
    
    try:
        # config.toml 파일 생성/업데이트
        config_content = f"""[server]
maxUploadSize = 2048

[theme]
primaryColor = "{themes[theme_type]['primaryColor']}"
backgroundColor = "{themes[theme_type]['backgroundColor']}"
secondaryBackgroundColor = "{themes[theme_type]['secondaryBackgroundColor']}"
textColor = "{themes[theme_type]['textColor']}"

[browser]
gatherUsageStats = false
"""
        
        # 디렉토리 생성 (없는 경우)
        os.makedirs(".streamlit", exist_ok=True)
        
        # 파일 쓰기
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        return True
    except Exception as e:
        st.error(f"❌ Theme update failed: {e}")
        return False

# 환경 설정 로드
ENV_CONFIG = get_environment_config()

# 페이지 설정 / Page Configuration
st.set_page_config(
    page_title="🎬 Video to Text Converter",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시된 변환기 로딩 / Load Cached Converter
@st.cache_resource
def load_video_converter(model_name, use_gpu=True):
    return VideoToTextConverter(model_size=model_name, use_gpu=use_gpu)

# 사이드바 설정 / Sidebar Configuration  
with st.sidebar:
    st.title("⚙️ Settings / 설정")
    
    # 환경 정보 표시
    st.info(f"🌍 Environment: {ENV_CONFIG['environment']}")
    st.info(f"📁 Max File Size: {ENV_CONFIG['max_file_display']}")
    
    # 로컬 환경에서만 테마 선택 표시
    if ENV_CONFIG['environment'] == "🏠 Local Environment":
        st.markdown("---")
        theme_options = {
            "light": "☀️ Light Theme / 라이트 테마",
            "dark": "🌙 Dark Theme / 다크 테마",
            "midnight": "🌌 Midnight Blue / 미드나이트 블루",
            "neon": "⚡ Neon Dark / 네온 다크"
        }
        
        # 세션 상태로 현재 테마 관리
        if 'current_theme' not in st.session_state:
            st.session_state.current_theme = get_current_theme()
        
        selected_theme = st.selectbox(
            "🎨 Theme / 테마:",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=list(theme_options.keys()).index(st.session_state.current_theme) if st.session_state.current_theme in theme_options else 0,
            help="Select theme and click apply / 테마를 선택하고 적용 버튼을 클릭하세요"
        )
        
        # 현재 테마와 다른 경우에만 버튼 표시
        if selected_theme != st.session_state.current_theme:
            if st.button("🔄 Apply Theme / 테마 적용", 
                        type="primary",
                        help="Apply selected theme immediately / 선택한 테마를 즉시 적용"):
                # 테마 적용 및 즉시 새로고침
                if update_theme_config(selected_theme):
                    st.session_state.current_theme = selected_theme
                    st.success(f"✅ Theme applied! Refreshing... / 테마 적용 완료! 새로고침 중...")
                    
                    # 즉시 재실행
                    try:
                        st.rerun()
                    except (AttributeError, NameError):
                        try:
                            st.experimental_rerun()
                        except (AttributeError, NameError):
                            # 최후 수단: JavaScript 새로고침 + 효과
                            st.balloons()
                            st.markdown("""
                            <script>
                            setTimeout(() => {
                                window.parent.location.reload();
                            }, 1000);
                            </script>
                            """, unsafe_allow_html=True)
        else:
            st.success(f"✅ Current theme: {theme_options[st.session_state.current_theme]}")
            st.info("💡 Select a different theme to apply changes / 다른 테마를 선택하여 변경하세요")
    
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
        index=1
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
        st.success("🚀 GPU Available")
    else:
        st.info("💻 CPU Mode")

# 메인 페이지 / Main Page
st.title("🎬 Video to Text Converter")
st.markdown("### AI-powered video transcription service / AI 기반 비디오 텍스트 변환 서비스")

# 환경별 안내 메시지
if ENV_CONFIG['environment'] == "☁️ Cloud Environment":
    st.info("☁️ **Cloud Demo Version** - For larger files (>200MB), please use the local version / 큰 파일(200MB 초과)은 로컬 버전을 사용하세요")
else:
    st.success("🏠 **Local Production Version** - Full features with GPU acceleration up to 2GB / GPU 가속을 포함한 모든 기능, 최대 2GB 지원")

# 파일 업로드 / File Upload
uploaded_file = st.file_uploader(
    "Choose a video or audio file / 비디오 또는 오디오 파일을 선택하세요",
    type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'mp3', 'wav', 'm4a', 'aac'],
    help=f"Maximum file size: {ENV_CONFIG['max_file_display']} / 최대 파일 크기: {ENV_CONFIG['max_file_display']}"
)

if uploaded_file is not None:
    # 파일 크기 체크
    file_size_mb = uploaded_file.size / (1024*1024)
    
    if file_size_mb > ENV_CONFIG['max_file_size_mb']:
        st.error(f"❌ File too large! Maximum size: {ENV_CONFIG['max_file_display']} / 파일이 너무 큽니다! 최대 크기: {ENV_CONFIG['max_file_display']}")
        st.stop()
    
    # 파일 정보 표시 / Display File Info
    col1, col2 = st.columns(2)
    with col1:
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{file_size_mb:.1f} MB"
        }
        st.json(file_details)
    
    with col2:
        model_info = {
            "Selected Model": model_options[selected_model].split(' /')[0],
            "Language": language_options[selected_language].split(' /')[0]
        }
        st.json(model_info)
    
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
                temp_file_path = tmp_file.name
            
            # 변환기 로딩 / Load Converter
            status_text.text(f"🤖 Loading {selected_model} model... / {selected_model} 모델 로딩 중...")
            progress_bar.progress(30)
            
            use_gpu = torch.cuda.is_available()
            converter = load_video_converter(selected_model, use_gpu)
            
            # 텍스트 변환 / Text Conversion
            status_text.text("🔄 Converting speech to text... / 음성을 텍스트로 변환 중...")
            progress_bar.progress(70)
            
            # 언어 설정
            language = None if selected_language == "auto" else selected_language
            
            # 변환 실행
            result = converter.process_local_video_with_info(
                temp_file_path, 
                language=language, 
                save_transcript=False
            )
            
            # 완료 / Complete
            progress_bar.progress(100)
            status_text.text("✅ Conversion completed! / 변환 완료!")
            
            # 결과 표시 / Display Results
            st.success("🎉 Transcription completed successfully! / 텍스트 변환이 성공적으로 완료되었습니다!")
            
            # 변환된 텍스트 / Converted Text
            st.subheader("📝 Transcribed Text / 변환된 텍스트")
            
            transcript_text = result.get("transcript", "").strip()
            
            if transcript_text:
                # 텍스트 영역 / Text Area
                edited_text = st.text_area(
                    "Edit the text if needed / 필요시 텍스트를 편집하세요:",
                    value=transcript_text,
                    height=300,
                    help="You can edit the transcribed text before downloading / 다운로드 전에 변환된 텍스트를 편집할 수 있습니다"
                )
                
                # 통계 정보 / Statistics
                word_count = len(edited_text.split())
                char_count = len(edited_text)
                detected_lang = result.get("detected_language", "unknown")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Language / 언어", detected_lang.upper())
                with col2:
                    st.metric("Words / 단어수", word_count)
                with col3:
                    st.metric("Characters / 문자수", char_count)
                
                # 다운로드 버튼 / Download Button
                st.download_button(
                    label="📥 Download Text File / 텍스트 파일 다운로드",
                    data=edited_text,
                    file_name=f"{uploaded_file.name.split('.')[0]}_transcript.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No speech detected in the file. Please check if the file contains audio. / 파일에서 음성이 감지되지 않았습니다. 파일에 오디오가 포함되어 있는지 확인해주세요.")
            
            # 임시 파일 정리 / Clean up temporary files
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
        except Exception as e:
            st.error(f"❌ Error occurred: {str(e)} / 오류가 발생했습니다: {str(e)}")
            progress_bar.progress(0)
            status_text.text("❌ Conversion failed / 변환 실패")
            
            # 임시 파일 정리 / Clean up temporary files
            try:
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)
            except:
                pass

# 사용법 안내 / Usage Instructions
with st.expander("📖 How to use / 사용 방법"):
    st.markdown(f"""
    ### English:
    1. **Select Model**: Choose AI model size (tiny=fastest, small=most accurate)
    2. **Select Language**: Choose target language or use auto-detect
    3. **Upload File**: Click "Browse files" and select your audio/video file
    4. **Convert**: Click "Convert to Text" button and wait for processing
    5. **Download**: Edit text if needed and download the result
    
    ### 한국어:
    1. **모델 선택**: AI 모델 크기 선택 (tiny=최고속도, small=최고정확도)
    2. **언어 선택**: 대상 언어 선택 또는 자동 감지 사용
    3. **파일 업로드**: "파일 선택" 클릭하여 오디오/비디오 파일 선택
    4. **변환**: "텍스트 변환" 버튼 클릭 후 처리 완료까지 대기
    5. **다운로드**: 필요시 텍스트 편집 후 결과 다운로드
    
    **Supported formats**: MP4, AVI, MOV, MKV, FLV, WMV, WEBM, MP3, WAV, M4A, AAC
    **Current Environment**: {ENV_CONFIG['environment']}
    **Maximum file size**: {ENV_CONFIG['max_file_display']}
    """)

# 푸터 / Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center'>
        <p>🎬 Video to Text Converter v1.0 | Powered by OpenAI Whisper & Streamlit</p>
        <p>💡 Free service for everyone! / 모두를 위한 무료 서비스!</p>
        <p><small>{ENV_CONFIG['environment']} - Max File: {ENV_CONFIG['max_file_display']}</small></p>
    </div>
    """, 
    unsafe_allow_html=True
) 