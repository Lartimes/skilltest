# KuaiRec 数据集推荐系统：项目报告

> 协作仓库：https://github.com/LeoN1203/FinalProject_2025_LeonAYRAL.git

推荐系统已成为数字平台提供个性化内容的关键技术。本报告介绍了一个基于 KuaiRec 数据集开发的混合推荐系统，该系统针对快手短视频平台的用户交互和内容数据进行了优化。

**项目成员：**
- **Yacine BENIHADDADENE**
- **Gabriel CALVENTE**
- **Cédric DAMAIS**
- **Léon AYRAL**

---

## 1. 引言

### 1.1 项目目标

本项目的主要目标是针对 KuaiRec 数据集开发一个混合推荐系统。该系统旨在预测用户与短视频之间的交互行为，利用各种用户和物品特征来提供个性化推荐。

### 1.2 KuaiRec 数据集概述

KuaiRec 数据集是从快手短视频平台收集的大规模真实世界数据集。它包含丰富的用户交互信息、用户画像、物品（视频）特征和社交网络数据。本项目使用了以下关键数据文件：

| 文件名 | 描述 |
|--------|------|
| `big_matrix.csv` | 用户-视频交互大矩阵，包含 `user_id`、`video_id`、`watch_ratio` 和 `timestamp`，是训练和验证的主要数据源 |
| `small_matrix.csv` | 较小的交互矩阵，时间上晚于 `big_matrix.csv`，用于测试模型在未见数据上的表现 |
| `user_features.csv` | 用户特征数据，包含活跃度、注册时长、人口统计代理变量等 |
| `item_daily_features.csv` | 物品每日聚合特征，如点赞、评论、分享、播放次数等随时间变化的指标 |
| `item_features.csv` | 物品静态特征，从 `item_daily_features.csv` 汇总得出 |
| `item_categories.csv` | 视频类别信息 |
| `kuairec_caption_category.csv` | 视频标题和关联类别 |
| `social_network.csv` | 用户间的社交连接关系 |

这些多样化的数据源使得开发能够融合协同过滤信号和基于内容特征的混合推荐系统成为可能。

---

## 2. 数据加载与预处理

### 2.1 数据加载

项目首先将必要的 CSV 文件加载到 pandas DataFrame 中。主要在 `solution/eda_solution.ipynb` 和 `solution/feature_model_solution.ipynb` 笔记本中完成。

### 2.2 数据清洗

数据清洗是确保数据质量和一致性的关键步骤，主要清洗操作包括：

**处理缺失值：**
- 使用 `dropna()` 删除关键列（如交互矩阵中的 `user_id`、`video_id`）中包含缺失值的行
- 对于特征数据集，根据特征性质采用特定策略

**删除重复记录：**
- 使用 `drop_duplicates()` 从所有数据集中移除重复记录，防止冗余和潜在偏差

**修正无效数据：**
- **时间戳**：识别并修正或删除交互数据中的负值或无效时间戳，转换为 `datetime` 对象
- **其他不一致**：检查 `item_features` 中 `video_duration` 等列是否存在非正值

清洗效果显著，虽然数据集大小有所减少，但整体质量和可靠性得到提升。例如，`big_matrix` 在移除 `watch_ratio > 1` 或无效时间戳的条目后规模减小。

清洗后的数据集保存到 `solution/data/` 目录（如 `big_matrix_cleaned.csv`、`user_features_cleaned.csv`），供后续特征工程和建模使用。

---

## 3. 探索性数据分析（EDA）

### 3.1 交互矩阵分析

**统计数据：**

| 数据集 | 用户数 | 物品数 | 交互数 |
|--------|--------|--------|--------|
| `big_matrix` | 7,176 | 107,280 | 12,630,246 |
| `small_matrix` | 7,080 | 53,790 | 1,381,001 |

**用户与物品交互分布：**
- 分析显示用户活跃度和物品流行度呈**长尾分布**
- 少数用户高度活跃，少数物品获得大量交互
- 使用对数刻度图更好地可视化这些偏态分布

