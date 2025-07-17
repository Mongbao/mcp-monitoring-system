# CLAUDE.md

此文件為 Claude Code (claude.ai/code) 在此程式庫中工作時提供指導。

## 重要設定

**請使用中文與我對話**。這個專案完全使用中文開發，包括程式碼註解、使用者介面、文件和所有溝通都應該使用中文。

**Python 虛擬環境設定**：此專案預設使用位於 `/home/bao/mcp_use/mcp_env/` 的虛擬環境。所有 Python 相關指令都應該在此虛擬環境中執行。

**Root 權限指令處理**：當需要執行需要 root 權限的指令時（如 systemctl、systemd 相關操作），請提供完整指令讓使用者手動執行，而不是直接嘗試執行。

## 專案概述

這是一個使用 FastAPI 構建的綜合系統監控應用程式，具備即時系統指標、Discord 整合和現代化網頁儀表板。系統提供 CPU、記憶體、磁碟使用率、進程、網路連線和系統服務的監控，並具有自動警報和 Discord 通知功能。

## 常用開發指令

### 執行應用程式
```bash
# 開發模式（熱重新載入）- 預設使用虛擬環境
cd /home/bao/mcp_use
source mcp_env/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# 生產模式服務啟動（需要 root 權限）
# 請手動執行以下指令：
# sudo systemctl start mcp-web.service
# sudo systemctl start mcp-discord-monitor.service
```

### 測試
```bash
# 啟用虛擬環境（如果尚未啟用）
cd /home/bao/mcp_use
source mcp_env/bin/activate

# 執行測試套件
pytest tests/

# 測試特定元件
pytest tests/test_discord_monitor.py
pytest tests/test_models.py

# 測試 API 端點
curl http://localhost:8003/api/system
curl http://localhost:8003/api/logs?limit=10
```

### 服務管理
```bash
# 檢查服務狀態（無需 root 權限）
systemctl status mcp-web.service
systemctl status mcp-discord-monitor.service

# 檢視服務日誌（無需 root 權限）
journalctl -u mcp-web.service -f
journalctl -u mcp-discord-monitor.service -f

# 程式碼變更後重新啟動服務（需要 root 權限）
# 請手動執行以下指令：
# sudo systemctl restart mcp-web.service
# sudo systemctl restart mcp-discord-monitor.service

# 停止服務（需要 root 權限）
# 請手動執行以下指令：
# sudo systemctl stop mcp-web.service
# sudo systemctl stop mcp-discord-monitor.service
```

## 架構概述

### 核心應用程式結構
- **`app/main.py`**: FastAPI 應用程式進入點，包含中介軟體、路由和排程器啟動
- **`app/api/routes/`**: 按功能組織的模組化 API 端點（系統、進程、日誌、服務等）
- **`app/api/models/`**: 用於請求/回應驗證和型別檢查的 Pydantic 資料模型
- **`app/core/`**: 商業邏輯，包括監控類別和任務排程
- **`discord_integration/`**: 獨立的 Discord 機器人，具備自動報告功能

### 關鍵設計模式
- **監控器模式**: 基礎監控類別（`app/core/monitors/base.py`）與針對不同系統元件的專門實作
- **依賴注入**: FastAPI 的依賴系統用於服務管理和配置
- **檔案式配置**: 使用 JSON 檔案儲存排程和閾值，而非資料庫
- **模組化路由**: 每個監控領域都有自己的路由模組和資料模型

### 資料流架構
1. **即時指標**: 系統監控器透過 psutil 和系統指令收集資料
2. **API 層**: FastAPI 路由透過 RESTful 端點暴露指標
3. **前端儀表板**: 具備即時資料更新和主題支援的單頁應用程式
4. **Discord 整合**: Discord 通知和警報的自動排程系統
5. **警報管理**: 儲存在 `data/alert_thresholds.json` 的可配置閾值

## 關鍵配置檔案

### 服務配置
- **`config/mcp-web.service`**: 主要網頁應用程式的 Systemd 服務
- **`config/mcp-discord-monitor.service`**: Discord 整合的 Systemd 服務
- **`data/alert_thresholds.json`**: 系統警報閾值（CPU、記憶體、磁碟使用率限制）
- **`data/schedules.json`**: Discord 報告排程配置

### 環境設定
- **虛擬環境**: 位於 `mcp_env/`，已安裝所有依賴套件
- **Python 需求**: 定義在 `requirements.txt`（FastAPI 0.104.1+、psutil 等）
- **系統依賴**: 需要 systemd 進行服務管理

