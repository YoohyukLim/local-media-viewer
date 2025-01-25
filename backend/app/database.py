from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

Base = declarative_base()

def init_db():
    """데이터베이스를 초기화합니다."""
    # DB 디렉토리 생성
    db_dir = os.path.dirname(settings.DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # SQLite 엔진 생성
    engine = create_engine(
        f"sqlite:///{settings.DATABASE_PATH}",
        connect_args={"check_same_thread": False}
    )
    
    # 세션 팩토리 생성
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal

# DB 초기화는 main.py에서 settings 초기화 후에 수행
engine = None
SessionLocal = None

def get_db():
    global SessionLocal  # 전역 변수 참조
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 