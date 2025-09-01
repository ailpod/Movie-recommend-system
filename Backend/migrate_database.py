#!/usr/bin/env python3
"""
数据库迁移脚本 - 创建用户和电影表，导入电影数据
Database Migration Script - Create users and movies tables, import movie data
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.models import User, Movie
from app.core.config import get_settings

def create_database():
    """创建数据库和表"""
    settings = get_settings()
    engine = create_engine(settings.database.url, echo=True)
    
    print("🗃️  创建数据库表...")
    Base.metadata.drop_all(bind=engine)  # 删除所有表
    Base.metadata.create_all(bind=engine)  # 重新创建表
    print("✅ 数据库表创建成功!")
    
    return engine

def load_movie_data():
    """加载电影数据"""
    movie_data_path = project_root / "static" / "movie_data_new.json"
    
    if not movie_data_path.exists():
        print(f"❌ 电影数据文件不存在: {movie_data_path}")
        return []
    
    print(f"📁 读取电影数据: {movie_data_path}")
    with open(movie_data_path, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)
    
    # 过滤vote >= 1000的电影
    filtered_movies = [movie for movie in movies_data if movie.get('vote', 0) >= 1000]
    
    print(f"🎬 原始电影数量: {len(movies_data)}")
    print(f"🎯 过滤后电影数量: {len(filtered_movies)} (vote >= 1000)")
    
    return filtered_movies

def import_movies(engine, movies_data):
    """导入电影数据到数据库"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("📥 开始导入电影数据...")
        
        imported_count = 0
        for movie_data in movies_data:
            try:
                movie = Movie(
                    id=movie_data.get('id'),
                    title=movie_data.get('title', ''),
                    description=movie_data.get('description', ''),
                    poster_path=movie_data.get('poster_path', ''),
                    avg_rate=round(float(movie_data.get('avg_rate', 0)), 2),
                    genres=movie_data.get('genres', ''),
                    release_year=movie_data.get('release_year'),
                    director=movie_data.get('director', ''),
                    actors=movie_data.get('actors', ''),
                    vote=int(movie_data.get('vote', 0))
                )
                
                db.add(movie)
                imported_count += 1
                
                # 每100条提交一次
                if imported_count % 100 == 0:
                    db.commit()
                    print(f"  ✓ 已导入 {imported_count} 部电影...")
                    
            except Exception as e:
                print(f"  ❌ 导入电影失败 {movie_data.get('title', 'Unknown')}: {str(e)}")
                db.rollback()
                continue
        
        # 最终提交
        db.commit()
        print(f"✅ 电影数据导入完成! 总计: {imported_count} 部电影")
        
    except Exception as e:
        print(f"❌ 导入电影数据时发生错误: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_user(engine):
    """创建示例用户"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        from app.core.security import get_password_hash
        
        print("👤 创建示例用户...")
        
        # 检查是否已存在用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("  ⚠️  admin用户已存在，跳过创建")
            return
        
        # 创建admin用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            age=25,
            gender="other",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ 示例用户创建成功!")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  邮箱: admin@example.com")
        
    except Exception as e:
        print(f"❌ 创建示例用户失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

def verify_migration(engine):
    """验证迁移结果"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n🔍 验证迁移结果...")
        
        # 检查用户表
        user_count = db.query(User).count()
        print(f"  📊 用户数量: {user_count}")
        
        # 检查电影表
        movie_count = db.query(Movie).count()
        print(f"  📊 电影数量: {movie_count}")
        
        # 显示一些电影信息
        if movie_count > 0:
            top_movies = db.query(Movie).order_by(Movie.avg_rate.desc()).limit(3).all()
            print(f"  🏆 评分最高的电影:")
            for movie in top_movies:
                print(f"    • {movie.title} - 评分: {movie.avg_rate} - 投票: {movie.vote}")
        
        print("✅ 数据库迁移验证完成!")
        
    except Exception as e:
        print(f"❌ 验证迁移结果失败: {str(e)}")
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 50)
    print("🎬 电影推荐系统 - 数据库迁移")
    print("Movie Recommendation System - Database Migration")
    print("=" * 50)
    
    try:
        # 1. 创建数据库
        engine = create_database()
        
        # 2. 加载电影数据
        movies_data = load_movie_data()
        if not movies_data:
            print("❌ 没有电影数据可导入")
            return
        
        # 3. 导入电影数据
        import_movies(engine, movies_data)
        
        # 4. 创建示例用户
        create_sample_user(engine)
        
        # 5. 验证迁移结果
        verify_migration(engine)
        
        print("\n" + "=" * 50)
        print("🎉 数据库迁移完成!")
        print("=" * 50)
        print("\n💡 接下来你可以:")
        print("  1. 启动后端服务: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("  2. 访问API文档: http://localhost:8000/docs")
        print("  3. 使用admin/admin123登录测试")
        
    except Exception as e:
        print(f"\n❌ 数据库迁移失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
