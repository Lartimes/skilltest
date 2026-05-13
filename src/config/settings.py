"""
src2 配置模块

提供生产级配置管理，支持多环境配置切换
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import yaml


class EnvMode(str, Enum):
    """环境模式"""
    DEV = "dev"           # 开发模式 - 使用采样数据
    PROD = "prod"         # 生产模式 - 使用全量数据
    FULL = "full"         # 全量模式 - 全量数据 + 完整特征


class DataSource(str, Enum):
    """数据源类型"""
    USER_FEATURES = "user_features"
    ITEM_FEATURES = "item_features"
    REC_INTERACTIONS = "rec_inter"
    SRC_INTERACTIONS = "src_inter"
    SOCIAL_NETWORK = "social_network"


@dataclass
class PathConfig:
    """路径配置"""
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = field(init=False)
    cache_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    log_dir: Path = field(init=False)

    def __post_init__(self):
        self.data_dir = self.project_root / "data"
        self.cache_dir = self.project_root / "cache" / "src2"
        self.output_dir = self.project_root / "output"
        self.log_dir = self.project_root / "logs"

        # 确保目录存在
        for d in [self.cache_dir, self.output_dir, self.log_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def get_data_path(self, source: DataSource, mode: EnvMode = EnvMode.DEV) -> Path:
        """获取数据文件路径"""
        # 根据模式选择不同的数据目录
        mode_dir_map = {
            EnvMode.DEV: self.data_dir / "sample_1k",  # 默认用采样数据
            EnvMode.PROD: self.data_dir,
            EnvMode.FULL: self.data_dir / "full_processed",
        }

        base_dir = mode_dir_map.get(mode, self.data_dir)

        # 文件名映射
        filename_map = {
            DataSource.USER_FEATURES: "user_features.csv",
            DataSource.ITEM_FEATURES: "item_features.csv",
            DataSource.REC_INTERACTIONS: "rec_inter.csv",
            DataSource.SRC_INTERACTIONS: "src_inter.csv",
            DataSource.SOCIAL_NETWORK: "social_network.csv",
        }

        return base_dir / filename_map[source]


@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    memory_max_size: int = 100        # 内存缓存最大条目数
    disk_ttl_seconds: int = 21600    # 磁盘缓存TTL: 6小时
    compress: bool = True            # 是否压缩缓存


@dataclass
class LoaderConfig:
    """数据加载器配置"""
    chunk_size: int = 50000          # 分块加载大小
    n_workers: int = 4               # 并行工作线程数
    retry_times: int = 3             # 重试次数
    retry_delay: float = 1.0         # 重试延迟(秒)
    timeout: float = 300.0          # 单次加载超时(秒)


@dataclass
class CleanerConfig:
    """数据清洗配置"""
    drop_duplicates: bool = True
    drop_null_threshold: float = 0.5  # 缺失率超过此比例则删除列
    fill_null_strategy: str = "median" # 填充策略: mean, median, mode, 0
    outlier_std: float = 3.0          # 使用多少倍标准差识别异常值


@dataclass
class DataQualityConfig:
    """数据质量检查配置"""
    check_missing: bool = True
    check_duplicates: bool = True
    check_outliers: bool = True
    check_dtype: bool = True
    report_format: str = "dict"       # 报告格式: dict, dataframe, json


@dataclass
class Config:
    """主配置类"""
    env_mode: EnvMode = EnvMode.DEV
    paths: PathConfig = field(default_factory=PathConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    loader: LoaderConfig = field(default_factory=LoaderConfig)
    cleaner: CleanerConfig = field(default_factory=CleanerConfig)
    quality: DataQualityConfig = field(default_factory=DataQualityConfig)

    # 数据源启用状态
    enabled_sources: list[DataSource] = field(default_factory=lambda: [
        DataSource.USER_FEATURES,
        DataSource.REC_INTERACTIONS,
        DataSource.ITEM_FEATURES,
    ])

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        """从YAML文件加载配置"""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "Config":
        """从字典创建配置"""
        def _dict_to_dataclass(dc_class, data_dict):
            if data_dict is None:
                return None
            field_values = {}
            for field_name, field_info in dc_class.__dataclass_fields__.items():
                if field_name in data_dict:
                    value = data_dict[field_name]
                    # 处理枚举类型
                    if field_info.type in (EnvMode, DataSource):
                        value = field_info.type(value) if isinstance(value, str) else value
                    # 处理嵌套dataclass
                    elif hasattr(field_info.type, "__dataclass_fields__"):
                        value = _dict_to_dataclass(field_info.type, value)
                    field_values[field_name] = value
            return dc_class(**field_values)

        return _dict_to_dataclass(cls, data)

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {}
        for field_name, field_info in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            if hasattr(value, "__dataclass_fields__"):
                result[field_name] = self._dataclass_to_dict(value)
            else:
                result[field_name] = value.value if isinstance(value, Enum) else value
        return result

    @staticmethod
    def _dataclass_to_dict(obj) -> dict:
        """dataclass转字典"""
        result = {}
        for field_name, field_info in obj.__dataclass_fields__.items():
            value = getattr(obj, field_name)
            if hasattr(value, "__dataclass_fields__"):
                result[field_name] = Config._dataclass_to_dict(value)
            else:
                result[field_name] = value.value if isinstance(value, Enum) else value
        return result


# 全局配置实例
_global_config: Config | None = None


def get_config() -> Config:
    """获取全局配置"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config) -> None:
    """设置全局配置"""
    global _global_config
    _global_config = config


def init_config(mode: EnvMode = EnvMode.DEV, config_path: str | Path | None = None) -> Config:
    """初始化配置"""
    if config_path:
        config = Config.from_yaml(config_path)
    else:
        config = Config(env_mode=mode)
    set_config(config)
    return config
