#!/usr/bin/env python3
"""
MCP 日誌即時監控器
提供即時日誌查看和分析功能
"""

import os
import time
import threading
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime, timedelta
import re
import json
from collections import deque
import subprocess

class MCPLogMonitor:
    def __init__(self):
        # 常見日誌路徑
        self.log_paths = {
            'system': '/var/log/syslog',
            'auth': '/var/log/auth.log',
            'kernel': '/var/log/kern.log',
            'mail': '/var/log/mail.log',
            'cron': '/var/log/cron.log',
            'daemon': '/var/log/daemon.log',
            'user': '/var/log/user.log'
        }
        
        # 日誌級別正則表達式
        self.level_patterns = {
            'ERROR': re.compile(r'\b(ERROR|error|Error|FAILED|failed|Failed|CRITICAL|critical|Critical)\b'),
            'WARNING': re.compile(r'\b(WARNING|warning|Warning|WARN|warn|Warn)\b'),
            'INFO': re.compile(r'\b(INFO|info|Info|NOTICE|notice|Notice)\b'),
            'DEBUG': re.compile(r'\b(DEBUG|debug|Debug|TRACE|trace|Trace)\b')
        }
        
        # 即時日誌緩存 (最近1000條)
        self.recent_logs = deque(maxlen=1000)
        
        # 監控線程
        self.monitoring_threads = {}
        self.is_monitoring = {}
        
        # 日誌統計
        self.log_stats = {
            'total_lines': 0,
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'last_updated': datetime.now()
        }
    
    def start_monitoring(self, log_types: List[str] = None):
        """啟動日誌監控"""
        if log_types is None:
            log_types = ['system', 'auth']  # 預設監控系統和認證日誌
        
        for log_type in log_types:
            if log_type in self.log_paths and log_type not in self.is_monitoring:
                self.is_monitoring[log_type] = True
                thread = threading.Thread(
                    target=self._monitor_log_file, 
                    args=(log_type, self.log_paths[log_type]),
                    daemon=True
                )
                thread.start()
                self.monitoring_threads[log_type] = thread
                print(f"📋 開始監控 {log_type} 日誌: {self.log_paths[log_type]}")
    
    def stop_monitoring(self, log_types: List[str] = None):
        """停止日誌監控"""
        if log_types is None:
            log_types = list(self.is_monitoring.keys())
        
        for log_type in log_types:
            if log_type in self.is_monitoring:
                self.is_monitoring[log_type] = False
                print(f"📋 停止監控 {log_type} 日誌")
        
        # 等待線程結束
        for log_type in log_types:
            if log_type in self.monitoring_threads:
                self.monitoring_threads[log_type].join(timeout=5)
                del self.monitoring_threads[log_type]
    
    def _monitor_log_file(self, log_type: str, file_path: str):
        """監控單個日誌文件"""
        if not os.path.exists(file_path):
            print(f"日誌文件不存在: {file_path}")
            return
        
        try:
            # 移動到文件末尾
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(0, 2)  # 移動到文件末尾
                
                while self.is_monitoring.get(log_type, False):
                    line = f.readline()
                    if line:
                        self._process_log_line(log_type, line.strip())
                    else:
                        time.sleep(0.1)  # 沒有新內容時短暫休息
                        
        except Exception as e:
            print(f"監控日誌文件 {file_path} 時發生錯誤: {e}")
    
    def _process_log_line(self, log_type: str, line: str):
        """處理日誌行"""
        if not line.strip():
            return
        
        # 解析日誌級別
        level = self._detect_log_level(line)
        
        # 創建日誌條目
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'log_type': log_type,
            'level': level,
            'message': line,
            'original_timestamp': self._extract_timestamp(line)
        }
        
        # 添加到緩存
        self.recent_logs.append(log_entry)
        
        # 更新統計
        self._update_stats(level)
        
        # 如果是錯誤級別，可能需要觸發警報
        if level == 'ERROR':
            self._handle_error_log(log_entry)
    
    def _detect_log_level(self, line: str) -> str:
        """檢測日誌級別"""
        line_lower = line.lower()
        
        for level, pattern in self.level_patterns.items():
            if pattern.search(line):
                return level
        
        # 預設為 INFO
        return 'INFO'
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """提取日誌中的時間戳"""
        # 嘗試匹配常見的時間戳格式
        timestamp_patterns = [
            r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',  # Jan 15 14:30:25
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',  # 2024-01-15 14:30:25
            r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',  # 01/15/2024 14:30:25
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        
        return None
    
    def _update_stats(self, level: str):
        """更新日誌統計"""
        self.log_stats['total_lines'] += 1
        
        if level == 'ERROR':
            self.log_stats['error_count'] += 1
        elif level == 'WARNING':
            self.log_stats['warning_count'] += 1
        elif level == 'INFO':
            self.log_stats['info_count'] += 1
        elif level == 'DEBUG':
            self.log_stats['debug_count'] += 1
        
        self.log_stats['last_updated'] = datetime.now()
    
    def _handle_error_log(self, log_entry: Dict[str, Any]):
        """處理錯誤日誌"""
        # 這裡可以實現錯誤日誌的特殊處理邏輯
        # 例如：觸發警報、發送通知等
        print(f"🔴 錯誤日誌: [{log_entry['log_type']}] {log_entry['message']}")
    
    def get_recent_logs(self, count: int = 100, level_filter: str = None, 
                       log_type_filter: str = None) -> List[Dict[str, Any]]:
        """獲取最近的日誌"""
        logs = list(self.recent_logs)
        
        # 按時間戳倒序排列
        logs.reverse()
        
        # 應用過濾器
        if level_filter:
            logs = [log for log in logs if log['level'] == level_filter]
        
        if log_type_filter:
            logs = [log for log in logs if log['log_type'] == log_type_filter]
        
        return logs[:count]
    
    def search_logs(self, query: str, log_type: str = None, 
                   since_hours: int = 24) -> List[Dict[str, Any]]:
        """搜尋日誌"""
        since_time = datetime.now() - timedelta(hours=since_hours)
        
        # 如果指定了日誌類型，搜尋對應的日誌文件
        if log_type and log_type in self.log_paths:
            return self._search_log_file(self.log_paths[log_type], query, since_time)
        
        # 否則搜尋所有監控的日誌
        results = []
        for log_type, log_path in self.log_paths.items():
            if os.path.exists(log_path):
                results.extend(self._search_log_file(log_path, query, since_time))
        
        return results
    
    def _search_log_file(self, file_path: str, query: str, 
                        since_time: datetime) -> List[Dict[str, Any]]:
        """搜尋單個日誌文件"""
        results = []
        
        try:
            # 使用 grep 命令進行高效搜尋
            cmd = ['grep', '-i', query, file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    # 檢查時間是否在範圍內
                    timestamp = self._extract_timestamp(line)
                    if timestamp:
                        # 這裡需要更完善的時間解析邏輯
                        # 簡化處理：如果有時間戳就認為是最近的
                        pass
                    
                    results.append({
                        'timestamp': datetime.now().isoformat(),
                        'log_type': os.path.basename(file_path).replace('.log', ''),
                        'level': self._detect_log_level(line),
                        'message': line,
                        'original_timestamp': timestamp
                    })
            
        except Exception as e:
            print(f"搜尋日誌文件 {file_path} 時發生錯誤: {e}")
        
        return results
    
    def get_log_tail(self, log_type: str, lines: int = 50) -> List[str]:
        """獲取日誌尾部內容"""
        if log_type not in self.log_paths:
            return []
        
        file_path = self.log_paths[log_type]
        if not os.path.exists(file_path):
            return []
        
        try:
            result = subprocess.run(['tail', '-n', str(lines), file_path], 
                                  capture_output=True, text=True)
            return result.stdout.split('\n')
        except Exception as e:
            print(f"獲取日誌尾部時發生錯誤: {e}")
            return []
    
    def get_log_stats(self) -> Dict[str, Any]:
        """獲取日誌統計資訊"""
        return self.log_stats.copy()
    
    def get_available_log_types(self) -> List[str]:
        """獲取可用的日誌類型"""
        available = []
        for log_type, log_path in self.log_paths.items():
            if os.path.exists(log_path):
                available.append(log_type)
        return available
    
    def add_custom_log_path(self, log_type: str, file_path: str):
        """添加自定義日誌路徑"""
        if os.path.exists(file_path):
            self.log_paths[log_type] = file_path
            return True
        return False
    
    def analyze_error_patterns(self, hours: int = 24) -> Dict[str, Any]:
        """分析錯誤模式"""
        since_time = datetime.now() - timedelta(hours=hours)
        
        # 從最近日誌中提取錯誤
        error_logs = [log for log in self.recent_logs 
                     if log['level'] == 'ERROR' and 
                     datetime.fromisoformat(log['timestamp']) >= since_time]
        
        # 錯誤統計
        error_patterns = {}
        for log in error_logs:
            # 簡化的錯誤分類（基於關鍵字）
            message = log['message'].lower()
            
            if 'failed' in message or 'failure' in message:
                error_patterns['failed_operations'] = error_patterns.get('failed_operations', 0) + 1
            elif 'connection' in message or 'network' in message:
                error_patterns['network_errors'] = error_patterns.get('network_errors', 0) + 1
            elif 'permission' in message or 'access' in message:
                error_patterns['permission_errors'] = error_patterns.get('permission_errors', 0) + 1
            elif 'timeout' in message:
                error_patterns['timeout_errors'] = error_patterns.get('timeout_errors', 0) + 1
            else:
                error_patterns['other_errors'] = error_patterns.get('other_errors', 0) + 1
        
        return {
            'total_errors': len(error_logs),
            'error_patterns': error_patterns,
            'analysis_period_hours': hours,
            'most_recent_error': error_logs[0] if error_logs else None
        }

# 全局實例
log_monitor = MCPLogMonitor()

def get_log_monitor() -> MCPLogMonitor:
    """獲取日誌監控器實例"""
    return log_monitor

def start_log_monitoring(log_types: List[str] = None):
    """啟動日誌監控"""
    log_monitor.start_monitoring(log_types)

def stop_log_monitoring(log_types: List[str] = None):
    """停止日誌監控"""
    log_monitor.stop_monitoring(log_types)

if __name__ == "__main__":
    # 測試運行
    monitor = MCPLogMonitor()
    monitor.start_monitoring(['system', 'auth'])
    
    try:
        print("日誌監控已啟動，按 Ctrl+C 停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("日誌監控已停止")