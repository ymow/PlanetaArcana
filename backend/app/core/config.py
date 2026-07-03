from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """應用程式設定"""

    # Database
    DATABASE_URL: str = "sqlite:///./planeta_arcana.db"

    # Anthropic API
    ANTHROPIC_API_KEY: str

    # App Settings
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    PROJECT_NAME: str = "Planeta Arcana"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    APP_TIMEZONE: str = "Asia/Taipei"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """將 CORS_ORIGINS 字串轉換為列表"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:5173"]

    # AI Settings
    AI_MODEL: str = "claude-sonnet-4-6"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7

    # Rate Limiting（AI 端點成本保護）
    AI_DAILY_LIMIT: int = 20  # 每 IP 每日 AI 呼叫上限
    AI_RATE_LIMIT_PER_MINUTE: int = 5  # 每 IP 每分鐘突發上限
    AI_SHARE_BONUS_DAILY_MAX: int = 3  # 每日透過分享最多可加的配額次數

    # Auth
    GOOGLE_CLIENT_ID: str = ""
    AUTH_TOKEN_TTL_SECONDS: int = 60 * 60 * 24 * 30
    AUTH_DEV_LOGIN_ENABLED: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
