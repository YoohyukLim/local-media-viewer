from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.video import scan_videos, get_videos
from ..models.video import Video

router = APIRouter()

@router.post("/scan", summary="비디오 파일 스캔", 
    description="설정된 디렉토리들에서 비디오 파일들을 스캔하여 DB에 저장합니다.")
def scan_directory(db: Session = Depends(get_db)):
    """
    config.yaml에 설정된 video_directories 경로들에서 비디오 파일들을 스캔하여 DB에 저장합니다.
    """
    scan_videos(db)
    return {"message": "Video scanning completed"}

@router.get("/list", summary="비디오 목록 조회",
    description="저장된 모든 비디오 파일 목록을 반환합니다.")
def list_videos(db: Session = Depends(get_db)):
    """
    DB에 저장된 모든 비디오 파일 정보를 반환합니다.
    """
    return get_videos(db) 