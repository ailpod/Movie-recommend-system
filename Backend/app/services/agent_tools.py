"""
AI Agent 工具函数集
为 DeepSeek AI 提供可调用的工具函数，连接现有数据库功能
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
import json

from ..models.models import Movie, Favorite, Rating, User
from ..services.recommendation import RecommendationService


async def search_movies(
    db: Session,
    query: Optional[str] = None,
    genre: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    根据关键词、类型或年份搜索电影库
    
    Args:
        db: 数据库会话
        query: 搜索关键词（标题、概述）
        genre: 电影类型
        year_start: 起始年份
        year_end: 结束年份
        limit: 返回数量限制
    
    Returns:
        电影列表，包含标题、评分、概述等信息
    """
    try:
        # 构建基础查询
        db_query = db.query(Movie)
        
        # 关键词搜索
        if query:
            search_filter = or_(
                Movie.title.ilike(f"%{query}%"),
                Movie.description.ilike(f"%{query}%")
            )
            db_query = db_query.filter(search_filter)
        
        # 类型筛选
        if genre:
            db_query = db_query.filter(Movie.genres.ilike(f"%{genre}%"))
        
        # 年份筛选
        if year_start:
            db_query = db_query.filter(Movie.release_year >= year_start)
        if year_end:
            db_query = db_query.filter(Movie.release_year <= year_end)
        
        # 按评分排序
        db_query = db_query.order_by(Movie.avg_rate.desc())
        
        # 限制数量
        movies = db_query.limit(limit).all()
        
        # 格式化结果
        results = []
        for movie in movies:
            results.append({
                "id": movie.id,
                "title": movie.title,
                "description": movie.description[:200] if movie.description else "",
                "genres": movie.genres,
                "release_year": movie.release_year or 0,
                "avg_rate": float(movie.avg_rate) if movie.avg_rate else 0,
                "vote": movie.vote or 0,
                "poster_path": movie.poster_path
            })
        
        return results
    except Exception as e:
        print(f"搜索电影错误: {str(e)}")
        return []


