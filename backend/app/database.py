from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# DB 파일 경로 설정
db_dir = os.path.dirname(settings.DATABASE_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.DATABASE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 