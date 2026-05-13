import type { 
  CleaningRule, 
  CleaningResult, 
  Model, 
  ModelConfig,
  Statistic,
  ModelMetrics,
  ModelRecommendation 
} from '../types';

// 数据清洗规则
export const cleaningRules: CleaningRule[] = [
  { id: '1', name: '缺失值填充', type: 'missing', enabled: true, config: { method: 'mean' } },
  { id: '2', name: '重复数据删除', type: 'duplicate', enabled: true, config: { keep: 'first' } },
  { id: '3', name: '异常值处理', type: 'outlier', enabled: true, config: { method: 'iqr', threshold: 3 } },
  { id: '4', name: '格式标准化', type: 'format', enabled: false, config: { target: 'lowercase' } },
];

export const cleaningResults: CleaningResult = {
  totalRows: 100000,
  cleanedRows: 98500,
  removedRows: 1500,
  missingFilled: 3200,
  duplicatesRemoved: 1200,
  outliersHandled: 300,
};

// 模型列表
export const models: Model[] = [
  {
    id: 'deepfm-001',
    name: 'DeepFM 推荐模型',
    type: 'deepfm',
    status: 'completed',
    accuracy: 0.892,
    precision: 0.865,
    recall: 0.834,
    f1: 0.849,
    createdAt: '2026-04-15',
    updatedAt: '2026-05-01',
  },
  {
    id: 'mf-001',
    name: '矩阵分解模型',
    type: 'mf',
    status: 'completed',
    accuracy: 0.756,
    precision: 0.742,
    recall: 0.718,
    f1: 0.730,
    createdAt: '2026-04-10',
    updatedAt: '2026-04-28',
  },
  {
    id: 'neumf-001',
    name: '神经矩阵分解',
    type: 'neumf',
    status: 'training',
    createdAt: '2026-05-05',
    updatedAt: '2026-05-07',
  },
  {
    id: 'deepfm-002',
    name: 'DeepFM v2',
    type: 'deepfm',
    status: 'draft',
    createdAt: '2026-05-06',
    updatedAt: '2026-05-06',
  },
];

export const modelConfig: ModelConfig = {
  learningRate: 0.001,
  batchSize: 256,
  epochs: 50,
  embeddingDim: 64,
  layers: [128, 64, 32],
};

// EDA 统计数据
export const statistics: Statistic[] = [
  { column: 'user_id', type: 'int64', count: 100000, missing: 0, unique: 10000 },
  { column: 'item_id', type: 'int64', count: 100000, missing: 0, unique: 5000 },
  { column: 'rating', type: 'float64', count: 100000, missing: 50, mean: 3.72, std: 1.23, min: 1, max: 5, unique: 5 },
  { column: 'timestamp', type: 'datetime', count: 100000, missing: 0, unique: 86400 },
  { column: 'category', type: 'category', count: 100000, missing: 120, unique: 20 },
  { column: 'duration', type: 'int64', count: 100000, missing: 0, mean: 180, std: 45, min: 15, max: 600 },
];

// 缺失值数据
export const missingData = [
  { column: 'rating', missing: 50, percentage: 0.05 },
  { column: 'category', missing: 120, percentage: 0.12 },
  { column: 'user_id', missing: 0, percentage: 0 },
  { column: 'item_id', missing: 0, percentage: 0 },
  { column: 'timestamp', missing: 0, percentage: 0 },
];

// 分布数据
export const distributionData = [
  { range: '0-1', count: 8000 },
  { range: '1-2', count: 12000 },
  { range: '2-3', count: 25000 },
  { range: '3-4', count: 35000 },
  { range: '4-5', count: 20000 },
];

// 模型状态指标
export const modelMetrics: ModelMetrics[] = Array.from({ length: 24 }, (_, i) => ({
  timestamp: `${i.toString().padStart(2, '0')}:00`,
  requests: Math.floor(Math.random() * 5000) + 1000,
  latency: Math.floor(Math.random() * 50) + 20,
  errorRate: Math.random() * 0.02,
  hitRate: 0.85 + Math.random() * 0.1,
}));

// 模型推荐
export const recommendations: ModelRecommendation[] = [
  {
    id: 'rec-1',
    name: 'DeepFM',
    type: '推荐系统',
    scenario: '短视频推荐场景',
    accuracy: 0.892,
    speed: 'medium',
    resourceUsage: 'medium',
    pros: ['同时学习低阶和高阶特征交互', '无需人工特征工程', '性能优异'],
    cons: ['训练时间较长', '资源消耗中等'],
  },
  {
    id: 'rec-2',
    name: 'DIN',
    type: '推荐系统',
    scenario: '用户兴趣动态变化场景',
    accuracy: 0.875,
    speed: 'slow',
    resourceUsage: 'high',
    pros: ['捕捉用户兴趣的动态变化', '注意力机制精确建模'],
    cons: ['计算开销大', '需要大量训练数据'],
  },
  {
    id: 'rec-3',
    name: 'Wide&Deep',
    type: '推荐系统',
    scenario: '需要记忆和泛化能力的场景',
    accuracy: 0.858,
    speed: 'fast',
    resourceUsage: 'low',
    pros: ['平衡记忆与泛化', '训练速度快', '易于部署'],
    cons: ['Wide部分需要人工设计特征'],
  },
];

// 清洗日志
export const cleaningLogs = [
  { time: '15:30:22', level: 'info', message: '开始加载数据文件 user_behavior.csv' },
  { time: '15:30:25', level: 'info', message: '数据加载完成，共 100,000 行' },
  { time: '15:30:26', level: 'warning', message: '检测到 50 个缺失值 in rating 列' },
  { time: '15:30:27', level: 'warning', message: '检测到 120 个缺失值 in category 列' },
  { time: '15:30:28', level: 'info', message: '开始执行缺失值填充策略' },
  { time: '15:30:30', level: 'info', message: '检测到 1,200 个重复记录' },
  { time: '15:30:31', level: 'info', message: '开始删除重复记录' },
  { time: '15:30:32', level: 'info', message: '检测到 300 个异常值' },
  { time: '15:30:33', level: 'info', message: '异常值处理完成' },
  { time: '15:30:34', level: 'success', message: '数据清洗完成，共移除 1,500 行' },
];
