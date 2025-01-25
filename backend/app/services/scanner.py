import os
import cv2
from sqlalchemy.orm import Session
from ..models.video import Video
from .thumbnail import ensure_thumbnail, create_thumbnail
from .metadata import (
    get_video_duration, is_video_modified, 
    update_video_metadata
)
from ..config import Settings
from typing import List
from .tags import cleanup_unused_tags
from ..logger import logger
from .thumbnail_worker import get_thumbnail_worker
import hashlib
from datetime import datetime

# 전역 settings 객체 초기화
settings = Settings()

def reload_settings() -> None:
    """설정 파일을 다시 로드합니다."""
    global settings
    settings = Settings()

def is_file_in_video_directories(file_path: str, video_directories: list[str]) -> bool:
    """파일이 설정된 비디오 디렉토리 중 하나에 포함되어 있는지 확인합니다."""
    file_path = os.path.normpath(file_path)
    for dir_path in video_directories:
        dir_path = os.path.normpath(dir_path)
        if file_path.startswith(dir_path):
            return True
    return False

def remove_missing_videos(db: Session, existing_files: set[str], video_directories: list[str], settings):
    """실제로 존재하지 않거나 설정된 디렉토리 외부에 있는 비디오 파일들을 DB에서 삭제합니다."""
    all_videos = db.query(Video).all()
    
    for video in all_videos:
        if (video.file_path not in existing_files or 
            not is_file_in_video_directories(video.file_path, video_directories)):
            logger.info(f"Removing video from DB: {video.file_path}")
            try:
                thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            except Exception as e:
                logger.error(f"Error removing thumbnail file: {str(e)}")
            db.delete(video)
    
    db.commit()

def get_thumbnail_id(file_path: str) -> str:
    """파일 경로를 해시하여 썸네일 ID를 생성합니다."""
    # 경로를 UTF-8로 인코딩하고 SHA-256 해시 생성
    hash_obj = hashlib.sha256(file_path.encode('utf-8'))
    # 32자리 hex 문자열 반환
    return hash_obj.hexdigest()[:32]

def scan_videos(db: Session):
    """비디오 파일들을 스캔하여 DB에 저장합니다."""
    try:
        logger.info("Starting video scan...")
        reload_settings()
        
        # 썸네일 워커 시작
        thumbnail_worker = get_thumbnail_worker(settings)
        
        video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
        existing_files = set()
        
        for base_dir in settings.VIDEO_DIRECTORIES:
            for root, _, files in os.walk(base_dir):
                for file in files:
                    if file.lower().endswith(video_extensions):
                        try:
                            file_path = os.path.join(root, file)
                            existing_files.add(file_path)
                            
                            existing_video = db.query(Video).filter(Video.file_path == file_path).first()
                            if existing_video:
                                if is_video_modified(file_path, existing_video):
                                    logger.info(f"Updating modified video: {file_path}")
                                    duration = get_video_duration(file_path)
                                    if duration > 0:
                                        existing_video.duration = duration
                                        existing_video.file_name = Video.get_file_name(file_path)
                                        existing_video.thumbnail_id = get_thumbnail_id(file_path)
                                        existing_video.updated_at = datetime.now()
                                db.add(existing_video)
                                db.flush()
                                update_video_metadata(existing_video, file_path, base_dir, db)

                                # 썸네일 업데이트 요청을 큐에 추가
                                thumbnail_worker.add_task(existing_video.thumbnail_id, file_path)
                            else:
                                logger.info(f"Adding new video: {file_path}")
                                # 새 비디오 추가
                                thumbnail_id = get_thumbnail_id(file_path)
                                duration = get_video_duration(file_path)
                                video = Video(
                                    file_path=file_path,
                                    file_name=Video.get_file_name(file_path),
                                    thumbnail_id=thumbnail_id,
                                    duration=duration
                                )
                                db.add(video)
                                db.flush()
                                update_video_metadata(video, file_path, base_dir, db)
                                
                                # 썸네일 생성 요청을 큐에 추가
                                thumbnail_worker.add_task(thumbnail_id, file_path)
                                
                        except Exception as e:
                            logger.error(f"Error processing file {file_path}: {str(e)}")
                            db.rollback()
                            raise
        
        remove_missing_videos(db, existing_files, settings.VIDEO_DIRECTORIES, settings)
        cleanup_unused_tags(db)
        db.commit()
        logger.info("Video scan completed successfully")
        
    except Exception as e:
        logger.error(f"Error in scan_videos: {str(e)}")
        db.rollback()
        raise

def get_videos(db: Session, page: int = 1, page_size: int = 10) -> tuple[List[dict], int]:
    """저장된 비디오 목록을 반환합니다."""
    # 전체 비디오 수 조회
    total = db.query(Video).count()
    
    # 페이징 및 정렬 적용하여 비디오 조회
    videos = db.query(Video)\
        .order_by(Video.file_name)\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
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
            "tags": [{"id": tag.id, "name": tag.name} for tag in video.tags]
        }
        result.append(video_dict)
    
    return result, total 