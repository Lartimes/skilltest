"""
特征工程模块
"""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader as TorchDataLoader
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FeatureData:
    """特征数据容器"""
    def __init__(self, user_ids, item_ids, labels, 
                 user_feats=None, item_feats=None):
        self.user_ids = user_ids
        self.item_ids = item_ids
        self.labels = labels
        self.user_feats = user_feats
        self.item_feats = item_feats
        
        # 默认值
        self.n_users = 0
        self.n_items = 0
        self.n_user_onehot = 0
        self.n_user_dense = 0
        self.n_item_onehot = 0
        self.n_item_dense = 0
        self.idx2user = {}
        self.idx2item = {}
        self.user2idx = {}
        self.item2idx = {}


class FeatureProcessor:
    """特征处理器"""
    
    def __init__(self, data):
        """
        Args:
            data: RecommenderData 对象或 dict (interactions, user_features, item_features)
        """
        # 支持 dict 或 RecommenderData 对象
        if isinstance(data, dict):
            self.data = data
        else:
            # RecommenderData -> dict
            self.data = {
                'interactions': data.interactions,
                'user_features': data.user_features,
                'item_features': data.item_features,
            }
        self.user2idx = {}
        self.item2idx = {}
    
    def process(self, test_ratio: float = 0.2) -> Tuple[FeatureData, FeatureData]:
        """处理数据并划分 - 按用户分层划分"""
        df = self.data['interactions'].copy()
        
        # ID映射
        unique_users = df['user_id'].unique()
        unique_items = df['item_id'].unique()
        self.user2idx = {u: i for i, u in enumerate(unique_users)}
        self.item2idx = {v: i for i, v in enumerate(unique_items)}
        idx2user = {i: u for u, i in self.user2idx.items()}
        idx2item = {i: v for v, i in self.item2idx.items()}
        
        # 编码
        user_ids = df['user_id'].map(self.user2idx).values
        item_ids = df['item_id'].map(self.item2idx).values
        labels = df['label'].values.astype(np.float32)
        
        # 特征处理
        user_feats = self._process_user_features(df)
        item_feats = self._process_item_features(df)
        
        # 构建特征数据
        feature_data = FeatureData(user_ids, item_ids, labels, user_feats, item_feats)
        feature_data.n_users = len(unique_users)
        feature_data.n_items = len(unique_items)
        feature_data.idx2user = idx2user
        feature_data.idx2item = idx2item
        feature_data.user2idx = self.user2idx
        feature_data.item2idx = self.item2idx
        
        # ========== 按用户分层划分 ==========
        # 确保每个用户在训练集和测试集中都有记录
        np.random.seed(42)
        
        train_indices = []
        test_indices = []
        
        for uid in df['user_id'].unique():
            user_mask = df['user_id'] == uid
            user_indices = np.where(user_mask)[0]
            
            if len(user_indices) == 1:
                # 只有一条记录，随机分配
                if np.random.random() < (1 - test_ratio):
                    train_indices.extend(user_indices)
                else:
                    test_indices.extend(user_indices)
            else:
                # 按比例划分用户记录
                n_test = max(1, int(len(user_indices) * test_ratio))
                np.random.shuffle(user_indices)
                test_indices.extend(user_indices[:n_test])
                train_indices.extend(user_indices[n_test:])
        
        train_idx = np.array(train_indices)
        test_idx = np.array(test_indices)
        
        def subset(fd: FeatureData, idx: np.ndarray) -> FeatureData:
            return FeatureData(
                fd.user_ids[idx],
                fd.item_ids[idx],
                fd.labels[idx],
                fd.user_feats[idx] if fd.user_feats is not None else None,
                fd.item_feats[idx] if fd.item_feats is not None else None
            )
        
        train_data = subset(feature_data, train_idx)
        test_data = subset(feature_data, test_idx)
        train_data.n_users = test_data.n_users = feature_data.n_users
        train_data.n_items = test_data.n_items = feature_data.n_items
        train_data.idx2user = test_data.idx2user = idx2user
        train_data.idx2item = test_data.idx2item = idx2item
        train_data.user2idx = test_data.user2idx = self.user2idx
        train_data.item2idx = test_data.item2idx = self.item2idx
        
        logger.info(f"  训练集: {len(train_data.user_ids):,} 条")
        logger.info(f"  测试集: {len(test_data.user_ids):,} 条")
        
        # 统计有效评估用户
        train_users = set(train_data.user_ids)
        test_users = set(test_data.user_ids)
        valid_users = train_users & test_users
        logger.info(f"  有效评估用户: {len(valid_users):,} ({len(valid_users)/len(train_users | test_users)*100:.1f}%)")
        
        return train_data, test_data
    
    def _process_user_features(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """处理用户特征"""
        user_df = self.data.get('user_features')
        if user_df is None:
            return None
        
        user_df = user_df[user_df['user_id'].isin(df['user_id'].unique())]
        df_merged = df.merge(user_df, on='user_id', how='left')
        
        feature_cols = [c for c in user_df.columns if c != 'user_id']
        feats = df_merged[feature_cols].fillna(0).values.astype(np.float32)
        
        # 归一化
        if feats.shape[1] > 0:
            mins, maxs = feats.min(axis=0), feats.max(axis=0)
            ranges = maxs - mins
            ranges[ranges == 0] = 1
            feats = (feats - mins) / ranges
        
        return feats
    
    def _process_item_features(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """处理物品特征"""
        item_df = self.data.get('item_features')
        if item_df is None:
            return None
        
        item_df = item_df[item_df['item_id'].isin(df['item_id'].unique())]
        df_merged = df.merge(item_df, on='item_id', how='left')
        
        # 只选择数值类型的列
        feature_cols = [c for c in item_df.columns if c != 'item_id' 
                       and item_df[c].dtype in ['int64', 'float64', 'int32', 'float32']]
        
        if not feature_cols:
            return None
        
        feats = df_merged[feature_cols].fillna(0).values.astype(np.float32)
        
        if feats.shape[1] > 0:
            mins, maxs = feats.min(axis=0), feats.max(axis=0)
            ranges = maxs - mins
            ranges[ranges == 0] = 1
            feats = (feats - mins) / ranges
        
        return feats


class RecommenderDataset(Dataset):
    """PyTorch Dataset"""
    def __init__(self, data: FeatureData):
        self.user_ids = torch.LongTensor(data.user_ids)
        self.item_ids = torch.LongTensor(data.item_ids)
        self.labels = torch.FloatTensor(data.labels)
        self.user_feats = torch.FloatTensor(data.user_feats) if data.user_feats is not None else None
        self.item_feats = torch.FloatTensor(data.item_feats) if data.item_feats is not None else None
    
    def __len__(self):
        return len(self.user_ids)
    
    def __getitem__(self, idx):
        result = {
            'user_id': self.user_ids[idx],
            'item_id': self.item_ids[idx],
            'label': self.labels[idx],
        }
        if self.user_feats is not None:
            result['user_feats'] = self.user_feats[idx]
        if self.item_feats is not None:
            result['item_feats'] = self.item_feats[idx]
        return result


def create_dataloader(data: FeatureData, batch_size: int = 1024, shuffle: bool = True):
    """创建DataLoader"""
    return TorchDataLoader(
        RecommenderDataset(data),
        batch_size=batch_size,
        shuffle=shuffle
    )
