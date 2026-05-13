# -*- coding: utf-8 -*-
"""
ItemCF (基于物品的协同过滤) 算法
利用物品之间的相似度进行推荐
"""

import numpy as np
from collections import defaultdict
from typing import Optional, List, Dict, Tuple
import logging

from ..base import BaseRecommender
from ..data import FeatureData

logger = logging.getLogger(__name__)


class ItemCFRecommender(BaseRecommender):
    """基于物品的协同过滤推荐器
    
    算法原理:
    - 计算物品之间的相似度 (余弦相似度)
    - 根据用户历史喜欢的物品，找到相似的物品推荐
    - 适合用户数多于物品数的场景
    """
    
    def __init__(self,
                 n_similar_items: int = 20,
                 normalize: bool = True,
                 device: Optional[str] = None):
        """
        Args:
            n_similar_items: 每个物品保留的相似物品数量
            normalize: 是否归一化相似度
            device: 设备 (cpu/cuda)
        """
        super().__init__('ItemCF', device, embedding_dim=0)
        self.n_similar_items = n_similar_items
        self.normalize = normalize
        
        # 物品相似度矩阵: {item_id: [(similar_item_id, similarity), ...]}
        self.item_similarity: Dict[int, List[Tuple[int, float]]] = {}
        
        # 用户-物品交互表: {user_id: {item_id: rating}}
        self.user_items: Dict[int, Dict[int, float]] = {}
        
        # 物品-用户交互表: {item_id: {user_id: rating}}
        self.item_users: Dict[int, Dict[int, float]] = {}
        
        # 所有物品集合
        self.all_items: set = set()
        
        # 每个物品的热门度 (用于降权热门物品)
        self.item_popularity: Dict[int, int] = {}
    
    def build_model(self):
        """ItemCF 不需要构建模型，直接返回"""
        return self
    
    def fit(self, train_data: FeatureData,
            val_data: Optional[FeatureData] = None,
            verbose: bool = True) -> 'ItemCFRecommender':
        """训练模型 (构建相似度矩阵)"""
        self.set_feature_dims(train_data)
        
        logger.info(f"  [ItemCF] 构建用户-物品交互表...")
        
        # 构建交互表
        self.user_items = defaultdict(dict)
        self.item_users = defaultdict(dict)
        self.all_items = set()
        self.item_popularity = defaultdict(int)
        
        for i in range(len(train_data.user_ids)):
            uid = train_data.user_ids[i]
            iid = train_data.item_ids[i]
            label = train_data.labels[i] if hasattr(train_data, 'labels') else 1.0
            
            self.user_items[uid][iid] = label
            self.item_users[iid][uid] = label
            self.all_items.add(iid)
            self.item_popularity[iid] += 1
        
        n_users = len(self.user_items)
        n_items = len(self.all_items)
        n_interactions = sum(len(items) for items in self.user_items.values())
        
        logger.info(f"  [ItemCF] 用户: {n_users}, 物品: {n_items}, 交互: {n_interactions}")
        
        # 计算物品相似度
        logger.info(f"  [ItemCF] 计算物品相似度 (n_similar_items={self.n_similar_items})...")
        self._compute_item_similarity()
        
        self.is_fitted = True
        logger.info(f"  [ItemCF] 完成! 相似度矩阵大小: {len(self.item_similarity)}")
        
        return self
    
    def _compute_item_similarity(self):
        """计算物品之间的相似度"""
        self.item_similarity = {}
        
        all_items_list = list(self.all_items)
        n_items = len(all_items_list)
        
        # 使用余弦相似度
        # sim(i,j) = |N(i) ∩ N(j)| / sqrt(|N(i)| * |N(j)|)
        
        for idx, item_i in enumerate(all_items_list):
            if idx % 5000 == 0:
                logger.info(f"  [ItemCF] 处理进度: {idx}/{n_items}")
            
            users_i = self.item_users[item_i]
            if not users_i:
                continue
            
            similarities = []
            
            for item_j in self.all_items:
                if item_i == item_j:
                    continue
                
                users_j = self.item_users[item_j]
                if not users_j:
                    continue
                
                # 交集
                common_users = set(users_i.keys()) & set(users_j.keys())
                if not common_users:
                    continue
                
                # 计算相似度
                dot_i = sum(users_i[u] for u in common_users)
                dot_j = sum(users_j[u] for u in common_users)
                
                norm_i = np.sqrt(sum(users_i[u]**2 for u in users_i.keys()))
                norm_j = np.sqrt(sum(users_j[u]**2 for u in users_j.keys()))
                
                if norm_i > 0 and norm_j > 0:
                    sim = dot_i / (norm_i * norm_j)
                    
                    # 可选：对热门物品降权
                    if self.normalize:
                        popularity_i = self.item_popularity[item_i]
                        popularity_j = self.item_popularity[item_j]
                        if popularity_i > 0 and popularity_j > 0:
                            # IDF-like 降权
                            sim *= 1.0 / np.log1p(popularity_i * popularity_j / (n_items + 1))
                    
                    similarities.append((item_j, sim))
            
            # 只保留最相似的 n_similar_items 个
            similarities.sort(key=lambda x: -x[1])
            self.item_similarity[item_i] = similarities[:self.n_similar_items]
    
    def predict(self, user_id: int, item_ids: np.ndarray) -> np.ndarray:
        """预测用户对物品的评分"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        scores = np.zeros(len(item_ids))
        
        # 用户历史喜欢的物品
        user_history = self.user_items.get(user_id, {})
        if not user_history:
            # 冷启动用户，返回平均分
            return np.ones(len(item_ids)) * 0.5
        
        for idx, item in enumerate(item_ids):
            score = 0.0
            total_sim = 0.0
            
            # 对于用户喜欢的每个物品，找到与目标物品的相似度
            for liked_item, rating in user_history.items():
                # 找到 liked_item 相似的物品中是否有 item
                similar_items = self.item_similarity.get(liked_item, [])
                for sim_item, sim_score in similar_items:
                    if sim_item == item:
                        score += sim_score * rating
                        total_sim += abs(sim_score)
                        break
            
            if total_sim > 0:
                scores[idx] = score / total_sim
            else:
                # 没有相似物品，使用物品热门度
                scores[idx] = self.item_popularity.get(item, 1) / max(self.item_popularity.values())
        
        # 归一化到 [0, 1]
        if scores.max() > scores.min():
            scores = (scores - scores.min()) / (scores.max() - scores.min())
        
        return scores
    
    def recommend(self, user_id: any, n: int = 10,
                  exclude_known: bool = True,
                  known_items: Optional[set] = None) -> List[Tuple[any, float]]:
        """为用户推荐物品"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        # 转换 user_id
        if user_id not in self.user2idx:
            return []
        
        u_idx = self.user2idx[user_id]
        known = known_items or set()
        
        # 获取所有未交互的物品
        all_items = list(self.all_items - known if exclude_known else self.all_items)
        
        if not all_items:
            return []
        
        # 预测分数
        item_ids = np.array([self.item2idx.get(i, -1) for i in all_items])
        valid_mask = item_ids >= 0
        valid_items = [all_items[i] for i in range(len(all_items)) if valid_mask[i]]
        valid_ids = item_ids[valid_mask]
        
        if len(valid_ids) == 0:
            return []
        
        scores = self.predict(u_idx, valid_ids)
        
        # 取 top-n
        top_indices = np.argsort(scores)[::-1][:n]
        
        return [(valid_items[i], float(scores[i])) for i in top_indices]
    
    def most_popular(self, n: int = 10) -> List[Tuple[int, int]]:
        """返回最热门的物品"""
        sorted_items = sorted(self.item_popularity.items(), key=lambda x: -x[1])
        return sorted_items[:n]


# 注册
from ..registry import register
register('itemcf')(ItemCFRecommender)
