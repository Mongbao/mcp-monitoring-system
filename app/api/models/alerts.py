"""
智能警報系統數據模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AlertLevel(str, Enum):
    """警報級別"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(str, Enum):
    """警報狀態"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertCategory(str, Enum):
    """警報類別"""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SERVICE = "service"
    NETWORK = "network"
    STORAGE = "storage"


class AlertRule(BaseModel):
    """警報規則"""
    id: str = Field(..., description="規則ID")
    name: str = Field(..., description="規則名稱")
    description: Optional[str] = Field(None, description="規則描述")
    category: AlertCategory = Field(..., description="警報類別")
    metric: str = Field(..., description="監控指標")
    condition: str = Field(..., description="觸發條件 (>, <, ==, !=, etc.)")
    threshold: float = Field(..., description="閾值")
    level: AlertLevel = Field(..., description="警報級別")
    enabled: bool = Field(True, description="是否啟用")
    duration: int = Field(60, description="持續時間（秒）")
    cool_down: int = Field(300, description="冷卻時間（秒）")
    auto_resolve: bool = Field(True, description="是否自動解決")
    notification_channels: List[str] = Field(default_factory=list, description="通知渠道")
    tags: Dict[str, str] = Field(default_factory=dict, description="標籤")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")


class AlertIncident(BaseModel):
    """警報事件"""
    id: str = Field(..., description="事件ID")
    rule_id: str = Field(..., description="規則ID")
    rule_name: str = Field(..., description="規則名稱")
    level: AlertLevel = Field(..., description="警報級別")
    category: AlertCategory = Field(..., description="警報類別")
    status: AlertStatus = Field(..., description="警報狀態")
    title: str = Field(..., description="警報標題")
    message: str = Field(..., description="警報訊息")
    metric_value: float = Field(..., description="觸發時的指標值")
    threshold: float = Field(..., description="閾值")
    started_at: datetime = Field(..., description="開始時間")
    resolved_at: Optional[datetime] = Field(None, description="解決時間")
    acknowledged_at: Optional[datetime] = Field(None, description="確認時間")
    acknowledged_by: Optional[str] = Field(None, description="確認用戶")
    last_notification: Optional[datetime] = Field(None, description="最後通知時間")
    notification_count: int = Field(0, description="通知次數")
    suppressed_until: Optional[datetime] = Field(None, description="抑制到期時間")
    tags: Dict[str, str] = Field(default_factory=dict, description="標籤")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class AlertSummary(BaseModel):
    """警報摘要"""
    total_alerts: int = Field(..., description="總警報數")
    active_alerts: int = Field(..., description="活躍警報數")
    critical_alerts: int = Field(..., description="嚴重警報數")
    warning_alerts: int = Field(..., description="警告警報數")
    acknowledged_alerts: int = Field(..., description="已確認警報數")
    resolved_today: int = Field(..., description="今日已解決警報數")
    avg_resolution_time: float = Field(..., description="平均解決時間（分鐘）")
    top_categories: List[Dict[str, Any]] = Field(default_factory=list, description="主要警報類別")


class AlertNotification(BaseModel):
    """警報通知"""
    id: str = Field(..., description="通知ID")
    incident_id: str = Field(..., description="事件ID")
    channel: str = Field(..., description="通知渠道")
    status: str = Field(..., description="發送狀態")
    sent_at: datetime = Field(..., description="發送時間")
    response: Optional[str] = Field(None, description="回應內容")
    error: Optional[str] = Field(None, description="錯誤信息")


class AlertRuleCreate(BaseModel):
    """創建警報規則請求"""
    name: str = Field(..., description="規則名稱")
    description: Optional[str] = Field(None, description="規則描述")
    category: AlertCategory = Field(..., description="警報類別")
    metric: str = Field(..., description="監控指標")
    condition: str = Field(..., description="觸發條件")
    threshold: float = Field(..., description="閾值")
    level: AlertLevel = Field(..., description="警報級別")
    duration: int = Field(60, description="持續時間（秒）", ge=1, le=3600)
    cool_down: int = Field(300, description="冷卻時間（秒）", ge=60, le=7200)
    notification_channels: List[str] = Field(default_factory=list, description="通知渠道")
    tags: Dict[str, str] = Field(default_factory=dict, description="標籤")


class AlertRuleUpdate(BaseModel):
    """更新警報規則請求"""
    name: Optional[str] = Field(None, description="規則名稱")
    description: Optional[str] = Field(None, description="規則描述")
    threshold: Optional[float] = Field(None, description="閾值")
    level: Optional[AlertLevel] = Field(None, description="警報級別")
    enabled: Optional[bool] = Field(None, description="是否啟用")
    duration: Optional[int] = Field(None, description="持續時間（秒）", ge=1, le=3600)
    cool_down: Optional[int] = Field(None, description="冷卻時間（秒）", ge=60, le=7200)
    notification_channels: Optional[List[str]] = Field(None, description="通知渠道")
    tags: Optional[Dict[str, str]] = Field(None, description="標籤")


class AlertIncidentAction(BaseModel):
    """警報事件操作"""
    action: str = Field(..., description="操作類型 (acknowledge, resolve, suppress)")
    comment: Optional[str] = Field(None, description="操作備註")
    suppress_duration: Optional[int] = Field(None, description="抑制持續時間（分鐘）")