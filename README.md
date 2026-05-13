# 短视频推荐系统

> 基于 KuaiRec 数据集的混合推荐算法研究与实现

## 项目概述

本项目针对短视频平台用户行为数据，研究并实现了多种推荐算法，包括协同过滤、内容推荐和混合推荐，旨在提升短视频内容推荐的精准度。

### 毕设需求

- 分析短视频平台用户观看时长、点赞、评论、分享等行为数据
- 挖掘用户内容偏好（如题材、风格、时长）
- 构建多维度用户画像
- 设计基于内容或协同过滤的推荐算法
- 对比不同算法的推荐效果

## 数据集

使用 KuaiRec 公开数据集，包含：

| 文件                   | 大小      | 说明        |
| -------------------- | ------- | --------- |
| `rec_inter.csv`      | 541 MB  | 用户-视频交互数据 |
| `item_features.csv`  | 1.18 GB | 视频特征数据    |
| `user_features.csv`  | 0.33 MB | 用户特征数据    |
| `social_network.csv` | 0.01 MB | 社交网络数据    |

## 项目结构

```
backend/
├── src/                    # 源代码
│   ├── config.py          # 配置管理（Pydantic）
│   └── data_loader.py     # 数据加载模块
├── notebooks/             # Jupyter notebooks
│   └── 01_data_cleaning.ipynb
├── config.yaml            # YAML 配置文件
├── requirements.txt       # 依赖清单
├── README.md             # 项目说明
├── README_项目报告_中文.md # 参考项目报告（中文翻译）
└── data/                  # 数据目录
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 数据加载

```python
from src.data_loader import load_data

# 开发模式（快速采样）
data = load_data(mode="dev")

# 生产模式（用户采样）
data = load_data(mode="prod")

# 全量模式（流式处理）
stats = load_data(mode="full")
```

### 3. 运行 Notebook

```bash
cd notebooks
jupyter notebook
# 打开 01_data_cleaning.ipynb
```

## 技术栈

- **数据处理**：pandas, numpy
- **数据验证**：pydantic
- **推荐算法**：LightFM, scikit-learn
- **可视化**：matplotlib, seaborn, plotly
- **进度追踪**：tqdm

## 核心模块

### 数据加载器特性

| 特性     | 说明                |
| ------ | ----------------- |
| 三模式加载  | dev / prod / full |
| 流式处理   | 支持大文件分块读取         |
| 数据质量检查 | 缺失值、重复值、异常值检测     |
| 自动缓存   | pickle 缓存 + 磁盘持久化 |
| 进度追踪   | tqdm 实时进度条        |
| 日志系统   | 生产级日志             |

### 待实现模块

- [ ] 用户画像构建
- [ ] 协同过滤算法
- [ ] 内容推荐算法
- [ ] LightFM 混合推荐
- [ ] 算法评估对比

## 参考项目

本项目参考了以下优秀项目：

- [KuaiRec 官方数据](https://github.com/LeoN1203/FinalProject_2025_LeonAYRAL.git)
- [Kuairec Hybrid Recommender System](learning/Kuairec_Hybrid_recommender_system-master/)

详见 `README_项目报告_中文.md`。

## License

MIT License

```commandline
┌──────────────────────────────────────────────────────────────────┐
│                        Production Pipeline                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │   Config    │───▶│   Data      │───▶│  Features   │           │
│  │   Center    │    │   Pipeline  │    │  Pipeline   │           │
│  │  (YAML)     │    │  (清洗+监控) │    │ (用户+物品+文本)│        │
│  └─────────────┘    └─────────────┘    └─────────────┘           │
│         │               │                   │                   │
│         ▼               ▼                   ▼                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │   Model     │◀───│  Dataset     │◀───│   Feature   │           │
│  │  Trainer    │    │  Builder    │    │   Store     │           │
│  │(LightFM+Optuna)│  │ (稀疏矩阵)   │    │  (缓存)      │          │
│  └─────────────┘    └─────────────┘    └─────────────┘           │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │  Evaluation │    │Recommendation│   │   API       │           │
│  │  (多K指标)  │    │  Generator   │───▶│  Service    │           │
│  │  + 报告     │    │ (召回+精排)  │    │  (Flask/gRPC)│          │
│  └─────────────┘    └─────────────┘    └─────────────┘           │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                        支撑系统                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Logging  │  │ Metrics  │  │ Alerting │  │ Cache    │         │
│  │ (结构化) │  │ (Prom)   │  │ (SLO)    │  │ (多级)   │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└──────────────────────────────────────────────────────────────────┘

```

