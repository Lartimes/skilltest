import { Database, Brain, BarChart3, Activity, Sparkles, TrendingUp, Users, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';

const modules = [
  { path: '/data', label: '数据清洗', icon: Database, desc: '数据上传与清洗规则配置', color: 'bg-blue-500' },
  { path: '/modeling', label: '模型建模', icon: Brain, desc: '创建与训练推荐模型', color: 'bg-purple-500' },
  { path: '/eda', label: 'EDA分析', icon: BarChart3, desc: '探索性数据分析与可视化', color: 'bg-green-500' },
  { path: '/status', label: '模型状态', icon: Activity, desc: '实时监控模型运行状态', color: 'bg-orange-500' },
  { path: '/recommend', label: '模型推荐', icon: Sparkles, desc: '智能推荐最优模型', color: 'bg-pink-500' },
];

const recentModels = [
  { name: 'DeepFM 推荐模型', status: '运行中', accuracy: '89.2%', time: '2小时前' },
  { name: '矩阵分解模型', status: '已完成', accuracy: '75.6%', time: '1天前' },
  { name: '神经矩阵分解', status: '训练中', accuracy: '-', time: '进行中' },
];

export default function Dashboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">模型中台首页</h1>
        <p className="text-gray-500 mt-1">欢迎使用 ML Platform 模型中台管理系统</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard icon={Brain} label="在线模型" value="3" trend="+1 本周" color="purple" />
        <StatCard icon={Database} label="数据总量" value="1.2M" trend="+15%" color="blue" />
        <StatCard icon={Users} label="日均请求" value="12.5K" trend="+8%" color="green" />
        <StatCard icon={TrendingUp} label="平均准确率" value="87.2%" trend="+2.3%" color="orange" />
      </div>

      {/* 功能模块 */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">功能模块</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {modules.map((mod) => (
            <Link key={mod.path} to={mod.path} className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-all group">
              <div className={`w-12 h-12 rounded-lg ${mod.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <mod.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">{mod.label}</h3>
              <p className="text-sm text-gray-500 mt-1">{mod.desc}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* 最近模型 & 快捷操作 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-900">最近模型</h2>
            <Layers className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {recentModels.map((model, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{model.name}</p>
                  <p className="text-xs text-gray-500">{model.time}</p>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-medium ${model.status === '训练中' ? 'text-blue-500' : 'text-green-500'}`}>
                    {model.status}
                  </p>
                  <p className="text-xs text-gray-500">{model.accuracy}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">快捷操作</h2>
          <div className="grid grid-cols-2 gap-3">
            <Link to="/data" className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              <Database className="w-5 h-5 text-blue-500 mb-2" />
              <p className="text-sm font-medium text-gray-900">上传数据</p>
            </Link>
            <Link to="/modeling" className="p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
              <Brain className="w-5 h-5 text-purple-500 mb-2" />
              <p className="text-sm font-medium text-gray-900">新建模型</p>
            </Link>
            <Link to="/eda" className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
              <BarChart3 className="w-5 h-5 text-green-500 mb-2" />
              <p className="text-sm font-medium text-gray-900">数据分析</p>
            </Link>
            <Link to="/recommend" className="p-4 bg-pink-50 rounded-lg hover:bg-pink-100 transition-colors">
              <Sparkles className="w-5 h-5 text-pink-500 mb-2" />
              <p className="text-sm font-medium text-gray-900">模型推荐</p>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, trend, color }: { icon: any; label: string; value: string; trend: string; color: string }) {
  const colorMap: Record<string, { bg: string; text: string }> = {
    purple: { bg: 'bg-purple-100', text: 'text-purple-500' },
    blue: { bg: 'bg-blue-100', text: 'text-blue-500' },
    green: { bg: 'bg-green-100', text: 'text-green-500' },
    orange: { bg: 'bg-orange-100', text: 'text-orange-500' },
  };
  const colors = colorMap[color] || colorMap.blue;

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colors.bg}`}>
          <Icon className={`w-6 h-6 ${colors.text}`} />
        </div>
        <span className="text-xs text-green-500 bg-green-50 px-2 py-1 rounded-full">{trend}</span>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}
