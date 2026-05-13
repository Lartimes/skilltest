"""
推荐模型基类
所有深度学习推荐模型必须继承此类
"""

from abc import ABC, abstractmethod
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
import logging
import numpy as np
import pandas as pd

from .data import FeatureData

logger = logging.getLogger(__name__)


class BaseRecommender(ABC):
    """推荐模型基类
    
    所有推荐模型必须实现以下方法:
    - build_model(): 构建模型
    - fit(): 训练模型
    - predict(): 预测
    - recommend(): 推荐
    """
    
    def __init__(self, name: str, device: Optional[str] = None, **kwargs):
        self.name = name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model: Optional[nn.Module] = None
        self.is_fitted = False
        
        # ID映射
        self.user2idx: Dict[Any, int] = {}
        self.idx2user: Dict[int, Any] = {}
        self.item2idx: Dict[Any, int] = {}
        self.idx2item: Dict[int, Any] = {}
        
        # 嵌入维度
        self.embedding_dim: int = kwargs.get('embedding_dim', 64)
        
        # 特征维度信息
        self.n_users: int = 0
        self.n_items: int = 0
        self.n_user_onehot: int = 0
        self.n_user_dense: int = 0
        self.n_item_onehot: int = 0
        self.n_item_dense: int = 0
        
        logger.info(f"初始化模型: {name}, 设备: {self.device}")
    
    @abstractmethod
    def build_model(self) -> nn.Module:
        """构建模型"""
        pass
    
    @abstractmethod
    def fit(self, train_data: FeatureData, 
            val_data: Optional[FeatureData] = None,
            **kwargs) -> 'BaseRecommender':
        """训练模型"""
        pass
    
    @abstractmethod
    def predict(self, user_id: int, item_ids: np.ndarray) -> np.ndarray:
        """预测评分"""
        pass
    
    def recommend(self, user_id: Any, n: int = 10,
                  exclude_known: bool = True,
                  known_items: Optional[set] = None) -> List[Tuple[Any, float]]:
        """为用户推荐物品"""
        if not self.is_fitted or self.model is None:
            raise ValueError("Model not fitted")
        
        # 转换user_id
        if user_id not in self.user2idx:
            # 冷启动用户，返回热门物品
            return self._recommend_cold_start(n)
        
        u_idx = self.user2idx[user_id]
        
        # 预测所有物品
        scores = self.predict(u_idx, np.arange(self.n_items))
        
        # 排序并过滤
        if exclude_known and known_items:
            candidate_indices = [
                i for i, item in enumerate(self.idx2item.values())
                if item not in known_items
            ]
        else:
            candidate_indices = list(range(self.n_items))
        
        # 取top-k
        top_k_idx = np.argsort(scores[candidate_indices])[::-1][:n]
        top_items = [candidate_indices[i] for i in top_k_idx]
        
        return [(self.idx2item[i], float(scores[i])) for i in top_items]
    
    def _recommend_cold_start(self, n: int) -> List[Tuple[Any, float]]:
        """冷启动推荐"""
        return [(self.idx2item[i], 0.5) for i in range(min(n, self.n_items))]
    
    def set_feature_dims(self, data: FeatureData):
        """设置特征维度"""
        self.n_users = data.n_users
        self.n_items = data.n_items
        self.n_user_onehot = data.n_user_onehot
        self.n_user_dense = data.n_user_dense
        self.n_item_onehot = data.n_item_onehot
        self.n_item_dense = data.n_item_dense
        self.idx2user = data.idx2user
        self.idx2item = data.idx2item
        self.user2idx = {v: k for k, v in data.idx2user.items()}
        self.item2idx = {v: k for k, v in data.idx2item.items()}
    
    def set_feature_dims_from_checkpoint(self, checkpoint: dict):
        """从checkpoint加载特征维度"""
        config = checkpoint.get('config', checkpoint)
        self._load_config(config)
    
    def save(self, path: str) -> None:
        """保存模型"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'user2idx': self.user2idx,
            'item2idx': self.item2idx,
            'config': self._get_config()
        }, path)
        logger.info(f"[{self.name}] 模型已保存: {path}")
    
    def load(self, path: str) -> 'BaseRecommender':
        """加载模型"""
        checkpoint = torch.load(path, map_location=self.device)
        self.user2idx = checkpoint['user2idx']
        self.item2idx = checkpoint['item2idx']
        self._load_config(checkpoint['config'])
        self.build_model()
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.is_fitted = True
        logger.info(f"[{self.name}] 模型已加载: {path}")
        return self
    
    def _get_config(self) -> dict:
        """获取配置"""
        return {
            'name': self.name, 
            'embedding_dim': self.embedding_dim,
            'n_users': self.n_users,
            'n_items': self.n_items,
            'n_user_onehot': self.n_user_onehot,
            'n_user_dense': self.n_user_dense,
            'n_item_onehot': self.n_item_onehot,
            'n_item_dense': self.n_item_dense,
        }
    
    def _load_config(self, config: dict) -> None:
        """加载配置"""
        self.embedding_dim = config.get('embedding_dim', 64)
        self.n_users = config.get('n_users', 0)
        self.n_items = config.get('n_items', 0)
        self.n_user_onehot = config.get('n_user_onehot', 0)
        self.n_user_dense = config.get('n_user_dense', 0)
        self.n_item_onehot = config.get('n_item_onehot', 0)
        self.n_item_dense = config.get('n_item_dense', 0)
    
    def __repr__(self) -> str:
        status = "fitted" if self.is_fitted else "not fitted"
        return f"<{self.__class__.__name__}[{self.name}] ({status})>"
