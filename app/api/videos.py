from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.scanner import scan_videos, get_videos
from ..services.tags import search_videos_by_tags, get_all_tags
from ..config import settings
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

@router.get("/tags", summary="전체 태그 목록",
    description="사용 중인 모든 태그 목록을 반환합니다.")
def list_tags(db: Session = Depends(get_db)):
    """모든 태그 목록을 반환합니다."""
    return get_all_tags(db)

@router.get("/search", summary="태그로 비디오 검색",
    description="지정된 태그들을 포함하는 비디오를 검색합니다.")
def search_videos(
    tags: List[str] = Query(..., description="검색할 태그 목록"),
    require_all: bool = Query(False, description="모든 태그를 포함해야 하는지 여부"),
    db: Session = Depends(get_db)
):
    """태그로 비디오를 검색합니다."""
    videos = search_videos_by_tags(db, tags, require_all)
    # 썸네일 경로 추가
    for video in videos:
        video.thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
    return videos 