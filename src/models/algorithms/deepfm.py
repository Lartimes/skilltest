"""
DeepFM - Deep Factorization Machine
支持特征输入的混合推荐模型
同时学习低阶特征交互(FM)和高阶特征交互(DNN)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from typing import Optional, List, Tuple, Dict
import logging

from ..base import BaseRecommender
from ..data import FeatureData

logger = logging.getLogger(__name__)


class FMComponent(nn.Module):
    """Factorization Machine组件 - 捕获二阶特征交互"""
    
    def __init__(self):
        super().__init__()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: [batch_size, field_dim] 拼接后的特征
        Returns:
            [batch_size, 1] FM输出
        """
        # FM: 0.5 * sum((sum(v_i)^2 - sum(v_i^2)))
        square_of_sum = torch.pow(torch.sum(x, dim=1), 2)
        sum_of_square = torch.sum(torch.pow(x, 2), dim=1)
        output = 0.5 * (square_of_sum - sum_of_square)
        return output.unsqueeze(-1)


class DNNComponent(nn.Module):
    """Deep Neural Network组件 - 捕获高阶特征交互"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], dropout: float = 0.5):
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim
        
        self.dnn = nn.Sequential(*layers)
        self.output_layer = nn.Linear(prev_dim, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.output_layer(self.dnn(x))


class DeepFMNet(nn.Module):
    """DeepFM网络结构"""
    
    def __init__(self,
                 n_users: int,
                 n_items: int,
                 embedding_dim: int = 64,
                 
                 # 用户特征
                 n_user_onehot: int = 0,
                 n_user_dense: int = 0,
                 user_onehot_max: int = 10,
                 
                 # 物品特征
                 n_item_onehot: int = 0,
                 n_item_dense: int = 0,
                 item_onehot_max: int = 10,
                 
                 # DNN结构
                 hidden_dims: List[int] = [128, 64],
                 dropout: float = 0.5):
        super().__init__()
        
        self.embedding_dim = embedding_dim
        
        # 1. ID Embeddings
        self.user_embedding = nn.Embedding(n_users, embedding_dim)
        self.item_embedding = nn.Embedding(n_items, embedding_dim)
        
        # 2. One-hot特征 Embeddings (如类别、标签)
        self.user_onehot_embedding = nn.Embedding(user_onehot_max + 1, embedding_dim) \
            if n_user_onehot > 0 else None
        self.item_onehot_embedding = nn.Embedding(item_onehot_max + 1, embedding_dim) \
            if n_item_onehot > 0 else None
        
        # 3. Dense特征处理 (用Linear映射到embedding维度)
        self.user_dense_layer = nn.Linear(n_user_dense, embedding_dim) \
            if n_user_dense > 0 else None
        self.item_dense_layer = nn.Linear(n_item_dense, embedding_dim) \
            if n_item_dense > 0 else None
        
        # 特征维度统计
        self.n_user_onehot = n_user_onehot
        self.n_user_dense = n_user_dense
        self.n_item_onehot = n_item_onehot
        self.n_item_dense = n_item_dense
        
        # 4. FM组件
        self.fm = FMComponent()
        
        # 5. DNN组件 - 输入是所有embedding的拼接
        total_embedding_dim = embedding_dim * self._count_fields()
        self.dnn = DNNComponent(total_embedding_dim, hidden_dims, dropout)
        
        # 6. 最终输出
        # Linear: 处理FM的输出(1维) + DNN的输出(1维)
        self.output_layer = nn.Linear(2, 1)
        
        # 初始化
        self._init_weights()
    
    def _count_fields(self) -> int:
        """计算字段数"""
        fields = 2  # user_id + item_id
        
        # 只有当特征存在时才计入
        if self.n_user_onehot > 0:
            fields += self.n_user_onehot
        if self.n_user_dense > 0:
            fields += 1
        if self.n_item_onehot > 0:
            fields += self.n_item_onehot
        if self.n_item_dense > 0:
            fields += 1
        
        return max(fields, 2)  # 至少是 2 (user_id + item_id)
    
    def _init_weights(self):
        """初始化权重"""
        for m in self.modules():
            if isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.01)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
    
    def forward(self, 
                user_ids: torch.Tensor,
                item_ids: torch.Tensor,
                user_onehot: Optional[torch.Tensor] = None,
                user_dense: Optional[torch.Tensor] = None,
                item_onehot: Optional[torch.Tensor] = None,
                item_dense: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        前向传播
        """
        embeddings = []
        
        # User ID embedding
        user_emb = self.user_embedding(user_ids)  # [B, E]
        embeddings.append(user_emb)
        
        # Item ID embedding
        item_emb = self.item_embedding(item_ids)  # [B, E]
        embeddings.append(item_emb)
        
        # User one-hot features
        if self.user_onehot_embedding is not None and user_onehot is not None:
            user_onehot_emb = self.user_onehot_embedding(user_onehot)
            embeddings.append(user_onehot_emb.view(-1, self.n_user_onehot * self.embedding_dim))
        
        # User dense features
        if self.user_dense_layer is not None and user_dense is not None:
            user_dense_emb = self.user_dense_layer(user_dense)
            embeddings.append(user_dense_emb)
        elif self.user_dense_layer is not None:
            # 特征为 None 时，用全零填充
            batch_size = user_ids.shape[0]
            fake_dense = torch.zeros(batch_size, self.n_user_dense).to(user_ids.device)
            user_dense_emb = self.user_dense_layer(fake_dense)
            embeddings.append(user_dense_emb)
        
        # Item one-hot features
        if self.item_onehot_embedding is not None and item_onehot is not None:
            item_onehot_emb = self.item_onehot_embedding(item_onehot)
            embeddings.append(item_onehot_emb.view(-1, self.n_item_onehot * self.embedding_dim))
        
        # Item dense features
        if self.item_dense_layer is not None and item_dense is not None:
            item_dense_emb = self.item_dense_layer(item_dense)
            embeddings.append(item_dense_emb)
        elif self.item_dense_layer is not None:
            # 特征为 None 时，用全零填充
            batch_size = item_ids.shape[0]
            fake_dense = torch.zeros(batch_size, self.n_item_dense).to(item_ids.device)
            item_dense_emb = self.item_dense_layer(fake_dense)
            embeddings.append(item_dense_emb)
        
        # 拼接所有embedding
        concat_emb = torch.cat(embeddings, dim=1)  # [B, total_dim]
        
        # FM: 二阶交互
        fm_input = concat_emb.view(-1, self._count_fields(), self.embedding_dim)
        fm_output = self.fm(fm_input.view(-1, self._count_fields() * self.embedding_dim))
        
        # DNN: 高阶交互
        dnn_output = self.dnn(concat_emb)
        
        # 合并FM和DNN
        combined = torch.cat([fm_output, dnn_output], dim=1)
        output = torch.sigmoid(self.output_layer(combined))
        
        return output.squeeze(-1)


