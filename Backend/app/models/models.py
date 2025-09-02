# SQLAlchemy models
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..core.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)  # male, female, other
    like_genres = Column(Text, nullable=True)  # 用户喜欢的电影类型，逗号分隔
    avatar = Column(String(255), nullable=True, default="/static/identify.jpg")  # 头像路径
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    browsing_history = relationship("BrowsingHistory", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

class Movie(Base):
    """电影模型 - 匹配JSON数据结构"""
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)  # 电影描述
    poster_path = Column(String(500))  # 海报路径
    avg_rate = Column(Float, default=0.0)  # 平均评分
    genres = Column(Text)  # 电影类型列表，逗号分隔
    release_year = Column(Integer)  # 发行年份
    director = Column(String(100))  # 导演
    actors = Column(Text)  # 演员列表，逗号分隔
    vote = Column(Integer, default=0)  # 投票数量
    keyword = Column(Text)  # 关键词，逗号分隔
    
    # 关联关系
    history_entries = relationship("BrowsingHistory", back_populates="movie")
    favorited_by = relationship("Favorite", back_populates="movie")


# 新增：浏览历史模型
class BrowsingHistory(Base):
    __tablename__ = "browsing_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    visited_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="browsing_history")
    movie = relationship("Movie", back_populates="history_entries")


# 新增：收藏记录模型
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="favorites")
    movie = relationship("Movie", back_populates="favorited_by")
