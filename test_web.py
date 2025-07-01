import streamlit as st

# 간단한 테스트 페이지 / Simple test page
st.set_page_config(
    page_title="🧪 Test Page",
    page_icon="🧪"
)

st.title("🧪 Streamlit Test Page")
st.write("If you can see this message, Streamlit is working! / 이 메시지가 보이면 Streamlit이 작동합니다!")

# 라이브러리 테스트 / Library Testing
st.subheader("📚 Library Test / 라이브러리 테스트")

try:
    import torch
    st.success("✅ PyTorch: OK")
    st.write(f"PyTorch version: {torch.__version__}")
    if torch.cuda.is_available():
        st.success(f"🚀 CUDA Available: {torch.cuda.get_device_name(0)}")
    else:
        st.info("💻 CUDA not available, using CPU")
except ImportError as e:
    st.error(f"❌ PyTorch: {e}")

try:
    import whisper
    st.success("✅ Whisper: OK")
except ImportError as e:
    st.error(f"❌ Whisper: {e}")

try:
    from moviepy.editor import VideoFileClip
    st.success("✅ MoviePy: OK")
except ImportError as e:
    st.error(f"❌ MoviePy: {e}")

try:
    import numpy
    st.success(f"✅ NumPy: OK ({numpy.__version__})")
except ImportError as e:
    st.error(f"❌ NumPy: {e}")

try:
    import scipy
    st.success(f"✅ SciPy: OK ({scipy.__version__})")
except ImportError as e:
    st.error(f"❌ SciPy: {e}")

try:
    import librosa
    st.success(f"✅ Librosa: OK ({librosa.__version__})")
except ImportError as e:
    st.error(f"❌ Librosa: {e}")

# 파일 업로드 테스트 / File upload test
st.subheader("📁 File Upload Test / 파일 업로드 테스트")
uploaded_file = st.file_uploader("Test file upload", type=['txt', 'mp4', 'avi'])
if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")

# 버튼 테스트 / Button test
if st.button("🔵 Test Button / 테스트 버튼"):
    st.balloons()
    st.success("Button clicked! / 버튼이 클릭되었습니다!")

st.markdown("---")
st.write("If all tests pass, the main app should work! / 모든 테스트가 통과하면 메인 앱이 작동할 것입니다!") 