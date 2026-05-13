import { useState } from 'react'
import { 
  Heart, MessageCircle, Share2, Bookmark, 
  Play, Volume2, VolumeX, Eye, ThumbsUp,
  Clock, TrendingUp, Filter, Grid, List
} from 'lucide-react'

// Mock 视频数据
const mockVideos = [
  { 
    id: 1, 
    title: 'MacBook Pro M4 深度测评：性能炸裂！',
    author: '科技美学',
    authorAvatar: '🍎',
    likes: '32.5万',
    comments: '8921',
    shares: '2.3万',
    views: '156万',
    description: 'M4 芯片性能实测，太强了！🔥 #苹果 #MacBook #测评',
    duration: '18:32',
    category: '科技',
    publishedAt: '2小时前',
    tags: ['MacBook', '苹果', '测评']
  },
  { 
    id: 2, 
    title: 'iPhone 16 Pro 夜景拍摄对比三星S25 Ultra',
    author: '数码研究所',
    authorAvatar: '📱',
    likes: '18.7万',
    comments: '5632',
    shares: '1.1万',
    views: '89万',
    description: '夜景拍照谁更强？实拍对比告诉你答案 📸 #iPhone16 #手机摄影',
    duration: '12:45',
    category: '数码',
    publishedAt: '昨天',
    tags: ['iPhone', '拍照', '对比']
  },
  { 
    id: 3, 
    title: 'GPT-5 能取代程序员吗？我测试了一个月',
    author: 'AI前线',
    authorAvatar: '🤖',
    likes: '45.2万',
    comments: '1.2万',
    shares: '5.6万',
    views: '234万',
    description: 'AI 编程能力大挑战，结果出乎意料... 👨‍💻 #ChatGPT #AI #程序员',
    duration: '25:18',
    category: 'AI',
    publishedAt: '3天前',
    tags: ['AI', '编程', 'ChatGPT']
  },
  { 
    id: 4, 
    title: '索尼 WH-1000XM6 降噪耳机体验报告',
    author: '音频发烧友',
    authorAvatar: '🎧',
    likes: '9.8万',
    comments: '3456',
    shares: '8900',
    views: '45万',
    description: '顶级降噪耳机对比测评，买前必看！🎵 #耳机 #降噪 #索尼',
    duration: '15:20',
    category: '音频',
    publishedAt: '5天前',
    tags: ['耳机', '降噪', '索尼']
  },
  { 
    id: 5, 
    title: '小米15 Ultra 拍照对比佳能R5',
    author: '摄影频道',
    authorAvatar: '📷',
    likes: '27.3万',
    comments: '7823',
    shares: '3.4万',
    views: '178万',
    description: '手机拍照真的能超越单反吗？🏔️ #小米15Ultra #手机摄影 #对比',
    duration: '20:45',
    category: '摄影',
    publishedAt: '1周前',
    tags: ['小米', '拍照', '单反']
  },
  { 
    id: 6, 
    title: 'NVIDIA RTX 5090 性能首测',
    author: '硬件星球',
    authorAvatar: '🎮',
    likes: '52.1万',
    comments: '2.1万',
    shares: '8.9万',
    views: '312万',
    description: '史上最强显卡！游戏性能实测 🔥 #RTX5090 #NVIDIA #显卡',
    duration: '22:10',
    category: '硬件',
    publishedAt: '2周前',
    tags: ['显卡', 'NVIDIA', '游戏']
  },
]

