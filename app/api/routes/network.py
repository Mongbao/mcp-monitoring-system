"""
網路監控 API 路由
"""
from typing import Any
from fastapi import APIRouter, HTTPException, Depends

from app.api.models.response import DataResponse
from app.api.models.system import NetworkInfo
from app.core.monitors.base import NetworkMonitor

router = APIRouter()

def get_network_monitor():
    """獲取網路監控模組"""
    return NetworkMonitor()

@router.get("/network", response_model=DataResponse)
async def get_network_info(monitor: NetworkMonitor = Depends(get_network_monitor)):
    """獲取網路資訊"""
    try:
        data = monitor.get_network_info()
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取網路資訊失敗: {str(e)}"
        )