import { useState } from 'react'
import { 
  Clock, TrendingUp, 
  Star, ChevronRight, Sparkles, Zap
} from 'lucide-react'

// Mock 用户数据
const mockUser = {
  id: 'user_001',
  name: '张小明',
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Zhang',
  interests: ['科技', '数码', 'AI', '数码测评'],
  level: '资深用户',
  joinDate: '2024-03-15'
}

// Mock 最近观看
const mockWatchHistory = [
  { id: 1, title: 'MacBook Pro M4 深度测评', channel: '科技美学', duration: '18:32', watchedAt: '2小时前', thumbnail: '💻', progress: 95 },
  { id: 2, title: 'iPhone 16 Pro 夜景拍摄对比', channel: '数码研究所', duration: '12:45', watchedAt: '昨天', thumbnail: '📱', progress: 100 },
  { id: 3, title: 'GPT-5 能取代程序员吗', channel: 'AI前线', duration: '25:18', watchedAt: '2天前', thumbnail: '🤖', progress: 78 },
  { id: 4, title: 'Sony WH-1000XM6 体验报告', channel: '音频发烧友', duration: '15:20', watchedAt: '3天前', thumbnail: '🎧', progress: 60 },
  { id: 5, title: 'NVIDIA RTX 5090 性能首测', channel: '硬件星球', duration: '22:10', watchedAt: '4天前', thumbnail: '🎮', progress: 100 },
  { id: 6, title: '小米15 Ultra 拍照体验', channel: '摄影频道', duration: '16:40', watchedAt: '5天前', thumbnail: '📷', progress: 45 },
]

// Mock 推荐结果
const mockRecommendations = [
  { id: 101, title: 'Apple Intelligence 全面解析', channel: '科技美学', reason: '与你观看的科技内容高度相关', score: 0.96, thumbnail: '🍎' },
  { id: 102, title: 'iPad Pro M4 能否替代电脑', channel: '数码研究所', reason: '基于你的数码设备偏好', score: 0.92, thumbnail: '📲' },
  { id: 103, title: 'Claude 4 深度测评', channel: 'AI前线', reason: '你经常观看AI相关视频', score: 0.89, thumbnail: '🧠' },
  { id: 104, title: 'Type-C 接口发展史', channel: '硬件星球', reason: '基于你的设备测评偏好', score: 0.85, thumbnail: '🔌' },
  { id: 105, title: 'AirPods Pro 3 抢先体验', channel: '音频发烧友', reason: '你观看过同类型音频内容', score: 0.82, thumbnail: '🎵' },
]

// 用户实时指标
const mockMetrics = {
  watchTime: '12.5h',
  avgWatchTime: '15min',
  interaction: '85%',
  completionRate: '72%',
  activeDays: 28,
  totalViews: 156
}

