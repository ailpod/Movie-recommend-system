"""评分路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.dependencies import get_db, get_current_user
from ..models.models import User, Movie
from ..schemas.schemas import RatingCreate, RatingUpdate, Rating, RatingResponse
from ..crud import crud_ratings

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("/", response_model=Rating, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建电影评分
    
    - **movie_id**: 电影ID
    - **rating**: 评分（1.0-10.0）
    """
    # 检查电影是否存在
    movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="电影不存在"
        )
    
    # 检查是否已经评分过
    existing_rating = crud_ratings.get_user_rating(
        db, 
        user_id=current_user.id, 
        movie_id=rating.movie_id
    )
    
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经对这部电影评分，请使用更新评分接口"
        )
    
    # 创建评分
    db_rating = crud_ratings.create_rating(db, rating, current_user.id)
    
    # 更新电影的评分统计
    crud_ratings.update_movie_rating_stats(db, rating.movie_id)
    
    return db_rating


@router.put("/{movie_id}", response_model=Rating)
def update_rating(
    movie_id: int,
    rating_update: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新电影评分
    
    - **movie_id**: 电影ID
    - **rating**: 新的评分（1.0-10.0）
    """
    # 获取用户的评分记录
    db_rating = crud_ratings.get_user_rating(
        db, 
        user_id=current_user.id, 
        movie_id=movie_id
    )
    
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评分记录不存在"
        )
    
    # 更新评分
    updated_rating = crud_ratings.update_rating(db, db_rating, rating_update)
    
    # 更新电影的评分统计
    crud_ratings.update_movie_rating_stats(db, movie_id)
    
    return updated_rating


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除电影评分
    
    - **movie_id**: 电影ID
    """
    # 获取用户的评分记录
    db_rating = crud_ratings.get_user_rating(
        db, 
        user_id=current_user.id, 
        movie_id=movie_id
    )
    
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评分记录不存在"
        )
    
    # 删除评分
    crud_ratings.delete_rating(db, db_rating)
    
    # 更新电影的评分统计
    crud_ratings.update_movie_rating_stats(db, movie_id)


@router.get("/movie/{movie_id}", response_model=Rating)
def get_user_movie_rating(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户对某电影的评分
    
    - **movie_id**: 电影ID
    """
    rating = crud_ratings.get_user_rating(
        db, 
        user_id=current_user.id, 
        movie_id=movie_id
    )
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="尚未对该电影评分"
        )
    
    return rating


@router.get("/my-ratings", response_model=List[RatingResponse])
def get_my_ratings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有评分记录
    
    - **skip**: 跳过的记录数（分页）
    - **limit**: 返回的最大记录数（分页）
    """
    ratings = crud_ratings.get_user_ratings(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )
    
    # 构建响应数据
    return [
        {
            "id": rating.id,
            "rating": rating.rating,
            "movie": rating.movie,
            "created_at": rating.created_at,
            "updated_at": rating.updated_at
        }
        for rating in ratings
    ]
