# 설정 파일 구조

## 기본 설정 파일 위치
- backend/config/config.yaml

## 설정 항목

### 1. 비디오 디렉토리
```yaml
video_directories:
  - "D:/videos"
  - "E:/MOVIE/Marvel"
```

### 2. 데이터베이스 설정
```yaml
database:
  path: "D:/videos/videos.db"
```

### 3. 썸네일 설정
```yaml
thumbnails:
  directory: "D:/videos/thumbnails"
  extension: ".webp"
  duration: 3.0      # 썸네일 영상 길이 (초)
  fps: 5.0          # 초당 프레임 수
  max_size: 480     # 최대 크기 (px)
  max_workers: 6    # 썸네일 생성 워커 수
```

## 커맨드라인 설정
```bash
python -m app.main --config /path/to/config.yaml
```

## 설정 우선순위
1. 커맨드라인 지정 설정 파일
2. backend/config/config.yaml
3. 기본값 