#!/usr/bin/env python3
"""
Discord API 路由
提供 Discord 監控相關的 API 端點
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from app.core.monitors.discord import DiscordMonitor
from app.core.monitors.base import BaseMonitor, SystemMonitor
from app.api.models.response import DataResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# 全局 Discord 監控器實例
discord_monitor = DiscordMonitor()

class DiscordMessageRequest(BaseModel):
    """Discord 訊息請求模型"""
    message: str
    urgent: bool = False

class SystemReportRequest(BaseModel):
    """系統報告請求模型"""
    include_charts: bool = False
    format: str = "detailed"

@router.get("/status")
async def get_discord_status():
    """獲取 Discord 連接狀態"""
    try:
        status = discord_monitor.get_discord_status()
        return DataResponse(
            success=True,
            data=status,
            message="Discord 狀態獲取成功"
        )
    except Exception as e:
        logger.error(f"獲取 Discord 狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages")
async def get_recent_messages(limit: int = 10):
    """獲取最近的 Discord 訊息"""
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(status_code=400, detail="limit 必須在 1-50 之間")
        
        messages = discord_monitor.get_recent_messages(limit)
        return DataResponse(
            success=True,
            data=messages,
            message=f"獲取最近 {limit} 條訊息"
        )
    except Exception as e:
        logger.error(f"獲取 Discord 訊息失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-report")
async def send_system_report(
    request: SystemReportRequest,
    background_tasks: BackgroundTasks
):
    """發送系統報告到 Discord"""
    try:
        # 獲取系統數據
        system_monitor = SystemMonitor()
        system_data = system_monitor.get_system_info()
        
        # 添加額外的系統指標
        import psutil
        system_data.update({
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').used / psutil.disk_usage('/').total * 100,
            "memory_used": psutil.virtual_memory().used,
            "memory_total": psutil.virtual_memory().total,
            "disk_used": psutil.disk_usage('/').used,
            "disk_total": psutil.disk_usage('/').total,
            "network_sent": psutil.net_io_counters().bytes_sent,
            "network_recv": psutil.net_io_counters().bytes_recv,
            "processes": len(psutil.pids()),
            "load_avg": [0, 0, 0]  # Linux 特定，可能需要調整
        })
        
        try:
            import os
            system_data["load_avg"] = list(os.getloadavg())
        except:
            pass
        
        # 發送報告
        result = discord_monitor.send_system_report(system_data)
        
        if result["success"]:
            return DataResponse(
                success=True,
                data=result,
                message="系統報告已發送到 Discord"
            )
        else:
            return DataResponse(
                success=False,
                data=result,
                message=f"發送失敗: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"發送系統報告失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-message")
async def send_discord_message(request: DiscordMessageRequest):
    """發送自定義訊息到 Discord"""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="訊息內容不能為空")
        
        # 準備訊息格式
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"📢 **手動訊息** - {timestamp}\n\n{request.message}"
        
        if request.urgent:
            formatted_message = f"🚨 **緊急通知** - {timestamp}\n\n{request.message}"
        
        # 模擬發送 (使用系統報告的發送功能)
        system_data = {"custom_message": formatted_message}
        
        # 這裡需要修改 discord_monitor 來支援自定義訊息
        import requests
        import os
        
        discord_token = os.getenv('DISCORD_TOKEN')
        channel_id = os.getenv('DISCORD_CHANNEL_ID', '1393483928823660585')
        
        if not discord_token:
            raise HTTPException(status_code=500, detail="Discord Token 未設定")
        
        headers = {
            "Authorization": f"Bot {discord_token}",
            "Content-Type": "application/json"
        }
        
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        data = {"content": formatted_message}
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            message_data = response.json()
            return DataResponse(
                success=True,
                data={
                    "message_id": message_data.get("id"),
                    "sent_time": timestamp
                },
                message="訊息已發送到 Discord"
            )
        else:
            return DataResponse(
                success=False,
                data={"error": f"發送失敗 (狀態碼: {response.status_code})"},
                message="訊息發送失敗"
            )
            
    except Exception as e:
        logger.error(f"發送 Discord 訊息失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_discord_analytics():
    """獲取 Discord 監控分析數據"""
    try:
        # 獲取基本狀態
        status = discord_monitor.get_discord_status()
        messages = discord_monitor.get_recent_messages(20)
        
        # 簡單的分析
        analytics = {
            "connection_status": status.get("status"),
            "guild_name": status.get("guild_name", "Unknown"),
            "channel_name": status.get("channel_name", "Unknown"),
            "recent_activity": {
                "total_messages": messages.get("count", 0),
                "bot_messages": sum(1 for msg in messages.get("messages", []) if msg.get("is_bot")),
                "user_messages": sum(1 for msg in messages.get("messages", []) if not msg.get("is_bot"))
            },
            "last_report_time": status.get("last_sent_time"),
            "timestamp": datetime.now().isoformat()
        }
        
        return DataResponse(
            success=True,
            data=analytics,
            message="Discord 分析數據獲取成功"
        )
        
    except Exception as e:
        logger.error(f"獲取 Discord 分析數據失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_discord_overview():
    """獲取 Discord 監控概覽"""
    try:
        data = discord_monitor.get_data()
        return DataResponse(
            success=True,
            data=data,
            message="Discord 監控概覽獲取成功"
        )
    except Exception as e:
        logger.error(f"獲取 Discord 概覽失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))