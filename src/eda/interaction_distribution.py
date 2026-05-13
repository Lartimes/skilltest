# -*- coding: utf-8 -*-
"""
Interaction Distribution Analyzer - 交互行为分布分析
分析转发、点赞、关注、点击等行为
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer, clean_series


class InteractionDistributionAnalyzer(BaseAnalyzer):
    """交互行为分布分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[3/13] Interaction Distribution Analysis...")
        
        df_inter = self.get_df("rec_inter")
        df_src = self.get_df("src_inter")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        plt.suptitle("交互行为分布分析", fontsize=16, fontweight='bold')
        
        # 1. 交互行为数量分布
        ax = axes[0, 0]
        action_cols = ["forward", "like", "follow", "click"]
        labels_cn = {"forward": "转发", "like": "点赞", "follow": "关注", "click": "点击"}
        action_counts = df_inter[action_cols].sum()
        colors = [self.colors['success'], self.colors['danger'], self.colors['primary'], self.colors['warning']]
        bars = ax.bar([labels_cn[c] for c in action_cols], action_counts.values, color=colors)
        ax.set_ylabel("次数")
        ax.set_title("交互行为数量")
        for bar, val in zip(bars, action_counts.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val/1e6:.1f}M', ha='center', va='bottom')
        
        # 2. 交互行为占比
        ax = axes[0, 1]
        ax.pie(action_counts.values, labels=[labels_cn[c] for c in action_cols], autopct='%1.1f%%',
              colors=colors, startangle=90)
        ax.set_title("交互行为占比")
        
        # 3. 搜索来源分布
        ax = axes[0, 2]
        if "search_source" in df_src.columns:
            counts = df_src["search_source"].value_counts().head(6)
            counts.index = clean_series(counts.index)
            ax.bar(range(len(counts)), counts.values, color=self.colors['success'], edgecolor='white')
            ax.set_xticks(range(len(counts)))
            ax.set_xticklabels(counts.index, rotation=45, ha='right')
            ax.set_ylabel("搜索次数")
            ax.set_title("搜索来源分布")
        
        # 4. 各行为用户分布
        ax = axes[1, 0]
        user_actions = df_inter.groupby("user_id")[action_cols].sum()
        for col, label in labels_cn.items():
            ax.hist(np.log1p(user_actions[col] + 1), bins=30, alpha=0.5, label=label)
        ax.set_xlabel("对数(行为次数+1)")
        ax.set_ylabel("用户数量")
        ax.set_title("各行为用户分布")
        ax.legend()
        
        # 5. 行为相关性
        ax = axes[1, 1]
        if len(action_cols) >= 2:
            corr = user_actions.corr()
            corr.columns = [labels_cn[c] for c in corr.columns]
            corr.index = [labels_cn[c] for c in corr.index]
            im = ax.imshow(corr.values, cmap='RdYlBu_r', vmin=-1, vmax=1)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.index)))
            ax.set_xticklabels(corr.columns, rotation=45)
            ax.set_yticklabels(corr.index)
            ax.set_title("行为相关性")
            plt.colorbar(im, ax=ax)
        
        # 6. 交互广度（每用户交互物品数）
        ax = axes[1, 2]
        user_breadth = df_inter.groupby("user_id")['item_id'].nunique()
        ax.hist(np.log1p(user_breadth), bins=40, color=self.colors['purple'], edgecolor='white', alpha=0.7)
        ax.set_xlabel("对数(交互物品数)")
        ax.set_ylabel("用户数量")
        ax.set_title(f"用户交互广度\n(中位数: {user_breadth.median():.0f})")
        
        plt.tight_layout()
        path = self.save_fig(fig, "interaction_distribution.png")
        print(f"  [OK] {path.name}")
        return {"interaction_distribution.png": path}
