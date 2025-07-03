import streamlit as st
import tempfile
import os
import torch
import traceback
import whisper

# 모듈 임포트
from src.ffmpeg_setup import setup_ffmpeg_path
from src.converter import VideoToTextConverter

# 환경 감지 헬퍼 함수 / Environment Detection Helper
def is_cloud_environment():
    """클라우드 환경인지 확인 / Check if running in cloud environment"""
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
    return any(cloud_indicators)

# FFmpeg 경로 설정 실행 (클라우드 환경에서는 스킵)
def setup_ffmpeg_safely():
    """FFmpeg를 안전하게 설정 / Setup FFmpeg safely"""
    try:
        if not is_cloud_environment():
            setup_ffmpeg_path()
        else:
            # 클라우드 환경에서는 시스템 FFmpeg 사용
            pass
    except Exception as e:
        # FFmpeg 설정 실패 시 조용히 넘어감
        print(f"FFmpeg setup skipped: {e}")

# FFmpeg 설정 실행
setup_ffmpeg_safely()

# yt-dlp 버전 확인을 위한 임포트
try:
    import yt_dlp
    YT_DLP_VERSION = yt_dlp.version.__version__
except (ImportError, AttributeError) as e:
    YT_DLP_VERSION = "Not installed"
    print(f"yt-dlp not available: {e}")

# 환경 감지 / Environment Detection
def get_environment_config():
    """환경에 따른 설정 반환 / Return config based on environment"""
    if is_cloud_environment():
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

# 전체 페이지 스타일링 / Global Page Styling
st.markdown("""
<style>
/* 전체 페이지 스타일 */
.main > div {
    padding-top: 2rem;
}

/* 메인 컨테이너 카드 스타일 */
.main .block-container {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
}

/* 제목 스타일 */
h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    font-size: 3rem !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    text-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* 부제목 스타일 */
h3 {
    text-align: center;
    color: #6c757d;
    font-weight: 400;
    margin-bottom: 2rem !important;
}

/* 탭 스타일 개선 */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 15px;
    padding: 8px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    color: white;
    font-weight: 600;
    padding: 12px 24px;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
}

.stTabs [data-baseweb="tab"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.4);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
    box-shadow: 0 4px 15px rgba(255,107,107,0.4);
}

/* 버튼 스타일 개선 */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.4);
}

.stButton > button:active {
    transform: translateY(-1px);
}

/* Primary 버튼 특별 스타일 */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
    box-shadow: 0 4px 15px rgba(255,107,107,0.3);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ffa500 0%, #ff6b6b 100%);
    box-shadow: 0 6px 20px rgba(255,107,107,0.4);
}

/* 파일 업로더 스타일 */
.stFileUploader > div {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 2px dashed #667eea;
    border-radius: 15px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stFileUploader > div:hover {
    border-color: #ff6b6b;
    background: linear-gradient(135deg, rgba(255,107,107,0.1) 0%, rgba(255,165,0,0.05) 100%);
}

/* 텍스트 입력 스타일 */
.stTextInput > div > div > input {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 2px solid #667eea;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #ff6b6b;
    box-shadow: 0 0 0 3px rgba(255,107,107,0.2);
}

/* 선택 박스 스타일 */
.stSelectbox > div > div > div {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 2px solid #667eea;
    border-radius: 12px;
    transition: all 0.3s ease;
}

/* 메트릭 카드 스타일 */
.metric-container {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
}

/* 정보 박스 스타일 */
.stInfo {
    background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.05) 100%);
    border-left: 4px solid #667eea;
    border-radius: 12px;
    padding: 1rem;
    backdrop-filter: blur(10px);
}

.stSuccess {
    background: linear-gradient(135deg, rgba(40,167,69,0.1) 0%, rgba(40,167,69,0.05) 100%);
    border-left: 4px solid #28a745;
    border-radius: 12px;
    padding: 1rem;
    backdrop-filter: blur(10px);
}

.stError {
    background: linear-gradient(135deg, rgba(220,53,69,0.1) 0%, rgba(220,53,69,0.05) 100%);
    border-left: 4px solid #dc3545;
    border-radius: 12px;
    padding: 1rem;
    backdrop-filter: blur(10px);
}

/* 사이드바 스타일 */
.css-1d391kg {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255,255,255,0.2);
}

/* 확장 가능한 섹션 스타일 */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 12px;
    padding: 1rem;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.2);
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.05) 100%);
    border-color: #667eea;
}

/* 체크박스 스타일 */
.stCheckbox > label {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.2);
}

.stCheckbox > label:hover {
    background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.05) 100%);
    border-color: #667eea;
}

/* 애니메이션 효과 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.main > div {
    animation: fadeIn 0.6s ease-out;
}

/* 텍스트 영역 스타일 */
.stTextArea > div > div > textarea {
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    border: 2px solid #667eea;
    border-radius: 12px;
    padding: 1rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    transition: all 0.3s ease;
}

.stTextArea > div > div > textarea:focus {
    border-color: #ff6b6b;
    box-shadow: 0 0 0 3px rgba(255,107,107,0.2);
}

/* 다운로드 버튼 특별 스타일 */
.stDownloadButton > button {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(40,167,69,0.3);
    transition: all 0.3s ease;
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #20c997 0%, #28a745 100%);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(40,167,69,0.4);
}
</style>
""", unsafe_allow_html=True)

