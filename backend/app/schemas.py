"""
Pydantic 数据验证模型
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ── 用户 ──────────────────────────────
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ── 文件 ──────────────────────────────
class FileBase(BaseModel):
    filename: str
    description: Optional[str] = None
    tags: Optional[str] = None


class FileCreate(FileBase):
    pass


class FileResponse(FileBase):
    id: int
    file_size: int
    file_type: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ── 评论 ──────────────────────────────
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    file_id: int


class CommentResponse(CommentBase):
    id: int
    file_id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ── 登录 ──────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
