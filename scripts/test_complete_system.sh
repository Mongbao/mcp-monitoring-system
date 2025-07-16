#!/bin/bash
# 測試所有 MCP Server 包括 Discord

echo "=== 完整 MCP 監控系統測試 ==="
echo "時間: $(date)"
echo ""

echo "🔧 檢查已安裝的 MCP Server..."
echo ""

# 檢查 Python MCP servers
echo "📊 Python MCP Servers:"
MCP_FILES=(
    "mcp_system_monitor.py"
    "mcp_filesystem_monitor.py" 
    "mcp_network_monitor.py"
    "mcp_log_analyzer.py"
    "mcp_process_monitor.py"
)

for file in "${MCP_FILES[@]}"; do
    if [ -f "/home/bao/mcp_use/$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 未找到"
    fi
done

echo ""
echo "🎮 Discord MCP Server:"
if command -v mcp-discord &> /dev/null; then
    echo "  ✅ mcp-discord 已安裝"
    echo "  📍 位置: $(which mcp-discord)"
else
    echo "  ❌ mcp-discord 未安裝"
fi

echo ""
echo "⚙️ 檢查 MCP 配置..."
if [ -f "/home/bao/mcp_use/.vscode/mcp.json" ]; then
    echo "  ✅ MCP 配置檔案存在"
    
    # 檢查各個 server 配置
    echo "  📋 已配置的 MCP Servers:"
    grep -o '"[^"]*"[[:space:]]*:[[:space:]]*{' /home/bao/mcp_use/.vscode/mcp.json | grep -v '^[[:space:]]*{' | while read -r line; do
        server_name=$(echo "$line" | cut -d'"' -f2)
        echo "    - $server_name"
    done
else
    echo "  ❌ MCP 配置檔案未找到"
fi

echo ""
echo "🌐 檢查 Web 服務..."
if pgrep -f "web_dashboard/mcp_web_server.py" > /dev/null; then
    echo "  ✅ MCP Web 服務正在執行"
    
    if netstat -ln 2>/dev/null | grep -q ":8003"; then
        echo "  ✅ Web 服務埠 8003 正在監聽"
    else
        echo "  ⚠️ Web 服務埠 8003 未監聽"
    fi
else
    echo "  ❌ MCP Web 服務未執行"
fi

echo ""
echo "🔗 檢查 Apache 配置..."
if [ -f "/etc/apache2/sites-available/bao-ssl.conf" ]; then
    echo "  ✅ Apache 配置檔案存在"
    
    if apache2ctl -t &>/dev/null; then
        echo "  ✅ Apache 配置語法正確"
    else
        echo "  ⚠️ Apache 配置有語法錯誤"
    fi
else
    echo "  ❌ Apache 配置檔案未找到"
fi

echo ""
echo "📱 Discord MCP Server 功能說明:"
echo "  🎯 主要功能:"
echo "    - Discord 伺服器管理"
echo "    - 訊息發送和接收"
echo "    - 頻道管理"
echo "    - 成員資訊查詢"
echo "    - Bot 狀態監控"
echo ""
echo "  ⚙️ 設定方式:"
echo "    1. 在 Discord Developer Portal 建立 Bot"
echo "    2. 獲取 Bot Token"
echo "    3. 在 MCP 配置中設定 Discord Token"
echo "    4. 邀請 Bot 到您的 Discord 伺服器"
echo ""

echo "🎉 MCP 監控系統整合完成！"
echo ""
echo "📊 系統元件:"
echo "  - 5 個 Python 監控 MCP Servers"
echo "  - 1 個 Discord 整合 MCP Server" 
echo "  - Web 監控儀表板"
echo "  - Apache 反向代理"
echo "  - 自動化部署腳本"
echo ""
echo "🌍 存取方式:"
echo "  - 本地: http://localhost:8003"
echo "  - 網路: https://bao.mengwei710.com"
echo "  - VS Code MCP: 透過 .vscode/mcp.json 配置"
