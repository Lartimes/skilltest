"""
src 数据模块

提供数据加载、清洗、验证等数据处理功能
"""

from .sources import (
    DataSourceType,
    ColumnSchema,
    DataSourceConfig,
    USER_FEATURES_SCHEMA,
    ITEM_FEATURES_SCHEMA,
    REC_INTER_SCHEMA,
    SOCIAL_NETWORK_SCHEMA,
    SRC_INTER_SCHEMA,
    create_data_source_configs,
)

from .loader import (
    LoadProgress,
    DataLoader,
    get_loader,
    load_data,
    load_cleaned_data,
    load_all_cleaned_data,
)

from .cleaner import (
    CleaningStep,
    CleaningReport,
    CleaningRule,
    DataCleaner,
    StreamingCleaner,
    get_cleaner,
    clean_data,
)

from .validator import (
    QualityLevel,
    ColumnQuality,
    DataQualityReport,
    SchemaValidator,
    DataValidator,
    validate_data_quality,
)

__all__ = [
    # sources
    "DataSourceType",
    "ColumnSchema",
    "DataSourceConfig",
    "USER_FEATURES_SCHEMA",
    "ITEM_FEATURES_SCHEMA",
    "REC_INTER_SCHEMA",
    "SOCIAL_NETWORK_SCHEMA",
    "SRC_INTER_SCHEMA",
    "create_data_source_configs",
    # loader
    "LoadProgress",
    "DataLoader",
    "get_loader",
    "load_data",
    "load_cleaned_data",
    "load_all_cleaned_data",
    # cleaner
    "CleaningStep",
    "CleaningReport",
    "CleaningRule",
    "DataCleaner",
    "StreamingCleaner",
    "get_cleaner",
    "clean_data",
    # validator
    "QualityLevel",
    "ColumnQuality",
    "DataQualityReport",
    "SchemaValidator",
    "DataValidator",
    "validate_data_quality",
]
