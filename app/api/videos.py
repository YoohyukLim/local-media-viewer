from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, conint
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.scanner import scan_videos, get_videos
from ..services.tags import search_videos_by_tags, get_all_tags, add_video_tag, remove_video_tag
from ..config import settings
from ..models.video import Video

router = APIRouter()

# 요청 모델 추가
class AddTagRequest(BaseModel):
    tag_name: str

@router.post("/scan", summary="비디오 파일 스캔", 
    description="설정된 디렉토리들에서 비디오 파일들을 스캔하여 DB에 저장합니다.")
def scan_directory(db: Session = Depends(get_db)):
    """
    config.yaml에 설정된 video_directories 경로들에서 비디오 파일들을 스캔하여 DB에 저장합니다.
    """
    scan_videos(db)
    return {"message": "Video scanning completed"}

@router.get("/list", 
    summary="비디오 목록 조회",
    description="저장된 비디오 파일 목록을 페이징하여 반환합니다.")
def list_videos(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, ge=1, le=100, description="페이지당 아이템 수"),
    db: Session = Depends(get_db)
):
    """
    DB에 저장된 비디오 파일 정보를 페이징하여 반환합니다.
    - page: 페이지 번호 (1부터 시작)
    - page_size: 페이지당 아이템 수 (1~100)
    """
    videos, total = get_videos(db, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size  # 전체 페이지 수 계산
    
    return {
        "total_items": total,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "items": videos
    }

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
    result = []
    
    for video in videos:
        video_dict = {
            "id": video.id,
            "file_path": video.file_path,
            "file_name": video.file_name,
            "thumbnail_id": video.thumbnail_id,
            "duration": video.duration,
            "category": video.category,
            "created_at": video.created_at,
            "updated_at": video.updated_at,
            "thumbnail_path": settings.get_thumbnail_path(video.thumbnail_id),
            "tags": [{"id": tag.id, "name": tag.name} for tag in video.tags]
        }
        result.append(video_dict)
    
    return result

@router.post("/{video_id}/tags", 
    summary="비디오에 태그 추가",
    description="지정된 비디오에 태그를 추가합니다.")
def add_tag(
    video_id: int,
    tag_request: AddTagRequest,
    db: Session = Depends(get_db)
):
    """비디오에 태그를 추가합니다."""
    video, added = add_video_tag(db, video_id, tag_request.tag_name)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "message": "Tag added successfully" if added else "Tag already exists",
        "video_id": video_id,
        "tag_name": tag_request.tag_name,
        "added": added
    }

@router.delete("/{video_id}/tags/{tag_id}",
    summary="비디오에서 태그 제거",
    description="지정된 비디오에서 태그를 제거합니다.")
def remove_tag(
    video_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """비디오에서 태그를 제거합니다."""
    video, removed = remove_video_tag(db, video_id, tag_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "message": "Tag removed successfully" if removed else "Tag not found",
        "video_id": video_id,
        "tag_id": tag_id,
        "removed": removed
    } 