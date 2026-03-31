"""
Company — 团队协作平台
FastAPI 主应用
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Security, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import shutil
from typing import Optional

from .database import get_db, init_db
from .models import User, File as FileModel, Comment
from .schemas import (
    UserCreate, UserResponse, FileCreate, FileResponse,
    CommentCreate, CommentResponse, Token
)
from .auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from .api_key import generate_api_key, get_user_by_api_key

# 初始化应用
app = FastAPI(title="Company", description="团队协作平台")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()

# 文件存储目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── 用户相关 ──────────────────────────────────────

@app.post("/api/users/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """注册用户"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/users/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """登录"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


# ── 文件相关 ──────────────────────────────────────

@app.post("/api/files/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(default=""),
    tags: str = Form(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文件"""
    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 获取文件大小和类型
    file_size = os.path.getsize(file_path)
    file_type = file.content_type or "unknown"
    
    # 保存到数据库
    db_file = FileModel(
        filename=file.filename,
        description=description,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        tags=tags,
        owner_id=current_user.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file


@app.get("/api/files/public")
def list_public_files(db: Session = Depends(get_db)):
    """公开文件列表（无需登录）"""
    files = db.query(FileModel).all()
    return files


@app.get("/api/files", response_model=list[FileResponse])
def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出所有文件"""
    files = db.query(FileModel).all()
    return files


@app.get("/api/files/{file_id}", response_model=FileResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文件详情"""
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@app.get("/api/files/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """下载文件"""
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file.file_path,
        filename=file.filename
    )


@app.delete("/api/files/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除文件"""
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted"}


# ── 评论相关 ──────────────────────────────────────

@app.post("/api/comments", response_model=CommentResponse)
def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建评论"""
    file = db.query(FileModel).filter(FileModel.id == comment.file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    db_comment = Comment(
        content=comment.content,
        file_id=comment.file_id,
        author_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


@app.get("/api/files/{file_id}/comments", response_model=list[CommentResponse])
def get_file_comments(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文件的所有评论"""
    comments = db.query(Comment).filter(Comment.file_id == file_id).all()
    return comments


# ── API Key 管理（QClaw 集成）────────────────────

@app.post("/api/users/me/api-key")
def generate_api_key_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成用户的 API Key（用于 QClaw 集成）"""
    from .api_key import generate_api_key
    
    if current_user.api_key:
        return {"api_key": current_user.api_key, "message": "You already have an API Key"}
    
    api_key = generate_api_key()
    current_user.api_key = api_key
    db.commit()
    
    return {"api_key": api_key, "message": "API Key generated. Keep it safe!"}


# ── 管理员功能 ─────────────────────────────────────

@app.get("/api/admin/users")
def list_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """列出所有用户（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_admin": u.is_admin,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]


@app.delete("/api/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.is_admin:
        raise HTTPException(status_code=400, detail="不能删除管理员")
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户已删除"}


@app.post("/api/admin/users/{user_id}/toggle-admin")
def toggle_admin(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换用户管理员权限（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_admin = not user.is_admin
    db.commit()
    
    return {"message": f"用户 {'已成为' if user.is_admin else '已取消'} 管理员"}


@app.post("/api/files/upload-by-api-key", response_model=FileResponse)
async def upload_file_by_api_key(
    file: UploadFile = File(...),
    description: str = Form(default=""),
    tags: str = Form(default=""),
    current_user: User = Depends(get_user_by_api_key),
    db: Session = Depends(get_db)
):
    """通过 API Key 上传文件（QClaw 专用）"""
    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path)
    file_type = file.content_type or "unknown"
    
    db_file = FileModel(
        filename=file.filename,
        description=description,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        tags=tags,
        owner_id=current_user.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file


# ── 健康检查 ──────────────────────────────────────

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
