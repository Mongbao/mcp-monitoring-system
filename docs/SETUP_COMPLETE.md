# MCP 監控系統設定完成

## 已建立的檔案

✅ **MCP Server 檔案：**
- `mcp_system_monitor.py` - 系統資源監控 (CPU, 記憶體, 磁碟)
- `mcp_filesystem_monitor.py` - 檔案系統監控
- `mcp_network_monitor.py` - 網路監控
- `mcp_log_analyzer.py` - 日誌分析
- `mcp_process_monitor.py` - 進程監控

✅ **配置檔案：**
- `.vscode/mcp.json` - VS Code MCP 配置
- `requirements.txt` - Python 相依套件
- `README.md` - 完整使用說明

✅ **輔助檔案：**
- `test_mcp_servers.sh` - 測試腳本
- `test_basic.py` - 基本功能測試

## 虛擬環境

✅ 虛擬環境已建立在：`/home/bao/mcp_use/mcp_env/`

## 使用方法

### 1. 啟動虛擬環境並安裝套件
```bash
cd /home/bao/mcp_use
source mcp_env/bin/activate
pip install psutil
# 如果有 MCP 套件可用，也可安裝：
# pip install mcp
```

### 2. 測試 MCP Server
```bash
# 執行測試腳本
./test_mcp_servers.sh

# 或測試基本功能
python test_basic.py

# 手動測試系統監控
python -m mcp_system_monitor
```

### 3. 在 VS Code 中使用
MCP server 配置已經設定在 `.vscode/mcp.json` 中，您可以直接在 VS Code 中使用。

## 監控功能

### 系統監控
- CPU 使用率
- 記憶體使用情況
- 磁碟空間
- 網路 I/O

### 檔案系統監控
- 目錄掃描
- 檔案權限檢查
- 大檔案搜尋

### 網路監控
- 網路介面狀態
- 連線監控
- Ping 測試
- 埠掃描

### 日誌分析
- 日誌搜尋
- 錯誤趨勢分析
- 日誌統計

### 進程監控
- 進程詳細資訊
- 進程樹監控
- 服務健康檢查

## 環境變數配置

可以透過修改 `.vscode/mcp.json` 中的環境變數來自訂監控範圍：

- `WATCH_PATHS` - 檔案系統監控路徑
- `MONITOR_INTERFACES` - 網路介面
- `LOG_PATHS` - 日誌檔案路徑
- `MONITOR_PROCESSES` - 要監控的進程

您的 MCP 監控系統已經完全設定好了！
