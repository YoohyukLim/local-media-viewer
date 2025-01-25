from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, conint
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.scanner import scan_videos, get_videos
from ..services.tags import get_all_tags, add_video_tag, remove_video_tag
from ..config import settings
from ..models.video import Video
from ..models.tag import Tag
from fastapi.responses import FileResponse
import os
import subprocess
import platform
from ..logger import logger
from sqlalchemy import select, and_
from sqlalchemy.sql import func
import math
from enum import Enum
from datetime import datetime, timedelta

router = APIRouter()

# 요청 모델 추가
class AddTagRequest(BaseModel):
    tag_name: str

class TagSearchMode(str, Enum):
    OR = "or"
    AND = "and"

class TagResponse(BaseModel):
    id: int
    name: str

class VideoResponse(BaseModel):
    id: int
    file_path: str
    file_name: str
    thumbnail_id: str
    duration: float
    category: str | None
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse]

    class Config:
        from_attributes = True

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
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=100),
    tag_ids: Optional[List[int]] = Query(None),
    tag_mode: TagSearchMode = Query(TagSearchMode.OR),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size
    
    # 태그 검색 조건 구성
    query = db.query(Video)
    if tag_ids:
        if tag_mode == TagSearchMode.OR:
            # OR 검색: 지정된 태그 중 하나라도 있는 비디오
            query = query.filter(Video.tags.any(Tag.id.in_(tag_ids)))
        else:
            # AND 검색: 지정된 태그를 모두 가진 비디오
            for tag_id in tag_ids:
                query = query.filter(Video.tags.any(Tag.id == tag_id))
    
    # 전체 개수 조회
    total = query.count()
    
    # 페이지네이션 적용
    videos = query.offset(offset).limit(size).all()
    
    total_pages = (total + size - 1) // size
    
    return {
        "items": [
            {
                "id": video.id,
                "file_path": video.file_path,
                "file_name": video.file_name,
                "thumbnail_id": video.thumbnail_id,
                "duration": video.duration,
                "category": video.category,
                "created_at": video.created_at,
                "updated_at": video.updated_at,
                "tags": [
                    {"id": tag.id, "name": tag.name} 
                    for tag in video.tags
                ]
            }
            for video in videos
        ],
        "total": total,
        "page": page,
        "size": size,
        "pages": total_pages
    }

@router.get("/tags", summary="전체 태그 목록",
    description="사용 중인 모든 태그 목록을 반환합니다.")
def list_tags(db: Session = Depends(get_db)):
    """모든 태그 목록을 반환합니다."""
    return get_all_tags(db)

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

@router.get("/thumbnails/{thumbnail_id}", 
    summary="썸네일 이미지 조회",
    description="지정된 ID의 썸네일 이미지를 반환합니다.",
    response_class=FileResponse)
async def get_thumbnail(thumbnail_id: str):
    """썸네일 이미지를 반환합니다."""
    try:
        thumbnail_path = settings.get_thumbnail_path(thumbnail_id)
        
        if not os.path.exists(thumbnail_path):
            raise HTTPException(
                status_code=404, 
                detail="Thumbnail not found"
            )
            
        headers = {
            'Cache-Control': 'public, max-age=600',  # 10분 캐싱
            'Expires': (datetime.now() + timedelta(minutes=10)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        }
            
        return FileResponse(
            path=thumbnail_path,
            media_type="image/webp",
            filename=f"{thumbnail_id}.webp",
            headers=headers
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving thumbnail: {str(e)}"
        )

@router.post("/play/{video_id}", 
    summary="비디오 재생",
    description="로컬 시스템에서 비디오 파일을 재생합니다.")
async def play_video(video_id: int, db: Session = Depends(get_db)):
    """비디오 파일을 시스템 기본 플레이어로 재생합니다."""
    # 비디오 정보 조회
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        logger.error(f"Video not found: {video_id}")
        raise HTTPException(status_code=404, detail="Video not found")
    
    # 파일 존재 여부 확인
    if not os.path.exists(video.file_path):
        logger.error(f"Video file not found: {video.file_path}")
        raise HTTPException(
            status_code=404, 
            detail=f"Video file not found: {video.file_path}"
        )
    
    try:
        logger.info(f"Playing video: {video.file_path}")
        system = platform.system()
        
        if system == "Windows":
            subprocess.Popen(['cmd', '/c', 'start', '', video.file_path], shell=True)
        elif system == "Darwin":  # macOS
            subprocess.Popen(['open', video.file_path])
        else:  # Linux
            subprocess.Popen(['xdg-open', video.file_path])
            
        return {"message": "Video playback started", "file_path": video.file_path}
        
    except Exception as e:
        logger.error(f"Failed to play video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to play video: {str(e)}"
        ) 