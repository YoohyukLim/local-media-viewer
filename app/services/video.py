import os
from sqlalchemy.orm import Session
from ..models.video import Video

def scan_videos(directory: str, db: Session):
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(video_extensions):
                file_path = os.path.join(root, file)
                
                # DB에 이미 존재하는지 확인
                existing_video = db.query(Video).filter(Video.file_path == file_path).first()
                if not existing_video:
                    # 임시 썸네일 경로 (실제로는 썸네일 생성 로직 구현 필요)
                    thumbnail_path = f"thumbnails/{os.path.splitext(file)[0]}.jpg"
                    
                    video = Video(
                        file_path=file_path,
                        thumbnail_path=thumbnail_path
                    )
                    db.add(video)
    
    db.commit() 