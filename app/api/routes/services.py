"""
服務監控 API 路由
"""
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from app.api.models.response import DataResponse, PaginatedResponse
from app.api.models.system import ServiceInfo
from app.core.monitors.base import ServiceMonitor

router = APIRouter()

def get_service_monitor():
    """獲取服務監控模組"""
    return ServiceMonitor()

@router.get("/services", response_model=DataResponse)
async def get_services_info(monitor: ServiceMonitor = Depends(get_service_monitor)):
    """獲取服務資訊"""
    try:
        data = monitor.get_services_info()
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取服務資訊失敗: {str(e)}"
        )

@router.get("/services/paginated", response_model=PaginatedResponse)
async def get_paginated_services(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(50, ge=1, le=200, description="每頁數量"),
    sort_by: Optional[str] = Query("name", description="排序欄位"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    status: Optional[str] = Query(None, description="狀態過濾"),
    monitor: ServiceMonitor = Depends(get_service_monitor)
):
    """獲取分頁服務資訊"""
    try:
        data = monitor.get_paginated_services(
            page=page, 
            page_size=page_size, 
            sort_by=sort_by,
            search=search,
            status=status
        )
            
        total_pages = max(1, (data.get('total', 0) + page_size - 1) // page_size)
        
        return PaginatedResponse(
            data=data.get('services', []),
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
            detail=f"獲取分頁服務資訊失敗: {str(e)}"
        )