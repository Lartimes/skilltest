# -*- coding: utf-8 -*-
"""
Temporal Analyzer - 时序分析
分析按小时/星期分布、观看完成度、趋势
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class TemporalAnalyzer(BaseAnalyzer):
    """时序分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[6/13] Temporal Analysis...")
        
        df = self.get_df("rec_inter").copy()
        
        if "time" in df.columns:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
            df['hour'] = df['time'].dt.hour
            df['weekday'] = df['time'].dt.dayofweek
            df['date'] = df['time'].dt.date
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        plt.suptitle("时序模式分析", fontsize=16, fontweight='bold')
        
        # 1. 按小时分布
        ax = axes[0, 0]
        if 'hour' in df.columns:
            counts = df['hour'].value_counts().sort_index()
            ax.bar(counts.index, counts.values, color=self.colors['primary'], edgecolor='white', alpha=0.8)
            ax.set_xlabel("小时 (0-23)")
            ax.set_ylabel("交互次数")
            ax.set_title("用户活跃度按小时分布")
            ax.axhline(counts.mean(), color='red', linestyle='--', label="平均值")
            ax.legend()
        
        # 2. 按星期分布
        ax = axes[0, 1]
        if 'weekday' in df.columns:
            names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            counts = df['weekday'].value_counts().sort_index()
            ax.bar(range(7), counts.values, color=self.colors['danger'], edgecolor='white', alpha=0.8)
            ax.set_xticks(range(7))
            ax.set_xticklabels(names)
            ax.set_xlabel("星期")
            ax.set_ylabel("交互次数")
            ax.set_title("用户活跃度按星期分布")
            ax.axhline(counts.mean(), color='red', linestyle='--', label="平均值")
            ax.legend()
        
        # 3. 观看完成度分布
        ax = axes[0, 2]
        if "duration_ms" in df.columns and "playing_time" in df.columns:
            df['watch_ratio'] = df['playing_time'] / (df['duration_ms'] + 1)
            ratios = df['watch_ratio'].clip(0, 5)
            ax.hist(ratios, bins=50, color=self.colors['success'], edgecolor='white', alpha=0.7)
            ax.set_xlabel("观看比率 (播放时长/视频时长)")
            ax.set_ylabel("次数")
            ax.set_title(f"观看完成度分布\n(中位数: {ratios.median():.2f})")
            ax.axvline(ratios.median(), color='red', linestyle='--')
        
        # 4. 每日趋势
        ax = axes[1, 0]
        if 'date' in df.columns:
            daily = df.groupby('date').size()
            if len(daily) > 30:
                daily = daily.iloc[::max(1, len(daily)//30)]
            ax.plot(range(len(daily)), daily.values, color=self.colors['purple'], alpha=0.7, linewidth=1.5)
            ax.fill_between(range(len(daily)), daily.values, alpha=0.3, color=self.colors['purple'])
            ax.set_xlabel("日期序号")
            ax.set_ylabel("交互次数")
            ax.set_title("每日交互趋势")
        
        # 5. 峰值时段分析
        ax = axes[1, 1]
        if 'hour' in df.columns:
            hour_counts = df['hour'].value_counts().sort_index()
            peak_hours = hour_counts.nlargest(3).index.tolist()
            low_hours = hour_counts.nsmallest(3).index.tolist()
            peak_data = {
                '高峰时段': hour_counts[peak_hours].sum(),
                '低谷时段': hour_counts[low_hours].sum(),
                '其他时段': hour_counts.sum() - hour_counts[peak_hours].sum() - hour_counts[low_hours].sum()
            }
            ax.bar(peak_data.keys(), peak_data.values(), color=['#e74c3c', '#3498db', '#2ecc71'], edgecolor='white')
            ax.set_ylabel("交互次数")
            ax.set_title(f"时段分析\n(高峰: {peak_hours}, 低谷: {low_hours})")
        
        # 6. 周末vs工作日
        ax = axes[1, 2]
        if 'weekday' in df.columns:
            weekday_counts = df[df['weekday'] < 5]['hour'].value_counts().sort_index()
            weekend_counts = df[df['weekday'] >= 5]['hour'].value_counts().sort_index()
            ax.plot(weekday_counts.index, weekday_counts.values, label='工作日', color='#3498db', linewidth=2)
            ax.plot(weekend_counts.index, weekend_counts.values, label='周末', color='#e74c3c', linewidth=2)
            ax.set_xlabel("小时")
            ax.set_ylabel("交互次数")
            ax.set_title("工作日vs周末活跃对比")
            ax.legend()
        
        plt.tight_layout()
        path = self.save_fig(fig, "temporal_analysis.png")
        print(f"  [OK] {path.name}")
        return {"temporal_analysis.png": path}
