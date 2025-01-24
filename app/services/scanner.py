import os
import cv2
from sqlalchemy.orm import Session
from ..models.video import Video
from .thumbnail import ensure_thumbnail, create_thumbnail
from .metadata import (
    get_video_duration, is_video_modified, 
    update_video_metadata
)

def reload_settings() -> None:
    """설정 파일을 다시 로드합니다."""
    global settings
    from ..config import Settings
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
            print(f"Removing video from DB: {video.file_path}")
            try:
                thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            except Exception as e:
                print(f"Error removing thumbnail file: {str(e)}")
            db.delete(video)
    
    db.commit()

def scan_videos(db: Session):
    """설정된 디렉토리들의 비디오 파일들을 스캔하여 DB에 저장합니다."""
    reload_settings()
    
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    existing_files = set()
    
    for base_dir in settings.VIDEO_DIRECTORIES:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(video_extensions):
                    file_path = os.path.join(root, file)
                    existing_files.add(file_path)
                    
                    existing_video = db.query(Video).filter(Video.file_path == file_path).first()
                    if existing_video:
                        if is_video_modified(file_path, existing_video):
                            print(f"Updating modified video: {file_path}")
                            if not ensure_thumbnail(existing_video, file_path, settings):
                                print(f"Failed to create thumbnail for existing video: {file_path}")
                            
                            duration = get_video_duration(file_path)
                            if duration > 0:
                                existing_video.duration = duration
                                existing_video.file_name = Video.get_file_name(file_path)
                                update_video_metadata(existing_video, file_path, base_dir)
                                db.add(existing_video)
                        else:
                            if not ensure_thumbnail(existing_video, file_path, settings):
                                print(f"Failed to create thumbnail for existing video: {file_path}")
                            update_video_metadata(existing_video, file_path, base_dir)
                            db.add(existing_video)
                    else:
                        thumbnail_id = Video.generate_thumbnail_id()
                        thumbnail_path = settings.get_thumbnail_path(thumbnail_id)
                        
                        if create_thumbnail(file_path, thumbnail_path):
                            duration = get_video_duration(file_path)
                            video = Video(
                                file_path=file_path,
                                file_name=Video.get_file_name(file_path),
                                thumbnail_id=thumbnail_id,
                                duration=duration,
                                tags=[]
                            )
                            update_video_metadata(video, file_path, base_dir)
                            db.add(video)
                        else:
                            print(f"Skipping {file_path} due to thumbnail creation failure")
    
    remove_missing_videos(db, existing_files, settings.VIDEO_DIRECTORIES, settings)
    db.commit()

def get_videos(db: Session):
    """저장된 모든 비디오 목록을 반환합니다."""
    videos = db.query(Video).all()
    for video in videos:
        video.thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
    return videos 