# -*- coding: utf-8 -*-
"""
Retention Analyzer - 留存分析
分析用户留存率
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class RetentionAnalyzer(BaseAnalyzer):
    """留存分析"""
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[11/13] Retention Analysis...")
        
        df_inter = self.get_df("rec_inter")
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        plt.suptitle("用户留存分析", fontsize=16, fontweight='bold')
        
        if len(df_inter) > 0 and "time" in df_inter.columns:
            df = df_inter.copy()
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
            df['date'] = df['time'].dt.date
            
            daily_users = df.groupby('date')['user_id'].apply(set).sort_index()
            dates = list(daily_users.index)
            
            if len(dates) >= 7:
                retention_rates = {'次日': [], '3日': [], '7日': []}
                
                for i in range(min(30, len(dates) - 7)):
                    base_users = daily_users.iloc[i]
                    next_day = daily_users.iloc[i + 1] if i + 1 < len(dates) else set()
                    day3 = daily_users.iloc[i + 3] if i + 3 < len(dates) else set()
                    day7 = daily_users.iloc[i + 7] if i + 7 < len(dates) else set()
                    
                    retention_rates['次日'].append(len(base_users & next_day) / len(base_users) * 100 if base_users else 0)
                    retention_rates['3日'].append(len(base_users & day3) / len(base_users) * 100 if base_users else 0)
                    retention_rates['7日'].append(len(base_users & day7) / len(base_users) * 100 if base_users else 0)
                
                # 1. 留存曲线
                ax = axes[0, 0]
                x = range(len(retention_rates['次日']))
                ax.plot(x, retention_rates['次日'], label='次日留存', color='#3498db', linewidth=2)
                ax.plot(x, retention_rates['3日'], label='3日留存', color='#2ecc71', linewidth=2)
                ax.plot(x, retention_rates['7日'], label='7日留存', color='#e74c3c', linewidth=2)
                ax.set_xlabel("用户批次")
                ax.set_ylabel("留存率 (%)")
                ax.set_title("用户留存曲线")
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # 2. 平均留存率
                ax = axes[0, 1]
                avg_retention = {
                    '次日': np.mean(retention_rates['次日']),
                    '3日': np.mean(retention_rates['3日']),
                    '7日': np.mean(retention_rates['7日'])
                }
                bars = ax.bar(avg_retention.keys(), avg_retention.values(),
                             color=['#3498db', '#2ecc71', '#e74c3c'], edgecolor='white')
                ax.set_ylabel("留存率 (%)")
                ax.set_title("平均留存率")
                for bar, val in zip(bars, avg_retention.values()):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                           f'{val:.2f}%', ha='center')
                
                # 3. 每日活跃用户
                ax = axes[0, 2]
                daily_count = daily_users.apply(len)
                ax.bar(range(len(daily_count)), daily_count.values, color=self.colors['primary'], edgecolor='white', alpha=0.7)
                ax.set_xlabel("天数")
                ax.set_ylabel("用户数")
                ax.set_title("每日活跃用户数")
                
                # 4. 用户生命周期
                ax = axes[1, 0]
                user_lifespan = df.groupby('user_id')['date'].agg(['min', 'max', 'count'])
                user_lifespan['min'] = pd.to_datetime(user_lifespan['min'])
                user_lifespan['max'] = pd.to_datetime(user_lifespan['max'])
                user_lifespan['days'] = (user_lifespan['max'] - user_lifespan['min']).dt.days + 1
                ax.hist(user_lifespan['days'].clip(0, 30), bins=30, color=self.colors['purple'], edgecolor='white', alpha=0.7)
                ax.set_xlabel("活跃天数")
                ax.set_ylabel("用户数量")
                ax.set_title(f"用户生命周期分布\n(中位数: {user_lifespan['days'].median():.0f}天)")
                
                # 5. 留存率分布
                ax = axes[1, 1]
                ax.hist(retention_rates['次日'], bins=20, alpha=0.5, label='次日', color='#3498db')
                ax.hist(retention_rates['3日'], bins=20, alpha=0.5, label='3日', color='#2ecc71')
                ax.hist(retention_rates['7日'], bins=20, alpha=0.5, label='7日', color='#e74c3c')
                ax.set_xlabel("留存率 (%)")
                ax.set_ylabel("批次数量")
                ax.set_title("留存率分布")
                ax.legend()
                
                # 6. 留存率统计
                ax = axes[1, 2]
                stats_data = {
                    '次日-均值': np.mean(retention_rates['次日']),
                    '次日-标准差': np.std(retention_rates['次日']),
                    '7日-均值': np.mean(retention_rates['7日']),
                    '7日-标准差': np.std(retention_rates['7日']),
                }
                bars = ax.bar(stats_data.keys(), stats_data.values(), 
                             color=['#3498db', '#3498db', '#e74c3c', '#e74c3c'],
                             edgecolor='white')
                ax.set_ylabel("留存率 (%)")
                ax.set_title("留存率统计")
                ax.tick_params(axis='x', rotation=45)
        else:
            for ax in axes.flat:
                ax.text(0.5, 0.5, '数据不足', ha='center', va='center', fontsize=14)
                ax.axis('off')
        
        plt.tight_layout()
        path = self.save_fig(fig, "retention_analysis.png")
        print(f"  [OK] {path.name}")
        return {"retention_analysis.png": path}
