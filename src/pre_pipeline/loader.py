"""
src2 数据模块 - loader

生产级数据加载器，支持:
- 分块加载 (大文件处理)
- 多级缓存
- 指数退避重试
- 进度回调
- 内存优化
"""

import hashlib
import time
from pathlib import Path
from typing import Optional, Callable, Any, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

from ..config.settings import Config, DataSource, EnvMode, get_config
from ..utils.logging import get_logger, Logger
from ..utils.cache import MultiLevelCache, get_cache
from ..utils.decorators import retry, timing


@dataclass
class LoadProgress:
    """加载进度"""
    source: str
    total_chunks: int
    processed_chunks: int = 0
    rows_loaded: int = 0
    start_time: float = 0
    elapsed_seconds: float = 0

    @property
    def progress_percent(self) -> float:
        if self.total_chunks == 0:
            return 0
        return self.processed_chunks / self.total_chunks * 100

    @property
    def rows_per_second(self) -> float:
        if self.elapsed_seconds == 0:
            return 0
        return self.rows_loaded / self.elapsed_seconds


class DataLoader:
    """
    生产级数据加载器

    Features:
        - 分块加载 (chunksize)
        - 多级缓存 (内存 + 磁盘)
        - 指数退避重试
        - 进度回调
        - 类型自动推断 + 优化
        - 采样支持
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        cache: Optional[MultiLevelCache] = None,
        logger: Optional[Logger] = None,
    ):
        self.config = config or get_config()
        self.cache = cache or get_cache()
        self.logger = logger or get_logger()
        
        # 加载统计
        self._load_stats: dict[str, dict] = {}

    @retry(max_times=3, delay=1.0, exceptions=(OSError, pd.errors.ParserError))
    def load(
        self,
        source: Union[str, Path, DataSource],
        use_cache: bool = True,
        n_rows: Optional[int] = None,
        usecols: Optional[list[str]] = None,
        dtype: Optional[dict] = None,
        parse_dates: Optional[list[str]] = None,
        progress_callback: Optional[Callable[[LoadProgress], None]] = None,
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """
        加载数据文件

        Args:
            source: 数据源 (DataSource枚举 或 路径)
            use_cache: 是否使用缓存
            n_rows: 采样行数
            usecols: 只读取指定列
            dtype: 列类型字典
            parse_dates: 需要解析为日期的列
            progress_callback: 进度回调函数
            show_progress: 是否显示进度条

        Returns:
            pd.DataFrame
        """
        # 转换source为路径
        if isinstance(source, DataSource):
            path = self.config.paths.get_data_path(source, self.config.env_mode)
        else:
            path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在: {path}")

        # 生成缓存key
        cache_key = self._generate_cache_key(path, n_rows, usecols, dtype)

        # 检查缓存
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                self.logger.info(f"[缓存命中] {path.name}, 形状: {cached_data.shape}")
                return cached_data

        self.logger.info(f"开始加载: {path.name}")
        start_time = time.time()

        try:
            # 分块加载大文件
            if self._is_large_file(path):
                df = self._load_chunked(
                    path,
                    n_rows=n_rows,
                    usecols=usecols,
                    dtype=dtype,
                    parse_dates=parse_dates,
                    progress_callback=progress_callback,
                    show_progress=show_progress,
                )
            else:
                df = self._load_full(
                    path,
                    n_rows=n_rows,
                    usecols=usecols,
                    dtype=dtype,
                    parse_dates=parse_dates,
                )

            # 内存优化
            df = self._optimize_memory(df)

            # 更新统计
            elapsed = time.time() - start_time
            self._load_stats[str(path)] = {
                "rows": len(df),
                "cols": len(df.columns),
                "memory_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                "elapsed_sec": elapsed,
            }

            self.logger.info(
                f"加载完成: {path.name}, "
                f"形状: {df.shape}, "
                f"内存: {self._load_stats[str(path)]['memory_mb']:.2f}MB, "
                f"耗时: {elapsed:.2f}秒"
            )

            # 更新缓存
            if use_cache:
                self.cache.set(cache_key, df)

            return df

        except Exception as e:
            self.logger.error(f"加载失败: {path.name}, 错误: {e}")
            raise

    def _load_full(
        self,
        path: Path,
        n_rows: Optional[int] = None,
        usecols: Optional[list[str]] = None,
        dtype: Optional[dict] = None,
        parse_dates: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """一次性加载小文件"""
        return pd.read_csv(
            path,
            nrows=n_rows,
            usecols=usecols,
            dtype=dtype,
            parse_dates=parse_dates,
            low_memory=self.config.loader.chunk_size is None,
            encoding="utf-8",
        )

    def _load_chunked(
        self,
        path: Path,
        n_rows: Optional[int] = None,
        usecols: Optional[list[str]] = None,
        dtype: Optional[dict] = None,
        parse_dates: Optional[list[str]] = None,
        progress_callback: Optional[Callable[[LoadProgress], None]] = None,
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """分块加载大文件"""
        chunk_size = self.config.loader.chunk_size

        # 估算总行数
        total_lines = sum(1 for _ in open(path, encoding="utf-8", errors="ignore"))
        total_chunks = (min(total_lines, n_rows or float("inf")) // chunk_size) + 1

        progress = LoadProgress(
            source=str(path),
            total_chunks=total_chunks,
            start_time=time.time(),
        )

        chunks = []
        rows_loaded = 0

        iterator = pd.read_csv(
            path,
            chunksize=chunk_size,
            usecols=usecols,
            dtype=dtype,
            parse_dates=parse_dates,
            low_memory=False,
            encoding="utf-8",
        )

        if show_progress:
            iterator = tqdm(
                iterator,
                total=min(total_chunks, (n_rows or float("inf")) // chunk_size),
                desc=f"加载 {path.name}",
                unit="chunk",
            )

        for chunk in iterator:
            # 检查是否达到采样数
            if n_rows and rows_loaded >= n_rows:
                break

            # 截断到采样数
            if n_rows:
                remaining = n_rows - rows_loaded
                chunk = chunk.head(remaining)

            chunks.append(chunk)
            rows_loaded += len(chunk)

            # 更新进度
            progress.processed_chunks += 1
            progress.rows_loaded = rows_loaded
            progress.elapsed_seconds = time.time() - progress.start_time

            if progress_callback:
                progress_callback(progress)

        if not chunks:
            return pd.DataFrame()

        df = pd.concat(chunks, ignore_index=True)

        # 更新进度
        progress.processed_chunks = progress.total_chunks
        if progress_callback:
            progress_callback(progress)

        return df

    def _is_large_file(self, path: Path, threshold_mb: int = 100) -> bool:
        """判断是否是大文件"""
        size_mb = path.stat().st_size / 1024 / 1024
        return size_mb > threshold_mb

    def _generate_cache_key(
        self,
        path: Path,
        n_rows: Optional[int] = None,
        usecols: Optional[list[str]] = None,
        dtype: Optional[dict] = None,
    ) -> str:
        """生成缓存key"""
        parts = [
            str(path.absolute()),
            str(n_rows or ""),
            "|".join(sorted(usecols)) if usecols else "",
            "|".join(f"{k}:{v}" for k, v in sorted(dtype.items())) if dtype else "",
        ]
        key_str = "_".join(parts)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _optimize_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """内存优化"""
        # 数值类型优化
        for col in df.select_dtypes(include=["int64"]).columns:
            col_min = df[col].min()
            col_max = df[col].max()

            if col_min >= 0:
                if col_max < 255:
                    df[col] = df[col].astype("uint8")
                elif col_max < 65535:
                    df[col] = df[col].astype("uint16")
                elif col_max < 4294967295:
                    df[col] = df[col].astype("uint32")
            else:
                if col_min > -128 and col_max < 127:
                    df[col] = df[col].astype("int8")
                elif col_min > -32768 and col_max < 32767:
                    df[col] = df[col].astype("int16")
                elif col_min > -2147483648 and col_max < 2147483647:
                    df[col] = df[col].astype("int32")

        # 浮点类型优化
        for col in df.select_dtypes(include=["float64"]).columns:
            df[col] = df[col].astype("float32")

        return df

    @timing(logger=None)
    def load_multiple(
        self,
        sources: list[Union[str, Path, DataSource]],
        parallel: bool = False,
        n_workers: int = 4,
    ) -> dict[str, pd.DataFrame]:
        """
        批量加载多个数据源

        Args:
            sources: 数据源列表
            parallel: 是否并行加载
            n_workers: 并行工作数

        Returns:
            {数据源名称: DataFrame} 字典
        """
        results = {}

        if parallel:
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                futures = {
                    executor.submit(self.load, src): src for src in sources
                }
                for future in as_completed(futures):
                    src = futures[future]
                    try:
                        results[str(src)] = future.result()
                    except Exception as e:
                        self.logger.error(f"加载 {src} 失败: {e}")
        else:
            for src in sources:
                try:
                    results[str(src)] = self.load(src)
                except Exception as e:
                    self.logger.error(f"加载 {src} 失败: {e}")

        return results

    def get_load_stats(self) -> dict:
        """获取加载统计"""
        return self._load_stats.copy()

    def clear_cache(self, source: Optional[str] = None):
        """清除缓存"""
        if source:
            self.cache.delete(source)
        else:
            self.cache.clear()


# 便捷函数
_default_loader: Optional[DataLoader] = None


def get_loader() -> DataLoader:
    """获取全局数据加载器"""
    global _default_loader
    if _default_loader is None:
        _default_loader = DataLoader()
    return _default_loader


def load_data(
    source: Union[str, Path, DataSource],
    **kwargs,
) -> pd.DataFrame:
    """便捷加载函数"""
    return get_loader().load(source, **kwargs)


# 清洗后数据的便捷加载
import pandas as pd
from pathlib import Path


def load_cleaned_data(
    dataset_name: str,
    cleaned_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    加载清洗后的parquet数据
    
    Args:
        dataset_name: 数据集名称 (user_features, item_features, rec_inter)
        cleaned_dir: 清洗后数据目录，默认使用 output/cleaned
    
    Returns:
        pd.DataFrame
    
    Example:
        >>> df = load_cleaned_data("user_features")
        >>> df = load_cleaned_data("rec_inter", cleaned_dir=Path("my_data/cleaned"))
    """
    if cleaned_dir is None:
        # 默认使用项目下的 output/cleaned 目录
        project_root = Path(__file__).parent.parent.parent
        cleaned_dir = project_root / "output" / "cleaned"
    
    # 文件名映射
    filename_map = {
        "user_features": "user_features_clean.parquet",
        "item_features": "item_features_clean.parquet",
        "rec_inter": "rec_inter_clean.parquet",
        "rec_interactions": "rec_inter_clean.parquet",
        "social_network": "social_network_clean.parquet",
        "src_inter": "src_inter_clean.parquet",
    }
    
    filename = filename_map.get(dataset_name, f"{dataset_name}_clean.parquet")
    filepath = cleaned_dir / filename
    
    if not filepath.exists():
        raise FileNotFoundError(
            f"清洗后的数据文件不存在: {filepath}\n"
            f"请先运行 save_cleaned_data.py 生成数据"
        )
    
    return pd.read_parquet(filepath)


def load_all_cleaned_data(
    cleaned_dir: Optional[Path] = None,
) -> dict[str, pd.DataFrame]:
    """
    加载所有清洗后的数据
    
    Returns:
        dict: {数据集名: DataFrame}
    
    Example:
        >>> pre_pipeline = load_all_cleaned_data()
        >>> df_user = pre_pipeline["user_features"]
        >>> df_item = pre_pipeline["item_features"]
        >>> df_inter = pre_pipeline["rec_inter"]
    """
    return {
        "user_features": load_cleaned_data("user_features", cleaned_dir),
        "item_features": load_cleaned_data("item_features", cleaned_dir),
        "rec_inter": load_cleaned_data("rec_inter", cleaned_dir),
    }
