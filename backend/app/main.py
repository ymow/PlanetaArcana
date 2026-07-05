"""FastAPI 主應用程式"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import (
    auth,
    card_visuals,
    cards,
    conversations,
    daily_draws,
    divines,
    personas,
    quota,
    spreads,
)
from app.db.database import Base, engine, ensure_schema

# 建立資料表（create_all 只建新表;ensure_schema 補既有表的新欄位）
Base.metadata.create_all(bind=engine)
ensure_schema()

# 建立 FastAPI 應用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基於 Claude AI 的偉特塔羅占卜與解讀系統",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(cards.router, prefix=settings.API_V1_PREFIX)
app.include_router(card_visuals.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(divines.router, prefix=settings.API_V1_PREFIX)
app.include_router(conversations.router, prefix=settings.API_V1_PREFIX)
app.include_router(daily_draws.router, prefix=settings.API_V1_PREFIX)
app.include_router(quota.router, prefix=settings.API_V1_PREFIX)
app.include_router(personas.router, prefix=settings.API_V1_PREFIX)
app.include_router(spreads.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """根路徑"""
    return {
        "message": "歡迎來到 Planeta Arcana - AI 塔羅解讀系統",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy"}
