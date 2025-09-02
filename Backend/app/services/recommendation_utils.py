"""
推荐算法工具模块
"""

import numpy as np
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
