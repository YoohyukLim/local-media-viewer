# 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 애플리케이션
│   ├── config.py         # 설정 관리
│   ├── database.py       # DB 연결 및 모델
│   ├── models/          # 데이터 모델
│   │   ├── __init__.py
│   │   ├── video.py
│   │   └── tag.py
│   ├── services/        # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── scanner.py
│   │   ├── thumbnail.py
│   │   ├── thumbnail_worker.py
│   │   └── metadata.py
│   └── api/            # API 라우터
│       ├── __init__.py
│       └── videos.py
├── config/            # 설정 파일 디렉토리
│   └── config.yaml
└── requirements.txt

frontend/
├── src/
│   ├── components/    # React 컴포넌트
│   ├── types/        # TypeScript 타입 정의
│   ├── services/     # API 통신
│   └── styles/       # 스타일 정의
└── package.json
``` 