import os
import datetime
import pandas as pd
import torch
import numpy as np
from torch_geometric.data import Data
from sklearn.model_selection import train_test_split

# 从自己写的代码导入
from model import LightGCN
from utils import evaluate_model

# 1. 加载预处理后的数据
users = pd.read_csv("../data/processed/movielens/users.csv")
items = pd.read_csv("../data/processed/movielens/items.csv")
ratings = pd.read_csv("../data/processed/movielens/ratings.csv")

# 2. 划分训练集和测试集
train_ratings, test_ratings = train_test_split(ratings, test_size=0.2, random_state=42)

# 3. 构建训练图的边（用户-物品交互）
num_users = users["user_id"].max() + 1
num_items = items["movie_id"].max() + 1

# 4. 构建训练和测试图
train_user_nodes = train_ratings["user_id"].values
train_item_nodes = train_ratings["movie_id"].values  # 不偏移
train_edge_index = torch.tensor(
    np.vstack([np.concatenate([train_user_nodes, train_item_nodes + num_users]),
               np.concatenate([train_item_nodes + num_users, train_user_nodes])]),
    dtype=torch.long
)

test_user_nodes = test_ratings["user_id"].values
test_item_nodes = test_ratings["movie_id"].values 
test_edge_index = torch.tensor(
    np.vstack([np.concatenate([test_user_nodes, test_item_nodes + num_users]),
               np.concatenate([test_item_nodes + num_users, test_user_nodes])]),
    dtype=torch.long
)

# 转换为 PyTorch Geometric 的 Data 对象
train_data = Data(edge_index=train_edge_index)
test_data = Data(edge_index=test_edge_index)

# 5. 初始化模型
embedding_dim = 64
num_layers = 3
model = LightGCN(num_users, num_items, embedding_dim, num_layers)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# # 6. 训练模型
# num_epochs = 50
# for epoch in range(num_epochs):
#     model.train()
#     optimizer.zero_grad()

#     # 获取用户和物品嵌入
#     users_emb, items_emb = model(train_data.edge_index)

#     # 负采样（全局均匀采样）
#     neg_items = torch.randint(0, num_items, (train_user_nodes.shape[0],))
#     neg_items_emb = items_emb[neg_items]

#     # 计算损失
#     loss = model.loss(users_emb[train_user_nodes], items_emb[train_item_nodes], neg_items_emb)
#     loss.backward()
#     optimizer.step()

#     print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}")

# 6. 训练模型
# 预先构建 用户->交互过物品 的映射
user2items = train_ratings.groupby("user_id")["movie_id"].apply(set).to_dict()
all_items = np.arange(num_items)

num_epochs = 1000
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()

    # 获取用户和物品嵌入
    users_emb, items_emb = model(train_data.edge_index)

    # ----------------------------
    # 负采样（向量化）
    # ----------------------------
    # 先随机采样候选负样本
    neg_items = np.random.randint(0, num_items, size=len(train_user_nodes))

    # 检查是否采到正样本，如果采到则重新采直到合法
    for i, u in enumerate(train_user_nodes):
        while neg_items[i] in user2items.get(u, set()):
            neg_items[i] = np.random.randint(0, num_items)

    neg_items = torch.tensor(neg_items, dtype=torch.long)
    neg_items_emb = items_emb[neg_items]

    # 计算损失
    loss = model.loss(
        users_emb[train_user_nodes],
        items_emb[train_item_nodes],
        neg_items_emb
    )
    loss.backward()
    optimizer.step()

    # 在每个epoch结束后评估模型的准确率
    if (epoch + 1) % 10 == 0 or epoch == num_epochs - 1:
        model.eval()
        recalls, ndcgs = evaluate_model(model, test_data, num_users, num_items, K=10)
        print(f"Epoch {epoch+1}/{num_epochs}, Recall@10: {np.mean(recalls):.4f}, NDCG@10: {np.mean(ndcgs):.4f}")

# 7. 评估模型
recalls, ndcgs = evaluate_model(model, test_data, num_users, num_items, K=10)
print(f"Recall@10: {np.mean(recalls):.4f}")
print(f"NDCG@10: {np.mean(ndcgs):.4f}")

# 8. 保存模型
date_str = datetime.datetime.now().strftime("%Y%m%d")
save_dir = f"../logs/recommender/output/LightGCN_{date_str}"
os.makedirs(save_dir, exist_ok=True)
torch.save(model.state_dict(), os.path.join(save_dir, "LightGCN_model.pth"))
