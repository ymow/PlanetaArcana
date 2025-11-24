from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 建立資料庫引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG
)

# 建立 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立 Base Model
Base = declarative_base()


def get_db():
    """
    資料庫 Session 依賴注入
    用於 FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
