# 貢獻指南

感謝你對 MCP 監控系統的興趣！我們歡迎各種形式的貢獻。

## 如何貢獻

### 回報 Bug
1. 檢查 [Issues](../../issues) 確認問題尚未被回報
2. 使用 Bug 回報模板創建新的 issue
3. 提供詳細的重現步驟和環境資訊

### 建議新功能
1. 檢查現有的功能請求
2. 使用功能請求模板創建新的 issue
3. 詳細描述功能的用途和實現方式

### 提交代碼
1. Fork 此倉庫
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 創建 Pull Request

## 開發環境設置

### 前置需求
- Python 3.8+
- Linux/Unix 系統（推薦 Ubuntu）

### 安裝步驟
```bash
# 克隆倉庫
git clone https://github.com/your-username/mcp_use.git
cd mcp_use

# 創建虛擬環境
python3 -m venv mcp_env
source mcp_env/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 安裝系統依賴
sudo apt-get install python3-psutil
```

### 運行測試
```bash
# 測試 MCP 伺服器
python mcp_servers/mcp_system_monitor.py --test
python web_dashboard/test_process_monitor.py

# 啟動 Web 儀表板
python web_dashboard/mcp_web_server.py
```

## 代碼風格

### Python 代碼風格
- 遵循 PEP 8 風格指南
- 使用 4 個空格縮排
- 行長度限制為 127 字符
- 使用有意義的變數和函數名稱

### 提交訊息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

類型：
- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文件變更
- `style`: 格式變更
- `refactor`: 代碼重構
- `test`: 測試相關
- `chore`: 雜項變更

例子：
```
feat(web): 新增進程監控橫向卡片顯示

- 將進程監控改為橫向卡片式佈局
- 新增響應式設計支援行動裝置
- 優化 CSS grid 佈局

Closes #123
```

## 專案結構

```
mcp_use/
├── mcp_servers/          # MCP 伺服器模組
├── web_dashboard/        # Web 儀表板
├── scripts/             # 工具腳本
├── config/              # 配置檔案
├── docs/                # 文件
├── discord_integration/ # Discord 整合
└── requirements.txt     # Python 依賴
```

## 聯絡方式

如有任何問題，歡迎：
- 創建 Issue
- 發起 Discussion
- 聯絡維護者

感謝你的貢獻！ 🎉
