from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.video import scan_videos
from ..models.video import Video

router = APIRouter()

@router.post("/scan")
def scan_directory(directory: str, db: Session = Depends(get_db)):
    scan_videos(directory, db)
    return {"message": "Video scanning completed"}

@router.get("/list")
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).all()
    return videos 