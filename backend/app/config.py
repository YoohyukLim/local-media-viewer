import os
import yaml
from pathlib import Path

class Settings:
    def __init__(self):
        self.reload()
    
    def reload(self):
        """설정 파일을 다시 로드합니다."""
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        self.VIDEO_DIRECTORIES = config["video_directories"]
        
        # DB 설정
        self.DATABASE_PATH = config["database"]["path"]
        
        # 썸네일 설정
        thumbnails = config["thumbnails"]
        self.THUMBNAIL_DIR = thumbnails["directory"]
        self.THUMBNAIL_EXT = thumbnails["extension"]
        self.THUMBNAIL_DURATION = float(thumbnails.get("duration", 3.0))
        self.THUMBNAIL_FPS = float(thumbnails.get("fps", 10.0))
        self.THUMBNAIL_MAX_SIZE = int(thumbnails.get("max_size", 480))
        self.THUMBNAIL_MAX_WORKERS = int(thumbnails.get("max_workers", 4))

    def get_thumbnail_path(self, thumbnail_id: str) -> str:
        """썸네일 파일의 전체 경로를 반환합니다."""
        return os.path.join(self.THUMBNAIL_DIR, f"{thumbnail_id}{self.THUMBNAIL_EXT}")

settings = Settings() 