# GPU 사용 가능 여부 확인 / Check GPU availability
use_gpu = torch.cuda.is_available()

# 캐시된 변환기 로딩 / Load Cached Converter
@st.cache_resource
def load_video_converter(model_name, use_gpu=True):
    """비디오 변환기 로딩 (오류 처리 강화)"""
    try:
        # 클라우드 환경에서는 GPU 사용 안함
        if is_cloud_environment():
            use_gpu = False
        
        converter = VideoToTextConverter(model_size=model_name, use_gpu=use_gpu)
        return converter
    except Exception as e:
        st.error(f"❌ Failed to load AI model: {str(e)} / AI 모델 로딩 실패: {str(e)}")
        st.info("💡 Try using a smaller model (tiny/base) or refresh the page / 더 작은 모델을 사용하거나 페이지를 새로고침해보세요")
        st.stop()

# 파일 업로드 처리 함수 / File Upload Processing Function
def process_file_upload(uploaded_file, selected_model, selected_language, use_gpu):
    """파일 업로드 처리 함수"""
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
            model_options_display = {
                "tiny": "🚀 Tiny (매우빠름, ⭐ 기본정확도) / Very Fast, Basic Accuracy",
                "base": "⚡ Base (빠름, ⭐⭐ 좋은정확도) / Fast, Good Accuracy", 
                "small": "🚶 Small (보통, ⭐⭐⭐ 더좋음) / Normal, Higher Accuracy",
                "medium": "🐌 Medium (느림, ⭐⭐⭐⭐ 높음) / Slow, High Accuracy",
                "large": "🐌🐌 Large (매우느림, ⭐⭐⭐⭐⭐ 최고) / Very Slow, Best Accuracy"
            }
            language_options_display = {
                "auto": "🌐 Auto Detect / 자동감지",
                "ko": "🇰🇷 Korean / 한국어",
                "en": "🇺🇸 English / 영어", 
                "ja": "🇯🇵 Japanese / 일본어",
                "zh": "🇨🇳 Chinese / 중국어",
                "es": "🇪🇸 Spanish / 스페인어",
                "fr": "🇫🇷 French / 프랑스어",
                "de": "🇩🇪 German / 독일어"
            }
            model_info = {
                "Selected Model": model_options_display[selected_model].split(' /')[0],
                "Language": language_options_display[selected_language].split(' /')[0]
            }
            st.json(model_info)
        
        # 변환 버튼 / Convert Button
        if st.button("🚀 Convert to Text / 텍스트 변환", type="primary", use_container_width=True):
            
            # 간단한 퍼센트 표시만
            progress_container = st.container()
            
            with progress_container:
                # 퍼센트 표시만
                progress_percent = st.empty()
                
                # 상태 텍스트와 단계별 진행 표시
                status_text = st.empty()
                progress_steps = st.empty()
            
            def update_progress_gui_style(value, step_message=""):
                """간단한 퍼센트만 표시 (파일 업로드용)"""
                progress_percent.text(f"{value}%")
                if step_message:
                    progress_steps.markdown(f"**• {step_message}**")
                else:
                    status_text.text("")  # 기존 상태 메시지 지우기
            
            try:
                # Step 1/6: 파일 정보 읽기 (5%)
                update_progress_gui_style(5, "📹 Step 1/6: Reading video information / 영상 정보 읽는중...")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_file_path = tmp_file.name
                
                # Step 1/6: 완료 (10%)
                update_progress_gui_style(10, "✅ Step 1/6: Video info loaded / 영상 정보 로딩 완료")
                
                # Step 2/6: AI 모델 로딩 (15%)
                update_progress_gui_style(15, "🤖 Step 2/6: Loading AI model / AI 모델 로딩중...")
                
                use_gpu = torch.cuda.is_available()
                converter = load_video_converter(selected_model, use_gpu)
                
                # Step 2/6: 완료 (25%)
                update_progress_gui_style(25, "✅ Step 2/6: AI model loaded / AI 모델 로딩 완료")
                
                # Step 3/6: 오디오 추출 준비 (30%)
                update_progress_gui_style(30, "⚙️ Step 3/6: Preparing audio extraction / 오디오 추출 준비중...")
                
                # 언어 설정
                language = None if selected_language == "auto" else selected_language
                
                # 간단한 GUI 스타일 진행률 콜백 함수 (파일 업로드용)
                def progress_callback(value, message="", **kwargs):
                    # 복잡한 기술 정보는 무시하고 단계별 메시지만 표시
                    if value >= 40 and value < 60:
                        step_msg = "🎵 Step 4/6: Extracting audio from video / 비디오에서 오디오 추출중..."
                    elif value == 60:
                        step_msg = "✅ Step 4/6: Audio extraction completed / 오디오 추출 완료"
                    elif value >= 65 and value < 85:
                        step_msg = "🔄 Step 5/6: Starting AI transcription / AI 텍스트 변환 시작..."
                    elif value == 85:
                        step_msg = "✅ Step 5/6: Transcription completed / 텍스트 변환 완료"
                    elif value >= 90:
                        step_msg = "📝 Step 6/6: Finalizing results / 결과 정리중..."
                    else:
                        step_msg = ""
                    
                    # 간단한 진행률만 표시 (기술적 세부사항은 무시)
                    update_progress_gui_style(min(value, 95), step_msg)
                
                # 변환 실행
                result = converter.process_local_video_with_info(
                    temp_file_path, 
                    language=language, 
                    save_transcript=False,
                    progress_callback=progress_callback
                )
                
                # Step 6/6: 완료 (100%)
                update_progress_gui_style(100, "🎉 Step 6/6: All completed! / 모든 단계 완료!")
                
                # 결과 표시
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
                update_progress_gui_style(0, "❌ Conversion failed / 변환 실패")
                
                # 임시 파일 정리 / Clean up temporary files
                try:
                    if 'temp_file_path' in locals():
                        os.unlink(temp_file_path)
                except:
                    pass

