# Local Video Manager

로컬 비디오 파일들을 관리하고 태그를 붙일 수 있는 웹 애플리케이션입니다.

## 주요 기능

### 1. 비디오 스캔 및 관리
- 설정된 디렉토리에서 비디오 파일들을 자동으로 스캔
- 지원 포맷: mp4, avi, mkv, mov
- 비디오 메타데이터(길이, 생성일 등) 자동 추출
- 썸네일 자동 생성
- 컨테이너 모드에서 호스트 경로 매핑

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
- 컨테이너 모드 설정
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

### Infrastructure
- Docker
- Nginx
- Socket 통신

## 실행 방법

### 1. 컨테이너 모드로 실행

1. 설정 파일 준비:
```bash
# config/config.container.yaml 파일 생성
cp config/config.yaml.example config/config.container.yaml
# 설정 파일 수정
```

2. Docker Compose로 실행:
```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

3. 플레이어 모니터 실행:
```bash
# Windows
start_player.cmd

# Linux/macOS
cd player
python monitor.py --config config.yaml
```

### 2. 로컬 모드로 실행

1. 백엔드 실행:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main --config ./config/config.local.yaml
```

2. 프론트엔드 실행:
```bash
cd frontend
npm install
npm start
```

브라우저에서 http://localhost:3000 으로 접속하면 됩니다.

> 참고: 로컬 모드에서는 백엔드가 직접 시스템의 기본 비디오 플레이어를 실행하므로 별도의 플레이어 모니터가 필요하지 않습니다.

## 설정 파일 구조

### Backend 설정
```yaml
# 비디오 파일이 있는 디렉토리 목록
video_directories:
  - "/videos/data"
  - "/videos/marvel"

# DB 설정
database:
  path: "/videos/data/videos.db"

# 썸네일 설정
thumbnails:
  directory: "/videos/data/thumbnails"
  extension: ".webp"
  duration: 3.0
  fps: 5.0
  max_size: 480
  max_workers: 6

# 컨테이너 모드 설정
container:
  mode: true
  player_host: "localhost"
  player_port: 9990
```

### Player 설정
```yaml
host: "localhost"
port: 9990
```

## 브라우저 접속

- 컨테이너 모드: http://localhost:3000
- 로컬 모드: http://localhost:3000

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