import streamlit as st
import tempfile
import os
import torch
import traceback
import whisper

# 모듈 임포트
from src.ffmpeg_setup import setup_ffmpeg_path
from src.converter import VideoToTextConverter

# FFmpeg 경로 설정 실행
setup_ffmpeg_path()

# yt-dlp 버전 확인을 위한 임포트
try:
    import yt_dlp
    YT_DLP_VERSION = yt_dlp.version.__version__
except ImportError:
    YT_DLP_VERSION = "Not installed"

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

# GPU 사용 가능 여부 확인 / Check GPU availability
use_gpu = torch.cuda.is_available()

# 캐시된 변환기 로딩 / Load Cached Converter
@st.cache_resource
def load_video_converter(model_name, use_gpu=True):
    return VideoToTextConverter(model_size=model_name, use_gpu=use_gpu)

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
            
            # GUI 스타일 진행률 컨테이너
            progress_container = st.container()
            
            with progress_container:
                # 진행률 바와 퍼센트 표시
                col1, col2 = st.columns([4, 1])
                with col1:
                    progress_bar = st.progress(0)
                with col2:
                    progress_percent = st.empty()
                
                # 상태 텍스트와 단계별 진행 표시
                status_text = st.empty()
                progress_steps = st.empty()
            
            def update_progress_gui_style(value, step_message, status_message=""):
                """GUI 스타일 진행률 업데이트"""
                progress_bar.progress(value)
                progress_percent.text(f"{value}%")
                if status_message:
                    status_text.text(status_message)
                if step_message:
                    progress_steps.markdown(f"**• {step_message}**")
            
            try:
                # Step 1/6: 파일 정보 읽기 (5%)
                update_progress_gui_style(5,
                    "📹 Step 1/6: Reading video information / 영상 정보 읽는중...",
                    "📁 Saving uploaded file... / 업로드된 파일 저장 중...")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_file_path = tmp_file.name
                
                # Step 1/6: 완료 (10%)
                update_progress_gui_style(10,
                    "✅ Step 1/6: Video info loaded / 영상 정보 로딩 완료")
                
                # Step 2/6: AI 모델 로딩 (15%)
                update_progress_gui_style(15,
                    "🤖 Step 2/6: Loading AI model / AI 모델 로딩중...",
                    f"🤖 Loading {selected_model} model... / {selected_model} 모델 로딩 중...")
                
                use_gpu = torch.cuda.is_available()
                converter = load_video_converter(selected_model, use_gpu)
                
                # Step 2/6: 완료 (25%)
                update_progress_gui_style(25,
                    "✅ Step 2/6: AI model loaded / AI 모델 로딩 완료")
                
                # Step 3/6: 오디오 추출 준비 (30%)
                update_progress_gui_style(30,
                    "⚙️ Step 3/6: Preparing audio extraction / 오디오 추출 준비중...")
                
                # 언어 설정
                language = None if selected_language == "auto" else selected_language
                
                # GUI 스타일 진행률 콜백 함수
                def progress_callback(value, message):
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
                    
                    update_progress_gui_style(min(value, 95), step_msg, message)
                
                # 변환 실행
                result = converter.process_local_video_with_info(
                    temp_file_path, 
                    language=language, 
                    save_transcript=False,
                    progress_callback=progress_callback
                )
                
                # Step 6/6: 완료 (100%)
                update_progress_gui_style(100,
                    "🎉 Step 6/6: All completed! / 모든 단계 완료!",
                    "✅ Conversion completed! / 변환 완료!")
                
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
                progress_bar.progress(0)
                status_text.text("❌ Conversion failed / 변환 실패")
                
                # 임시 파일 정리 / Clean up temporary files
                try:
                    if 'temp_file_path' in locals():
                        os.unlink(temp_file_path)
                except:
                    pass

