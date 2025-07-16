"""
日誌監控 API 路由
"""
import sys
from typing import Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query

# 添加 MCP 模組路徑
sys.path.insert(0, '/home/bao/mcp_use')

from app.api.models.response import DataResponse
from app.api.models.system import LogEntry

router = APIRouter()

def get_log_monitor():
    """獲取日誌監控模組"""
    try:
        from mcp_servers.mcp_log_monitor import LogMonitor
        return LogMonitor()
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"無法導入日誌監控模組: {str(e)}")

@router.get("/logs", response_model=DataResponse)
async def get_logs(
    level: Optional[str] = Query(None, description="日誌級別過濾"),
    limit: int = Query(100, ge=1, le=1000, description="返回條數限制"),
    monitor: Any = Depends(get_log_monitor)
):
    """獲取日誌資訊"""
    try:
        if hasattr(monitor, 'get_logs'):
            data = monitor.get_logs(level=level, limit=limit)
        else:
            data = {
                'logs': [],
                'total': 0
            }
            
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取日誌資訊失敗: {str(e)}"
        )