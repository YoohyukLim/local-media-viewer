# Local Video Manager

로컬 비디오 파일들을 관리하고 태그를 붙일 수 있는 웹 애플리케이션입니다.

## 주요 기능

### 1. 비디오 스캔 및 관리
- 설정된 디렉토리에서 비디오 파일들을 자동으로 스캔
- 지원 포맷: mp4, avi, mkv, mov
- 비디오 메타데이터(길이, 생성일 등) 자동 추출
- 썸네일 자동 생성

### 2. 태그 시스템
- 비디오에 여러 태그 추가/삭제 가능
- 태그 기반 검색 지원 (AND/OR 검색)
- 태그 정보는 info 파일에도 저장되어 DB 리셋 후에도 복구 가능

### 3. 썸네일 관리
- WebP 포맷으로 썸네일 자동 생성
- 비동기 워커를 통한 썸네일 생성으로 성능 최적화
- 썸네일 크기, FPS 등 설정 가능

### 4. 설정 시스템
- YAML 기반 설정 파일
- 비디오 디렉토리 목록
- 데이터베이스 위치
- 썸네일 설정 (디렉토리, 포맷, 크기 등)
- 커맨드라인에서 설정 파일 위치 지정 가능

## 기술 스택

### Backend
- FastAPI
- SQLAlchemy (SQLite)
- OpenCV (비디오 처리)
- YAML (설정 관리)

### Frontend
- React
- TypeScript
- Styled Components
- Tailwind CSS

## 설정 파일 구조

```yaml
# 비디오 파일이 있는 디렉토리 목록
video_directories:
  - "D:/videos"

# DB 설정
database:
  path: "D:/videos/videos.db"

# 썸네일 설정
thumbnails:
  directory: "D:/videos/thumbnails"
  extension: ".webp"
  duration: 3.0      # 썸네일 영상 길이 (초)
  fps: 5.0          # 초당 프레임 수
  max_size: 480     # 최대 크기 (px)
  max_workers: 6    # 썸네일 생성 워커 수
```

## 실행 방법

1. 백엔드 실행:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main --port 8000 --config ./config/config.yaml
```

2. 프론트엔드 실행:
```bash
cd frontend
nvm use 18.18.0
npm install
npm start
```

## 주요 구현 사항

1. 비디오 메타데이터
   - 파일 경로를 해시하여 고유한 썸네일 ID 생성
   - info 파일에 태그와 카테고리 정보 저장

2. 썸네일 시스템
   - 비동기 워커로 썸네일 생성 작업 처리
   - 썸네일 로딩 실패 시 대체 UI 표시

3. 데이터베이스
   - SQLite 사용으로 설치 없이 바로 사용 가능
   - 설정에서 DB 파일 위치 지정 가능

4. 프론트엔드
   - 반응형 디자인
   - 키보드 네비게이션 지원
   - 태그 관리 UI
   - 페이지네이션