# MCP 監控系統

一個基於 FastAPI 的現代化系統監控解決方案，整合 Discord 通知和智能排程功能，提供全面的系統資源監控、進程管理、網路監控等功能。

## 🌟 功能特點

- 🖥️ **系統監控**: CPU、記憶體、磁碟使用率即時監控
- 📊 **進程管理**: 進程列表、資源使用情況、進程控制
- 🌐 **網路監控**: 網路連接狀態、流量統計、端口監控
- 📝 **日誌監控**: 系統日誌收集、分析和告警
- 🔧 **服務管理**: 系統服務狀態監控和控制
- 📈 **歷史數據**: 系統指標歷史記錄和趨勢分析
- 🎯 **智能告警**: 可自定義的告警規則和通知
- 🌓 **Web 儀表板**: 現代化的響應式 Web 界面
- 🌙 **深色模式**: 支援明亮/深色主題切換
- 🤖 **Discord 整合**: Discord 機器人通知和報告
- 📅 **智能排程**: 自動化報告排程系統

## 🏗️ 系統架構

該系統採用現代化 FastAPI 架構，包含以下核心組件：

### FastAPI 應用程式
- `app/main.py` - 主應用程式入口
- `app/api/routes/` - API 路由模組
- `app/core/` - 核心業務邏輯
- `app/config.py` - 配置管理

### 核心監控模組
- `app/core/monitors/base.py` - 基礎監控類別
- `app/core/monitors/discord.py` - Discord 監控整合
- `app/core/scheduler.py` - 智能排程管理器

### Web 儀表板
- `app/static/templates/dashboard.html` - 現代化 Web 監控界面
- 響應式設計，支援桌面和移動設備
- 即時數據更新和互動式圖表
- 深色/明亮主題切換

### Discord 整合
- `discord_integration/` - Discord 機器人整合
- 自動化系統報告
- 即時通知和警報

## 🚀 安裝指南

### 系統需求

- Python 3.10+
- Linux/macOS/Windows
- 8GB+ RAM 推薦
- 1GB+ 可用磁碟空間

### 快速開始

1. **克隆儲存庫**
```bash
git clone https://github.com/Mongbao/mcp-monitoring-system.git
cd mcp-monitoring-system
```

2. **建立虛擬環境**
```bash
python -m venv mcp_env
source mcp_env/bin/activate  # Linux/macOS
# 或 Windows: mcp_env\Scripts\activate
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **配置環境變數**
```bash
cp .env.example .env
# 編輯 .env 檔案設定必要參數
```

環境變數說明：
```bash
# Discord 設定
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here

# 應用程式設定
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

5. **啟動服務**
```bash
# 啟動 FastAPI 應用程式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 或使用 Python 直接啟動
python app/main.py
```

6. **訪問 Web 界面**
```
打開瀏覽器訪問: http://localhost:8000
```

## 📖 使用說明

### Web 儀表板

Web 儀表板提供直觀的監控界面：

- **系統概覽**: 顯示 CPU、記憶體、磁碟使用率
- **進程管理**: 檢視和管理系統進程
- **網路監控**: 監控網路連接和流量
- **日誌查看**: 檢視系統日誌和告警
- **服務狀態**: 監控系統服務狀態
- **檔案系統**: 監控磁碟使用情況
- **Discord 監控**: Discord 機器人狀態和控制
- **排程管理**: 自動化報告排程設定

### Discord 整合

系統支援 Discord 機器人整合：

1. **設定 Discord 機器人**
   - 在 Discord 開發者門戶建立機器人
   - 獲取機器人 Token
   - 邀請機器人到您的伺服器

2. **配置環境變數**
   ```bash
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_CHANNEL_ID=your_channel_id_here
   ```

3. **使用功能**
   - 手動發送系統報告
   - 發送自定義訊息
   - 設定自動化排程報告

### 排程功能

支援多種排程類型：

- **每日排程**: 每天固定時間發送報告
- **每週排程**: 每週特定日期發送報告
- **每小時排程**: 每隔指定小時發送報告

排程配置選項：
- 系統資訊包含
- 進程資訊包含
- 網路資訊包含
- 警報資訊包含
- 自定義訊息前綴

## 🛠️ 開發指南

### 專案結構

```
mcp-monitoring-system/
├── app/                    # FastAPI 應用程式
│   ├── main.py            # 主應用程式入口
│   ├── config.py          # 配置管理
│   ├── api/               # API 路由
│   │   ├── models/        # 資料模型
│   │   └── routes/        # API 路由實現
│   ├── core/              # 核心業務邏輯
│   │   ├── monitors/      # 監控模組
│   │   ├── scheduler.py   # 排程管理
│   │   └── utils/         # 工具函數
│   └── static/            # 靜態資源
│       └── templates/     # HTML 模板
├── discord_integration/   # Discord 整合
├── data/                  # 數據儲存
├── tests/                 # 測試檔案
├── config/                # 配置檔案
└── requirements.txt       # 依賴列表
```

