"""
監控基礎類和工具函數
"""
import psutil
import platform
import time
from datetime import datetime
from typing import Dict, Any, List

class BaseMonitor:
    """基礎監控類"""
    
    def __init__(self):
        self.start_time = time.time()
        
    def format_bytes(self, bytes_value: int) -> str:
        """格式化位元組數為可讀字符串"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def format_uptime(self, boot_time: float) -> str:
        """格式化系統運行時間"""
        uptime_seconds = time.time() - boot_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{days}天 {hours}小時 {minutes}分鐘"

class SystemMonitor(BaseMonitor):
    """系統監控類"""
    
    def get_system_info(self) -> Dict[str, Any]:
        """獲取系統資訊"""
        try:
            # CPU 資訊
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # 記憶體資訊
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # 磁碟資訊
            disk = psutil.disk_usage('/')
            
            # 系統負載
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # 系統資訊
            boot_time = psutil.boot_time()
            
            return {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_freq': cpu_freq.current if cpu_freq else 0,
                'memory_percent': memory.percent,
                'memory_total': memory.total,
                'memory_used': memory.used,
                'memory_available': memory.available,
                'swap_percent': swap.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'disk_percent': disk.percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_free': disk.free,
                'load_avg': f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}",
                'uptime': self.format_uptime(boot_time),
                'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
                'platform': platform.platform(),
                'hostname': platform.node()
            }
        except Exception as e:
            return {
                'error': f"獲取系統資訊時發生錯誤: {str(e)}",
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'load_avg': 'N/A',
                'uptime': 'N/A'
            }

class ProcessMonitor(BaseMonitor):
    """進程監控類"""
    
    def get_process_info(self) -> Dict[str, Any]:
        """獲取進程資訊"""
        try:
            processes = list(psutil.process_iter())
            total = len(processes)
            
            status_count = {
                'running': 0,
                'sleeping': 0,
                'zombie': 0,
                'stopped': 0,
                'other': 0
            }
            
            for proc in processes:
                try:
                    status = proc.status()
                    if status == psutil.STATUS_RUNNING:
                        status_count['running'] += 1
                    elif status in [psutil.STATUS_SLEEPING, psutil.STATUS_IDLE]:
                        status_count['sleeping'] += 1
                    elif status == psutil.STATUS_ZOMBIE:
                        status_count['zombie'] += 1
                    elif status == psutil.STATUS_STOPPED:
                        status_count['stopped'] += 1
                    else:
                        status_count['other'] += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'total_processes': total,
                'running_processes': status_count['running'],
                'sleeping_processes': status_count['sleeping'],
                'zombie_processes': status_count['zombie'],
                'stopped_processes': status_count['stopped'],
                'other_processes': status_count['other']
            }
        except Exception as e:
            return {
                'error': f"獲取進程資訊時發生錯誤: {str(e)}",
                'total_processes': 0,
                'running_processes': 0,
                'sleeping_processes': 0,
                'zombie_processes': 0
            }

class NetworkMonitor(BaseMonitor):
    """網路監控類"""
    
    def get_network_info(self) -> Dict[str, Any]:
        """獲取網路資訊"""
        try:
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            net_interfaces = len(psutil.net_if_addrs())
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout,
                'interface_count': net_interfaces,
                'connections': net_connections
            }
        except Exception as e:
            return {
                'error': f"獲取網路資訊時發生錯誤: {str(e)}",
                'bytes_sent': 0,
                'bytes_recv': 0,
                'packets_sent': 0,
                'packets_recv': 0,
                'interface_count': 0,
                'connections': 0
            }

class FilesystemMonitor(BaseMonitor):
    """檔案系統監控類"""
    
    def get_filesystem_info(self) -> Dict[str, Any]:
        """獲取檔案系統資訊"""
        try:
            # 獲取根目錄磁碟使用情況
            disk_usage = psutil.disk_usage('/')
            
            # 獲取所有磁碟分區
            partitions = psutil.disk_partitions()
            monitored_paths = len(partitions)
            
            return {
                'monitored_paths': monitored_paths,
                'total_space': disk_usage.total,
                'free_space': disk_usage.free,
                'used_space': disk_usage.used,
                'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 1),
                'partitions': [
                    {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype
                    }
                    for partition in partitions
                ]
            }
        except Exception as e:
            return {
                'error': f"獲取檔案系統資訊時發生錯誤: {str(e)}",
                'monitored_paths': 0,
                'total_space': 0,
                'free_space': 0,
                'used_space': 0,
                'usage_percent': 0
            }

class ServiceMonitor(BaseMonitor):
    """服務監控類"""
    
    def get_services_info(self) -> Dict[str, Any]:
        """獲取服務資訊"""
        try:
            # 獲取所有進程作為服務列表
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['name'] and pinfo['pid'] > 1:  # 排除 kernel 進程
                        processes.append({
                            'name': pinfo['name'],
                            'pid': pinfo['pid'],
                            'status': pinfo['status'],
                            'cpu_percent': pinfo['cpu_percent'] or 0.0,
                            'memory_percent': pinfo['memory_percent'] or 0.0,
                            'username': pinfo['username'] or 'unknown'
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 按 CPU 使用率排序
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                'services': processes[:100],  # 限制返回前 100 個
                'total': len(processes)
            }
        except Exception as e:
            return {
                'error': f"獲取服務資訊時發生錯誤: {str(e)}",
                'services': [],
                'total': 0
            }
    
    def get_paginated_services(self, page: int = 1, page_size: int = 50, sort_by: str = "name", 
                             search: str = None, status: str = None) -> Dict[str, Any]:
        """獲取分頁服務資訊"""
        try:
            # 獲取所有服務
            all_services = self.get_services_info()
            if 'error' in all_services:
                return all_services
                
            services = all_services['services']
            
            # 過濾
            if search:
                services = [s for s in services if search.lower() in s['name'].lower()]
            if status:
                services = [s for s in services if s['status'].lower() == status.lower()]
            
            # 排序
            if sort_by == "cpu":
                services.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif sort_by == "memory":
                services.sort(key=lambda x: x['memory_percent'], reverse=True)
            elif sort_by == "name":
                services.sort(key=lambda x: x['name'].lower())
            
            # 分頁
            total = len(services)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_services = services[start_idx:end_idx]
            
            return {
                'services': paginated_services,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        except Exception as e:
            return {
                'error': f"獲取分頁服務資訊時發生錯誤: {str(e)}",
                'services': [],
                'total': 0,
                'page': page,
                'page_size': page_size
            }