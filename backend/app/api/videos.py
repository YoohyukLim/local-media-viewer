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
from ..services.metadata import update_video_info
import socket

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

class TagCreate(BaseModel):
    name: str

class UpdateVideoTags(BaseModel):
    tag_ids: List[int]

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
    
    # 비디오 목록 변환
    items = []
    for video in videos:
        # 컨테이너 모드일 때 파일 경로를 호스트 경로로 변환
        file_path = settings.get_host_path(video.file_path) if settings.CONTAINER_MODE else video.file_path
        
        items.append({
            "id": video.id,
            "file_path": file_path,
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
        })
    
    return {
        "items": items,
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

@router.post("/tags", 
    response_model=TagResponse,
    summary="태그 생성",
    description="새로운 태그를 생성하거나, 이미 존재하는 태그의 정보를 반환합니다.")
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """태그를 생성하고 ID를 반환합니다."""
    try:
        # 이미 존재하는 태그 확인
        existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
        if existing_tag:
            return {"id": existing_tag.id, "name": existing_tag.name}
        
        # 새 태그 생성
        new_tag = Tag(name=tag.name)
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        
        return {"id": new_tag.id, "name": new_tag.name}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{video_id}/tags", 
    response_model=TagResponse,
    summary="비디오에 태그 추가",
    description="비디오에 새로운 태그를 추가합니다. 태그가 존재하지 않으면 새로 생성합니다.")
async def add_video_tag(
    video_id: int, 
    tag: TagCreate
):
    """비디오에 태그를 추가합니다."""
    db = next(get_db())
    cursor = db.cursor()
    
    try:
        # 먼저 태그 생성 또는 조회
        cursor.execute(
            "SELECT id, name FROM tags WHERE name = ?",
            (tag.name,)
        )
        existing_tag = cursor.fetchone()
        
        if existing_tag:
            tag_id = existing_tag[0]
        else:
            cursor.execute(
                "INSERT INTO tags (name) VALUES (?)",
                (tag.name,)
            )
            tag_id = cursor.lastrowid
        
        # 비디오-태그 연결이 이미 존재하는지 확인
        cursor.execute(
            "SELECT 1 FROM video_tags WHERE video_id = ? AND tag_id = ?",
            (video_id, tag_id)
        )
        if cursor.fetchone():
            return {"id": tag_id, "name": tag.name}
        
        # 비디오-태그 연결
        cursor.execute(
            "INSERT INTO video_tags (video_id, tag_id) VALUES (?, ?)",
            (video_id, tag_id)
        )
        db.commit()
        
        return {"id": tag_id, "name": tag.name}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

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
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    try:
        logger.info(f"Playing video: {video.file_path}")
        if settings.CONTAINER_MODE:
            # 컨테이너 내부 경로를 호스트 경로로 변환
            host_path = settings.get_host_path(video.file_path)
            logger.info(f"Converted path: {host_path}")
            
            try:
                # TCP 소켓으로 파일 경로 전송
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    logger.info(f"Connecting to player at {settings.PLAYER_HOST}:{settings.PLAYER_PORT}")
                    sock.connect((settings.PLAYER_HOST, settings.PLAYER_PORT))
                    sock.sendall(f"{host_path}\n".encode('utf-8'))
                    logger.info("Sent file path to player")
            except ConnectionRefusedError:
                raise HTTPException(
                    status_code=500,
                    detail="Player service is not running"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to player: {str(e)}"
                )
        else:
            # 로컬 모드에서는 기존 방식대로 직접 실행
            os.startfile(video.file_path)
            
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error playing video: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to play video: {str(e)}"
        )

@router.put("/{video_id}/tags",
    response_model=List[TagResponse],
    summary="비디오 태그 목록 갱신",
    description="비디오의 태그 목록을 갱신합니다. 요청에 포함되지 않은 기존 태그는 삭제됩니다.")
async def update_video_tags(video_id: int, update: UpdateVideoTags, db: Session = Depends(get_db)):
    """비디오의 태그 목록을 갱신합니다."""
    try:
        # 비디오 조회
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        # 요청된 태그들이 실제로 존재하는지 확인
        tags = db.query(Tag).filter(Tag.id.in_(update.tag_ids)).all()
        if len(tags) != len(update.tag_ids):
            raise HTTPException(status_code=400, detail="Some tag IDs are invalid")
        
        # 태그 목록 업데이트
        video.tags = tags
        db.commit()

        # info 파일 업데이트
        tag_list = [{"id": tag.id, "name": tag.name} for tag in tags]
        update_video_info(video.file_path, {"tags": tag_list})
        
        return tag_list
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 