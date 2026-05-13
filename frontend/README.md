# ML Platform - 模型中台管理系统

一个面向数据科学团队的模型中台前端展示系统（纯 Mock 数据，不对接真实 API）。

## 🚀 快速启动

```bash
# 进入项目目录
cd d:/Desktop/毕设/backend/frontend/ml-platform

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 🛠️ 技术栈

| 技术 | 说明 |
|------|------|
| **React 18** | UI 框架 |
| **TypeScript** | 类型安全 |
| **Vite** | 快速构建工具 |
| **TailwindCSS** | 原子化 CSS 样式 |
| **React Router** | 页面路由 |
| **Recharts** | 数据可视化图表 |
| **Lucide React** | 图标库 |

## 📂 项目结构

```
ml-platform/
├── src/
│   ├── components/     # 公共组件（Layout 布局）
│   ├── pages/         # 页面组件
│   │   ├── Dashboard.tsx      # 首页
│   │   ├── DataCleaning.tsx    # 数据清洗
│   │   ├── Modeling.tsx       # 建模
│   │   ├── EDA.tsx            # EDA分析
│   │   ├── ModelStatus.tsx    # 模型状态
│   │   └── ModelRecommend.tsx # 模型推荐
│   ├── App.tsx        # 根组件 & 路由配置
│   └── main.tsx      # 入口文件
├── index.html
└── package.json
```

## 📱 页面介绍

| 路径 | 页面 | 功能说明 |
|------|------|----------|
| `/` | 首页 Dashboard | 统计概览、功能入口、最近模型、快捷操作 |
| `/data` | 数据清洗 | 文件上传拖拽、清洗规则配置、清洗结果统计、日志展示 |
| `/modeling` | 模型建模 | 模型列表展示、参数配置表单、训练状态进度条 |
| `/eda` | EDA分析 | 数据统计表格、评分分布图、缺失值饼图、相关性热力图 |
| `/status` | 模型状态 | 实时指标监控图表（请求量、延迟、错误率、命中率） |
| `/recommendation` | 模型推荐 | 场景化模型推荐卡片、模型对比表格、推荐理由 |

## ✨ 页面预览

### 首页 Dashboard
- 4 个统计卡片：在线模型、数据总量、日均请求、平均准确率
- 5 个功能模块入口卡片
- 最近模型列表
- 4 个快捷操作入口

### 数据清洗
- 拖拽上传区域（支持 CSV/JSON/Parquet）
- 清洗结果统计卡片
- 清洗日志列表

### 建模
- 模型卡片列表（DeepFM、MF、NeuMF）
- 训练状态标签（草稿/训练中/已完成/失败）
- 准确率进度条
- 新建模型弹窗（参数配置表单）

### EDA 分析
- 数据概览统计
- 评分分布柱状图
- 缺失值饼图
- 数据类型分布

### 模型状态
- 24 小时请求量折线图
- 延迟监控
- 错误率趋势
- Hit Rate 指标

### 模型推荐
- 推荐模型卡片（DeepFM、DIN、Wide&Deep）
- 场景匹配说明
- 优缺点对比

---

> ⚠️ **注意**：此项目为前端展示页面，所有数据均为本地 Mock 数据，不涉及真实后端 API 对接。

## 📦 可用命令

```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览生产版本
```
