# -*- coding: utf-8 -*-
"""
Social Network Analyzer - 社交网络分析
分析关注关系、粉丝网络
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class SocialNetworkAnalyzer(BaseAnalyzer):
    """社交网络分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[5/13] Social Network Analysis...")
        
        df_social = self.get_df("social_network")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        plt.suptitle("社交网络分析", fontsize=16, fontweight='bold')
        
        if len(df_social) > 0:
            # 1. 关注数分布
            ax = axes[0, 0]
            if "user_id" in df_social.columns:
                follow_counts = df_social.groupby("user_id").size()
                ax.hist(np.log1p(follow_counts), bins=30, color='#9b59b6', edgecolor='white', alpha=0.7)
                ax.set_xlabel("对数(关注数)")
                ax.set_ylabel("用户数量")
                ax.set_title(f"用户关注数分布\n(中位数: {follow_counts.median():.0f})")
            
            # 2. 被关注数分布
            ax = axes[0, 1]
            col = "follower_id" if "follower_id" in df_social.columns else df_social.columns[1]
            follower_counts = df_social.groupby(col).size()
            ax.hist(np.log1p(follower_counts), bins=30, color='#3498db', edgecolor='white', alpha=0.7)
            ax.set_xlabel("对数(粉丝数)")
            ax.set_ylabel("用户数量")
            ax.set_title(f"用户粉丝数分布\n(中位数: {follower_counts.median():.0f})")
            
            # 3. 网络规模统计
            ax = axes[0, 2]
            unique_users = df_social['user_id'].nunique()
            unique_followers = df_social[col].nunique()
            total_edges = len(df_social)
            stats = ['关注用户', '粉丝用户', '关注边']
            values = [unique_users, unique_followers, total_edges]
            bars = ax.bar(stats, values, color=['#9b59b6', '#3498db', '#2ecc71'], edgecolor='white')
            ax.set_ylabel("数量")
            ax.set_title("社交网络规模")
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                       f'{val:,}', ha='center')
            
            # 4. 度统计
            ax = axes[1, 0]
            out_stats = follow_counts.describe()
            in_stats = follower_counts.describe()
            stats_labels = ['出度-均值', '出度-最大', '入度-均值', '入度-最大']
            stats_values = [out_stats['mean'], out_stats['max'], in_stats['mean'], in_stats['max']]
            bars = ax.bar(stats_labels, stats_values, color=['#9b59b6', '#9b59b6', '#3498db', '#3498db'])
            ax.set_ylabel("数量")
            ax.set_title("网络度统计")
            
            # 5. 出度vs入度散点图
            ax = axes[1, 1]
            user_degree = pd.DataFrame({
                'out_degree': follow_counts,
                'in_degree': follower_counts
            }).fillna(0)
            ax.scatter(np.log1p(user_degree['out_degree']), np.log1p(user_degree['in_degree']), 
                      alpha=0.3, s=10, color='#3498db')
            ax.set_xlabel("对数(出度)")
            ax.set_ylabel("对数(入度)")
            ax.set_title("出度vs入度分布")
            
            # 6. 关注/粉丝比例
            ax = axes[1, 2]
            ratio_data = {
                '关注数>粉丝数': (follow_counts > follower_counts.reindex(follow_counts.index).fillna(0)).sum(),
                '粉丝数>关注数': (follower_counts > follow_counts.reindex(follower_counts.index).fillna(0)).sum(),
                '相等': (follow_counts == follower_counts.reindex(follow_counts.index).fillna(0)).sum(),
            }
            ax.pie(ratio_data.values(), labels=ratio_data.keys(), autopct='%1.1f%%',
                  colors=['#3498db', '#e74c3c', '#2ecc71'], startangle=90)
            ax.set_title("关注/粉丝对比")
        else:
            for ax in axes.flat:
                ax.text(0.5, 0.5, '社交数据不足', ha='center', va='center', fontsize=14)
                ax.axis('off')
        
        plt.tight_layout()
        path = self.save_fig(fig, "social_network.png")
        print(f"  [OK] {path.name}")
        return {"social_network.png": path}
