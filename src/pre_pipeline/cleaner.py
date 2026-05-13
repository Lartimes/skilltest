"""
src2 数据模块 - cleaner

数据清洗流水线，支持:
- 流水线式清洗
- 可配置的清洗规则
- 增量清洗
- 清洗报告生成
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any, Union, Callable
from enum import Enum
import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm

from ..config.settings import Config, CleanerConfig, get_config
from ..utils.logging import get_logger, Logger


class CleaningStep(str, Enum):
    """清洗步骤枚举"""
    DROP_DUPLICATES = "drop_duplicates"
    HANDLE_MISSING = "handle_missing"
    DROP_MISSING_COLS = "drop_missing_cols"
    HANDLE_OUTLIERS = "handle_outliers"
    FIX_TYPES = "fix_types"
    VALIDATE_SCHEMA = "validate_schema"
    FILTER_INVALID = "filter_invalid"
    DEDUPLICATE_IDS = "deduplicate_ids"


@dataclass
class CleaningReport:
    """清洗报告"""
    original_shape: tuple[int, int]
    final_shape: tuple[int, int]
    rows_removed: int = 0
    cols_removed: int = 0
    duplicates_removed: int = 0
    missing_filled: dict = field(default_factory=dict)
    outliers_handled: dict = field(default_factory=dict)
    invalid_filtered: dict = field(default_factory=dict)
    schema_validations: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def rows_removed_pct(self) -> float:
        if self.original_shape[0] == 0:
            return 0
        return self.rows_removed / self.original_shape[0] * 100

    @property
    def memory_saved_mb(self) -> float:
        return 0.0  # 简化实现

    def to_dict(self) -> dict:
        return {
            "original_shape": self.original_shape,
            "final_shape": self.final_shape,
            "rows_removed": self.rows_removed,
            "rows_removed_pct": f"{self.rows_removed_pct:.2f}%",
            "cols_removed": self.cols_removed,
            "duplicates_removed": self.duplicates_removed,
            "missing_filled": self.missing_filled,
            "outliers_handled": self.outliers_handled,
            "invalid_filtered": self.invalid_filtered,
            "schema_validations": self.schema_validations,
            "warnings": self.warnings,
        }


@dataclass
class CleaningRule:
    """清洗规则"""
    name: str
    func: Callable[[pd.DataFrame], tuple[pd.DataFrame, dict]]
    enabled: bool = True


class DataCleaner:
    """
    数据清洗器

    支持流水线式清洗，可配置各种清洗规则
    """

    # 默认清洗规则
    DEFAULT_RULES: dict[str, dict] = {
        "rec_inter": {
            "drop_duplicates": True,
            "drop_nulls": ["user_id", "video_id"],
            "filter_invalid": {
                "watch_ratio": {"min": 0, "max": 100},
                "timestamp": {"min": 0},
                "playing_time": {"min": 0},
                "duration_ms": {"min": 0},
            },
            "derive_features": {
                "watch_ratio": "playing_time / duration_ms",
            },
        },
        "user_features": {
            "drop_duplicates": True,
            "drop_nulls": ["user_id"],
            "fill_nulls": {
                "onehot_feat1": 0,
                "onehot_feat2": 0,
            },
            "clip_range": {
                "search_active_level": (0, 5),
                "reco_active_level": (0, 5),
            },
        },
        "item_features": {
            "drop_duplicates": True,
            "drop_nulls": ["video_id"],
            "fill_nulls": {
                "caption": "",
                "item_type": "UNKNOWN",
            },
            "deduplicate_ids": True,
        },
        "social_network": {
            "drop_duplicates": True,
            "drop_nulls": ["user_id", "user_follow_id"],
        },
        "src_inter": {
            "drop_duplicates": True,
            "drop_nulls": ["user_id", "item_id"],
            "filter_invalid": {
                "click_cnt": {"min": 0},
            },
        },
    }

    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None,
    ):
        self.config = config or get_config()
        self.logger = logger or get_logger()
        self._report: Optional[CleaningReport] = None

    def clean(
        self,
        df: pd.DataFrame,
        dataset_name: str = "default",
        rules: Optional[dict] = None,
        steps: Optional[list[CleaningStep]] = None,
        verbose: bool = True,
    ) -> tuple[pd.DataFrame, CleaningReport]:
        """
        执行数据清洗

        Args:
            df: 输入DataFrame
            dataset_name: 数据集名称，用于选择规则
            rules: 自定义清洗规则
            steps: 指定清洗步骤
            verbose: 是否打印进度

        Returns:
            (清洗后的DataFrame, 清洗报告)
        """
        self.logger.info(f"开始清洗数据集: {dataset_name}, 原始形状: {df.shape}")

        original_shape = df.shape
        self._report = CleaningReport(original_shape=original_shape, final_shape=original_shape)

        # 选择规则
        rules = rules or self.DEFAULT_RULES.get(dataset_name, {})
        df_cleaned = df.copy()

        # 确定清洗步骤
        if steps is None:
            steps = [
                CleaningStep.FIX_TYPES,
                CleaningStep.DROP_DUPLICATES,
                CleaningStep.HANDLE_MISSING,
                CleaningStep.FILTER_INVALID,
                CleaningStep.DROP_MISSING_COLS,
                CleaningStep.HANDLE_OUTLIERS,
            ]

        # 执行清洗
        if verbose:
            steps_iter = tqdm(steps, desc=f"清洗 {dataset_name}")
        else:
            steps_iter = steps

        for step in steps_iter:
            try:
                if step == CleaningStep.DROP_DUPLICATES:
                    df_cleaned = self._drop_duplicates(df_cleaned, rules)
                elif step == CleaningStep.HANDLE_MISSING:
                    df_cleaned = self._handle_missing(df_cleaned, rules)
                elif step == CleaningStep.FILTER_INVALID:
                    df_cleaned = self._filter_invalid(df_cleaned, rules)
                elif step == CleaningStep.HANDLE_OUTLIERS:
                    df_cleaned = self._handle_outliers(df_cleaned, rules)
                elif step == CleaningStep.DROP_MISSING_COLS:
                    df_cleaned = self._drop_missing_cols(df_cleaned, rules)
                elif step == CleaningStep.FIX_TYPES:
                    df_cleaned = self._fix_types(df_cleaned)
            except Exception as e:
                self._report.warnings.append(f"步骤 {step} 出错: {str(e)}")
                self.logger.warning(f"清洗步骤 {step} 出错: {e}")

        # 更新报告
        self._report.final_shape = df_cleaned.shape
        self._report.rows_removed = original_shape[0] - df_cleaned.shape[0]
        self._report.cols_removed = original_shape[1] - df_cleaned.shape[1]

        self.logger.info(
            f"清洗完成: {dataset_name}, "
            f"最终形状: {df_cleaned.shape}, "
            f"移除行数: {self._report.rows_removed} ({self._report.rows_removed_pct:.2f}%)"
        )

        return df_cleaned, self._report

    def _drop_duplicates(self, df: pd.DataFrame, rules: dict) -> pd.DataFrame:
        """删除重复行"""
        if not rules.get("drop_duplicates", True):
            return df

        original_len = len(df)
        df = df.drop_duplicates()
        removed = original_len - len(df)

        if removed > 0:
            self._report.duplicates_removed += removed
            self.logger.debug(f"删除重复行: {removed}")

        return df

    def _handle_missing(self, df: pd.DataFrame, rules: dict) -> pd.DataFrame:
        """处理缺失值"""
        fill_strategy = self.config.cleaner.fill_null_strategy

        # 指定的填充列
        fill_specified = rules.get("fill_nulls", {})
        for col, value in fill_specified.items():
            if col in df.columns:
                filled_count = df[col].isna().sum()
                df[col] = df[col].fillna(value)
                if filled_count > 0:
                    self._report.missing_filled[col] = filled_count

        # 删除指定必须非空的行
        drop_nulls = rules.get("drop_nulls", [])
        for col in drop_nulls:
            if col in df.columns:
                original_len = len(df)
                df = df.dropna(subset=[col])
                removed = original_len - len(df)
                if removed > 0:
                    self._report.missing_filled[f"{col}_dropped"] = removed

        # 对剩余数值列用策略填充
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in fill_specified and df[col].isna().any():
                filled_count = df[col].isna().sum()
                if fill_strategy == "mean":
                    df[col] = df[col].fillna(df[col].mean())
                elif fill_strategy == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif fill_strategy == "mode":
                    df[col] = df[col].fillna(df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 0)
                elif fill_strategy == "zero":
                    df[col] = df[col].fillna(0)
                
                if filled_count > 0:
                    self._report.missing_filled[col] = filled_count

        return df

    def _filter_invalid(self, df: pd.DataFrame, rules: dict) -> pd.DataFrame:
        """过滤无效数据"""
        filter_config = rules.get("filter_invalid", {})

        for col, range_spec in filter_config.items():
            if col not in df.columns:
                continue

            original_len = len(df)

            # 范围过滤
            if isinstance(range_spec, dict):
                if "min" in range_spec:
                    df = df[df[col] >= range_spec["min"]]
                if "max" in range_spec:
                    df = df[df[col] <= range_spec["max"]]

            removed = original_len - len(df)
            if removed > 0:
                self._report.invalid_filtered[col] = removed

        return df

    def _handle_outliers(self, df: pd.DataFrame, rules: dict) -> pd.DataFrame:
        """处理异常值"""
        threshold = self.config.cleaner.outlier_std
        clip_range = rules.get("clip_range", {})

        for col, (low, high) in clip_range.items():
            if col in df.columns and df[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
                df[col] = df[col].clip(lower=low, upper=high)
                self._report.outliers_handled[col] = f"clipped to [{low}, {high}]"

        # Z-score 异常值处理
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in clip_range:
                continue
            
            mean = df[col].mean()
            std = df[col].std()
            if std == 0:
                continue

            outliers = np.abs((df[col] - mean) / std) > threshold
            if outliers.any():
                self._report.outliers_handled[col] = outliers.sum()

        return df

    def _drop_missing_cols(self, df: pd.DataFrame, rules: dict) -> pd.DataFrame:
        """删除缺失率过高的列"""
        threshold = self.config.cleaner.drop_null_threshold

        cols_to_drop = []
        for col in df.columns:
            missing_ratio = df[col].isna().sum() / len(df)
            if missing_ratio > threshold:
                cols_to_drop.append(col)

        if cols_to_drop:
            self.logger.warning(f"删除高缺失率列: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)

        return df

    def _fix_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """修正数据类型"""
        # ID列应为整数
        id_cols = [c for c in df.columns if c.endswith("_id") or c == "user_id" or c == "video_id"]
        for col in id_cols:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
                except Exception:
                    pass

        return df

    def get_report(self) -> Optional[CleaningReport]:
        """获取清洗报告"""
        return self._report


class StreamingCleaner:
    """
    流式数据清洗器 (用于大数据集)

    分批处理数据，最后合并结果
    """

    def __init__(
        self,
        cleaner: Optional[DataCleaner] = None,
        chunk_size: int = 50000,
    ):
        self.cleaner = cleaner or DataCleaner()
        self.chunk_size = chunk_size
        self._chunk_reports: list[CleaningReport] = []

    def clean_stream(
        self,
        file_path: Union[str, Path],
        dataset_name: str = "stream",
        rules: Optional[dict] = None,
        **read_kwargs,
    ) -> tuple[pd.DataFrame, CleaningReport]:
        """
        流式清洗大文件

        Args:
            file_path: 文件路径
            dataset_name: 数据集名称
            rules: 清洗规则
            **read_kwargs: pd.read_csv 额外参数

        Returns:
            (清洗后的DataFrame, 汇总报告)
        """
        chunks = []
        self._chunk_reports = []

        for chunk in tqdm(
            pd.read_csv(file_path, chunksize=self.chunk_size, **read_kwargs),
            desc=f"流式清洗 {Path(file_path).name}",
        ):
            cleaned_chunk, report = self.cleaner.clean(chunk, dataset_name, rules, verbose=False)
            chunks.append(cleaned_chunk)
            self._chunk_reports.append(report)

        # 合并结果
        df = pd.concat(chunks, ignore_index=True)

        # 汇总报告
        summary_report = self._aggregate_reports()

        return df, summary_report

    def _aggregate_reports(self) -> CleaningReport:
        """汇总分块报告"""
        if not self._chunk_reports:
            return CleaningReport(original_shape=(0, 0), final_shape=(0, 0))

        first = self._chunk_reports[0]

        # 简单汇总
        total_removed = sum(r.rows_removed for r in self._chunk_reports)
        total_duplicates = sum(r.duplicates_removed for r in self._chunk_reports)
        final_shape = self._chunk_reports[-1].final_shape

        summary = CleaningReport(
            original_shape=(sum(r.original_shape[0] for r in self._chunk_reports), first.original_shape[1]),
            final_shape=final_shape,
            rows_removed=total_removed,
            duplicates_removed=total_duplicates,
            warnings=[f"流式处理 {len(self._chunk_reports)} 个分块"],
        )

        return summary


# 便捷函数
_default_cleaner: Optional[DataCleaner] = None


def get_cleaner() -> DataCleaner:
    """获取全局清洗器"""
    global _default_cleaner
    if _default_cleaner is None:
        _default_cleaner = DataCleaner()
    return _default_cleaner


def clean_data(
    df: pd.DataFrame,
    dataset_name: str = "default",
    **kwargs,
) -> tuple[pd.DataFrame, CleaningReport]:
    """便捷清洗函数"""
    return get_cleaner().clean(df, dataset_name, **kwargs)
