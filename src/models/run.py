# -*- coding: utf-8 -*-
"""
推荐算法运行脚本
支持单个算法运行，可配置参数

使用方法:
    # 在 backend 目录下运行
    python -m src.models.run --algorithm mf --sample 50000

    # 指定数据目录和算法
    python -m src.models.run --algorithm neumf --data output/cleaned --sample 100000

    # 自定义参数
    python -m src.models.run --algorithm deepfm --epochs 50 --batch_size 512
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import argparse
import logging
from datetime import datetime

from src.models import (
    create_recommender,
    load_data,
    FeatureProcessor,
    RecommenderEvaluator,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class ModelRunner:
    """推荐算法运行器"""
    
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    
    # 算法默认配置 (使用算法类实际接受的参数名)
    ALGORITHM_CONFIGS = {
        'mf': {
            'embedding_dim': 64,
            'lr': 0.01,
            'reg': 0.01,
            'epochs': 20,
            'batch_size': 256,
        },
        'neumf': {
            'embedding_dim': 64,
            'layers': [128, 64, 32],
            'lr': 0.001,
            'reg': 0.0001,
            'epochs': 30,
            'batch_size': 256,
        },
        'deepfm': {
            'embedding_dim': 64,
            'hidden_layers': [256, 128, 64],
            'lr': 0.001,
            'reg': 0.0001,
            'epochs': 30,
            'batch_size': 512,
        },
    }
    
    def __init__(self,
                 data_dir: str = None,
                 algorithm: str = 'mf',
                 sample_size: int = 100000,
                 test_ratio: float = 0.2,
                 k_values: list = None,
                 output_dir: str = None,
                 **model_kwargs):
        """
        Args:
            data_dir: 数据目录 (默认: 项目根目录/output/cleaned)
            algorithm: 算法名称 (mf, neumf, deepfm)
            sample_size: 采样数量
            test_ratio: 测试集比例
            k_values: 评估指标K值列表
            output_dir: 模型输出目录 (默认: 项目根目录/output/models)
            **model_kwargs: 算法额外参数
        """
        # 默认使用项目根目录下的路径
        if data_dir is None:
            data_dir = self.PROJECT_ROOT / 'output' / 'cleaned'
        self.data_dir = Path(data_dir)
        self.algorithm = algorithm
        self.sample_size = sample_size
        self.test_ratio = test_ratio
        self.k_values = k_values or [5, 10, 20]
        
        # 默认使用项目根目录下的路径
        if output_dir is None:
            output_dir = self.PROJECT_ROOT / 'output' / 'models'
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取算法默认配置并合并用户参数
        default_config = self.ALGORITHM_CONFIGS.get(algorithm, {})
        self.model_params = {**default_config, **model_kwargs}
        
        # 数据和模型
        self.raw_data = None
        self.train_data = None
        self.test_data = None
        self.model = None
        self.evaluator = RecommenderEvaluator(k_values=self.k_values)
    
    def load_data(self):
        """加载并处理数据"""
        logger.info("=" * 60)
        logger.info("步骤1: 加载数据")
        logger.info("=" * 60)
        logger.info(f"  数据目录: {self.data_dir}")
        logger.info(f"  采样数量: {self.sample_size:,}")
        
        self.raw_data = load_data(str(self.data_dir), sample_size=self.sample_size)
        
        logger.info("\n" + "=" * 60)
        logger.info("步骤2: 特征工程")
        logger.info("=" * 60)
        
        processor = FeatureProcessor(self.raw_data)
        self.train_data, self.test_data = processor.process(
            test_ratio=self.test_ratio
        )
        
        logger.info(f"\n  训练集: {len(self.train_data.user_ids):,} 条")
        logger.info(f"  测试集: {len(self.test_data.user_ids):,} 条")
    
    def build_model(self):
        """构建模型"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤3: 构建模型")
        logger.info("=" * 60)
        logger.info(f"  算法: {self.algorithm.upper()}")
        logger.info(f"  参数:")
        for k, v in self.model_params.items():
            logger.info(f"    - {k}: {v}")
        
        self.model = create_recommender(self.algorithm, **self.model_params)
        logger.info(f"  模型名称: {self.model.name}")
    
    def train(self):
        """训练模型"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤4: 训练模型")
        logger.info("=" * 60)
        
        self.model.fit(self.train_data, verbose=True)
        logger.info("  训练完成!")
    
    def evaluate(self):
        """评估模型"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤5: 评估模型")
        logger.info("=" * 60)
        
        metrics = self.evaluator.evaluate(self.model, self.train_data, self.test_data)
        
        if metrics:
            logger.info("\n  评估结果:")
            for metric, value in sorted(metrics.items()):
                logger.info(f"    {metric}: {value:.6f}")
        
        return metrics
    
    def save(self):
        """保存模型"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_name = f"{self.algorithm}_{timestamp}"
        
        # 保存模型
        model_path = self.output_dir / f"{model_name}.pkl"
        self.model.save(str(model_path))
        logger.info(f"\n  模型已保存: {model_path}")
        
        # 保存评估结果
        metrics = self.evaluator.evaluate(self.model, self.train_data, self.test_data)
        results_path = self.output_dir / f"{model_name}_metrics.txt"
        with open(results_path, 'w') as f:
            f.write(f"Algorithm: {self.algorithm}\n")
            f.write(f"Parameters: {self.model_params}\n\n")
            f.write("Metrics:\n")
            for metric, value in sorted(metrics.items()):
                f.write(f"  {metric}: {value:.6f}\n")
        logger.info(f"  结果已保存: {results_path}")
        
        return model_path, results_path
    
    def recommend(self, user_ids: list = None, n: int = 10):
        """为用户推荐物品"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤6: 生成推荐")
        logger.info("=" * 60)
        
        if user_ids is None:
            # 使用测试集中的用户
            user_ids = list(self.test_data.user_ids[:5])
        
        recommendations = {}
        for uid in user_ids:
            items = self.model.recommend(uid, n=n)
            recommendations[uid] = items
            logger.info(f"  用户 {uid}: 推荐 {n} 个物品")
        
        return recommendations
    
    def run(self, save: bool = True, recommend: bool = True) -> dict:
        """运行完整流程"""
        start_time = datetime.now()
        
        logger.info("\n" + "=" * 60)
        logger.info(f"推荐算法运行器 - {self.algorithm.upper()}")
        logger.info("=" * 60)
        
        self.load_data()
        self.build_model()
        self.train()
        metrics = self.evaluate()
        
        model_path, results_path = None, None
        recommendations = None
        if save:
            model_path, results_path = self.save()
        if recommend:
            recommendations = self.recommend()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "=" * 60)
        logger.info(f"运行完成! 耗时: {elapsed:.2f} 秒")
        logger.info("=" * 60)
        
        return {
            'algorithm': self.algorithm,
            'metrics': metrics,
            'model_path': model_path,
            'results_path': results_path,
            'recommendations': recommendations,
            'elapsed_seconds': elapsed,
        }


