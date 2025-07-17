#!/bin/bash

# 模擬 GitHub Actions CI 環境測試

echo "📋 設定測試環境..."

# 創建必要的目錄結構
mkdir -p data
echo '{}' > data/alert_rules.json
echo '{}' > data/alert_thresholds.json
echo '{}' > data/historical_metrics.json
echo '{}' > data/performance_baselines.json
echo '[]' > data/schedules.json

echo "✅ 數據目錄結構已創建"

# 設置環境變數
export DISCORD_TOKEN=dummy_token_for_testing
export CI=true

echo "✅ 環境變數已設置"

echo ""
echo "🧪 開始運行測試..."

# 測試 FastAPI 應用程式
echo "🔍 測試 FastAPI 應用程式導入..."
python -c "from app.main import app; print('✅ FastAPI 應用程式可以正常導入')"

# 測試排程器
echo "🔍 測試 Discord 排程器導入..."
python -c "from app.core.scheduler import scheduler; print('✅ Discord 排程器可以正常導入')"

# 測試 Discord 監控模組
echo "🔍 測試 Discord 監控模組導入..."
python -c "from app.core.monitors.discord import DiscordMonitor; print('✅ Discord 監控模組可以正常導入')"

# 測試排程模型
echo "🔍 測試排程模型導入..."
python -c "from app.api.models.schedule import ScheduleConfig; print('✅ 排程模型可以正常導入')"

# 測試 Discord 集成模組
echo "🔍 測試 Discord 集成模組導入..."
python -c "from discord_integration.mcp_discord_system_monitor import MCPDiscordMonitor; print('✅ Discord 系統監控可以正常導入')"

# 測試警報引擎
echo "🔍 測試警報引擎導入..."
python -c "from app.core.alerts.engine import alert_engine; print('✅ 警報引擎可以正常導入')"

echo ""
echo "🎉 所有測試通過！"