# YouTube 비디오 처리 함수 / YouTube Video Processing Function
def process_youtube_video(youtube_url, model_size, language, use_gpu):
    """YouTube 비디오를 처리하고 결과를 표시합니다 (GUI 스타일 진행률 포함)"""
    
    # GUI 스타일 진행률 컨테이너
    progress_container = st.container()
    
    with progress_container:
        # 진행률 바와 퍼센트 표시
        col1, col2 = st.columns([4, 1])
        with col1:
            progress_bar = st.progress(0)
        with col2:
            progress_percent = st.empty()
        
        # 상태 텍스트와 단계별 진행 표시
        status_text = st.empty()
        progress_steps = st.empty()
    
    def update_progress_gui_style(value, step_message, status_message=""):
        """GUI 스타일 진행률 업데이트"""
        progress_bar.progress(value)
        progress_percent.text(f"{value}%")
        if status_message:
            status_text.text(status_message)
        if step_message:
            progress_steps.markdown(f"**• {step_message}**")
    
    try:
        # Step 1/6: 초기화 (5%)
        update_progress_gui_style(5, 
            "📹 Step 1/6: Reading video information / 영상 정보 읽는중...",
            "🔍 Validating YouTube URL... / YouTube URL 검증 중...")
        
        # 변환기 로딩
        converter = load_video_converter(model_size, use_gpu)
        
        # URL 검증
        if not converter.is_youtube_url(youtube_url):
            st.error("❌ Invalid YouTube URL / 유효하지 않은 YouTube URL입니다")
            return
        
        # Step 1/6: 완료 (10%)
        update_progress_gui_style(10, 
            "✅ Step 1/6: Video info loaded / 영상 정보 로딩 완료")
        
        # Step 2/6: AI 모델 로딩 (15%)
        update_progress_gui_style(15,
            "🤖 Step 2/6: Loading AI model / AI 모델 로딩중...",
            f"🤖 Loading {model_size} model... / {model_size} 모델 로딩 중...")
        
        # YouTube 정보 가져오기
        youtube_info = converter.get_youtube_info(youtube_url)
        if not youtube_info:
            st.error("❌ Failed to get YouTube video information / YouTube 영상 정보를 가져올 수 없습니다")
            return
        
        # Step 2/6: 완료 (25%)
        update_progress_gui_style(25,
            "✅ Step 2/6: AI model loaded / AI 모델 로딩 완료")
        
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
        update_progress_gui_style(30,
            "⚙️ Step 3/6: Preparing audio extraction / 오디오 추출 준비중...")
        
        # 언어 설정
        lang = None if language == "auto" else language
        
        # GUI 스타일 진행률 콜백 함수
        def progress_callback(value, message):
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
            
            update_progress_gui_style(min(value, 95), step_msg, message)
        
        # YouTube 비디오 처리
        result = converter.process_youtube_video(
            youtube_url,
            language=lang,
            save_transcript=False,
            progress_callback=progress_callback
        )
        
        # Step 6/6: 완료 (100%)
        update_progress_gui_style(100,
            "🎉 Step 6/6: All completed! / 모든 단계 완료!",
            "✅ Conversion completed! / 변환 완료!")
        
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
            progress_bar.progress(0)
            status_text.text("❌ Conversion failed / 변환 실패")
        except:
            pass

# 사이드바 설정 / Sidebar Configuration  
with st.sidebar:
    st.title("⚙️ Settings / 설정")
    
    # 환경 정보 표시
    st.info(f"🌍 Environment: {ENV_CONFIG['environment']}")
    st.info(f"📁 Max File Size: {ENV_CONFIG['max_file_display']}")
    st.info(f"📹 yt-dlp Version: {YT_DLP_VERSION}")
    
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

# 메인 페이지 / Main Page
st.title("🎬 Video to Text Converter")
st.markdown("### AI-powered video transcription service / AI 기반 비디오 텍스트 변환 서비스")

# 환경별 안내 메시지
if ENV_CONFIG['environment'] == "☁️ Cloud Environment":
    st.info("☁️ **Cloud Demo Version** - For larger files (>200MB), please use the local version / 큰 파일(200MB 초과)은 로컬 버전을 사용하세요")
else:
    st.success("🏠 **Local Production Version** - Full features with GPU acceleration up to 2GB / GPU 가속을 포함한 모든 기능, 최대 2GB 지원")

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
    
    # YouTube 기능 설명
    st.info("""
    🎬 **YouTube Video Support / YouTube 영상 지원**
    
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
                
                # 디버깅 정보 표시
                st.info(f"🔧 Processing with: Model={selected_model}, Language={selected_language}, GPU={current_use_gpu}")
                
                try:
                    process_youtube_video(st.session_state.youtube_url, selected_model, selected_language, current_use_gpu)
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
                    st.exception(e)
        
        elif youtube_url and youtube_url.strip() and not st.session_state.youtube_validated:
            st.info("👆 Click 'Validate' to check the YouTube URL / 'Validate' 버튼을 클릭하여 YouTube URL을 확인하세요")



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