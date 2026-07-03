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


# create_all 只會建新表,不會對既有表加欄位。這裡列出後來新增的欄位,
# 啟動時補上缺的（SQLite 專用的極簡 migration;正式引入 Alembic 後應移除）。
_COLUMN_PATCHES = [
    ("divines", "persona_id", "VARCHAR(50)"),
]


def ensure_schema() -> None:
    """對既有資料表補上後來新增的欄位（於 create_all 之後呼叫）。"""
    if "sqlite" not in settings.DATABASE_URL:
        return

    from sqlalchemy import text

    with engine.connect() as conn:
        for table, column, ddl_type in _COLUMN_PATCHES:
            existing = {
                row[1]
                for row in conn.execute(text(f"PRAGMA table_info({table})"))
            }
            if existing and column not in existing:
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type}")
                )
                conn.commit()
