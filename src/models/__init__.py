"""
推荐模型模块
"""

# ============== 算法模块 ==============
from .algorithms import (
    MatrixFactorizationRecommender,
    NeuMFRecommender,
    DeepFMRecommender,
)

# ============== 基类和注册 ==============
from .base import BaseRecommender
from .registry import (
    register,
    get_algorithm as get,
    list_algorithms,
    create_recommender,
    RecommenderRegistry,
)

# ============== 数据模块 ==============
from .data import (
    DataLoader,
    RecommenderData,
    load_data,
    FeatureProcessor,
    FeatureData,
    RecommenderDataset,
    create_dataloader,
)

# ============== 评估模块 ==============
from .evaluation.metrics import RecommenderEvaluator

# ============== 运行模块 ==============
from .run import ModelRunner

__all__ = [
    # 基类和注册
    'BaseRecommender',
    'register',
    'get',
    'list_algorithms',
    'create_recommender',
    'RecommenderRegistry',
    
    # 算法
    'MatrixFactorizationRecommender',
    'NeuMFRecommender',
    'DeepFMRecommender',
    
    # 数据
    'DataLoader',
    'RecommenderData',
    'load_data',
    'FeatureProcessor',
    'FeatureData',
    'RecommenderDataset',
    'create_dataloader',
    
    # 评估
    'RecommenderEvaluator',
    
    # 运行器
    'ModelRunner',
]
