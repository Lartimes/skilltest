# -*- coding: utf-8 -*-
"""
Category Analyzer - 类别分析
分析类别覆盖率、标题分析
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer, clean_series


class CategoryAnalyzer(BaseAnalyzer):
    """类别分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[7/13] Category Analysis...")
        
        df_item = self.get_df("item_features")
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        plt.suptitle("类别覆盖率与标题分析", fontsize=16, fontweight='bold')
        
        levels = [
            ('first_level_category_name', '一级'),
            ('second_level_category_name', '二级'),
            ('third_level_category_name', '三级'),
            ('fourth_level_category_name', '四级'),
        ]
        
        # 1. 各级别覆盖率
        ax = axes[0, 0]
        data = []
        for col, name in levels:
            if col in df_item.columns:
                coverage = df_item[col].notna().sum() / len(df_item) * 100
                data.append((name, coverage))
        names = [x[0] for x in data]
        coverage = [x[1] for x in data]
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
        bars = ax.bar(names, coverage, color=colors, edgecolor='white')
        ax.set_ylabel("覆盖率 (%)")
        ax.set_title("各级别类别覆盖率")
        ax.set_ylim(0, 110)
        for bar, cov in zip(bars, coverage):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{cov:.1f}%', ha='center')
        
        # 2. 各级别唯一数量
        ax = axes[0, 1]
        data = []
        for col, name in levels:
            if col in df_item.columns:
                data.append((name, df_item[col].nunique()))
        names = [x[0] for x in data]
        counts = [x[1] for x in data]
        bars = ax.bar(names, counts, color=colors, edgecolor='white')
        ax.set_ylabel("唯一类别数量")
        ax.set_title("各级别唯一类别数量")
        for i, cnt in enumerate(counts):
            ax.text(i, cnt + 5, str(cnt), ha='center')
        
        # 3. 一级类别占比
        ax = axes[0, 2]
        if "first_level_category_name" in df_item.columns:
            counts = df_item["first_level_category_name"].value_counts()
            top_n = min(8, len(counts))
            top_cats = counts.head(top_n).copy()
            top_cats.index = clean_series(top_cats.index)
            others = counts.iloc[top_n:].sum() if len(counts) > top_n else 0
            if others > 0:
                top_cats['其他'] = others
            ax.pie(top_cats.values, labels=top_cats.index, autopct='%1.1f%%',
                  colors=plt.cm.tab10.colors[:len(top_cats)], startangle=90)
            ax.set_title("一级类别占比 (Top8+其他)")
        
        # 4. 标题长度分布
        ax = axes[1, 0]
        if "caption" in df_item.columns:
            has_caption = df_item['caption'].notna() & (df_item['caption'] != '')
            lengths = df_item.loc[has_caption, 'caption'].str.len()
            ax.hist(lengths.clip(0, 200), bins=40, color=self.colors['success'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("标题长度 (字符)")
            ax.set_ylabel("视频数量")
            ax.set_title(f"视频标题长度分布\n(有标题: {has_caption.sum():,} / {len(df_item):,})")
            ax.axvline(lengths.median(), color='red', linestyle='--', label=f"中位数: {lengths.median():.0f}")
            ax.legend()
        
        # 5. 类别-视频数关系
        ax = axes[1, 1]
        if "first_level_category_name" in df_item.columns:
            cat_counts = df_item["first_level_category_name"].value_counts()
            cat_counts.index = clean_series(cat_counts.index)
            ax.bar(range(len(cat_counts)), cat_counts.values, color=self.colors['purple'], edgecolor='white')
            ax.set_xticks(range(len(cat_counts)))
            ax.set_xticklabels(cat_counts.index, rotation=45, ha='right')
            ax.set_ylabel("视频数量")
            ax.set_title("一级类别视频数分布")
        
        # 6. 覆盖率vs数量
        ax = axes[1, 2]
        if "first_level_category_name" in df_item.columns:
            cat_stats = df_item.groupby("first_level_category_name").agg({
                'item_id': 'count',
                'caption': lambda x: x.notna().sum() / len(x) * 100
            })
            cat_stats.columns = ['视频数', '标题覆盖率']
            cat_stats = cat_stats.sort_values('视频数', ascending=False).head(10)
            ax.scatter(cat_stats['视频数'], cat_stats['标题覆盖率'], 
                      s=100, c=range(len(cat_stats)), cmap='viridis', alpha=0.7)
            ax.set_xlabel("视频数量")
            ax.set_ylabel("标题覆盖率 (%)")
            ax.set_title("类别-视频数vs标题覆盖率")
        
        plt.tight_layout()
        path = self.save_fig(fig, "category_coverage.png")
        print(f"  [OK] {path.name}")
        return {"category_coverage.png": path}
