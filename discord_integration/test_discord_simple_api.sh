#!/bin/bash
# Discord API 測試腳本（不使用 jq）

echo "🎯 Discord API 直接測試"
echo "========================"

# 檢查環境變數
if [ -z "$DISCORD_TOKEN" ]; then
    echo "❌ DISCORD_TOKEN 環境變數未設定"
    exit 1
fi

echo "✅ Discord Token 已設定"

# Discord API 基本資訊
BOT_TOKEN="$DISCORD_TOKEN"
GUILD_ID="1363426069595820092"
CHANNEL_ID="1393483928823660585"

echo "📋 使用設定:"
echo "  Guild ID: $GUILD_ID"  
echo "  Channel ID: $CHANNEL_ID"
echo ""

# 測試 Bot 身份
echo "🔍 測試 Bot 身份..."
BOT_INFO=$(curl -s -H "Authorization: Bot $BOT_TOKEN" \
    "https://discord.com/api/v10/users/@me")

echo "Bot 資訊回應: $BOT_INFO"

if echo "$BOT_INFO" | grep -q '"username"'; then
    echo "✅ Bot 身份確認成功"
else
    echo "❌ Bot 身份驗證失敗"
    echo "完整回應: $BOT_INFO"
    exit 1
fi

# 測試頻道存取
echo ""
echo "📢 測試頻道存取..."
CHANNEL_INFO=$(curl -s -H "Authorization: Bot $BOT_TOKEN" \
    "https://discord.com/api/v10/channels/$CHANNEL_ID")

echo "頻道資訊回應: $CHANNEL_INFO"

if echo "$CHANNEL_INFO" | grep -q '"name"'; then
    echo "✅ 頻道存取成功"
else
    echo "❌ 頻道存取失敗"
    echo "嘗試獲取伺服器頻道列表..."
    
    GUILD_CHANNELS=$(curl -s -H "Authorization: Bot $BOT_TOKEN" \
        "https://discord.com/api/v10/guilds/$GUILD_ID/channels")
    
    echo "伺服器頻道: $GUILD_CHANNELS"
fi

# 準備簡單的測試訊息
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
MESSAGE="MCP 系統監控測試 - $TIMESTAMP\n\n✅ Discord API 連線成功\n📡 自動化訊息發送功能正常"

echo ""
echo "📝 準備發送測試訊息..."
echo "內容: $MESSAGE"

# 使用簡單的 JSON 格式
JSON_DATA="{\"content\": \"$MESSAGE\"}"

echo ""
echo "🚀 發送訊息..."
echo "JSON 資料: $JSON_DATA"

RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bot $BOT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$JSON_DATA" \
    "https://discord.com/api/v10/channels/$CHANNEL_ID/messages")

echo ""
echo "📡 發送結果:"
echo "$RESPONSE"

# 檢查是否包含訊息 ID
if echo "$RESPONSE" | grep -q '"id"'; then
    echo ""
    echo "✅ 訊息發送成功!"
    echo "🎉 請檢查 Discord 的頻道確認訊息已送達。"
else
    echo ""
    echo "❌ 訊息可能發送失敗，請檢查上方回應"
    
    # 如果失敗，嘗試檢查權限
    echo ""
    echo "🔧 檢查 Bot 權限..."
    BOT_MEMBER=$(curl -s -H "Authorization: Bot $BOT_TOKEN" \
        "https://discord.com/api/v10/guilds/$GUILD_ID/members/@me")
    
    echo "Bot 成員資訊: $BOT_MEMBER"
fi
