import { useState } from 'react';
import { Activity, Brain, CheckCircle, XCircle, Clock, Play, Pause, Trash2, RefreshCw, Zap, TrendingUp, Users, ChevronRight } from 'lucide-react';

interface Model {
  id: string;
  name: string;
  algorithm: string;
  status: 'draft' | 'training' | 'completed' | 'failed' | 'online' | 'offline';
  metrics: {
    hr5: number;
    hr10: number;
    hr20: number;
    mrr10: number;
    auc: number;
  };
  trainingProgress: number;
  currentEpoch: number;
  totalEpochs: number;
  requests: number;
  avgLatency: number;
  onlineTime: string;
}

const mockModels: Model[] = [
  {
    id: 'model-001',
    name: 'DeepFM 推荐模型 v2.1',
    algorithm: 'DeepFM',
    status: 'online',
    metrics: { hr5: 0.892, hr10: 0.923, hr20: 0.956, mrr10: 0.634, auc: 0.845 },
    trainingProgress: 100,
    currentEpoch: 50,
    totalEpochs: 50,
    requests: 12580,
    avgLatency: 23,
    onlineTime: '2026-05-06 14:30',
  },
  {
    id: 'model-002',
    name: '矩阵分解模型 v1.5',
    algorithm: 'MF',
    status: 'online',
    metrics: { hr5: 0.756, hr10: 0.812, hr20: 0.878, mrr10: 0.521, auc: 0.782 },
    trainingProgress: 100,
    currentEpoch: 30,
    totalEpochs: 30,
    requests: 8932,
    avgLatency: 12,
    onlineTime: '2026-05-05 09:15',
  },
  {
    id: 'model-003',
    name: '神经矩阵分解 v1.0',
    algorithm: 'NeuMF',
    status: 'training',
    metrics: { hr5: 0, hr10: 0, hr20: 0, mrr10: 0, auc: 0 },
    trainingProgress: 68,
    currentEpoch: 34,
    totalEpochs: 50,
    requests: 0,
    avgLatency: 0,
    onlineTime: '-',
  },
  {
    id: 'model-004',
    name: 'Wide&Deep 实验版',
    algorithm: 'WideDeep',
    status: 'failed',
    metrics: { hr5: 0, hr10: 0, hr20: 0, mrr10: 0, auc: 0 },
    trainingProgress: 45,
    currentEpoch: 23,
    totalEpochs: 50,
    requests: 0,
    avgLatency: 0,
    onlineTime: '-',
  },
];

const statusConfig = {
  draft: { label: '草稿', color: 'bg-gray-100 text-gray-600', icon: Clock },
  training: { label: '训练中', color: 'bg-blue-100 text-blue-600', icon: RefreshCw },
  completed: { label: '已完成', color: 'bg-green-100 text-green-600', icon: CheckCircle },
  failed: { label: '失败', color: 'bg-red-100 text-red-600', icon: XCircle },
  online: { label: '在线', color: 'bg-emerald-100 text-emerald-600', icon: Zap },
  offline: { label: '离线', color: 'bg-gray-100 text-gray-500', icon: XCircle },
};

