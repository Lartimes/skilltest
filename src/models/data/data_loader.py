"""
数据加载模块
统一加载交互数据、用户特征、物品特征
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class RecommenderData:
    """推荐系统数据容器"""
    interactions: pd.DataFrame  # 交互数据
    user_features: Optional[pd.DataFrame] = None  # 用户特征
    item_features: Optional[pd.DataFrame] = None  # 物品特征
    
    # 特征维度信息
    n_users: int = 0
    n_items: int = 0
    n_user_features: int = 0
    n_item_features: int = 0
    
    # ID映射
    user2idx: dict = field(default_factory=dict)
    idx2user: dict = field(default_factory=dict)
    item2idx: dict = field(default_factory=dict)
    idx2item: dict = field(default_factory=dict)


class DataLoader:
    """推荐系统数据加载器"""
    
    # 项目根目录: src/models/data/__file__ -> parent -> parent -> parent -> parent = 项目根
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
    
    def __init__(self, data_dir: str = None):
        # 默认使用项目根目录/output/cleaned
        if data_dir is None:
            data_dir = self.PROJECT_ROOT / 'output' / 'cleaned'
        else:
            data_dir = Path(data_dir)
            # 如果是相对路径，转换为相对于项目根目录的绝对路径
            if not data_dir.is_absolute():
                data_dir = self.PROJECT_ROOT / data_dir
        self.data_dir = data_dir
        self._validate_data_dir()
    
    def _validate_data_dir(self):
        """验证数据目录"""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"数据目录不存在: {self.data_dir}")
        
        # 检查必要文件（优先 parquet，其次 csv）
        rec_parquet = self.data_dir / 'rec_inter_clean.parquet'
        rec_csv = self.data_dir / 'rec_inter.csv'
        if not rec_parquet.exists() and not rec_csv.exists():
            raise FileNotFoundError(f"交互数据文件不存在: {rec_parquet} 或 {rec_csv}")
        
        logger.info(f"数据目录: {self.data_dir}")
    
    def load(self, 
             sample_size: Optional[int] = None,
             random_state: int = 42) -> RecommenderData:
        """
        加载所有数据
        
        Args:
            sample_size: 采样数量，None表示全量
            random_state: 随机种子
        
        Returns:
            RecommenderData对象
        """
        logger.info("=" * 50)
        logger.info("开始加载数据...")
        
        # 1. 加载交互数据
        logger.info("加载交互数据...")
        df_inter = self._load_interactions(sample_size, random_state)
        
        # 2. 加载用户特征
        logger.info("加载用户特征...")
        df_user = self._load_user_features()
        
        # 3. 加载物品特征
        logger.info("加载物品特征...")
        df_item = self._load_item_features()
        
        # 4. 构建数据容器
        data = RecommenderData(
            interactions=df_inter,
            user_features=df_user,
            item_features=df_item,
            n_users=df_inter['user_id'].nunique(),
            n_items=df_inter['item_id'].nunique(),
        )
        
        # 5. 统计信息
        logger.info(f"  用户数: {data.n_users:,}")
        logger.info(f"  物品数: {data.n_items:,}")
        logger.info(f"  交互数: {len(df_inter):,}")
        if df_user is not None:
            data.n_user_features = len(df_user.columns) - 1  # 减去user_id
            logger.info(f"  用户特征数: {data.n_user_features}")
        if df_item is not None:
            data.n_item_features = len(df_item.columns) - 1  # 减去item_id
            logger.info(f"  物品特征数: {data.n_item_features}")
        
        return data
    
    def _load_interactions(self, 
                          sample_size: Optional[int],
                          random_state: int) -> pd.DataFrame:
        """加载交互数据"""
        # 优先读取 parquet 文件，其次 csv
        parquet_path = self.data_dir / 'rec_inter_clean.parquet'
        csv_path = self.data_dir / 'rec_inter.csv'
        
        if parquet_path.exists():
            file_path = parquet_path
            logger.info("  使用 parquet 格式加载交互数据...")
            if sample_size is not None:
                df = pd.read_parquet(file_path)
                if len(df) > sample_size:
                    df = df.sample(n=sample_size, random_state=random_state)
            else:
                df = pd.read_parquet(file_path)
        else:
            file_path = csv_path
            logger.info("  使用 csv 格式加载交互数据...")
            # 确定需要的列
            usecols = ['user_id', 'item_id']
            
            # 读取少量行获取列信息
            df_sample = pd.read_csv(file_path, nrows=10)
            available_cols = set(df_sample.columns)
            
            # 添加可选列
            optional_cols = ['watch_ratio', 'watch_time', 'like', 'share', 'comment', 'date']
            for col in optional_cols:
                if col in available_cols:
                    usecols.append(col)
            
            # 分块读取大文件
            if sample_size is not None:
                df = pd.read_csv(file_path, usecols=usecols, nrows=sample_size, 
                               random_state=random_state)
            else:
                # 使用分块读取
                chunks = []
                chunk_size = 100000
                for chunk in pd.read_csv(file_path, usecols=usecols, chunksize=chunk_size):
                    chunks.append(chunk)
                df = pd.concat(chunks, ignore_index=True)
        
        # 统一列名
        if 'video_id' in df.columns:
            df = df.rename(columns={'video_id': 'item_id'})
        
        # 确保必要的列存在
        required_cols = ['user_id', 'item_id']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"交互数据缺少必要列: {col}")
        
        # 创建标签 - 使用 like 或 click 列（如果有的话）
        # 这是有区分度的标签，可以训练推荐模型
        if 'label' in df.columns:
            df['label'] = df['label'].astype(float)
        elif 'watch_ratio' in df.columns:
            df['label'] = df['watch_ratio'].astype(float)
        elif 'like' in df.columns and 'click' in df.columns:
            # 使用 like 或 click 作为标签（有区分度）
            df['label'] = ((df['like'] == 1) | (df['click'] == 1)).astype(float)
            logger.info("  使用 like/click 作为标签")
        elif 'like' in df.columns:
            df['label'] = df['like'].astype(float)
            logger.info("  使用 like 作为标签")
        elif 'click' in df.columns:
            df['label'] = df['click'].astype(float)
            logger.info("  使用 click 作为标签")
        else:
            # 没有可用的标签，使用播放时长归一化作为软标签
            if 'playing_time' in df.columns and 'duration_ms' in df.columns:
                df['label'] = (df['playing_time'] / (df['duration_ms'] + 1)).clip(0, 1).astype(float)
                logger.info("  使用播放时长比例作为标签")
            else:
                df['label'] = 1.0
                logger.warning("  无可用标签，设为1.0（模型可能无法有效学习）")
        
        logger.info(f"  交互数据: {len(df):,} 条")
        return df
    
    def _load_user_features(self) -> Optional[pd.DataFrame]:
        """加载用户特征"""
        # 支持多种文件名格式
        possible_names = [
            'user_features_clean.parquet',
            'user_features.parquet',
            'user_features.csv',
        ]
        
        file_path = None
        for name in possible_names:
            p = self.data_dir / name
            if p.exists():
                file_path = p
                break
        
        if file_path is None:
            logger.warning("  用户特征文件不存在")
            return None
        
        try:
            if file_path.suffix == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # 统一列名
            if 'user_id' not in df.columns and 'uid' in df.columns:
                df = df.rename(columns={'uid': 'user_id'})
            
            logger.info(f"  用户特征: {len(df.columns) - 1} 维, {len(df):,} 条")
            return df
        except Exception as e:
            logger.warning(f"  加载用户特征失败: {e}")
            return None
    
    def _load_item_features(self) -> Optional[pd.DataFrame]:
        """加载物品特征"""
        # 支持多种文件名格式
        possible_names = [
            'item_features_clean.parquet',
            'item_features.parquet',
            'item_features.csv',
        ]
        
        file_path = None
        for name in possible_names:
            p = self.data_dir / name
            if p.exists():
                file_path = p
                break
        
        if file_path is None:
            logger.warning("  物品特征文件不存在")
            return None
        
        try:
            if file_path.suffix == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                df = pd.read_csv(file_path, nrows=500000)
            
            # 统一列名
            if 'item_id' not in df.columns and 'video_id' in df.columns:
                df = df.rename(columns={'video_id': 'item_id'})
            
            logger.info(f"  物品特征: {len(df.columns) - 1} 维, {len(df):,} 条")
            return df
        except Exception as e:
            logger.warning(f"  加载物品特征失败: {e}")
            return None


def load_data(data_dir: str = None, 
              sample_size: Optional[int] = None) -> RecommenderData:
    """便捷加载函数"""
    loader = DataLoader(data_dir)
    return loader.load(sample_size=sample_size)