export default function ModelRecommendation() {
  const [isRecommending, setIsRecommending] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [selectedModel, setSelectedModel] = useState('neumf')

  const handleRecommend = () => {
    setIsRecommending(true)
    setTimeout(() => {
      setIsRecommending(false)
      setShowResults(true)
    }, 2000)
  }

  const models = [
    { id: 'neumf', name: 'NeuMF', desc: '神经矩阵分解' },
    { id: 'deepfm', name: 'DeepFM', desc: '深度因子分解机' },
    { id: 'mf', name: '矩阵分解', desc: '传统协同过滤' },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">模型推荐</h1>
          <p className="text-gray-500 mt-1">基于你的观看行为，获取个性化视频推荐</p>
        </div>
        <select 
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="px-4 py-2 border border-gray-200 rounded-lg bg-white text-gray-700"
        >
          {models.map(m => (
            <option key={m.id} value={m.id}>{m.name} ({m.desc})</option>
          ))}
        </select>
      </div>

      {/* 用户概览 */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center gap-4">
          <img src={mockUser.avatar} alt={mockUser.name} className="w-16 h-16 rounded-full bg-white/20" />
          <div className="flex-1">
            <h2 className="text-xl font-semibold">{mockUser.name}</h2>
            <p className="text-white/80 text-sm mt-1">{mockUser.level} · {mockUser.interests.join('、')}</p>
          </div>
          <div className="grid grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold">{mockMetrics.watchTime}</p>
              <p className="text-xs text-white/80">本周观看</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{mockMetrics.avgWatchTime}</p>
              <p className="text-xs text-white/80">平均时长</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{mockMetrics.interaction}</p>
              <p className="text-xs text-white/80">互动率</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{mockMetrics.totalViews}</p>
              <p className="text-xs text-white/80">观看总数</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* 左侧：最近观看 */}
        <div className="col-span-2 bg-white rounded-xl border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-indigo-500" />
              <h3 className="font-semibold text-gray-900">最近观看</h3>
            </div>
            <span className="text-sm text-gray-500">共 {mockWatchHistory.length} 个视频</span>
          </div>
          <div className="divide-y divide-gray-50">
            {mockWatchHistory.map((video) => (
              <div key={video.id} className="px-6 py-4 flex items-center gap-4 hover:bg-gray-50 transition-colors">
                <div className="text-3xl">{video.thumbnail}</div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-gray-900 truncate">{video.title}</h4>
                  <p className="text-sm text-gray-500 mt-1">{video.channel} · {video.watchedAt}</p>
                </div>
                <div className="text-right">
                  <span className="text-sm text-gray-600">{video.duration}</span>
                  <div className="w-20 h-1.5 bg-gray-200 rounded-full mt-2">
                    <div 
                      className="h-full bg-indigo-500 rounded-full" 
                      style={{ width: `${video.progress}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧：推荐按钮 + 结果 */}
        <div className="space-y-6">
          {/* 推荐按钮卡片 */}
          <div className="bg-white rounded-xl border border-gray-100 p-6 text-center">
            <div className="w-16 h-16 mx-auto bg-indigo-100 rounded-full flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-indigo-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">AI 智能推荐</h3>
            <p className="text-sm text-gray-500 mb-6">
              基于 {mockUser.name} 的观看历史和偏好，使用 <span className="font-medium text-indigo-600">{models.find(m => m.id === selectedModel)?.name}</span> 模型生成个性化推荐
            </p>
            <button
              onClick={handleRecommend}
              disabled={isRecommending}
              className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                isRecommending 
                  ? 'bg-gray-100 text-gray-400' 
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isRecommending ? (
                <>
                  <div className="w-5 h-5 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin" />
                  分析中...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  获取推荐
                </>
              )}
            </button>
          </div>

          {/* 推荐结果 */}
          {showResults && (
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-indigo-50">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-purple-500" />
                  <h3 className="font-semibold text-gray-900">为你推荐</h3>
                </div>
              </div>
              <div className="divide-y divide-gray-50">
                {mockRecommendations.map((video) => (
                  <div key={video.id} className="px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors cursor-pointer">
                    <div className="text-2xl">{video.thumbnail}</div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 truncate">{video.title}</h4>
                      <p className="text-xs text-gray-500 mt-0.5">{video.channel}</p>
                      <p className="text-xs text-indigo-600 mt-1 flex items-center gap-1">
                        <Star className="w-3 h-3" />
                        {(video.score * 100).toFixed(0)}% 匹配度
                      </p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </div>
                ))}
              </div>
              <div className="px-4 py-3 bg-gray-50 text-center">
                <button className="text-sm text-indigo-600 font-medium hover:text-indigo-700">
                  查看更多推荐
                </button>
              </div>
            </div>
          )}

          {/* 推荐理由说明 */}
          {showResults && (
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4">
              <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-500" />
                推荐理由
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li className="flex items-start gap-2">
                  <span className="text-indigo-500">•</span>
                  基于你近期观看的科技/数码类视频
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-indigo-500">•</span>
                  匹配你的高互动率（85%）特征
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-indigo-500">•</span>
                  考虑视频的完播率和用户评分
                </li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