# YouTube 비디오 처리 함수 / YouTube Video Processing Function
def process_youtube_video(youtube_url, model_size, language, use_gpu):
    """YouTube 비디오를 처리하고 결과를 표시합니다 (간단한 진행률 표시)"""
    
    # 간단한 퍼센트 표시만
    progress_container = st.container()
    
    with progress_container:
        # 퍼센트 표시만
        progress_percent = st.empty()
        
        # 상태 텍스트와 단계별 진행 표시
        status_text = st.empty()
        progress_steps = st.empty()
    
    def update_progress_gui_style(value, step_message=""):
        """간단한 퍼센트만 표시"""
        progress_percent.text(f"{value}%")
        
        if step_message:
            progress_steps.markdown(f"**• {step_message}**")
        else:
            status_text.text("")  # 기존 상태 메시지 지우기
    
    try:
        # Step 1/6: 초기화 (5%)
        update_progress_gui_style(5, "📹 Step 1/6: Reading video information / 영상 정보 읽는중...")
        
        # 변환기 로딩
        converter = load_video_converter(model_size, use_gpu)
        
        # URL 검증
        if not converter.is_youtube_url(youtube_url):
            st.error("❌ Invalid YouTube URL / 유효하지 않은 YouTube URL입니다")
            return
        
        # Step 1/6: 완료 (10%)
        update_progress_gui_style(10, "✅ Step 1/6: Video info loaded / 영상 정보 로딩 완료")
        
        # Step 2/6: AI 모델 로딩 (15%)
        update_progress_gui_style(15, "🤖 Step 2/6: Loading AI model / AI 모델 로딩중...")
        
        # YouTube 정보 가져오기
        youtube_info = converter.get_youtube_info(youtube_url)
        if not youtube_info:
            st.error("❌ Failed to get YouTube video information / YouTube 영상 정보를 가져올 수 없습니다")
            return
        
        # Step 2/6: 완료 (25%)
        update_progress_gui_style(25, "✅ Step 2/6: AI model loaded / AI 모델 로딩 완료")
        
        # 영상 정보 표시 (GUI와 동일한 형식)
        with st.expander("📺 YouTube Video Information / 유튜브 영상 정보", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title / 제목:** {youtube_info['title']}")
                st.write(f"**Uploader / 업로더:** {youtube_info['uploader']}")
            with col2:
                # Duration 포맷팅 (GUI와 동일)
                if youtube_info['duration']:
                    duration_seconds = int(youtube_info['duration'])
                    hours = duration_seconds // 3600
                    minutes = (duration_seconds % 3600) // 60
                    seconds = duration_seconds % 60
                    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    duration_str = "--:--:--"
                st.write(f"**Duration / 재생시간:** {duration_str}")
                st.write(f"**Views / 조회수:** {youtube_info.get('view_count', 'Unknown'):,}" if isinstance(youtube_info.get('view_count'), int) else f"**Views / 조회수:** Unknown")
        
        # Step 3/6: 오디오 추출 준비 (30%)
        update_progress_gui_style(30, "⚙️ Step 3/6: Preparing audio extraction / 오디오 추출 준비중...")
        
        # 언어 설정
        lang = None if language == "auto" else language
        
        # 간단한 GUI 스타일 진행률 콜백 함수 (YouTube용)
        def progress_callback(value, message="", **kwargs):
            # 복잡한 기술 정보는 무시하고 단계별 메시지만 표시
            if value >= 10 and value < 50:
                step_msg = "📥 Step 4/6: Downloading video / 비디오 다운로드중..."
            elif value == 50:
                step_msg = "✅ Step 4/6: Download completed / 다운로드 완료"
            elif value >= 55 and value < 65:
                step_msg = "🎵 Step 5/6: Extracting audio / 오디오 추출중..."
            elif value >= 65 and value < 85:
                step_msg = "🤖 Step 6/6: AI transcription in progress / AI 텍스트 변환 진행중..."
            elif value == 85:
                step_msg = "✅ Step 6/6: Transcription completed / 텍스트 변환 완료"
            elif value >= 90:
                step_msg = "📝 Finalizing results / 결과 정리중..."
            else:
                step_msg = ""
            
            # 간단한 진행률만 표시 (기술적 세부사항은 무시)
            update_progress_gui_style(min(value, 95), step_msg)
        
        # YouTube 비디오 처리
        result = converter.process_youtube_video(
            youtube_url,
            language=lang,
            save_transcript=False,
            progress_callback=progress_callback
        )
        
        # Step 6/6: 완료 (100%)
        update_progress_gui_style(100, "🎉 Step 6/6: All completed! / 모든 단계 완료!")
        
        # 결과 표시
        st.success("🎉 YouTube transcription completed successfully! / YouTube 텍스트 변환이 성공적으로 완료되었습니다!")
        
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
            
            # 파일명 생성 (YouTube 제목 기반)
            safe_title = "".join(c for c in youtube_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
            filename = f"{safe_title}_transcript.txt" if safe_title else "youtube_transcript.txt"
            
            # 다운로드 버튼 / Download Button
            st.download_button(
                label="📥 Download Text File / 텍스트 파일 다운로드",
                data=edited_text,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.warning("⚠️ No speech detected in the video. Please check if the video contains audio. / 영상에서 음성이 감지되지 않았습니다. 영상에 오디오가 포함되어 있는지 확인해주세요.")
        
    except Exception as e:
        st.error(f"❌ Error occurred: {str(e)} / 오류가 발생했습니다: {str(e)}")
        
        # 상세 에러 정보 표시
        with st.expander("🔍 Error Details / 에러 상세 정보"):
            st.text(f"Error Type: {type(e).__name__}")
            st.text(f"Error Message: {str(e)}")
            st.code(traceback.format_exc())
        
        # 진행률 리셋
        try:
            update_progress_gui_style(0, "❌ Conversion failed / 변환 실패")
        except:
            pass

# 사이드바 설정 / Sidebar Configuration  
with st.sidebar:
    # 사이드바 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="background: linear-gradient(135deg, #667eea, #764ba2); 
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent; 
                   background-clip: text; 
                   font-size: 2rem; 
                   font-weight: 700; 
                   margin: 0;">
            ⚙️ Settings
        </h2>
        <p style="color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            Customize your experience / 설정 조정
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 환경 정보 카드들
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.05)); 
                border-radius: 12px; 
                padding: 1rem; 
                margin-bottom: 1rem; 
                border: 1px solid rgba(102,126,234,0.2);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 0.9rem; display: flex; align-items: center;">
            <span style="margin-right: 0.5rem;">🌍</span> Environment
        </h4>
        <p style="margin: 0; color: #6c757d; font-size: 0.8rem;">
            {ENV_CONFIG['environment']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(255,165,0,0.05)); 
                border-radius: 12px; 
                padding: 1rem; 
                margin-bottom: 1rem; 
                border: 1px solid rgba(255,107,107,0.2);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4 style="color: #ff6b6b; margin: 0 0 0.5rem 0; font-size: 0.9rem; display: flex; align-items: center;">
            <span style="margin-right: 0.5rem;">📁</span> Max File Size
        </h4>
        <p style="margin: 0; color: #6c757d; font-size: 0.8rem;">
            {ENV_CONFIG['max_file_display']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(40,167,69,0.1), rgba(32,201,151,0.05)); 
                border-radius: 12px; 
                padding: 1rem; 
                margin-bottom: 1.5rem; 
                border: 1px solid rgba(40,167,69,0.2);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h4 style="color: #28a745; margin: 0 0 0.5rem 0; font-size: 0.9rem; display: flex; align-items: center;">
            <span style="margin-right: 0.5rem;">📹</span> yt-dlp Version
        </h4>
        <p style="margin: 0; color: #6c757d; font-size: 0.8rem;">
            {YT_DLP_VERSION}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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
            help="Theme will be applied automatically / 테마가 자동으로 적용됩니다"
        )
        
        # 테마가 변경되면 자동으로 적용
        if selected_theme != st.session_state.current_theme:
            # 테마 적용
            if update_theme_config(selected_theme):
                st.session_state.current_theme = selected_theme
                st.success(f"✅ Theme applied: {theme_options[selected_theme].split(' /')[0]} / 테마 적용됨")
                
                # 효과 추가
                st.balloons()
                
                # 즉시 새로고침 (Streamlit 내장 기능 사용)
                try:
                    st.rerun()
                except (AttributeError, NameError):
                    try:
                        st.experimental_rerun()
                    except (AttributeError, NameError):
                        # 최후 수단: 페이지 새로고침
                        st.markdown("""
                        <script>
                        window.parent.location.reload();
                        </script>
                        """, unsafe_allow_html=True)
        else:
            st.success(f"✅ Current theme: {theme_options[st.session_state.current_theme].split(' /')[0]}")
    
    # 모델 선택 / Model Selection
    model_options = {
        "tiny": "🚀 Tiny (매우빠름, ⭐ 기본정확도) / Very Fast, Basic Accuracy",
        "base": "⚡ Base (빠름, ⭐⭐ 좋은정확도) / Fast, Good Accuracy", 
        "small": "🚶 Small (보통, ⭐⭐⭐ 더좋음) / Normal, Higher Accuracy",
        "medium": "🐌 Medium (느림, ⭐⭐⭐⭐ 높음) / Slow, High Accuracy",
        "large": "🐌🐌 Large (매우느림, ⭐⭐⭐⭐⭐ 최고) / Very Slow, Best Accuracy"
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
        "zh": "🇨🇳 Chinese / 중국어",
        "es": "🇪🇸 Spanish / 스페인어",
        "fr": "🇫🇷 French / 프랑스어",
        "de": "🇩🇪 German / 독일어"
    }
    
    selected_language = st.selectbox(
        "Language / 언어:",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x]
    )
    
    # GPU 설정 / GPU Settings
    st.markdown("---")
    
    # GPU 사용 가능 여부 표시
    if torch.cuda.is_available():
        gpu_available = True
        st.success("🚀 GPU Available / GPU 사용 가능")
        
        # GPU 사용 여부 선택
        use_gpu_option = st.checkbox("Use GPU / GPU 사용", value=True, 
                                   help="Enable GPU acceleration for faster processing / GPU 가속을 통한 빠른 처리")
        
    else:
        gpu_available = False
        st.info("💻 CPU Mode Only / CPU 모드만 사용 가능")
        st.caption("GPU가 감지되지 않았습니다 / No GPU detected")
        use_gpu_option = False
    
    # GPU 설정을 세션 상태에 저장
    if 'use_gpu_setting' not in st.session_state:
        st.session_state.use_gpu_setting = True
    
    # GPU 설정 적용
    st.session_state.use_gpu_setting = use_gpu_option if torch.cuda.is_available() else False

