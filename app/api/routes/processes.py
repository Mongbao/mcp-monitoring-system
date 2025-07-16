"""
進程監控 API 路由
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from app.api.models.response import DataResponse, PaginatedResponse
from app.api.models.system import ProcessInfo
from app.core.monitors.base import ProcessMonitor

router = APIRouter()

def get_process_monitor():
    """獲取進程監控模組"""
    return ProcessMonitor()

@router.get("/processes", response_model=DataResponse)
async def get_process_info(monitor: ProcessMonitor = Depends(get_process_monitor)):
    """獲取進程資訊"""
    try:
        data = monitor.get_process_info()
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取進程資訊失敗: {str(e)}"
        )

@router.get("/processes/detailed", response_model=PaginatedResponse)
async def get_detailed_processes(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(50, ge=1, le=200, description="每頁數量"),
    sort_by: Optional[str] = Query("cpu", description="排序欄位"),
    monitor: Any = Depends(get_process_monitor)
):
    """獲取詳細進程資訊（分頁）"""
    try:
        if hasattr(monitor, 'get_detailed_processes'):
            data = monitor.get_detailed_processes(page=page, page_size=page_size, sort_by=sort_by)
        else:
            data = {
                'processes': [],
                'total': 0,
                'page': page,
                'page_size': page_size
            }
            
        total_pages = max(1, (data.get('total', 0) + page_size - 1) // page_size)
        
        return PaginatedResponse(
            data=data.get('processes', []),
            count=data.get('total', 0),
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取詳細進程資訊失敗: {str(e)}"
        )