# -*- coding: utf-8 -*-
"""
推荐系统推理脚本
用于加载训练好的模型，给定用户ID，输出推荐结果

使用方法:
    python -m src.models.inference
"""

from src.models import load_data, FeatureProcessor, create_recommender
import torch
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger(__name__)


class Recommender:
    """推荐系统推理封装类"""
    
    def __init__(self, model_path: str, data_dir: str = 'output/cleaned'):
        """
        初始化推荐系统
        
        Args:
            model_path: 模型文件路径 (.pkl)
            data_dir: 清洗后数据目录
        """
        self.model_path = model_path
        self.data_dir = data_dir
        
        # 加载模型和数据
        self._load_model()
        self._load_data()
        
    def _load_model(self):
        """加载模型"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"模型文件不存在: {self.model_path}")
        
        # 获取模型类型
        if 'deepfm' in self.model_path.lower():
            model_name = 'deepfm'
        elif 'neumf' in self.model_path.lower():
            model_name = 'neumf'
        elif 'mf' in self.model_path.lower():
            model_name = 'mf'
        else:
            raise ValueError(f"无法识别模型类型: {self.model_path}")
        
        # 加载checkpoint
        checkpoint = torch.load(self.model_path, map_location='cpu')
        
        # 创建模型
        self.model = create_recommender(model_name)
        self.model.set_feature_dims_from_checkpoint(checkpoint)
        self.model.build_model()
        self.model.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.model.eval()
        self.model.is_fitted = True
        
        logger.info(f"模型加载成功: {model_name}")
        
    def _load_data(self):
        """加载数据"""
        self.data = load_data(self.data_dir)
        logger.info(f"数据加载成功: 用户{self.data.n_users}, 物品{self.data.n_items}")
        
        # 设置ID映射
        self.model.user2idx = self.data.user2idx
        self.model.idx2user = self.data.idx2user
        self.model.item2idx = self.data.item2idx
        self.model.idx2item = self.data.idx2item
        self.model.n_items = self.data.n_items
        
    def recommend(self, user_id, n: int = 10, exclude_known: bool = True) -> list:
        """
        为用户推荐物品
        
        Args:
            user_id: 用户ID
            n: 推荐数量
            exclude_known: 是否排除用户已交互的物品
        
        Returns:
            推荐列表 [(item_id, score), ...]
        """
        # 获取用户已知交互的物品
        known_items = set()
        if exclude_known:
            user_interactions = self.data.interactions[
                self.data.interactions['user_id'] == user_id
            ]
            known_items = set(user_interactions['item_id'].values) if len(user_interactions) > 0 else set()
        
        # 调用模型的recommend方法
        recommendations = self.model.recommend(
            user_id=user_id,
            n=n,
            exclude_known=exclude_known,
            known_items=known_items
        )
        
        return recommendations
    
    def batch_recommend(self, user_ids: list, n: int = 10) -> dict:
        """
        批量为多个用户推荐
        
        Args:
            user_ids: 用户ID列表
            n: 每个用户的推荐数量
        
        Returns:
            {user_id: [(item_id, score), ...], ...}
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = self.recommend(user_id, n=n)
        return results
    
    def get_user_profile(self, user_id: int) -> dict:
        """获取用户基本信息"""
        if user_id not in self.model.user2idx:
            return {"error": "用户不存在"}
        
        u_idx = self.model.user2idx[user_id]
        user_data = self.data.user_features
        
        if user_id in user_data['user_id'].values:
            profile = user_data[user_data['user_id'] == user_id].iloc[0].to_dict()
            return profile
        return {"user_id": user_id, "index": u_idx}
    
    def get_item_info(self, item_id: int) -> dict:
        """获取物品基本信息"""
        if item_id not in self.model.item2idx:
            return {"error": "物品不存在"}
        
        item_data = self.data.item_features
        if item_id in item_data['item_id'].values:
            info = item_data[item_data['item_id'] == item_id].iloc[0].to_dict()
            return info
        return {"item_id": item_id}


def demo():
    """演示推荐系统使用"""
    
    print("\n" + "=" * 60)
    print("短视频推荐系统 - 推理演示")
    print("=" * 60)
    
    # 方法1: 如果已有训练好的模型
    model_path = 'output/models/deepfm_best.pkl'
    
    # 检查是否有模型文件
    if os.path.exists(model_path):
        print(f"\n[方式1] 使用已训练的模型: {model_path}")
        recommender = Recommender(model_path)
    else:
        # 方法2: 训练新模型
        print("\n[方式2] 训练新模型...")
        recommender = train_new_model()
    
    # ========== 演示推荐 ==========
    print("\n" + "-" * 40)
    print("推荐演示")
    print("-" * 40)
    
    # 随机选择一个用户
    sample_user = list(recommender.model.user2idx.keys())[0]
    print(f"\n为用户 {sample_user} 推荐:")
    
    # 获取推荐结果
    recommendations = recommender.recommend(user_id=sample_user, n=10)
    
    print(f"\n{'排名':<6} {'物品ID':<20} {'预测得分':<10}")
    print("-" * 40)
    for rank, (item_id, score) in enumerate(recommendations, 1):
        print(f"{rank:<6} {item_id:<20} {score:.4f}")
    
    # ========== 批量推荐 ==========
    print("\n" + "-" * 40)
    print("批量推荐演示")
    print("-" * 40)
    
    # 选择多个用户
    all_users = list(recommender.model.user2idx.keys())[:3]
    batch_results = recommender.batch_recommend(all_users, n=5)
    
    for user_id, recs in batch_results.items():
        print(f"\n用户 {user_id}:")
        for rank, (item_id, score) in enumerate(recs, 1):
            print(f"  {rank}. 物品{item_id} (得分: {score:.4f})")
    
    return recommender


def train_new_model():
    """训练并返回新模型"""
    print("\n[训练新模型...]")
    
    from src.models import load_data, FeatureProcessor, create_recommender
    
    # 1. 加载数据
    data = load_data('output/cleaned', sample_size=50000)
    print(f"数据: 用户{data.n_users}, 物品{data.n_items}")
    
    # 2. 特征工程
    processor = FeatureProcessor(data)
    train_data, _ = processor.process(test_ratio=0.2)
    
    # 3. 构建并训练模型
    model = create_recommender('deepfm', embedding_dim=64, epochs=3)
    model.fit(train_data, verbose=True)
    
    # 4. 保存模型
    save_path = 'output/models/deepfm_inference_demo.pkl'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save(save_path)
    print(f"模型已保存: {save_path}")
    
    # 5. 封装为推理类
    recommender = Recommender.__new__(Recommender)
    recommender.model = model
    recommender.data = data
    recommender.model_path = save_path
    
    return recommender


if __name__ == '__main__':
    recommender = demo()
