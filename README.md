# Local Media Viewer

로컬 영상들을 관리하고 볼 수 있는 웹 애플리케이션입니다.

## 프로젝트 구조

```
app/
├── __init__.py
├── main.py              # FastAPI 애플리케이션
├── database.py          # DB 연결 및 모델
├── models/             # 데이터 모델
│   ├── __init__.py
│   └── video.py
├── services/           # 비즈니스 로직
│   ├── __init__.py
│   └── video.py
└── api/               # API 라우터
    ├── __init__.py
    └── videos.py
```

## 개발 환경 설정

### 0. 설정 파일

프로젝트 루트 디렉토리에 `config.yaml` 파일을 생성하고 다음과 같이 설정합니다:

```yaml
# 비디오 파일이 있는 디렉토리 목록
video_directories:
  - "D:/Videos"  # 실제 비디오가 있는 경로로 수정해주세요

# 썸네일 저장 경로
thumbnail_dir: "thumbnails"
```

### 1. Python 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows (Command Prompt)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. 필요한 패키지 설치

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 설치
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python -m uvicorn app.main:app --reload
```

## API 엔드포인트

서버가 실행되면 다음 URL로 접속할 수 있습니다:
- API 문서: http://localhost:8000/docs
- 비디오 스캔 API: http://localhost:8000/api/videos/scan
- 비디오 목록 API: http://localhost:8000/api/videos/list
