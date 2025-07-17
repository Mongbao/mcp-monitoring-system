#!/usr/bin/env python3
"""
MCP Discord 系統監控整合
定期收集系統資訊並發送到 Discord 頻道
"""

import psutil
import requests
import json
import time
import os
import subprocess
from datetime import datetime, timedelta
import schedule
import logging
from dotenv import load_dotenv

# 載入環境變數
def load_environment():
    """載入環境變數，處理檔案路徑不存在的情況"""
    env_paths = [
        '/home/bao/mcp_use/.env',
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        '.env'
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break

load_environment()

# 設定日誌
def setup_logging():
    """設定日誌，處理檔案路徑不存在的情況"""
    handlers = [logging.StreamHandler()]
    
    try:
        # 嘗試使用專案相對路徑
        from pathlib import Path
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "discord_monitor.log"
        handlers.append(logging.FileHandler(str(log_file)))
    except (OSError, PermissionError):
        # 如果無法創建日誌檔案，只使用控制台輸出
        pass
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

setup_logging()
logger = logging.getLogger(__name__)

class MCPDiscordMonitor:
    def __init__(self):
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.guild_id = os.getenv('DISCORD_GUILD_ID', '1363426069595820092')
        self.channel_id = os.getenv('DISCORD_CHANNEL_ID', '1393483928823660585')
        self.discord_api_base = "https://discord.com/api/v10"
        
        # 在 CI 環境中允許 dummy token
        if not self.discord_token:
            if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
                logger.warning("在 CI 環境中運行，DISCORD_TOKEN 未設定")
                self.discord_token = "dummy_token_for_ci"
            else:
                raise ValueError("DISCORD_TOKEN 環境變數未設定")
        
        logger.info("MCP Discord 監控器已初始化")
        logger.info(f"Guild ID: {self.guild_id}")
        logger.info(f"Channel ID: {self.channel_id}")
    
    def get_system_metrics(self):
        """收集詳細的系統指標"""
        try:
            # CPU 資訊
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # 記憶體資訊
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # 磁碟資訊
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # 網路資訊
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            # 系統資訊
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            # 進程資訊
            processes = len(psutil.pids())
            
            # 負載平均
            try:
                load_avg = os.getloadavg()
            except:
                load_avg = (0, 0, 0)
            
            return {
                'timestamp': datetime.now(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 0
                },
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'percent': memory.percent,
                    'available': memory.available
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': (disk_usage.used / disk_usage.total) * 100,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'connections': net_connections
                },
                'system': {
                    'uptime': uptime,
                    'processes': processes,
                    'load_avg': load_avg
                }
            }
        except Exception as e:
            logger.error(f"收集系統指標時發生錯誤: {e}")
            return None
    
    def check_mcp_services(self):
        """檢查 MCP 服務狀態"""
        services = {
            'web_server': False,
            'apache': False,
            'mcp_servers': 0
        }
        
        try:
            # 檢查 Web 服務 (port 8003)
            result = subprocess.run(['netstat', '-ln'], capture_output=True, text=True)
            if ':8003' in result.stdout:
                services['web_server'] = True
            
            # 檢查 Apache
            result = subprocess.run(['systemctl', 'is-active', 'apache2'], 
                                  capture_output=True, text=True)
            if result.stdout.strip() == 'active':
                services['apache'] = True
            
            # 檢查 MCP 相關進程
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            mcp_count = result.stdout.count('mcp_') + result.stdout.count('mcp-')
            services['mcp_servers'] = mcp_count
            
        except Exception as e:
            logger.error(f"檢查服務狀態時發生錯誤: {e}")
        
        return services
    
    def format_system_report(self, metrics, services):
        """格式化系統報告為 Discord 訊息"""
        if not metrics:
            return "❌ 系統指標收集失敗"
        
        timestamp = metrics['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        # 狀態指示器
        cpu_status = "🟢" if metrics['cpu']['percent'] < 80 else "🟡" if metrics['cpu']['percent'] < 95 else "🔴"
        mem_status = "🟢" if metrics['memory']['percent'] < 80 else "🟡" if metrics['memory']['percent'] < 95 else "🔴"
        disk_status = "🟢" if metrics['disk']['percent'] < 80 else "🟡" if metrics['disk']['percent'] < 95 else "🔴"
        
        # 格式化記憶體和磁碟大小
        mem_used_gb = metrics['memory']['used'] / (1024**3)
        mem_total_gb = metrics['memory']['total'] / (1024**3)
        disk_used_gb = metrics['disk']['used'] / (1024**3)
        disk_total_gb = metrics['disk']['total'] / (1024**3)
        
        # 格式化運行時間
        uptime_str = str(metrics['system']['uptime']).split('.')[0]
        
        # 網路流量 (MB)
        net_sent_mb = metrics['network']['bytes_sent'] / (1024**2)
        net_recv_mb = metrics['network']['bytes_recv'] / (1024**2)
        
        report = f"""🤖 **MCP 系統監控報告** - {timestamp}

{cpu_status} **CPU 使用率**: {metrics['cpu']['percent']:.1f}% ({metrics['cpu']['count']} 核心)
{mem_status} **記憶體**: {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB ({metrics['memory']['percent']:.1f}%)
{disk_status} **磁碟空間**: {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB ({metrics['disk']['percent']:.1f}%)

📊 **系統負載**: {metrics['system']['load_avg'][0]:.2f}, {metrics['system']['load_avg'][1]:.2f}, {metrics['system']['load_avg'][2]:.2f}
⏰ **運行時間**: {uptime_str}
🔄 **進程數**: {metrics['system']['processes']}
🌐 **網路連線**: {metrics['network']['connections']}
📡 **網路流量**: ↑{net_sent_mb:.1f}MB ↓{net_recv_mb:.1f}MB

🛠️ **MCP 服務狀態**:
{'✅' if services['web_server'] else '❌'} Web 儀表板 (Port 8003)
{'✅' if services['apache'] else '❌'} Apache 反向代理
🔧 MCP Servers: {services['mcp_servers']} 個進程運行中

📈 **監控網址**: https://bao.mengwei710.com/"""
        
        return report
    
    def send_to_discord(self, message):
        """發送訊息到 Discord"""
        try:
            url = f"{self.discord_api_base}/channels/{self.channel_id}/messages"
            headers = {
                "Authorization": f"Bot {self.discord_token}",
                "Content-Type": "application/json"
            }
            data = {
                "content": message
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                message_data = response.json()
                logger.info(f"訊息發送成功，ID: {message_data.get('id')}")
                return True
            else:
                logger.error(f"發送訊息失敗，狀態碼: {response.status_code}")
                logger.error(f"錯誤回應: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"發送 Discord 訊息時發生錯誤: {e}")
            return False
    
    def run_monitoring_cycle(self):
        """執行一次監控循環"""
        logger.info("開始監控循環")
        
        # 收集系統指標
        metrics = self.get_system_metrics()
        if not metrics:
            logger.error("無法收集系統指標")
            return False
        
        # 檢查服務狀態
        services = self.check_mcp_services()
        
        # 格式化報告
        report = self.format_system_report(metrics, services)
        
        # 發送到 Discord
        success = self.send_to_discord(report)
        
        if success:
            logger.info("監控報告已發送到 Discord")
        else:
            logger.error("監控報告發送失敗")
        
        return success
    
    def start_scheduled_monitoring(self):
        """啟動排程監控"""
        logger.info("啟動排程監控")
        
        # 排程設定
        schedule.every(15).minutes.do(self.run_monitoring_cycle)  # 每15分鐘
        schedule.every().hour.at(":00").do(self.run_monitoring_cycle)  # 每小時整點
        schedule.every().day.at("09:00").do(self.run_monitoring_cycle)  # 每天早上9點
        schedule.every().day.at("18:00").do(self.run_monitoring_cycle)  # 每天晚上6點
        
        # 立即執行一次
        self.run_monitoring_cycle()
        
        logger.info("排程監控已啟動，開始等待執行...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次排程
        except KeyboardInterrupt:
            logger.info("監控已停止")

def main():
    """主函數"""
    print("🎯 MCP Discord 系統監控")
    print("=" * 40)
    
    try:
        # 初始化監控器
        monitor = MCPDiscordMonitor()
        
        # 檢查參數
        import sys
        if len(sys.argv) > 1:
            if sys.argv[1] == "--once":
                print("📊 執行單次監控...")
                monitor.run_monitoring_cycle()
                return
            elif sys.argv[1] == "--schedule":
                print("⏰ 啟動排程監控...")
                monitor.start_scheduled_monitoring()
                return
        
        # 預設執行單次監控
        print("📊 執行單次監控...")
        success = monitor.run_monitoring_cycle()
        
        if success:
            print("✅ 監控完成！請檢查 Discord 頻道。")
        else:
            print("❌ 監控失敗！")
            
    except Exception as e:
        logger.error(f"主程序錯誤: {e}")
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    main()