async def get_user_favorites(
    db: Session,
    user_id: int,
    limit: int = 20
) -> Dict[str, Any]:
    """
    获取用户收藏的电影列表以分析口味
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        limit: 返回数量限制
    
    Returns:
        用户收藏信息，包含电影列表和分析
    """
    try:
        # 获取用户收藏
        favorites = db.query(Favorite).filter(
            Favorite.user_id == user_id
        ).limit(limit).all()
        
        if not favorites:
            return {
                "total_favorites": 0,
                "movies": [],
                "favorite_genres": [],
                "average_rating_preference": 0,
                "analysis": "用户还没有收藏任何电影"
            }
        
        # 获取电影详情
        movie_ids = [fav.movie_id for fav in favorites]
        movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
        
        # 分析用户口味
        genres_count = {}
        total_rating = 0
        movie_list = []
        
        for movie in movies:
            if movie.genres:
                for genre in movie.genres.split(','):
                    genre = genre.strip()
                    genres_count[genre] = genres_count.get(genre, 0) + 1
            
            if movie.avg_rate:
                total_rating += movie.avg_rate
            
            movie_list.append({
                "id": movie.id,
                "title": movie.title,
                "genres": movie.genres,
                "avg_rate": float(movie.avg_rate) if movie.avg_rate else 0,
                "release_year": movie.release_year or 0
            })
        
        # 排序找出最喜欢的类型
        favorite_genres = sorted(
            genres_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        avg_rating = total_rating / len(movies) if movies else 0
        
        return {
            "total_favorites": len(movie_list),
            "movies": movie_list,
            "favorite_genres": [g[0] for g in favorite_genres],
            "average_rating_preference": round(avg_rating, 2),
            "analysis": f"用户收藏了 {len(movie_list)} 部电影，主要喜欢 {', '.join([g[0] for g in favorite_genres[:2]])} 类型"
        }
    except Exception as e:
        print(f"获取用户收藏错误: {str(e)}")
        return {
            "total_favorites": 0,
            "movies": [],
            "favorite_genres": [],
            "average_rating_preference": 0,
            "analysis": "无法获取用户收藏信息"
        }


async def get_user_ratings(
    db: Session,
    user_id: int,
    limit: int = 20
) -> Dict[str, Any]:
    """
    获取用户评分历史以了解喜好
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        limit: 返回数量限制
    
    Returns:
        用户评分信息和分析
    """
    try:
        # 获取用户评分
        ratings = db.query(Rating).filter(
            Rating.user_id == user_id
        ).order_by(Rating.rating.desc()).limit(limit).all()
        
        if not ratings:
            return {
                "total_ratings": 0,
                "high_rated_movies": [],
                "low_rated_movies": [],
                "analysis": "用户还没有评分记录"
            }
        
        # 获取电影详情
        movie_ids = [r.movie_id for r in ratings]
        movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
        movie_dict = {m.id: m for m in movies}
        
        high_rated_movies = []
        low_rated_movies = []
        
        for rating in ratings:
            movie = movie_dict.get(rating.movie_id)
            if not movie:
                continue
            
            movie_info = {
                "id": movie.id,
                "title": movie.title,
                "user_rating": rating.rating,
                "genres": movie.genres
            }
            
            if rating.rating >= 4.0:
                high_rated_movies.append(movie_info)
            elif rating.rating <= 2.0:
                low_rated_movies.append(movie_info)
        
        return {
            "total_ratings": len(ratings),
            "high_rated_movies": high_rated_movies[:5],
            "low_rated_movies": low_rated_movies[:5],
            "analysis": f"用户评分了 {len(ratings)} 部电影，其中高分 {len(high_rated_movies)} 部，低分 {len(low_rated_movies)} 部"
        }
    except Exception as e:
        print(f"获取用户评分错误: {str(e)}")
        return {
            "total_ratings": 0,
            "high_rated_movies": [],
            "low_rated_movies": [],
            "analysis": "无法获取用户评分信息"
        }


async def get_recommendations_for_user(
    db: Session,
    user_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    基于用户历史生成个性化推荐
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        limit: 返回数量限制
    
    Returns:
        推荐电影列表
    """
    try:
        # 使用现有的推荐服务
        rec_service = RecommendationService(db)
        recommended_movies = rec_service.get_user_recommendations(user_id, limit)
        
        results = []
        for movie in recommended_movies:
            results.append({
                "id": movie.id,
                "title": movie.title,
                "description": movie.description[:200] if movie.description else "",
                "genres": movie.genres,
                "avg_rate": float(movie.avg_rate) if movie.avg_rate else 0,
                "release_year": movie.release_year or 0,
                "reason": "基于您的观看历史和评分"
            })
        
        return results
    except Exception as e:
        print(f"获取推荐错误: {str(e)}")
        return []


async def get_similar_movies(
    db: Session,
    movie_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    获取相似电影
    
    Args:
        db: 数据库会话
        movie_id: 电影ID
        limit: 返回数量限制
    
    Returns:
        相似电影列表
    """
    try:
        # 获取目标电影
        target_movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not target_movie:
            return []
        
        # 使用推荐服务获取相似电影
        rec_service = RecommendationService(db)
        similar_movies = rec_service.get_similar_movies(movie_id, limit)
        
        results = []
        for movie in similar_movies:
            results.append({
                "id": movie.id,
                "title": movie.title,
                "description": movie.description[:200] if movie.description else "",
                "genres": movie.genres,
                "avg_rate": float(movie.avg_rate) if movie.avg_rate else 0,
                "release_year": movie.release_year or 0,
                "similarity_reason": f"与《{target_movie.title}》类型相似"
            })
        
        return results
    except Exception as e:
        print(f"获取相似电影错误: {str(e)}")
        return []


async def get_movie_details(
    db: Session,
    movie_id: int
) -> Optional[Dict[str, Any]]:
    """
    获取电影详细信息
    
    Args:
        db: 数据库会话
        movie_id: 电影ID
    
    Returns:
        电影详细信息
    """
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return None
        
        return {
            "id": movie.id,
            "title": movie.title,
            "description": movie.description,
            "genres": movie.genres,
            "release_year": movie.release_year or 0,
            "avg_rate": float(movie.avg_rate) if movie.avg_rate else 0,
            "vote": movie.vote or 0,
            "director": movie.director,
            "actors": movie.actors,
            "poster_path": movie.poster_path
        }
    except Exception as e:
        print(f"获取电影详情错误: {str(e)}")
        return None
