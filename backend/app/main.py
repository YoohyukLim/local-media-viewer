import signal
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import argparse
from .config import Settings

# 전역 설정 초기화
settings = None

def init_settings(config_path: str | None = None):
    """전역 설정을 초기화합니다."""
    global settings
    settings = Settings(config_path)
    # settings를 다른 모듈에서 참조할 수 있도록 config.py에도 설정
    from . import config
    config.settings = settings

# 시작할 때 바로 설정 초기화
if settings is None:
    init_settings()

# settings 초기화 후에 다른 모듈 import
from .database import engine, Base, get_db
from .api import videos
from .services.scanner import scan_videos
from .services.thumbnail_worker import shutdown_thumbnail_worker
from .logger import logger, shutdown_logger

logger = logging.getLogger(__name__)

# 종료 플래그
should_exit = False

def signal_handler(signum, frame):
    """시그널 핸들러"""
    global should_exit
    if not should_exit:
        logger.info("Received shutdown signal, cleaning up...")
        should_exit = True
        
        try:
            # 리소스 정리
            shutdown_thumbnail_worker()
        except Exception as e:
            logger.error(f"Error during thumbnail worker shutdown: {e}")
            
        try:
            shutdown_logger()
        except Exception as e:
            print(f"Error during logger shutdown: {e}")
        
        sys.exit(0)

def setup_signal_handlers():
    """시그널 핸들러 설정"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    서버 시작/종료 시 실행되는 이벤트 핸들러
    """
    try:
        db = next(get_db())
        scan_videos(db)
        logger.info("Initial video scan completed")
    except Exception as e:
        logger.error(f"Error during initial video scan: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        db.close()
    
    yield  # 서버 실행 중
    
    # 종료 시 실행
    logger.info("Shutting down...")
    shutdown_thumbnail_worker()  # 썸네일 워커 종료
    shutdown_logger()  # 로그 리스너 종료

app = FastAPI(
    title="Video Manager",
    lifespan=lifespan
)

# CORS 미들웨어 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Video Manager"}

def start_server(host: str = "localhost", port: int = 8000, config_path: str | None = None):
    """서버를 시작합니다."""
    # 설정 초기화
    init_settings(config_path)
    
    setup_signal_handlers()
    
    # uvicorn 설정
    config = uvicorn.Config(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        reload_includes=["*.py", "*.yaml"],  # 설정 파일 변경 감지
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, initiating shutdown...")
        signal_handler(signal.SIGINT, None)  # 종료 핸들러 호출

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video Manager Server")
    parser.add_argument("--host", default="localhost", help="서버 호스트 주소")
    parser.add_argument("--port", type=int, default=8000, help="서버 포트 번호")
    parser.add_argument("--config", help="설정 파일 경로")
    
    args = parser.parse_args()
    start_server(args.host, args.port, args.config) 