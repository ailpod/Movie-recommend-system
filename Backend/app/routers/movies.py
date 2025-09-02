# 电影列表/详情/推荐路由
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json

from ..core.database import get_db
from ..core.dependencies import get_current_active_user, get_current_user_optional
from ..crud import movie_crud
from ..crud.crud_user_actions import check_movie_favorited
from ..services.recommendation import RecommendationService
from ..models import models
from ..schemas.schemas import Movie, MovieCreate


class UTF8JSONResponse(JSONResponse):
    """确保UTF-8编码的JSON响应"""
    media_type = "application/json; charset=utf-8"
    
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


router = APIRouter(prefix="/movies", tags=["电影"])

@router.get("/", response_model=List[Movie])
async def get_movies(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    sort_by: Optional[str] = Query("popular", description="排序方式: popular, top_rated, latest, vote, title"),
    genre: Optional[str] = Query(None, description="电影类型筛选"),
    year_start: Optional[int] = Query(None, description="起始年份"),
    year_end: Optional[int] = Query(None, description="结束年份"),
    rating_min: Optional[float] = Query(None, description="最低评分"),
    rating_max: Optional[float] = Query(None, description="最高评分"),
    vote_min: Optional[int] = Query(None, description="最低投票数"),
    vote_max: Optional[int] = Query(None, description="最高投票数"),
    db: Session = Depends(get_db)
):
    """获取电影列表，支持多种筛选和排序"""
    return movie_crud.get_movies_with_filters(
        db, 
        skip=skip, 
        limit=limit,
        sort_by=sort_by,
        genre=genre,
        year_start=year_start,
        year_end=year_end,
        rating_min=rating_min,
        rating_max=rating_max,
        vote_min=vote_min,
        vote_max=vote_max
    )

@router.get("/popular", response_model=List[Movie])
async def get_popular_movies(
    page: int = Query(1, ge=1, description="页码"),
    db: Session = Depends(get_db)
):
    """获取热门电影 - 投票数大于10000且评分大于7"""
    skip = (page - 1) * 20
    limit = 20
    return movie_crud.get_popular_movies(db, skip=skip, limit=limit)

@router.get("/top-rated", response_model=List[Movie])
async def get_top_rated_movies(
    page: int = Query(1, ge=1, description="页码"),
    db: Session = Depends(get_db)
):
    """获取高分电影"""
    skip = (page - 1) * 20
    limit = 20
    return movie_crud.get_top_rated_movies(db, skip=skip, limit=limit)

@router.get("/latest", response_model=List[Movie])
async def get_latest_movies(
    page: int = Query(1, ge=1, description="页码"),
    db: Session = Depends(get_db)
):
    """获取最新电影"""
    skip = (page - 1) * 20
    limit = 20
    return movie_crud.get_latest_movies(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[Movie])
async def search_movies(
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    db: Session = Depends(get_db)
):
    """搜索电影"""
    skip = (page - 1) * 20
    limit = 20
    return movie_crud.search_movies(db, title=q, skip=skip, limit=limit)

@router.get("/genre/{genre}", response_model=List[Movie])
async def get_movies_by_genre(
    genre: str,
    page: int = Query(1, ge=1, description="页码"),
    db: Session = Depends(get_db)
):
    """按类型获取电影"""
    skip = (page - 1) * 20
    limit = 20
    return movie_crud.get_movies_by_genre(db, genre=genre, skip=skip, limit=limit)

@router.get("/genres", response_model=List[str])
async def get_genres(db: Session = Depends(get_db)):
    """获取所有电影类型"""
    return movie_crud.get_all_genres(db)

@router.get("/recommendations/for-me", response_model=List[Movie])
async def get_user_recommendations(
    limit: int = Query(10, ge=1, le=50, description="推荐电影数量"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取个性化推荐"""
    recommendation_service = RecommendationService(db)
    return recommendation_service.get_user_recommendations(current_user.id, limit)

@router.get("/{movie_id}", response_model=Movie)
async def get_movie(
    movie_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    """获取电影详情"""
    movie = movie_crud.get_movie(db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # 如果用户已登录，检查收藏状态
    if current_user:
        movie.is_favorited = check_movie_favorited(db, current_user.id, movie_id)
    else:
        movie.is_favorited = False
    
    return movie

@router.get("/{movie_id}/recommendations", response_model=List[Movie])
async def get_movie_recommendations(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50, description="推荐电影数量"),
    db: Session = Depends(get_db)
):
    """获取相似电影推荐"""
    # 先检查电影是否存在
    movie = movie_crud.get_movie(db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    recommendation_service = RecommendationService(db)
    return recommendation_service.get_similar_movies(movie_id, limit)

@router.post("/", response_model=Movie)
async def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """创建新电影（管理员功能）"""
    return movie_crud.create_movie(db=db, movie=movie)
