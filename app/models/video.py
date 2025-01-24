from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
import uuid
from ..database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True)
    thumbnail_id = Column(String, unique=True, index=True)  # UUID 기반 썸네일 ID
    duration = Column(Float)  # 영상 길이 (초 단위)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def generate_thumbnail_id():
        return str(uuid.uuid4()) 