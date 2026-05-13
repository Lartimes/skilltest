"""
src 工具模块 - decorators

提供常用装饰器: 重试、耗时统计、缓存
"""

import functools
import time
import hashlib
import json
from typing import Callable, Any, Optional, TypeVar, Union
from pathlib import Path

T = TypeVar("T")


def retry(
    max_times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[Any] = None,
):
    """
    指数退避重试装饰器

    Args:
        max_times: 最大重试次数
        delay: 初始延迟(秒)
        backoff: 退避系数
        exceptions: 需要重试的异常类型
        logger: 日志记录器
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_times:
                        if logger:
                            logger.warning(
                                f"[{func.__name__}] 第{attempt + 1}次尝试失败: {e}, "
                                f"{current_delay:.1f}秒后重试..."
                            )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        if logger:
                            logger.error(f"[{func.__name__}] 达到最大重试次数({max_times}), 失败")
                        raise last_exception

            raise last_exception

        return wrapper
    return decorator


def timing(logger: Optional[Any] = None, name: Optional[str] = None):
    """
    耗时统计装饰器

    Args:
        logger: 日志记录器
        name: 自定义计时名称
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            func_name = name or func.__name__

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                if logger:
                    if elapsed > 60:
                        logger.warning(f"[{func_name}] 耗时: {elapsed:.2f}秒 ({elapsed/60:.1f}分钟)")
                    else:
                        logger.info(f"[{func_name}] 耗时: {elapsed:.2f}秒")

                return result
            except Exception as e:
                elapsed = time.time() - start_time
                if logger:
                    logger.error(f"[{func_name}] 执行失败, 耗时: {elapsed:.2f}秒, 错误: {e}")
                raise

        return wrapper
    return decorator


def log_calls(logger: Optional[Any] = None, level: str = "DEBUG"):
    """
    函数调用日志装饰器

    Args:
        logger: 日志记录器
        level: 日志级别
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            log_fn = getattr(logger, level.lower(), logger.info)

            # 记录入参(截断过长参数)
            args_repr = [
                repr(a) if len(str(a)) < 100 else f"{str(a)[:50]}...{str(a)[-50:]}"
                for a in args
            ]
            kwargs_repr = {
                k: repr(v) if len(str(v)) < 100 else f"{str(v)[:50]}...{str(v)[-50:]}"
                for k, v in kwargs.items()
            }

            log_fn(f"[调用] {func.__name__}({', '.join(args_repr)}, {kwargs_repr})")

            try:
                result = func(*args, **kwargs)
                log_fn(f"[返回] {func.__name__} => {type(result).__name__}")
                return result
            except Exception as e:
                log_fn(f"[异常] {func.__name__}: {e}")
                raise

        return wrapper
    return decorator


def cache_result(
    cache: Any = None,
    key_func: Optional[Callable[..., str]] = None,
    ttl: Optional[float] = None,
):
    """
    结果缓存装饰器

    Args:
        cache: 缓存对象(需实现get/set接口)
        key_func: 生成缓存key的函数
        ttl: 缓存过期时间(秒)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # 如果没有传入cache, 使用全局缓存
        _cache = cache

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            nonlocal _cache

            # 生成缓存key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名+参数hash
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key_str = "|".join(key_parts)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()

            # 尝试从缓存获取
            if _cache is None:
                try:
                    from .cache import get_cache
                    _cache = get_cache()
                except ImportError:
                    return func(*args, **kwargs)

            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            _cache.set(cache_key, result)

            return result

        return wrapper
    return decorator


def deprecated(reason: str = "", version: str = ""):
    """
    标记废弃函数装饰器

    Args:
        reason: 废弃原因
        version: 废弃版本
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            msg = f"[废弃警告] {func.__name__} 已废弃"
            if version:
                msg += f" (v{version})"
            if reason:
                msg += f": {reason}"
            import warnings
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper
    return decorator


def validate_args(**validators):
    """
    参数验证装饰器

    Args:
        validators: {参数名: 验证函数} 字典
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # 获取函数签名
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # 验证参数
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"参数 {param_name}={value} 验证失败"
                        )

            return func(*args, **kwargs)

        return wrapper
    return decorator


def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """
    简单内存记忆化装饰器 (无外部依赖)
    """
    cache: dict = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # 生成key
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper
