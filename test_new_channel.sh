#!/bin/bash
# 測試新的 Discord 頻道 ID

echo "🎯 測試新的 Discord 頻道 ID"
echo "=============================="

# 載入環境變數（從 .env 檔案）
source /home/bao/mcp_use/.env

echo "📋 測試參數:"
echo "  Guild ID: $DISCORD_GUILD_ID"
echo "  舊頻道 ID: 1363426069595820095"
echo "  新頻道 ID: $DISCORD_CHANNEL_ID"
echo ""

# 測試新頻道是否可存取
echo "🔍 測試新頻道存取..."
CHANNEL_INFO=$(curl -s -H "Authorization: Bot $DISCORD_TOKEN" \
    "https://discord.com/api/v10/channels/$DISCORD_CHANNEL_ID")

echo "頻道回應: $CHANNEL_INFO"

if echo "$CHANNEL_INFO" | grep -q '"name"'; then
    CHANNEL_NAME=$(echo "$CHANNEL_INFO" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    echo "✅ 新頻道存取成功: #$CHANNEL_NAME"
    
    # 發送測試訊息
    echo ""
    echo "📤 發送測試訊息到新頻道..."
    
    MESSAGE="🔄 **頻道 ID 更新測試** - $(date '+%Y-%m-%d %H:%M:%S')

✅ 新頻道 ID 測試成功
📡 頻道 ID: $DISCORD_CHANNEL_ID
🤖 MCP Discord 整合正常運作

此訊息確認新頻道配置正確。"

    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bot $DISCORD_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"$MESSAGE\"}" \
        "https://discord.com/api/v10/channels/$DISCORD_CHANNEL_ID/messages")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        MESSAGE_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "✅ 測試訊息發送成功!"
        echo "   訊息 ID: $MESSAGE_ID"
        echo ""
        echo "🔗 新頻道連結:"
        echo "   https://discord.com/channels/$DISCORD_GUILD_ID/$DISCORD_CHANNEL_ID/$MESSAGE_ID"
    else
        echo "❌ 測試訊息發送失敗"
        echo "回應: $RESPONSE"
    fi
else
    echo "❌ 新頻道存取失敗"
    echo "請檢查頻道 ID 是否正確，或 Bot 是否有權限存取該頻道"
fi

echo ""
echo "🎉 頻道 ID 更新測試完成!"
