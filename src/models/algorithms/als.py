# -*- coding: utf-8 -*-
"""
ALS (交替最小二乘) 算法
专门用于隐式反馈数据的推荐
内存效率高，支持全量数据训练
"""

import numpy as np
from scipy import sparse
from implicit.als import AlternatingLeastSquares
from typing import Optional, List, Dict, Tuple
import logging

from ..base import BaseRecommender
from ..data import FeatureData

logger = logging.getLogger(__name__)


class ALSRecommender(BaseRecommender):
    """ALS (交替最小二乘) 推荐器
    
    专门用于隐式反馈数据的矩阵分解算法
    - 内存效率高，适合大规模稀疏矩阵
    - 不需要梯度下降，通过闭式解求解
    - 支持用户/物品因子的稀疏表示
    
    参考: "Collaborative Filtering for Implicit Feedback Datasets" (Hu et al., 2008)
    """
    
    def __init__(self,
                 factors: int = 64,
                 regularization: float = 0.01,
                 alpha: float = 40.0,
                 iterations: int = 15,
                 calculate_training_loss: bool = False,
                 random_state: int = 42,
                 device: Optional[str] = None):
        """
        Args:
            factors: 隐因子数量 (相当于embedding维度)
            regularization: L2正则化系数
            alpha: 置信度系数，值越高越关注正向反馈
            iterations: 迭代次数
            calculate_training_loss: 是否计算训练损失
            random_state: 随机种子
        """
        super().__init__('ALS', device, embedding_dim=factors)
        self.factors = factors
        self.regularization = regularization
        self.alpha = alpha
        self.iterations = iterations
        self.calculate_training_loss = calculate_training_loss
        self.random_state = random_state
        
        self.model: Optional[AlternatingLeastSquares] = None
        self.item_user_matrix: Optional[sparse.csr_matrix] = None
        self.user_item_matrix: Optional[sparse.csc_matrix] = None
    
    def build_model(self):
        """构建ALS模型"""
        self.model = AlternatingLeastSquares(
            factors=self.factors,
            regularization=self.regularization,
            alpha=self.alpha,
            iterations=self.iterations,
            calculate_training_loss=self.calculate_training_loss,
            random_state=self.random_state,
            use_gpu=False,  # 强制使用CPU
        )
        return self
    
    def fit(self, train_data: FeatureData,
            val_data: Optional[FeatureData] = None,
            verbose: bool = True) -> 'ALSRecommender':
        """训练模型"""
        self.set_feature_dims(train_data)
        self.build_model()
        
        # 构建稀疏矩阵 (item x user)
        self.item_user_matrix = self._build_item_user_matrix(train_data)
        self.user_item_matrix = self.item_user_matrix.T.tocsr()
        
        logger.info(f"  [ALS] factors={self.factors}, alpha={self.alpha}, iterations={self.iterations}")
        logger.info(f"  [ALS] 稀疏矩阵: {self.item_user_matrix.nnz} 非零元素")
        
        # 训练
        logger.info(f"  [ALS] 开始训练...")
        self.model.fit(
            self.item_user_matrix,
            show_progress=verbose
        )
        
        self.is_fitted = True
        logger.info(f"  [ALS] 训练完成!")
        
        return self
    
    def _build_item_user_matrix(self, data: FeatureData) -> sparse.csr_matrix:
        """构建物品-用户稀疏矩阵"""
        n_items = data.n_items
        n_users = data.n_users
        
        # 使用标签作为置信度权重
        weights = data.labels if hasattr(data, 'labels') else np.ones(len(data.user_ids))
        weights = (weights * self.alpha).astype(np.float32)
        
        # 构建稀疏矩阵 (item x user)
        matrix = sparse.csr_matrix(
            (weights, (data.item_ids, data.user_ids)),
            shape=(n_items, n_users)
        )
        
        return matrix
    
    def predict(self, user_id: int, item_ids: np.ndarray) -> np.ndarray:
        """预测用户对物品的评分"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        # 计算用户对所有物品的分数
        # user_factors: (1, factors), item_factors: (factors, n_items)
        user_vector = self.model.user_factors[user_id]
        
        scores = []
        for item_id in item_ids:
            if item_id < len(self.model.item_factors):
                item_vector = self.model.item_factors[item_id]
                score = np.dot(user_vector, item_vector)
            else:
                score = 0.0
            scores.append(score)
        
        # 归一化到 [0, 1]
        scores = np.array(scores)
        scores = 1 / (1 + np.exp(-scores))  # sigmoid
        return scores
    
    def recommend(self, user_id: any, n: int = 10,
                  exclude_known: bool = True,
                  known_items: Optional[set] = None) -> List[Tuple[any, float]]:
        """为用户推荐物品"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        if user_id not in self.user2idx:
            return []
        
        u_idx = self.user2idx[user_id]
        
        # 使用库自带的推荐函数
        # 返回: [(item_id, score), ...]
        recommendations = self.model.recommend(
            userid=u_idx,
            user_items=self.user_item_matrix,
            N=n,
            filter_already_liked_items=exclude_known
        )
        
        return [(int(item_id), float(score)) for item_id, score in recommendations]
    
    @property
    def user_factors(self) -> np.ndarray:
        """获取用户因子矩阵"""
        if self.model:
            return self.model.user_factors
        return None
    
    @property
    def item_factors(self) -> np.ndarray:
        """获取物品因子矩阵"""
        if self.model:
            return self.model.item_factors
        return None


# 注册
from ..registry import register
register('als')(ALSRecommender)