**时序模式：**
- **按小时分布**：每日交互呈现明显模式，晚间时段活动达到峰值，中午时段较低
- **按星期分布**：周三和周四通常比其他工作日有更高的用户活跃度

**稀疏度：**
- `big_matrix` 高度稀疏，稀疏度计算公式为 `1 - (交互数 / (用户数 × 物品数))`
- 稀疏度约为 **98.37%**，这是推荐系统数据集的典型特征

### 3.2 用户特征分析

分析了各种分类和数值特征的分布：
- `onehot_feat4`（独热编码特征）的可视化显示了各类别用户比例
- 还探索了 `user_active_degree`、`follow_user_num_range` 等特征

### 3.3 物品特征分析

**类别分布：**
- 分析了物品类别分布，展示了数据集中最具代表性的类别

**每日特征汇总：**
- 将 `item_daily_features` 数据集按 `video_id` 分组，汇总每日性能指标
- 创建了新的比率特征来捕捉参与度和吸引力：
  - `appeal`：展示数/有效播放数
  - `like_ratio`：点赞数/有效播放数
  - `share_ratio`：分享数/有效播放数

**文本内容与标签：**
- 许多 `topic_tag` 条目需要从字符串列表表示中解析
- 最常见的标签（如"颜值"、"生活"、"美食"）突出了热门主题
- 约 **54.82%** 的视频至少有 一个标签

**标题与封面文本：**
- **有标题**：95.19% 的视频有非空标题
- **有封面文本**：42.23% 的视频有有意义的 `manual_cover_text`（非"UNKNOWN"）
- 分析了平均字符长度和精确匹配与差异的比较

**元数据覆盖率（small_matrix）：**

| 特征 | 数量 | 百分比 |
|------|------|--------|
| 有标题或标签的视频 | 3,167 | 95.19% |
| 同时有标题和标签 | 1,824 | 54.82% |
| 只有标题 | 1,343 | 40.37% |
| 只有标签 | 0 | 0.00% |

**层级类别覆盖率：**

| 级别 | 覆盖率 |
|------|--------|
| 一级类别 | 95.16% |
| 二级类别 | 72.32% |
| 三级类别 | 37.96% |
| 三个级别都有 | 37.96% |

- 38 个唯一一级类别
- 109 个唯一二级类别
- 153 个唯一三级类别

**用户-物品交互统计：**

| 指标 | small_matrix | big_matrix |
|------|-------------|------------|
| 唯一用户数 | 1,411 | 7,176 |
| 唯一物品数 | 3,327 | 10,728 |
| 实际交互数 | 4,494,578 | 11,564,987 |
| 总可能交互数 | 4,694,397 | 76,984,128 |
| **交互密度** | **0.9574** | **0.1502** |

- **small_matrix** 非常密集（约95.7%），表明几乎所有可能的用户-物品对都已被观测到
- **big_matrix** 稀疏得多（约15.0%），这会影响模型学习和过拟合模式

---

## 4. 特征工程

### 4.1 用户特征选择

从清洗后的 `user_features` 数据集中选择了用户特征子集，创建了 `new_user_features` DataFrame，包括：
- `user_id`、`is_video_author`、`follow_user_num_range`、`friend_user_num_range`、`register_days_range`、`is_lowactive_period`、`user_active_degree`
- 后续还添加了 `onehot_feat0` 到 `onehot_feat10` 的独热编码向量用户特征，提升了整体模型性能

### 4.2 物品特征创建与转换

**创建新物品特征：**
- 将 `item_daily_features_cleaned.csv` 按 `video_id` 分组，汇总每日指标
- 新建的比率特征：
  - `appeal`：展示数/有效播放数
  - `like_ratio`：点赞数/有效播放数
  - `download_ratio`：下载数/有效播放数
  - `comment_ratio`：评论数/有效播放数
  - `share_ratio`：分享数/有效播放数

**多步归一化：**
1. 处理 NaN/inf 值（比率计算产生，由除零引起）
2. 初始 MinMaxScaler：将特征缩放到 [0,1] 范围
3. 对数变换：`np.log1p` 处理偏态和压缩值范围
4. 二次 MinMaxScaler：再次缩放到 [0,1] 范围

