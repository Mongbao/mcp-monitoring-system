"""
I/O 分析數據模型
"""
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DiskIOStats(BaseModel):
    """磁碟 I/O 統計"""
    device_name: str = Field(..., description="設備名稱")
    read_bytes: int = Field(..., description="讀取位元組數")
    write_bytes: int = Field(..., description="寫入位元組數")
    read_ops: int = Field(..., description="讀取操作數")
    write_ops: int = Field(..., description="寫入操作數")
    read_time_ms: int = Field(..., description="讀取時間（毫秒）")
    write_time_ms: int = Field(..., description="寫入時間（毫秒）")
    io_in_progress: int = Field(..., description="進行中的 I/O 操作")


class NetworkIOStats(BaseModel):
    """網路 I/O 統計"""
    interface_name: str = Field(..., description="網路介面名稱")
    bytes_sent: int = Field(..., description="發送位元組數")
    bytes_recv: int = Field(..., description="接收位元組數")
    packets_sent: int = Field(..., description="發送封包數")
    packets_recv: int = Field(..., description="接收封包數")
    errors_in: int = Field(..., description="接收錯誤數")
    errors_out: int = Field(..., description="發送錯誤數")
    drops_in: int = Field(..., description="接收丟棄數")
    drops_out: int = Field(..., description="發送丟棄數")


class ProcessIOStats(BaseModel):
    """進程 I/O 統計"""
    pid: int = Field(..., description="進程 ID")
    process_name: str = Field(..., description="進程名稱")
    read_bytes: int = Field(..., description="讀取位元組數")
    write_bytes: int = Field(..., description="寫入位元組數")
    read_chars: int = Field(..., description="讀取字符數")
    write_chars: int = Field(..., description="寫入字符數")
    read_syscalls: int = Field(..., description="讀取系統調用數")
    write_syscalls: int = Field(..., description="寫入系統調用數")


class IOPerformanceMetrics(BaseModel):
    """I/O 性能指標"""
    timestamp: datetime = Field(..., description="時間戳")
    disk_io_stats: List[DiskIOStats] = Field(default_factory=list, description="磁碟 I/O 統計")
    network_io_stats: List[NetworkIOStats] = Field(default_factory=list, description="網路 I/O 統計")
    top_io_processes: List[ProcessIOStats] = Field(default_factory=list, description="Top I/O 進程")
    total_disk_read_rate: float = Field(..., description="總磁碟讀取速率 (MB/s)")
    total_disk_write_rate: float = Field(..., description="總磁碟寫入速率 (MB/s)")
    total_network_in_rate: float = Field(..., description="總網路接收速率 (MB/s)")
    total_network_out_rate: float = Field(..., description="總網路發送速率 (MB/s)")


class IOBottleneckAnalysis(BaseModel):
    """I/O 瓶頸分析"""
    bottleneck_type: str = Field(..., description="瓶頸類型 (disk/network/process)")
    resource_name: str = Field(..., description="資源名稱")
    severity_score: float = Field(..., description="嚴重程度分數 (0-10)")
    current_utilization: float = Field(..., description="當前使用率 (%)")
    max_throughput: float = Field(..., description="最大吞吐量")
    current_throughput: float = Field(..., description="當前吞吐量")
    impact_description: str = Field(..., description="影響描述")
    optimization_suggestions: List[str] = Field(default_factory=list, description="優化建議")


class IOTrendAnalysis(BaseModel):
    """I/O 趨勢分析"""
    metric_name: str = Field(..., description="指標名稱")
    trend_direction: str = Field(..., description="趨勢方向 (increasing/stable/decreasing)")
    change_rate: float = Field(..., description="變化率 (%/hour)")
    peak_time: Optional[datetime] = Field(None, description="峰值時間")
    peak_value: float = Field(..., description="峰值")
    average_value: float = Field(..., description="平均值")
    prediction_next_hour: float = Field(..., description="下一小時預測值")


class FileSystemAnalysis(BaseModel):
    """檔案系統分析"""
    mount_point: str = Field(..., description="掛載點")
    file_system_type: str = Field(..., description="檔案系統類型")
    total_space: int = Field(..., description="總空間 (bytes)")
    used_space: int = Field(..., description="已使用空間 (bytes)")
    free_space: int = Field(..., description="可用空間 (bytes)")
    usage_percentage: float = Field(..., description="使用率 (%)")
    inode_total: int = Field(..., description="總 inode 數")
    inode_used: int = Field(..., description="已使用 inode 數")
    inode_usage_percentage: float = Field(..., description="inode 使用率 (%)")
    fragmentation_level: Optional[float] = Field(None, description="碎片化程度 (%)")


class IOInsight(BaseModel):
    """I/O 洞察"""
    insight_type: str = Field(..., description="洞察類型")
    title: str = Field(..., description="標題")
    description: str = Field(..., description="描述")
    severity: str = Field(..., description="嚴重程度 (info/warning/critical)")
    affected_resources: List[str] = Field(default_factory=list, description="受影響的資源")
    recommended_actions: List[str] = Field(default_factory=list, description="建議行動")
    confidence: float = Field(..., description="信心度 (0-1)")
    detected_at: datetime = Field(default_factory=datetime.now, description="檢測時間")


class IOSummary(BaseModel):
    """I/O 摘要"""
    analysis_period: str = Field(..., description="分析期間")
    total_disk_read: float = Field(..., description="總磁碟讀取 (GB)")
    total_disk_write: float = Field(..., description="總磁碟寫入 (GB)")
    total_network_in: float = Field(..., description="總網路接收 (GB)")
    total_network_out: float = Field(..., description="總網路發送 (GB)")
    peak_disk_io_time: Optional[datetime] = Field(None, description="磁碟 I/O 峰值時間")
    peak_network_io_time: Optional[datetime] = Field(None, description="網路 I/O 峰值時間")
    bottlenecks_detected: int = Field(..., description="檢測到的瓶頸數量")
    optimization_opportunities: int = Field(..., description="優化機會數量")
    overall_io_health_score: float = Field(..., description="整體 I/O 健康分數 (0-100)")