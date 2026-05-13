# -*- coding: utf-8 -*-
"""
Item Quality Analyzer - 物品质量分析
分析物品播放、点赞、评论、分享等质量指标
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class ItemQualityAnalyzer(BaseAnalyzer):
    """物品质量分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[13/13] Item Quality Analysis...")
        
        df_inter = self.get_df("rec_inter")
        df_item = self.get_df("item_features")
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        plt.suptitle("物品质量分析", fontsize=16, fontweight='bold')
        
        if len(df_inter) > 0:
            # 计算物品质量指标
            item_quality = df_inter.groupby("item_id").agg({
                "forward": "sum",
                "like": "sum",
                "follow": "sum",
                "click": "sum",
                "playing_time": "sum"
            }).reset_index()
            
            # 1. 物品点赞分布
            ax = axes[0, 0]
            ax.hist(np.log1p(item_quality['like']), bins=50, color=self.colors['danger'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("对数(点赞数+1)")
            ax.set_ylabel("物品数量")
            ax.set_title(f"物品点赞数分布\n(均值: {item_quality['like'].mean():.1f})")
            
            # 2. 物品转发分布
            ax = axes[0, 1]
            ax.hist(np.log1p(item_quality['forward'] + 1), bins=50, color=self.colors['success'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("对数(转发数+1)")
            ax.set_ylabel("物品数量")
            ax.set_title(f"物品转发数分布\n(均值: {item_quality['forward'].mean():.1f})")
            
            # 3. 物品质量指标对比
            ax = axes[0, 2]
            metrics = ['转发', '点赞', '关注', '点击']
            metric_cols = ['forward', 'like', 'follow', 'click']
            totals = [item_quality[c].sum() for c in metric_cols]
            bars = ax.bar(metrics, totals, color=[self.colors['success'], self.colors['danger'], 
                                                  self.colors['primary'], self.colors['warning']], edgecolor='white')
            ax.set_ylabel("总次数")
            ax.set_title("物品交互指标总量")
            for bar, val in zip(bars, totals):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val/1e6:.1f}M', ha='center')
            
            # 4. 播放时长分布
            ax = axes[1, 0]
            total_time = item_quality['playing_time'] / 1000  # 转为秒
            ax.hist(total_time.clip(0, 1000), bins=50, color=self.colors['purple'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("总播放时长 (秒)")
            ax.set_ylabel("物品数量")
            ax.set_title(f"物品总播放时长分布\n(均值: {total_time.mean():.0f}秒)")
            
            # 5. 物品互动率
            ax = axes[1, 1]
            item_clicks = df_inter.groupby("item_id")['click'].sum()
            item_interactions = df_inter.groupby("item_id").size()
            interaction_rate = (item_clicks / item_interactions).clip(0, 1)
            ax.hist(interaction_rate, bins=50, color=self.colors['warning'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("互动率 (点击/曝光)")
            ax.set_ylabel("物品数量")
            ax.set_title(f"物品互动率分布\n(均值: {interaction_rate.mean():.2f})")
            
            # 6. 物品质量散点图
            ax = axes[1, 2]
            ax.scatter(np.log1p(item_quality['like']), np.log1p(item_quality['forward']), 
                      alpha=0.3, s=10, c=item_quality['click'] / item_quality['click'].max(), 
                      cmap='viridis')
            ax.set_xlabel("对数(点赞数)")
            ax.set_ylabel("对数(转发数)")
            ax.set_title("物品质量散点图\n(颜色=点击率)")
        else:
            for ax in axes.flat:
                ax.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=14)
                ax.axis('off')
        
        plt.tight_layout()
        path = self.save_fig(fig, "item_quality.png")
        print(f"  [OK] {path.name}")
        return {"item_quality.png": path}
