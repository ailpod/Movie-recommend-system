"""评分相关的数据库操作"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from ..models.models import Rating, Movie
from ..schemas.schemas import RatingCreate, RatingUpdate


def get_user_rating(db: Session, user_id: int, movie_id: int) -> Optional[Rating]:
    """获取用户对某电影的评分"""
    return db.query(Rating).filter(
        Rating.user_id == user_id,
        Rating.movie_id == movie_id
    ).first()


def get_user_ratings(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Rating]:
    """获取用户的所有评分记录"""
    return db.query(Rating).filter(
        Rating.user_id == user_id
    ).options(
        joinedload(Rating.movie)
    ).order_by(
        desc(Rating.updated_at)
    ).offset(skip).limit(limit).all()


def create_rating(
    db: Session, 
    rating: RatingCreate, 
    user_id: int
) -> Rating:
    """创建新的评分记录"""
    db_rating = Rating(
        user_id=user_id,
        movie_id=rating.movie_id,
        rating=rating.rating
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


def update_rating(
    db: Session, 
    db_rating: Rating, 
    rating_update: RatingUpdate
) -> Rating:
    """更新评分"""
    db_rating.rating = rating_update.rating
    db_rating.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_rating)
    return db_rating


def delete_rating(db: Session, db_rating: Rating) -> None:
    """删除评分"""
    db.delete(db_rating)
    db.commit()


def get_movie_ratings_count(db: Session, movie_id: int) -> int:
    """获取电影的评分数量"""
    return db.query(Rating).filter(Rating.movie_id == movie_id).count()


def get_movie_average_rating(db: Session, movie_id: int) -> Optional[float]:
    """计算电影的平均评分"""
    from sqlalchemy import func
    
    result = db.query(func.avg(Rating.rating)).filter(
        Rating.movie_id == movie_id
    ).scalar()
    
    return round(result, 1) if result else None


def update_movie_rating_stats(db: Session, movie_id: int) -> None:
    """更新电影的评分统计信息"""
    avg_rating = get_movie_average_rating(db, movie_id)
    rating_count = get_movie_ratings_count(db, movie_id)
    
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        movie.avg_rate = avg_rating if avg_rating else 0.0
        movie.vote = rating_count
        db.commit()
