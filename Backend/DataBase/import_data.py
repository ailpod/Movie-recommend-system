#!/usr/bin/env python3
"""
电影数据导入脚本
从 tmdb_1000_movies.json 导入电影数据到数据库中
过滤掉 vote 小于 1000 的电影
"""

import json
import sys
import os
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.models import Base, Movie


def load_movies_data(file_path: str) -> List[Dict[str, Any]]:
    """从JSON文件加载电影数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载 {len(data)} 部电影的数据")
        return data
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"错误: JSON文件格式错误 {file_path}")
        return []


def filter_movies_by_vote(movies: List[Dict[str, Any]], min_vote: int = 1000) -> List[Dict[str, Any]]:
    """根据投票数过滤电影"""
    filtered_movies = [movie for movie in movies if movie.get('vote', 0) >= min_vote]
    print(f"过滤前: {len(movies)} 部电影")
    print(f"过滤后: {len(filtered_movies)} 部电影 (vote >= {min_vote})")
    return filtered_movies


def process_poster_path(poster_path: str) -> str:
    """处理海报路径，确保是完整的URL"""
    if not poster_path:
        return ""
    
    # 如果已经是完整的URL，直接返回
    if poster_path.startswith(('http://', 'https://')):
        return poster_path
    
    # 如果是相对路径，添加TMDB基础URL
    if poster_path.startswith('/'):
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    
    return poster_path


def convert_to_movie_model(movie_data: Dict[str, Any]) -> Movie:
    """将JSON数据转换为Movie模型对象"""
    # 处理genres列表，转换为逗号分隔的字符串
    genres_str = ""
    if movie_data.get('genres'):
        if isinstance(movie_data['genres'], list):
            genres_str = ",".join(movie_data['genres'])
        else:
            genres_str = str(movie_data['genres'])
    
    # 处理actors列表，转换为逗号分隔的字符串
    actors_str = ""
    if movie_data.get('actors'):
        if isinstance(movie_data['actors'], list):
            actors_str = ",".join(movie_data['actors'])
        else:
            actors_str = str(movie_data['actors'])
    
    # 处理keywords列表，转换为逗号分隔的字符串
    keywords_str = ""
    if movie_data.get('keywords'):
        if isinstance(movie_data['keywords'], list):
            # 如果是字典列表，提取name字段
            if movie_data['keywords'] and isinstance(movie_data['keywords'][0], dict):
                keywords_str = ",".join([kw.get('name', '') for kw in movie_data['keywords'] if kw.get('name')])
            else:
                keywords_str = ",".join(movie_data['keywords'])
        else:
            keywords_str = str(movie_data['keywords'])
    
    # 处理poster_path
    poster_path = process_poster_path(movie_data.get('poster_path', ''))
    
    return Movie(
        id=movie_data.get('id'),
        title=movie_data.get('title', ''),
        description=movie_data.get('description', ''),
        poster_path=poster_path,
        avg_rate=float(movie_data.get('avg_rate', 0.0)),
        genres=genres_str,
        release_year=movie_data.get('release_year'),
        director=movie_data.get('director', ''),
        actors=actors_str,
        vote=movie_data.get('vote', 0),
        keyword=keywords_str
    )


def import_movies_to_database(movies_data: List[Dict[str, Any]]) -> bool:
    """将电影数据导入数据库"""
    try:
        # 创建数据库表（如果不存在）
        Base.metadata.create_all(bind=engine)
        
        db: Session = SessionLocal()
        
        # 统计信息
        inserted_count = 0
        updated_count = 0
        error_count = 0
        
        for movie_data in movies_data:
            try:
                movie_id = movie_data.get('id')
                if not movie_id:
                    print(f"跳过没有ID的电影: {movie_data.get('title', 'Unknown')}")
                    error_count += 1
                    continue
                
                # 检查电影是否已存在
                existing_movie = db.query(Movie).filter(Movie.id == movie_id).first()
                
                if existing_movie:
                    # 更新现有电影
                    movie_obj = convert_to_movie_model(movie_data)
                    for key, value in movie_obj.__dict__.items():
                        if not key.startswith('_'):
                            setattr(existing_movie, key, value)
                    updated_count += 1
                    print(f"更新电影: {movie_data.get('title', 'Unknown')} (ID: {movie_id})")
                else:
                    # 插入新电影
                    movie_obj = convert_to_movie_model(movie_data)
                    db.add(movie_obj)
                    inserted_count += 1
                    print(f"插入电影: {movie_data.get('title', 'Unknown')} (ID: {movie_id})")
                
                # 每10条记录提交一次
                if (inserted_count + updated_count) % 10 == 0:
                    try:
                        db.commit()
                        print(f"已处理 {inserted_count + updated_count} 部电影...")
                    except Exception as commit_error:
                        print(f"提交时出错: {commit_error}")
                        db.rollback()
                        # 重新开始会话
                        db.close()
                        db = SessionLocal()
                    
            except Exception as e:
                print(f"处理电影时出错 {movie_data.get('title', 'Unknown')}: {str(e)}")
                error_count += 1
                try:
                    db.rollback()
                    # 重新开始会话
                    db.close()
                    db = SessionLocal()
                except:
                    pass
                continue
        
        # 最终提交
        try:
            db.commit()
            print(f"\n导入完成!")
            print(f"插入新电影: {inserted_count} 部")
            print(f"更新电影: {updated_count} 部")
            print(f"错误: {error_count} 个")
        except Exception as final_error:
            print(f"最终提交时出错: {final_error}")
            db.rollback()
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"数据库操作错误: {str(e)}")
        return False


def main():
    """主函数"""
    print("开始导入电影数据...")
    
    # JSON文件路径 - static 文件夹在 Backend 目录下
    json_file_path = os.path.join(backend_dir, "static", "tmdb_1000_movies.json")
    
    # 加载电影数据
    movies_data = load_movies_data(json_file_path)
    if not movies_data:
        print("没有加载到电影数据，退出...")
        return
    
    # 过滤投票数小于1000的电影
    filtered_movies = filter_movies_by_vote(movies_data, min_vote=1000)
    if not filtered_movies:
        print("过滤后没有符合条件的电影，退出...")
        return
    
    # 导入到数据库
    success = import_movies_to_database(filtered_movies)
    
    if success:
        print("✅ 电影数据导入成功!")
    else:
        print("❌ 电影数据导入失败!")


if __name__ == "__main__":
    main()
