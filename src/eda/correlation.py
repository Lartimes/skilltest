# -*- coding: utf-8 -*-
"""
Correlation Analyzer - 相关性分析
分析交互行为相关性热力图
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class CorrelationAnalyzer(BaseAnalyzer):
    """相关性分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[8/13] Correlation Analysis...")
        
        df_inter = self.get_df("rec_inter")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        plt.suptitle("交互行为相关性分析", fontsize=16, fontweight='bold')
        
        cols = ["forward", "like", "follow", "click", "playing_time"]
        labels_cn = {"forward": "转发", "like": "点赞", "follow": "关注", "click": "点击", "playing_time": "播放时长"}
        available = [c for c in cols if c in df_inter.columns]
        
        # 1. 相关性热力图
        ax = axes[0, 0]
        if len(available) >= 2:
            corr = df_inter[available].corr()
            corr.columns = [labels_cn.get(c, c) for c in corr.columns]
            corr.index = [labels_cn.get(c, c) for c in corr.index]
            sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlBu_r',
                       center=0, ax=ax, square=True, linewidths=0.5)
            ax.set_title("交互行为相关性热力图")
        
        # 2. 观看完成度分布
        ax = axes[0, 1]
        if "duration_ms" in df_inter.columns and "playing_time" in df_inter.columns:
            df = df_inter.copy()
            df['watch_ratio'] = df['playing_time'] / (df['duration_ms'] + 1)
            ratios = df['watch_ratio'].clip(0, 3)
            ax.hist(ratios, bins=50, color=self.colors['primary'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("观看比率")
            ax.set_ylabel("次数")
            ax.set_title(f"观看完成度分布\n(中位数: {ratios.median():.2f})")
            ax.axvline(ratios.median(), color='red', linestyle='--')
        
        # 3. 行为共现矩阵
        ax = axes[1, 0]
        action_cols = ["forward", "like", "follow", "click"]
        available_actions = [c for c in action_cols if c in df_inter.columns]
        if len(available_actions) >= 2:
            cooccur = df_inter[available_actions].astype(bool).T.dot(df_inter[available_actions].astype(bool))
            cooccur.columns = [labels_cn.get(c, c) for c in cooccur.columns]
            cooccur.index = [labels_cn.get(c, c) for c in cooccur.index]
            sns.heatmap(cooccur, annot=True, fmt='.0f', cmap='Blues',
                       ax=ax, square=True, linewidths=0.5)
            ax.set_title("行为共现次数")
        
        # 4. 播放时长分布
        ax = axes[1, 1]
        if "playing_time" in df_inter.columns:
            times = df_inter['playing_time'].dropna()
            times_ms = times / 1000  # 转换为秒
            ax.hist(times_ms.clip(0, 300), bins=50, color=self.colors['success'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("播放时长 (秒)")
            ax.set_ylabel("次数")
            ax.set_title(f"播放时长分布\n(中位数: {times_ms.median():.0f}秒)")
            ax.axvline(times_ms.median(), color='red', linestyle='--')
        
        plt.tight_layout()
        path = self.save_fig(fig, "correlation.png")
        print(f"  [OK] {path.name}")
        return {"correlation.png": path}
