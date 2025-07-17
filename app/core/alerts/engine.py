"""
智能警報引擎
負責警報規則評估、事件管理和通知發送
"""
import json
import uuid
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from app.api.models.alerts import (
    AlertRule, AlertIncident, AlertLevel, AlertStatus, 
    AlertCategory, AlertSummary, AlertNotification
)

logger = logging.getLogger(__name__)


class AlertEngine:
    """智能警報引擎"""
    
    def __init__(self, data_dir: str = "/home/bao/mcp_use/data"):
        self.data_dir = Path(data_dir)
        self.rules_file = self.data_dir / "alert_rules.json"
        self.incidents_file = self.data_dir / "alert_incidents.json"
        self.notifications_file = self.data_dir / "alert_notifications.json"
        
        # 內存存儲
        self.rules: Dict[str, AlertRule] = {}
        self.incidents: Dict[str, AlertIncident] = {}
        self.active_incidents: Dict[str, AlertIncident] = {}
        self.rule_states: Dict[str, Dict] = {}  # 規則狀態追蹤
        
        # 確保數據目錄存在
        self.data_dir.mkdir(exist_ok=True)
        
        # 載入數據
        self._load_rules()
        self._load_incidents()
        
        # 初始化預設規則
        self._initialize_default_rules()
    
    def _load_rules(self):
        """載入警報規則"""
        try:
            if self.rules_file.exists():
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    for rule_id, rule_dict in rules_data.items():
                        # 轉換時間字符串為 datetime 對象
                        if 'created_at' in rule_dict:
                            rule_dict['created_at'] = datetime.fromisoformat(rule_dict['created_at'])
                        if 'updated_at' in rule_dict:
                            rule_dict['updated_at'] = datetime.fromisoformat(rule_dict['updated_at'])
                        self.rules[rule_id] = AlertRule(**rule_dict)
        except Exception as e:
            logger.error(f"載入警報規則失敗: {e}")
    
    def _save_rules(self):
        """保存警報規則"""
        try:
            rules_data = {}
            for rule_id, rule in self.rules.items():
                rule_dict = rule.dict()
                # 轉換 datetime 對象為字符串
                rule_dict['created_at'] = rule_dict['created_at'].isoformat()
                rule_dict['updated_at'] = rule_dict['updated_at'].isoformat()
                rules_data[rule_id] = rule_dict
            
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存警報規則失敗: {e}")
    
    def _load_incidents(self):
        """載入警報事件"""
        try:
            if self.incidents_file.exists():
                with open(self.incidents_file, 'r', encoding='utf-8') as f:
                    incidents_data = json.load(f)
                    for incident_id, incident_dict in incidents_data.items():
                        # 轉換時間字符串為 datetime 對象
                        time_fields = ['started_at', 'resolved_at', 'acknowledged_at', 'last_notification', 'suppressed_until']
                        for field in time_fields:
                            if incident_dict.get(field):
                                incident_dict[field] = datetime.fromisoformat(incident_dict[field])
                        
                        incident = AlertIncident(**incident_dict)
                        self.incidents[incident_id] = incident
                        
                        # 如果是活躍的警報，添加到活躍警報列表
                        if incident.status == AlertStatus.ACTIVE:
                            self.active_incidents[incident_id] = incident
        except Exception as e:
            logger.error(f"載入警報事件失敗: {e}")
    
    def _save_incidents(self):
        """保存警報事件"""
        try:
            incidents_data = {}
            for incident_id, incident in self.incidents.items():
                incident_dict = incident.dict()
                # 轉換 datetime 對象為字符串
                time_fields = ['started_at', 'resolved_at', 'acknowledged_at', 'last_notification', 'suppressed_until']
                for field in time_fields:
                    if incident_dict.get(field):
                        incident_dict[field] = incident_dict[field].isoformat()
                incidents_data[incident_id] = incident_dict
            
            with open(self.incidents_file, 'w', encoding='utf-8') as f:
                json.dump(incidents_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存警報事件失敗: {e}")
    
    def _initialize_default_rules(self):
        """初始化預設警報規則"""
        if not self.rules:
            default_rules = [
                {
                    "name": "CPU 使用率過高",
                    "description": "CPU 使用率超過 80% 持續 2 分鐘",
                    "category": AlertCategory.PERFORMANCE,
                    "metric": "cpu_percent",
                    "condition": ">",
                    "threshold": 80.0,
                    "level": AlertLevel.WARNING,
                    "duration": 120,
                    "cool_down": 300,
                    "notification_channels": ["discord"]
                },
                {
                    "name": "記憶體使用率危險",
                    "description": "記憶體使用率超過 90%",
                    "category": AlertCategory.PERFORMANCE,
                    "metric": "memory_percent",
                    "condition": ">",
                    "threshold": 90.0,
                    "level": AlertLevel.CRITICAL,
                    "duration": 60,
                    "cool_down": 600,
                    "notification_channels": ["discord"]
                },
                {
                    "name": "磁碟空間不足",
                    "description": "磁碟使用率超過 85%",
                    "category": AlertCategory.STORAGE,
                    "metric": "disk_percent",
                    "condition": ">",
                    "threshold": 85.0,
                    "level": AlertLevel.WARNING,
                    "duration": 300,
                    "cool_down": 1800,
                    "notification_channels": ["discord"]
                },
                {
                    "name": "系統負載過高",
                    "description": "1分鐘平均負載超過 CPU 核心數",
                    "category": AlertCategory.PERFORMANCE,
                    "metric": "load_avg_1min",
                    "condition": ">",
                    "threshold": 4.0,  # 將根據實際 CPU 核心數調整
                    "level": AlertLevel.WARNING,
                    "duration": 180,
                    "cool_down": 300,
                    "notification_channels": ["discord"]
                }
            ]
            
            for rule_data in default_rules:
                rule_id = str(uuid.uuid4())
                rule_data["id"] = rule_id
                rule = AlertRule(**rule_data)
                self.rules[rule_id] = rule
            
            self._save_rules()
    
    async def evaluate_metrics(self, metrics: Dict[str, float]):
        """評估指標並觸發警報"""
        current_time = datetime.now()
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            try:
                await self._evaluate_rule(rule, metrics, current_time)
            except Exception as e:
                logger.error(f"評估規則 {rule.name} 失敗: {e}")
    
    async def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, float], current_time: datetime):
        """評估單個規則"""
        metric_value = metrics.get(rule.metric)
        if metric_value is None:
            return
        
        # 檢查是否滿足觸發條件
        triggered = self._check_condition(metric_value, rule.condition, rule.threshold)
        
        # 獲取規則狀態
        if rule.id not in self.rule_states:
            self.rule_states[rule.id] = {
                "triggered_at": None,
                "last_check": current_time,
                "consecutive_triggers": 0,
                "last_notification": None
            }
        
        state = self.rule_states[rule.id]
        
        if triggered:
            if state["triggered_at"] is None:
                # 首次觸發
                state["triggered_at"] = current_time
                state["consecutive_triggers"] = 1
            else:
                state["consecutive_triggers"] += 1
                
                # 檢查是否達到持續時間要求
                trigger_duration = (current_time - state["triggered_at"]).total_seconds()
                if trigger_duration >= rule.duration:
                    # 檢查冷卻時間
                    if (state["last_notification"] is None or 
                        (current_time - state["last_notification"]).total_seconds() >= rule.cool_down):
                        
                        await self._create_incident(rule, metric_value, current_time)
                        state["last_notification"] = current_time
        else:
            # 條件不滿足，重置狀態
            if state["triggered_at"] is not None:
                # 如果之前有觸發，檢查是否需要自動解決警報
                if rule.auto_resolve:
                    await self._auto_resolve_incidents(rule.id, current_time)
                
                state["triggered_at"] = None
                state["consecutive_triggers"] = 0
        
        state["last_check"] = current_time
    
    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """檢查條件是否滿足"""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return abs(value - threshold) < 0.01
        elif condition == "!=":
            return abs(value - threshold) >= 0.01
        else:
            return False
    
    async def _create_incident(self, rule: AlertRule, metric_value: float, current_time: datetime):
        """創建警報事件"""
        incident_id = str(uuid.uuid4())
        
        incident = AlertIncident(
            id=incident_id,
            rule_id=rule.id,
            rule_name=rule.name,
            level=rule.level,
            category=rule.category,
            status=AlertStatus.ACTIVE,
            title=f"{rule.name} - {rule.level.value.upper()}",
            message=f"{rule.description or rule.name}。當前值: {metric_value:.2f}, 閾值: {rule.threshold}",
            metric_value=metric_value,
            threshold=rule.threshold,
            started_at=current_time,
            tags=rule.tags,
            context={"metric": rule.metric, "condition": rule.condition}
        )
        
        self.incidents[incident_id] = incident
        self.active_incidents[incident_id] = incident
        
        # 發送通知
        await self._send_notifications(incident, rule)
        
        # 保存數據
        self._save_incidents()
        
        logger.info(f"創建警報事件: {incident.title}")
    
    async def _auto_resolve_incidents(self, rule_id: str, current_time: datetime):
        """自動解決相關的警報事件"""
        for incident in list(self.active_incidents.values()):
            if incident.rule_id == rule_id and incident.status == AlertStatus.ACTIVE:
                incident.status = AlertStatus.RESOLVED
                incident.resolved_at = current_time
                
                if incident.id in self.active_incidents:
                    del self.active_incidents[incident.id]
                
                logger.info(f"自動解決警報事件: {incident.title}")
        
        self._save_incidents()
    
    async def _send_notifications(self, incident: AlertIncident, rule: AlertRule):
        """發送通知"""
        for channel in rule.notification_channels:
            try:
                await self._send_notification(incident, channel)
            except Exception as e:
                logger.error(f"發送通知到 {channel} 失敗: {e}")
    
    async def _send_notification(self, incident: AlertIncident, channel: str):
        """發送單個通知"""
        # 這裡可以整合不同的通知渠道
        if channel == "discord":
            await self._send_discord_notification(incident)
        elif channel == "email":
            await self._send_email_notification(incident)
        # 可以添加更多通知渠道
    
    async def _send_discord_notification(self, incident: AlertIncident):
        """發送 Discord 通知"""
        try:
            # 導入 Discord 監控器
            from app.core.monitors.discord import DiscordMonitor
            
            discord_monitor = DiscordMonitor()
            
            # 格式化訊息
            emoji = {
                AlertLevel.INFO: "ℹ️",
                AlertLevel.WARNING: "⚠️", 
                AlertLevel.CRITICAL: "🚨",
                AlertLevel.EMERGENCY: "🔥"
            }.get(incident.level, "📢")
            
            message = f"""
{emoji} **系統警報** {emoji}

**級別**: {incident.level.value.upper()}
**分類**: {incident.category.value}
**標題**: {incident.title}
**訊息**: {incident.message}
**時間**: {incident.started_at.strftime('%Y-%m-%d %H:%M:%S')}

請檢查系統狀態並採取適當行動。
"""
            
            await discord_monitor.send_message(message)
            
        except Exception as e:
            logger.error(f"發送 Discord 通知失敗: {e}")
    
    async def _send_email_notification(self, incident: AlertIncident):
        """發送郵件通知（預留接口）"""
        # TODO: 實現郵件通知
        pass
    
    def get_alert_summary(self) -> AlertSummary:
        """獲取警報摘要"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_alerts = len(self.incidents)
        active_alerts = len(self.active_incidents)
        critical_alerts = sum(1 for i in self.active_incidents.values() if i.level == AlertLevel.CRITICAL)
        warning_alerts = sum(1 for i in self.active_incidents.values() if i.level == AlertLevel.WARNING)
        acknowledged_alerts = sum(1 for i in self.active_incidents.values() if i.status == AlertStatus.ACKNOWLEDGED)
        
        # 今日已解決警報
        resolved_today = sum(1 for i in self.incidents.values() 
                           if i.resolved_at and i.resolved_at >= today_start)
        
        # 平均解決時間
        resolved_incidents = [i for i in self.incidents.values() if i.resolved_at]
        if resolved_incidents:
            total_resolution_time = sum(
                (i.resolved_at - i.started_at).total_seconds() / 60
                for i in resolved_incidents
            )
            avg_resolution_time = total_resolution_time / len(resolved_incidents)
        else:
            avg_resolution_time = 0.0
        
        # 主要警報類別
        category_counts = {}
        for incident in self.active_incidents.values():
            category = incident.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        top_categories = [
            {"name": cat, "count": count}
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return AlertSummary(
            total_alerts=total_alerts,
            active_alerts=active_alerts,
            critical_alerts=critical_alerts,
            warning_alerts=warning_alerts,
            acknowledged_alerts=acknowledged_alerts,
            resolved_today=resolved_today,
            avg_resolution_time=avg_resolution_time,
            top_categories=top_categories
        )
    
    def get_active_incidents(self) -> List[AlertIncident]:
        """獲取活躍的警報事件"""
        return list(self.active_incidents.values())
    
    def get_recent_incidents(self, hours: int = 24) -> List[AlertIncident]:
        """獲取最近的警報事件"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            incident for incident in self.incidents.values()
            if incident.started_at >= cutoff_time
        ]
    
    async def acknowledge_incident(self, incident_id: str, user: str = "system", comment: str = None):
        """確認警報事件"""
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            incident.status = AlertStatus.ACKNOWLEDGED
            incident.acknowledged_at = datetime.now()
            incident.acknowledged_by = user
            
            # 如果有註解，添加到上下文
            if comment:
                incident.context["acknowledgment_comment"] = comment
            
            self._save_incidents()
            logger.info(f"警報事件已確認: {incident.title} by {user}")
    
    async def resolve_incident(self, incident_id: str, comment: str = None):
        """解決警報事件"""
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            incident.status = AlertStatus.RESOLVED
            incident.resolved_at = datetime.now()
            
            if incident_id in self.active_incidents:
                del self.active_incidents[incident_id]
            
            if comment:
                incident.context["resolution_comment"] = comment
            
            self._save_incidents()
            logger.info(f"警報事件已解決: {incident.title}")
    
    async def suppress_incident(self, incident_id: str, duration_minutes: int = 60):
        """抑制警報事件"""
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            incident.status = AlertStatus.SUPPRESSED
            incident.suppressed_until = datetime.now() + timedelta(minutes=duration_minutes)
            
            self._save_incidents()
            logger.info(f"警報事件已抑制 {duration_minutes} 分鐘: {incident.title}")


# 全局警報引擎實例
alert_engine = AlertEngine()