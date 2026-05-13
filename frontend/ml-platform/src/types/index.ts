// 数据清洗相关类型
export interface CleaningRule {
  id: string;
  name: string;
  type: 'missing' | 'duplicate' | 'outlier' | 'format';
  enabled: boolean;
  config: Record<string, unknown>;
}

export interface CleaningResult {
  totalRows: number;
  cleanedRows: number;
  removedRows: number;
  missingFilled: number;
  duplicatesRemoved: number;
  outliersHandled: number;
}

// 建模相关类型
export interface Model {
  id: string;
  name: string;
  type: 'deepfm' | 'mf' | 'neumf';
  status: 'draft' | 'training' | 'completed' | 'failed';
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1?: number;
  createdAt: string;
  updatedAt: string;
}

export interface ModelConfig {
  learningRate: number;
  batchSize: number;
  epochs: number;
  embeddingDim: number;
  layers: number[];
}

// EDA相关类型
export interface Statistic {
  column: string;
  type: string;
  count: number;
  missing: number;
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  unique?: number;
}

// 模型状态相关类型
export interface ModelMetrics {
  timestamp: string;
  requests: number;
  latency: number;
  errorRate: number;
  hitRate: number;
}

// 模型推荐相关类型
export interface ModelRecommendation {
  id: string;
  name: string;
  type: string;
  scenario: string;
  accuracy: number;
  speed: 'fast' | 'medium' | 'slow';
  resourceUsage: 'low' | 'medium' | 'high';
  pros: string[];
  cons: string[];
}