export default function VideoFeed() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedCategory, setSelectedCategory] = useState('全部')
  const [likedVideos, setLikedVideos] = useState<number[]>([])
  const [savedVideos, setSavedVideos] = useState<number[]>([])
  const [isMuted, setIsMuted] = useState(false)

  const categories = ['全部', '科技', '数码', 'AI', '音频', '摄影', '硬件']

  const filteredVideos = selectedCategory === '全部' 
    ? mockVideos 
    : mockVideos.filter(v => v.category === selectedCategory)

  const toggleLike = (id: number) => {
    setLikedVideos(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const toggleSave = (id: number) => {
    setSavedVideos(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-full">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">视频推荐</h1>
          <p className="text-gray-500 mt-1">个性化视频推荐，基于你的观看偏好</p>
        </div>
        <div className="flex items-center gap-4">
          {/* 分类筛选 */}
          <div className="flex items-center gap-2 bg-white rounded-lg p-1 border border-gray-200">
            {categories.slice(0, 5).map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  selectedCategory === cat 
                    ? 'bg-indigo-600 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
          {/* 视图切换 */}
          <div className="flex items-center gap-1 bg-white rounded-lg p-1 border border-gray-200">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'grid' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'list' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
          {/* 静音控制 */}
          <button 
            onClick={() => setIsMuted(!isMuted)}
            className="p-2 bg-white rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50"
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* 推荐统计 */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Eye className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">1.2M</p>
              <p className="text-sm text-gray-500">总播放量</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-pink-100 rounded-lg">
              <ThumbsUp className="w-5 h-5 text-pink-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">185K</p>
              <p className="text-sm text-gray-500">总点赞数</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Clock className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">8.5h</p>
              <p className="text-sm text-gray-500">观看时长</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">72%</p>
              <p className="text-sm text-gray-500">完播率</p>
            </div>
          </div>
        </div>
      </div>

      {/* 视频列表 */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-3 gap-6">
          {filteredVideos.map((video) => (
            <div key={video.id} className="bg-white rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group">
              {/* 视频封面 */}
              <div className="relative aspect-video bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
                <span className="text-6xl">{video.authorAvatar}</span>
                <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                  {video.duration}
                </div>
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                  <div className="w-14 h-14 bg-white/90 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Play className="w-6 h-6 text-gray-800 ml-1" />
                  </div>
                </div>
              </div>
              {/* 视频信息 */}
              <div className="p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-lg flex-shrink-0">
                    {video.authorAvatar}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 line-clamp-2 leading-snug">
                      {video.title}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">{video.author}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-500 mt-2">
                      <span>{video.views} 播放</span>
                      <span>·</span>
                      <span>{video.publishedAt}</span>
                    </div>
                  </div>
                </div>
                {/* 操作栏 */}
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-50">
                  <div className="flex items-center gap-4">
                    <button 
                      onClick={(e) => { e.stopPropagation(); toggleLike(video.id) }}
                      className={`flex items-center gap-1 text-sm ${likedVideos.includes(video.id) ? 'text-red-500' : 'text-gray-500 hover:text-red-500'}`}
                    >
                      <Heart className={`w-4 h-4 ${likedVideos.includes(video.id) ? 'fill-current' : ''}`} />
                      <span>{video.likes}</span>
                    </button>
                    <button className="flex items-center gap-1 text-sm text-gray-500 hover:text-blue-500">
                      <MessageCircle className="w-4 h-4" />
                      <span>{video.comments}</span>
                    </button>
                    <button className="flex items-center gap-1 text-sm text-gray-500 hover:text-green-500">
                      <Share2 className="w-4 h-4" />
                      <span>{video.shares}</span>
                    </button>
                  </div>
                  <button 
                    onClick={(e) => { e.stopPropagation(); toggleSave(video.id) }}
                    className={`p-1.5 rounded-lg ${savedVideos.includes(video.id) ? 'bg-yellow-100 text-yellow-600' : 'text-gray-400 hover:bg-gray-100'}`}
                  >
                    <Bookmark className={`w-4 h-4 ${savedVideos.includes(video.id) ? 'fill-current' : ''}`} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredVideos.map((video) => (
            <div key={video.id} className="bg-white rounded-xl border border-gray-100 p-4 flex gap-4 hover:shadow-md transition-shadow cursor-pointer group">
              {/* 缩略图 */}
              <div className="relative w-64 aspect-video bg-gradient-to-br from-gray-700 to-gray-900 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-5xl">{video.authorAvatar}</span>
                <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                  {video.duration}
                </div>
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors rounded-lg flex items-center justify-center">
                  <div className="w-12 h-12 bg-white/90 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Play className="w-5 h-5 text-gray-800 ml-0.5" />
                  </div>
                </div>
              </div>
              {/* 信息 */}
              <div className="flex-1 py-1">
                <h3 className="font-medium text-gray-900 line-clamp-2">{video.title}</h3>
                <p className="text-sm text-gray-500 mt-1">{video.description}</p>
                <div className="flex items-center gap-4 mt-3">
                  <span className="text-sm text-gray-600">{video.author}</span>
                  <span className="text-sm text-gray-400">·</span>
                  <span className="text-sm text-gray-500">{video.views} 播放</span>
                  <span className="text-sm text-gray-400">·</span>
                  <span className="text-sm text-gray-500">{video.publishedAt}</span>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  {video.tags.map(tag => (
                    <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
              {/* 操作 */}
              <div className="flex flex-col items-center justify-center gap-3">
                <button 
                  onClick={(e) => { e.stopPropagation(); toggleLike(video.id) }}
                  className={`p-2 rounded-lg ${likedVideos.includes(video.id) ? 'bg-red-50 text-red-500' : 'text-gray-400 hover:bg-gray-100'}`}
                >
                  <Heart className={`w-5 h-5 ${likedVideos.includes(video.id) ? 'fill-current' : ''}`} />
                </button>
                <button className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg">
                  <Bookmark className="w-5 h-5" />
                </button>
                <button className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg">
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
