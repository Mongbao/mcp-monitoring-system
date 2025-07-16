#!/usr/bin/env python3
"""
VS Code SSH 記憶體監控和清理工具
用於監控和管理 VS Code Server 的記憶體使用
"""

import psutil
import time
import subprocess
import logging
import json
from datetime import datetime, timedelta
import signal
import os

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/bao/mcp_use/logs/vscode_memory.log'),
        logging.StreamHandler()
    ]
)

class VSCodeMemoryMonitor:
    def __init__(self):
        self.memory_threshold = 80  # 記憶體使用率閾值（%）
        self.vscode_memory_limit = 2048  # VS Code 進程記憶體限制（MB）
        self.check_interval = 30  # 檢查間隔（秒）
        self.running = True
        
    def get_vscode_processes(self):
        """獲取所有VS Code相關進程"""
        vscode_processes = []
        keywords = ['code-server', 'node', 'copilot', 'typescript', 'eslint']
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'memory_percent', 'create_time']):
            try:
                pinfo = proc.info
                cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                
                # 檢查是否為VS Code相關進程
                if any(keyword in cmdline.lower() or keyword in pinfo['name'].lower() for keyword in keywords):
                    memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    vscode_processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                        'memory_mb': memory_mb,
                        'memory_percent': pinfo['memory_percent'],
                        'create_time': datetime.fromtimestamp(pinfo['create_time']),
                        'process': proc
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return sorted(vscode_processes, key=lambda x: x['memory_mb'], reverse=True)
    
    def get_system_memory_info(self):
        """獲取系統記憶體資訊"""
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / (1024**3),
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3),
            'percent': memory.percent
        }
    
    def cleanup_vscode_processes(self, force=False):
        """清理VS Code進程"""
        vscode_procs = self.get_vscode_processes()
        cleaned = []
        
        for proc_info in vscode_procs:
            proc = proc_info['process']
            memory_mb = proc_info['memory_mb']
            
            # 如果記憶體使用超過限制或強制清理
            if memory_mb > self.vscode_memory_limit or force:
                try:
                    # 首先嘗試優雅關閉
                    proc.terminate()
                    time.sleep(5)
                    
                    # 如果還活著，強制殺死
                    if proc.is_running():
                        proc.kill()
                    
                    cleaned.append(proc_info)
                    logging.info(f"清理進程: PID {proc_info['pid']}, 記憶體: {memory_mb:.1f}MB")
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logging.warning(f"無法清理進程 {proc_info['pid']}: {e}")
        
        return cleaned
    
    def restart_vscode_server(self):
        """重啟VS Code Server"""
        try:
            # 查找VS Code Server的systemd服務（如果有的話）
            result = subprocess.run(['systemctl', '--user', 'list-units', '--type=service'], 
                                  capture_output=True, text=True)
            
            if 'code-server' in result.stdout:
                subprocess.run(['systemctl', '--user', 'restart', 'code-server'], check=True)
                logging.info("重啟了 code-server 服務")
            else:
                logging.info("未找到 code-server 服務，僅清理進程")
                
        except subprocess.CalledProcessError as e:
            logging.error(f"重啟VS Code Server失敗: {e}")
    
    def monitor_loop(self):
        """主監控循環"""
        logging.info("開始VS Code記憶體監控")
        
        while self.running:
            try:
                # 獲取系統記憶體資訊
                sys_memory = self.get_system_memory_info()
                vscode_procs = self.get_vscode_processes()
                
                total_vscode_memory = sum(proc['memory_mb'] for proc in vscode_procs)
                
                # 記錄狀態
                logging.info(f"系統記憶體: {sys_memory['used_gb']:.2f}GB/{sys_memory['total_gb']:.2f}GB ({sys_memory['percent']:.1f}%)")
                logging.info(f"VS Code進程數: {len(vscode_procs)}, 總記憶體: {total_vscode_memory:.1f}MB")
                
                # 詳細記錄大記憶體進程
                for proc in vscode_procs[:5]:  # 顯示前5個最大的進程
                    if proc['memory_mb'] > 100:  # 只顯示超過100MB的
                        logging.info(f"  PID {proc['pid']}: {proc['name']} - {proc['memory_mb']:.1f}MB")
                
                # 檢查是否需要清理
                cleanup_needed = False
                cleanup_reason = ""
                
                if sys_memory['percent'] > self.memory_threshold:
                    cleanup_needed = True
                    cleanup_reason = f"系統記憶體使用率過高: {sys_memory['percent']:.1f}%"
                
                elif any(proc['memory_mb'] > self.vscode_memory_limit for proc in vscode_procs):
                    cleanup_needed = True
                    cleanup_reason = f"VS Code進程記憶體過高"
                
                elif total_vscode_memory > 4096:  # 總VS Code記憶體超過4GB
                    cleanup_needed = True
                    cleanup_reason = f"VS Code總記憶體過高: {total_vscode_memory:.1f}MB"
                
                # 執行清理
                if cleanup_needed:
                    logging.warning(f"觸發清理: {cleanup_reason}")
                    cleaned = self.cleanup_vscode_processes()
                    
                    if cleaned:
                        logging.info(f"已清理 {len(cleaned)} 個進程")
                        time.sleep(10)  # 等待進程清理完成
                        
                        # 如果系統記憶體仍然很高，考慮重啟VS Code Server
                        if sys_memory['percent'] > 90:
                            self.restart_vscode_server()
                
                # 等待下次檢查
                time.sleep(self.check_interval)
                
            except Exception as e:
                logging.error(f"監控循環出錯: {e}")
                time.sleep(self.check_interval)
    
    def stop(self):
        """停止監控"""
        self.running = False
        logging.info("停止VS Code記憶體監控")

def signal_handler(signum, frame):
    """信號處理器"""
    global monitor
    if monitor:
        monitor.stop()

def main():
    global monitor
    
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    monitor = VSCodeMemoryMonitor()
    
    if len(os.sys.argv) > 1:
        command = os.sys.argv[1]
        
        if command == 'status':
            # 顯示當前狀態
            sys_memory = monitor.get_system_memory_info()
            vscode_procs = monitor.get_vscode_processes()
            
            print(f"系統記憶體: {sys_memory['used_gb']:.2f}GB/{sys_memory['total_gb']:.2f}GB ({sys_memory['percent']:.1f}%)")
            print(f"VS Code進程數: {len(vscode_procs)}")
            print("\nVS Code相關進程:")
            
            for proc in vscode_procs:
                print(f"  PID {proc['pid']:>6}: {proc['name']:>15} - {proc['memory_mb']:>7.1f}MB ({proc['memory_percent']:>4.1f}%)")
                print(f"           {proc['cmdline']}")
        
        elif command == 'cleanup':
            # 強制清理
            cleaned = monitor.cleanup_vscode_processes(force=True)
            print(f"已清理 {len(cleaned)} 個VS Code進程")
            
        elif command == 'restart':
            # 重啟VS Code Server
            monitor.restart_vscode_server()
            
        else:
            print("使用方法:")
            print("  python3 vscode_memory_monitor.py status   # 顯示狀態")
            print("  python3 vscode_memory_monitor.py cleanup  # 強制清理")
            print("  python3 vscode_memory_monitor.py restart  # 重啟服務")
            print("  python3 vscode_memory_monitor.py          # 開始監控")
    else:
        # 開始監控
        monitor.monitor_loop()

if __name__ == '__main__':
    monitor = None
    main()