class DeepFMRecommender(BaseRecommender):
    """DeepFM推荐模型"""
    
    def __init__(self,
                 embedding_dim: int = 64,
                 hidden_dims: List[int] = None,
                 lr: float = 0.001,
                 epochs: int = 20,
                 batch_size: int = 1024,
                 dropout: float = 0.5,
                 device: Optional[str] = None):
        super().__init__('DeepFM', device, embedding_dim=embedding_dim)
        self.hidden_dims = hidden_dims or [128, 64]
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.dropout = dropout
        
        self.model: Optional[DeepFMNet] = None
        self.optimizer = None
        self.criterion = nn.BCELoss()
        
        # 特征最大值
        self.user_onehot_max = 10
        self.item_onehot_max = 10
    
    def build_model(self) -> nn.Module:
        self.model = DeepFMNet(
            n_users=self.n_users,
            n_items=self.n_items,
            embedding_dim=self.embedding_dim,
            n_user_onehot=self.n_user_onehot,
            n_user_dense=self.n_user_dense,
            user_onehot_max=self.user_onehot_max,
            n_item_onehot=self.n_item_onehot,
            n_item_dense=self.n_item_dense,
            item_onehot_max=self.item_onehot_max,
            hidden_dims=self.hidden_dims,
            dropout=self.dropout
        )
        self.model.to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        return self.model
    
    def fit(self, train_data: FeatureData,
            val_data: Optional[FeatureData] = None,
            verbose: bool = True) -> 'DeepFMRecommender':
        """训练模型"""
        self.set_feature_dims(train_data)
        
        # 获取特征维度 - 使用 user_feats/item_feats
        if train_data.user_feats is not None:
            self.n_user_dense = train_data.user_feats.shape[1]
            self.n_user_onehot = 0
        if train_data.item_feats is not None:
            self.n_item_dense = train_data.item_feats.shape[1]
            self.n_item_onehot = 0
        
        self.build_model()
        
        # 准备数据
        train_loader = self._create_dataloader(train_data)
        
        best_loss = float('inf')
        patience = 5
        patience_counter = 0
        
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0
            
            for batch in train_loader:
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                        for k, v in batch.items()}
                
                self.optimizer.zero_grad()
                
                outputs = self.model(
                    user_ids=batch['user_id'],
                    item_ids=batch['item_id'],
                    user_onehot=batch.get('user_onehot'),
                    user_dense=batch.get('user_dense'),
                    item_onehot=batch.get('item_onehot'),
                    item_dense=batch.get('item_dense')
                )
                
                loss = self.criterion(outputs, batch['label'])
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            
            if verbose and (epoch + 1) % 5 == 0:
                logger.info(f"  [{self.name}] Epoch {epoch+1}/{self.epochs}, Loss: {avg_loss:.4f}")
                
                if avg_loss < best_loss:
                    best_loss = avg_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        logger.info(f"  [{self.name}] Early stopping at epoch {epoch+1}")
                        break
        
        self.is_fitted = True
        return self
    
    def _create_dataloader(self, data: FeatureData):
        """创建DataLoader"""
        from ..data import RecommenderDataset
        return DataLoader(
            RecommenderDataset(data),
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0
        )
    
    def predict(self, user_id: int, item_ids: np.ndarray) -> np.ndarray:
        """预测"""
        self.model.eval()
        with torch.no_grad():
            user_tensor = torch.LongTensor([user_id] * len(item_ids)).to(self.device)
            item_tensor = torch.LongTensor(item_ids).to(self.device)
            
            # 只传 user_id 和 item_id，不传特征
            scores = self.model(
                user_ids=user_tensor,
                item_ids=item_tensor,
                user_onehot=None,
                user_dense=None,
                item_onehot=None,
                item_dense=None
            )
            return scores.cpu().numpy()


# 注册
from ..registry import register
register('deepfm')(DeepFMRecommender)
