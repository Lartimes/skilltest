"""
Matrix Factorization (MF) - 矩阵分解
作为深度学习模型的基线对比
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


class MFNet(nn.Module):
    """矩阵分解网络"""
    def __init__(self, n_users: int, n_items: int, embedding_dim: int):
        super().__init__()
        self.user_embedding = nn.Embedding(n_users, embedding_dim)
        self.item_embedding = nn.Embedding(n_items, embedding_dim)
        
        # 偏置
        self.user_bias = nn.Embedding(n_users, 1)
        self.item_bias = nn.Embedding(n_items, 1)
        self.global_bias = nn.Parameter(torch.zeros(1))
        
        # 初始化
        nn.init.normal_(self.user_embedding.weight, std=0.01)
        nn.init.normal_(self.item_embedding.weight, std=0.01)
    
    def forward(self, user_ids: torch.Tensor, item_ids: torch.Tensor) -> torch.Tensor:
        user_emb = self.user_embedding(user_ids)
        item_emb = self.item_embedding(item_ids)
        
        # 内积
        interaction = (user_emb * item_emb).sum(dim=1)
        
        # 偏置
        user_b = self.user_bias(user_ids).squeeze(-1)
        item_b = self.item_bias(item_ids).squeeze(-1)
        
        return interaction + user_b + item_b + self.global_bias


class MatrixFactorizationRecommender(BaseRecommender):
    """矩阵分解推荐模型"""
    
    def __init__(self, embedding_dim: int = 64, lr: float = 0.001,
                 reg: float = 0.001, epochs: int = 20, batch_size: int = 1024,
                 device: Optional[str] = None):
        super().__init__('MF', device, embedding_dim=embedding_dim)
        self.lr = lr
        self.reg = reg
        self.epochs = epochs
        self.batch_size = batch_size
        
        self.model: Optional[MFNet] = None
        self.optimizer = None
        self.criterion = nn.BCELoss()
    
    def build_model(self) -> nn.Module:
        self.model = MFNet(self.n_users, self.n_items, self.embedding_dim)
        self.model.to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=self.reg)
        return self.model
    
    def fit(self, train_data: FeatureData,
            val_data: Optional[FeatureData] = None,
            verbose: bool = True) -> 'MatrixFactorizationRecommender':
        """训练模型"""
        self.set_feature_dims(train_data)
        self.build_model()
        
        # 准备数据
        train_loader = self._create_dataloader(train_data)
        
        best_val_loss = float('inf')
        patience = 5
        patience_counter = 0
        
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0
            
            for batch in train_loader:
                user_ids = batch['user_id'].to(self.device)
                item_ids = batch['item_id'].to(self.device)
                labels = batch['label'].to(self.device)
                
                self.optimizer.zero_grad()
                predictions = self.model(user_ids, item_ids)
                loss = self.criterion(torch.sigmoid(predictions), labels)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            
            if verbose and (epoch + 1) % 5 == 0:
                msg = f"Epoch {epoch+1}/{self.epochs}, Loss: {avg_loss:.4f}"
                logger.info(f"  [{self.name}] {msg}")
                
                # 早停
                if avg_loss < best_val_loss:
                    best_val_loss = avg_loss
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
        dataset = TensorDataset(
            torch.LongTensor(data.user_ids),
            torch.LongTensor(data.item_ids),
            torch.FloatTensor(data.labels)
        )
        
        class BatchDataLoader:
            """返回字典格式的DataLoader包装器"""
            def __init__(self, dataloader):
                self.dataloader = dataloader
                self.device = None
            
            def __iter__(self):
                for batch in self.dataloader:
                    yield {
                        'user_id': batch[0],
                        'item_id': batch[1],
                        'label': batch[2]
                    }
            
            def __len__(self):
                return len(self.dataloader)
        
        return BatchDataLoader(DataLoader(dataset, batch_size=self.batch_size, shuffle=True))
    
    def predict(self, user_id: int, item_ids: np.ndarray) -> np.ndarray:
        """预测"""
        self.model.eval()
        with torch.no_grad():
            user_tensor = torch.LongTensor([user_id] * len(item_ids)).to(self.device)
            item_tensor = torch.LongTensor(item_ids).to(self.device)
            scores = self.model(user_tensor, item_tensor)
            return torch.sigmoid(scores).cpu().numpy()


# 注册
from ..registry import register
register('mf')(MatrixFactorizationRecommender)
