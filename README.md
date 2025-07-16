# 🖥️ MCP 監控系統

[![CI](https://github.com/username/mcp-monitoring-system/workflows/CI/badge.svg)](https://github.com/username/mcp-monitoring-system/actions)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/username/mcp-monitoring-system)](https://github.com/username/mcp-monitoring-system/issues)
[![GitHub stars](https://img.shields.io/github/stars/username/mcp-monitoring-system)](https://github.com/username/mcp-monitoring-system/stargazers)

一個基於 Model Context Protocol (MCP) 的先進監控平台，整合了 **系統監控**、**Web 儀表板** 和 **Discord 通知** 功能。

## ✨ 主要特色

- 🔄 **即時系統監控** - CPU、記憶體、磁碟、網路狀態
- 📊 **Web 儀表板** - 響應式設計，支援桌面和行動裝置
- 🤖 **Discord 整合** - 自動通知和互動式查詢
- ⚙️ **進程監控** - 詳細的進程資源使用分析
- 📁 **檔案系統監控** - 磁碟使用率和 I/O 監控
- 🌐 **網路監控** - 流量統計和連線狀態
- 📋 **日誌分析** - 系統日誌自動分析和警報

## 📁 專案結構

```
mcp_use/
├── README.md                    # 專案說明
├── requirements.txt             # Python 依賴套件
├── mcp_env/                     # Python 虛擬環境
├── .vscode/
│   └── mcp.json                 # VS Code MCP 配置
├── mcp_servers/                 # MCP 監控 servers
│   ├── mcp_system_monitor.py    # 系統監控 MCP server
│   ├── mcp_filesystem_monitor.py # 檔案系統監控
│   ├── mcp_network_monitor.py   # 網路監控
│   ├── mcp_log_analyzer.py      # 日誌分析
│   └── mcp_process_monitor.py   # 進程監控
├── web_dashboard/               # Web 儀表板
│   └── mcp_web_server.py        # Web 儀表板服務
├── discord_integration/         # Discord 整合
│   ├── mcp_discord_system_monitor.py # Discord 監控主程式
│   ├── start_discord_monitor.sh # Discord 監控啟動腳本
│   └── test_discord_simple_api.sh # Discord API 測試
├── config/                      # 配置檔案
│   ├── bao-ssl.conf            # Apache 反向代理配置
│   ├── mcp-web.service         # Web 服務 systemd 配置
│   └── mcp-discord-monitor.service # Discord 監控服務配置
├── scripts/                     # 部署與測試腳本
│   ├── deploy_apache.sh        # Apache 部署腳本
│   ├── test_complete_system.sh # 完整系統測試
│   ├── test_mcp_servers.sh     # MCP servers 測試
│   └── test_setup.sh           # 設定測試
├── docs/                        # 文件
│   ├── DEPLOYMENT_GUIDE.md     # 部署指南
│   ├── DISCORD_INTEGRATION_COMPLETE.md # Discord 整合完成說明
│   ├── DISCORD_SETUP_GUIDE.md  # Discord 設定指南
│   └── SETUP_COMPLETE.md       # 設定完成說明
└── logs/                        # 日誌檔案
    └── discord_monitor.log      # Discord 監控日誌
```

**環境變數：**
- `WATCH_PATHS` - 要監控的路徑，以逗號分隔 (預設: `/home,/var/log`)

### 3. 網路監控 (mcp_network_monitor.py)
監控網路連線、介面狀態和流量。

**資源：**
- `network://interfaces` - 網路介面狀態
- `network://connections` - 當前網路連線
- `network://traffic` - 網路流量統計

**工具：**
- `ping_host` - Ping 主機測試連通性
- `port_scan` - 掃描主機開放的埠
- `get_routing_table` - 獲取路由表

**環境變數：**
- `MONITOR_INTERFACES` - 要監控的網路介面，以逗號分隔 (預設: `eth0,wlan0`)

### 4. 日誌分析 (mcp_log_analyzer.py)
分析系統日誌檔案，檢測錯誤和異常。

**資源：**
- `log://[日誌檔案路徑]` - 分析指定日誌檔案

**工具：**
- `search_logs` - 在日誌中搜尋特定模式
- `analyze_error_trends` - 分析錯誤趨勢
- `get_log_stats` - 獲取日誌統計資訊

**環境變數：**
- `LOG_PATHS` - 要分析的日誌檔案路徑，以逗號分隔 (預設: `/var/log/syslog,/var/log/auth.log`)

### 5. 進程監控 (mcp_process_monitor.py)
監控系統進程和服務狀態。

**資源：**
- `process://all` - 所有進程概覽
- `process://monitored` - 監控進程狀態
- `process://top` - CPU/記憶體使用率最高的進程

**工具：**
- `get_process_details` - 獲取進程詳細資訊
- `kill_process` - 終止進程
- `monitor_process_tree` - 監控進程樹
- `check_service_health` - 檢查服務健康狀態

**環境變數：**
- `MONITOR_PROCESSES` - 要監控的進程名稱，以逗號分隔 (預設: `apache2,nginx,mysql`)

## 使用方法

### 在 VS Code 中使用

MCP server 配置檔案位於 `.vscode/mcp.json`，您可以直接在 VS Code 中使用這些 server。

### 直接執行測試

```bash
# 執行測試腳本
./test_mcp_servers.sh

# 或者手動測試單個 server
source mcp_env/bin/activate
python -m mcp_system_monitor
```

## 配置檔案

### .vscode/mcp.json
包含所有 MCP server 的配置，每個 server 都有自己的環境變數設定。

### requirements.txt
列出所有必需的 Python 套件。

## 安全注意事項

1. 某些功能需要 root 權限 (如終止其他使用者的進程)
2. 檔案系統監控可能會存取敏感目錄
3. 網路監控功能可能需要特殊權限
4. 建議在受控環境中使用

## 故障排除

### 權限錯誤
如果遇到權限錯誤，請確保：
- 使用者有足夠權限存取監控的檔案/目錄
- 對於系統日誌，可能需要將使用者加入相關群組

### 套件缺失
確保已安裝所有相依套件：
```bash
pip install -r requirements.txt
```

### 網路功能問題
某些網路監控功能可能需要：
- `ping` 命令可用
- `ip` 命令可用 (iproute2 套件)

## 自訂擴展

您可以透過以下方式擴展系統：

1. 修改環境變數來調整監控範圍
2. 在各個 server 中添加新的資源或工具
3. 建立新的 MCP server 來監控其他面向

## 授權

此專案採用 MIT 授權條款。
