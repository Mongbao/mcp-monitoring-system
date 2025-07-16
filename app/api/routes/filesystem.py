"""
檔案系統監控 API 路由
"""
from typing import Any
from fastapi import APIRouter, HTTPException, Depends

from app.api.models.response import DataResponse
from app.api.models.system import FilesystemInfo
from app.core.monitors.base import FilesystemMonitor

router = APIRouter()

def get_filesystem_monitor():
    """獲取檔案系統監控模組"""
    return FilesystemMonitor()

@router.get("/filesystem", response_model=DataResponse)
async def get_filesystem_info(monitor: FilesystemMonitor = Depends(get_filesystem_monitor)):
    """獲取檔案系統資訊"""
    try:
        data = monitor.get_filesystem_info()
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取檔案系統資訊失敗: {str(e)}"
        )