# -*- coding: utf-8 -*-
"""
ItemCF (基于物品的协同过滤) 算法测试
使用方法: python -m src.models.run_itemcf

ItemCF 原理:
- 利用物品之间的相似度进行推荐
- 如果用户喜欢物品A，且物品B与A相似，则推荐B
- 使用余弦相似度计算物品相似度
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


def run_itemcf(
    sample_size=100000,           # 采样数量
    test_ratio=0.2,              # 测试集比例
    n_similar_items=20,           # 每个物品保留的相似物品数量
    normalize=True,              # 是否对热门物品降权
    k_values=[5, 10, 20],         # 评估K值
    sample_users=500,             # 评估采样用户数
):
    """运行 ItemCF 算法"""
    
    print("\n" + "=" * 60)
    print("ItemCF (基于物品的协同过滤) 推荐算法")
    print("=" * 60)
    print("算法原理: 利用物品之间的相似度进行推荐")
    
    # 1. 加载数据
    print("\n[1/4] 加载数据...")
    data = load_data('output/cleaned', sample_size=sample_size)
    print(f"    用户: {data.n_users:,}, 物品: {data.n_items:,}, 交互: {len(data.interactions):,}")
    
    # 2. 特征工程
    print("\n[2/4] 特征工程...")
    processor = FeatureProcessor(data)
    train_data, test_data = processor.process(test_ratio=test_ratio)
    print(f"    训练: {len(train_data.user_ids):,}, 测试: {len(test_data.user_ids):,}")
    
    # 3. 构建模型
    print("\n[3/4] 构建 ItemCF 模型...")
    model = create_recommender(
        'itemcf',
        n_similar_items=n_similar_items,
        normalize=normalize,
    )
    print(f"    相似物品数: {n_similar_items}")
    print(f"    热门降权: {normalize}")
    
    # 4. 训练 (ItemCF不需要训练迭代，计算相似度即可)
    print("\n[4/4] 计算相似度...")
    start = datetime.now()
    model.fit(train_data, verbose=True)
    train_time = (datetime.now() - start).total_seconds()
    print(f"    完成! 耗时: {train_time:.1f}s")
    
    # 评估
    print("\n评估中...")
    evaluator = RecommenderEvaluator(k_values=k_values, sample_users=sample_users)
    metrics = evaluator.evaluate(model, train_data, test_data)
    
    print("\n" + "=" * 60)
    print("ItemCF 评估结果")
    print("=" * 60)
    for k, v in sorted(metrics.items()):
        chinese_name = METRIC_NAMES.get(k, k)
        print(f"  {chinese_name:30s}: {v:.4f}")
    
    # 打印热门物品
    popular = model.most_popular(10)
    print("\n热门物品 Top 10:")
    for item, count in popular:
        print(f"    物品 {item}: {count} 次交互")
    
    return model, metrics


if __name__ == '__main__':
    # ====== 修改参数 ======
    SAMPLE_SIZE = 30000     # 数据量
    N_SIMILAR = 10           # 相似物品数量
    NORMALIZE = True         # 对热门物品降权
    # =====================
    
    run_itemcf(
        sample_size=SAMPLE_SIZE,
        n_similar_items=N_SIMILAR,
        normalize=NORMALIZE,
    )
