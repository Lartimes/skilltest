# -*- coding: utf-8 -*-
"""
Item Distribution Analyzer - 物品分布分析
分析物品流行度、物品类型等
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer, clean_series


class ItemDistributionAnalyzer(BaseAnalyzer):
    """物品分布分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[2/13] Item Distribution Analysis...")
        
        df_inter = self.get_df("rec_inter")
        df_item = self.get_df("item_features")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        plt.suptitle("物品分布分析", fontsize=16, fontweight='bold')
        
        # 1. 物品流行度分布
        ax = axes[0, 0]
        counts = df_inter.groupby("item_id").size()
        ax.hist(np.log1p(counts), bins=50, color=self.colors['danger'], edgecolor='white', alpha=0.7)
        ax.set_xlabel("对数(交互数)")
        ax.set_ylabel("物品数量")
        ax.set_title("物品流行度分布（长尾）")
        ax.axvline(np.log1p(counts.median()), color='red', linestyle='--', label="中位数")
        ax.legend()
        
        # 2. 物品交互次数统计
        ax = axes[0, 1]
        item_stats = counts.describe()
        stats_labels = ['均值', '标准差', '最小', '25%', '50%', '75%', '最大']
        stats_values = np.array([item_stats['mean'], item_stats['std'], item_stats['min'], 
                       item_stats['25%'], item_stats['50%'], item_stats['75%'], item_stats['max']])
        bars = ax.bar(stats_labels, np.log1p(stats_values + 1), color=self.colors['warning'], edgecolor='white')
        ax.set_ylabel("对数(交互数+1)")
        ax.set_title("物品交互次数统计")
        ax.tick_params(axis='x', rotation=45)
        
        # 3. 物品类型分布
        ax = axes[0, 2]
        if "item_type" in df_item.columns:
            counts = df_item["item_type"].value_counts()
            counts.index = clean_series(counts.index)
            ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%',
                  colors=plt.cm.Set3.colors[:len(counts)], startangle=90)
            ax.set_title("物品类型分布")
        
        # 4. 一级类别分布
        ax = axes[1, 0]
        if "first_level_category_name" in df_item.columns:
            cats = df_item["first_level_category_name"].value_counts().head(10)
            cats.index = clean_series(cats.index)
            ax.barh(range(len(cats)), cats.values, color=self.colors['purple'])
            ax.set_yticks(range(len(cats)))
            ax.set_yticklabels([str(x)[:15] for x in cats.index], fontsize=9)
            ax.set_xlabel("视频数量")
            ax.set_title("一级类别分布 (Top10)")
            ax.invert_yaxis()
        
        # 5. 物品流行度箱线图
        ax = axes[1, 1]
        if len(df_inter) > 0:
            item_popularity = df_inter.groupby("item_id").size()
            ax.boxplot([np.log1p(item_popularity)], labels=['物品流行度'])
            ax.set_ylabel("对数(交互数)")
            ax.set_title("物品流行度箱线图")
        
        # 6. 热门物品占比
        ax = axes[1, 2]
        total_items = df_item['item_id'].nunique()
        popular_items = counts[counts >= counts.quantile(0.9)].shape[0]
        cold_items = total_items - popular_items
        ax.pie([popular_items, cold_items], labels=['热门物品(Top10%)', '冷门物品'], autopct='%1.1f%%',
              colors=[self.colors['success'], self.colors['primary']], startangle=90)
        ax.set_title(f"物品冷热占比\n(总物品: {total_items:,})")
        
        plt.tight_layout()
        path = self.save_fig(fig, "item_distribution.png")
        print(f"  [OK] {path.name}")
        return {"item_distribution.png": path}
