import signal
import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine, Base, get_db
from .api import videos
from .services.scanner import scan_videos
from .services.thumbnail_worker import shutdown_thumbnail_worker
from .logger import logger, shutdown_logger
import uvicorn
import logging

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

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Video Manager"}

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """서버를 시작합니다."""
    setup_signal_handlers()  # 시그널 핸들러 설정
    
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Manager Server")
    parser.add_argument("--host", default="127.0.0.1", help="서버 호스트 주소")
    parser.add_argument("--port", type=int, default=8000, help="서버 포트 번호")
    
    args = parser.parse_args()
    start_server(args.host, args.port) 