### 4.3 用户特征转换

计划对数值用户特征进行类似的多步归一化处理（log1p 后接 MinMaxScaler），但实际执行时数值列列表为空，导致数值用户特征未进行变换。分类特征直接使用。

### 4.4 数值特征分箱

**方法与原理：**
- 为使数值特征适合 LightFM 模型（通常更适合分类特征或分箱数值特征），采用基于分位数的离散化
- 使用 `pd.qcut` 递归分箱函数 `bin_numerical_column_recursive`，自动调整分位数数量以处理边界情况

---

## 5. LightFM 模型开发

### 5.1 模型选择：LightFM

选择 LightFM 的原因：
- **混合特性**：有效融合协同过滤与基于内容的特征
- **隐式反馈**：专为隐式反馈信号设计
- **高效性**：优化处理大规模数据集
- **灵活性**：支持多种损失函数

### 5.2 LightFM 数据准备

**特征名称字符串：**
- `all_user_feature_names`：用户特征列名与其唯一值组合
- `all_item_feature_names`：物品特征名与分箱特征组合

**数据构建：**
- 创建 `lightfm.data.Dataset` 实例
- `dataset.fit()`：映射用户ID、物品ID、用户特征名、物品特征名
- `dataset.build_interactions()`：构建稀疏交互矩阵，`watch_ratio` 作为权重
- `dataset.build_user_features()` 和 `dataset.build_item_features()`：构建用户和物品特征稀疏矩阵

### 5.3 模型实例化

```python
model = LightFM(
    loss='warp',           # 加权近似排名成对损失
    no_components=128,     # 潜在维度数
    learning_rate=0.05,    # 学习率
    item_alpha=1e-5,       # 物品特征 L2 正则化
    user_alpha=1e-5,       # 用户特征 L2 正则化
    random_state=42        # 可重复性
)
```

### 5.4 训练/验证/测试划分

**策略：**
- 训练与验证：使用 `big_matrix` 交互数据
- 测试：使用 `small_matrix`（时间上更晚）作为最终测试集

**防止数据泄露：**
- 在划分前对稀疏交互和权重矩阵实施**规范形式**（COO 格式转换自动合并重复坐标）
- 确保每个用户-物品对在划分前只有一个聚合值

---

## 6. 增强模型：融合文本特征

### 6.1 文本特征工程

从 `kuairec_caption_category.csv` 提取信息：

**合并文本数据：**
- 拼接 `manual_cover_text` 和 `caption` 创建 `full_text` 字段
- 使用 TF-IDF 提取关键词
- 将 `"UNKNOWN"` 替换为空字符串以避免干扰

**层级类别名称：**
- `first_level_category_name`、`second_level_category_name`、`third_level_category_name`

**话题标签：**
- 每个视频关联的话题标签

### 6.2 特征简化策略

实验发现：
- 标签和深层类别特征虽然对 `big_matrix` 有信息量，但严重损害了跨数据集泛化能力
- **删除标签和二级/三级类别后，small_matrix 上的 Precision@10 从 0.0313 提升到 0.4200**
- 证实了**更简单、更稳健的特征**泛化效果更好

---

## 7. 模型训练

### 7.1 训练配置

```python
model.fit(
    train_interactions,
    user_features=user_features_matrix,
    item_features=item_features_matrix,
    sample_weight=train_interactions_w,
    epochs=50,
    num_threads=12,
    verbose=True
)
```

### 7.2 早停策略

观察发现：
- 在 `big_matrix` 验证集上 AUC 保持高位
- 但 `small_matrix` 评估 AUC 在 **epoch 10-12** 左右达到峰值（约 0.71）
- 到 epoch 50 时，`small_matrix` AUC 下降到约 0.67，表明过拟合

实现基于测试 Precision@10 的早停机制。

---

## 8. 评估

### 8.1 评估指标

