# -*- coding: utf-8 -*-
"""
Base Classes - 基类和公共组件
"""

import abc
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配置路径
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.eda.config import OUTPUT_DIR


def clean_text(text):
    """清理文本中的特殊Unicode字符"""
    if pd.isna(text):
        return text
    text = str(text)
    text = re.sub(r'[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\s.,!?;:：；、，。（）【】《》\-_()（）]', '', text)
    return text.strip()


def clean_series(series):
    """清理Series或Index中的特殊字符"""
    if hasattr(series, 'map'):
        return series.map(lambda x: clean_text(x) if pd.notna(x) else x)
    return series


class BaseAnalyzer(abc.ABC):
    """分析器基类"""
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.data = data
        self.dpi = 150
        self.colors = {
            'primary': '#3498db',
            'success': '#2ecc71',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'purple': '#9b59b6',
        }
    
    @abc.abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """执行分析"""
        pass
    
    def get_df(self, key: str) -> pd.DataFrame:
        return self.data.get(key, pd.DataFrame())
    
    def save_fig(self, fig: plt.Figure, filename: str) -> Path:
        path = OUTPUT_DIR / filename
        fig.savefig(path, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        return path


class DataLoader:
    """数据加载器"""
    
    _instance = None
    _data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, force: bool = False) -> Dict[str, pd.DataFrame]:
        if self._data is not None and not force:
            return self._data
        
        from src.eda.config import DATA_DIR
        
        files = {
            "user_features": "user_features_clean.parquet",
            "item_features": "item_features_clean.parquet",
            "rec_inter": "rec_inter_clean.parquet",
            "social_network": "social_network_clean.parquet",
            "src_inter": "src_inter_clean.parquet",
        }
        
        self._data = {}
        for key, filename in files.items():
            filepath = DATA_DIR / filename
            if filepath.exists():
                self._data[key] = pd.read_parquet(filepath)
                print(f"  [OK] {key}: {len(self._data[key]):,} rows")
            else:
                self._data[key] = pd.DataFrame()
                print(f"  [FAIL] {key}: not found")
        
        return self._data
