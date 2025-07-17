"""
系統監控 API 路由
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends

from app.api.models.response import DataResponse, ErrorResponse
from app.api.models.system import SystemInfo
from app.core.monitors.base import SystemMonitor
from app.config import settings

router = APIRouter()

def get_system_monitor():
    """獲取系統監控模組"""
    return SystemMonitor()

@router.get("/system", response_model=DataResponse)
async def get_system_info(monitor: SystemMonitor = Depends(get_system_monitor)):
    """獲取系統資訊"""
    try:
        data = monitor.get_system_info()
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取系統資訊失敗: {str(e)}"
        )

@router.get("/system/quick-status", response_model=DataResponse)
async def get_quick_status(monitor: SystemMonitor = Depends(get_system_monitor)):
    """獲取系統快速狀態指標"""
    try:
        import psutil
        
        # 獲取基本系統指標
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 計算負載平均值
        try:
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else cpu_percent / 100
        except:
            load_avg = cpu_percent / 100
        
        data = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "load_avg": load_avg,
            "memory_used": memory.used,
            "memory_total": memory.total,
            "disk_used": disk.used,
            "disk_total": disk.total
        }
        
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取系統快速狀態失敗: {str(e)}"
        )

@router.get("/system/detailed", response_model=DataResponse)
async def get_detailed_status(monitor: SystemMonitor = Depends(get_system_monitor)):
    """獲取詳細系統狀態"""
    try:
        data = monitor.get_system_info()
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取詳細系統狀態失敗: {str(e)}"
        )