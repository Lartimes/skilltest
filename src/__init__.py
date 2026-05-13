"""
src2 - 混合推荐系统

生产级推荐系统框架，支持:
- 多级缓存数据加载
- 流水线式数据清洗
- 数据质量验证
- 特征工程
- LightFM 混合推荐模型
- 多指标评估
- 推荐生成服务
"""

__version__ = "2.0.0"

from . import config
from . import utils
from . import pre_pipeline
# from . import features
# from . import model
# from . import evaluation
# from . import recommendation

__all__ = [
    "config",
    "utils",
    "pre_pipeline",
    # "features",
    # "model",
    # "evaluation",
    # "recommendation",
]
