# -*- coding: utf-8 -*-
"""
Funnel Analyzer - 漏斗分析
分析用户行为转化漏斗
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class FunnelAnalyzer(BaseAnalyzer):
    """漏斗分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[9/13] Funnel Analysis...")
        
        df_inter = self.get_df("rec_inter")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        plt.suptitle("用户行为漏斗分析", fontsize=16, fontweight='bold')
        
        # 1. 行为转化漏斗
        ax = axes[0, 0]
        total = len(df_inter)
        clicked = df_inter['click'].sum()
        liked = df_inter['like'].sum()
        forwarded = df_inter['forward'].sum()
        followed = df_inter['follow'].sum()
        
        stages = ['曝光', '点击', '点赞', '转发', '关注']
        values = [total, clicked, liked, forwarded, followed]
        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
        
        max_val = values[0]
        norm_values = [v / max_val * 100 for v in values]
        
        bars = ax.barh(stages, norm_values, color=colors)
        ax.set_xlabel("相对比例 (%)")
        ax.set_title("用户行为转化漏斗 (归一化)")
        ax.set_xlim(0, 120)
        for bar, val, real in zip(bars, norm_values, values):
            ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, 
                   f'{real/1e6:.1f}M ({val:.1f}%)', va='center', fontsize=9)
        
        # 2. 各环节转化率
        ax = axes[0, 1]
        conversion_rates = {
            '点击率': clicked / total * 100 if total > 0 else 0,
            '点赞率': liked / clicked * 100 if clicked > 0 else 0,
            '转发率': forwarded / clicked * 100 if clicked > 0 else 0,
            '关注率': followed / clicked * 100 if clicked > 0 else 0,
        }
        bars = ax.bar(conversion_rates.keys(), conversion_rates.values(), 
                     color=['#3498db', '#2ecc71', '#e74c3c', '#9b59b6'], edgecolor='white')
        ax.set_ylabel("转化率 (%)")
        ax.set_title("各环节转化率")
        for bar, val in zip(bars, conversion_rates.values()):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                   f'{val:.2f}%', ha='center', fontsize=10)
        
        # 3. 漏斗阶梯图
        ax = axes[1, 0]
        ax.bar(range(len(stages)), norm_values, color=colors, edgecolor='white')
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages)
        ax.set_ylabel("相对比例 (%)")
        ax.set_title("漏斗阶梯图")
        for i, val in enumerate(norm_values):
            ax.text(i, val + 2, f'{val:.1f}%', ha='center')
        
        # 4. 绝对数值
        ax = axes[1, 1]
        ax.bar(range(len(stages)), [v/1e6 for v in values], color=colors, edgecolor='white')
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages)
        ax.set_ylabel("次数 (百万)")
        ax.set_title("漏斗绝对数值")
        for i, val in enumerate(values):
            ax.text(i, val/1e6 + 0.5, f'{val/1e6:.1f}M', ha='center')
        
        plt.tight_layout()
        path = self.save_fig(fig, "funnel_analysis.png")
        print(f"  [OK] {path.name}")
        return {"funnel_analysis.png": path}
