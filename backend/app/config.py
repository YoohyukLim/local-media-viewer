import os
import yaml
import logging
from pathlib import Path
from typing import Dict

# 로거 설정
logger = logging.getLogger(__name__)

class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config_path = None
        return cls._instance
    
    def __init__(self):
        # __new__에서 이미 초기화된 경우 __init__은 건너뜀
        pass
    
    def init_settings(self, config_path: str | None = None):
        """설정을 초기화합니다."""
        self.config_path = config_path
        self.reload()
    
    def reload(self):
        """설정 파일을 다시 로드합니다."""
        # 설정 파일 경로 결정
        if self.config_path is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
            self.config_path = os.path.join(config_dir, "config.local.yaml")
        
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
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
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
        
        # 컨테이너 모드 설정
        container_config = config.get("container", {})
        self.CONTAINER_MODE = bool(container_config.get("mode", False))
        self.PLAYER_HOST = container_config.get("player_host", "localhost")
        self.PLAYER_PORT = int(container_config.get("player_port", 9990))
        self.COMPOSE_PATH = container_config.get("compose_path", "/app/docker-compose.yml")

        # Docker Compose 볼륨 마운트 정보 로드
        self.volume_mounts = {}
        if self.CONTAINER_MODE and os.path.exists(self.COMPOSE_PATH):
            logger.info(f"Loading Docker Compose file: {self.COMPOSE_PATH}")
            try:
                with open(self.COMPOSE_PATH, 'r', encoding='utf-8') as f:
                    compose_config = yaml.safe_load(f)
                
                if compose_config and 'services' in compose_config:
                    backend_config = compose_config['services'].get('backend', {})
                    volumes = backend_config.get('volumes', [])
                    
                    for volume in volumes:
                        if isinstance(volume, dict) and volume.get('type') == 'bind':
                            source = volume.get('source', '').replace('\\', '/')
                            target = volume.get('target', '').replace('\\', '/')
                            if source and target:
                                self.volume_mounts[target] = source
                
                logger.info(f"Loaded volume mounts: {self.volume_mounts}")
            except Exception as e:
                logger.error(f"Failed to load docker-compose.yml: {e}")
                self.volume_mounts = {}

    def get_thumbnail_path(self, thumbnail_id: str) -> str:
        """썸네일 파일의 전체 경로를 반환합니다."""
        return os.path.join(self.THUMBNAIL_DIR, f"{thumbnail_id}{self.THUMBNAIL_EXT}")

    def get_host_path(self, container_path: str) -> str:
        """컨테이너 내부 경로를 호스트 경로로 변환"""
        if not self.CONTAINER_MODE:
            return container_path
            
        container_path = container_path.replace('\\', '/')
        for target, source in self.volume_mounts.items():
            if container_path.startswith(target):
                return container_path.replace(target, source)
        
        return container_path
    
    def get_container_path(self, host_path: str) -> str:
        """호스트 경로를 컨테이너 내부 경로로 변환"""
        if not self.CONTAINER_MODE:
            return host_path
            
        host_path = host_path.replace('\\', '/')
        for target, source in self.volume_mounts.items():
            if host_path.startswith(source):
                return host_path.replace(source, target)
        
        return host_path

# 전역 설정 객체
settings = Settings() 