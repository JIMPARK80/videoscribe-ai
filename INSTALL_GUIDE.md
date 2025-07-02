# 🎬 Video to Text Converter - 로컬 설치 가이드

## 📋 시스템 요구사항

- **Python 3.8 이상** (Python 3.9 권장)
- **4GB 이상 RAM** (AI 모델 로딩용)
- **2GB 이상 디스크 공간**
- **Windows 10/11** (현재 버전)

## 🚀 빠른 설치 (Windows)

### 방법 1: 원클릭 설치 (권장)

1. **[여기서 다운로드](https://github.com/your-repo/YouTube_VideoToText/archive/main.zip)**
2. **압축 해제**
3. **`install_and_run.bat` 더블클릭**
4. **완료!** 🎉

### 방법 2: 수동 설치

```bash
# 1. 저장소 다운로드
git clone https://github.com/your-repo/YouTube_VideoToText.git
cd YouTube_VideoToText

# 2. Python 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate

# 3. 의존성 설치
pip install -r config/requirements.txt

# 4. 실행
streamlit run streamlit_app.py
```

## 🌟 로컬 버전 장점

| 기능 | 클라우드 버전 | 로컬 버전 |
|------|-------------|----------|
| **파일 크기 제한** | 200MB | **2GB** |
| **처리 속도** | 보통 | **빠름 (GPU 가속)** |
| **프라이버시** | 업로드 필요 | **완전 로컬** |
| **오프라인 사용** | ❌ | **✅** |
| **테마 변경** | ❌ | **✅** |

## 🔧 문제 해결

### Python이 설치되지 않은 경우
1. **[Python 공식 사이트](https://python.org/downloads/)에서 다운로드**
2. **설치 시 "Add Python to PATH" 체크**
3. **재부팅 후 다시 시도**

### 의존성 설치 실패 시
```bash
# 최신 pip로 업데이트
python -m pip install --upgrade pip

# 캐시 클리어 후 재설치
pip cache purge
pip install -r config/requirements.txt --no-cache-dir
```

### GPU 가속 활성화
```bash
# NVIDIA GPU 있는 경우
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 💡 사용 팁

- **GPU 사용 시**: 처리 속도 3-5배 빠름
- **큰 파일**: 10GB 이상도 처리 가능
- **배치 처리**: 여러 파일 동시 변환 가능
- **오프라인**: 인터넷 연결 없이도 사용 가능

## 📞 지원

문제가 있으면 [GitHub Issues](https://github.com/your-repo/YouTube_VideoToText/issues)에 문의하세요! 