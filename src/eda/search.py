# -*- coding: utf-8 -*-
"""
Search Analyzer - 搜索行为分析
分析搜索来源、关键词、搜索偏好
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer, clean_series


class SearchAnalyzer(BaseAnalyzer):
    """搜索行为分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[12/13] Search Behavior Analysis...")
        
        df_src = self.get_df("src_inter")
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        plt.suptitle("搜索行为分析", fontsize=16, fontweight='bold')
        
        if len(df_src) > 0:
            # 1. 搜索来源分布
            ax = axes[0, 0]
            if "search_source" in df_src.columns:
                counts = df_src["search_source"].value_counts()
                counts.index = clean_series(counts.index)
                ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%',
                      colors=plt.cm.Set3.colors[:len(counts)], startangle=90)
                ax.set_title("搜索来源分布")
            
            # 2. 搜索关键词长度分布
            ax = axes[0, 1]
            if "keyword" in df_src.columns:
                keyword_lengths = df_src["keyword"].dropna().str.len()
                ax.hist(keyword_lengths.clip(0, 50), bins=30, color=self.colors['primary'], edgecolor='white', alpha=0.7)
                ax.set_xlabel("关键词长度")
                ax.set_ylabel("搜索次数")
                ax.set_title(f"搜索关键词长度分布\n(中位数: {keyword_lengths.median():.0f}字符)")
            
            # 3. 每用户搜索次数分布
            ax = axes[0, 2]
            if "user_id" in df_src.columns:
                searches_per_user = df_src.groupby("user_id").size()
                ax.hist(np.log1p(searches_per_user), bins=40, color=self.colors['success'], edgecolor='white', alpha=0.7)
                ax.set_xlabel("对数(搜索次数)")
                ax.set_ylabel("用户数量")
                ax.set_title(f"用户搜索次数分布\n(人均: {searches_per_user.mean():.1f}次)")
            
            # 4. 搜索物品类型分布
            ax = axes[1, 0]
            if "item_type" in df_src.columns:
                counts = df_src["item_type"].value_counts()
                counts.index = clean_series(counts.index)
                ax.barh(range(len(counts)), counts.values, color=self.colors['warning'], edgecolor='white')
                ax.set_yticks(range(len(counts)))
                ax.set_yticklabels(counts.index)
                ax.set_xlabel("搜索次数")
                ax.set_title("搜索物品类型分布")
                ax.invert_yaxis()
            
            # 5. 关键词长度统计
            ax = axes[1, 1]
            if "keyword" in df_src.columns:
                lengths = df_src["keyword"].dropna().str.len()
                stats = lengths.describe()
                stats_labels = ['均值', '标准差', '最小', '25%', '50%', '75%', '最大']
                stats_values = [stats['mean'], stats['std'], stats['min'], 
                               stats['25%'], stats['50%'], stats['75%'], stats['max']]
                bars = ax.bar(stats_labels, stats_values, color=self.colors['purple'], edgecolor='white')
                ax.set_ylabel("字符数")
                ax.set_title("关键词长度统计")
                ax.tick_params(axis='x', rotation=45)
            
            # 6. 热门搜索词
            ax = axes[1, 2]
            if "keyword" in df_src.columns:
                top_keywords = df_src["keyword"].value_counts().head(10)
                top_keywords.index = clean_series(top_keywords.index)
                ax.barh(range(len(top_keywords)), top_keywords.values, color=self.colors['danger'], edgecolor='white')
                ax.set_yticks(range(len(top_keywords)))
                ax.set_yticklabels([str(x)[:20] for x in top_keywords.index])
                ax.set_xlabel("搜索次数")
                ax.set_title("Top10热门搜索词")
                ax.invert_yaxis()
        else:
            for ax in axes.flat:
                ax.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=14)
                ax.axis('off')
        
        plt.tight_layout()
        path = self.save_fig(fig, "search_analysis.png")
        print(f"  [OK] {path.name}")
        return {"search_analysis.png": path}
