# -*- coding: utf-8 -*-
"""
Table Relationship Analyzer - 数据表关系分析
分析五表关联、稀疏度、重叠率
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.eda.base import BaseAnalyzer


class TableRelationshipAnalyzer(BaseAnalyzer):
    """数据表关系分析"""
    
    def __init__(self, data):
        super().__init__(data)
        self.relationships = {}
    
    def analyze(self) -> Dict[str, Any]:
        print("\n[4/13] Table Relationship Analysis...")
        
        df_user = self.get_df("user_features")
        df_item = self.get_df("item_features")
        df_inter = self.get_df("rec_inter")
        df_src = self.get_df("src_inter")
        
        # 计算关系
        all_users = set(df_user["user_id"].unique()) if len(df_user) > 0 else set()
        all_items = set(df_item["item_id"].unique()) if len(df_item) > 0 else set()
        users_in_inter = set(df_inter["user_id"].unique()) if len(df_inter) > 0 else set()
        items_in_inter = set(df_inter["item_id"].unique()) if len(df_inter) > 0 else set()
        users_in_src = set(df_src["user_id"].unique()) if len(df_src) > 0 else set()
        items_in_src = set(df_src["item_id"].unique()) if "item_id" in df_src.columns and len(df_src) > 0 else set()
        
        self.relationships = {
            "all_users": all_users, "all_items": all_items,
            "users_in_inter": users_in_inter, "items_in_inter": items_in_inter,
            "users_in_src": users_in_src, "items_in_src": items_in_src,
        }
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        plt.suptitle("数据表关系分析", fontsize=16, fontweight='bold')
        
        # 1. 五表数据规模对比
        ax = axes[0, 0]
        tables = ['user', 'item', 'rec_inter', 'src_inter']
        counts = [len(df_user), len(df_item), len(df_inter), len(df_src)]
        ax.bar(tables, counts, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
        ax.set_ylabel("记录数")
        ax.set_title("五表数据规模对比")
        ax.set_yscale('log')
        for i, c in enumerate(counts):
            ax.text(i, c, f'{c/1e6:.1f}M', ha='center', va='bottom')
        
        # 2. 用户覆盖率
        ax = axes[0, 1]
        coverage = {
            'rec_inter': len(users_in_inter & all_users) / len(users_in_inter) * 100 if users_in_inter else 0,
            'src_inter': len(users_in_src & all_users) / len(users_in_src) * 100 if users_in_src else 0,
        }
        bars = ax.bar(coverage.keys(), coverage.values(), color=['#2ecc71', '#3498db'])
        ax.set_ylabel("覆盖率 (%)")
        ax.set_title("用户覆盖率")
        ax.set_ylim(0, 110)
        for bar, val in zip(bars, coverage.values()):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{val:.1f}%', ha='center')
        
        # 3. 物品覆盖率
        ax = axes[0, 2]
        item_coverage = {
            'rec_inter': len(items_in_inter & all_items) / len(items_in_inter) * 100 if items_in_inter else 0,
            'src_inter': len(items_in_src & all_items) / len(items_in_src) * 100 if items_in_src else 0,
        }
        bars = ax.bar(item_coverage.keys(), item_coverage.values(), color=['#2ecc71', '#3498db'])
        ax.set_ylabel("覆盖率 (%)")
        ax.set_title("物品覆盖率")
        ax.set_ylim(0, 110)
        for bar, val in zip(bars, item_coverage.values()):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f'{val:.1f}%', ha='center')
        
        # 4. 交互矩阵稀疏度
        ax = axes[1, 0]
        if users_in_inter and items_in_inter:
            total = len(users_in_inter) * len(items_in_inter)
            sparsity = (1 - len(df_inter) / total) * 100 if total > 0 else 0
            density = (len(df_inter) / total) * 100 if total > 0 else 0
            bars = ax.bar(['稀疏度', '密度'], [sparsity, density],
                         color=[self.colors['danger'], self.colors['success']])
            ax.set_ylabel("百分比 (%)")
            ax.set_title(f"交互矩阵稀疏度\n用户:{len(users_in_inter):,} x 物品:{len(items_in_inter):,}")
            for bar, val in zip(bars, [sparsity, density]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.4f}%', ha='center')
        
        # 5. 用户重叠分析
        ax = axes[1, 1]
        cats = ['rec_inter', 'src_inter']
        sets = [users_in_inter, users_in_src]
        in_user = [len(s & all_users) for s in sets]
        not_in = [len(s - all_users) for s in sets]
        x = np.arange(2)
        ax.bar(x, in_user, 0.5, label='在user中', color='#3498db')
        ax.bar(x, not_in, 0.5, bottom=in_user, label='不在user中', color='#e74c3c')
        ax.set_xticks(x)
        ax.set_xticklabels(cats)
        ax.set_ylabel("用户数量")
        ax.set_title("用户重叠分析")
        ax.legend()
        
        # 6. 数据流向图
        ax = axes[1, 2]
        ax.axis('off')
        ax.set_title("数据流向关系图")
        ax.text(0.15, 0.85, f'user\n{len(df_user):,}', transform=ax.transAxes, ha='center',
               fontsize=10, bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.8), color='white')
        ax.text(0.15, 0.55, f'item\n{len(df_item):,}', transform=ax.transAxes, ha='center',
               fontsize=10, bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.8), color='white')
        ax.text(0.5, 0.55, f'rec_inter\n{len(df_inter):,}', transform=ax.transAxes, ha='center',
               fontsize=10, bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.8), color='white')
        ax.text(0.85, 0.55, f'src_inter\n{len(df_src):,}', transform=ax.transAxes, ha='center',
               fontsize=10, bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.8), color='white')
        ax.annotate('', xy=(0.45, 0.55), xytext=(0.22, 0.75), arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
        ax.annotate('', xy=(0.45, 0.55), xytext=(0.22, 0.45), arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
        ax.annotate('', xy=(0.75, 0.65), xytext=(0.55, 0.6), arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
        ax.annotate('', xy=(0.75, 0.45), xytext=(0.55, 0.5), arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
        
        plt.tight_layout()
        path = self.save_fig(fig, "table_relationship.png")
        print(f"  [OK] {path.name}")
        return {"table_relationship.png": path}
    
    def get_relationships(self) -> Dict[str, Any]:
        return self.relationships
