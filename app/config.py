import os
import yaml
from pathlib import Path

class Settings:
    def __init__(self):
        self.config = self._load_config()
        self.VIDEO_DIRECTORIES = self._get_video_directories()
        self.THUMBNAIL_CONFIG = self._get_thumbnail_config()
    
    def _load_config(self) -> dict:
        """설정 파일을 로드합니다."""
        config_path = Path("config.yaml")
        
        # 설정 파일이 없으면 기본 설정 파일 생성
        if not config_path.exists():
            default_config = {
                "video_directories": ["D:/Videos"],
                "thumbnails": {
                    "directory": "D:/thumbnails",
                    "extension": ".jpg"
                }
            }
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
        
        # 설정 파일 로드
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _get_video_directories(self) -> list[str]:
        """설정된 비디오 디렉토리 목록을 반환합니다."""
        dirs = self.config.get("video_directories", [])
        
        # 존재하는 디렉토리만 필터링
        valid_dirs = [dir for dir in dirs if os.path.isdir(dir)]
        
        if not valid_dirs:
            raise ValueError(
                "유효한 비디오 디렉토리가 없습니다. "
                "config.yaml의 video_directories를 확인해주세요."
            )
        
        return valid_dirs

    def _get_thumbnail_config(self) -> dict:
        """썸네일 설정을 반환합니다."""
        thumb_config = self.config.get("thumbnails", {})
        thumb_dir = thumb_config.get("directory", "D:/thumbnails")
        
        # 썸네일 디렉토리가 없으면 생성
        os.makedirs(thumb_dir, exist_ok=True)
        
        return {
            "directory": thumb_dir,
            "extension": thumb_config.get("extension", ".jpg")
        }
    
    def get_thumbnail_path(self, thumbnail_id: str) -> str:
        """썸네일 ID로부터 전체 경로를 생성합니다."""
        return os.path.join(
            self.THUMBNAIL_CONFIG["directory"],
            f"{thumbnail_id}{self.THUMBNAIL_CONFIG['extension']}"
        )

settings = Settings() 