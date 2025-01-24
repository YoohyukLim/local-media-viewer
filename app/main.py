from fastapi import FastAPI
from .database import engine, Base, get_db
from .api import videos
from .services.scanner import scan_videos

app = FastAPI(title="Video Manager")

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트 핸들러"""
    print("Scanning videos on startup...")
    try:
        # get_db는 제너레이터이므로 next()로 첫 번째 값을 가져옴
        db = next(get_db())
        scan_videos(db)
        print("Initial video scan completed")
    except Exception as e:
        print(f"Error during initial video scan: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Video Manager"} 