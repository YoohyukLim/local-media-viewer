from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import os
from ..database import Base
from .tag import video_tags

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True)
    file_name = Column(String, index=True)  # 파일 이름 필드 추가
    thumbnail_id = Column(String, unique=True, index=True)  # UUID 기반 썸네일 ID
    duration = Column(Float)  # 영상 길이 (초 단위)
    category = Column(String, index=True)  # 카테고리
    tags = relationship("Tag", secondary=video_tags, back_populates="videos")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_file_name(file_path: str) -> str:
        """파일 경로에서 파일 이름을 추출합니다."""
        return os.path.basename(file_path) 