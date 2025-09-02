# DB CRUD 封装 - 简化版本
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models import models
from ..schemas.schemas import UserCreate, MovieCreate
from ..core.security import get_password_hash, verify_password

# 用户 CRUD 操作
class UserCRUD:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> models.User:
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            age=getattr(user, 'age', None),
            gender=getattr(user, 'gender', None),
            like_genres=getattr(user, 'like_genres', None)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: dict) -> Optional[models.User]:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return None
        
        # 更新允许的字段
        allowed_fields = ['username', 'email', 'age', 'gender', 'like_genres']
        for field, value in user_data.items():
            if field in allowed_fields and hasattr(db_user, field):
                setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
        user = UserCRUD.get_user_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

# 电影 CRUD 操作
class MovieCRUD:
    @staticmethod
    def get_movie(db: Session, movie_id: int) -> Optional[models.Movie]:
        return db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    
    @staticmethod
    def get_movies(db: Session, skip: int = 0, limit: int = 100) -> List[models.Movie]:
        return db.query(models.Movie).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_movies_with_filters(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        sort_by: str = "popular",
        genre: Optional[str] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_min: Optional[int] = None,
        vote_max: Optional[int] = None
    ) -> List[models.Movie]:
        """获取带筛选和排序的电影列表"""
        query = db.query(models.Movie)
        
        # 应用筛选条件
        if genre:
            query = query.filter(models.Movie.genres.contains(genre))
        
        if year_start:
            query = query.filter(models.Movie.release_year >= year_start)
        
        if year_end:
            query = query.filter(models.Movie.release_year <= year_end)
        
        if rating_min:
            query = query.filter(models.Movie.avg_rate >= rating_min)
        
        if rating_max:
            query = query.filter(models.Movie.avg_rate <= rating_max)
        
        if vote_min:
            query = query.filter(models.Movie.vote >= vote_min)
        
        if vote_max:
            query = query.filter(models.Movie.vote <= vote_max)
        
        # 应用排序
        if sort_by == "popular":
            # 热门：投票数大于10000且评分大于7，按投票数排序
            query = query.filter(
                and_(
                    models.Movie.vote > 10000,
                    models.Movie.avg_rate > 7.0
                )
            ).order_by(models.Movie.vote.desc())
        elif sort_by == "top_rated":
            # 高分：投票数大于5000，按评分排序
            query = query.filter(models.Movie.vote > 5000).order_by(models.Movie.avg_rate.desc())
        elif sort_by == "latest":
            # 最新：综合时间和评分
            query = query.filter(
                and_(
                    models.Movie.release_year.isnot(None),
                    models.Movie.avg_rate.isnot(None)
                )
            ).order_by(
                (
                    ((models.Movie.release_year - 1900) / 125.0) * 0.8 +
                    ((models.Movie.avg_rate - 1.0) / 9.0) * 0.2
                ).desc()
            )
        elif sort_by == "vote":
            query = query.order_by(models.Movie.vote.desc())
        elif sort_by == "rating":
            query = query.order_by(models.Movie.avg_rate.desc())
        elif sort_by == "title":
            query = query.order_by(models.Movie.title)
        elif sort_by == "year":
            query = query.order_by(models.Movie.release_year.desc())
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def search_movies(db: Session, title: str = None, genre: str = None, skip: int = 0, limit: int = 100) -> List[models.Movie]:
        query = db.query(models.Movie)
        
        if title:
            query = query.filter(models.Movie.title.contains(title))
        
        if genre:
            query = query.filter(models.Movie.genres.contains(genre))
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_movies_by_genre(db: Session, genre: str, skip: int = 0, limit: int = 100) -> List[models.Movie]:
        return db.query(models.Movie).filter(
            models.Movie.genres.contains(genre)
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_genres(db: Session) -> List[str]:
        """获取所有电影类型"""
        movies = db.query(models.Movie).filter(models.Movie.genres.isnot(None)).all()
        genres_set = set()
        for movie in movies:
            if movie.genres:
                # 分割逗号分隔的类型字符串
                genre_list = [g.strip() for g in movie.genres.split(',') if g.strip()]
                genres_set.update(genre_list)
        return sorted(list(genres_set))
    
    @staticmethod
    def get_top_rated_movies(db: Session, skip: int = 0, limit: int = 100) -> List[models.Movie]:
        """获取高分精选电影 - 投票数大于5000，按评分排序"""
        return db.query(models.Movie).filter(
            and_(
                models.Movie.avg_rate.isnot(None),
                models.Movie.vote > 5000
            )
        ).order_by(models.Movie.avg_rate.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_latest_movies(db: Session, skip: int = 0, limit: int = 100) -> List[models.Movie]:
        """获取最新上映电影 - 以时间最近为主(80%)，评分为辅(20%)"""
        from sqlalchemy import func, case
        
        # 计算综合评分：时间最近权重80% + 评分权重20%
        # 为了平衡两个指标，我们对年份和评分都进行归一化处理
        return db.query(models.Movie).filter(
            and_(
                models.Movie.release_year.isnot(None),
                models.Movie.avg_rate.isnot(None)
            )
        ).order_by(
            # 综合评分公式：(归一化年份 * 0.8) + (归一化评分 * 0.2)
            (
                ((models.Movie.release_year - 1900) / 125.0) * 0.8 +  # 时间最近权重80%，年份范围1900-2025
                ((models.Movie.avg_rate - 1.0) / 9.0) * 0.2  # 评分权重20%，评分范围1-10
            ).desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_popular_movies(db: Session, skip: int = 0, limit: int = 100) -> List[models.Movie]:
        """获取热门电影 - 投票数大于10000且评分大于7"""
        return db.query(models.Movie).filter(
            and_(
                models.Movie.vote > 10000,
                models.Movie.avg_rate > 7.0
            )
        ).order_by(models.Movie.vote.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_movie(db: Session, movie: "MovieCreate") -> models.Movie:
        """创建新电影"""
        db_movie = models.Movie(**movie.dict())
        db.add(db_movie)
        db.commit()
        db.refresh(db_movie)
        return db_movie

# 创建 CRUD 实例
user_crud = UserCRUD()
movie_crud = MovieCRUD()
