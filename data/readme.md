# 数据集说明

## 数据集来源

- 主数据集：https://zenodo.org/records/8181109
- 参考项目：
  - https://github.com/chongminggao/KuaiRec
  - https://github.com/gabcal07/Kuairec_Hybrid_recommender_system

## 数据集文件

### 1. user_features.csv

**文件大小**：约351KB
**记录数**：约10,000条

**字段说明**：
- `user_id`：用户唯一标识
- `onehot_feat1`：用户特征1（one-hot编码）
- `onehot_feat2`：用户特征2（one-hot编码）
- `search_active_level`：搜索活跃度等级（0-5）
- `reco_active_level`：推荐活跃度等级（0-5）

### 2. item_features.csv

**文件大小**：约1.2GB
**记录数**：约1,000,000条

**字段说明**：
- `item_id`：物品唯一标识
- `caption`：物品标题/描述（可能是编码后的形式）
- `author_id`：作者/上传者ID
- `item_type`：物品类型（如NORMAL, UNKNOW, IMAGE_ATLAS等）
- `upload_time`：上传时间
- `upload_type`：上传类型
- `music_id`：背景音乐ID
- `first_level_category_id`：一级分类ID
- `first_level_category_name`：一级分类名称
- `second_level_category_id`：二级分类ID
- `second_level_category_name`：二级分类名称
- `third_level_category_id`：三级分类ID
- `third_level_category_name`：三级分类名称
- `fourth_level_category_id`：四级分类ID
- `fourth_level_category_name`：四级分类名称
- `first_level_category_name_en`：一级分类英文名称
- `second_level_category_name_en`：二级分类英文名称
- `third_level_category_name_en`：三级分类英文名称
- `fourth_level_category_name_en`：四级分类英文名称

### 3. social_network.csv

**文件大小**：约6.8KB
**记录数**：约500条

**字段说明**：
- `user_id`：用户唯一标识
- `user_follow_id`：用户关注的其他用户ID

### 4. src_inter.csv

**文件大小**：约333MB
**记录数**：约5,000,000条

**字段说明**：
- `keyword`：搜索关键词（编码后的形式）
- `item_id`：物品唯一标识
- `click_cnt`：点击次数
- `search_session_id`：搜索会话ID
- `item_type`：物品类型
- `user_id`：用户唯一标识
- `search_session_timestamp`：搜索会话时间戳
- `search_source`：搜索来源
- `search_session_time`：搜索会话时间

### 5. rec_inter.csv

**文件大小**：约568MB
**记录数**：约10,000,000条

**字段说明**：
- `user_id`：用户唯一标识
- `item_id`：物品唯一标识
- `duration_ms`：物品时长（毫秒）
- `playing_time`：播放时长（毫秒）
- `timestamp`：时间戳
- `forward`：是否转发（0/1）
- `like`：是否点赞（0/1）
- `follow`：是否关注（0/1）
- `search_item_related`：是否与搜索相关（0/1）
- `search`：是否搜索（0/1）
- `click`：是否点击（0/1）
- `time`：时间

## 数据关系

```
用户 (user_features) <--> 搜索交互 (src_inter)
用户 (user_features) <--> 推荐交互 (rec_inter)
用户 (user_features) <--> 社交网络 (social_network)
物品 (item_features) <--> 搜索交互 (src_inter)
物品 (item_features) <--> 推荐交互 (rec_inter)
```

## 数据处理建议

### 大文件处理策略

由于`item_features.csv`、`src_inter.csv`和`rec_inter.csv`文件较大（超过100MB），建议采用以下处理策略：

1. **流式处理**：使用pandas的`chunksize`参数进行分块读取
2. **数据采样**：在初始分析阶段，可使用采样数据进行探索
3. **并行处理**：利用多核CPU进行并行数据处理
4. **数据压缩**：考虑使用压缩格式存储处理后的数据

### 数据清洗建议

1. **缺失值处理**：检查并处理各数据集中的缺失值
2. **异常值处理**：识别并处理异常值，如播放时长超过物品时长的情况
3. **重复数据处理**：移除重复记录
4. **数据类型优化**：优化数据类型以减少内存使用

### 特征工程建议

1. **用户特征**：
   - 活跃度特征组合
   - 用户行为统计特征

2. **物品特征**：
   - 分类特征编码
   - 物品 popularity 特征
   - 文本特征提取（如标题中的关键词）

3. **交互特征**：
   - 点击率、点赞率等衍生特征
   - 时间特征（如小时、星期等）

4. **社交特征**：
   - 用户关注数、粉丝数
   - 社交网络结构特征

## 推荐系统应用

本数据集可用于构建以下推荐系统：

1. **协同过滤推荐**：基于用户-物品交互矩阵
2. **内容推荐**：基于物品特征和用户偏好
3. **混合推荐**：结合协同过滤和内容推荐
4. **社交推荐**：利用社交网络信息
5. **搜索推荐**：结合搜索行为和推荐结果

## 注意事项

1. 数据集中的某些字段（如`caption`、`keyword`）可能是编码后的形式，需要进一步解析
2. 时间字段需要统一处理为标准格式
3. 分类特征需要进行适当的编码处理
4. 大文件处理时需注意内存限制
