from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., description="Google Identity Services ID token")


class DevLoginRequest(BaseModel):
    email: str
    name: Optional[str] = None
