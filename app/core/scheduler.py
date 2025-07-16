#!/usr/bin/env python3
"""
Discord 報告排程管理器
"""

import json
import uuid
import time as time_module
import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import schedule
import threading
from concurrent.futures import ThreadPoolExecutor

from app.api.models.schedule import ScheduleConfig, ScheduleType, ScheduleStatus, ScheduleExecutionLog
from app.core.monitors.discord import DiscordMonitor
from app.core.monitors.base import SystemMonitor
import psutil

logger = logging.getLogger(__name__)

class DiscordScheduler:
    """Discord 報告排程管理器"""
    
    def __init__(self, config_file: str = None):
        # 使用相對路徑或臨時目錄
        if config_file is None:
            # 嘗試使用項目目錄下的 data 目錄
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "data" / "schedules.json"
        
        self.config_file = Path(config_file)
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.execution_logs: List[ScheduleExecutionLog] = []
        self.discord_monitor = DiscordMonitor()
        self.system_monitor = SystemMonitor()
        self.scheduler_thread = None
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # 確保配置目錄存在（只在有寫入權限時）
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            # 如果無法創建目錄，使用臨時目錄
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "mcp_schedules"
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = temp_dir / "schedules.json"
        
        # 載入配置
        self.load_schedules()
    
    def load_schedules(self):
        """載入排程配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 載入排程
                for schedule_data in data.get('schedules', []):
                    schedule = ScheduleConfig(**schedule_data)
                    self.schedules[schedule.id] = schedule
                
                # 載入執行日誌
                for log_data in data.get('execution_logs', []):
                    log = ScheduleExecutionLog(**log_data)
                    self.execution_logs.append(log)
                    
                logger.info(f"載入 {len(self.schedules)} 個排程配置")
        except Exception as e:
            logger.warning(f"載入排程配置失敗: {e}，將使用空配置")
    
    def save_schedules(self):
        """保存排程配置"""
        try:
            data = {
                'schedules': [schedule.dict() for schedule in self.schedules.values()],
                'execution_logs': [log.dict() for log in self.execution_logs[-100:]]  # 只保留最近100條日誌
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
            logger.info("排程配置已保存")
        except Exception as e:
            logger.warning(f"保存排程配置失敗: {e}，配置將不會持久化")
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> ScheduleConfig:
        """建立新排程"""
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(id=schedule_id, **schedule_data)
        
        # 計算下次執行時間
        schedule_config.next_run = self._calculate_next_run(schedule_config)
        
        self.schedules[schedule_id] = schedule_config
        self.save_schedules()
        
        # 重新配置排程器
        self._setup_scheduler()
        
        logger.info(f"建立新排程: {schedule_config.name} (ID: {schedule_id})")
        return schedule_config
    
    def update_schedule(self, schedule_id: str, update_data: Dict[str, Any]) -> Optional[ScheduleConfig]:
        """更新排程"""
        if schedule_id not in self.schedules:
            return None
        
        schedule = self.schedules[schedule_id]
        
        # 更新字段
        for field, value in update_data.items():
            if hasattr(schedule, field) and value is not None:
                setattr(schedule, field, value)
        
        schedule.updated_at = datetime.now()
        schedule.next_run = self._calculate_next_run(schedule)
        
        self.save_schedules()
        self._setup_scheduler()
        
        logger.info(f"更新排程: {schedule.name} (ID: {schedule_id})")
        return schedule
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """刪除排程"""
        if schedule_id not in self.schedules:
            return False
        
        schedule_name = self.schedules[schedule_id].name
        del self.schedules[schedule_id]
        
        self.save_schedules()
        self._setup_scheduler()
        
        logger.info(f"刪除排程: {schedule_name} (ID: {schedule_id})")
        return True
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleConfig]:
        """獲取排程"""
        return self.schedules.get(schedule_id)
    
    def list_schedules(self) -> List[ScheduleConfig]:
        """列出所有排程"""
        return list(self.schedules.values())
    
    def get_execution_logs(self, schedule_id: Optional[str] = None, limit: int = 50) -> List[ScheduleExecutionLog]:
        """獲取執行日誌"""
        logs = self.execution_logs
        
        if schedule_id:
            logs = [log for log in logs if log.schedule_id == schedule_id]
        
        return logs[-limit:]
    
    def _calculate_next_run(self, schedule: ScheduleConfig) -> datetime:
        """計算下次執行時間"""
        now = datetime.now()
        target_time = datetime.strptime(schedule.time, "%H:%M").time()
        
        if schedule.type == ScheduleType.DAILY:
            # 每日執行
            next_run = datetime.combine(now.date(), target_time)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif schedule.type == ScheduleType.WEEKLY:
            # 每週執行
            weekday_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            
            target_weekdays = [weekday_map[day] for day in schedule.weekdays]
            
            # 找到下一個目標日期
            next_run = None
            for i in range(7):
                check_date = now.date() + timedelta(days=i)
                if check_date.weekday() in target_weekdays:
                    potential_run = datetime.combine(check_date, target_time)
                    if potential_run > now:
                        next_run = potential_run
                        break
            
            if not next_run:
                # 如果這週沒有合適的日期，找下週第一個
                next_run = datetime.combine(now.date() + timedelta(days=7), target_time)
        
        elif schedule.type == ScheduleType.HOURLY:
            # 每小時執行
            next_run = now + timedelta(hours=schedule.interval_hours)
        
        else:
            # 自訂類型，預設為明天同一時間
            next_run = datetime.combine(now.date() + timedelta(days=1), target_time)
        
        return next_run
    
    def _setup_scheduler(self):
        """設定排程器"""
        # 清除所有現有任務
        schedule.clear()
        
        # 為每個活動排程設定任務
        for schedule_config in self.schedules.values():
            if schedule_config.status != ScheduleStatus.ACTIVE:
                continue
            
            if schedule_config.type == ScheduleType.DAILY:
                schedule.every().day.at(schedule_config.time).do(
                    self._execute_schedule, schedule_config.id
                )
            elif schedule_config.type == ScheduleType.WEEKLY:
                for weekday in schedule_config.weekdays:
                    getattr(schedule.every(), weekday.lower()).at(schedule_config.time).do(
                        self._execute_schedule, schedule_config.id
                    )
            elif schedule_config.type == ScheduleType.HOURLY:
                schedule.every(schedule_config.interval_hours).hours.do(
                    self._execute_schedule, schedule_config.id
                )
    
    def _execute_schedule(self, schedule_id: str):
        """執行排程"""
        if schedule_id not in self.schedules:
            return
        
        schedule_config = self.schedules[schedule_id]
        
        # 提交到線程池執行
        self.executor.submit(self._run_schedule_task, schedule_config)
    
    def _run_schedule_task(self, schedule_config: ScheduleConfig):
        """在線程池中執行排程任務"""
        start_time = datetime.now()
        
        try:
            # 收集系統數據
            system_data = self._collect_system_data(schedule_config)
            
            # 生成報告
            report = self._generate_report(schedule_config, system_data)
            
            # 發送到 Discord
            result = self.discord_monitor.send_system_report(system_data)
            
            # 記錄執行結果
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            log = ScheduleExecutionLog(
                id=str(uuid.uuid4()),
                schedule_id=schedule_config.id,
                executed_at=start_time,
                success=result.get('success', False),
                message=result.get('message', ''),
                error=result.get('error'),
                execution_time_ms=int(execution_time),
                discord_message_id=result.get('message_id')
            )
            
            self.execution_logs.append(log)
            
            # 更新排程資訊
            schedule_config.last_run = start_time
            schedule_config.next_run = self._calculate_next_run(schedule_config)
            schedule_config.run_count += 1
            
            self.save_schedules()
            
            logger.info(f"排程執行完成: {schedule_config.name} - 成功: {result.get('success', False)}")
            
        except Exception as e:
            # 記錄錯誤
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            log = ScheduleExecutionLog(
                id=str(uuid.uuid4()),
                schedule_id=schedule_config.id,
                executed_at=start_time,
                success=False,
                error=str(e),
                execution_time_ms=int(execution_time)
            )
            
            self.execution_logs.append(log)
            self.save_schedules()
            
            logger.error(f"排程執行失敗: {schedule_config.name} - {e}")
    
    def _collect_system_data(self, schedule_config: ScheduleConfig) -> Dict[str, Any]:
        """收集系統數據"""
        system_data = {}
        
        if schedule_config.include_system_info:
            system_data.update(self.system_monitor.get_system_info())
        
        # 添加額外的系統指標
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
            "load_avg": [0, 0, 0]
        })
        
        try:
            import os
            system_data["load_avg"] = list(os.getloadavg())
        except:
            pass
        
        return system_data
    
    def _generate_report(self, schedule_config: ScheduleConfig, system_data: Dict[str, Any]) -> str:
        """生成報告"""
        # 使用 Discord 監控器的格式化方法
        return self.discord_monitor._format_system_report(system_data)
    
    def start(self):
        """啟動排程器"""
        if self.running:
            return
        
        self.running = True
        self._setup_scheduler()
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time_module.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Discord 排程器已啟動")
    
    def stop(self):
        """停止排程器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        self.executor.shutdown(wait=True)
        
        logger.info("Discord 排程器已停止")

# 全局排程器實例
scheduler = DiscordScheduler()