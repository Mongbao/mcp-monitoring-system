#!/bin/bash
# MCP 監控系統測試腳本

echo "=== MCP 監控系統測試 ==="
echo ""

# 檢查 Python 虛擬環境
echo "🐍 檢查 Python 虛擬環境..."
if [ -f "/home/bao/mcp_use/mcp_env/bin/python" ]; then
    PYTHON_VERSION=$(/home/bao/mcp_use/mcp_env/bin/python --version 2>&1)
    echo "✅ Python 虛擬環境: $PYTHON_VERSION"
else
    echo "❌ Python 虛擬環境未找到"
fi

# 檢查必要套件
echo ""
echo "📦 檢查必要套件..."
cd /home/bao/mcp_use
source mcp_env/bin/activate 2>/dev/null

if python -c "import psutil" 2>/dev/null; then
    echo "✅ psutil 套件已安裝"
else
    echo "❌ psutil 套件未安裝"
    echo "   請執行: pip install psutil"
fi

# 檢查 MCP server 檔案
echo ""
echo "📄 檢查 MCP Server 檔案..."
MCP_FILES=(
    "mcp_system_monitor.py"
    "mcp_filesystem_monitor.py"
    "mcp_network_monitor.py"
    "mcp_log_analyzer.py"
    "mcp_process_monitor.py"
    "web_dashboard/mcp_web_server.py"
)

for file in "${MCP_FILES[@]}"; do
    if [ -f "/home/bao/mcp_use/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file 未找到"
    fi
done

# 檢查配置檔案
echo ""
echo "⚙️ 檢查配置檔案..."
if [ -f "/home/bao/mcp_use/.vscode/mcp.json" ]; then
    echo "✅ MCP 配置檔案"
else
    echo "❌ MCP 配置檔案未找到"
fi

if [ -f "/home/bao/mcp_use/bao-ssl.conf" ]; then
    echo "✅ Apache 配置檔案"
else
    echo "❌ Apache 配置檔案未找到"
fi

# 檢查 Apache 配置 (需要 sudo)
echo ""
echo "🌐 檢查 Apache 配置..."
if [ -f "/etc/apache2/sites-available/bao-ssl.conf" ]; then
    echo "✅ Apache 站台配置已安裝"
    if a2ensite -q bao-ssl 2>/dev/null; then
        echo "✅ bao-ssl 站台已啟用"
    else
        echo "⚠️ bao-ssl 站台未啟用"
    fi
else
    echo "❌ Apache 站台配置未安裝"
    echo "   請執行: sudo ./deploy_apache.sh"
fi

# 檢查 systemd 服務
echo ""
echo "🔧 檢查 systemd 服務..."
if [ -f "/etc/systemd/system/mcp-web.service" ]; then
    echo "✅ MCP Web 服務已安裝"
    
    SERVICE_STATUS=$(systemctl is-active mcp-web 2>/dev/null)
    if [ "$SERVICE_STATUS" = "active" ]; then
        echo "✅ MCP Web 服務正在執行"
    else
        echo "⚠️ MCP Web 服務未執行 (狀態: $SERVICE_STATUS)"
    fi
else
    echo "❌ MCP Web 服務未安裝"
fi

# 檢查埠
echo ""
echo "🔌 檢查埠使用情況..."
if netstat -ln 2>/dev/null | grep -q ":8003 "; then
    echo "✅ 埠 8003 正在使用中"
else
    echo "⚠️ 埠 8003 未使用"
fi

if netstat -ln 2>/dev/null | grep -q ":443 "; then
    echo "✅ 埠 443 (HTTPS) 正在使用中"
else
    echo "⚠️ 埠 443 (HTTPS) 未使用"
fi

echo ""
echo "🎯 測試建議："
echo ""

if [ ! -f "/etc/apache2/sites-available/bao-ssl.conf" ]; then
    echo "1. 執行部署腳本: sudo ./deploy_apache.sh"
fi

if ! python -c "import psutil" 2>/dev/null; then
    echo "2. 安裝 Python 套件: pip install psutil"
fi

echo "3. 測試 Web 介面: http://localhost:8003"
echo "4. 檢查服務狀態: sudo systemctl status mcp-web"
echo "5. 檢視日誌: sudo journalctl -u mcp-web -f"

echo ""
echo "完成測試！"
