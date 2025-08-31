import numpy as np 
import torch

def evaluate_model(model, test_data, num_users, num_items, K=10):
    model.eval()
    recalls = []
    ndcgs = []

    # 获取用户和物品嵌入
    user_emb, item_emb = model(test_data.edge_index)

    # 遍历每个用户
    for user_id in range(num_users):
        # 获取该用户的测试集物品（注意要减去 num_users 偏移）
        true_items = (
            test_data.edge_index[1][test_data.edge_index[0] == user_id]
            .unique()
            .cpu()
            .numpy()
            - num_users
        )
        true_items = true_items[(true_items >= 0) & (true_items < num_items)]

        if len(true_items) == 0:
            recalls.append(0)
            ndcgs.append(0)
            continue

        # 预测所有物品的分数
        scores = torch.matmul(user_emb[user_id], item_emb.T).detach().cpu().numpy()

        # 选出分数最高的 K 个物品
        top_k_items = np.argsort(scores)[-K:][::-1]

        # 计算 Recall@K
        hits = np.intersect1d(top_k_items, true_items)
        recall = len(hits) / len(true_items)
        recalls.append(recall)

        # 计算 NDCG@K
        dcg = 0
        for rank, item in enumerate(top_k_items):
            if item in true_items:
                dcg += 1 / np.log2(rank + 2)
        idcg = sum(1 / np.log2(i + 2) for i in range(min(len(true_items), K)))
        ndcg = dcg / idcg if idcg > 0 else 0
        ndcgs.append(ndcg)

    return recalls, ndcgs
