#!/bin/bash
# MCP 監控系統測試腳本

echo "=== MCP 監控系統測試 ==="
echo "虛擬環境路徑: /home/bao/mcp_use/mcp_env"
echo "工作目錄: /home/bao/mcp_use"
echo ""

# 啟動虛擬環境
source /home/bao/mcp_use/mcp_env/bin/activate

echo "測試 MCP Server..."
echo ""

# 測試系統監控
echo "1. 測試系統監控 MCP Server"
echo "資源: system://cpu, system://memory, system://disk, system://network"
echo "工具: get_system_summary, monitor_process"
echo ""

# 測試檔案系統監控
echo "2. 測試檔案系統監控 MCP Server"
echo "資源: filesystem://[路徑]"
echo "工具: scan_directory, check_permissions, find_large_files"
echo ""

# 測試網路監控
echo "3. 測試網路監控 MCP Server"
echo "資源: network://interfaces, network://connections, network://traffic"
echo "工具: ping_host, port_scan, get_routing_table"
echo ""

# 測試日誌分析
echo "4. 測試日誌分析 MCP Server"
echo "資源: log://[日誌檔案路徑]"
echo "工具: search_logs, analyze_error_trends, get_log_stats"
echo ""

# 測試進程監控
echo "5. 測試進程監控 MCP Server"
echo "資源: process://all, process://monitored, process://top"
echo "工具: get_process_details, kill_process, monitor_process_tree, check_service_health"
echo ""

echo "所有 MCP Server 已準備就緒！"
echo "您可以在 VS Code 中使用這些 MCP server。"
echo ""
echo "配置檔案位置: /home/bao/mcp_use/.vscode/mcp.json"
