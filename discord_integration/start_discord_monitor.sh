#!/bin/bash
# MCP Discord 監控系統啟動腳本

# 設定工作目錄
cd /home/bao/mcp_use

# 載入環境變數（從 .env 檔案）
source /home/bao/mcp_use/.env

# 啟動虛擬環境
source mcp_env/bin/activate

echo "🎯 MCP Discord 監控系統"
echo "========================"
echo ""
echo "可用選項:"
echo "  1. 立即發送系統報告"
echo "  2. 啟動排程監控 (每15分鐘)"
echo "  3. 測試 Discord 連線"
echo "  4. 檢視監控日誌"
echo ""

read -p "請選擇 (1-4): " choice

case $choice in
    1)
        echo "📊 發送系統報告到 Discord..."
        python discord_integration/mcp_discord_system_monitor.py --once
        ;;
    2)
        echo "⏰ 啟動排程監控..."
        echo "注意: 使用 Ctrl+C 停止監控"
        python discord_integration/mcp_discord_system_monitor.py --schedule
        ;;
    3)
        echo "🔗 測試 Discord API 連線..."
        ./discord_integration/test_discord_simple_api.sh
        ;;
    4)
        echo "📋 最近的監控日誌:"
        if [ -f logs/discord_monitor.log ]; then
            tail -20 logs/discord_monitor.log
        else
            echo "尚無日誌檔案"
        fi
        ;;
    *)
        echo "❌ 無效選項"
        exit 1
        ;;
esac
