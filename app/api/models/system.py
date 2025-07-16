"""
系統監控數據模型
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SystemInfo(BaseModel):
    """系統資訊模型"""
    cpu_percent: float = Field(..., description="CPU 使用率百分比")
    memory_percent: float = Field(..., description="記憶體使用率百分比")
    disk_percent: float = Field(..., description="磁碟使用率百分比")
    load_avg: str = Field(..., description="系統負載平均值")
    uptime: str = Field(..., description="系統運行時間")
    boot_time: Optional[datetime] = Field(None, description="系統啟動時間")
    
class ProcessInfo(BaseModel):
    """進程資訊模型"""
    total_processes: int = Field(..., description="總進程數")
    running_processes: int = Field(..., description="運行中進程數")
    sleeping_processes: int = Field(..., description="休眠進程數")
    zombie_processes: int = Field(..., description="殭屍進程數")
    
class ProcessDetail(BaseModel):
    """進程詳細資訊模型"""
    pid: int = Field(..., description="進程 ID")
    name: str = Field(..., description="進程名稱")
    cpu_percent: float = Field(..., description="CPU 使用率")
    memory_percent: float = Field(..., description="記憶體使用率")
    status: str = Field(..., description="進程狀態")
    username: str = Field(..., description="用戶名")
    command: str = Field(..., description="命令行")
    create_time: datetime = Field(..., description="建立時間")

class NetworkInfo(BaseModel):
    """網路資訊模型"""
    bytes_sent: int = Field(..., description="發送位元組數")
    bytes_recv: int = Field(..., description="接收位元組數")
    packets_sent: int = Field(..., description="發送封包數")
    packets_recv: int = Field(..., description="接收封包數")
    interface_count: int = Field(..., description="網路介面數量")
    connections: int = Field(..., description="網路連線數")

class FilesystemInfo(BaseModel):
    """檔案系統資訊模型"""
    monitored_paths: int = Field(..., description="監控路徑數")
    total_space: int = Field(..., description="總空間")
    free_space: int = Field(..., description="可用空間")
    used_space: int = Field(..., description="已用空間")
    usage_percent: float = Field(..., description="使用率百分比")

class HealthScore(BaseModel):
    """健康度評分模型"""
    overall: float = Field(..., description="整體健康度評分")
    cpu: float = Field(..., description="CPU 評分")
    memory: float = Field(..., description="記憶體評分")
    disk: float = Field(..., description="磁碟評分")
    process: float = Field(..., description="進程評分")
    timestamp: datetime = Field(default_factory=datetime.now, description="評分時間")

class AlertInfo(BaseModel):
    """警報資訊模型"""
    alert_count: int = Field(..., description="警報數量")
    critical_count: int = Field(..., description="嚴重警報數量")
    warning_count: int = Field(..., description="警告數量")
    current_alerts: List[Dict] = Field(default_factory=list, description="當前警報列表")

class LogEntry(BaseModel):
    """日誌條目模型"""
    timestamp: datetime = Field(..., description="時間戳")
    level: str = Field(..., description="日誌級別")
    message: str = Field(..., description="日誌訊息")
    source: Optional[str] = Field(None, description="日誌來源")
    
class ServiceInfo(BaseModel):
    """服務資訊模型"""
    name: str = Field(..., description="服務名稱")
    status: str = Field(..., description="服務狀態")
    pid: Optional[int] = Field(None, description="進程 ID")
    cpu_percent: float = Field(0.0, description="CPU 使用率")
    memory_percent: float = Field(0.0, description="記憶體使用率")
    memory_mb: float = Field(0.0, description="記憶體使用量(MB)")
    uptime: Optional[str] = Field(None, description="運行時間")
    
class TrendData(BaseModel):
    """趨勢數據模型"""
    timestamp: datetime = Field(..., description="時間戳")
    overall_score: float = Field(..., description="整體評分")
    cpu_score: float = Field(..., description="CPU 評分")
    memory_score: float = Field(..., description="記憶體評分")
    disk_score: float = Field(..., description="磁碟評分")