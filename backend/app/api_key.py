"""
API Key 认证（用于 QClaw 集成）
"""
from fastapi import HTTPException, Header
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User
import secrets


def generate_api_key() -> str:
    """生成安全的 API Key"""
    return f"cp_{secrets.token_urlsafe(32)}"


async def get_user_by_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> User:
    """通过 API Key 获取用户"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key required. Add X-API-Key header."
        )
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.api_key == x_api_key, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=403,
                detail="Invalid API Key"
            )
        return user
    finally:
        db.close()
