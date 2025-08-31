import torch
import pandas as pd
import sqlite3
from model import LightGCN   # 确保 model.py 里有 get_embeddings(edge_index)

# ------------------------
# 1. 加载数据和模型
# ------------------------
users = pd.read_csv("../data/processed/movielens/users.csv")
items = pd.read_csv("../data/processed/movielens/items.csv")
ratings = pd.read_csv("../data/processed/movielens/ratings.csv")

num_users = users["user_id"].nunique()
num_items = items["movie_id"].nunique()

# 初始化模型
model = LightGCN(num_users=num_users, num_items=num_items, embedding_dim=64, num_layers=3)
model.load_state_dict(torch.load("../logs/recommender/output/LightGCN_20250831/LightGCN_model.pth", map_location="cpu"))
model.eval()

# ------------------------
# 2. 构建图结构 edge_index
# ------------------------
# 注意：物品 id 需要整体 +num_users 以区分用户/物品
rows = ratings["user_id"].values
cols = ratings["movie_id"].values + num_users
edge_index = torch.tensor([rows, cols], dtype=torch.long)

# 对称化（加上反向边）
edge_index = torch.cat([edge_index, edge_index.flip(0)], dim=1)

# ------------------------
# 3. 得到最终嵌入
# ------------------------
user_emb, item_emb = model.get_embeddings(edge_index)  # [num_users, dim], [num_items, dim]

# 计算用户对所有物品的预测分数
scores = torch.matmul(user_emb, item_emb.t())  # [num_users, num_items]

# ------------------------
# 4. 为每个用户取 Top-K 推荐
# ------------------------
K = 10
recommendations = []

for u in range(num_users):
    # 找到该用户已经评分过的物品
    seen_items = ratings[ratings["user_id"] == u]["movie_id"].tolist()
    user_scores = scores[u].clone()

    if len(seen_items) > 0:
        user_scores[seen_items] = -1e9  # 屏蔽已交互过的物品

    # Top-K 推荐
    top_items = torch.topk(user_scores, K).indices.tolist()
    for rank, movie_id in enumerate(top_items, 1):
        recommendations.append((int(u), int(movie_id), rank))

# ------------------------
# 5. 存入../data/database/recommender.csv
# ------------------------
import os

output_dir = "../data/database_data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "recommender.csv")

recommendations_df = pd.DataFrame(recommendations, columns=["user_id", "movie_id", "rank"])
recommendations_df.to_csv(output_path, index=False)

print(f"推荐结果已保存到 {output_path}")
