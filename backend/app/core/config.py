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

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """將 CORS_ORIGINS 字串轉換為列表"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except:
            return ["http://localhost:5173"]

    # AI Settings
    AI_MODEL: str = "claude-sonnet-4-20250514"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
