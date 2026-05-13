"""
NeuMF - Neural Matrix Factorization
结合 Generalized Matrix Factorization (GMF) 和 Multi-Layer Perceptron (MLP)
支持特征输入
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from typing import Optional, List
import logging

from ..base import BaseRecommender
from ..data import FeatureData, RecommenderDataset

logger = logging.getLogger(__name__)


class NeuMFNet(nn.Module):
    """NeuMF网络结构: GMF + MLP"""
    
    def __init__(self,
                 n_users: int,
                 n_items: int,
                 embedding_dim: int = 64,
                 gmf_dim: int = 32,
                 mlp_dims: List[int] = None,
                 dropout: float = 0.2):
        super().__init__()
        
        mlp_dims = mlp_dims or [128, 64, 32]
        
        # GMF: 使用 element-wise product
        self.gmf_user_embedding = nn.Embedding(n_users, gmf_dim)
        self.gmf_item_embedding = nn.Embedding(n_items, gmf_dim)
        
        # MLP: 使用 concat + Dense
        self.mlp_user_embedding = nn.Embedding(n_users, embedding_dim)
        self.mlp_item_embedding = nn.Embedding(n_items, embedding_dim)
        
        mlp_layers = []
        mlp_input_dim = embedding_dim * 2
        for dim in mlp_dims:
            mlp_layers.append(nn.Linear(mlp_input_dim, dim))
            mlp_layers.append(nn.BatchNorm1d(dim))
            mlp_layers.append(nn.ReLU())
            mlp_layers.append(nn.Dropout(dropout))
            mlp_input_dim = dim
        self.mlp = nn.Sequential(*mlp_layers)
        
        # 最终预测层: GMF输出(gmf_dim) + MLP输出(mlp_dims[-1])
        self.output = nn.Linear(gmf_dim + mlp_dims[-1], 1)
        
        # 初始化
        self._init_weights()
    
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.01)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
    
    def forward(self, user_ids: torch.Tensor, item_ids: torch.Tensor) -> torch.Tensor:
        # GMF
        gmf_user_emb = self.gmf_user_embedding(user_ids)
        gmf_item_emb = self.gmf_item_embedding(item_ids)
        gmf_output = gmf_user_emb * gmf_item_emb  # element-wise product
        
        # MLP
        mlp_user_emb = self.mlp_user_embedding(user_ids)
        mlp_item_emb = self.mlp_item_embedding(item_ids)
        mlp_input = torch.cat([mlp_user_emb, mlp_item_emb], dim=1)
        mlp_output = self.mlp(mlp_input)
        
        # 合并
        concat = torch.cat([gmf_output, mlp_output], dim=1)
        output = torch.sigmoid(self.output(concat))
        
        return output.squeeze(-1)


class NeuMFRecommender(BaseRecommender):
    """Neural Matrix Factorization推荐模型"""
    
    def __init__(self,
                 embedding_dim: int = 64,
                 gmf_dim: int = None,
                 mlp_dims: List[int] = None,
                 lr: float = 0.001,
                 epochs: int = 20,
                 batch_size: int = 1024,
                 dropout: float = 0.2,
                 device: Optional[str] = None):
        super().__init__('NeuMF', device, embedding_dim=embedding_dim)
        self.gmf_dim = gmf_dim or (embedding_dim // 2)
        self.mlp_dims = mlp_dims or [128, 64, 32]
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.dropout = dropout
        
        self.model: Optional[NeuMFNet] = None
        self.optimizer = None
        self.criterion = nn.BCELoss()
    
    def build_model(self) -> nn.Module:
        self.model = NeuMFNet(
            n_users=self.n_users,
            n_items=self.n_items,
            embedding_dim=self.embedding_dim,
            gmf_dim=self.gmf_dim,
            mlp_dims=self.mlp_dims,
            dropout=self.dropout
        )
        self.model.to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        return self.model
    
    def fit(self, train_data: FeatureData,
            val_data: Optional[FeatureData] = None,
            verbose: bool = True) -> 'NeuMFRecommender':
        """训练模型"""
        self.set_feature_dims(train_data)
        self.build_model()
        
        train_loader = DataLoader(
            RecommenderDataset(train_data),
            batch_size=self.batch_size,
            shuffle=True
        )
        
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0
            
            for batch in train_loader:
                batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v
                        for k, v in batch.items()}
                
                self.optimizer.zero_grad()
                outputs = self.model(batch['user_id'], batch['item_id'])
                loss = self.criterion(outputs, batch['label'])
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            
            if verbose and (epoch + 1) % 5 == 0:
                logger.info(f"  [{self.name}] Epoch {epoch+1}/{self.epochs}, Loss: {avg_loss:.4f}")
        
        self.is_fitted = True
        return self
    
    def predict(self, user_id: int, item_ids: np.ndarray) -> np.ndarray:
        """预测"""
        self.model.eval()
        with torch.no_grad():
            user_tensor = torch.LongTensor([user_id] * len(item_ids)).to(self.device)
            item_tensor = torch.LongTensor(item_ids).to(self.device)
            scores = self.model(user_tensor, item_tensor)
            return scores.cpu().numpy()


# 注册
from ..registry import register
register('neumf')(NeuMFRecommender)
