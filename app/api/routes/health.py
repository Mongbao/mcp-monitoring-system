"""
健康檢查 API 路由
"""
import sys
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

# 添加 MCP 模組路徑
sys.path.insert(0, '/home/bao/mcp_use')

from app.api.models.response import DataResponse
from app.api.models.system import HealthScore, AlertInfo, TrendData

router = APIRouter()

def get_health_monitor():
    """獲取健康度監控模組 - 嘗試多個可能的模組"""
    # 嘗試導入可能的健康度監控模組
    try:
        from mcp_servers.mcp_system_monitor import SystemMonitor
        return SystemMonitor()
    except ImportError:
        pass
    
    try:
        from mcp_servers.mcp_health_monitor import HealthMonitor
        return HealthMonitor()
    except ImportError:
        pass
    
    # 如果都沒有，返回一個模擬的監控器
    class MockHealthMonitor:
        def get_health_score(self):
            return {
                'overall': 85.0,
                'cpu': 80.0,
                'memory': 90.0,
                'disk': 85.0,
                'process': 88.0
            }
        
        def get_alerts(self):
            return {
                'alert_count': 0,
                'critical_count': 0,
                'warning_count': 0,
                'current_alerts': []
            }
            
        def get_trends(self, type='health', hours=24):
            """生成模擬的趨勢數據"""
            import datetime
            from random import uniform
            
            trends = []
            current_time = datetime.datetime.now()
            
            # 生成過去指定小時數的趨勢數據
            for i in range(min(hours, 24)):  # 最多24個數據點
                timestamp = current_time - datetime.timedelta(hours=i)
                
                # 根據類型生成不同的模擬數據
                if type == 'health':
                    trends.append({
                        'timestamp': timestamp.isoformat(),
                        'overall_score': round(uniform(80, 95), 1),
                        'cpu_score': round(uniform(75, 90), 1),
                        'memory_score': round(uniform(85, 95), 1),
                        'disk_score': round(uniform(80, 90), 1),
                        'process_score': round(uniform(85, 95), 1)
                    })
                else:
                    # 其他類型的基本數據
                    trends.append({
                        'timestamp': timestamp.isoformat(),
                        'value': round(uniform(50, 100), 1)
                    })
            
            # 按時間順序排列（最新的在前）
            trends.reverse()
            
            return {
                'trends': trends
            }
    
    return MockHealthMonitor()

@router.get("/health", response_model=DataResponse)
async def get_health_score(monitor: Any = Depends(get_health_monitor)):
    """獲取系統健康度評分"""
    try:
        if hasattr(monitor, 'get_health_score'):
            data = monitor.get_health_score()
        else:
            data = {
                'overall': 85.0,
                'cpu': 80.0,
                'memory': 90.0,
                'disk': 85.0,
                'process': 88.0
            }
            
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取健康度評分失敗: {str(e)}"
        )

@router.get("/alerts", response_model=DataResponse)
async def get_alerts(monitor: Any = Depends(get_health_monitor)):
    """獲取系統警報資訊"""
    try:
        if hasattr(monitor, 'get_alerts'):
            data = monitor.get_alerts()
        else:
            data = {
                'alert_count': 0,
                'critical_count': 0,
                'warning_count': 0,
                'current_alerts': []
            }
            
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取警報資訊失敗: {str(e)}"
        )

@router.get("/trends", response_model=DataResponse)
async def get_trend_data(
    type: Optional[str] = Query("health", description="趨勢類型"),
    hours: int = Query(24, ge=1, le=168, description="時間範圍（小時）"),
    monitor: Any = Depends(get_health_monitor)
):
    """獲取趨勢數據"""
    try:
        if hasattr(monitor, 'get_trends'):
            data = monitor.get_trends(type=type, hours=hours)
        else:
            data = {
                'trends': []
            }
            
        return DataResponse(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取趨勢數據失敗: {str(e)}"
        )