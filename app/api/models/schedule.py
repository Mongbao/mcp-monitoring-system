#!/usr/bin/env python3
"""
排程配置模型
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from enum import Enum

class ScheduleType(str, Enum):
    """排程類型"""
    DAILY = "daily"
    WEEKLY = "weekly"
    HOURLY = "hourly"
    CUSTOM = "custom"

class ScheduleStatus(str, Enum):
    """排程狀態"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"

class WeekDay(str, Enum):
    """週幾"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class ScheduleConfig(BaseModel):
    """排程配置"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100, description="排程名稱")
    description: Optional[str] = Field(None, max_length=500, description="排程描述")
    
    # 排程類型和狀態
    type: ScheduleType = Field(..., description="排程類型")
    status: ScheduleStatus = Field(default=ScheduleStatus.ACTIVE, description="排程狀態")
    
    # 時間設定
    time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="執行時間 (HH:MM)")
    timezone: str = Field(default="Asia/Taipei", description="時區")
    
    # 週期設定
    weekdays: Optional[List[WeekDay]] = Field(None, description="每週哪幾天執行（僅 weekly 類型）")
    interval_hours: Optional[int] = Field(None, ge=1, le=168, description="間隔小時數（僅 hourly 類型）")
    
    # 報告設定
    include_system_info: bool = Field(default=True, description="包含系統資訊")
    include_process_info: bool = Field(default=True, description="包含進程資訊")
    include_network_info: bool = Field(default=True, description="包含網路資訊")
    include_alerts: bool = Field(default=True, description="包含警報資訊")
    include_charts: bool = Field(default=False, description="包含圖表（暫不支援）")
    
    # 自訂報告內容
    custom_message: Optional[str] = Field(None, max_length=1000, description="自訂訊息前綴")
    
    # 執行記錄
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="建立時間")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新時間")
    last_run: Optional[datetime] = Field(None, description="上次執行時間")
    next_run: Optional[datetime] = Field(None, description="下次執行時間")
    run_count: int = Field(default=0, description="執行次數")
    
    @validator('weekdays')
    def validate_weekdays(cls, v, values):
        if values.get('type') == ScheduleType.WEEKLY and not v:
            raise ValueError('weekly 類型必須指定 weekdays')
        return v
    
    @validator('interval_hours')
    def validate_interval_hours(cls, v, values):
        if values.get('type') == ScheduleType.HOURLY and not v:
            raise ValueError('hourly 類型必須指定 interval_hours')
        return v

class ScheduleCreateRequest(BaseModel):
    """建立排程請求"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: ScheduleType
    time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: str = Field(default="Asia/Taipei")
    weekdays: Optional[List[WeekDay]] = None
    interval_hours: Optional[int] = Field(None, ge=1, le=168)
    include_system_info: bool = Field(default=True)
    include_process_info: bool = Field(default=True)
    include_network_info: bool = Field(default=True)
    include_alerts: bool = Field(default=True)
    include_charts: bool = Field(default=False)
    custom_message: Optional[str] = Field(None, max_length=1000)

class ScheduleUpdateRequest(BaseModel):
    """更新排程請求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[ScheduleType] = None
    status: Optional[ScheduleStatus] = None
    time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: Optional[str] = None
    weekdays: Optional[List[WeekDay]] = None
    interval_hours: Optional[int] = Field(None, ge=1, le=168)
    include_system_info: Optional[bool] = None
    include_process_info: Optional[bool] = None
    include_network_info: Optional[bool] = None
    include_alerts: Optional[bool] = None
    include_charts: Optional[bool] = None
    custom_message: Optional[str] = Field(None, max_length=1000)

class ScheduleExecutionLog(BaseModel):
    """排程執行日誌"""
    id: Optional[str] = None
    schedule_id: str
    executed_at: datetime
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    discord_message_id: Optional[str] = None