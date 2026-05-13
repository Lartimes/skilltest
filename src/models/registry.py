# -*- coding: utf-8 -*-
"""
推荐算法注册中心
使用装饰器模式注册和获取算法
"""

from typing import Dict, Type, Optional, Any
from .base import BaseRecommender
import logging

logger = logging.getLogger(__name__)


class RecommenderRegistry:
    """推荐算法注册中心
    
    Usage:
        @RecommenderRegistry.register('svd')
        class SVDRecommender(BaseRecommender):
            ...
        
        # 获取算法
        recommender = RecommenderRegistry.get('svd')(params)
    """
    
    _registry: Dict[str, Type[BaseRecommender]] = {}
    _config_registry: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, name: str, config: Optional[Dict[str, Any]] = None):
        """注册算法
        
        Args:
            name: 算法名称 (唯一标识)
            config: 算法默认配置
            
        Returns:
            装饰器函数
        """
        def decorator(recommender_class: Type[BaseRecommender]) -> Type[BaseRecommender]:
            if name in cls._registry:
                logger.warning(f"算法 '{name}' 已存在，将被覆盖")
            
            cls._registry[name] = recommender_class
            if config:
                cls._config_registry[name] = config
            
            logger.debug(f"注册算法: {name} -> {recommender_class.__name__}")
            return recommender_class
        
        return decorator
    
    @classmethod
    def get(cls, name: str) -> Type[BaseRecommender]:
        """获取算法类
        
        Args:
            name: 算法名称
            
        Returns:
            算法类
            
        Raises:
            KeyError: 算法不存在
        """
        if name not in cls._registry:
            available = list(cls._registry.keys())
            raise KeyError(
                f"算法 '{name}' 不存在. 可用的算法: {available}"
            )
        return cls._registry[name]
    
    @classmethod
    def get_config(cls, name: str) -> Dict[str, Any]:
        """获取算法配置"""
        return cls._config_registry.get(name, {})
    
    @classmethod
    def list_algorithms(cls) -> list:
        """列出所有注册的算法"""
        return list(cls._registry.keys())
    
    @classmethod
    def create(cls, name: str, **kwargs) -> BaseRecommender:
        """创建算法实例
        
        Args:
            name: 算法名称
            **kwargs: 算法参数
            
        Returns:
            算法实例
        """
        recommender_class = cls.get(name)
        return recommender_class(**kwargs)
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """注销算法"""
        if name in cls._registry:
            del cls._registry[name]
            if name in cls._config_registry:
                del cls._config_registry[name]
            return True
        return False


# 全局注册函数别名
register = RecommenderRegistry.register
get_algorithm = RecommenderRegistry.get
list_algorithms = RecommenderRegistry.list_algorithms
create_recommender = RecommenderRegistry.create
