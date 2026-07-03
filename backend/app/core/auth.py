"""輕量帳號驗證與 session token dependency"""

import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(user: User) -> str:
    """建立 HMAC 簽章的 app session token。"""
    payload = {
        "sub": user.id,
        "email": user.email,
        "exp": int(time.time()) + settings.AUTH_TOKEN_TTL_SECONDS,
    }
    body = _b64encode(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), body.encode("ascii"), hashlib.sha256
    ).digest()
    return f"{body}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict:
    try:
        body, signature = token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="無效的登入憑證")

    expected = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), body.encode("ascii"), hashlib.sha256
    ).digest()
    try:
        provided = _b64decode(signature)
    except Exception:
        raise HTTPException(status_code=401, detail="無效的登入憑證")

    if not hmac.compare_digest(expected, provided):
        raise HTTPException(status_code=401, detail="無效的登入憑證")

    try:
        payload = json.loads(_b64decode(body))
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=401, detail="無效的登入憑證")

    if payload.get("exp", 0) < int(time.time()):
        raise HTTPException(status_code=401, detail="登入已過期")

    return payload


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="無效的 Authorization header")
    return token


def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    token = _extract_bearer_token(authorization)
    if not token:
        return None

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="無效的登入憑證")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="找不到登入使用者")
    return user


def get_current_user(user: Optional[User] = Depends(get_optional_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="請先登入")
    return user
