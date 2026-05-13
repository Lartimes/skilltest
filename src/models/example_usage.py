# -*- coding: utf-8 -*-
"""
推荐系统使用示例

场景: 用户打开APP -> 获取推荐列表 -> 展示给用户

使用方法:
    python -m src.models.example_usage
"""

from src.models import load_data, FeatureProcessor, create_recommender
import os

def example_single_user():
    """
    示例1: 单用户推荐
    场景: 用户ID=12345打开APP，获取10条推荐
    """
    print("\n" + "=" * 50)
    print("示例1: 单用户推荐")
    print("=" * 50)
    
    # ===== Step 1: 加载数据 =====
    print("\n[Step 1] 加载数据...")
    data = load_data('output/cleaned', sample_size=50000)
    
    # ===== Step 2: 特征工程 =====
    print("\n[Step 2] 特征工程...")
    processor = FeatureProcessor(data)
    train_data, test_data = processor.process(test_ratio=0.2)
    
    # 训练后获取ID映射
    user2idx = train_data.user2idx
    item2idx = train_data.item2idx
    idx2item = train_data.idx2item
    n_items = train_data.n_items
    
    print(f"用户数: {train_data.n_users}, 物品数: {train_data.n_items}")
    
    # ===== Step 3: 训练模型 =====
    print("\n[Step 3] 训练模型...")
    model = create_recommender('deepfm', embedding_dim=64, epochs=3)
    model.fit(train_data, verbose=False)
    
    # 设置ID映射到模型
    model.set_feature_dims(train_data)
    
    # ===== Step 4: 保存模型 =====
    print("\n[Step 4] 模型训练完成")
    save_path = 'output/models/deepfm_production.pkl'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    
    # ===== Step 5: 推理给用户推荐 =====
    print("\n[Step 5] 为用户生成推荐...")
    
    # 获取一个用户ID
    user_id = list(user2idx.keys())[0]
    print(f"用户ID: {user_id}")
    
    # 获取用户已交互的物品 (用于过滤)
    known_items = set()
    user_interactions = data.interactions[data.interactions['user_id'] == user_id]
    if len(user_interactions) > 0:
        known_items = set(user_interactions['item_id'].values)
        print(f"该用户历史交互物品数: {len(known_items)}")
    
    # 为用户推荐Top 10
    recommendations = model.recommend(
        user_id=user_id,
        n=10,
        exclude_known=True,  # 排除已看过的
        known_items=known_items
    )
    
    # ===== Step 5: 返回推荐结果 =====
    print("\n[Step 5] 推荐结果:")
    print("-" * 40)
    print(f"{'排名':<6} {'物品ID':<20} {'预测得分':<10}")
    print("-" * 40)
    for rank, (item_id, score) in enumerate(recommendations, 1):
        print(f"{rank:<6} {item_id:<20} {score:.4f}")
    
    return recommendations


def example_batch_recommend():
    """
    示例2: 批量推荐
    场景: 首页Feed流，为所有活跃用户生成推荐
    """
    print("\n" + "=" * 50)
    print("示例2: 批量推荐")
    print("=" * 50)
    
    # 加载数据
    data = load_data('output/cleaned', sample_size=50000)
    processor = FeatureProcessor(data)
    train_data, _ = processor.process(test_ratio=0.2)
    
    # 训练模型
    model = create_recommender('deepfm', embedding_dim=64, epochs=3)
    model.fit(train_data, verbose=False)
    model.set_feature_dims(train_data)
    
    # 模拟用户列表 (生产环境中从数据库读取)
    active_users = list(train_data.user2idx.keys())[:5]
    print(f"\n活跃用户数: {len(active_users)}")
    
    # 批量生成推荐
    print("\n批量生成推荐...")
    all_recommendations = {}
    
    for user_id in active_users:
        # 获取用户已知物品
        known_items = set(
            data.interactions[data.interactions['user_id'] == user_id]['item_id'].values
        )
        
        # 推荐
        recs = model.recommend(user_id, n=5, known_items=known_items)
        all_recommendations[user_id] = recs
    
    # 输出结果
    print("\n推荐结果汇总:")
    for user_id, recs in all_recommendations.items():
        item_ids = [item_id for item_id, _ in recs]
        print(f"  用户 {user_id}: 推荐 {len(recs)} 个物品 - {item_ids[:3]}...")
    
    return all_recommendations


def example_with_item_info():
    """
    示例3: 带物品信息的推荐
    场景: 推荐物品时同时返回物品详情 (标题、类别等)
    """
    print("\n" + "=" * 50)
    print("示例3: 带物品信息的推荐")
    print("=" * 50)
    
    # 加载数据和训练模型
    data = load_data('output/cleaned', sample_size=50000)
    processor = FeatureProcessor(data)
    train_data, _ = processor.process(test_ratio=0.2)
    model = create_recommender('deepfm', embedding_dim=64, epochs=3)
    model.fit(train_data, verbose=False)
    model.set_feature_dims(train_data)
    
    # 获取推荐
    user_id = list(train_data.user2idx.keys())[0]
    recommendations = model.recommend(user_id, n=5)
    
    # 获取物品信息
    print("\n推荐结果 (含物品信息):")
    print("-" * 60)
    print(f"{'排名':<4} {'物品ID':<15} {'得分':<8} {'一级分类':<15}")
    print("-" * 60)
    
    item_features = data.item_features
    
    for rank, (item_id, score) in enumerate(recommendations, 1):
        # 查询物品信息
        item_info = item_features[item_features['item_id'] == item_id]
        if len(item_info) > 0:
            category = item_info.iloc[0].get('first_level_category_name', 'N/A')
        else:
            category = 'N/A'
        
        print(f"{rank:<4} {item_id:<15} {score:<8.4f} {category:<15}")
    
    return recommendations


def example_api_format():
    """
    示例4: API返回格式
    场景: 为前端/API提供标准化返回格式
    """
    print("\n" + "=" * 50)
    print("示例4: API返回格式")
    print("=" * 50)
    
    # 加载数据和训练模型
    data = load_data('output/cleaned', sample_size=50000)
    processor = FeatureProcessor(data)
    train_data, _ = processor.process(test_ratio=0.2)
    model = create_recommender('deepfm', embedding_dim=64, epochs=3)
    model.fit(train_data, verbose=False)
    model.set_feature_dims(train_data)
    
    user_id = list(train_data.user2idx.keys())[0]
    recommendations = model.recommend(user_id, n=10)
    
    # 构造API返回格式
    api_response = {
        "code": 200,
        "message": "success",
        "data": {
            "user_id": str(user_id),  # 转为字符串
            "request_id": "req_123456",  # 请求ID，用于追踪
            "total": 10,
            "items": []
        }
    }
    
    # 填充推荐结果
    for rank, (item_id, score) in enumerate(recommendations, 1):
        api_response["data"]["items"].append({
            "rank": rank,
            "item_id": str(item_id),  # 转为字符串
            "score": float(score),
            "reason": "猜你喜欢"  # 可解释性原因
        })
    
    print("\nAPI返回 JSON:")
    import json
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    return api_response


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("短视频推荐系统 - 使用示例")
    print("=" * 60)
    
    # 运行所有示例
    example_single_user()
    example_batch_recommend()
    example_with_item_info()
    example_api_format()
    
    print("\n" + "=" * 60)
    print("所有示例执行完成!")
    print("=" * 60)
