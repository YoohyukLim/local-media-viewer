import os
from app.database import engine

def init_db():
    """데이터베이스를 초기화합니다."""
    db_path = "videos.db"
    
    # DB 연결 종료
    engine.dispose()
    
    # DB 파일이 존재하면 삭제
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Database file '{db_path}' has been deleted.")
        except Exception as e:
            print(f"Error deleting database file: {str(e)}")
    else:
        print(f"Database file '{db_path}' does not exist.")

if __name__ == "__main__":
    init_db()