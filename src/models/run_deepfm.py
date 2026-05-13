# -*- coding: utf-8 -*-
"""
DeepFM 算法测试
使用方法: python -m src.models.run_deepfm
"""

from src.models import (
    load_data,
    FeatureProcessor,
    create_recommender,
    RecommenderEvaluator,
)
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)


# 指标中文名称映射
METRIC_NAMES = {
    'auc': 'AUC (曲线下面积)',
    'hit_rate@5': 'Hit Rate@5 (命中率)',
    'hit_rate@10': 'Hit Rate@10 (命中率)',
    'hit_rate@20': 'Hit Rate@20 (命中率)',
    'mrr@5': 'MRR@5 (平均倒数排名)',
    'mrr@10': 'MRR@10 (平均倒数排名)',
    'mrr@20': 'MRR@20 (平均倒数排名)',
    'ndcg@5': 'NDCG@5 (归一化折损累计增益)',
    'ndcg@10': 'NDCG@10 (归一化折损累计增益)',
    'ndcg@20': 'NDCG@20 (归一化折损累计增益)',
}

def run_deepfm(
    sample_size=100000,     # 采样数量
    test_ratio=0.2,         # 测试集比例
    epochs=5,              # 训练轮数
    embedding_dim=64,       # 嵌入维度
    hidden_dims=[128, 64], # DNN隐藏层
    batch_size=512,         # 批次大小
    lr=0.001,             # 学习率
    k_values=[5, 10, 20],  # 评估K值
    sample_users=500,       # 评估采样用户数
):
    """运行 DeepFM 算法"""
    
    print("\n" + "=" * 60)
    print("DeepFM 推荐算法")
    print("=" * 60)
    
    # 1. 加载数据
    print("\n[1/5] 加载数据...")
    data = load_data('output/cleaned', sample_size=sample_size)
    print(f"    用户: {data.n_users:,}, 物品: {data.n_items:,}, 交互: {len(data.interactions):,}")
    
    # 2. 特征工程
    print("\n[2/5] 特征工程...")
    processor = FeatureProcessor(data)
    train_data, test_data = processor.process(test_ratio=test_ratio)
    print(f"    训练: {len(train_data.user_ids):,}, 测试: {len(test_data.user_ids):,}")
    
    # 3. 构建模型
    print("\n[3/5] 构建 DeepFM 模型...")
    model = create_recommender(
        'deepfm',
        embedding_dim=embedding_dim,
        hidden_dims=hidden_dims,
        lr=lr,
        epochs=epochs,
        batch_size=batch_size,
    )
    
    # 4. 训练
    print("\n[4/5] 训练...")
    start = datetime.now()
    model.fit(train_data, verbose=True)
    train_time = (datetime.now() - start).total_seconds()
    print(f"    完成! 耗时: {train_time:.1f}s")
    
    # 5. 评估
    print("\n[5/5] 评估...")
    evaluator = RecommenderEvaluator(k_values=k_values, sample_users=sample_users)
    metrics = evaluator.evaluate(model, train_data, test_data)
    
    print("\n" + "=" * 60)
    print("DeepFM 评估结果")
    print("=" * 60)
    for k, v in sorted(metrics.items()):
        chinese_name = METRIC_NAMES.get(k, k)
        print(f"  {chinese_name:30s}: {v:.4f}")
    
    return model, metrics


if __name__ == '__main__':
    # ====== 修改参数 ======
    SAMPLE_SIZE = 100000    # 数据量
    EPOCHS = 5            # 训练轮数
    EMBEDDING_DIM = 64     # 嵌入维度
    HIDDEN_DIMS = [128, 64] # DNN隐藏层
    LEARNING_RATE = 0.001  # 学习率
    # =====================
    
    run_deepfm(
        sample_size=SAMPLE_SIZE,
        epochs=EPOCHS,
        embedding_dim=EMBEDDING_DIM,
        hidden_dims=HIDDEN_DIMS,
        lr=LEARNING_RATE,
    )
