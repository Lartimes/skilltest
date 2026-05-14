# Skill vs Tool vs MCP 区别说明

## 快速对比

| 特性 | Skill | Tool | MCP |
|------|-------|------|-----|
| **定位** | AI 技能扩展包 | 代码执行能力 | 服务连接协议 |
| **本质** | Prompt + 工具封装 | 可执行函数 | 标准化 API 接口 |
| **触发方式** | 自动或手动 | AI 自动调用 | 手动配置 |
| **使用场景** | 领域专家指导 | 自动化执行 | 接入外部服务 |

---

## 1. Skill - AI 的"专业技能包"

### 是什么？
Skill 是给 AI 装备的专业知识包，包含：
- 领域知识（Prompt 模板）
- 工作流程（SOP）
- 最佳实践
- 专用工具调用

### 工作原理
```
用户请求 → AI 检测到相关 Skill → 加载 Skill 知识 → 执行任务
```

### 示例
- `feynman-perspective` - 费曼思维框架
- `git-commit` - 规范提交代码
- `excalidraw-diagram` - 画 Excalidraw 图
- `dockerfile-generator` - 生成 Dockerfile

### 触发方式
- **自动**：AI 根据上下文自动加载相关 Skill
- **手动**：用户通过 `@skill-name` 显式调用

### 代码示例
```json
// Skill 定义结构
{
  "name": "feynman-perspective",
  "description": "费曼思维框架与表达方式",
  "location": "user",
  "commands": ["用费曼视角", "feynman perspective"]
}
```

---

## 2. Tool - 代码执行能力

### 是什么？
Tool 是 AI 可以直接调用的代码函数，执行具体操作：
- 文件读写
- 执行命令
- 搜索代码
- 调用 API

### 工作原理
```
用户请求 → AI 判断需要 Tool → 调用 Tool 函数 → 返回结果
```

### 示例
- `execute_command` - 执行 shell 命令
- `write_to_file` - 写入文件
- `search_content` - 搜索代码内容
- `use_skill` - 调用其他 Skill

### 触发方式
- **自动**：AI 根据任务需求自动判断并调用
- 无需用户显式触发

### 代码示例
```python
# Tool 定义示例
def execute_command(command: str, requires_approval: bool) -> dict:
    """执行系统命令"""
    result = subprocess.run(command, shell=True)
    return {"stdout": result.stdout, "exitCode": result.returncode}
```

---

## 3. MCP (Model Context Protocol) - 服务连接协议

### 是什么？
MCP 是一个标准化协议，用于 AI 连接外部服务和数据源：
- 数据库连接
- 云服务集成
- API 网关
- 企业系统对接

### 工作原理
```
AI → MCP Server → 外部服务 → 返回数据 → AI 处理
```

### 示例
- **Supabase** - PostgreSQL 数据库
- **CloudBase** - 腾讯云服务
- **GitHub** - 代码仓库
- **文件系统** - 本地文件访问

### 触发方式
- **手动配置**：用户在 IDE 中配置并授权
- 不是代码触发，而是服务连接

### 配置示例
```json
// MCP Server 配置
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    }
  }
}
```

---

## 三者关系图

```
┌─────────────────────────────────────────────────────────┐
│                        AI 助手                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐                   │
│  │   Skill     │    │    Tool     │                   │
│  │  (知识包)   │    │  (执行器)   │                   │
│  │             │    │             │                   │
│  │ Prompt 模板 │    │ 读/写文件   │                   │
│  │ 工作流程   │    │ 执行命令   │                   │
│  │ 最佳实践   │    │ 搜索代码   │                   │
│  └──────┬──────┘    └──────┬──────┘                   │
│         │                   │                          │
│         │    ┌───────────────┘                          │
│         │    │                                          │
│         ▼    ▼                                          │
│  ┌─────────────────────────────────┐                    │
│  │         Core AI Engine          │                    │
│  └─────────────────────────────────┘                    │
│                    │                                    │
│                    ▼                                    │
│  ┌─────────────────────────────────┐                    │
│  │            MCP Layer             │                    │
│  │     (服务连接协议层)              │                    │
│  └─────────────────────────────────┘                    │
│                    │                                    │
│         ┌──────────┼──────────┐                        │
│         ▼          ▼          ▼                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ Supabase │ │CloudBase │ │  GitHub  │              │
│  │  数据库   │ │  腾讯云   │ │ 代码仓库 │              │
│  └──────────┘ └──────────┘ └──────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 核心区别总结

| 维度 | Skill | Tool | MCP |
|------|-------|------|-----|
| **做什么** | 教 AI "怎么想" | 教 AI "怎么做" | 帮 AI "连接外部" |
| **内容** | Prompt、流程、知识 | 代码函数 | API 配置 |
| **谁来用** | AI 自动加载/用户调用 | AI 自动调用 | 用户手动配置 |
| **类比** | 教科书 | 工具箱 | 网线接口 |
| **位置** | Prompt 层 | 执行层 | 集成层 |

---

## 什么时候用？

### 用 Skill 当：
- 需要 AI 用特定方法论思考问题
- 需要领域专家知识指导
- 需要标准化工作流程

### 用 Tool 当：
- 需要执行具体代码操作
- 需要读写文件、运行命令
- 需要搜索和分析代码

### 用 MCP 当：
- 需要连接数据库
- 需要接入云服务
- 需要访问外部 API

---

## 实际使用示例

### 场景：分析 Git 冲突

**Skill** → `feynman-perspective`
- 提供费曼的分析框架

**Tool** → `execute_command`, `read_file`, `search_content`
- 执行 git 命令读取冲突
- 读取冲突文件内容

**MCP** → 无需使用（本地操作）

---

## 查看已安装的 Skill

```bash
npx skills check
```

## 创建自定义 Skill

```bash
npx skills init my-custom-skill
```
