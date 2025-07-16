#!/bin/bash
# MCP 監控系統 Apache 部署腳本

echo "=== MCP 監控系統 Apache 部署 ==="
echo ""

# 檢查是否為 root 用戶
if [ "$EUID" -ne 0 ]; then
    echo "❌ 請使用 sudo 執行此腳本"
    echo "使用方法: sudo ./deploy_apache.sh"
    exit 1
fi

echo "📋 部署步驟："
echo "1. 複製 Apache 配置檔案"
echo "2. 啟用 Apache 模組"
echo "3. 啟用新站台"
echo "4. 設定 systemd 服務"
echo "5. 重新載入服務"
echo ""

# 1. 複製 Apache 配置檔案
echo "📁 複製 Apache 配置檔案..."
cp /home/bao/mcp_use/config/bao-ssl.conf /etc/apache2/sites-available/
chown root:root /etc/apache2/sites-available/bao-ssl.conf
chmod 644 /etc/apache2/sites-available/bao-ssl.conf
echo "✅ Apache 配置檔案已複製"

# 2. 啟用必要的 Apache 模組
echo "🔧 啟用 Apache 模組..."
a2enmod ssl
a2enmod proxy
a2enmod proxy_http
a2enmod headers
a2enmod rewrite
echo "✅ Apache 模組已啟用"

# 3. 啟用新站台
echo "🌐 啟用新站台..."
a2ensite bao-ssl
echo "✅ bao-ssl 站台已啟用"

# 4. 設定 systemd 服務
echo "⚙️ 設定 systemd 服務..."
cp /home/bao/mcp_use/config/mcp-web.service /etc/systemd/system/
chown root:root /etc/systemd/system/mcp-web.service
chmod 644 /etc/systemd/system/mcp-web.service
systemctl daemon-reload
systemctl enable mcp-web.service
echo "✅ systemd 服務已設定"

# 5. 重新載入 Apache
echo "🔄 重新載入 Apache..."
systemctl reload apache2
if [ $? -eq 0 ]; then
    echo "✅ Apache 已重新載入"
else
    echo "⚠️ Apache 重新載入時出現警告，請檢查配置"
fi

# 6. 啟動 MCP Web 服務
echo "🚀 啟動 MCP Web 服務..."
systemctl start mcp-web.service
if [ $? -eq 0 ]; then
    echo "✅ MCP Web 服務已啟動"
else
    echo "❌ MCP Web 服務啟動失敗"
fi

echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 服務狀態："
echo "- Apache: $(systemctl is-active apache2)"
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
