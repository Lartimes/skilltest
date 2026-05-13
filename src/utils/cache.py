"""
src2 工具模块 - cache

提供多层缓存机制（内存 + 磁盘）
"""

import hashlib
import json
import pickle
import zlib
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, TypeVar, Generic
from threading import RLock

import pandas as pd

T = TypeVar("T")


@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    saves: int = 0
    loads: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class MemoryCache(Generic[T]):
    """内存缓存 (LRU)"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = RLock()

    def get(self, key: str) -> Optional[T]:
        """获取缓存"""
        with self._lock:
            if key in self._cache:
                value, expire_time = self._cache[key]
                # 检查是否过期
                if expire_time < time.time():
                    del self._cache[key]
                    return None
                # 移到末尾(最新使用)
                self._cache.move_to_end(key)
                return value
            return None

    def set(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """设置缓存"""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self.max_size:
                    # 删除最旧的
                    self._cache.popitem(last=False)
            
            expire_time = time.time() + ttl if ttl else float("inf")
            self._cache[key] = (value, expire_time)

    def delete(self, key: str) -> bool:
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()

    def cleanup(self) -> int:
        """清理过期项"""
        with self._lock:
            now = time.time()
            expired_keys = [
                k for k, (_, expire_time) in self._cache.items()
                if expire_time < now
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    def __len__(self) -> int:
        return len(self._cache)


class DiskCache:
    """磁盘缓存"""

    def __init__(self, cache_dir: Path, ttl: float = 21600, compress: bool = True):
        """
        Args:
            cache_dir: 缓存目录
            ttl: 缓存过期时间(秒), 默认6小时
            compress: 是否压缩
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.compress = compress
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 对key进行hash，避免特殊字符问题
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return None

            try:
                # 检查是否过期
                mtime = cache_path.stat().st_mtime
                if time.time() - mtime > self.ttl:
                    cache_path.unlink()
                    return None

                with open(cache_path, "rb") as f:
                    if self.compress:
                        data = zlib.decompress(f.read())
                    else:
                        data = f.read()
                    return pickle.loads(data)
            except Exception:
                return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        with self._lock:
            cache_path = self._get_cache_path(key)
            try:
                data = pickle.dumps(value)
                if self.compress:
                    data = zlib.compress(data)
                with open(cache_path, "wb") as f:
                    f.write(data)
            except Exception:
                pass

    def delete(self, key: str) -> bool:
        """删除缓存"""
        with self._lock:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                return True
            return False

    def clear(self) -> int:
        """清空所有缓存"""
        with self._lock:
            count = 0
            for f in self.cache_dir.glob("*.pkl"):
                f.unlink()
                count += 1
            return count

    def cleanup(self) -> int:
        """清理过期缓存"""
        with self._lock:
            count = 0
            now = time.time()
            for f in self.cache_dir.glob("*.pkl"):
                if now - f.stat().st_mtime > self.ttl:
                    f.unlink()
                    count += 1
            return count

    def __len__(self) -> int:
        return len(list(self.cache_dir.glob("*.pkl")))


class MultiLevelCache:
    """多级缓存 (L1: 内存 -> L2: 磁盘)"""

    def __init__(
        self,
        memory: Optional[MemoryCache] = None,
        disk: Optional[DiskCache] = None,
    ):
        self.memory = memory or MemoryCache(max_size=100)
        self.disk = disk or DiskCache(cache_dir=Path("cache"), ttl=21600)
        self.stats = CacheStats()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存, 先查L1, 再查L2"""
        # L1 命中
        value = self.memory.get(key)
        if value is not None:
            self.stats.hits += 1
            return value

        # L2 命中
        value = self.disk.get(key)
        if value is not None:
            # 回填L1
            self.memory.set(key, value)
            self.stats.hits += 1
            self.stats.loads += 1
            return value

        self.stats.misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存, 同时写入L1和L2"""
        self.memory.set(key, value)
        self.disk.set(key, value)
        self.stats.saves += 1

    def delete(self, key: str) -> bool:
        """删除缓存"""
        mem_deleted = self.memory.delete(key)
        disk_deleted = self.disk.delete(key)
        return mem_deleted or disk_deleted

    def clear(self) -> None:
        """清空所有缓存"""
        self.memory.clear()
        self.disk.clear()
        self.stats = CacheStats()

    def cleanup(self) -> dict:
        """清理过期缓存"""
        mem_cleaned = self.memory.cleanup()
        disk_cleaned = self.disk.cleanup()
        return {"memory": mem_cleaned, "disk": disk_cleaned}


# 全局缓存实例
_global_cache: Optional[MultiLevelCache] = None


def get_cache() -> MultiLevelCache:
    """获取全局缓存"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLevelCache()
    return _global_cache


def set_cache(cache: MultiLevelCache) -> None:
    """设置全局缓存"""
    global _global_cache
    _global_cache = cache


def init_cache(
    memory_max_size: int = 100,
    disk_cache_dir: Path | str = Path("cache/src2"),
    disk_ttl: float = 21600,
    compress: bool = True,
) -> MultiLevelCache:
    """初始化缓存"""
    cache = MultiLevelCache(
        memory=MemoryCache(max_size=memory_max_size),
        disk=DiskCache(
            cache_dir=Path(disk_cache_dir),
            ttl=disk_ttl,
            compress=compress,
        ),
    )
    set_cache(cache)
    return cache
