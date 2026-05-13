"""
src2 数据模块 - validator

数据质量验证，支持:
- Schema验证
- 完整性检查
- 一致性检查
- 质量报告生成
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any, Union
from enum import Enum

import numpy as np
import pandas as pd

from ..config.settings import Config, DataQualityConfig, get_config
from ..utils.logging import get_logger, Logger


class QualityLevel(str, Enum):
    """数据质量等级"""
    EXCELLENT = "excellent"      # >= 95分
    GOOD = "good"               # >= 85分
    ACCEPTABLE = "acceptable"   # >= 70分
    POOR = "poor"               # >= 50分
    BAD = "bad"                 # < 50分


@dataclass
class ColumnQuality:
    """单列质量信息"""
    name: str
    dtype: str
    total_count: int
    missing_count: int
    missing_pct: float
    unique_count: int
    unique_pct: float
    null_or_empty_count: int = 0

    @property
    def completeness(self) -> float:
        """完整度"""
        return (1 - self.missing_pct) * 100

    def is_valid(self, missing_threshold: float = 0.5) -> bool:
        return self.missing_pct <= missing_threshold


@dataclass
class DataQualityReport:
    """数据质量报告"""
    dataset_name: str
    shape: tuple[int, int]
    total_rows: int
    total_cols: int
    
    # 整体统计
    completeness: float = 0.0        # 整体完整度
    duplicate_rows: int = 0
    duplicate_pct: float = 0.0
    
    # 列级质量
    column_quality: dict[str, ColumnQuality] = field(default_factory=dict)
    
    # 问题列
    low_quality_cols: list[str] = field(default_factory=list)
    high_null_cols: list[str] = field(default_factory=list)
    
    # ID相关
    id_cols_valid: bool = True
    id_coverage: dict = field(default_factory=dict)
    
    # 业务规则验证
    business_rules_passed: dict = field(default_factory=dict)
    business_rules_failed: dict = field(default_factory=dict)
    
    # 警告和建议
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    
    # 综合评分
    quality_score: float = 100.0
    quality_level: QualityLevel = QualityLevel.EXCELLENT

    def __post_init__(self):
        self._calculate_score()

    def _calculate_score(self):
        """计算综合质量分数"""
        # 基础分
        score = 100.0
        
        # 缺失率扣分
        if self.total_rows > 0 and self.column_quality:
            avg_missing = sum(c.missing_pct for c in self.column_quality.values()) / len(self.column_quality)
            score -= avg_missing * 30
        
        # 重复行扣分
        score -= self.duplicate_pct * 20
        
        # 低质量列扣分
        score -= len(self.low_quality_cols) * 5
        
        # ID无效扣分
        if not self.id_cols_valid:
            score -= 10
        
        # 业务规则失败扣分
        score -= len(self.business_rules_failed) * 5
        
        self.quality_score = max(0, min(100, score))
        
        # 评定等级
        if self.quality_score >= 95:
            self.quality_level = QualityLevel.EXCELLENT
        elif self.quality_score >= 85:
            self.quality_level = QualityLevel.GOOD
        elif self.quality_score >= 70:
            self.quality_level = QualityLevel.ACCEPTABLE
        elif self.quality_score >= 50:
            self.quality_level = QualityLevel.POOR
        else:
            self.quality_level = QualityLevel.BAD

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "dataset_name": self.dataset_name,
            "shape": self.shape,
            "quality_score": f"{self.quality_score:.2f}",
            "quality_level": self.quality_level.value,
            "completeness": f"{self.completeness:.2f}%",
            "duplicate_rows": self.duplicate_rows,
            "duplicate_pct": f"{self.duplicate_pct:.2f}%",
            "column_quality": {
                col: {
                    "dtype": q.dtype,
                    "missing_pct": f"{q.missing_pct:.2f}%",
                    "unique_pct": f"{q.unique_pct:.2f}%",
                }
                for col, q in self.column_quality.items()
            },
            "low_quality_cols": self.low_quality_cols,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
        }

    def print_summary(self):
        """打印摘要"""
        print("=" * 60)
        print(f"数据质量报告: {self.dataset_name}")
        print("=" * 60)
        print(f"形状: {self.shape}")
        print(f"质量评分: {self.quality_score:.2f} ({self.quality_level.value})")
        print(f"完整度: {self.completeness:.2f}%")
        print(f"重复行: {self.duplicate_rows} ({self.duplicate_pct:.2f}%)")
        
        if self.warnings:
            print("\n⚠️ 警告:")
            for w in self.warnings:
                print(f"  - {w}")
        
        if self.suggestions:
            print("\n💡 建议:")
            for s in self.suggestions:
                print(f"  - {s}")
        
        print("=" * 60)


class DataValidator:
    """
    数据质量验证器

    功能:
    - Schema验证
    - 完整性检查
    - 重复检查
    - ID覆盖度检查
    - 业务规则验证
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None,
    ):
        self.config = config or get_config()
        self.logger = logger or get_logger()

    def validate(
        self,
        df: pd.DataFrame,
        dataset_name: str = "unknown",
        check_missing: bool = True,
        check_duplicates: bool = True,
        check_id_coverage: Optional[dict] = None,
        business_rules: Optional[dict] = None,
        missing_threshold: float = 0.5,
    ) -> DataQualityReport:
        """
        执行数据质量验证

        Args:
            df: 待验证的DataFrame
            dataset_name: 数据集名称
            check_missing: 是否检查缺失值
            check_duplicates: 是否检查重复
            check_id_coverage: ID列覆盖度检查 {列名: expected_ratio}
            business_rules: 业务规则 {"规则名": lambda df: bool}
            missing_threshold: 缺失率阈值

        Returns:
            DataQualityReport
        """
        self.logger.info(f"开始数据质量验证: {dataset_name}")

        report = DataQualityReport(
            dataset_name=dataset_name,
            shape=df.shape,
            total_rows=len(df),
            total_cols=len(df.columns),
        )

        # 1. 列级质量分析
        if check_missing:
            report = self._check_missing(df, report)

        # 2. 重复检查
        if check_duplicates:
            report = self._check_duplicates(df, report)

        # 3. ID覆盖度检查
        if check_id_coverage:
            report = self._check_id_coverage(df, report, check_id_coverage)

        # 4. 业务规则验证
        if business_rules:
            report = self._validate_business_rules(df, report, business_rules)

        # 5. 生成警告和建议
        report = self._generate_warnings(df, report, missing_threshold)

        # 计算完整度
        if report.column_quality:
            total_cells = report.total_rows * report.total_cols
            missing_cells = sum(c.missing_count for c in report.column_quality.values())
            report.completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 0

        self.logger.info(
            f"验证完成: {dataset_name}, "
            f"质量评分: {report.quality_score:.2f}, "
            f"等级: {report.quality_level.value}"
        )

        return report

    def _check_missing(self, df: pd.DataFrame, report: DataQualityReport) -> DataQualityReport:
        """检查缺失值"""
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = missing_count / len(df) if len(df) > 0 else 0

            # 空字符串也算缺失
            if df[col].dtype == object:
                null_or_empty = (df[col] == "").sum()
            else:
                null_or_empty = 0

            unique_count = df[col].nunique()
            unique_pct = unique_count / len(df) * 100 if len(df) > 0 else 0

            col_quality = ColumnQuality(
                name=col,
                dtype=str(df[col].dtype),
                total_count=len(df),
                missing_count=missing_count,
                missing_pct=missing_pct,
                unique_count=unique_count,
                unique_pct=unique_pct,
                null_or_empty_count=null_or_empty,
            )

            report.column_quality[col] = col_quality

        return report

    def _check_duplicates(self, df: pd.DataFrame, report: DataQualityReport) -> DataQualityReport:
        """检查重复行"""
        report.duplicate_rows = df.duplicated().sum()
        report.duplicate_pct = report.duplicate_rows / len(df) * 100 if len(df) > 0 else 0
        return report

    def _check_id_coverage(
        self,
        df: pd.DataFrame,
        report: DataQualityReport,
        id_specs: dict[str, float],
    ) -> DataQualityReport:
        """检查ID列覆盖度"""
        id_cols = [c for c in df.columns if c.endswith("_id") or c in ("user_id", "video_id")]

        for col in id_cols:
            if col in df.columns:
                non_null_ratio = df[col].notna().sum() / len(df)
                report.id_coverage[col] = f"{non_null_ratio:.2%}"

                if col in id_specs:
                    expected = id_specs[col]
                    if non_null_ratio < expected:
                        report.id_cols_valid = False
                        report.warnings.append(
                            f"{col} 覆盖度 {non_null_ratio:.2%} 低于预期 {expected:.2%}"
                        )

        return report

    def _validate_business_rules(
        self,
        df: pd.DataFrame,
        report: DataQualityReport,
        rules: dict[str, callable],
    ) -> DataQualityReport:
        """验证业务规则"""
        for rule_name, rule_func in rules.items():
            try:
                passed = rule_func(df)
                report.business_rules_passed[rule_name] = True
            except Exception as e:
                report.business_rules_passed[rule_name] = False
                report.business_rules_failed[rule_name] = str(e)

        return report

    def _generate_warnings(
        self,
        df: pd.DataFrame,
        report: DataQualityReport,
        missing_threshold: float,
    ) -> DataQualityReport:
        """生成警告和建议"""
        # 高缺失率列
        for col, quality in report.column_quality.items():
            if quality.missing_pct > missing_threshold:
                report.high_null_cols.append(col)
                report.warnings.append(
                    f"{col} 缺失率 {quality.missing_pct:.2%} 超过阈值 {missing_threshold:.0%}"
                )

        # 低质量列(高缺失或低唯一性)
        for col, quality in report.column_quality.items():
            if quality.missing_pct > missing_threshold or quality.unique_pct < 1:
                report.low_quality_cols.append(col)

        # 生成建议
        if report.duplicate_rows > 0:
            report.suggestions.append(
                f"存在 {report.duplicate_rows} 行重复数据，建议去重"
            )

        if report.high_null_cols:
            cols_str = ", ".join(report.high_null_cols[:5])
            if len(report.high_null_cols) > 5:
                cols_str += f"... (共{len(report.high_null_cols)}列)"
            report.suggestions.append(
                f"高缺失率列 [{cols_str}] 需要处理"
            )

        # 检查数据类型
        for col in df.columns:
            if "id" in col.lower() and df[col].dtype != "int64":
                report.suggestions.append(
                    f"{col} 应为整数类型，建议转换"
                )

        return report


