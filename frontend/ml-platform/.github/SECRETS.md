# GitHub Actions CI/CD 配置指南

本指南帮助你配置 ML Platform 前端项目的 CI/CD 流水线。

## 📋 需要的 Secrets 配置

在 GitHub 仓库设置中添加以下 Secrets（Settings → Secrets and variables → Actions）：

### Vercel 部署（推荐）
| Secret 名称 | 说明 | 如何获取 |
|------------|------|---------|
| `VERCEL_TOKEN` | Vercel API Token | [Vercel Dashboard](https://vercel.com/account/tokens) |
| `VERCEL_ORG_ID` | Vercel Organization ID | 运行 `vercel inspect` 获取 |
| `VERCEL_PROJECT_ID` | Vercel Project ID | 在项目设置中获取 |

### GitHub Pages 部署（可选）
| Secret 名称 | 说明 |
|------------|------|
| `GITHUB_TOKEN` | 自动提供，无需手动设置 |

### Docker 部署（可选）
| Secret 名称 | 说明 |
|------------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 访问令牌 |

## 📋 需要的 Variables 配置

在 GitHub 仓库设置中添加以下 Variables（Settings → Secrets and variables → Actions → Variables）：

| Variable 名称 | 说明 | 示例值 |
|--------------|------|--------|
| `DEPLOYMENT_URL` | 部署后的 URL | `ml-platform.vercel.app` |
| `ENABLE_GITHUB_PAGES` | 是否启用 GitHub Pages | `true` |

## 🚀 快速开始

### 方式一：部署到 Vercel（推荐）

1. **Fork 或复制此仓库到你的 GitHub**

2. **在 Vercel 创建一个新项目**
   - 访问 [vercel.com](https://vercel.com)
   - 导入 GitHub 仓库
   - 选择 `frontend/ml-platform` 作为根目录
   - 记下 Organization ID 和 Project ID

3. **配置 GitHub Secrets**
   ```bash
   # 使用 GitHub CLI 设置 secrets
   gh secret set VERCEL_TOKEN -b "your-token"
   gh secret set VERCEL_ORG_ID -b "team_xxx"
   gh secret set VERCEL_PROJECT_ID -b "prj_xxx"
   ```

4. **推送代码触发流水线**
   ```bash
   git add .
   git commit -m "feat: setup CI/CD pipeline"
   git push origin main
   ```

### 方式二：部署到 GitHub Pages

1. **启用 GitHub Pages**
   - 仓库 Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` / `(root)`

2. **配置 Variables**
   ```bash
   gh variable set DEPLOYMENT_URL -b "your-username.github.io"
   gh variable set ENABLE_GITHUB_PAGES -b "true"
   ```

## 📁 流水线文件说明

| 文件 | 说明 |
|------|------|
| `.github/workflows/ci-cd.yml` | 主要 CI/CD 流水线 |
| `.github/workflows/docker.yml` | Docker 镜像构建流水线 |
| `Dockerfile` | 容器镜像定义 |
| `docker-compose.yml` | 本地开发环境 |
| `nginx.conf` | Nginx 配置文件 |

## 🔄 流水线流程

```
代码推送 → 代码检查 → 类型检查 → 单元测试 → 构建应用
                                                      ↓
                                              部署预览 (PR)
                                                      ↓
                                              合并到主分支
                                                      ↓
                                              部署到生产环境
```

## 🛠️ 本地测试

在本地测试 GitHub Actions 工作流：

```bash
# 安装 act
brew install act

# 运行默认 workflow
act

# 运行特定事件
act push
act pull_request
```

## 📊 监控

- 查看 Actions 日志：仓库 → Actions 标签
- 配置通知：Settings → Notifications
- 查看部署历史：Vercel Dashboard 或 GitHub Pages 设置

## ⚠️ 常见问题

### Q: 构建失败？
- 检查 Node.js 版本是否匹配（当前使用 v20）
- 确保 `npm ci` 可以正常运行
- 查看 Actions 日志中的具体错误

### Q: 部署后页面空白？
- 检查 `vite.config.ts` 中的 base 配置
- 确保 GitHub Pages 的 404 处理已启用

### Q: 权限不足？
- 检查 repo 的 Actions permissions 设置
- 确保 secrets 和 variables 已正确配置
