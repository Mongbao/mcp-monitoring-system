# GitHub 倉庫設置指南

## 在 GitHub 上創建倉庫

1. **登入 GitHub** 並點擊 "New repository"

2. **倉庫設定**：
   - Repository name: `mcp-monitoring-system`
   - Description: `🖥️ 先進的系統監控平台 - 具備 Web 儀表板、Discord 整合和即時監控功能`
   - Visibility: Public（或 Private）
   - ✅ Add a README file（取消勾選，我們已經有了）
   - ✅ Add .gitignore（取消勾選，我們已經有了）
   - ✅ Choose a license（取消勾選，我們已經有了）

3. **創建倉庫後，在本地連接遠程倉庫**：
```bash
cd /home/bao/mcp_use
git remote add origin https://github.com/YOUR_USERNAME/mcp-monitoring-system.git
git branch -M main
git push -u origin main
```

## 推薦的 GitHub 設定

### 1. 倉庫設定
在 GitHub 倉庫的 Settings 頁面：

**General**：
- 啟用 Issues
- 啟用 Discussions
- 啟用 Projects
- 設定 Default branch 為 `main`

**Security**：
- 啟用 Dependency graph
- 啟用 Dependabot alerts
- 啟用 Dependabot security updates

### 2. 分支保護規則
在 Settings > Branches 設定 `main` 分支保護：
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators

### 3. Labels 設定
建議創建以下標籤：

**類型標籤**：
- `bug` (紅色) - Bug 回報
- `enhancement` (藍色) - 功能增強
- `documentation` (綠色) - 文件相關
- `question` (紫色) - 問題討論

**優先度標籤**：
- `priority: high` (紅色) - 高優先度
- `priority: medium` (橙色) - 中優先度
- `priority: low` (黃色) - 低優先度

**狀態標籤**：
- `status: in-progress` (藍色) - 進行中
- `status: needs-review` (橙色) - 需要審查
- `status: blocked` (紅色) - 被阻擋

### 4. GitHub Pages（可選）
如果要公開展示文件：
1. 到 Settings > Pages
2. Source: Deploy from a branch
3. Branch: main / docs

## 工作流程建議

### 1. 開發流程
```bash
# 1. 創建功能分支
git checkout -b feature/new-monitoring-feature

# 2. 開發和測試
# ... 進行開發 ...

# 3. 提交變更
git add .
git commit -m "feat(monitor): 新增 CPU 溫度監控功能"

# 4. 推送分支
git push origin feature/new-monitoring-feature

# 5. 在 GitHub 上創建 Pull Request
```

### 2. 版本發布
```bash
# 1. 更新版本號
git tag -a v1.0.0 -m "Release v1.0.0: 初始版本發布"

# 2. 推送標籤
git push origin v1.0.0

# 3. 在 GitHub 上創建 Release
```

## 自動化設定

我們已經設定了以下自動化流程：

### CI/CD Pipeline (`.github/workflows/ci.yml`)
- ✅ 多版本 Python 測試 (3.8-3.12)
- ✅ 代碼品質檢查 (flake8)
- ✅ 安全掃描 (bandit, safety)
- ✅ 自動測試執行

### 問題模板
- ✅ Bug 回報模板
- ✅ 功能請求模板
- ✅ Pull Request 模板

## 維護建議

1. **定期更新依賴**：
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **代碼品質**：
   ```bash
   flake8 .
   bandit -r .
   ```

3. **文件更新**：
   - 保持 README.md 更新
   - 更新 API 文件
   - 記錄重大變更

4. **安全性**：
   - 定期檢查 GitHub Security 建議
   - 更新安全相關依賴
   - 審查 Pull Requests

## 推廣建議

1. **添加徽章到 README**：
   ```markdown
   ![CI](https://github.com/username/mcp-monitoring-system/workflows/CI/badge.svg)
   ![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
   ![License](https://img.shields.io/badge/license-MIT-green.svg)
   ```

2. **創建 Demo 影片或截圖**

3. **撰寫部落格文章**

4. **參與相關社群討論**

---

完成這些設定後，你的 MCP 監控系統將有一個專業的 GitHub 倉庫！ 🚀
