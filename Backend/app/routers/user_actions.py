# User actions routes - favorites and browsing history
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..core.dependencies import get_db, get_current_user
from ..crud import crud_user_actions

router = APIRouter(
    prefix="/users/me",
    tags=["User Actions"],
    dependencies=[Depends(get_current_user)]  # 保护这些路由
)


# --- 历史记录路由 ---
@router.post("/history/{movie_id}", status_code=status.HTTP_201_CREATED)
def record_browsing_history(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """当用户访问电影详情页时，前端调用此接口"""
    # 检查电影是否存在
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    crud_user_actions.create_or_update_history(
        db=db, user_id=current_user.id, movie_id=movie_id
    )
    return {"message": "History recorded successfully"}


@router.get("/history", response_model=List[schemas.BrowsingHistoryResponse])
def read_user_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取当前用户的浏览历史"""
    history = crud_user_actions.get_user_history(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return history


@router.delete("/history/{movie_id}")
def delete_history_record(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """删除特定的浏览历史记录"""
    # 检查历史记录是否存在
    if not crud_user_actions.get_history_record(db, user_id=current_user.id, movie_id=movie_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found"
        )
    
    crud_user_actions.delete_history_record(
        db=db, user_id=current_user.id, movie_id=movie_id
    )
    return {"message": "History record deleted successfully"}


@router.delete("/history")
def clear_all_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """清空用户所有浏览历史"""
    deleted_count = crud_user_actions.delete_all_user_history(
        db=db, user_id=current_user.id
    )
    return {"message": f"Cleared {deleted_count} history records successfully"}


# --- 收藏路由 ---
@router.post("/favorites/{movie_id}", response_model=schemas.FavoriteResponse)
def add_favorite_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """收藏电影"""
    # 检查电影是否存在
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # 检查是否已收藏
    if crud_user_actions.get_favorite(db, user_id=current_user.id, movie_id=movie_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie already in favorites"
        )
    
    return crud_user_actions.create_favorite(
        db=db, user_id=current_user.id, movie_id=movie_id
    )


@router.delete("/favorites/{movie_id}")
def remove_favorite_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """取消收藏电影"""
    if not crud_user_actions.get_favorite(db, user_id=current_user.id, movie_id=movie_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    crud_user_actions.delete_favorite(
        db=db, user_id=current_user.id, movie_id=movie_id
    )
    return {"message": "Favorite removed successfully"}


@router.get("/favorites", response_model=List[schemas.FavoriteResponse])
def read_user_favorites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取当前用户的收藏列表"""
    favorites = crud_user_actions.get_user_favorites(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return favorites


@router.get("/favorites/{movie_id}/status")
def check_favorite_status(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """检查电影是否已被收藏"""
    is_favorited = crud_user_actions.check_movie_favorited(
        db, user_id=current_user.id, movie_id=movie_id
    )
    return {"is_favorited": is_favorited}
