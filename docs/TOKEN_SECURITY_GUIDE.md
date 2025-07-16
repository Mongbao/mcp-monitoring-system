# Token 和 ID 安全管理指南

## 概覽
所有敏感的 token 和 ID 現在都已移動到環境變數檔案中，以提高安全性並防止意外暴露在版本控制中。

## 檔案結構

### `.env` (實際機密資訊)
- 包含真實的 token 和 ID
- **已被 git 排除**，不會上傳到 GitHub
- 僅存在於本地開發環境

### `.env.example` (範例檔案)
- 包含環境變數的範例格式
- 不包含真實機密資訊
- **包含在 git 中**，作為設定指南

### `.vscode/mcp.json.example` (範例設定)
- 包含 MCP 設定的範例格式
- 使用 `${VAR}` 佔位符表示環境變數
- **包含在 git 中**，作為設定指南

### `.vscode/mcp.json` (實際設定)
- 包含真實的 MCP 設定
- **已被 git 排除**，需要手動設定

## 設定步驟

### 1. 複製範例檔案
```bash
# 複製 .env 範例
cp .env.example .env

# 複製 MCP 設定範例  
cp .vscode/mcp.json.example .vscode/mcp.json
```

### 2. 填入真實值
編輯 `.env` 檔案，將佔位符替換為實際的 token 和 ID：

```bash
# Discord Integration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_discord_guild_id_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here

# GitHub Integration  
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here
```

### 3. 更新 MCP 設定
編輯 `.vscode/mcp.json` 檔案，將 `${VAR}` 佔位符替換為實際值。

## 安全功能

### Git 排除
`.gitignore` 已更新以排除：
- `.env` 和相關環境檔案
- `.vscode/mcp.json` 實際設定檔案
- 同時保留範例檔案供參考

### Python 整合
Discord 監控腳本已更新為使用 `python-dotenv`：
```python
from dotenv import load_dotenv
load_dotenv('/home/bao/mcp_use/.env')
```

## 注意事項

1. **永遠不要**將包含真實 token 的檔案推送到 GitHub
2. 定期輪換 token 以提高安全性
3. 確保 `.env` 檔案權限適當 (chmod 600)
4. 新團隊成員需要設定自己的 `.env` 檔案

## 驗證設定
運行以下命令確認設定正確：
```bash
# 測試 Discord 整合
python discord_integration/mcp_discord_system_monitor.py

# 測試 GitHub MCP
# (在 VS Code 中測試 MCP 功能)
```
