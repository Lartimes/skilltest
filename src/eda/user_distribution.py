# -*- coding: utf-8 -*-
"""
User Distribution Analyzer - 用户分布分析
分析用户活跃度、用户特征等
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class UserDistributionAnalyzer(BaseAnalyzer):
    """用户分布分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[1/13] User Distribution Analysis...")
        
        df_inter = self.get_df("rec_inter")
        df_user = self.get_df("user_features")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        plt.suptitle("用户分布分析", fontsize=16, fontweight='bold')
        
        # 1. 用户活跃度分布
        ax = axes[0, 0]
        counts = df_inter.groupby("user_id").size()
        ax.hist(np.log1p(counts), bins=50, color=self.colors['primary'], edgecolor='white', alpha=0.7)
        ax.set_xlabel("对数(交互数)")
        ax.set_ylabel("用户数量")
        ax.set_title("用户活跃度分布（长尾）")
        ax.axvline(np.log1p(counts.median()), color='red', linestyle='--', label=f"中位数")
        ax.legend()
        
        # 2. 用户交互次数统计
        ax = axes[0, 1]
        user_stats = counts.describe()
        stats_labels = ['均值', '标准差', '最小', '25%', '50%', '75%', '最大']
        stats_values = [user_stats['mean'], user_stats['std'], user_stats['min'], 
                       user_stats['25%'], user_stats['50%'], user_stats['75%'], user_stats['max']]
        bars = ax.bar(stats_labels, np.log1p(stats_values), color=self.colors['success'], edgecolor='white')
        ax.set_ylabel("对数(交互数)")
        ax.set_title("用户交互次数统计")
        ax.tick_params(axis='x', rotation=45)
        
        # 3. 用户独热特征分布
        ax = axes[0, 2]
        if "onehot_feat1" in df_user.columns:
            feat_counts = df_user["onehot_feat1"].value_counts().sort_index()
            ax.bar(feat_counts.index.astype(str), feat_counts.values, color=self.colors['warning'], edgecolor='white')
            ax.set_xlabel("onehot_feat1")
            ax.set_ylabel("用户数量")
            ax.set_title("用户独热特征分布")
        
        # 4. 用户搜索活跃等级
        ax = axes[1, 0]
        if "search_active_level" in df_user.columns:
            level_counts = df_user["search_active_level"].value_counts().sort_index()
            ax.bar(level_counts.index.astype(str), level_counts.values, color=self.colors['purple'], edgecolor='white')
            ax.set_xlabel("活跃等级")
            ax.set_ylabel("用户数量")
            ax.set_title("用户搜索活跃等级")
        
        # 5. 用户活跃度箱线图
        ax = axes[1, 1]
        if len(df_inter) > 0:
            user_activity = df_inter.groupby("user_id").size()
            ax.boxplot([np.log1p(user_activity)], labels=['用户活跃度'])
            ax.set_ylabel("对数(交互数)")
            ax.set_title("用户活跃度箱线图")
        
        # 6. 活跃用户占比
        ax = axes[1, 2]
        total_users = len(df_user)
        active_users = df_inter['user_id'].nunique()
        inactive = total_users - active_users
        ax.pie([active_users, inactive], labels=['活跃用户', '沉默用户'], autopct='%1.1f%%',
              colors=[self.colors['success'], self.colors['danger']], startangle=90)
        ax.set_title(f"用户活跃占比\n(总用户: {total_users:,})")
        
        plt.tight_layout()
        path = self.save_fig(fig, "user_distribution.png")
        print(f"  [OK] {path.name}")
        return {"user_distribution.png": path}
