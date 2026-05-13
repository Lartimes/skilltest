"""
数据处理完整流程
加载 → 清洗 → 验证 → 保存

使用方法:
    python -m src.pre_pipeline.pipeline
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import EnvMode, DataSource, Config
from src.pre_pipeline.loader import DataLoader, load_cleaned_data
from src.pre_pipeline.cleaner import DataCleaner, CleaningReport
from src.pre_pipeline.validator import DataValidator, DataQualityReport, QualityLevel


class DataPipeline:
    """数据处理流水线"""
    
    def __init__(self, use_cleaned: bool = True):
        """
        Args:
            use_cleaned: 是否使用已清洗的数据(True)还是重新清洗(False)
        """
        self.config = Config()
        self.config.env_mode = EnvMode.PROD
        
        self.loader = DataLoader(config=self.config)
        self.cleaner = DataCleaner(config=self.config)
        self.validator = DataValidator(config=self.config)
        self.use_cleaned = use_cleaned
        
        # 输出目录
        self.output_dir = project_root / "output" / "cleaned"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self, source: DataSource) -> tuple:
        """加载数据"""
        name = source.value
        print(f"\n[1/4] 加载数据: {name}")
        
        if self.use_cleaned:
            try:
                df = load_cleaned_data(name)
                print(f"  -> 使用已清洗数据: {df.shape}")
                return df, None
            except FileNotFoundError:
                print(f"  -> 已清洗数据不存在，将重新清洗")
        
        df = self.loader.load(source, show_progress=False)
        print(f"  -> 原始数据: {df.shape}")
        return df, None
    
    def clean_data(self, df, name: str) -> tuple:
        """清洗数据"""
        print(f"\n[2/4] 清洗数据: {name}")
        
        df_clean, report = self.cleaner.clean(df, name, verbose=False)
        
        print(f"  -> 清洗后: {df_clean.shape}")
        print(f"  -> 删除行数: {report.rows_removed} ({report.rows_removed_pct:.2f}%)")
        print(f"  -> 删除重复: {report.duplicates_removed}")
        if report.missing_filled:
            print(f"  -> 缺失填充: {report.missing_filled}")
        if report.invalid_filtered:
            print(f"  -> 无效过滤: {report.invalid_filtered}")
        
        return df_clean, report
    
    def validate_data(self, df, name: str) -> DataQualityReport:
        """验证数据"""
        print(f"\n[3/4] 验证数据: {name}")
        
        report = self.validator.validate(df, name)
        
        print(f"  -> 质量评分: {report.quality_score:.2f}")
        print(f"  -> 质量等级: {report.quality_level.value}")
        print(f"  -> 完整度: {report.completeness:.2f}%")
        print(f"  -> 重复行: {report.duplicate_rows}")
        
        if report.warnings:
            print(f"  -> 警告:")
            for w in report.warnings[:3]:
                print(f"      - {w}")
        
        return report
    
    def save_data(self, df, name: str) -> Path:
        """保存数据"""
        print(f"\n[4/4] 保存数据: {name}")
        
        output_file = self.output_dir / f"{name}_clean.parquet"
        df.to_parquet(output_file, compression="snappy", index=False)
        
        size_mb = output_file.stat().st_size / 1024 / 1024
        print(f"  -> 文件: {output_file.name}")
        print(f"  -> 大小: {size_mb:.2f} MB")
        
        return output_file
    
    def process(self, source: DataSource, save: bool = True) -> dict:
        """
        执行完整流程
        
        Args:
            source: 数据源
            save: 是否保存
            
        Returns:
            处理结果字典
        """
        name = source.value
        
        print("=" * 60)
        print(f"数据处理流水线: {name}")
        print("=" * 60)
        
        # 1. 加载
        df, _ = self.load_data(source)
        
        # 2. 清洗
        df_clean, clean_report = self.clean_data(df, name)
        
        # 3. 验证
        quality_report = self.validate_data(df_clean, name)
        
        # 4. 保存
        output_file = None
        if save:
            output_file = self.save_data(df_clean, name)
        
        print("\n" + "=" * 60)
        print("处理完成!")
        print("=" * 60)
        
        return {
            "name": name,
            "source": source,
            "original_shape": df.shape,
            "clean_shape": df_clean.shape,
            "clean_report": clean_report,
            "quality_report": quality_report,
            "output_file": output_file,
        }
    
    def process_all(self, save: bool = True) -> list[dict]:
        """处理所有数据集"""
        sources = [
            DataSource.USER_FEATURES,
            DataSource.ITEM_FEATURES,
            DataSource.REC_INTERACTIONS,
            DataSource.SOCIAL_NETWORK,
            DataSource.SRC_INTERACTIONS,
        ]
        
        results = []
        for source in sources:
            result = self.process(source, save=save)
            results.append(result)
        
        # 汇总
        print("\n" + "=" * 60)
        print("所有数据处理完成!")
        print("=" * 60)
        print("\n汇总:")
        print("-" * 60)
        print(f"{'数据集':<20} {'原始':<15} {'清洗后':<15} {'评分':<10}")
        print("-" * 60)
        for r in results:
            print(f"{r['name']:<20} {str(r['original_shape']):<15} "
                  f"{str(r['clean_shape']):<15} {r['quality_report'].quality_score:.1f}")
        
        return results


def main():
    """主函数"""
    print("=" * 60)
    print("数据处理流水线")
    print("=" * 60)
    
    # 创建流水线
    pipeline = DataPipeline(use_cleaned=False)
    
    # 处理所有数据
    results = pipeline.process_all(save=True)
    
    # 显示生成的文件
    print("\n生成的文件:")
    print("-" * 40)
    for r in results:
        if r["output_file"]:
            size = r["output_file"].stat().st_size / 1024 / 1024
            print(f"  {r['output_file'].name:<35} {size:>8.2f} MB")


if __name__ == "__main__":
    main()
