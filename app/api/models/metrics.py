"""
歷史數據和趨勢分析數據模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MetricData(BaseModel):
    """指標數據點"""
    timestamp: datetime = Field(..., description="時間戳")
    cpu_percent: float = Field(..., description="CPU使用率")
    memory_percent: float = Field(..., description="記憶體使用率")
    disk_percent: float = Field(..., description="磁碟使用率")
    load_avg_1min: float = Field(..., description="1分鐘平均負載")
    load_avg_5min: float = Field(..., description="5分鐘平均負載")
    load_avg_15min: float = Field(..., description="15分鐘平均負載")
    network_bytes_sent: int = Field(0, description="網路發送位元組數")
    network_bytes_recv: int = Field(0, description="網路接收位元組數")
    process_count: int = Field(0, description="進程總數")
    running_processes: int = Field(0, description="運行中進程數")
    zombie_processes: int = Field(0, description="殭屍進程數")


class TrendAnalysis(BaseModel):
    """趨勢分析結果"""
    metric_name: str = Field(..., description="指標名稱")
    trend_direction: str = Field(..., description="趨勢方向 (上升/下降/穩定)")
    trend_percentage: float = Field(..., description="趨勢變化百分比")
    average_value: float = Field(..., description="平均值")
    min_value: float = Field(..., description="最小值")
    max_value: float = Field(..., description="最大值")
    standard_deviation: float = Field(..., description="標準差")
    prediction_next_hour: Optional[float] = Field(None, description="下一小時預測值")


class PerformanceBaseline(BaseModel):
    """性能基線"""
    metric_name: str = Field(..., description="指標名稱")
    baseline_average: float = Field(..., description="基線平均值")
    baseline_std: float = Field(..., description="基線標準差")
    upper_threshold: float = Field(..., description="上限閾值")
    lower_threshold: float = Field(..., description="下限閾值")
    confidence_level: float = Field(0.95, description="信心水準")
    sample_count: int = Field(..., description="樣本數量")
    last_updated: datetime = Field(..., description="最後更新時間")


class AnomalyDetection(BaseModel):
    """異常檢測結果"""
    timestamp: datetime = Field(..., description="檢測時間")
    metric_name: str = Field(..., description="指標名稱")
    actual_value: float = Field(..., description="實際值")
    expected_value: float = Field(..., description="期望值")
    anomaly_score: float = Field(..., description="異常分數 (0-1)")
    is_anomaly: bool = Field(..., description="是否為異常")
    severity: str = Field(..., description="嚴重程度 (low/medium/high)")
    description: str = Field(..., description="異常描述")


class MetricsSummary(BaseModel):
    """指標摘要"""
    time_range: str = Field(..., description="時間範圍")
    total_data_points: int = Field(..., description="數據點總數")
    metrics_overview: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="指標概覽")
    trend_analysis: List[TrendAnalysis] = Field(default_factory=list, description="趨勢分析")
    anomalies_detected: int = Field(0, description="檢測到的異常數量")
    performance_score: float = Field(..., description="整體性能分數")


class CapacityForecast(BaseModel):
    """容量預測"""
    metric_name: str = Field(..., description="指標名稱")
    current_usage: float = Field(..., description="當前使用率")
    predicted_usage_7d: float = Field(..., description="7天後預測使用率")
    predicted_usage_30d: float = Field(..., description="30天後預測使用率")
    capacity_exhaustion_date: Optional[datetime] = Field(None, description="容量耗盡日期")
    recommended_action: str = Field(..., description="建議行動")
    confidence: float = Field(..., description="預測信心度")


class SystemInsight(BaseModel):
    """系統洞察"""
    insight_type: str = Field(..., description="洞察類型")
    title: str = Field(..., description="標題")
    description: str = Field(..., description="描述")
    impact_level: str = Field(..., description="影響級別 (low/medium/high)")
    recommendation: str = Field(..., description="建議")
    confidence: float = Field(..., description="信心度")
    detected_at: datetime = Field(default_factory=datetime.now, description="檢測時間")


class HistoricalDataQuery(BaseModel):
    """歷史數據查詢參數"""
    start_time: Optional[datetime] = Field(None, description="開始時間")
    end_time: Optional[datetime] = Field(None, description="結束時間")
    hours: Optional[int] = Field(24, description="小時數（如果沒有指定具體時間）", ge=1, le=8760)
    metrics: Optional[List[str]] = Field(None, description="指定的指標名稱")
    aggregation: Optional[str] = Field("raw", description="聚合方式 (raw/minute/hour/day)")
    limit: Optional[int] = Field(1000, description="最大返回數量", ge=1, le=10000)