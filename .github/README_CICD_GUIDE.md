# GitHub CI/CD 流水线使用指南

## 一、什么是 CI/CD？

**CI/CD** = **Continuous Integration（持续集成）** + **Continuous Deployment（持续部署）**

简单来说，CI/CD 就是让你的代码在**提交到 GitHub 后自动完成**：
- ✅ 代码检查（有没有语法错误）
- ✅ 自动运行测试（功能是否正常）
- ✅ 自动构建（打包成可运行的应用）
- ✅ 自动部署（发布到网站/服务器）

---

## 二、你的 CI/CD 流水线流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        完整 CI/CD 流程                                │
└─────────────────────────────────────────────────────────────────────┘

  提交代码 (git push)
         │
         ▼
┌─────────────────┐
│  代码检查 (lint) │  ← 检查代码语法、风格
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  后端代码检查 (backend)  │  ← Python 代码检查
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│  运行测试 (test) │  ← 自动运行所有测试
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  构建 (build)   │  ← 打包前端代码
└────────┬────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────────┐
│  部署预览 (PR)   │    │  部署生产 (master)   │
│  (Pull Request) │    │  (正式版本)          │
└─────────────────┘    └─────────────────────┘
```

---

## 三、如何使用（一步步来）

### 第一步：把 CI/CD 文件推送到 GitHub

```bash
# 1. 添加并提交这些文件
git add .github/
git commit -m "Add CI/CD pipeline"
git push origin master
```

### 第二步：配置必要的密钥（Secrets）

你需要配置一些密码信息（不能公开的密钥），步骤如下：

#### 1. 注册 Vercel 账号（用于部署前端）
- 访问 https://vercel.com
- 用 GitHub 账号登录
- 创建新项目，导入你的 `bishe` 仓库

#### 2. 获取 Vercel 的密钥
在 Vercel 项目 Settings → General → Regions 获取：
- `VERCEL_TOKEN` - 访问令牌
- `VERCEL_ORG_ID` - 组织 ID  
- `VERCEL_PROJECT_ID` - 项目 ID

#### 3. 在 GitHub 设置密钥
1. 进入你的仓库：https://github.com/lartimes/bishe/settings
2. 左侧菜单选择 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下密钥：

| 密钥名称 | 值来源 |
|---------|--------|
| `VERCEL_TOKEN` | Vercel 账号设置 |
| `VERCEL_ORG_ID` | Vercel 项目设置 |
| `VERCEL_PROJECT_ID` | Vercal 项目设置 |
| `DOCKERHUB_USERNAME` | Docker Hub 用户名 |
| `DOCKERHUB_TOKEN` | Docker Hub 访问令牌 |

---

## 四、不同的触发场景

### 场景 1：提交代码到 master 分支
```
代码 push → 自动检查 → 自动测试 → 自动构建 → 自动部署到生产环境
```
✅ **全自动！** 推完代码等几分钟，网站就更新了。

### 场景 2：创建 Pull Request（合并请求）
```
创建 PR → 自动检查 → 自动测试 → 自动构建 → 部署预览链接
```
✅ PR 页面会自动生成一个**预览链接**，你可以预览改动效果。

### 场景 3：打标签发布版本
```bash
git tag v1.0.0
git push origin v1.0.0
```
✅ 会触发 Docker 镜像构建和发布。

### 场景 4：手动触发
在 GitHub Actions 页面点击 **Run workflow** 按钮即可手动运行。

---

## 五、在 GitHub 查看流水线运行状态

1. 进入你的仓库：https://github.com/lartimes/bishe
2. 点击 **Actions** 标签
3. 你会看到所有运行记录：
   - ✅ 绿色 = 成功
   - ❌ 红色 = 失败
   - 🟡 黄色 = 运行中

---

## 六、常见问题

### Q1: 流水线失败了怎么办？
点击失败的流水线 → 查看日志 → 找到红色错误信息 → 修复本地代码 → 重新 push

### Q2: 可以跳过某些检查吗？
可以临时禁用，但**不推荐**：
```bash
git commit -m "fix: 修复bug [skip ci]"
```

### Q3: 部署需要多久？
- 代码检查 + 测试：约 2-3 分钟
- 构建 + 部署：约 3-5 分钟
- 总计：约 5-10 分钟

---

## 七、查看更多细节

关于每个步骤的具体说明，请参考：
- [workflows/ci-cd.yml](workflows/ci-cd.yml) - 主 CI/CD 流水线配置
- [workflows/docker.yml](workflows/docker.yml) - Docker 构建配置

---

## 八、推荐的学习顺序

1. **先尝试**：提交一个小改动到 master，看流水线自动运行
2. **创建 PR**：体验预览部署功能
3. **查看日志**：理解每个步骤在做什么
4. **自定义配置**：根据需要修改 yml 文件

---

有任何问题欢迎随时问我！
