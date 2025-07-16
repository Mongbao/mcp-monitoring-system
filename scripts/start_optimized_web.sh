#!/bin/bash
# MCP 監控系統 - 優化版 Web 伺服器啟動腳本

echo "🚀 MCP 監控系統 - 優化版伺服器"
echo "================================"

# 設定工作目錄
cd /home/bao/mcp_use

# 啟動虛擬環境
source mcp_env/bin/activate

# 檢查端口參數
PORT=${1:-8003}

echo "📊 功能特色："
echo "   • 🎯 虛擬滾動技術 - 處理大量數據無延遲"
echo "   • 📈 懶載入圖表 - 按需載入視覺化組件"
echo "   • 🗜️ Gzip 壓縮 - 減少網路傳輸大小"
echo "   • 📱 響應式設計 - 完美支援行動裝置"
echo "   • ⚡ 靜態資源優化 - 快速載入體驗"
echo ""
echo "🌐 啟動伺服器於端口: $PORT"
echo "📡 瀏覽器開啟: http://localhost:$PORT"
echo "💡 按 Ctrl+C 停止伺服器"
echo ""

# 啟動優化版伺服器
python3 web_dashboard/mcp_web_server_optimized.py $PORT