export default function ModelStatus() {
  const [models] = useState<Model[]>(mockModels);
  const [selectedModel, setSelectedModel] = useState<Model | null>(models[0]);

  const onlineModels = models.filter(m => m.status === 'online');
  const trainingModels = models.filter(m => m.status === 'training');

  return (
    <div className="p-8">
      {/* 标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">模型状态</h1>
          <p className="text-gray-500 mt-1">监控已部署模型的运行状态和性能指标</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <RefreshCw className="w-4 h-4" />
          刷新状态
        </button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard icon={Brain} label="模型总数" value={models.length.toString()} color="blue" />
        <StatCard icon={Zap} label="在线模型" value={onlineModels.length.toString()} color="green" />
        <StatCard icon={RefreshCw} label="训练中" value={trainingModels.length.toString()} color="purple" />
        <StatCard icon={TrendingUp} label="总请求量" value={(models.reduce((s, m) => s + m.requests, 0)).toLocaleString()} color="orange" />
      </div>

      <div className="flex gap-6">
        {/* 左侧：模型列表 */}
        <div className="w-96 flex-shrink-0">
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">模型列表</h2>
            </div>
            <div className="divide-y">
              {models.map((model) => {
                const status = statusConfig[model.status];
                const StatusIcon = status.icon;
                return (
                  <div
                    key={model.id}
                    onClick={() => setSelectedModel(model)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${selectedModel?.id === model.id ? 'bg-blue-50' : ''}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Brain className="w-5 h-5 text-gray-400" />
                        <span className="font-medium text-gray-900">{model.name}</span>
                      </div>
                      <span className={`flex items-center gap-1 px-2 py-1 text-xs rounded-full ${status.color}`}>
                        <StatusIcon className="w-3 h-3" />
                        {status.label}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>{model.algorithm}</span>
                      {model.status === 'training' && (
                        <span>{Math.round(model.trainingProgress)}%</span>
                      )}
                      {model.status === 'online' && (
                        <span>{model.requests.toLocaleString()} 请求</span>
                      )}
                    </div>
                    {model.status === 'training' && (
                      <div className="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full transition-all"
                          style={{ width: `${model.trainingProgress}%` }}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 右侧：模型详情 */}
        <div className="flex-1">
          {selectedModel ? (
            <div className="space-y-6">
              {/* 模型概览 */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-blue-100 rounded-xl">
                      <Brain className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{selectedModel.name}</h2>
                      <p className="text-gray-500">{selectedModel.algorithm} 算法</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {selectedModel.status === 'online' && (
                      <>
                        <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                          <Pause className="w-5 h-5" />
                        </button>
                        <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </>
                    )}
                    {selectedModel.status === 'training' && (
                      <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
                        <XCircle className="w-5 h-5" />
                      </button>
                    )}
                    {selectedModel.status === 'draft' && (
                      <button className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700">
                        <Play className="w-4 h-4" />
                        开始训练
                      </button>
                    )}
                  </div>
                </div>

                {/* 训练进度 */}
                {selectedModel.status === 'training' && (
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">训练进度</span>
                      <span className="text-sm font-medium">Epoch {selectedModel.currentEpoch} / {selectedModel.totalEpochs}</span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full transition-all"
                        style={{ width: `${selectedModel.trainingProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* 实时监控 */}
                {selectedModel.status === 'online' && (
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-gray-500 mb-1">
                        <Users className="w-4 h-4" />
                        <span className="text-sm">请求量</span>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">{selectedModel.requests.toLocaleString()}</p>
                      <p className="text-xs text-green-500 mt-1">+12% 较昨日</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-gray-500 mb-1">
                        <Activity className="w-4 h-4" />
                        <span className="text-sm">平均延迟</span>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">{selectedModel.avgLatency}ms</p>
                      <p className="text-xs text-green-500 mt-1">-5ms 较昨日</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-gray-500 mb-1">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">上线时间</span>
                      </div>
                      <p className="text-lg font-bold text-gray-900">{selectedModel.onlineTime.split(' ')[0]}</p>
                      <p className="text-xs text-gray-500 mt-1">2天前</p>
                    </div>
                  </div>
                )}
              </div>

              {/* 评估指标 */}
              {(selectedModel.status === 'completed' || selectedModel.status === 'online') && (
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">评估指标</h3>
                    <button className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
                      查看详情 <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-5 gap-4">
                    <MetricCard label="HR@5" value={(selectedModel.metrics.hr5 * 100).toFixed(1) + '%'} />
                    <MetricCard label="HR@10" value={(selectedModel.metrics.hr10 * 100).toFixed(1) + '%'} />
                    <MetricCard label="HR@20" value={(selectedModel.metrics.hr20 * 100).toFixed(1) + '%'} />
                    <MetricCard label="MRR@10" value={(selectedModel.metrics.mrr10 * 100).toFixed(1) + '%'} />
                    <MetricCard label="AUC" value={(selectedModel.metrics.auc * 100).toFixed(1) + '%'} />
                  </div>
                </div>
              )}

              {/* 失败原因 */}
              {selectedModel.status === 'failed' && (
                <div className="bg-red-50 rounded-xl border border-red-200 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <XCircle className="w-5 h-5 text-red-500" />
                    <h3 className="font-semibold text-red-900">训练失败</h3>
                  </div>
                  <div className="bg-white rounded-lg p-4 mb-4">
                    <p className="text-sm text-gray-600 mb-2">错误信息：</p>
                    <code className="text-sm text-red-600">RuntimeError: GPU memory overflow at Epoch 23</code>
                  </div>
                  <div className="flex gap-2">
                    <button className="flex-1 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                      重新训练
                    </button>
                    <button className="flex-1 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
                      查看日志
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full bg-white rounded-xl border border-gray-200">
              <p className="text-gray-500">选择一个模型查看详情</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colors[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3 text-center">
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}
