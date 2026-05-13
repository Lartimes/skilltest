import { useState } from 'react';
import { Plus, Play, Trash2, Eye, Clock, CheckCircle, XCircle, AlertCircle, Cpu } from 'lucide-react';

// 模型类型定义
type ModelStatus = 'draft' | 'training' | 'completed' | 'failed';

interface Model {
  id: string;
  name: string;
  algorithm: 'mf' | 'neumf' | 'deepfm';
  status: ModelStatus;
  params: {
    embedding_dim: number;
    lr: number;
    reg: number;
    epochs: number;
    batch_size: number;
    layers?: number[];
  };
  metrics?: {
    hit_rate_5: number;
    hit_rate_10: number;
    hit_rate_20: number;
    mrr_10: number;
    auc: number;
  };
  progress: number;
  createdAt: string;
  updatedAt: string;
}

// Mock 模型数据
const mockModels: Model[] = [
  {
    id: 'model-001',
    name: 'DeepFM 推荐模型',
    algorithm: 'deepfm',
    status: 'completed',
    params: { embedding_dim: 64, lr: 0.001, reg: 0.0001, epochs: 30, batch_size: 512, layers: [256, 128, 64] },
    metrics: { hit_rate_5: 0.452, hit_rate_10: 0.623, hit_rate_20: 0.756, mrr_10: 0.389, auc: 0.892 },
    progress: 100,
    createdAt: '2026-05-01 10:30:00',
    updatedAt: '2026-05-01 11:45:00',
  },
  {
    id: 'model-002',
    name: '矩阵分解模型',
    algorithm: 'mf',
    status: 'completed',
    params: { embedding_dim: 64, lr: 0.01, reg: 0.01, epochs: 20, batch_size: 256 },
    metrics: { hit_rate_5: 0.312, hit_rate_10: 0.458, hit_rate_20: 0.589, mrr_10: 0.278, auc: 0.756 },
    progress: 100,
    createdAt: '2026-04-28 14:20:00',
    updatedAt: '2026-04-28 15:10:00',
  },
  {
    id: 'model-003',
    name: '神经矩阵分解 v2',
    algorithm: 'neumf',
    status: 'training',
    params: { embedding_dim: 64, lr: 0.001, reg: 0.0001, epochs: 30, batch_size: 256, layers: [128, 64, 32] },
    progress: 67,
    createdAt: '2026-05-07 15:00:00',
    updatedAt: '2026-05-07 15:30:00',
  },
  {
    id: 'model-004',
    name: 'DeepFM v2',
    algorithm: 'deepfm',
    status: 'draft',
    params: { embedding_dim: 64, lr: 0.001, reg: 0.0001, epochs: 30, batch_size: 512, layers: [256, 128, 64] },
    progress: 0,
    createdAt: '2026-05-07 16:00:00',
    updatedAt: '2026-05-07 16:00:00',
  },
];

const algorithmInfo = {
  mf: { name: 'Matrix Factorization', desc: '矩阵分解，经典协同过滤算法' },
  neumf: { name: 'Neural MF', desc: '神经矩阵分解，结合MF与深度学习' },
  deepfm: { name: 'DeepFM', desc: '同时学习低阶和高阶特征交互' },
};

