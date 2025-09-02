"""
推荐算法工具模块
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional

# 全局变量存储推荐模型，由main.py设置
_recommendation_models = {}

def set_recommendation_models(models: dict):
    """设置推荐模型（由main.py调用）"""
    global _recommendation_models
    _recommendation_models = models

def get_recommendation_models():
    """获取推荐模型"""
    return _recommendation_models


def get_movie_recommendations(movie_title: str, num_recommendations: int = 10) -> List[Tuple[str, float]]:
    """
    基于电影标题获取推荐
    
    Args:
        movie_title: 电影标题
        num_recommendations: 推荐数量
        
    Returns:
        推荐电影列表，每个元素是(电影标题, 相似度分数)的元组
    """
    models = get_recommendation_models()
    
    if 'cosine_sim' not in models or 'indices' not in models:
        print("警告：推荐模型未加载")
        return []
    
    cosine_sim = models['cosine_sim']
    indices = models['indices']
    
    # 检查电影是否存在
    if movie_title not in indices:
        print(f"电影 '{movie_title}' 不在索引中")
        return []
    
    # 获取电影索引
    idx = indices[movie_title]
    
    # 获取所有电影的相似度分数
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # 按相似度分数排序
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # 获取前N个推荐（跳过自己）
    sim_scores = sim_scores[1:num_recommendations + 1]
    
    # 获取电影标题和分数
    movie_indices_list = [i[0] for i in sim_scores]
    similarity_scores = [i[1] for i in sim_scores]
    
    # 根据索引获取电影标题
    title_to_idx = {title: idx for title, idx in indices.items()}
    idx_to_title = {idx: title for title, idx in title_to_idx.items()}
    
    recommendations = []
    for movie_idx, score in zip(movie_indices_list, similarity_scores):
        if movie_idx in idx_to_title:
            recommendations.append((idx_to_title[movie_idx], float(score)))
    
    return recommendations


def get_movies_by_similarity_threshold(movie_title: str, threshold: float = 0.1) -> List[Tuple[str, float]]:
    """
    获取相似度超过阈值的所有电影
    
    Args:
        movie_title: 电影标题
        threshold: 相似度阈值
        
    Returns:
        符合条件的电影列表
    """
    models = get_recommendation_models()
    
    if 'cosine_sim' not in models or 'indices' not in models:
        return []
    
    cosine_sim = models['cosine_sim']
    indices = models['indices']
    
    if movie_title not in indices:
        return []
    
    idx = indices[movie_title]
    sim_scores = cosine_sim[idx]
    
    # 获取相似度超过阈值的电影
    title_to_idx = {title: idx for title, idx in indices.items()}
    idx_to_title = {idx: title for title, idx in title_to_idx.items()}
    
    recommendations = []
    for movie_idx, score in enumerate(sim_scores):
        if score >= threshold and movie_idx != idx:  # 排除自己
            if movie_idx in idx_to_title:
                recommendations.append((idx_to_title[movie_idx], float(score)))
    
    # 按相似度排序
    recommendations.sort(key=lambda x: x[1], reverse=True)
    
    return recommendations


def is_recommendation_available() -> bool:
    """检查推荐功能是否可用"""
    models = get_recommendation_models()
    return 'cosine_sim' in models and 'indices' in models


def get_model_info() -> dict:
    """获取模型信息"""
    models = get_recommendation_models()
    
    info = {
        "available": is_recommendation_available(),
        "models_loaded": list(models.keys())
    }
    
    if 'cosine_sim' in models:
        info["similarity_matrix_shape"] = models['cosine_sim'].shape
        
    if 'indices' in models:
        info["total_movies"] = len(models['indices'])
        info["sample_movies"] = list(models['indices'].keys())[:5]
    
    return info


def get_personalized_recommendations_v2(
    favorites: list, 
    history: list,
    preferred_genres: list, 
    cosine_sim, 
    indices: pd.Series,
    all_movies_df: pd.DataFrame,
    top_k: int = 10
):
    """
    个性化推荐算法 v2.0
    权重分配：用户偏好类型 60%，收藏 30%，浏览历史 10%
    """
    import random
    import time
    
    # 添加时间因子确保动态性
    current_hour = int(time.time()) // 3600
    random.seed(current_hour)
    
    print(f"[DEBUG] 推荐算法启动")
    print(f"  - 收藏数量: {len(favorites)}")
    print(f"  - 历史数量: {len(history)}")
    print(f"  - 偏好类型: {preferred_genres}")
    
    # 获取所有电影的标题列表
    if isinstance(indices, pd.Series):
        all_movie_titles = indices.index.tolist()
    else:
        all_movie_titles = list(indices.keys())
    
    print(f"  - 总电影数量: {len(all_movie_titles)}")
    
    # 初始化每部电影的综合得分
    movie_scores = {}
    
    # 收集用户已看过的电影
    seen_titles = set()
    for favorite in favorites:
        seen_titles.add(favorite.movie.title)
    for history_item in history:
        seen_titles.add(history_item.movie.title)
    
    print(f"  - 已看过电影数量: {len(seen_titles)}")
    
    # 遍历所有电影进行评分
    for movie_idx, movie_title in enumerate(all_movie_titles):
        if movie_title in seen_titles:
            continue  # 跳过已看过的电影
            
        total_score = 0.0
        
        # 1. 计算偏好类型匹配分数 (权重60%)
        genre_score = 0.0
        if preferred_genres:
            movie_row = all_movies_df[all_movies_df['title'] == movie_title]
            if not movie_row.empty:
                movie_genres_data = movie_row.iloc[0].get('genres', [])
                
                # genres 字段是一个列表
                if isinstance(movie_genres_data, list):
                    movie_genres = [g.lower() for g in movie_genres_data]
                elif isinstance(movie_genres_data, str):
                    # 如果是字符串，按逗号分割
                    movie_genres = [g.strip().lower() for g in movie_genres_data.split(',') if g.strip()]
                else:
                    movie_genres = []
                
                # 计算类型匹配度
                matches = 0
                for preferred_genre in preferred_genres:
                    preferred_lower = preferred_genre.strip().lower()
                    for movie_genre in movie_genres:
                        # 更宽松的匹配逻辑
                        if (preferred_lower in movie_genre or 
                            movie_genre in preferred_lower or
                            # 特殊处理一些常见的类型映射
                            (preferred_lower == 'animation' and 'animated' in movie_genre) or
                            (preferred_lower == '动画' and ('animation' in movie_genre or 'animated' in movie_genre)) or
                            (preferred_lower == 'sci-fi' and 'science fiction' in movie_genre) or
                            (preferred_lower == '科幻' and ('sci-fi' in movie_genre or 'science fiction' in movie_genre))):
                            matches += 1
                            break
                
                # 标准化类型匹配分数 (0-1)
                if len(preferred_genres) > 0:
                    genre_score = min(matches / len(preferred_genres), 1.0)
                    
                    # 如果有完全匹配的类型，给予额外奖励
                    if matches > 0:
                        genre_score = max(genre_score, 0.3)  # 至少给30%的分数
                    if matches >= len(preferred_genres):
                        genre_score = 1.0  # 完全匹配给满分
        
        total_score += genre_score * 0.6  # 60% 权重
        
        # 2. 计算基于收藏的相似度分数 (权重30%)
        favorites_score = 0.0
        if favorites:
            max_similarity = 0.0
            for favorite in favorites:
                fav_title = favorite.movie.title
                if fav_title in indices.index if isinstance(indices, pd.Series) else fav_title in indices:
                    try:
                        if isinstance(indices, pd.Series):
                            fav_idx = indices.index.get_loc(fav_title)
                        else:
                            fav_idx = indices[fav_title]
                        
                        # 获取当前电影与收藏电影的相似度
                        similarity = cosine_sim[fav_idx][movie_idx]
                        max_similarity = max(max_similarity, similarity)
                    except:
                        continue
            favorites_score = max_similarity
        
        total_score += favorites_score * 0.3  # 30% 权重
        
        # 3. 计算基于浏览历史的相似度分数 (权重10%)
        history_score = 0.0
        if history:
            max_similarity = 0.0
            for history_item in history:
                hist_title = history_item.movie.title
                if hist_title in indices.index if isinstance(indices, pd.Series) else hist_title in indices:
                    try:
                        if isinstance(indices, pd.Series):
                            hist_idx = indices.index.get_loc(hist_title)
                        else:
                            hist_idx = indices[hist_title]
                        
                        # 获取当前电影与历史电影的相似度
                        similarity = cosine_sim[hist_idx][movie_idx]
                        max_similarity = max(max_similarity, similarity)
                    except:
                        continue
            history_score = max_similarity
        
        total_score += history_score * 0.1  # 10% 权重
        
        # 4. 添加随机因子增加推荐多样性
        random_factor = random.random() * 0.1  # 最多10%的随机性
        total_score += random_factor
        
        # 5. 添加电影质量因子 (基于评分)
        movie_row = all_movies_df[all_movies_df['title'] == movie_title]
        if not movie_row.empty:
            movie_rating = movie_row.iloc[0].get('avg_rate', 0)
            if movie_rating and movie_rating > 0:
                # 将评分标准化到0-0.1的范围
                rating_bonus = min(movie_rating / 10.0 * 0.1, 0.1)
                total_score += rating_bonus
        
        movie_scores[movie_title] = total_score
        
        # 调试输出前几个电影的详细分数
        if movie_idx < 5:
            print(f"[DEBUG] 电影: {movie_title}")
            print(f"  - 类型分数: {genre_score:.3f} (权重后: {genre_score * 0.6:.3f})")
            print(f"  - 收藏分数: {favorites_score:.3f} (权重后: {favorites_score * 0.3:.3f})")
            print(f"  - 历史分数: {history_score:.3f} (权重后: {history_score * 0.1:.3f})")
            print(f"  - 总分: {total_score:.3f}")
    
    # 按分数排序并返回Top-K
    sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
    
    print(f"[DEBUG] 排序后的前10个推荐:")
    for i, (title, score) in enumerate(sorted_movies[:10]):
        print(f"  {i+1}. {title}: {score:.3f}")
    
    recommended_titles = [title for title, score in sorted_movies[:top_k]]
    
    print(f"[DEBUG] 最终推荐数量: {len(recommended_titles)}")
    return recommended_titles
