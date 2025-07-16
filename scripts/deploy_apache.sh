#!/bin/bash
# MCP 監控系統 Apache 部署腳本 (Port 8003)

echo "=== MCP 監控系統 Apache 部署 (Port 8003) ==="
echo ""

# 檢查是否為 root 用戶
if [ "$EUID" -ne 0 ]; then
    echo "❌ 請使用 sudo 執行此腳本"
    echo "使用方法: sudo ./deploy_apache.sh"
    exit 1
fi

echo "📋 部署步驟："
echo "1. 複製 Apache 配置檔案 (Port 8003)"
echo "2. 啟用 Apache 模組"
echo "3. 設定端口監聽"
echo "4. 啟用新站台"
echo "5. 設定 systemd 服務"
echo "6. 重新載入服務"
echo ""

# 1. 複製 Apache 配置檔案
echo "📁 複製 Apache 配置檔案..."
cp /home/bao/mcp_use/config/mcp-monitor-8003.conf /etc/apache2/sites-available/
chown root:root /etc/apache2/sites-available/mcp-monitor-8003.conf
chmod 644 /etc/apache2/sites-available/mcp-monitor-8003.conf
echo "✅ Apache 配置檔案已複製 (Port 8003)"

# 2. 啟用必要的 Apache 模組
echo "🔧 啟用 Apache 模組..."
a2enmod proxy
a2enmod proxy_http
a2enmod headers
a2enmod rewrite
a2enmod expires
a2enmod deflate
echo "✅ Apache 模組已啟用"

# 3. 設定端口監聽
echo "🔌 設定端口監聽..."
if ! grep -q "Listen 8003" /etc/apache2/ports.conf; then
    echo "Listen 8003" >> /etc/apache2/ports.conf
    echo "✅ 已新增 Port 8003 監聽設定"
else
    echo "✅ Port 8003 監聽設定已存在"
fi

# 4. 停用舊站台並啟用新站台
echo "🌐 管理站台..."
a2dissite bao-ssl 2>/dev/null || echo "  (舊站台不存在，跳過)"
a2ensite mcp-monitor-8003
# 5. 複製 systemd 服務檔案
echo "🔄 設定 systemd 服務..."
cp /home/bao/mcp_use/config/mcp-web.service /etc/systemd/system/
cp /home/bao/mcp_use/config/mcp-discord-monitor.service /etc/systemd/system/
chown root:root /etc/systemd/system/mcp-*.service
chmod 644 /etc/systemd/system/mcp-*.service
echo "✅ systemd 服務檔案已複製"

# 6. 重新載入服務
echo "♻️ 重新載入服務..."
systemctl daemon-reload
systemctl restart apache2
systemctl enable mcp-web
systemctl enable mcp-discord-monitor
echo "✅ 服務已重新載入並設定為開機啟動"

echo ""
echo "🎉 部署完成！"
echo ""
echo "📡 服務狀態檢查："
systemctl is-active apache2 >/dev/null && echo "✅ Apache 服務運行中" || echo "❌ Apache 服務未運行"
systemctl is-enabled apache2 >/dev/null && echo "✅ Apache 開機自啟動已啟用" || echo "❌ Apache 開機自啟動未啟用"
echo ""
echo "🌐 訪問地址："
echo "  - 主要入口 (優化版)：http://localhost:8003/"
echo "  - 標準版：http://localhost:8003/standard/"
echo ""
echo "🚀 啟動 MCP 伺服器："
echo "  sudo systemctl start mcp-web"
echo "  sudo systemctl start mcp-discord-monitor"
echo ""
echo "或使用腳本："
echo "  cd /home/bao/mcp_use"
echo "  ./scripts/start_web.sh          # 標準版 (8080)"
echo "  ./scripts/start_optimized_web.sh # 優化版 (8081)"
echo ""
echo "📝 檢查服務日誌："
echo "  sudo journalctl -u mcp-web -f"
echo "  sudo journalctl -u mcp-discord-monitor -f"
echo "  sudo tail -f /var/log/apache2/mcp_monitor_access.log"
echo "  sudo tail -f /var/log/apache2/mcp_monitor_error.log"
echo "- MCP Web: $(systemctl is-active mcp-web)"
echo ""
echo "🌍 存取網址："
echo "- https://bao.mengwei710.com (需要 DNS 設定)"
echo "- http://localhost:8001 (本地測試)"
echo ""
echo "📋 管理指令："
echo "- 檢查 MCP Web 服務狀態: sudo systemctl status mcp-web"
echo "- 重新啟動 MCP Web 服務: sudo systemctl restart mcp-web"
echo "- 檢視 MCP Web 日誌: sudo journalctl -u mcp-web -f"
echo "- 檢查 Apache 狀態: sudo systemctl status apache2"
echo "- 重新載入 Apache: sudo systemctl reload apache2"