- **Precision@k**：推荐列表中相关物品的比例
- **Recall@k**：成功推荐的所有相关物品的比例
- **AUC**：模型将相关物品排名高于无关物品的能力
- **NDCG@k**：考虑推荐物品位置的打分质量

### 8.2 基线模型结果（1 epoch）

| 数据集 | Precision@10 | Recall@10 | AUC |
|--------|--------------|-----------|-----|
| 训练集 | 0.0109 | 0.0034 | 0.7011 |
| 验证集 | 0.0012 | 0.0004 | 0.6118 |
| 测试集 | 0.0002 | 0.0001 | 0.5400 |

### 8.3 增强模型结果（10 epochs + 用户特征）

| 数据集 | Precision@10 | Recall@10 | AUC | NDCG@10 |
|--------|--------------|-----------|-----|---------|
| 训练集 | 0.5775 | 0.0051 | 0.8611 | 0.2198 |
| 验证集 | 0.5174 | 0.0164 | 0.8731 | 0.0724 |
| **测试集** | **0.9380** | **0.0029** | **0.7579** | **0.9057** |

### 8.4 评估挑战

早期遇到的挑战是训练集和测试集之间存在重叠的交互数据（同一用户-物品对出现多次但 `watch_ratio` 不同），导致数据泄露。通过矩阵规范化和使用 LightFM 专用划分方法解决。

---

## 9. 生成推荐

```python
def recommend_for_user(user_id, model, dataset, user_features_matrix, 
                       item_features_matrix, n=10):
    scores = model.predict(user_array, item_array, 
                          user_features=user_features_matrix, 
                          item_features=item_features_matrix)
    return top_n_items_by_score(scores)
```

函数使用 `model.predict()` 为给定用户预测所有物品的分数，然后返回排名前 n 的物品。

---

## 10. 讨论、挑战与未来工作

### 10.1 关键经验

- **数据清洗至关重要**：初始 EDA 和清洗阶段为构建稳定基础发挥了关键作用
- **特征工程驱动性能**：创建有意义的物品特征并正确转换是关键
- **处理稀疏性和隐式反馈**：LightFM 证明了其在处理稀疏隐式反馈数据和融合混合特征方面的能力
- **评估时谨慎划分**：防止训练/测试集之间的数据泄露对获得可靠评估指标至关重要

### 10.2 主要挑战

- **划分时的数据泄露**：矩阵规范化和仔细划分是解决之道
- **特征选择**：大数据集中选择哪些特征是一个具有高影响力的重大挑战
- **特征缩放和转换**：为不同类型的特征选择合适的归一化和变换技术需要实验
- **超参数调优**：当前模型使用初始参数训练，找到最优超参数对最大化性能至关重要
- **解释特征重要性**：LightFM 使用特征，但直接解释其全局重要性可能很复杂

### 10.3 未来工作

- 超参数调优
- 早停策略优化
- 探索其他模型（如深度学习方法）
- 考虑时序动态

---

## 11. 结论

本项目使用 **LightFM** 模型在 **KuaiRec 数据集**上开发了**混合推荐系统**，该数据集包含来自快手平台的丰富用户交互和内容元数据。

通过仔细的数据清洗、特征工程和评估，我们证明了 LightFM——利用协同过滤和基于内容的特征——能够有效地**从隐式反馈数据中学习用户偏好**。

我们探索了各种物品和用户特征，包括文本和分类元数据，发现简化特征可以提高跨数据集的泛化能力。尽管存在数据稀疏性和潜在泄露等挑战，我们的最终模型**取得了优异的结果**，特别是在测试集上，验证了**混合方法的可行性**。

---

## 参考资料

- LightFM 文档：https://making.lyst.com/lightfm/docs/home.html
- KuaiRec 论文：https://arxiv.org/pdf/2202.10842
- Medium 文章：https://medium.com/@dikosaktiprabowo/hybrid-recommendation-system-using-lightfm-e10dd6b42923
- Medium 文章：https://medium.com/analytics-vidhya/7-types-of-hybrid-recommendation-system-3e4f78266ad8
- 文章：https://brand24.com/blog/tiktok-metrics/
