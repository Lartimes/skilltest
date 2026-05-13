# -*- coding: utf-8 -*-
"""
Run EDA - EDA分析入口
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any

from src.eda.base import DataLoader
from src.eda import ANALYZERS


class EDAAnalyzer:
    """EDA分析器协调器"""
    
    def __init__(self):
        self.data = None
        self.results = {}
        self.analyzers = {}
    
    def load_data(self) -> 'EDAAnalyzer':
        print("=" * 60)
        print("快手推荐系统 - EDA探索性数据分析")
        print("=" * 60)
        print("\n[Loading] Loading data...")
        loader = DataLoader()
        self.data = loader.load()
        return self
    
    def run_all(self) -> Dict[str, Any]:
        if self.data is None:
            self.load_data()
        
        print("\n" + "=" * 60)
        print("Running Analysis")
        print("=" * 60)
        
        for i, (name, cls) in enumerate(ANALYZERS.items(), 1):
            analyzer = cls(self.data)
            result = analyzer.analyze()
            self.results[name] = result
            self.analyzers[name] = analyzer
        
        self._print_summary()
        return self.results
    
    def run(self, names: list) -> Dict[str, Any]:
        if self.data is None:
            self.load_data()
        for name in names:
            if name in ANALYZERS:
                analyzer = ANALYZERS[name](self.data)
                result = analyzer.analyze()
                self.results[name] = result
                self.analyzers[name] = analyzer
        return self.results
    
    def _print_summary(self):
        from src.eda.config import OUTPUT_DIR
        print("\n" + "=" * 60)
        print("EDA Analysis Complete!")
        print("=" * 60)
        print("\nGenerated files:")
        for name, result in self.results.items():
            if isinstance(result, dict):
                for filename in result.keys():
                    print(f"  [OK] {filename}")
        print(f"\nOutput directory: {OUTPUT_DIR}")
        print("=" * 60)


def run_eda():
    """便捷函数"""
    EDAAnalyzer().run_all()


if __name__ == "__main__":
    run_eda()
