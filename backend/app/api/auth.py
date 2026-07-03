"""帳號登入 API"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    DevLoginRequest,
    GoogleAuthRequest,
    User as UserSchema,
)

try:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token
except ImportError:  # pragma: no cover - exercised only when package is absent
    google_requests = None
    id_token = None

router = APIRouter(prefix="/auth", tags=["Auth"])


def _validate_email(email: str) -> str:
    normalized = email.strip().lower()
    if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=422, detail="email 格式不正確")
    return normalized


def _upsert_user(
    db: Session,
    *,
    email: str,
    name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    google_sub: Optional[str] = None,
) -> User:
    query = None
    if google_sub:
        query = db.query(User).filter(User.google_sub == google_sub).first()
    user = query or db.query(User).filter(User.email == email).first()

    if user:
        user.name = name or user.name
        user.avatar_url = avatar_url or user.avatar_url
        user.google_sub = google_sub or user.google_sub
        user.last_login_at = datetime.utcnow()
    else:
        user = User(
            email=email,
            name=name,
            avatar_url=avatar_url,
            google_sub=google_sub,
            last_login_at=datetime.utcnow(),
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(user), user=user)


@router.post("/google", response_model=AuthResponse)
def login_with_google(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    """使用 Google Identity Services ID token 登入。"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="尚未設定 GOOGLE_CLIENT_ID")
    if not id_token or not google_requests:
        raise HTTPException(status_code=503, detail="尚未安裝 google-auth")

    try:
        claims = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Google 登入憑證無效")

    email = claims.get("email")
    sub = claims.get("sub")
    if not email or not sub:
        raise HTTPException(status_code=401, detail="Google 登入憑證缺少必要資訊")

    user = _upsert_user(
        db,
        email=_validate_email(email),
        name=claims.get("name"),
        avatar_url=claims.get("picture"),
        google_sub=sub,
    )
    return _auth_response(user)


@router.post("/dev", response_model=AuthResponse)
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)):
    """本機開發用登入; production 預設關閉。"""
    if not (settings.DEBUG or settings.AUTH_DEV_LOGIN_ENABLED):
        raise HTTPException(status_code=403, detail="開發登入未啟用")

    user = _upsert_user(
        db,
        email=_validate_email(payload.email),
        name=payload.name or payload.email.split("@", 1)[0],
    )
    return _auth_response(user)


@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
