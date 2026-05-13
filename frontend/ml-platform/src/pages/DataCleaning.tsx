import { useState } from 'react';
import { Database, Play, CheckCircle, Clock, RefreshCw, FileText } from 'lucide-react';

const dataSources = [
  { id: 'user_features', name: '用户特征数据', file: 'user_features.csv', rows: 10000, cols: 5, status: 'ready' },
  { id: 'item_features', name: '物品特征数据', file: 'item_features.csv', rows: 5000, cols: 16, status: 'ready' },
  { id: 'rec_inter', name: '推荐交互数据', file: 'rec_inter.csv', rows: 100000, cols: 12, status: 'ready' },
  { id: 'social_network', name: '社交网络数据', file: 'social_network.csv', rows: 25000, cols: 2, status: 'ready' },
  { id: 'src_inter', name: '搜索交互数据', file: 'src_inter.csv', rows: 80000, cols: 9, status: 'ready' },
];

const cleaningSteps = [
  { id: 'fix_types', name: '修正数据类型', enabled: true },
  { id: 'drop_duplicates', name: '删除重复行', enabled: true },
  { id: 'handle_missing', name: '处理缺失值', enabled: true },
  { id: 'filter_invalid', name: '过滤无效数据', enabled: true },
  { id: 'drop_missing_cols', name: '删除高缺失列', enabled: false },
  { id: 'handle_outliers', name: '处理异常值', enabled: true },
];

interface CleaningTask {
  id: string;
  datasetName: string;
  startTime: string;
  status: 'running' | 'completed' | 'failed';
  originalRows: number;
  finalRows: number;
  duplicatesRemoved: number;
}

export default function DataCleaning() {
  const [tasks, setTasks] = useState<CleaningTask[]>([
    { id: 'task-001', datasetName: '推荐交互数据', startTime: '2026-05-07 15:30:22', status: 'completed', originalRows: 100000, finalRows: 98500, duplicatesRemoved: 1200 },
    { id: 'task-002', datasetName: '用户特征数据', startTime: '2026-05-07 14:20:10', status: 'completed', originalRows: 10000, finalRows: 9850, duplicatesRemoved: 150 },
  ]);
  const [runningTask, setRunningTask] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [currentResult, setCurrentResult] = useState<CleaningTask | null>(null);

  const handleClean = (datasetName: string, originalRows: number) => {
    setRunningTask(true);
    setTimeout(() => {
      const result: CleaningTask = {
        id: `task-${Date.now()}`,
        datasetName,
        startTime: new Date().toLocaleString(),
        status: 'completed',
        originalRows,
        finalRows: Math.floor(originalRows * 0.985),
        duplicatesRemoved: Math.floor(originalRows * 0.012),
      };
      setTasks([result, ...tasks]);
      setRunningTask(false);
      setCurrentResult(result);
      setShowResult(true);
    }, 3000);
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">数据清洗</h1>
          <p className="text-gray-500 mt-1">扫描并清洗后端存储的源数据文件</p>
        </div>
        <button className="flex items-center px-4 py-2 text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">
          <RefreshCw className="w-4 h-4 mr-2" />
          刷新文件列表
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 源文件列表 */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900 flex items-center">
                <Database className="w-5 h-5 mr-2 text-blue-600" />
                数据源列表
              </h2>
            </div>
            <div className="divide-y">
              {dataSources.map((source) => (
                <div key={source.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-gray-400 mr-3" />
                    <div>
                      <p className="font-medium text-gray-900">{source.name}</p>
                      <p className="text-sm text-gray-500">{source.file}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm text-gray-900">{source.rows.toLocaleString()} 行</p>
                      <p className="text-xs text-gray-500">{source.cols} 列</p>
                    </div>
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">{source.status}</span>
                    <button
                      onClick={() => handleClean(source.name, source.rows)}
                      disabled={runningTask}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg disabled:opacity-50"
                    >
                      <Play className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 清洗规则 */}
          <div className="mt-6 bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">清洗规则配置</h2>
            </div>
            <div className="p-4 grid grid-cols-2 gap-3">
              {cleaningSteps.map((step) => (
                <label key={step.id} className="flex items-center p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input type="checkbox" defaultChecked={step.enabled} className="w-4 h-4 text-blue-600 rounded" />
                  <span className="ml-3 text-sm text-gray-700">{step.name}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* 右侧 */}
        <div className="space-y-6">
          {runningTask && (
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-blue-500 animate-pulse mr-3" />
                <div>
                  <p className="font-medium text-blue-900">清洗任务执行中...</p>
                  <p className="text-sm text-blue-600">正在处理数据</p>
                </div>
              </div>
              <div className="mt-3 h-2 bg-blue-200 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full animate-pulse w-3/4" />
              </div>
            </div>
          )}

          {showResult && currentResult && (
            <div className="bg-green-50 rounded-xl p-4 border border-green-100">
              <div className="flex items-center mb-4">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                <span className="font-medium text-green-900">清洗完成</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">原始行数</span>
                  <span className="font-medium">{currentResult.originalRows.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">清洗后</span>
                  <span className="font-medium text-green-600">{currentResult.finalRows.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">删除重复</span>
                  <span className="font-medium text-red-500">{currentResult.duplicatesRemoved.toLocaleString()}</span>
                </div>
              </div>
              <button onClick={() => setShowResult(false)} className="mt-4 w-full py-2 text-sm text-green-700 bg-green-100 rounded-lg hover:bg-green-200">
                关闭
              </button>
            </div>
          )}

          {/* 历史任务 */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">清洗任务记录</h2>
            </div>
            <div className="divide-y max-h-96 overflow-y-auto">
              {tasks.map((task) => (
                <div key={task.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-gray-900">{task.datasetName}</p>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                  <p className="text-xs text-gray-500 mb-2">{task.startTime}</p>
                  <div className="flex gap-2">
                    <button className="flex-1 py-1 text-xs text-blue-600 bg-blue-50 rounded hover:bg-blue-100">查看详情</button>
                    <button className="flex-1 py-1 text-xs text-gray-600 bg-gray-50 rounded hover:bg-gray-100">下载报告</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