export default function Modeling() {
  const [models, setModels] = useState<Model[]>(mockModels);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newModel, setNewModel] = useState({
    name: '',
    algorithm: 'deepfm' as 'mf' | 'neumf' | 'deepfm',
    embedding_dim: 64,
    lr: 0.001,
    reg: 0.0001,
    epochs: 30,
    batch_size: 256,
    layers: [256, 128, 64],
  });

  const getStatusConfig = (status: ModelStatus) => {
    const configs = {
      draft: { icon: AlertCircle, color: 'text-gray-500 bg-gray-100', label: '草稿' },
      training: { icon: Clock, color: 'text-blue-500 bg-blue-100', label: '训练中' },
      completed: { icon: CheckCircle, color: 'text-green-500 bg-green-100', label: '已完成' },
      failed: { icon: XCircle, color: 'text-red-500 bg-red-100', label: '失败' },
    };
    return configs[status];
  };

  const handleCreateModel = () => {
    const model: Model = {
      id: `model-${Date.now()}`,
      name: newModel.name || `${algorithmInfo[newModel.algorithm].name} ${models.length + 1}`,
      algorithm: newModel.algorithm,
      status: 'draft',
      params: {
        embedding_dim: newModel.embedding_dim,
        lr: newModel.lr,
        reg: newModel.reg,
        epochs: newModel.epochs,
        batch_size: newModel.batch_size,
        layers: newModel.algorithm !== 'mf' ? newModel.layers : undefined,
      },
      progress: 0,
      createdAt: new Date().toLocaleString(),
      updatedAt: new Date().toLocaleString(),
    };
    setModels([model, ...models]);
    setShowCreateModal(false);
  };

  const handleStartTraining = (modelId: string) => {
    setModels(models.map(m => 
      m.id === modelId ? { ...m, status: 'training', progress: 0 } : m
    ));
    
    // 模拟训练进度
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setModels(models.map(m => 
          m.id === modelId ? { 
            ...m, 
            status: 'completed', 
            progress: 100,
            metrics: { 
              hit_rate_5: 0.35 + Math.random() * 0.15,
              hit_rate_10: 0.50 + Math.random() * 0.15,
              hit_rate_20: 0.65 + Math.random() * 0.15,
              mrr_10: 0.30 + Math.random() * 0.10,
              auc: 0.80 + Math.random() * 0.10,
            },
            updatedAt: new Date().toLocaleString(),
          } : m
        ));
      } else {
        setModels(models.map(m => 
          m.id === modelId ? { ...m, progress } : m
        ));
      }
    }, 500);
  };

  return (
    <div className="p-8">
      {/* 页面标题 */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">模型建模</h1>
          <p className="text-gray-500 mt-1">创建和训练推荐模型</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="w-5 h-5 mr-2" />
          新建模型
        </button>
      </div>

      {/* 模型列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {models.map((model) => {
          const statusConfig = getStatusConfig(model.status);
          const StatusIcon = statusConfig.icon;
          
          return (
            <div key={model.id} className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              {/* 模型头部 */}
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${
                      model.algorithm === 'deepfm' ? 'bg-purple-100' :
                      model.algorithm === 'neumf' ? 'bg-blue-100' : 'bg-green-100'
                    }`}>
                      <Cpu className={`w-5 h-5 ${
                        model.algorithm === 'deepfm' ? 'text-purple-600' :
                        model.algorithm === 'neumf' ? 'text-blue-600' : 'text-green-600'
                      }`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{model.name}</h3>
                      <p className="text-sm text-gray-500">{algorithmInfo[model.algorithm].name}</p>
                    </div>
                  </div>
                  <span className={`flex items-center px-3 py-1 rounded-full text-sm ${statusConfig.color}`}>
                    <StatusIcon className="w-4 h-4 mr-1" />
                    {statusConfig.label}
                  </span>
                </div>

                {/* 参数信息 */}
                <div className="grid grid-cols-3 gap-2 text-sm mb-4">
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-gray-500">嵌入维度</p>
                    <p className="font-medium">{model.params.embedding_dim}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-gray-500">学习率</p>
                    <p className="font-medium">{model.params.lr}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-gray-500">训练轮数</p>
                    <p className="font-medium">{model.params.epochs}</p>
                  </div>
                </div>

                {/* 训练进度 */}
                {model.status === 'training' && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-blue-600">训练进度</span>
                      <span className="font-medium">{model.progress.toFixed(0)}%</span>
                    </div>
                    <div className="h-2 bg-blue-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 rounded-full transition-all duration-500"
                        style={{ width: `${model.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">预计剩余时间：约 {Math.ceil((100 - model.progress) / 10)} 分钟</p>
                  </div>
                )}

                {/* 评估指标 */}
                {model.metrics && (
                  <div className="grid grid-cols-5 gap-2 text-xs">
                    <div className="text-center">
                      <p className="text-gray-500">HR@5</p>
                      <p className="font-semibold text-primary-600">{(model.metrics.hit_rate_5 * 100).toFixed(1)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500">HR@10</p>
                      <p className="font-semibold text-primary-600">{(model.metrics.hit_rate_10 * 100).toFixed(1)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500">HR@20</p>
                      <p className="font-semibold text-primary-600">{(model.metrics.hit_rate_20 * 100).toFixed(1)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500">MRR@10</p>
                      <p className="font-semibold text-green-600">{(model.metrics.mrr_10 * 100).toFixed(1)}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500">AUC</p>
                      <p className="font-semibold text-orange-600">{(model.metrics.auc * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                )}
              </div>

              {/* 模型底部 */}
              <div className="p-4 flex items-center justify-between">
                <div className="text-xs text-gray-500">
                  创建于 {model.createdAt}
                </div>
                <div className="flex gap-2">
                  {model.status === 'draft' && (
                    <button
                      onClick={() => handleStartTraining(model.id)}
                      className="flex items-center px-3 py-1.5 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm"
                    >
                      <Play className="w-4 h-4 mr-1" />
                      开始训练
                    </button>
                  )}
                  <button className="p-2 text-gray-400 hover:text-primary-600 hover:bg-gray-50 rounded-lg">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-gray-50 rounded-lg">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 新建模型弹窗 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold">新建模型</h2>
            </div>
            
            <div className="p-6 space-y-6">
              {/* 模型名称 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">模型名称</label>
                <input
                  type="text"
                  placeholder="留空将使用默认名称"
                  value={newModel.name}
                  onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* 算法选择 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">选择算法</label>
                <div className="grid grid-cols-3 gap-3">
                  {(['mf', 'neumf', 'deepfm'] as const).map((algo) => (
                    <button
                      key={algo}
                      onClick={() => setNewModel({ ...newModel, algorithm: algo })}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        newModel.algorithm === algo
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <Cpu className={`w-6 h-6 mx-auto mb-2 ${
                        algo === 'mf' ? 'text-green-500' : algo === 'neumf' ? 'text-blue-500' : 'text-purple-500'
                      }`} />
                      <p className="font-medium text-sm">{algorithmInfo[algo].name}</p>
                      <p className="text-xs text-gray-500 mt-1">{algorithmInfo[algo].desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* 训练参数 */}
              <div>
                <h3 className="text-lg font-semibold mb-4">训练参数</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">嵌入维度</label>
                    <input
                      type="number"
                      value={newModel.embedding_dim}
                      onChange={(e) => setNewModel({ ...newModel, embedding_dim: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">学习率</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={newModel.lr}
                      onChange={(e) => setNewModel({ ...newModel, lr: parseFloat(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">正则化系数</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={newModel.reg}
                      onChange={(e) => setNewModel({ ...newModel, reg: parseFloat(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">批次大小</label>
                    <input
                      type="number"
                      value={newModel.batch_size}
                      onChange={(e) => setNewModel({ ...newModel, batch_size: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">训练轮数</label>
                    <input
                      type="number"
                      value={newModel.epochs}
                      onChange={(e) => setNewModel({ ...newModel, epochs: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>

              {/* 隐藏层（NeuMF/DeepFM） */}
              {newModel.algorithm !== 'mf' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">隐藏层结构</label>
                  <div className="flex flex-wrap gap-2">
                    {newModel.layers.map((layer, index) => (
                      <div key={index} className="flex items-center bg-gray-100 rounded-lg px-3 py-2">
                        <span className="text-gray-500 text-sm">层{index + 1}:</span>
                        <input
                          type="number"
                          value={layer}
                          onChange={(e) => {
                            const newLayers = [...newModel.layers];
                            newLayers[index] = parseInt(e.target.value);
                            setNewModel({ ...newModel, layers: newLayers });
                          }}
                          className="w-16 bg-transparent text-center focus:outline-none"
                        />
                      </div>
                    ))}
                    <button
                      onClick={() => setNewModel({ ...newModel, layers: [...newModel.layers, 64] })}
                      className="px-3 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-primary-500 hover:text-primary-500"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                取消
              </button>
              <button
                onClick={handleCreateModel}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                创建模型
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
