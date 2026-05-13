import { useState } from 'react';
import { BarChart3, Table, Network, Clock, TrendingUp, Search, Users, Package, GitBranch, Activity, Filter, Target, RefreshCw, Play, ChevronRight, Download, Grid3X3 } from 'lucide-react';

const edaAnalyses = [
  { id: 'user_distribution', name: '用户分布', icon: Users, image: '/images/user_distribution.png', stats: [{ label: '用户总数', value: '128,456' }, { label: '活跃用户', value: '89,234' }] },
  { id: 'item_distribution', name: '物品分布', icon: Package, image: '/images/item_distribution.png', stats: [{ label: '物品总数', value: '45,892' }, { label: '热门物品', value: '2,341' }] },
  { id: 'interaction_distribution', name: '交互分布', icon: Activity, image: '/images/interaction_distribution.png', stats: [{ label: '总交互量', value: '5.2M' }, { label: '点击量', value: '3.8M' }] },
  { id: 'correlation', name: '相关性分析', icon: GitBranch, image: '/images/correlation.png', stats: [{ label: '高相关', value: '23对' }, { label: '中等相关', value: '67对' }] },
  { id: 'temporal', name: '时序分析', icon: Clock, image: '/images/temporal_analysis.png', stats: [{ label: '日均增长', value: '+2.3%' }, { label: '周期长度', value: '7天' }] },
  { id: 'category', name: '类目分析', icon: Grid3X3, image: '/images/category_coverage.png', stats: [{ label: '类目总数', value: '128' }, { label: '覆盖率', value: '94.5%' }] },
  { id: 'user_segmentation', name: '用户分群', icon: Target, image: '/images/user_segmentation.png', stats: [{ label: '分群数量', value: '5个' }, { label: '高价值用户', value: '12.3%' }] },
  { id: 'funnel', name: '漏斗分析', icon: Filter, image: '/images/funnel_analysis.png', stats: [{ label: '曝光量', value: '12.5M' }, { label: '转化率', value: '3.1%' }] },
  { id: 'retention', name: '留存分析', icon: TrendingUp, image: '/images/retention_analysis.png', stats: [{ label: '次日留存', value: '45.6%' }, { label: '7日留存', value: '23.4%' }] },
  { id: 'search', name: '搜索分析', icon: Search, image: '/images/search_analysis.png', stats: [{ label: '日均搜索', value: '89,234' }, { label: '无结果率', value: '2.3%' }] },
  { id: 'social_network', name: '社交网络', icon: Network, image: '/images/social_network.png', stats: [{ label: '关系数', value: '2.3M' }, { label: 'KOL数量', value: '1,234' }] },
  { id: 'table_relationship', name: '表关系', icon: Table, image: '/images/table_relationship.png', stats: [{ label: '表数量', value: '8个' }, { label: '关联关系', value: '12个' }] },
];

export default function EDA() {
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>('user_distribution');
  const [isRunning, setIsRunning] = useState(false);

  const handleRunAnalysis = () => {
    setIsRunning(true);
    setTimeout(() => setIsRunning(false), 3000);
  };

  const currentAnalysis = edaAnalyses.find((a) => a.id === selectedAnalysis);

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">EDA 分析</h1>
          <p className="text-gray-500 mt-1">探索性数据分析，可视化数据洞察</p>
        </div>
        <button
          onClick={handleRunAnalysis}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {isRunning ? '分析中...' : '运行分析'}
        </button>
      </div>

      <div className="flex gap-6">
        {/* 左侧分析列表 */}
        <div className="w-80 flex-shrink-0">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h2 className="font-semibold text-gray-900 mb-4">分析类型</h2>
            <div className="space-y-2">
              {edaAnalyses.map((analysis) => (
                <button
                  key={analysis.id}
                  onClick={() => setSelectedAnalysis(analysis.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                    selectedAnalysis === analysis.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50 border border-transparent'
                  }`}
                >
                  <div className={`p-2 rounded-lg ${selectedAnalysis === analysis.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}>
                    <analysis.icon className="w-5 h-5" />
                  </div>
                  <span className="flex-1 font-medium text-gray-900">{analysis.name}</span>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧内容 */}
        <div className="flex-1">
          {currentAnalysis ? (
            <div className="space-y-6">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 bg-blue-100 text-blue-600 rounded-xl">
                    <currentAnalysis.icon className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{currentAnalysis.name}</h2>
                    <p className="text-gray-500">数据分析详情</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-6">
                  {currentAnalysis.stats.map((stat, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-500">{stat.label}</p>
                      <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-900">分析图表</h3>
                  <button className="flex items-center gap-1 text-blue-600 hover:text-blue-700">
                    <Download className="w-4 h-4" />
                    下载图片
                  </button>
                </div>
                <img
                  src={currentAnalysis.image}
                  alt={currentAnalysis.name}
                  className="w-full rounded-lg"
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full bg-white rounded-xl border border-gray-200">
              <BarChart3 className="w-16 h-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900">选择分析类型</h3>
              <p className="text-gray-500 mt-1">从左侧选择一个分析类型查看详细结果</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
