import os
from sqlalchemy.orm import Session
from ..models.video import Video
from ..config import settings

def scan_videos(db: Session):
    """설정된 디렉토리들의 비디오 파일들을 스캔하여 DB에 저장합니다."""
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    
    for base_dir in settings.VIDEO_DIRECTORIES:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(video_extensions):
                    file_path = os.path.join(root, file)
                    
                    # DB에 이미 존재하는지 확인
                    existing_video = db.query(Video).filter(Video.file_path == file_path).first()
                    if not existing_video:
                        # 새로운 썸네일 ID 생성
                        thumbnail_id = Video.generate_thumbnail_id()
                        
                        video = Video(
                            file_path=file_path,
                            thumbnail_id=thumbnail_id
                        )
                        db.add(video)
    
    db.commit()
    
def get_videos(db: Session):
    """저장된 모든 비디오 목록을 반환합니다."""
    videos = db.query(Video).all()
    # 썸네일 전체 경로 추가
    for video in videos:
        video.thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
    return videos 