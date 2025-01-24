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
                        # 임시 썸네일 경로
                        thumbnail_path = f"{settings.THUMBNAIL_DIR}/{os.path.splitext(file)[0]}.jpg"
                        
                        video = Video(
                            file_path=file_path,
                            thumbnail_path=thumbnail_path
                        )
                        db.add(video)
    
    db.commit()
    
def get_videos(db: Session):
    """저장된 모든 비디오 목록을 반환합니다."""
    return db.query(Video).all() 