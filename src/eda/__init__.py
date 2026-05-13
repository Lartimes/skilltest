# -*- coding: utf-8 -*-
"""
EDA包 - 探索性数据分析
"""

from .base import BaseAnalyzer, DataLoader, clean_text, clean_series
from .user_distribution import UserDistributionAnalyzer
from .item_distribution import ItemDistributionAnalyzer
from .interaction_distribution import InteractionDistributionAnalyzer
from .table_relationship import TableRelationshipAnalyzer
from .social_network import SocialNetworkAnalyzer
from .temporal import TemporalAnalyzer
from .category import CategoryAnalyzer
from .correlation import CorrelationAnalyzer
from .funnel import FunnelAnalyzer
from .user_segmentation import UserSegmentationAnalyzer
from .retention import RetentionAnalyzer
from .search import SearchAnalyzer
from .item_quality import ItemQualityAnalyzer

# 分析器映射
ANALYZERS = {
    'user_distribution': UserDistributionAnalyzer,
    'item_distribution': ItemDistributionAnalyzer,
    'interaction_distribution': InteractionDistributionAnalyzer,
    'table_relationship': TableRelationshipAnalyzer,
    'social_network': SocialNetworkAnalyzer,
    'temporal': TemporalAnalyzer,
    'category': CategoryAnalyzer,
    'correlation': CorrelationAnalyzer,
    'funnel': FunnelAnalyzer,
    'user_segmentation': UserSegmentationAnalyzer,
    'retention': RetentionAnalyzer,
    'search': SearchAnalyzer,
    'item_quality': ItemQualityAnalyzer,
}

def run_eda():
    """便捷函数 - 运行所有分析"""
    from .run_eda import run_eda as _run_eda
    _run_eda()

__all__ = [
    'BaseAnalyzer',
    'DataLoader',
    'clean_text',
    'clean_series',
    'ANALYZERS',
    'run_eda',
]
