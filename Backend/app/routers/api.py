# 额外的API路由 - 处理前端特殊路径
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..crud import movie_crud
from ..schemas.schemas import Movie

router = APIRouter(tags=["通用API"])

@router.get("/movie/{movie_id}", response_model=Movie)
async def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """获取电影详情（兼容前端路径）"""
    movie = movie_crud.get_movie(db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.get("/search", response_model=List[Movie])
async def search_movies_global(
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    db: Session = Depends(get_db)
):
    """全局搜索电影（兼容前端路径）"""
    skip = (page - 1) * 20
    limit = 20
    return movie_crud.search_movies(db, title=q, skip=skip, limit=limit)

@router.get("/genres", response_model=List[str])
async def get_all_genres(db: Session = Depends(get_db)):
    """获取所有电影类型（兼容前端路径）"""
    return movie_crud.get_all_genres(db)
