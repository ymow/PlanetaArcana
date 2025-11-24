"""資料庫初始化腳本"""

from app.db.database import SessionLocal, Base, engine
from app.db.seed_cards import seed_tarot_cards


def init_db():
    """初始化資料庫"""
    print("初始化資料庫...")

    # 建立所有資料表
    Base.metadata.create_all(bind=engine)
    print("✓ 資料表建立完成")

    # 填入塔羅牌資料
    db = SessionLocal()
    try:
        seed_tarot_cards(db)
        print("✓ 塔羅牌資料建立完成")
    except Exception as e:
        print(f"✗ 塔羅牌資料建立失敗: {str(e)}")
        db.rollback()
    finally:
        db.close()

    print("\n資料庫初始化完成！")


if __name__ == "__main__":
    init_db()
