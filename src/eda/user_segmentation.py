# -*- coding: utf-8 -*-
"""
User Segmentation Analyzer - 用户分群分析
按活跃度分层
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class UserSegmentationAnalyzer(BaseAnalyzer):
    """用户分群分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[10/13] User Segmentation Analysis...")
        
        df_inter = self.get_df("rec_inter")
        df_user = self.get_df("user_features")
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        plt.suptitle("用户分群分析", fontsize=16, fontweight='bold')
        
        # 1. 用户活跃度分层
        ax = axes[0, 0]
        if len(df_inter) > 0:
            user_activity = df_inter.groupby("user_id").agg({
                "item_id": "count",
                "playing_time": "sum",
                "like": "sum",
                "forward": "sum"
            }).reset_index()
            user_activity.columns = ["user_id", "interactions", "watch_time", "likes", "forwards"]
            
            q25, q50, q75 = user_activity["interactions"].quantile([0.25, 0.5, 0.75])
            bins = [0, q25, q50, q75, float('inf')]
            labels = ['低活跃', '中低活跃', '中高活跃', '高活跃']
            user_activity['segment'] = pd.cut(user_activity["interactions"], bins=bins, labels=labels)
            
            seg_counts = user_activity['segment'].value_counts()
            ax.pie(seg_counts.values, labels=seg_counts.index, autopct='%1.1f%%',
                  colors=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'], startangle=90)
            ax.set_title(f"用户活跃度分层\n(阈值: {q25:.0f}/{q50:.0f}/{q75:.0f})")
        
        # 2. 各层用户平均行为
        ax = axes[0, 1]
        if len(df_inter) > 0:
            seg_stats = user_activity.groupby('segment', observed=True).agg({
                'interactions': 'mean',
                'watch_time': 'mean',
                'likes': 'mean'
            })
            x = range(len(labels))
            width = 0.25
            ax.bar([i - width for i in x], seg_stats['interactions'], width, label='互动数', color='#3498db')
            ax.bar(x, seg_stats['watch_time'] / 1000, width, label='观看时长(s)', color='#2ecc71')
            ax.bar([i + width for i in x], seg_stats['likes'], width, label='点赞数', color='#e74c3c')
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.set_ylabel("平均值")
            ax.set_title("各层用户平均行为")
            ax.legend(fontsize=8)
        
        # 3. 用户活跃度分布
        ax = axes[0, 2]
        if len(df_inter) > 0:
            ax.hist(np.log1p(user_activity["interactions"]), bins=50, 
                   color=self.colors['primary'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("对数(互动数)")
            ax.set_ylabel("用户数量")
            ax.set_title("用户活跃度分布 (对数)")
            for q, name in zip([q25, q50, q75], ['Q25', 'Q50', 'Q75']):
                ax.axvline(np.log1p(q), color='red', linestyle='--', alpha=0.7)
            ax.legend(['Q25', 'Q50', 'Q75'])
        
        # 4. 各层用户数量
        ax = axes[1, 0]
        if len(df_inter) > 0:
            seg_sizes = user_activity['segment'].value_counts()
            bars = ax.bar(labels, [seg_sizes.get(l, 0) for l in labels], 
                         color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'], edgecolor='white')
            ax.set_ylabel("用户数量")
            ax.set_title("各层用户数量")
            for bar, val in zip(bars, [seg_sizes.get(l, 0) for l in labels]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                       f'{val:,}', ha='center')
        
        # 5. 用户特征分布
        ax = axes[1, 1]
        if "onehot_feat1" in df_user.columns:
            feat_counts = df_user["onehot_feat1"].value_counts()
            ax.bar(range(len(feat_counts)), feat_counts.values, color=self.colors['purple'], edgecolor='white')
            ax.set_xticks(range(len(feat_counts)))
            ax.set_xticklabels([str(x) for x in feat_counts.index])
            ax.set_xlabel("onehot_feat1")
            ax.set_ylabel("用户数量")
            ax.set_title("用户特征分布")
        
        # 6. 层内行为分布
        ax = axes[1, 2]
        if len(df_inter) > 0:
            for i, seg in enumerate(labels):
                seg_data = user_activity[user_activity['segment'] == seg]['interactions']
                ax.hist(np.log1p(seg_data), bins=20, alpha=0.5, label=seg)
            ax.set_xlabel("对数(互动数)")
            ax.set_ylabel("用户数量")
            ax.set_title("各层活跃度分布")
            ax.legend()
        
        plt.tight_layout()
        path = self.save_fig(fig, "user_segmentation.png")
        print(f"  [OK] {path.name}")
        return {"user_segmentation.png": path}