# 메인 페이지 헤더 / Main Page Header
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 4rem; margin-bottom: 0.5rem;">
        🎬 Video to Text Converter
    </h1>
    <p style="font-size: 1.3rem; color: #6c757d; margin-bottom: 2rem; font-weight: 300;">
        ✨ AI-powered video transcription service / AI 기반 비디오 텍스트 변환 서비스 ✨
    </p>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 2rem;">
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.5rem 1.5rem; border-radius: 25px; font-weight: 600; box-shadow: 0 4px 15px rgba(102,126,234,0.3);">
            🚀 Fast Processing
        </div>
        <div style="background: linear-gradient(135deg, #ff6b6b, #ffa500); color: white; padding: 0.5rem 1.5rem; border-radius: 25px; font-weight: 600; box-shadow: 0 4px 15px rgba(255,107,107,0.3);">
            🎯 High Accuracy  
        </div>
        <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 0.5rem 1.5rem; border-radius: 25px; font-weight: 600; box-shadow: 0 4px 15px rgba(40,167,69,0.3);">
            🆓 Free Service
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 환경별 안내 메시지 카드
if ENV_CONFIG['environment'] == "☁️ Cloud Environment":
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.05)); 
                border-left: 5px solid #667eea; 
                border-radius: 15px; 
                padding: 1.5rem; 
                margin: 2rem 0; 
                box-shadow: 0 4px 15px rgba(102,126,234,0.1);
                backdrop-filter: blur(10px);">
        <h4 style="color: #667eea; margin: 0 0 0.5rem 0; display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">☁️</span>
            Cloud Demo Version
        </h4>
        <p style="margin: 0; color: #6c757d; font-size: 1.1rem;">
            <strong>파일이 200MB보다 크신가요?</strong><br>
            <span style="color: #999;">👇 아래 버튼으로 컴퓨터용(무제한) 버전을 받으세요!</span>
        </p>
        <div style="margin-top: 1.5rem; background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <h4 style="color: #28a745; margin: 0; font-size: 1.2rem;">
                    🏠 컴퓨터용 버전 (무료)
                </h4>
                <p style="margin: 0.5rem 0; color: #6c757d; font-size: 0.9rem;">
                    ✅ 파일 크기 무제한 &nbsp; ✅ 더 빠른 속도 &nbsp; ✅ 개인정보 안전
                </p>
            </div>
            <div style="text-align: center;">
                <a href="https://github.com/your-repo/YouTube_VideoToText/releases/latest/download/VideoToText.exe" 
                   style="background: linear-gradient(135deg, #28a745, #20c997); 
                          color: white; 
                          text-decoration: none; 
                          padding: 1rem 2rem; 
                          border-radius: 25px; 
                          font-weight: 700;
                          font-size: 1.1rem;
                          display: inline-block;
                          margin: 0.5rem;
                          box-shadow: 0 4px 15px rgba(40,167,69,0.3);">
                    💻 컴퓨터용 다운로드 (간단!)
                </a>
                <br>
                <small style="color: #999; font-size: 0.8rem;">
                    다운로드 후 파일을 더블클릭하면 자동 실행됩니다
                </small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(40,167,69,0.1), rgba(40,167,69,0.05)); 
                border-left: 5px solid #28a745; 
                border-radius: 15px; 
                padding: 1.5rem; 
                margin: 2rem 0; 
                box-shadow: 0 4px 15px rgba(40,167,69,0.1);
                backdrop-filter: blur(10px);">
        <h4 style="color: #28a745; margin: 0 0 0.5rem 0; display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">🏠</span>
            Local Production Version
        </h4>
        <p style="margin: 0; color: #6c757d; font-size: 1.1rem;">
            Full features with GPU acceleration up to 2GB<br>
            <span style="color: #999;">GPU 가속을 포함한 모든 기능, 최대 2GB 지원</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

