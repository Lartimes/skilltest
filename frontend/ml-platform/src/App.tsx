import { HashRouter, Routes, Route, NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, FileText, Cpu, BarChart3, Sparkles,
  Menu, X, Play
} from 'lucide-react'
import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import DataCleaning from './pages/DataCleaning'
import ModelTraining from './pages/ModelTraining'
import EDA from './pages/EDA'
import ModelStatus from './pages/ModelStatus'
import ModelRecommendation from './pages/ModelRecommendation'
import VideoFeed from './pages/VideoFeed'

const navItems = [
  { path: '/dashboard', label: '首页', icon: LayoutDashboard },
  { path: '/cleaning', label: '数据清洗', icon: FileText },
  { path: '/training', label: '建模', icon: Cpu },
  { path: '/eda', label: 'EDA分析', icon: BarChart3 },
  { path: '/status', label: '模型状态', icon: Sparkles },
  { path: '/recommendation', label: '模型推荐', icon: Sparkles },
  { path: '/video', label: '视频推荐', icon: Play },
]

function App() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <HashRouter>
      <div className="min-h-screen bg-gray-50">
        {/* 顶部导航 */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-6 sticky top-0 z-50">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="lg:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-gray-900 hidden sm:block">ML Platform</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-gray-600 hidden sm:block">系统正常</span>
            </div>
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full" />
          </div>
        </header>

        <div className="flex">
          {/* 侧边栏 */}
          <aside 
            className={`
              fixed lg:static inset-y-0 left-0 z-40
              w-56 bg-white border-r border-gray-200
              transform transition-transform duration-200 ease-out
              ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
              lg:block
            `}
          >
            <nav className="p-3 space-y-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-3 py-2.5 rounded-lg
                    transition-colors cursor-pointer
                    ${isActive 
                      ? 'bg-indigo-50 text-indigo-700' 
                      : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  <span className="font-medium">{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </aside>

          {/* 内容区域 */}
          <main className="flex-1 min-h-[calc(100vh-4rem)] overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/cleaning" element={<DataCleaning />} />
              <Route path="/training" element={<ModelTraining />} />
              <Route path="/eda" element={<EDA />} />
              <Route path="/status" element={<ModelStatus />} />
              <Route path="/recommendation" element={<ModelRecommendation />} />
              <Route path="/video" element={<VideoFeed />} />
            </Routes>
          </main>
        </div>

        {/* 移动端遮罩 */}
        {isOpen && (
          <div 
            className="fixed inset-0 bg-black/50 z-30 lg:hidden"
            onClick={() => setIsOpen(false)}
          />
        )}
      </div>
    </HashRouter>
  )
}

export default App
