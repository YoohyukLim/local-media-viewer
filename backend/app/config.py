import os
import yaml
import argparse
from pathlib import Path

class Settings:
    def __init__(self, config_path: str | None = None):
        self.config_path = config_path
        self.reload()
    
    def reload(self):
        """설정 파일을 다시 로드합니다."""
        # 설정 파일 경로 결정
        if self.config_path is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
            self.config_path = os.path.join(config_dir, "config.yaml")
        
        # config 디렉토리가 없으면 생성
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # 설정 파일이 없으면 기본 설정으로 생성
        if not os.path.exists(self.config_path):
            default_config = {
                "video_directories": ["D:/videos"],
                "database": {
                    "path": "D:/videos/videos.db"
                },
                "thumbnails": {
                    "directory": "D:/videos/thumbnails",
                    "extension": ".webp",
                    "duration": 3.0,
                    "fps": 5.0,
                    "max_size": 480,
                    "max_workers": 6
                }
            }
            os.makedirs(config_dir, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f, allow_unicode=True)

        # 설정 파일 로드
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        self.VIDEO_DIRECTORIES = config["video_directories"]
        self.DATABASE_PATH = config["database"]["path"]
        
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

# 전역 설정 객체는 main.py에서 초기화
settings = None 