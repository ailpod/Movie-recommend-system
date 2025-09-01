# CRUD operations for user actions (favorites, history)
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List

from .. import models

# 北京时间时区
BEIJING_TZ = timezone(timedelta(hours=8))


# --- 收藏功能 CRUD ---
def get_favorite(db: Session, user_id: int, movie_id: int):
    """检查用户是否已收藏特定电影"""
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id, 
        models.Favorite.movie_id == movie_id
    ).first()


def create_favorite(db: Session, user_id: int, movie_id: int):
    """添加收藏"""
    db_favorite = models.Favorite(user_id=user_id, movie_id=movie_id)
    db_favorite.created_at = datetime.now(BEIJING_TZ)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def delete_favorite(db: Session, user_id: int, movie_id: int):
    """删除收藏"""
    db_favorite = get_favorite(db, user_id, movie_id)
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
    return db_favorite


def get_user_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """获取用户收藏列表"""
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).order_by(models.Favorite.created_at.desc()).offset(skip).limit(limit).all()


# --- 历史记录 CRUD ---
def get_history_record(db: Session, user_id: int, movie_id: int):
    """获取特定的浏览历史记录"""
    return db.query(models.BrowsingHistory).filter(
        models.BrowsingHistory.user_id == user_id,
        models.BrowsingHistory.movie_id == movie_id
    ).first()


def create_or_update_history(db: Session, user_id: int, movie_id: int):
    """创建或更新浏览历史"""
    db_history = db.query(models.BrowsingHistory).filter_by(
        user_id=user_id, movie_id=movie_id
    ).first()
    
    if db_history:
        # 如果存在，则更新访问时间为北京时间
        db_history.visited_at = datetime.now(BEIJING_TZ)
    else:
        # 如果不存在，则创建新记录，使用北京时间
        db_history = models.BrowsingHistory(user_id=user_id, movie_id=movie_id)
        db_history.visited_at = datetime.now(BEIJING_TZ)
        db.add(db_history)
    
    db.commit()
    db.refresh(db_history)
    return db_history


def delete_history_record(db: Session, user_id: int, movie_id: int):
    """删除特定的浏览历史记录"""
    db_history = get_history_record(db, user_id, movie_id)
    if db_history:
        db.delete(db_history)
        db.commit()
    return db_history


def delete_all_user_history(db: Session, user_id: int):
    """删除用户的所有浏览历史"""
    deleted_count = db.query(models.BrowsingHistory).filter(
        models.BrowsingHistory.user_id == user_id
    ).delete()
    db.commit()
    return deleted_count


def get_user_history(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """获取用户浏览历史"""
    return db.query(models.BrowsingHistory).filter(
        models.BrowsingHistory.user_id == user_id
    ).order_by(models.BrowsingHistory.visited_at.desc()).offset(skip).limit(limit).all()


def check_movie_favorited(db: Session, user_id: int, movie_id: int) -> bool:
    """检查电影是否已被用户收藏"""
    favorite = get_favorite(db, user_id, movie_id)
    return favorite is not None
