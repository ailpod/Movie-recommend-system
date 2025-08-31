import torch
import torch.nn as nn
import torch.nn.functional as F

class LightGCN(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim, num_layers):
        super(LightGCN, self).__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.embedding_dim = embedding_dim
        self.num_layers = num_layers

        # 初始化用户和物品的嵌入
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.user_embedding.weight)
        nn.init.xavier_uniform_(self.item_embedding.weight)

    def forward(self, edge_index):
        # 获取初始嵌入
        users_emb = self.user_embedding.weight
        items_emb = self.item_embedding.weight
        all_emb = torch.cat([users_emb, items_emb], dim=0)

        # 存储每一层的嵌入
        embs = [all_emb]

        # 图卷积层
        for _ in range(self.num_layers):
            # 计算邻接矩阵的归一化
            row, col = edge_index
            deg = torch.bincount(row, minlength=all_emb.size(0))
            deg_inv_sqrt = deg.pow(-0.5)
            deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0
            norm = deg_inv_sqrt[row] * deg_inv_sqrt[col]

            # 稀疏矩阵乘法
            all_emb = torch.sparse_coo_tensor(
                edge_index, norm, size=(all_emb.size(0), all_emb.size(0))
            ).to_dense() @ all_emb
            embs.append(all_emb)

        # 平均所有层的嵌入
        final_emb = torch.mean(torch.stack(embs, dim=0), dim=0)

        # 分离用户和物品嵌入
        users_emb_final, items_emb_final = torch.split(
            final_emb, [self.num_users, self.num_items]
        )
        return users_emb_final, items_emb_final

    def loss(self, users_emb, pos_items_emb, neg_items_emb):
        # 计算正负样本的评分
        pos_scores = torch.sum(users_emb * pos_items_emb, dim=1)
        neg_scores = torch.sum(users_emb * neg_items_emb, dim=1)

        # 使用 BPR 损失
        loss = -torch.mean(F.logsigmoid(pos_scores - neg_scores))
        return loss
    
    def get_embeddings(self, edge_index):
        users_emb_final, items_emb_final = self.forward(edge_index)
        return users_emb_final, items_emb_final