class SchemaValidator:
    """Schema验证器"""

    def __init__(
        self,
        expected_schema: dict[str, str],
        required_cols: Optional[list[str]] = None,
    ):
        """
        Args:
            expected_schema: {列名: 期望类型} 字典
            required_cols: 必须存在的列列表
        """
        self.expected_schema = expected_schema
        self.required_cols = required_cols or []

    def validate(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """
        验证DataFrame是否符合Schema

        Returns:
            (是否通过, 错误信息列表)
        """
        errors = []

        # 检查必需列
        missing_cols = set(self.required_cols) - set(df.columns)
        if missing_cols:
            errors.append(f"缺少必需列: {missing_cols}")

        # 检查类型
        for col, expected_type in self.expected_schema.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if not self._type_matches(actual_type, expected_type):
                    errors.append(
                        f"{col} 类型不匹配: 期望 {expected_type}, 实际 {actual_type}"
                    )

        return len(errors) == 0, errors

    def _type_matches(self, actual: str, expected: str) -> bool:
        """检查类型是否匹配"""
        type_aliases = {
            "int": ["int64", "int32", "int16", "int8", "uint8", "uint16", "uint32", "uint64"],
            "float": ["float64", "float32", "float16"],
            "str": ["object", "string"],
            "datetime": ["datetime64", "datetime64[ns]"],
        }

        if expected in type_aliases:
            return actual in type_aliases[expected]
        return actual == expected


# 便捷函数
def validate_data_quality(
    df: pd.DataFrame,
    dataset_name: str = "pre_pipeline",
    **kwargs,
) -> DataQualityReport:
    """便捷验证函数"""
    validator = DataValidator()
    return validator.validate(df, dataset_name, **kwargs)
