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