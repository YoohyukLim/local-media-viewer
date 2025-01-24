# Local Media Viewer

로컬 비디오 파일들을 관리하고 태그 기반으로 검색할 수 있는 서버입니다.

## 설치 방법

1. Python 3.11 이상 설치
2. 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

## 설정

1. config.yaml 파일 생성:
```yaml
# 비디오 파일이 있는 디렉토리 목록
video_directories:
  - "D:/videos"  # 실제 비디오가 있는 경로로 수정

# 썸네일 설정
thumbnails:
  directory: "D:/videos/thumbnails"  # 썸네일이 저장될 절대 경로
  extension: ".jpg"  # 썸네일 파일 확장자
```

## 서버 실행

기본 설정(localhost:8000)으로 실행:
```bash
python -m app.main
```

특정 포트로 실행:
```bash
python -m app.main --port 8080
```

특정 호스트와 포트로 실행:
```bash
python -m app.main --host 0.0.0.0 --port 8080
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 기능

1. 비디오 관리
   - 설정된 디렉토리의 비디오 파일 자동 스캔
   - 메타데이터 추출 (길이, 썸네일)
   - 파일 변경 감지 및 자동 업데이트

2. 태그 관리
   - .info 파일을 통한 메타데이터 관리
   - 디렉토리 기반 자동 태그 생성
   - 태그 추가/제거 API

3. 검색
   - 태그 기반 비디오 검색
   - AND/OR 검색 지원
   - 페이징 지원

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
