"""
資源依賴關係分析 API 路由
"""
import sys
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

# 添加 MCP 模組路徑
sys.path.insert(0, '/home/bao/mcp_use')

from app.api.models.response import DataResponse
from app.api.models.dependencies import (
    ResourceDependency, ResourceImpactAnalysis, ResourceBottleneck,
    SystemHealthIndex, ResourceOptimization
)
from app.core.analytics.collector import metrics_collector
from app.core.analytics.dependency_analyzer import dependency_analyzer

router = APIRouter()


@router.get("/resource-dependencies", response_model=DataResponse)
async def get_resource_dependencies(
    hours: int = Query(24, ge=1, le=168, description="分析時間範圍（小時）")
):
    """獲取資源依賴關係分析"""
    try:
        # 獲取歷史數據
        historical_data = metrics_collector.get_historical_data(hours=hours)
        
        if len(historical_data) < 10:
            return DataResponse(
                data={
                    "dependencies": [],
                    "message": "數據不足，需要至少 10 個數據點進行依賴分析",
                    "data_points": len(historical_data)
                }
            )
        
        # 分析資源依賴關係
        dependencies = dependency_analyzer.analyze_resource_dependencies(historical_data)
        
        # 轉換為字典格式
        dependencies_data = [dep.dict() for dep in dependencies]
        
        return DataResponse(
            data={
                "dependencies": dependencies_data,
                "total_dependencies": len(dependencies_data),
                "analysis_period_hours": hours,
                "data_points_analyzed": len(historical_data),
                "message": f"分析了 {len(dependencies_data)} 個資源依賴關係"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取資源依賴關係失敗: {str(e)}"
        )


@router.get("/resource-impact", response_model=DataResponse)
async def get_resource_impact_analysis():
    """獲取資源影響分析"""
    try:
        # 獲取當前指標
        current_data = metrics_collector.get_historical_data(hours=1)
        
        if not current_data:
            raise HTTPException(
                status_code=400,
                detail="無法獲取當前系統指標"
            )
        
        current_metrics = current_data[-1]  # 最新的指標
        
        # 分析資源影響
        impacts = dependency_analyzer.analyze_resource_impact(current_metrics)
        
        # 轉換為字典格式
        impacts_data = [impact.dict() for impact in impacts]
        
        return DataResponse(
            data={
                "impacts": impacts_data,
                "total_impacts": len(impacts_data),
                "high_risk_count": len([i for i in impacts if i.risk_level in ['high', 'critical']]),
                "message": f"分析了 {len(impacts_data)} 個資源影響"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取資源影響分析失敗: {str(e)}"
        )


@router.get("/bottlenecks", response_model=DataResponse)
async def get_resource_bottlenecks(
    hours: int = Query(6, ge=1, le=24, description="分析時間範圍（小時）")
):
    """獲取資源瓶頸分析"""
    try:
        # 獲取歷史數據
        historical_data = metrics_collector.get_historical_data(hours=hours)
        
        if not historical_data:
            raise HTTPException(
                status_code=400,
                detail="無法獲取歷史數據"
            )
        
        # 識別瓶頸
        bottlenecks = dependency_analyzer.identify_bottlenecks(historical_data)
        
        # 轉換為字典格式
        bottlenecks_data = []
        for bottleneck in bottlenecks:
            bottleneck_dict = bottleneck.dict()
            if bottleneck_dict['predicted_saturation_time']:
                bottleneck_dict['predicted_saturation_time'] = bottleneck_dict['predicted_saturation_time'].isoformat()
            bottlenecks_data.append(bottleneck_dict)
        
        return DataResponse(
            data={
                "bottlenecks": bottlenecks_data,
                "total_bottlenecks": len(bottlenecks_data),
                "critical_bottlenecks": len([b for b in bottlenecks if b.bottleneck_severity > 7]),
                "analysis_period_hours": hours,
                "message": f"識別了 {len(bottlenecks_data)} 個資源瓶頸"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取資源瓶頸分析失敗: {str(e)}"
        )


@router.get("/system-health", response_model=DataResponse)
async def get_system_health_index(
    hours: int = Query(6, ge=1, le=24, description="分析時間範圍（小時）")
):
    """獲取系統健康指數"""
    try:
        # 獲取當前指標和趨勢數據
        current_data = metrics_collector.get_historical_data(hours=1)
        trend_data = metrics_collector.get_historical_data(hours=hours)
        
        if not current_data:
            raise HTTPException(
                status_code=400,
                detail="無法獲取當前系統指標"
            )
        
        current_metrics = current_data[-1]  # 最新的指標
        
        # 計算系統健康指數
        health_index = dependency_analyzer.calculate_system_health_index(
            current_metrics, trend_data
        )
        
        # 轉換為字典格式
        health_data = health_index.dict()
        health_data['health_timestamp'] = health_data['health_timestamp'].isoformat()
        
        return DataResponse(
            data={
                "health_index": health_data,
                "analysis_period_hours": hours,
                "data_points_analyzed": len(trend_data),
                "message": f"系統健康指數: {health_index.overall_score:.1f}/100"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取系統健康指數失敗: {str(e)}"
        )


@router.get("/optimization-recommendations", response_model=DataResponse)
async def get_optimization_recommendations():
    """獲取資源優化建議"""
    try:
        # 獲取當前指標
        current_data = metrics_collector.get_historical_data(hours=1)
        
        if not current_data:
            raise HTTPException(
                status_code=400,
                detail="無法獲取當前系統指標"
            )
        
        current_metrics = current_data[-1]
        recommendations = []
        
        # CPU 優化建議
        cpu_percent = current_metrics.get('cpu_percent', 0)
        if cpu_percent > 70:
            cpu_optimization = ResourceOptimization(
                resource_type="CPU",
                current_efficiency=max(0, 100 - cpu_percent),
                optimization_potential=min(30, cpu_percent - 50) if cpu_percent > 50 else 0,
                recommended_actions=[
                    "分析高 CPU 使用率進程",
                    "優化進程排程",
                    "考慮負載平衡"
                ],
                expected_improvement=min(20, (cpu_percent - 70) * 0.5) if cpu_percent > 70 else 0,
                implementation_difficulty="medium",
                priority_level="high" if cpu_percent > 85 else "medium"
            )
            recommendations.append(cpu_optimization)
        
        # 記憶體優化建議
        memory_percent = current_metrics.get('memory_percent', 0)
        if memory_percent > 75:
            memory_optimization = ResourceOptimization(
                resource_type="Memory",
                current_efficiency=max(0, 100 - memory_percent),
                optimization_potential=min(25, memory_percent - 60) if memory_percent > 60 else 0,
                recommended_actions=[
                    "清理記憶體快取",
                    "重啟記憶體洩漏進程",
                    "優化記憶體使用"
                ],
                expected_improvement=min(15, (memory_percent - 75) * 0.3) if memory_percent > 75 else 0,
                implementation_difficulty="easy",
                priority_level="critical" if memory_percent > 90 else "high"
            )
            recommendations.append(memory_optimization)
        
        # 磁碟優化建議
        disk_percent = current_metrics.get('disk_percent', 0)
        if disk_percent > 80:
            disk_optimization = ResourceOptimization(
                resource_type="Disk",
                current_efficiency=max(0, 100 - disk_percent),
                optimization_potential=min(20, disk_percent - 70) if disk_percent > 70 else 0,
                recommended_actions=[
                    "清理臨時檔案",
                    "壓縮舊日誌",
                    "移除不必要檔案"
                ],
                expected_improvement=min(10, (disk_percent - 80) * 0.2) if disk_percent > 80 else 0,
                implementation_difficulty="easy",
                priority_level="critical" if disk_percent > 95 else "medium"
            )
            recommendations.append(disk_optimization)
        
        # 轉換為字典格式
        recommendations_data = [rec.dict() for rec in recommendations]
        
        return DataResponse(
            data={
                "recommendations": recommendations_data,
                "total_recommendations": len(recommendations_data),
                "high_priority_count": len([r for r in recommendations if r.priority_level in ['high', 'critical']]),
                "total_potential_improvement": sum(r.optimization_potential for r in recommendations),
                "message": f"生成了 {len(recommendations_data)} 個優化建議"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取優化建議失敗: {str(e)}"
        )