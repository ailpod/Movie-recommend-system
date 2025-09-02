# 用户相关路由
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.dependencies import get_current_active_user
from ..crud import user_crud, movie_crud
from ..crud.crud_user_actions import get_user_favorites, get_user_history
from ..models import models
from ..schemas.schemas import User, UserUpdate, Movie
from ..services import recommendation_utils

router = APIRouter(prefix="/users", tags=["用户"])

@router.get("/me", response_model=User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=User)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 更新用户信息
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


# --- 👇 在文件末尾添加这个新的API端点 👇 ---

@router.get("/me/recommendations", response_model=List[Movie])
def get_my_personalized_recommendations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user) # 确保是已登录用户
):
    """
    为当前登录用户获取个性化推荐。
    糅合收藏、历史和个人偏好。
    """
    print(f"[DEBUG] 用户 {current_user.username} 请求个性化推荐")
    
    # 获取推荐模型
    global_models = recommendation_utils.get_recommendation_models()
    
    # 检查模型是否已加载
    if 'cosine_sim' not in global_models or 'all_movies_df' not in global_models:
        print("[DEBUG] 推荐模型未加载")
        raise HTTPException(status_code=503, detail="推荐服务当前不可用。")

    # 1. 从数据库获取用户的行为数据
    favorites = get_user_favorites(db, user_id=current_user.id)
    history = get_user_history(db, user_id=current_user.id)
    
    print(f"[DEBUG] 用户行为数据 - 收藏: {len(favorites)}, 历史: {len(history)}")
    
    # 2. 从数据库获取用户的偏好类型
    # 使用 like_genres 字段，存储为逗号分隔的字符串
    preferred_genres = current_user.like_genres.split(',') if current_user.like_genres else []
    print(f"[DEBUG] 用户偏好类型: {preferred_genres}")

    # 如果用户没有任何行为和偏好，执行冷启动策略（比如返回热门电影）
    if not favorites and not history and not preferred_genres:
        print("[DEBUG] 用户无行为和偏好，返回热门电影")
        return movie_crud.get_popular_movies(db, limit=10)

    # 3. 调用我们新的推荐服务函数
    recommended_titles = recommendation_utils.get_personalized_recommendations_v2(
        favorites=favorites,
        history=history,
        preferred_genres=preferred_genres,
        cosine_sim=global_models['cosine_sim'],
        indices=global_models['indices'],
        all_movies_df=global_models['all_movies_df']
    )

    if not recommended_titles:
        # 如果算法没有返回结果，也可以返回热门电影作为补充
        print("[DEBUG] 推荐算法无结果，返回热门电影")
        return movie_crud.get_popular_movies(db, limit=10)

    # 4. 根据标题列表查询完整的电影信息并返回
    recommended_movies = movie_crud.get_movies_by_titles(db, titles=recommended_titles)
    print(f"[DEBUG] 找到推荐电影: {len(recommended_movies)} 部")
    return recommended_movies
