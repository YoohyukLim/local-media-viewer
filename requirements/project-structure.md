# 프로젝트 구조

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI 애플리케이션
│   │   ├── config.py         # 설정 관리
│   │   ├── database.py       # DB 연결 및 모델
│   │   ├── models/          # 데이터 모델
│   │   ├── services/        # 비즈니스 로직
│   │   └── api/            # API 라우터
│   ├── config/            # 설정 파일 디렉토리
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── types/        # TypeScript 타입 정의
│   │   └── services/     # API 통신
│   ├── Dockerfile
│   └── nginx.conf
├── player/
│   ├── monitor.py        # 플레이어 모니터
│   └── config.yaml       # 플레이어 설정
├── docker-compose.yml
└── start_player.cmd      # 플레이어 실행 스크립트
``` 