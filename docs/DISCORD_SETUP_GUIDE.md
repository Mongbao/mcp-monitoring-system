# Discord MCP Server 設定指南

## 🎮 Discord MCP Server 已成功整合！

### 📋 當前狀態
✅ Discord MCP Server 已安裝並配置
✅ 在 VS Code MCP 配置中已添加
✅ 可透過 `mcp-discord` 命令執行

### 🔧 Discord Bot 設定步驟

#### 1. 建立 Discord Application
1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 點擊 "New Application"
3. 輸入應用程式名稱 (例如: "MCP Monitor Bot")
4. 點擊 "Create"

#### 2. 建立 Bot
1. 在左側選單點擊 "Bot"
2. 點擊 "Add Bot"
3. 自訂 Bot 名稱和頭像
4. 在 "Token" 區段點擊 "Copy" 複製 Bot Token
5. **重要**: 保持 Token 安全，不要分享給其他人

#### 3. 設定 Bot 權限
在 "Bot Permissions" 區段勾選：
- ✅ Send Messages
- ✅ Send Messages in Threads  
- ✅ Embed Links
- ✅ Attach Files
- ✅ Read Message History
- ✅ Use Slash Commands

#### 4. 邀請 Bot 到伺服器
1. 在左側選單點擊 "OAuth2" > "URL Generator"
2. 在 "Scopes" 勾選 "bot"
3. 在 "Bot Permissions" 勾選上述權限
4. 複製生成的 URL 並在瀏覽器中開啟
5. 選擇要邀請 Bot 的伺服器

### 🛠️ MCP 配置設定

#### 方法 1: 直接編輯環境變數
編輯 `/home/bao/mcp_use/.vscode/mcp.json`：

```json
"discord": {
  "command": "mcp-discord",
  "args": [],
  "cwd": "/home/bao/mcp_use",
  "env": {
    "DISCORD_TOKEN": "您的_BOT_TOKEN_在這裡",
    "DISCORD_GUILD_ID": "您的_伺服器_ID",
    "DISCORD_CHANNEL_ID": "預設_頻道_ID"
  }
}
```

#### 方法 2: 使用 Discord MCP 內建認證
1. 執行 `mcp-discord`
2. 使用內建指令進行登入和設定

### 📱 Discord MCP Server 功能

#### 🔍 可用資源
- `discord://servers` - Discord 伺服器列表
- `discord://channels` - 頻道資訊
- `discord://users` - 使用者資訊
- `discord://messages` - 訊息歷史

#### 🛠️ 可用工具
- `send_message` - 發送訊息到指定頻道
- `create_channel` - 建立新頻道
- `manage_roles` - 管理使用者角色
- `get_server_info` - 獲取伺服器資訊
- `moderate_content` - 內容審核功能

### 🚀 使用範例

#### 發送系統監控警報到 Discord
```javascript
// 透過 MCP 呼叫
await mcp.callTool("discord", "send_message", {
  channel: "system-alerts",
  message: "🚨 系統 CPU 使用率超過 90%",
  embed: true
});
```

#### 獲取伺服器狀態
```javascript
const serverInfo = await mcp.readResource("discord://servers");
console.log(serverInfo);
```

### 🔧 故障排除

#### 常見問題
1. **Token 無效**: 確認 Bot Token 正確且沒有過期
2. **權限不足**: 檢查 Bot 在伺服器中的權限
3. **連線失敗**: 確認網路連線和防火牆設定

#### 除錯命令
```bash
# 檢查 Discord MCP Server 狀態
mcp-discord --help

# 測試連線
mcp-discord --test-connection

# 檢視日誌
journalctl -f | grep discord
```

### 📊 整合到監控系統

Discord MCP Server 現在已整合到您的監控系統中：

1. **自動警報**: 系統監控異常時自動發送 Discord 通知
2. **狀態查詢**: 透過 Discord 指令查詢系統狀態  
3. **遠端控制**: 透過 Discord 執行基本的系統管理指令
4. **團隊協作**: 多人可透過 Discord 接收監控通知

### 🎯 下一步
1. 設定您的 Discord Bot Token
2. 測試 Discord 訊息發送功能
3. 建立自動化警報規則
4. 自訂 Discord 通知格式

您的 MCP 監控系統現在具備完整的 Discord 整合功能！
