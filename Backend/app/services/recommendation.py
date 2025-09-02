# 推荐算法服务
from typing import List
from sqlalchemy.orm import Session

from ..models import models
from ..crud import movie_crud
from .recommendation_utils import get_movie_recommendations, is_recommendation_available

class RecommendationService:
    """电影推荐服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[models.Movie]:
        """
        获取用户个性化推荐
        
        TODO: 实现推荐算法
        - 基于用户收藏历史的协同过滤
        - 基于电影内容的推荐
        - 混合推荐算法
        
        目前返回评分最高的电影作为占位
        """
        # 占位实现：返回评分最高的电影
        movies = self.db.query(models.Movie).filter(
            models.Movie.rating.isnot(None)
        ).order_by(
            models.Movie.rating.desc()
        ).limit(limit).all()
        
        return movies
    
    def get_similar_movies(self, movie_id: int, limit: int = 5) -> List[models.Movie]:
        """
        获取相似电影推荐
        
        使用训练好的相似度模型进行推荐
        """
        target_movie = movie_crud.get_movie(self.db, movie_id)
        if not target_movie:
            return []
        
        # 如果推荐模型可用，使用基于内容的推荐
        if is_recommendation_available():
            try:
                # 使用电影标题获取推荐
                recommendations = get_movie_recommendations(target_movie.title, limit)
                
                if recommendations:
                    # 根据推荐的电影标题从数据库获取完整信息
                    recommended_movies = []
                    for title, similarity_score in recommendations:
                        # 在数据库中查找推荐的电影
                        movie = self.db.query(models.Movie).filter(
                            models.Movie.title == title
                        ).first()
                        
                        if movie:
                            # 添加相似度分数作为额外信息（可选）
                            movie.similarity_score = similarity_score
                            recommended_movies.append(movie)
                    
                    return recommended_movies[:limit]
                    
            except Exception as e:
                print(f"推荐模型调用失败: {e}")
        
        # 降级方案：基于类型的简单推荐
        if not target_movie.genres:
            return []
        
        similar_movies = self.db.query(models.Movie).filter(
            models.Movie.genres.contains(target_movie.genres),
            models.Movie.id != movie_id
        ).limit(limit).all()
        
        return similar_movies
    
    def get_trending_movies(self, limit: int = 10) -> List[models.Movie]:
        """
        获取热门趋势电影
        
        TODO: 实现基于时间的热门度算法
        - 近期收藏数量
        - 评分趋势
        - 观看热度
        
        目前返回最新添加的高分电影作为占位
        """
        movies = self.db.query(models.Movie).filter(
            models.Movie.rating >= 7.0
        ).order_by(
            models.Movie.created_at.desc()
        ).limit(limit).all()
        
        return movies
