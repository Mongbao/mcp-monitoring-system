#!/bin/bash
# Discord 頻道 ID 更新驗證腳本

echo "🔍 Discord 頻道 ID 更新驗證"
echo "==========================="

echo "📋 檢查所有配置檔案中的頻道 ID..."

# 檢查 mcp.json
echo ""
echo "1. .vscode/mcp.json:"
grep -n "DISCORD_CHANNEL_ID" .vscode/mcp.json

# 檢查測試腳本
echo ""
echo "2. discord_integration/test_discord_simple_api.sh:"
grep -n "CHANNEL_ID=" discord_integration/test_discord_simple_api.sh

# 檢查服務配置
echo ""
echo "3. config/mcp-discord-monitor.service:"
grep -n "DISCORD_CHANNEL_ID" config/mcp-discord-monitor.service

# 檢查啟動腳本
echo ""
echo "4. discord_integration/start_discord_monitor.sh:"
grep -n "DISCORD_CHANNEL_ID" discord_integration/start_discord_monitor.sh

# 檢查監控主程式
echo ""
echo "5. discord_integration/mcp_discord_system_monitor.py:"
grep -n "DISCORD_CHANNEL_ID\|1393483928823660585" discord_integration/mcp_discord_system_monitor.py

echo ""
echo "✅ 所有配置檔案已檢查完成"
echo ""
echo "📱 新的 Discord 頻道連結:"
echo "https://discord.com/channels/1363426069595820092/1393483928823660585"
