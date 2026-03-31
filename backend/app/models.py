"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    api_key = Column(String, unique=True, index=True, nullable=True)  # API Key for QClaw
    created_at = Column(DateTime, default=datetime.utcnow)
    
    files = relationship("File", back_populates="owner")
    comments = relationship("Comment", back_populates="author")


class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)  # 本地路径
    file_size = Column(Integer)
    file_type = Column(String)  # 文件类型
    tags = Column(String, nullable=True)  # 逗号分隔的标签
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="files")
    comments = relationship("Comment", back_populates="file")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    file_id = Column(Integer, ForeignKey("files.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    file = relationship("File", back_populates="comments")
    author = relationship("User", back_populates="comments")
