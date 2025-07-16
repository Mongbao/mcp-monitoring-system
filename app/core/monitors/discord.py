#!/usr/bin/env python3
"""
Discord 監控模組
整合 Discord 系統監控功能到 FastAPI 應用中
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from dotenv import load_dotenv
from .base import BaseMonitor

# 載入環境變數
load_dotenv('/home/bao/mcp_use/.env')

logger = logging.getLogger(__name__)

class DiscordMonitor(BaseMonitor):
    """Discord 監控器"""
    
    def __init__(self):
        super().__init__()
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.guild_id = os.getenv('DISCORD_GUILD_ID', '1363426069595820092')
        self.channel_id = os.getenv('DISCORD_CHANNEL_ID', '1393483928823660585')
        self.discord_api_base = "https://discord.com/api/v10"
        
        self.last_message_id = None
        self.last_sent_time = None
        
        if not self.discord_token:
            logger.warning("DISCORD_TOKEN 環境變數未設定")
    
    def get_discord_status(self) -> Dict[str, Any]:
        """獲取 Discord 連接狀態"""
        try:
            if not self.discord_token:
                return {
                    "status": "disconnected",
                    "error": "Discord Token 未設定",
                    "guild_id": self.guild_id,
                    "channel_id": self.channel_id
                }
            
            # 測試 Discord API 連接
            headers = {
                "Authorization": f"Bot {self.discord_token}",
                "Content-Type": "application/json"
            }
            
            # 獲取頻道資訊
            channel_url = f"{self.discord_api_base}/channels/{self.channel_id}"
            channel_response = requests.get(channel_url, headers=headers, timeout=5)
            
            if channel_response.status_code == 200:
                channel_data = channel_response.json()
                
                # 獲取伺服器資訊
                guild_url = f"{self.discord_api_base}/guilds/{self.guild_id}"
                guild_response = requests.get(guild_url, headers=headers, timeout=5)
                
                guild_data = guild_response.json() if guild_response.status_code == 200 else {}
                
                return {
                    "status": "connected",
                    "guild_id": self.guild_id,
                    "guild_name": guild_data.get("name", "Unknown"),
                    "channel_id": self.channel_id,
                    "channel_name": channel_data.get("name", "Unknown"),
                    "last_message_id": self.last_message_id,
                    "last_sent_time": self.last_sent_time.isoformat() if self.last_sent_time else None
                }
            else:
                return {
                    "status": "error",
                    "error": f"無法連接到 Discord 頻道 (狀態碼: {channel_response.status_code})",
                    "guild_id": self.guild_id,
                    "channel_id": self.channel_id
                }
                
        except Exception as e:
            logger.error(f"檢查 Discord 狀態時發生錯誤: {e}")
            return {
                "status": "error",
                "error": str(e),
                "guild_id": self.guild_id,
                "channel_id": self.channel_id
            }
    
    def get_recent_messages(self, limit: int = 10) -> Dict[str, Any]:
        """獲取最近的 Discord 訊息"""
        try:
            if not self.discord_token:
                return {"error": "Discord Token 未設定"}
            
            headers = {
                "Authorization": f"Bot {self.discord_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.discord_api_base}/channels/{self.channel_id}/messages"
            params = {"limit": limit}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                messages = response.json()
                
                # 過濾 bot 自己的訊息
                processed_messages = []
                for msg in messages:
                    processed_messages.append({
                        "id": msg["id"],
                        "content": msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"],
                        "timestamp": msg["timestamp"],
                        "author": msg["author"]["username"],
                        "is_bot": msg["author"]["bot"]
                    })
                
                return {
                    "messages": processed_messages,
                    "count": len(processed_messages)
                }
            else:
                return {"error": f"無法獲取訊息 (狀態碼: {response.status_code})"}
                
        except Exception as e:
            logger.error(f"獲取 Discord 訊息時發生錯誤: {e}")
            return {"error": str(e)}
    
    def send_system_report(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """發送系統報告到 Discord"""
        try:
            if not self.discord_token:
                return {"success": False, "error": "Discord Token 未設定"}
            
            # 格式化系統報告
            report = self._format_system_report(system_data)
            
            headers = {
                "Authorization": f"Bot {self.discord_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.discord_api_base}/channels/{self.channel_id}/messages"
            data = {"content": report}
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                message_data = response.json()
                self.last_message_id = message_data.get("id")
                self.last_sent_time = datetime.now()
                
                return {
                    "success": True,
                    "message_id": self.last_message_id,
                    "sent_time": self.last_sent_time.isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"發送失敗 (狀態碼: {response.status_code})"
                }
                
        except Exception as e:
            logger.error(f"發送 Discord 訊息時發生錯誤: {e}")
            return {"success": False, "error": str(e)}
    
    def _format_system_report(self, system_data: Dict[str, Any]) -> str:
        """格式化系統報告為 Discord 訊息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 狀態指示器
        cpu_status = "🟢" if system_data.get("cpu_percent", 0) < 80 else "🟡" if system_data.get("cpu_percent", 0) < 95 else "🔴"
        mem_status = "🟢" if system_data.get("memory_percent", 0) < 80 else "🟡" if system_data.get("memory_percent", 0) < 95 else "🔴"
        disk_status = "🟢" if system_data.get("disk_percent", 0) < 80 else "🟡" if system_data.get("disk_percent", 0) < 95 else "🔴"
        
        # 格式化記憶體和磁碟大小
        mem_used_gb = system_data.get("memory_used", 0) / (1024**3)
        mem_total_gb = system_data.get("memory_total", 0) / (1024**3)
        disk_used_gb = system_data.get("disk_used", 0) / (1024**3)
        disk_total_gb = system_data.get("disk_total", 0) / (1024**3)
        
        # 網路流量 (MB)
        net_sent_mb = system_data.get("network_sent", 0) / (1024**2)
        net_recv_mb = system_data.get("network_recv", 0) / (1024**2)
        
        # 取得系統負載
        load_avg_value = system_data.get('load_avg', [0, 0, 0])
        if isinstance(load_avg_value, list):
            load_avg_str = f"{load_avg_value[0]:.2f}"
        else:
            load_avg_str = str(load_avg_value)
            
        report = f"""🤖 **MCP 系統監控報告** - {timestamp}

{cpu_status} **CPU 使用率**: {system_data.get('cpu_percent', 0):.1f}%
{mem_status} **記憶體**: {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB ({system_data.get('memory_percent', 0):.1f}%)
{disk_status} **磁碟空間**: {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB ({system_data.get('disk_percent', 0):.1f}%)

📊 **系統負載**: {load_avg_str}
⏰ **運行時間**: {system_data.get('uptime', 'N/A')}
🔄 **進程數**: {system_data.get('processes', 0)}
📡 **網路流量**: ↑{net_sent_mb:.1f}MB ↓{net_recv_mb:.1f}MB

📈 **監控網址**: https://bao.mengwei710.com/"""
        
        return report
    
    def get_data(self) -> Dict[str, Any]:
        """獲取 Discord 監控數據"""
        return {
            "discord_status": self.get_discord_status(),
            "recent_messages": self.get_recent_messages(),
            "timestamp": datetime.now().isoformat()
        }