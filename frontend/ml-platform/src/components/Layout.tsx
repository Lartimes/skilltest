import { NavLink, Outlet } from 'react-router-dom';
import { Home, Database, Brain, BarChart3, Activity, Sparkles } from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: '首页', icon: Home },
  { path: '/data', label: '数据清洗', icon: Database },
  { path: '/modeling', label: '建模', icon: Brain },
  { path: '/eda', label: 'EDA分析', icon: BarChart3 },
  { path: '/status', label: '模型状态', icon: Activity },
  { path: '/recommend', label: '模型推荐', icon: Sparkles },
];

export default function Layout() {
  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* 侧边栏 */}
      <aside className="w-64 bg-gradient-to-b from-blue-800 to-blue-900 text-white flex flex-col">
        <div className="h-16 flex items-center px-4 border-b border-blue-700/50">
          <Brain className="w-8 h-8 text-blue-300" />
          <span className="ml-3 font-bold text-lg">ML Platform</span>
        </div>
        <nav className="flex-1 py-4">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `flex items-center px-4 py-3 mx-2 rounded-lg transition-all ${
                  isActive ? 'bg-blue-700 text-white' : 'text-blue-200 hover:bg-blue-700/50'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="ml-3">{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      {/* 主内容 */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
