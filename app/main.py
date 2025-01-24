from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine, Base, get_db
from .api import videos
from .services.scanner import scan_videos
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    서버 시작/종료 시 실행되는 이벤트 핸들러
    """
    # 시작 시 실행
    print("Scanning videos on startup...")
    try:
        db = next(get_db())
        scan_videos(db)
        print("Initial video scan completed")
    except Exception as e:
        print(f"Error during initial video scan: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        db.close()
    
    yield  # 서버 실행 중
    
    # 종료 시 실행
    print("Shutting down...")

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
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Manager Server")
    parser.add_argument("--host", default="127.0.0.1", help="서버 호스트 주소")
    parser.add_argument("--port", type=int, default=8000, help="서버 포트 번호")
    
    args = parser.parse_args()
    start_server(args.host, args.port) 