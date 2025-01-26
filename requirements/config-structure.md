# 설정 파일 구조

## 설정 파일 위치
- backend/config/config.local.yaml (로컬 모드)
- backend/config/config.container.yaml (컨테이너 모드)
- player/config.yaml (플레이어 설정)

## Backend 설정

### 1. 비디오 디렉토리
```yaml
video_directories:
  - "/videos/data"
  - "/videos/marvel"
```

### 2. 데이터베이스 설정
```yaml
database:
  path: "/videos/data/videos.db"
```

### 3. 썸네일 설정
```yaml
thumbnails:
  directory: "/videos/data/thumbnails"
  extension: ".webp"
  duration: 3.0
  fps: 5.0
  max_size: 480
  max_workers: 6
```

### 4. 컨테이너 설정
```yaml
container:
  mode: true
  player_host: "localhost"
  player_port: 9990
```

## Player 설정
```yaml
host: "localhost"
port: 9990
```

## 커맨드라인 설정
```bash
python -m app.main --config /path/to/config.yaml
```

## 설정 우선순위
1. 커맨드라인 지정 설정 파일
2. backend/config/config.local.yaml
3. backend/config/config.container.yaml
4. player/config.yaml
5. 기본값 