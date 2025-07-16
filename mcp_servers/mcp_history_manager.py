#!/usr/bin/env python3
"""
MCP 歷史數據管理器
負責收集、存儲和提供系統監控歷史數據
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import os

class MCPHistoryManager:
    def __init__(self, db_path: str = "/home/bao/mcp_use/data/mcp_history.db"):
        self.db_path = db_path
        self.collection_interval = 60  # 每分鐘收集一次數據
        self.retention_days = 30  # 保留30天的數據
        
        # 確保數據目錄存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化數據庫
        self._init_database()
        
        # 啟動數據收集線程
        self.collection_thread = None
        self.is_collecting = False
        
    def _init_database(self):
        """初始化數據庫表結構"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 系統指標歷史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    load_avg TEXT,
                    network_sent INTEGER,
                    network_recv INTEGER
                )
            ''')
            
            # 進程監控歷史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS process_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_processes INTEGER,
                    running_processes INTEGER,
                    sleeping_processes INTEGER,
                    zombie_processes INTEGER
                )
            ''')
            
            # 服務詳細歷史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    service_name TEXT,
                    pid INTEGER,
                    cpu_percent REAL,
                    memory_percent REAL,
                    status TEXT
                )
            ''')
            
            # 警告事件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT,
                    severity TEXT,
                    title TEXT,
                    description TEXT,
                    metric_value REAL,
                    threshold_value REAL,
                    is_resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # 健康度評分歷史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    overall_score REAL,
                    cpu_score REAL,
                    memory_score REAL,
                    disk_score REAL,
                    process_score REAL
                )
            ''')
            
            # 創建索引以提高查詢性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_process_timestamp ON process_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_timestamp ON service_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_timestamp ON alert_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_scores(timestamp)')
            
            conn.commit()
    
    def start_collection(self):
        """啟動數據收集"""
        if self.is_collecting:
            return
            
        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        print("📊 MCP 歷史數據收集已啟動")
    
    def stop_collection(self):
        """停止數據收集"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        print("📊 MCP 歷史數據收集已停止")
    
    def _collection_loop(self):
        """數據收集主循環"""
        while self.is_collecting:
            try:
                self._collect_current_metrics()
                self._cleanup_old_data()
                time.sleep(self.collection_interval)
            except Exception as e:
                print(f"數據收集錯誤: {e}")
                time.sleep(10)  # 出錯時等待10秒再重試
    
    def _collect_current_metrics(self):
        """收集當前系統指標"""
        try:
            # 導入監控模組
            import mcp_servers.mcp_system_monitor as system_monitor
            import mcp_servers.mcp_process_monitor as process_monitor
            
            # 收集系統數據
            system_data = system_monitor.get_system_summary()
            process_data = process_monitor.get_process_summary()
            services_data = process_monitor.get_detailed_processes()
            
            # 計算健康度評分
            health_score = self._calculate_health_score(system_data, process_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 插入系統指標
                cursor.execute('''
                    INSERT INTO system_metrics 
                    (cpu_percent, memory_percent, disk_percent, load_avg, network_sent, network_recv)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    system_data.get('cpu_percent', 0),
                    system_data.get('memory_percent', 0),
                    system_data.get('disk_percent', 0),
                    json.dumps(system_data.get('load_avg', [])),
                    system_data.get('network_sent', 0),
                    system_data.get('network_recv', 0)
                ))
                
                # 插入進程指標
                cursor.execute('''
                    INSERT INTO process_metrics
                    (total_processes, running_processes, sleeping_processes, zombie_processes)
                    VALUES (?, ?, ?, ?)
                ''', (
                    process_data.get('total_processes', 0),
                    process_data.get('running_processes', 0),
                    process_data.get('sleeping_processes', 0),
                    process_data.get('zombie_processes', 0)
                ))
                
                # 插入健康度評分
                cursor.execute('''
                    INSERT INTO health_scores
                    (overall_score, cpu_score, memory_score, disk_score, process_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    health_score['overall'],
                    health_score['cpu'],
                    health_score['memory'],
                    health_score['disk'],
                    health_score['process']
                ))
                
                # 插入前10個高資源使用服務
                for service in services_data[:10]:
                    cursor.execute('''
                        INSERT INTO service_metrics
                        (service_name, pid, cpu_percent, memory_percent, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        service.get('name', ''),
                        service.get('pid', 0),
                        service.get('cpu_percent', 0),
                        service.get('memory_percent', 0),
                        service.get('status', 'unknown')
                    ))
                
                conn.commit()
                
        except Exception as e:
            print(f"收集指標時發生錯誤: {e}")
    
    def _calculate_health_score(self, system_data: Dict, process_data: Dict) -> Dict[str, float]:
        """計算系統健康度評分 (0-100)"""
        # CPU 評分 (使用率越低分數越高)
        cpu_percent = system_data.get('cpu_percent', 0)
        cpu_score = max(0, 100 - cpu_percent)
        
        # 記憶體評分
        memory_percent = system_data.get('memory_percent', 0)
        memory_score = max(0, 100 - memory_percent)
        
        # 磁碟評分
        disk_percent = system_data.get('disk_percent', 0)
        disk_score = max(0, 100 - disk_percent)
        
        # 進程評分 (殭屍進程會降低分數)
        zombie_processes = process_data.get('zombie_processes', 0)
        total_processes = process_data.get('total_processes', 1)
        process_score = max(0, 100 - (zombie_processes / total_processes * 100))
        
        # 整體評分 (加權平均)
        overall_score = (
            cpu_score * 0.3 +
            memory_score * 0.3 +
            disk_score * 0.2 +
            process_score * 0.2
        )
        
        return {
            'overall': round(overall_score, 2),
            'cpu': round(cpu_score, 2),
            'memory': round(memory_score, 2),
            'disk': round(disk_score, 2),
            'process': round(process_score, 2)
        }
    
    def _cleanup_old_data(self):
        """清理舊數據"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            tables = ['system_metrics', 'process_metrics', 'service_metrics', 'alert_events', 'health_scores']
            for table in tables:
                cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff_date,))
            
            conn.commit()
    
    def get_trend_data(self, metric_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """獲取趨勢數據"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if metric_type == 'system':
                cursor.execute('''
                    SELECT timestamp, cpu_percent, memory_percent, disk_percent
                    FROM system_metrics 
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                ''', (start_time,))
                
                columns = ['timestamp', 'cpu_percent', 'memory_percent', 'disk_percent']
                
            elif metric_type == 'health':
                cursor.execute('''
                    SELECT timestamp, overall_score, cpu_score, memory_score, disk_score
                    FROM health_scores 
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                ''', (start_time,))
                
                columns = ['timestamp', 'overall_score', 'cpu_score', 'memory_score', 'disk_score']
                
            else:
                return []
            
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_current_health_score(self) -> Dict[str, float]:
        """獲取當前健康度評分"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT overall_score, cpu_score, memory_score, disk_score, process_score
                FROM health_scores 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                return {
                    'overall': row[0],
                    'cpu': row[1],
                    'memory': row[2],
                    'disk': row[3],
                    'process': row[4]
                }
            return {'overall': 0, 'cpu': 0, 'memory': 0, 'disk': 0, 'process': 0}
    
    def add_alert(self, alert_type: str, severity: str, title: str, 
                  description: str, metric_value: float, threshold_value: float):
        """添加警告事件"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alert_events 
                (alert_type, severity, title, description, metric_value, threshold_value)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert_type, severity, title, description, metric_value, threshold_value))
            
            conn.commit()
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """獲取最近的警告事件"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, alert_type, severity, title, description, 
                       metric_value, threshold_value, is_resolved
                FROM alert_events 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (start_time,))
            
            columns = ['timestamp', 'alert_type', 'severity', 'title', 'description', 
                      'metric_value', 'threshold_value', 'is_resolved']
            
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

# 全局實例 (懶加載)
_history_manager = None

def get_history_manager() -> MCPHistoryManager:
    """獲取歷史管理器實例"""
    global _history_manager
    if _history_manager is None:
        try:
            # 嘗試使用預設路徑
            _history_manager = MCPHistoryManager()
        except (PermissionError, OSError) as e:
            # 如果失敗，使用臨時目錄
            import tempfile
            temp_dir = tempfile.mkdtemp()
            temp_db_path = os.path.join(temp_dir, "mcp_history.db")
            print(f"警告: 無法創建預設數據庫，使用臨時路徑: {temp_db_path}")
            _history_manager = MCPHistoryManager(temp_db_path)
    return _history_manager

def start_history_collection():
    """啟動歷史數據收集"""
    get_history_manager().start_collection()

def stop_history_collection():
    """停止歷史數據收集"""
    get_history_manager().stop_collection()

if __name__ == "__main__":
    # 測試運行
    manager = MCPHistoryManager()
    manager.start_collection()
    
    try:
        print("歷史數據收集已啟動，按 Ctrl+C 停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_collection()
        print("歷史數據收集已停止")