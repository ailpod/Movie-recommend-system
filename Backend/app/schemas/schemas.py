# Pydantic schemas - 简化版本
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


def process_movie_genres(genres_str: Optional[str]) -> Optional[str]:
    """
    处理电影标签显示逻辑：
    - 如果标签数量大于2个，就不展示"剧情"标签
    - 如果标签数量小于等于2个，保留"剧情"标签
    - 确保至少展示2-3个标签
    """
    if not genres_str:
        return None
    
    # 分割标签并去除空白
    genres = [genre.strip() for genre in genres_str.split(',') if genre.strip()]
    
    if len(genres) <= 2:
        # 标签数量<=2，保留所有标签包括"剧情"
        return ','.join(genres[:3])  # 最多展示3个
    else:
        # 标签数量>2，移除"剧情"标签
        filtered_genres = [genre for genre in genres if genre != '剧情']
        
        # 如果移除"剧情"后标签不足2个，保留原有标签
        if len(filtered_genres) < 2:
            return ','.join(genres[:3])
        else:
            # 确保展示2-3个标签
            return ','.join(filtered_genres[:3])


# 用户相关 Schema
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

# 电影相关 Schema
class MovieBase(BaseModel):
    title: str = Field(max_length=200)
    description: Optional[str] = None
    poster_path: Optional[str] = None
    genres: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    director: Optional[str] = Field(None, max_length=100)
    actors: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    poster_path: Optional[str] = None
    genres: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    director: Optional[str] = Field(None, max_length=100)
    actors: Optional[str] = None

class Movie(MovieBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    avg_rate: Optional[float] = 0.0
    vote: Optional[int] = 0
    is_favorited: Optional[bool] = False  # 添加收藏状态字段
    
    @field_validator('genres', mode='before')
    @classmethod
    def process_genres(cls, v):
        """应用标签显示逻辑"""
        return process_movie_genres(v)

# 响应中需要包含电影基本信息的简化版本
class MovieSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    poster_path: Optional[str] = None
    avg_rate: Optional[float] = 0.0
    genres: Optional[str] = None
    release_year: Optional[int] = None
    
    @field_validator('genres', mode='before')
    @classmethod
    def process_genres(cls, v):
        """应用标签显示逻辑"""
        return process_movie_genres(v)

# 浏览历史记录的响应 Schema
class BrowsingHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    movie: MovieSimple
    visited_at: datetime

# 收藏记录的响应 Schema  
class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    movie: MovieSimple
    created_at: datetime

# Token 相关
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
