"""
评估指标模块
支持隐式反馈推荐系统的评估
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

from ..data import FeatureData

logger = logging.getLogger(__name__)


class RecommenderEvaluator:
    """推荐系统评估器 - 适合隐式反馈数据"""
    
    def __init__(self, k_values: List[int] = None, sample_users: int = 500, 
                 neg_per_user: int = 100):
        """
        Args:
            k_values: K值列表
            sample_users: 采样评估的用户数
            neg_per_user: 每个用户采样的负样本数量
        """
        self.k_values = k_values or [5, 10, 20]
        self.sample_users = sample_users
        self.neg_per_user = neg_per_user
    
    def evaluate(self, model, train_data: FeatureData, 
                 test_data: FeatureData) -> Dict[str, float]:
        """评估模型"""
        logger.info("=" * 50)
        logger.info("开始评估...")
        
        # 构建训练集交互字典
        train_interactions = self._build_user_items(train_data)
        
        # 构建测试集交互字典（用于评估）
        test_interactions = self._build_user_items(test_data)
        
        # 找出在训练集和测试集中都有交互的用户
        valid_users = set(train_interactions.keys()) & set(test_interactions.keys())
        logger.info(f"  有效评估用户数: {len(valid_users)}")
        
        if len(valid_users) == 0:
            logger.warning("  没有同时出现在训练集和测试集中的用户！")
            logger.warning("  可能原因: 数据随机划分导致用户分布在不同集合")
            return self._fallback_evaluate(model, train_data, test_data)
        
        # 采样用户
        valid_users = list(valid_users)
        if self.sample_users and self.sample_users < len(valid_users):
            np.random.seed(42)
            eval_users = np.random.choice(valid_users, self.sample_users, replace=False)
        else:
            eval_users = valid_users
        
        logger.info(f"  采样 {len(eval_users)} 个用户进行评估")
        
        # 构建候选池：所有物品
        all_items = set(range(train_data.n_items))
        
        metrics = {}
        
        # ========== Hit Rate @ K ==========
        for k in self.k_values:
            hr = self._hit_rate_at_k(model, eval_users, train_interactions, 
                                     test_interactions, all_items, k)
            metrics[f'hit_rate@{k}'] = hr
            logger.info(f"  Hit Rate@{k}: {hr:.4f}")
        
        # ========== MRR @ K ==========
        for k in self.k_values:
            mrr = self._mrr_at_k(model, eval_users, train_interactions, 
                                test_interactions, all_items, k)
            metrics[f'mrr@{k}'] = mrr
            logger.info(f"  MRR@{k}: {mrr:.4f}")
        
        # ========== AUC ==========
        auc = self._auc(model, eval_users, train_interactions, test_interactions, all_items)
        metrics['auc'] = auc
        logger.info(f"  AUC: {auc:.4f}")
        
        # ========== NDCG @ K ==========
        for k in self.k_values:
            ndcg = self._ndcg_at_k(model, eval_users, train_interactions, 
                                  test_interactions, all_items, k)
            metrics[f'ndcg@{k}'] = ndcg
            logger.info(f"  NDCG@{k}: {ndcg:.4f}")
        
        return metrics
    
    def _fallback_evaluate(self, model, train_data: FeatureData, 
                           test_data: FeatureData) -> Dict[str, float]:
        """回退评估：当数据分布问题时使用"""
        logger.info("  使用回退评估方法...")
        
        metrics = {}
        
        # 简单的 AUC 评估：比较正负样本得分
        pos_mask = test_data.labels >= 0.5
        neg_mask = test_data.labels < 0.5
        
        if pos_mask.sum() > 0 and neg_mask.sum() > 0:
            pos_items = test_data.item_ids[pos_mask]
            neg_items = test_data.item_ids[neg_mask]
            
            all_auc = []
            for uid in np.unique(test_data.user_ids):
                user_mask = test_data.user_ids == uid
                if user_mask.sum() == 0:
                    continue
                
                pos_user = pos_items[np.isin(pos_items, test_data.item_ids[user_mask])]
                neg_user = neg_items[np.isin(neg_items, test_data.item_ids[user_mask])]
                
                if len(pos_user) == 0 or len(neg_user) == 0:
                    continue
                
                # 采样
                n_sample = min(len(pos_user), len(neg_user), 50)
                pos_sample = np.random.choice(pos_user, n_sample, replace=False)
                neg_sample = np.random.choice(neg_user, n_sample, replace=False)
                
                scores_pos = model.predict(uid, pos_sample)
                scores_neg = model.predict(uid, neg_sample)
                
                auc_user = (scores_pos > scores_neg).mean()
                all_auc.append(auc_user)
            
            if all_auc:
                metrics['auc'] = np.mean(all_auc)
            else:
                metrics['auc'] = 0.5
        else:
            metrics['auc'] = 0.5
        
        logger.info(f"  AUC (fallback): {metrics['auc']:.4f}")
        return metrics
    
    def _build_user_items(self, data: FeatureData) -> Dict[int, set]:
        """构建用户-物品交互字典"""
        user_items = {}
        for i in range(len(data.user_ids)):
            uid = data.user_ids[i]
            iid = data.item_ids[i]
            if uid not in user_items:
                user_items[uid] = set()
            user_items[uid].add(iid)
        return user_items
    
    def _hit_rate_at_k(self, model, users: List[int], 
                       train_interactions: Dict, test_interactions: Dict,
                       all_items: set, k: int) -> float:
        """计算 Hit Rate @ K"""
        hits = 0
        total = 0
        
        for uid in users:
            train_items = train_interactions.get(uid, set())
            test_items = test_interactions.get(uid, set())
            
            # 正样本: 测试集中的物品
            if not test_items:
                continue
            
            # 负样本: 用户在训练集中没有交互过的物品
            neg_candidates = list(all_items - train_items - test_items)
            if len(neg_candidates) < self.neg_per_user:
                neg_candidates = list(all_items - train_items)
            
            if len(neg_candidates) < 1:
                continue
            
            # 采样负样本
            n_neg = min(self.neg_per_user, len(neg_candidates))
            neg_sample = np.random.choice(neg_candidates, n_neg, replace=False)
            
            # 候选物品 = 正样本 + 负样本
            # 从测试集中选1个正样本进行评估
            pos_item = np.random.choice(list(test_items))
            candidates = np.concatenate([[pos_item], neg_sample])
            
            # 模型预测
            scores = model.predict(uid, candidates)
            top_k_items = candidates[np.argsort(scores)[::-1][:k]]
            
            # 检查是否命中
            if pos_item in top_k_items:
                hits += 1
            total += 1
        
        return hits / total if total > 0 else 0.0
    
    def _mrr_at_k(self, model, users: List[int],
                  train_interactions: Dict, test_interactions: Dict,
                  all_items: set, k: int) -> float:
        """计算 MRR @ K (Mean Reciprocal Rank)"""
        mrr_sum = 0
        total = 0
        
        for uid in users:
            train_items = train_interactions.get(uid, set())
            test_items = test_interactions.get(uid, set())
            
            if not test_items:
                continue
            
            # 负样本
            neg_candidates = list(all_items - train_items - test_items)
            if len(neg_candidates) < self.neg_per_user:
                neg_candidates = list(all_items - train_items)
            
            if len(neg_candidates) < 1:
                continue
            
            n_neg = min(self.neg_per_user, len(neg_candidates))
            neg_sample = np.random.choice(neg_candidates, n_neg, replace=False)
            
            # 候选
            pos_item = np.random.choice(list(test_items))
            candidates = np.concatenate([[pos_item], neg_sample])
            
            # 预测
            scores = model.predict(uid, candidates)
            ranked_items = candidates[np.argsort(scores)[::-1]]
            
            # 找正样本排名
            rank = np.where(ranked_items == pos_item)[0]
            if len(rank) > 0 and rank[0] < k:
                mrr_sum += 1.0 / (rank[0] + 1)
            total += 1
        
        return mrr_sum / total if total > 0 else 0.0
    
    def _auc(self, model, users: List[int],
             train_interactions: Dict, test_interactions: Dict,
             all_items: set) -> float:
        """计算 AUC"""
        aucs = []
        
        for uid in users:
            train_items = train_interactions.get(uid, set())
            test_items = test_interactions.get(uid, set())
            
            if not test_items:
                continue
            
            # 负样本
            neg_candidates = list(all_items - train_items - test_items)
            if len(neg_candidates) < 10:
                neg_candidates = list(all_items - train_items)
            
            if len(neg_candidates) < 10:
                continue
            
            # 采样
            n_sample = min(50, len(neg_candidates), len(test_items))
            pos_sample = np.random.choice(list(test_items), n_sample, replace=False)
            neg_sample = np.random.choice(neg_candidates, n_sample, replace=False)
            
            # 预测
            scores_pos = model.predict(uid, pos_sample)
            scores_neg = model.predict(uid, neg_sample)
            
            # 计算 AUC
            auc_user = (scores_pos[:, None] > scores_neg[None, :]).mean()
            aucs.append(auc_user)
        
        return np.mean(aucs) if aucs else 0.5
    
    def _ndcg_at_k(self, model, users: List[int],
                   train_interactions: Dict, test_interactions: Dict,
                   all_items: set, k: int) -> float:
        """计算 NDCG @ K"""
        ndcg_sum = 0
        total = 0
        
        for uid in users:
            train_items = train_interactions.get(uid, set())
            test_items = test_interactions.get(uid, set())
            
            if not test_items:
                continue
            
            # 负样本
            neg_candidates = list(all_items - train_items - test_items)
            if len(neg_candidates) < self.neg_per_user:
                neg_candidates = list(all_items - train_items)
            
            if len(neg_candidates) < k:
                continue
            
            # 采样
            n_neg = min(self.neg_per_user, len(neg_candidates))
            neg_sample = np.random.choice(neg_candidates, n_neg, replace=False)
            
            # 候选 = 所有正样本 + 负样本
            pos_items = list(test_items)
            candidates = np.concatenate([pos_items, neg_sample])
            
            # 真实标签
            labels = np.concatenate([np.ones(len(pos_items)), np.zeros(len(neg_sample))])
            
            # 预测
            scores = model.predict(uid, candidates)
            ranked_idx = np.argsort(scores)[::-1][:k]
            ranked_labels = labels[ranked_idx]
            
            # DCG
            dcg = np.sum(ranked_labels / np.log2(np.arange(2, len(ranked_labels) + 2)))
            
            # IDCG
            ideal_ranked = np.sort(labels)[::-1][:k]
            idcg = np.sum(ideal_ranked / np.log2(np.arange(2, len(ideal_ranked) + 2)))
            
            ndcg = dcg / idcg if idcg > 0 else 0
            ndcg_sum += ndcg
            total += 1
        
        return ndcg_sum / total if total > 0 else 0.0
    
    def compare(self, results: Dict[str, Dict[str, float]]) -> 'pd.DataFrame':
        """对比多个模型的结果"""
        import pandas as pd
        return pd.DataFrame(results).T