## API 端點組織

### 監控 APIs
- **`/api/system`**: CPU、記憶體、磁碟和負載平均指標
- **`/api/processes`**: 進程列表與 CPU/記憶體使用率及控制操作
- **`/api/network`**: 網路介面統計和連線資訊
- **`/api/services`**: 系統服務狀態和管理
- **`/api/filesystem`**: 磁碟使用率和掛載點資訊
- **`/api/logs`**: 系統日誌檢索，支援級別和類型篩選

### 管理 APIs
- **`/api/thresholds`**: 警報閾值配置（GET/POST）
- **`/api/schedule`**: Discord 報告排程管理
- **`/api/discord`**: Discord 機器人狀態和訊息發送
- **`/api/health`**: 應用程式健康檢查和指標

## 前端架構

### 儀表板功能
- **單頁應用程式**: 在 `app/static/templates/dashboard.html` 中的綜合監控儀表板
- **主題系統**: 使用 CSS 變數的深色/淺色模式支援
- **即時更新**: 基於 JavaScript 的即時資料獲取與錯誤處理
- **虛擬滾動**: 針對大型進程列表的效能最佳化渲染
- **響應式設計**: 基於網格的佈局與行動裝置最佳化

### JavaScript 架構
- **VirtualScrollList 類別**: 用於效能的自訂虛擬滾動實作
- **主題管理**: 具備 localStorage 持久化的動態主題切換
- **API 客戶端**: 具備超時和錯誤處理的集中式 `fetchData()` 函數
- **通知系統**: 用於使用者回饋的吐司式通知

## Discord 整合詳情

### 雙重整合方式
- **API 整合**: 透過網頁介面存取的 Discord 路由（`/api/discord/`）
- **獨立監控器**: 獨立的 Discord 服務（`discord_integration/mcp_discord_monitor.py`）
- **排程報告**: 可配置的自動系統狀態報告
- **警報通知**: 系統閾值突破的即時 Discord 警報

### Discord 訊息功能
- **豐富格式**: 表情符號指示器和格式化系統狀態
- **自動排程**: 類似 Cron 的定期報告排程
- **手動觸發**: 透過網頁介面的隨需系統報告
- **錯誤通知**: 系統問題和監控失敗的 Discord 警報

## 開發工作流程考量

### 程式碼風格和慣例
- **中文本地化**: 所有使用者介面文字、註解和文件使用中文
- **型別安全**: 整個程式碼庫中的綜合 Python 型別提示
- **Pydantic 模型**: 強大的資料驗證和序列化
- **錯誤處理**: 優雅的降級和綜合錯誤回應

### 測試策略
- **元件測試**: 個別監控器和模型測試
- **整合測試**: FastAPI 應用程式和端點測試
- **匯入驗證**: 基本匯入和實例化測試
- **手動測試**: 用於 API 驗證的 Curl 指令

### 常見除錯方法
- **服務日誌**: 使用 `journalctl -u mcp-web.service -f` 進行即時除錯
- **API 測試**: 直接 curl 測試端點進行快速驗證
- **前端控制台**: 瀏覽器開發者工具進行 JavaScript 除錯
- **Discord 日誌**: 監控 Discord 服務日誌以解決整合問題

## 重要實作注意事項

### 系統權限要求
- **日誌存取**: 某些日誌功能需要 `systemd-journal` 和 `adm` 群組成員資格
- **服務控制**: 進程管理功能需要適當的系統權限
- **檔案權限**: `data/` 目錄中的配置檔案需要寫入存取權限

### 效能考量
- **虛擬滾動**: 針對大型進程列表實作以保持 UI 響應性
- **優雅降級**: 當真實指標不可用時，系統回退到範例資料
- **記憶體管理**: 為了效率而進行記憶體內處理，無持久性儲存
- **API 超時**: 為外部依賴配置超時和重試邏輯

### 生產部署注意事項
- **Systemd 整合**: 配置自動啟動和重新啟動的服務
- **反向代理**: 設計在 Apache/nginx 代理後運作
- **資源監控**: 監控系統本身的自我監控功能
- **警報配置**: 透過網頁介面進行閾值管理

## 中文對話要求

當與我對話時，請：
- 使用繁體中文回應
- 理解這是一個完全中文化的專案
- 程式碼註解和變數名稱使用中文是正常的
- 所有使用者介面和錯誤訊息都應該是中文
- 技術討論也請使用中文進行