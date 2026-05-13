import { useState } from 'react'
import { 
  Play, Pause, Settings, Brain, Layers, 
  Database, Target, CheckCircle
} from 'lucide-react'

// Mock 模型配置
const modelConfigs = [
  { id: 'neumf', name: 'NeuMF', desc: '神经矩阵分解', params: 125000, selected: true },
  { id: 'deepfm', name: 'DeepFM', desc: '深度因子分解机', params: 256000, selected: false },
  { id: 'mf', name: 'Matrix Factorization', desc: '矩阵分解', params: 50000, selected: false },
  { id: 'dien', name: 'DIEN', desc: '深度兴趣网络', params: 320000, selected: false },
]

export default function ModelTraining() {
  const [isTraining, setIsTraining] = useState(false)
  const [trainingProgress, setTrainingProgress] = useState(0)
  const [currentEpoch, setCurrentEpoch] = useState(0)
  const [selectedModel, setSelectedModel] = useState('neumf')
  const [params, setParams] = useState({
    epochs: 50,
    batchSize: 256,
    learningRate: 0.001,
    optimizer: 'Adam',
    regularization: 0.01,
  })

  const handleTrain = () => {
    if (isTraining) {
      setIsTraining(false)
      return
    }
    setIsTraining(true)
    setTrainingProgress(0)
    setCurrentEpoch(0)
    
    const interval = setInterval(() => {
      setTrainingProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsTraining(false)
          return 100
        }
        setCurrentEpoch(Math.floor(prev / 100 * params.epochs))
        return prev + 2
      })
    }, 100)
  }

  return (
    <div className="p-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">模型训练</h1>
          <p className="text-gray-500 mt-1">配置并训练推荐模型</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 flex items-center gap-2">
            <Settings className="w-4 h-4" />
            高级配置
          </button>
          <button
            onClick={handleTrain}
            className={`px-6 py-2 rounded-lg font-medium flex items-center gap-2 ${
              isTraining 
                ? 'bg-red-500 text-white hover:bg-red-600' 
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }`}
          >
            {isTraining ? (
              <>
                <Pause className="w-4 h-4" />
                停止训练
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                开始训练
              </>
            )}
          </button>
        </div>
      </div>

      {/* 训练进度 */}
      {isTraining && (
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold">训练进行中...</h3>
                <p className="text-sm text-white/80">Epoch {currentEpoch} / {params.epochs}</p>
              </div>
            </div>
            <span className="text-2xl font-bold">{trainingProgress}%</span>
          </div>
          <div className="w-full h-3 bg-white/20 rounded-full overflow-hidden">
            <div 
              className="h-full bg-white rounded-full transition-all duration-300"
              style={{ width: `${trainingProgress}%` }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：模型选择 */}
        <div className="space-y-6">
          {/* 模型选择 */}
          <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-500" />
                选择模型
              </h3>
            </div>
            <div className="p-4 space-y-3">
              {modelConfigs.map((model) => (
                <button
                  key={model.id}
                  onClick={() => setSelectedModel(model.id)}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                    selectedModel === model.id 
                      ? 'border-indigo-500 bg-indigo-50' 
                      : 'border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{model.name}</h4>
                      <p className="text-sm text-gray-500 mt-1">{model.desc}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-gray-400">{(model.params / 1000).toFixed(0)}K 参数</span>
                      {selectedModel === model.id && (
                        <CheckCircle className="w-5 h-5 text-indigo-500 mt-1" />
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* 训练统计 */}
          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-indigo-500" />
              训练目标
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">目标指标 HR@10</span>
                <span className="font-medium text-indigo-600">≥ 0.65</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">目标指标 MRR@10</span>
                <span className="font-medium text-indigo-600">≥ 0.40</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">预计训练时间</span>
                <span className="font-medium text-gray-900">~15 分钟</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">数据集大小</span>
                <span className="font-medium text-gray-900">500K 样本</span>
              </div>
            </div>
          </div>
        </div>

        {/* 中间：训练参数 */}
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Settings className="w-5 h-5 text-indigo-500" />
              训练参数
            </h3>
          </div>
          <div className="p-6 space-y-6">
            {/* Epochs */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">训练轮数 (Epochs)</label>
                <span className="text-sm text-indigo-600 font-medium">{params.epochs}</span>
              </div>
              <input
                type="range"
                min={1}
                max={200}
                value={params.epochs}
                onChange={(e) => setParams({...params, epochs: Number(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>1</span>
                <span>200</span>
              </div>
            </div>

            {/* Batch Size */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">批量大小 (Batch Size)</label>
              <div className="flex gap-2">
                {[64, 128, 256, 512].map((size) => (
                  <button
                    key={size}
                    onClick={() => setParams({...params, batchSize: size})}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                      params.batchSize === size
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            {/* Learning Rate */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">学习率 (Learning Rate)</label>
              <div className="flex gap-2">
                {[0.0001, 0.0005, 0.001, 0.005].map((lr) => (
                  <button
                    key={lr}
                    onClick={() => setParams({...params, learningRate: lr})}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                      params.learningRate === lr
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {lr}
                  </button>
                ))}
              </div>
            </div>

            {/* Optimizer */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">优化器 (Optimizer)</label>
              <div className="flex gap-2">
                {['Adam', 'SGD', 'RMSprop'].map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setParams({...params, optimizer: opt})}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                      params.optimizer === opt
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            {/* Regularization */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">正则化系数</label>
                <span className="text-sm text-indigo-600 font-medium">{params.regularization}</span>
              </div>
              <input
                type="range"
                min={0}
                max={0.1}
                step={0.001}
                value={params.regularization}
                onChange={(e) => setParams({...params, regularization: Number(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
            </div>
          </div>
        </div>

        {/* 右侧：数据配置 */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Database className="w-5 h-5 text-indigo-500" />
                数据配置
              </h3>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">训练集比例</label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min={60}
                    max={90}
                    value={80}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                  <span className="text-sm font-medium text-indigo-600 w-12">80%</span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 border-t border-gray-100">
                <span className="text-gray-600">验证集</span>
                <span className="font-medium text-gray-900">10%</span>
              </div>
              <div className="flex items-center justify-between py-2 border-t border-gray-100">
                <span className="text-gray-600">测试集</span>
                <span className="font-medium text-gray-900">10%</span>
              </div>
            </div>
          </div>

          {/* 当前配置摘要 */}
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-indigo-500" />
              当前配置
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">模型</span>
                <span className="font-medium text-gray-900">{modelConfigs.find(m => m.id === selectedModel)?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Epochs</span>
                <span className="font-medium text-gray-900">{params.epochs}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Batch Size</span>
                <span className="font-medium text-gray-900">{params.batchSize}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Learning Rate</span>
                <span className="font-medium text-gray-900">{params.learningRate}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Optimizer</span>
                <span className="font-medium text-gray-900">{params.optimizer}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
