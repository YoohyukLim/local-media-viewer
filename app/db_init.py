from database import Base, engine

def init_db():
    """데이터베이스를 초기화합니다."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization completed!")

if __name__ == "__main__":
    init_db()