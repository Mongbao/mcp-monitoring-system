"""
警報閾值模型
"""
from typing import Dict
from pydantic import BaseModel, Field

class ThresholdConfig(BaseModel):
    """單項閾值配置模型"""
    warning: float = Field(..., description="警告閾值", ge=0, le=100)
    critical: float = Field(..., description="嚴重閾值", ge=0, le=100)

class LoadThresholdConfig(BaseModel):
    """負載閾值配置模型"""
    warning: float = Field(..., description="警告閾值", ge=0)
    critical: float = Field(..., description="嚴重閾值", ge=0)

class AlertThresholds(BaseModel):
    """警報閾值模型"""
    cpu: ThresholdConfig = Field(..., description="CPU 閾值")
    memory: ThresholdConfig = Field(..., description="記憶體閾值")
    disk: ThresholdConfig = Field(..., description="磁碟閾值")
    load: LoadThresholdConfig = Field(..., description="負載閾值")

class ThresholdUpdateRequest(BaseModel):
    """閾值更新請求模型"""
    cpu_warning: float = Field(..., description="CPU 警告閾值", ge=0, le=100)
    cpu_critical: float = Field(..., description="CPU 嚴重閾值", ge=0, le=100)
    memory_warning: float = Field(..., description="記憶體警告閾值", ge=0, le=100)
    memory_critical: float = Field(..., description="記憶體嚴重閾值", ge=0, le=100)
    disk_warning: float = Field(..., description="磁碟警告閾值", ge=0, le=100)
    disk_critical: float = Field(..., description="磁碟嚴重閾值", ge=0, le=100)
    load_warning: float = Field(..., description="負載警告閾值", ge=0)
    load_critical: float = Field(..., description="負載嚴重閾值", ge=0)