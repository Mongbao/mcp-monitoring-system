#!/usr/bin/env python3
"""
MCP 服務控制管理器
提供服務啟停控制、警報管理等功能
"""

import subprocess
import psutil
import signal
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import threading
import time

class MCPServiceController:
    def __init__(self):
        self.alert_thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 85.0,
            'memory_warning': 80.0,
            'memory_critical': 90.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'load_warning': 2.0,
            'load_critical': 4.0
        }
        
        # 警報狀態追蹤
        self.active_alerts = {}
        self.alert_history = []
        
        # 監控線程
        self.monitoring_thread = None
        self.is_monitoring = False
        
    def start_service_monitoring(self):
        """啟動服務監控"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("🔍 服務監控已啟動")
    
    def stop_service_monitoring(self):
        """停止服務監控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🔍 服務監控已停止")
    
    def _monitoring_loop(self):
        """監控主循環"""
        while self.is_monitoring:
            try:
                self._check_system_alerts()
                time.sleep(30)  # 每30秒檢查一次
            except Exception as e:
                print(f"監控循環錯誤: {e}")
                time.sleep(60)
    
    def _check_system_alerts(self):
        """檢查系統警報"""
        try:
            import mcp_servers.mcp_system_monitor as system_monitor
            system_data = system_monitor.get_system_summary()
            
            # 檢查 CPU 使用率
            cpu_percent = system_data.get('cpu_percent', 0)
            self._check_threshold_alert('cpu', cpu_percent, 'CPU 使用率')
            
            # 檢查記憶體使用率
            memory_percent = system_data.get('memory_percent', 0)
            self._check_threshold_alert('memory', memory_percent, '記憶體使用率')
            
            # 檢查磁碟使用率
            disk_percent = system_data.get('disk_percent', 0)
            self._check_threshold_alert('disk', disk_percent, '磁碟使用率')
            
            # 檢查系統負載
            load_avg = system_data.get('load_avg', [0, 0, 0])
            if load_avg:
                load_1min = load_avg[0] if isinstance(load_avg, list) else 0
                self._check_threshold_alert('load', load_1min, '系統負載')
                
        except Exception as e:
            print(f"檢查系統警報時發生錯誤: {e}")
    
    def _check_threshold_alert(self, metric_type: str, current_value: float, metric_name: str):
        """檢查閾值警報"""
        warning_key = f"{metric_type}_warning"
        critical_key = f"{metric_type}_critical"
        
        warning_threshold = self.alert_thresholds.get(warning_key, 999)
        critical_threshold = self.alert_thresholds.get(critical_key, 999)
        
        alert_key = f"{metric_type}_alert"
        
        if current_value >= critical_threshold:
            if alert_key not in self.active_alerts or self.active_alerts[alert_key]['severity'] != 'critical':
                self._trigger_alert(alert_key, 'critical', f"{metric_name}嚴重警告", 
                                  f"{metric_name} 已達到 {current_value:.1f}%，超過臨界值 {critical_threshold}%",
                                  current_value, critical_threshold)
        elif current_value >= warning_threshold:
            if alert_key not in self.active_alerts or self.active_alerts[alert_key]['severity'] != 'warning':
                self._trigger_alert(alert_key, 'warning', f"{metric_name}警告", 
                                  f"{metric_name} 已達到 {current_value:.1f}%，超過警告值 {warning_threshold}%",
                                  current_value, warning_threshold)
        else:
            # 清除警報
            if alert_key in self.active_alerts:
                self._clear_alert(alert_key)
    
    def _trigger_alert(self, alert_key: str, severity: str, title: str, 
                      description: str, metric_value: float, threshold_value: float):
        """觸發警報"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'title': title,
            'description': description,
            'metric_value': metric_value,
            'threshold_value': threshold_value,
            'is_active': True
        }
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert.copy())
        
        # 記錄到歷史管理器
        try:
            from mcp_servers.mcp_history_manager import get_history_manager
            history_manager = get_history_manager()
            history_manager.add_alert(
                alert_key, severity, title, description, 
                metric_value, threshold_value
            )
        except Exception as e:
            print(f"記錄警報到歷史時發生錯誤: {e}")
        
        print(f"🚨 {severity.upper()}: {title} - {description}")
    
    def _clear_alert(self, alert_key: str):
        """清除警報"""
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert['is_active'] = False
            alert['resolved_at'] = datetime.now().isoformat()
            del self.active_alerts[alert_key]
            print(f"✅ 警報已解除: {alert['title']}")
    
    def get_service_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """獲取服務詳細資訊"""
        try:
            process = psutil.Process(pid)
            return {
                'pid': pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'create_time': process.create_time(),
                'cmdline': ' '.join(process.cmdline()),
                'cwd': process.cwd() if hasattr(process, 'cwd') else None,
                'username': process.username() if hasattr(process, 'username') else None
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
    
    def terminate_service(self, pid: int, force: bool = False) -> Tuple[bool, str]:
        """終止服務"""
        try:
            process = psutil.Process(pid)
            service_name = process.name()
            
            if force:
                process.kill()  # SIGKILL
                action = "強制終止"
            else:
                process.terminate()  # SIGTERM
                action = "正常終止"
            
            # 等待進程結束
            try:
                process.wait(timeout=10)
                return True, f"服務 {service_name} (PID: {pid}) 已{action}"
            except psutil.TimeoutExpired:
                if not force:
                    # 如果正常終止失敗，嘗試強制終止
                    process.kill()
                    process.wait(timeout=5)
                    return True, f"服務 {service_name} (PID: {pid}) 已強制終止"
                else:
                    return False, f"無法終止服務 {service_name} (PID: {pid})"
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            return False, f"終止服務失敗: {str(e)}"
    
    def restart_systemd_service(self, service_name: str) -> Tuple[bool, str]:
        """重啟 systemd 服務"""
        try:
            # 檢查服務是否存在
            result = subprocess.run(['systemctl', 'status', service_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 4:  # 服務不存在
                return False, f"服務 {service_name} 不存在"
            
            # 重啟服務
            result = subprocess.run(['sudo', '-n', 'systemctl', 'restart', service_name], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, f"服務 {service_name} 已重啟"
            else:
                return False, f"重啟服務失敗: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"重啟服務 {service_name} 超時"
        except Exception as e:
            return False, f"重啟服務失敗: {str(e)}"
    
    def start_systemd_service(self, service_name: str) -> Tuple[bool, str]:
        """啟動 systemd 服務"""
        try:
            result = subprocess.run(['sudo', '-n', 'systemctl', 'start', service_name], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, f"服務 {service_name} 已啟動"
            else:
                return False, f"啟動服務失敗: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"啟動服務 {service_name} 超時"
        except Exception as e:
            return False, f"啟動服務失敗: {str(e)}"
    
    def stop_systemd_service(self, service_name: str) -> Tuple[bool, str]:
        """停止 systemd 服務"""
        try:
            result = subprocess.run(['sudo', '-n', 'systemctl', 'stop', service_name], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, f"服務 {service_name} 已停止"
            else:
                return False, f"停止服務失敗: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"停止服務 {service_name} 超時"
        except Exception as e:
            return False, f"停止服務失敗: {str(e)}"
    
    def get_systemd_services(self) -> List[Dict[str, Any]]:
        """獲取 systemd 服務列表"""
        try:
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--no-pager', '--plain'], 
                                  capture_output=True, text=True)
            
            services = []
            for line in result.stdout.split('\n')[1:]:  # 跳過標題行
                if line.strip() and not line.startswith('●'):
                    parts = line.split()
                    if len(parts) >= 4:
                        services.append({
                            'name': parts[0],
                            'loaded': parts[1],
                            'active': parts[2],
                            'sub': parts[3],
                            'description': ' '.join(parts[4:]) if len(parts) > 4 else ''
                        })
            
            return services
            
        except Exception as e:
            print(f"獲取 systemd 服務列表失敗: {e}")
            return []
    
    def update_alert_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """更新警報閾值"""
        try:
            self.alert_thresholds.update(thresholds)
            
            # 保存到文件
            config_path = "/home/bao/mcp_use/data/alert_thresholds.json"
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.alert_thresholds, f, indent=2)
            
            return True
        except Exception as e:
            print(f"更新警報閾值失敗: {e}")
            return False
    
    def load_alert_thresholds(self):
        """載入警報閾值"""
        try:
            config_path = "/home/bao/mcp_use/data/alert_thresholds.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.alert_thresholds.update(json.load(f))
        except Exception as e:
            print(f"載入警報閾值失敗: {e}")
    
    def get_current_alerts(self) -> List[Dict[str, Any]]:
        """獲取當前活躍警報"""
        return list(self.active_alerts.values())
    
    def get_alert_thresholds(self) -> Dict[str, float]:
        """獲取警報閾值設定"""
        return self.alert_thresholds.copy()

# 全局實例
service_controller = MCPServiceController()

def get_service_controller() -> MCPServiceController:
    """獲取服務控制器實例"""
    return service_controller

def start_service_monitoring():
    """啟動服務監控"""
    service_controller.load_alert_thresholds()
    service_controller.start_service_monitoring()

def stop_service_monitoring():
    """停止服務監控"""
    service_controller.stop_service_monitoring()

if __name__ == "__main__":
    # 測試運行
    controller = MCPServiceController()
    controller.start_service_monitoring()
    
    try:
        print("服務監控已啟動，按 Ctrl+C 停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop_service_monitoring()
        print("服務監控已停止")