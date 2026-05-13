"""
src2 数据模块 - sources

数据源定义与元信息管理
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any, Callable
from enum import Enum

import pandas as pd


class DataSourceType(str, Enum):
    """数据源类型"""
    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"
    SQL = "sql"
    API = "api"


@dataclass
class ColumnSchema:
    """列Schema定义"""
    name: str
    dtype: str                    # pandas dtype 或 python type
    nullable: bool = True
    description: Optional[str] = None
    default: Any = None


@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    path: Path
    source_type: DataSourceType = DataSourceType.CSV
    encoding: str = "utf-8"
    
    # 分块加载配置
    chunk_size: Optional[int] = None
    n_rows: Optional[int] = None        # 采样行数
    
    # 列定义
    columns: list[ColumnSchema] = field(default_factory=list)
    usecols: Optional[list[str]] = None  # 指定读取的列
    
    # 数据源特定配置
    sep: str = ","
    parse_dates: list[str] = field(default_factory=list)
    dtype: dict[str, str] = field(default_factory=dict)
    
    # 内存优化
    low_memory: bool = True
    
    # 元信息
    description: Optional[str] = None
    version: str = "1.0.0"
    
    def __post_init__(self):
        self.path = Path(self.path)
    
    def get_cache_key(self) -> str:
        """生成缓存key"""
        import hashlib
        key_str = f"{self.name}:{self.path}:{self.version}"
        return hashlib.md5(key_str.encode()).hexdigest()


# 数据集列定义
USER_FEATURES_SCHEMA = [
    ColumnSchema("user_id", "int64", nullable=False, description="用户ID"),
    ColumnSchema("onehot_feat1", "int64", description="用户特征1"),
    ColumnSchema("onehot_feat2", "int64", description="用户特征2"),
    ColumnSchema("search_active_level", "int64", description="搜索活跃度等级(0-5)"),
    ColumnSchema("reco_active_level", "int64", description="推荐活跃度等级(0-5)"),
]

ITEM_FEATURES_SCHEMA = [
    ColumnSchema("video_id", "int64", nullable=False, description="视频ID"),
    ColumnSchema("caption", "object", description="视频标题/描述"),
    ColumnSchema("author_id", "int64", description="作者ID"),
    ColumnSchema("item_type", "object", description="物品类型"),
    ColumnSchema("upload_time", "object", description="上传时间"),
    ColumnSchema("upload_type", "object", description="上传类型"),
    ColumnSchema("music_id", "int64", description="背景音乐ID"),
    ColumnSchema("first_level_category_id", "int64", description="一级分类ID"),
    ColumnSchema("first_level_category_name", "object", description="一级分类名称"),
    ColumnSchema("second_level_category_id", "int64", description="二级分类ID"),
    ColumnSchema("second_level_category_name", "object", description="二级分类名称"),
    ColumnSchema("third_level_category_id", "int64", description="三级分类ID"),
    ColumnSchema("third_level_category_name", "object", description="三级分类名称"),
    ColumnSchema("fourth_level_category_id", "int64", description="四级分类ID"),
    ColumnSchema("fourth_level_category_name", "object", description="四级分类名称"),
]

REC_INTER_SCHEMA = [
    ColumnSchema("user_id", "int64", nullable=False, description="用户ID"),
    ColumnSchema("video_id", "int64", nullable=False, description="视频ID"),
    ColumnSchema("duration_ms", "int64", description="视频时长(毫秒)"),
    ColumnSchema("playing_time", "int64", description="播放时长(毫秒)"),
    ColumnSchema("timestamp", "int64", description="时间戳"),
    ColumnSchema("forward", "int64", description="是否转发(0/1)"),
    ColumnSchema("like", "int64", description="是否点赞(0/1)"),
    ColumnSchema("follow", "int64", description="是否关注(0/1)"),
    ColumnSchema("search_item_related", "int64", description="是否与搜索相关"),
    ColumnSchema("search", "int64", description="是否搜索"),
    ColumnSchema("click", "int64", description="是否点击"),
    ColumnSchema("time", "object", description="时间"),
]

SOCIAL_NETWORK_SCHEMA = [
    ColumnSchema("user_id", "int64", nullable=False, description="用户ID"),
    ColumnSchema("user_follow_id", "int64", nullable=False, description="关注用户ID"),
]

SRC_INTER_SCHEMA = [
    ColumnSchema("keyword", "object", description="搜索关键词"),
    ColumnSchema("video_id", "int64", nullable=False, description="视频ID"),
    ColumnSchema("click_cnt", "int64", description="点击次数"),
    ColumnSchema("search_session_id", "int64", description="搜索会话ID"),
    ColumnSchema("item_type", "object", description="物品类型"),
    ColumnSchema("user_id", "int64", nullable=False, description="用户ID"),
    ColumnSchema("search_session_timestamp", "int64", description="会话时间戳"),
    ColumnSchema("search_source", "object", description="搜索来源"),
    ColumnSchema("search_session_time", "object", description="会话时间"),
]


def create_data_source_configs(
    data_dir: Path,
    sample_mode: bool = False,
    sample_size: Optional[int] = None,
) -> dict[str, DataSourceConfig]:
    """
    创建数据源配置字典

    Args:
        data_dir: 数据目录
        sample_mode: 是否使用采样模式
        sample_size: 采样行数
    """
    base_dir = data_dir / "sample_1k" if sample_mode else data_dir
    
    configs = {
        "user_features": DataSourceConfig(
            name="user_features",
            path=base_dir / "user_features.csv",
            columns=USER_FEATURES_SCHEMA,
            description="用户特征数据",
        ),
        "item_features": DataSourceConfig(
            name="item_features",
            path=base_dir / "item_features.csv",
            columns=ITEM_FEATURES_SCHEMA,
            description="物品特征数据",
            low_memory=False,  # 大文件，不使用低内存模式
        ),
        "rec_inter": DataSourceConfig(
            name="rec_inter",
            path=base_dir / "rec_inter.csv",
            columns=REC_INTER_SCHEMA,
            description="推荐系统交互数据",
            parse_dates=["time"],
        ),
        "social_network": DataSourceConfig(
            name="social_network",
            path=base_dir / "social_network.csv",
            columns=SOCIAL_NETWORK_SCHEMA,
            description="社交网络数据",
        ),
        "src_inter": DataSourceConfig(
            name="src_inter",
            path=base_dir / "src_inter.csv",
            columns=SRC_INTER_SCHEMA,
            description="搜索交互数据",
        ),
    }
    
    # 如果指定了采样行数
    if sample_size:
        for config in configs.values():
            config.n_rows = sample_size
    
    return configs