# 입력 방식 선택 탭 / Input Method Selection Tabs
tab1, tab2 = st.tabs(["📁 Upload Video File / 비디오 파일 업로드", "🎬 YouTube URL / 유튜브 링크"])

with tab1:
    # 파일 업로드 / File Upload
    uploaded_file = st.file_uploader(
        "Choose a video or audio file / 비디오 또는 오디오 파일을 선택하세요",
        type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'mp3', 'wav', 'm4a', 'aac'],
        help=f"Maximum file size: {ENV_CONFIG['max_file_display']} / 최대 파일 크기: {ENV_CONFIG['max_file_display']}"
    )
    
    process_file_upload(uploaded_file, selected_model, selected_language, st.session_state.get('use_gpu_setting', False))

with tab2:
    # YouTube URL 입력 / YouTube URL Input
    st.markdown("### 🎬 YouTube Video to Text / 유튜브 영상을 텍스트로")
    
    # 클라우드 환경에서 yt-dlp 상태 확인
    if ENV_CONFIG['environment'] == "☁️ Cloud Environment" and YT_DLP_VERSION == "Not installed":
        # 클라우드에서 yt-dlp 없음 - 경고 표시
        st.error("""
        ⚠️ **YouTube 기능 현재 불가** 
        
        클라우드 버전에서는 YouTube 다운로드가 제한됩니다.
        
        **해결 방법:**
        1. 📁 **파일 업로드** 탭 사용 (권장)
        2. 💻 **컴퓨터용 버전** 다운로드 (무제한 YouTube 지원)
        """)
        
        # 컴퓨터용 버전 다운로드 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; margin: 1rem 0;">
                <a href="https://github.com/your-repo/YouTube_VideoToText/releases/latest/download/VideoToText.exe" 
                   style="background: linear-gradient(135deg, #28a745, #20c997); 
                          color: white; 
                          text-decoration: none; 
                          padding: 1rem 2rem; 
                          border-radius: 25px; 
                          font-weight: 700;
                          font-size: 1.1rem;
                          display: inline-block;
                          box-shadow: 0 4px 15px rgba(40,167,69,0.3);">
                    💻 컴퓨터용 다운로드 (YouTube 지원)
                </a>
            </div>
            """, unsafe_allow_html=True)
    else:
        # YouTube 기능 설명 (정상 작동 시)
        st.info(f"""
        🎬 **YouTube Video Support / YouTube 영상 지원** (yt-dlp v{YT_DLP_VERSION})
        
        ✅ Extract text directly from YouTube videos
        ✅ YouTube 영상에서 직접 텍스트 추출
        
        **Supported formats / 지원 형식:**
        - Standard YouTube videos / 일반 YouTube 영상
        - Educational content / 교육용 콘텐츠  
        - Tutorial videos / 튜토리얼 영상
        
        **Tips for best results / 최상의 결과를 위한 팁:**
        - Use public, accessible videos / 공개된, 접근 가능한 영상 사용
        - Educational and tutorial content works best / 교육용과 튜토리얼 콘텐츠가 가장 잘 작동
        
        **Test URLs / 테스트 URL:**
        - `https://www.youtube.com/watch?v=jNQXAC9IVRw` (Me at the zoo)
        - `https://www.youtube.com/watch?v=dQw4w9WgXcQ` (Rick Roll)
        """)
    
    # 세션 상태 초기화
    if 'youtube_validated' not in st.session_state:
        st.session_state.youtube_validated = False
    if 'youtube_info' not in st.session_state:
        st.session_state.youtube_info = None
    if 'youtube_url' not in st.session_state:
        st.session_state.youtube_url = ""
    
    youtube_url = st.text_input(
        "YouTube URL / 유튜브 링크:",
        value=st.session_state.youtube_url,
        placeholder="https://www.youtube.com/watch?v=...",
        help="Enter a YouTube video URL / YouTube 비디오 URL을 입력하세요"
    )
    
    # URL이 변경되면 검증 상태 리셋
    if youtube_url != st.session_state.youtube_url:
        st.session_state.youtube_url = youtube_url
        st.session_state.youtube_validated = False
        st.session_state.youtube_info = None
    
    if youtube_url:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            validate_clicked = st.button("🔍 Validate / 검증", use_container_width=True)
        
        # 검증 버튼 클릭 처리
        if validate_clicked:
            converter_temp = load_video_converter("base", False)
            if converter_temp.is_youtube_url(youtube_url):
                try:
                    with st.spinner("Getting video info... / 영상 정보 가져오는 중..."):
                        info = converter_temp.get_youtube_info(youtube_url)
                    if info:
                        # 세션 상태에 정보 저장
                        st.session_state.youtube_validated = True
                        st.session_state.youtube_info = info
                        st.session_state.youtube_url = youtube_url
                    else:
                        st.error("❌ Failed to get video information / 영상 정보를 가져올 수 없습니다")
                        st.session_state.youtube_validated = False
                        st.session_state.youtube_info = None
                except Exception as e:
                    error_msg = str(e)
                    st.session_state.youtube_validated = False
                    st.session_state.youtube_info = None
                    
                    if "Video unavailable" in error_msg:
                        st.error("❌ **Video unavailable** / 영상을 사용할 수 없습니다")
                        st.info("💡 Try one of the test URLs above / 위의 테스트 URL을 시도해보세요")
                    elif "HTTP Error 403" in error_msg:
                        st.error("❌ **Access forbidden** / 접근이 금지되었습니다")
                        st.info("💡 This video may be region-blocked / 이 영상은 지역 차단되었을 수 있습니다")
                    else:
                        st.error(f"❌ Error: {error_msg}")
                        st.info("💡 Try a different YouTube URL / 다른 YouTube URL을 시도해보세요")
            else:
                st.error("❌ Invalid YouTube URL format / 유효하지 않은 YouTube URL 형식입니다")
                st.session_state.youtube_validated = False
                st.session_state.youtube_info = None
        
        # 검증된 정보 표시
        if st.session_state.youtube_validated and st.session_state.youtube_info:
            info = st.session_state.youtube_info
            duration_str = f"{int(info['duration']//60)}:{int(info['duration']%60):02d}" if info['duration'] else "Unknown"
            
            st.success(f"✅ **Valid Video Found:**\n\n**Title:** {info['title']}\n\n**Duration:** {duration_str}\n\n**Uploader:** {info['uploader']}")
            
            # 처리 버튼 - 항상 표시
            if st.button("🚀 **Extract Text from YouTube / 유튜브에서 텍스트 추출**", type="primary", use_container_width=True):
                # GPU 설정 가져오기
                current_use_gpu = st.session_state.get('use_gpu_setting', torch.cuda.is_available())
                
                # 디버깅 정보 표시 (숨김)
                # st.info(f"🔧 Processing with: Model={selected_model}, Language={selected_language}, GPU={current_use_gpu}")
                
                try:
                    process_youtube_video(st.session_state.youtube_url, selected_model, selected_language, current_use_gpu)
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
                    st.exception(e)
        
        elif youtube_url and youtube_url.strip() and not st.session_state.youtube_validated:
            st.info("👆 Click 'Validate' to check the YouTube URL / 'Validate' 버튼을 클릭하여 YouTube URL을 확인하세요")



# 사용법 안내 / Usage Instructions
with st.expander("📖 사용법이 궁금하세요? (클릭해서 보기)"):
    st.markdown(f"""
    ## 🎬 비디오를 텍스트로 바꾸는 방법 (매우 쉬움!)
    
    ### 📁 방법 1: 파일 업로드
    ```
    1. 👆 "파일 업로드" 탭 클릭
    2. 📁 "Browse files" 버튼 클릭 
    3. 💾 컴퓨터에서 동영상 파일 선택
    4. 🚀 "텍스트 변환" 버튼 클릭
    5. ⏰ 잠깐 기다리기 (몇 분)
    6. 📥 "다운로드" 버튼으로 텍스트 파일 저장
    ```
    
    ### 🎬 방법 2: 유튜브 링크  
    ```
    1. 👆 "유튜브 링크" 탭 클릭
    2. 🔗 유튜브 주소 복사해서 붙여넣기
    3. 🔍 "검증" 버튼 클릭 
    4. 🚀 "텍스트 추출" 버튼 클릭
    5. ⏰ 잠깐 기다리기 (몇 분)
    6. 📥 "다운로드" 버튼으로 텍스트 파일 저장
    ```
    
    ## 🤔 어떤 파일이 가능한가요?
    **동영상**: MP4, AVI, MOV, MKV 등  
    **음성**: MP3, WAV, M4A 등  
    **유튜브**: 모든 공개 영상
    
    ## ⚠️ 파일이 너무 크면?
    - **현재 환경**: {ENV_CONFIG['environment']}
    - **최대 크기**: {ENV_CONFIG['max_file_display']}
    - **더 큰 파일**: 위의 "컴퓨터용 다운로드" 버튼 클릭!
    
    ## 💡 꿀팁
    - **빠른 처리**: tiny 모델 선택
    - **정확한 결과**: small 모델 선택  
    - **언어**: 잘 모르겠으면 "자동감지" 그대로 두세요
    - **문제 발생**: 페이지 새로고침(F5) 해보세요
    """)

# 푸터 / Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🤖 Powered by**")
    st.caption("OpenAI Whisper & Streamlit")

with col2:
    st.markdown("**🎬 Video to Text Converter**")
    st.caption("v1.0 - Free Service")

with col3:
    st.markdown(f"**🌐 Environment**")
    st.caption(f"{ENV_CONFIG['environment']} - {ENV_CONFIG['max_file_display']}")

st.markdown(
    """
    <div style='text-align: center; margin-top: 2rem; color: #6c757d;'>
        Made with ❤️ for seamless video transcription experience<br>
        <small>원활한 비디오 텍스트 변환 경험을 위해 제작되었습니다</small>
    </div>
    """, 
    unsafe_allow_html=True
) 