### API 端點

主要 API 端點：

- `GET /` - Web 儀表板
- `GET /api/system/info` - 系統資訊
- `GET /api/processes/list` - 進程列表
- `GET /api/network/connections` - 網路連接
- `GET /api/logs/recent` - 最近日誌
- `GET /api/services/status` - 服務狀態
- `GET /api/filesystem/info` - 檔案系統資訊
- `GET /api/discord/status` - Discord 狀態
- `POST /api/discord/send-report` - 發送 Discord 報告
- `GET /api/schedule/` - 排程列表
- `POST /api/schedule/create` - 建立排程

### 新增監控功能

1. **建立新的監控類別**：
```python
# app/core/monitors/new_monitor.py
from .base import BaseMonitor
from typing import Dict, Any

class NewMonitor(BaseMonitor):
    async def get_metrics(self) -> Dict[str, Any]:
        # 實現監控邏輯
        return {
            "metric_name": "value",
            "timestamp": self.get_current_time()
        }
```

2. **註冊 API 路由**：
```python
# app/api/routes/new_monitor.py
from fastapi import APIRouter
from app.core.monitors.new_monitor import NewMonitor

router = APIRouter()
monitor = NewMonitor()

@router.get("/new-metrics")
async def get_new_metrics():
    return await monitor.get_metrics()
```

3. **更新主應用程式**：
```python
# app/main.py
from app.api.routes import new_monitor

app.include_router(new_monitor.router, prefix="/api", tags=["新監控"])
```

### 測試

```bash
# 運行所有測試
python -m pytest tests/ -v

# 運行特定測試
python -m pytest tests/test_basic.py -v

# 運行測試並生成覆蓋率報告
python -m pytest tests/ --cov=app --cov-report=html
```

## 🚀 部署

### 生產環境部署

1. **使用 Gunicorn**：
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **使用 Docker**：
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. **系統服務**：
```ini
# /etc/systemd/system/mcp-monitor.service
[Unit]
Description=MCP Monitoring System
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/mcp-monitoring-system
ExecStart=/opt/mcp-monitoring-system/mcp_env/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 環境配置

生產環境建議配置：

```bash
# 生產環境變數
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Discord 設定
DISCORD_BOT_TOKEN=your_production_bot_token
DISCORD_CHANNEL_ID=your_production_channel_id

# 安全設定
ALLOWED_ORIGINS=["https://your-domain.com"]
ENABLE_GZIP=true
```

## 🔧 故障排除

### 常見問題

1. **應用程式無法啟動**
   - 檢查 Python 版本 (需要 3.10+)
   - 確認所有依賴已安裝
   - 檢查端口是否被占用

2. **Discord 整合問題**
   - 驗證機器人 Token 是否正確
   - 檢查機器人是否有適當權限
   - 確認頻道 ID 是否正確

3. **排程不執行**
   - 檢查排程配置是否正確
   - 確認排程器是否啟動
   - 檢查日誌中的錯誤訊息

4. **權限問題**
   - 確保有足夠的系統權限
   - 檢查檔案權限設定
   - 以適當用戶運行服務

### 日誌檢查

```bash
# 查看應用程式日誌
tail -f logs/app.log

# 查看 Discord 日誌
tail -f logs/discord_monitor.log

# 查看排程日誌
tail -f logs/scheduler.log
```

## 🧪 CI/CD

專案使用 GitHub Actions 進行持續整合：

- **測試**: 自動運行單元測試
- **程式碼品質**: flake8 程式碼檢查
- **安全檢查**: bandit 安全掃描
- **建置測試**: FastAPI 應用程式啟動測試

## 🤝 貢獻指南

歡迎貢獻程式碼！請遵循以下步驟：

1. Fork 此儲存庫
2. 建立功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '新增新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 建立 Pull Request

### 程式碼規範

- 使用 Python 3.10+ 語法
- 遵循 PEP 8 程式碼風格
- 加入適當的文檔字串
- 編寫單元測試
- 使用型別提示

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡方式

- **專案儲存庫**: https://github.com/Mongbao/mcp-monitoring-system
- **問題回報**: https://github.com/Mongbao/mcp-monitoring-system/issues
- **功能請求**: https://github.com/Mongbao/mcp-monitoring-system/discussions

## 🙏 致謝

感謝所有貢獻者和以下專案：

- [FastAPI](https://fastapi.tiangolo.com/) - 現代化 Web 框架
- [psutil](https://github.com/giampaolo/psutil) - 系統監控庫
- [Discord.py](https://discordpy.readthedocs.io/) - Discord API 整合
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 資料驗證
- [Uvicorn](https://www.uvicorn.org/) - ASGI 服務器

---

⭐ 如果這個專案對您有幫助，請給我們一個 Star！