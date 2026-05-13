"""
保存清洗后的数据到 parquet 文件
一次处理，多次复用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import EnvMode, DataSource
from src.pre_pipeline.loader import DataLoader
from src.pre_pipeline.cleaner import DataCleaner


def save_cleaned_data():
    """清洗并保存所有数据到 parquet"""
    
    # 创建输出目录
    output_dir = project_root / "output" / "cleaned"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置
    from src.config.settings import Config
    config = Config()
    config.env_mode = EnvMode.PROD  # 使用全量数据
    
    loader = DataLoader(config=config)
    cleaner = DataCleaner(config=config)
    
    # 要处理的数据集
    datasets = [
        (DataSource.USER_FEATURES, "user_features"),
        (DataSource.ITEM_FEATURES, "item_features"),
        (DataSource.REC_INTERACTIONS, "rec_inter"),
    ]
    
    print("=" * 60)
    print("清洗并保存数据")
    print("=" * 60)
    
    for source, name in datasets:
        output_file = output_dir / f"{name}_clean.parquet"
        
        print(f"\n处理: {name}")
        print(f"  输出: {output_file}")
        
        # 加载
        df = loader.load(source, show_progress=False)
        print(f"  原始: {df.shape}")
        
        # 清洗
        df_clean, report = cleaner.clean(df, name, verbose=False)
        print(f"  清洗后: {df_clean.shape}")
        print(f"  删除行数: {report.rows_removed}")
        
        # 保存为 parquet（压缩格式，省空间）
        df_clean.to_parquet(
            output_file,
            compression="snappy",  # 快速压缩
            index=False
        )
        
        # 计算文件大小
        file_size = output_file.stat().st_size / 1024 / 1024
        print(f"  文件大小: {file_size:.2f} MB")
    
    print("\n" + "=" * 60)
    print("全部完成!")
    print("=" * 60)
    
    # 列出所有生成的文件
    print("\n生成的文件:")
    for f in sorted(output_dir.glob("*.parquet")):
        size = f.stat().st_size / 1024 / 1024
        print(f"  {f.name} ({size:.2f} MB)")


if __name__ == "__main__":
    save_cleaned_data()
