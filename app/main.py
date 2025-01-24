from fastapi import FastAPI
from .database import engine, Base
from .api import videos

app = FastAPI(title="Video Manager")

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])

# 루트 경로 핸들러 추가
@app.get("/")
def read_root():
    return {"message": "Welcome to Video Manager"} 