def main():
    parser = argparse.ArgumentParser(
        description='推荐算法运行器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行矩阵分解
  python -m src.models.run --algorithm mf --sample 50000

  # 运行神经矩阵分解
  python -m src.models.run --algorithm neumf --sample 100000 --epochs 50

  # 运行 DeepFM
  python -m src.models.run --algorithm deepfm --sample 200000 --epochs 30 --batch_size 512

可用算法: mf, neumf, deepfm
        """
    )
    
    # 数据配置
    parser.add_argument('--data', type=str, default='output/cleaned',
                       help='数据目录 (默认: output/cleaned)')
    parser.add_argument('--sample', type=int, default=100000,
                       help='采样数量 (默认: 100000)')
    parser.add_argument('--test_ratio', type=float, default=0.2,
                       help='测试集比例 (默认: 0.2)')
    
    # 算法配置
    parser.add_argument('--algorithm', '-a', type=str, default='mf',
                       choices=['mf', 'neumf', 'deepfm'],
                       help='算法名称 (默认: mf)')
    parser.add_argument('--epochs', type=int, default=None,
                       help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=None,
                       help='批次大小')
    parser.add_argument('--learning_rate', type=float, default=None,
                       help='学习率')
    parser.add_argument('--n_factors', type=int, default=None,
                       help='隐向量维度')
    
    # 输出配置
    parser.add_argument('--output', type=str, default='output/models',
                       help='输出目录 (默认: output/models)')
    parser.add_argument('--no_save', action='store_true',
                       help='不保存模型')
    parser.add_argument('--no_recommend', action='store_true',
                       help='不生成推荐')
    
    args = parser.parse_args()
    
    # 收集模型参数 (映射命令行参数到算法实际参数名)
    model_kwargs = {}
    if args.epochs is not None:
        model_kwargs['epochs'] = args.epochs
    if args.batch_size is not None:
        model_kwargs['batch_size'] = args.batch_size
    if args.learning_rate is not None:
        model_kwargs['lr'] = args.learning_rate  # learning_rate -> lr
    if args.n_factors is not None:
        model_kwargs['embedding_dim'] = args.n_factors  # n_factors -> embedding_dim
    
    # 创建运行器
    runner = ModelRunner(
        data_dir=args.data,
        algorithm=args.algorithm,
        sample_size=args.sample,
        test_ratio=args.test_ratio,
        output_dir=args.output,
        **model_kwargs
    )
    
    # 运行
    result = runner.run(save=not args.no_save, recommend=not args.no_recommend)
    
    return result


if __name__ == '__main__':
    main()
