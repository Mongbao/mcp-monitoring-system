"""
資源依賴關係分析資料模型
"""
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ResourceDependency(BaseModel):
    """資源依賴關係"""
    resource_name: str = Field(..., description="資源名稱")
    dependent_resources: List[str] = Field(default_factory=list, description="依賴的資源")
    dependency_strength: float = Field(..., description="依賴強度 (0-1)")
    correlation_coefficient: float = Field(..., description="相關係數 (-1 to 1)")
    description: str = Field(..., description="依賴關係描述")


class ResourceImpactAnalysis(BaseModel):
    """資源影響分析"""
    resource_name: str = Field(..., description="資源名稱")
    impact_score: float = Field(..., description="影響分數 (0-10)")
    affected_resources: List[str] = Field(default_factory=list, description="受影響的資源")
    cascade_effects: List[str] = Field(default_factory=list, description="連鎖效應")
    risk_level: str = Field(..., description="風險等級 (low/medium/high/critical)")
    mitigation_suggestions: List[str] = Field(default_factory=list, description="緩解建議")


class ResourceBottleneck(BaseModel):
    """資源瓶頸分析"""
    resource_name: str = Field(..., description="資源名稱")
    bottleneck_severity: float = Field(..., description="瓶頸嚴重程度 (0-10)")
    current_utilization: float = Field(..., description="當前使用率")
    threshold_percentage: float = Field(..., description="瓶頸閾值百分比")
    predicted_saturation_time: Optional[datetime] = Field(None, description="預測飽和時間")
    optimization_recommendations: List[str] = Field(default_factory=list, description="優化建議")


class SystemHealthIndex(BaseModel):
    """系統健康指數"""
    overall_score: float = Field(..., description="整體健康分數 (0-100)")
    cpu_health: float = Field(..., description="CPU 健康分數")
    memory_health: float = Field(..., description="記憶體健康分數")
    disk_health: float = Field(..., description="磁碟健康分數")
    network_health: float = Field(..., description="網路健康分數")
    stability_trend: str = Field(..., description="穩定性趨勢 (improving/stable/declining)")
    critical_issues: List[str] = Field(default_factory=list, description="關鍵問題")
    health_timestamp: datetime = Field(default_factory=datetime.now, description="健康檢查時間")


class ResourceOptimization(BaseModel):
    """資源優化建議"""
    resource_type: str = Field(..., description="資源類型")
    current_efficiency: float = Field(..., description="當前效率 (0-100)")
    optimization_potential: float = Field(..., description="優化潛力 (0-100)")
    recommended_actions: List[str] = Field(default_factory=list, description="建議行動")
    expected_improvement: float = Field(..., description="預期改善百分比")
    implementation_difficulty: str = Field(..., description="實施難度 (easy/medium/hard)")
    priority_level: str = Field(..., description="優先級 (low/medium/high/critical)")


class ProcessDependencyMap(BaseModel):
    """進程依賴關係圖"""
    process_name: str = Field(..., description="進程名稱")
    process_id: int = Field(..., description="進程ID")
    parent_processes: List[str] = Field(default_factory=list, description="父進程")
    child_processes: List[str] = Field(default_factory=list, description="子進程")
    shared_resources: List[str] = Field(default_factory=list, description="共享資源")
    resource_consumption: Dict[str, float] = Field(default_factory=dict, description="資源消耗")
    criticality_level: str = Field(..., description="關鍵程度 (low/medium/high/critical)")