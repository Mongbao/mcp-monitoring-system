"""
I/O 分析 API 路由
"""
import sys
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

# 添加 MCP 模組路徑
# 動態添加項目根目錄到 Python 路徑
from pathlib import Path
current_path = Path(__file__).parent
project_root = current_path
while project_root.parent != project_root:
    if (project_root / "app").exists():
        break
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

from app.api.models.response import DataResponse
from app.api.models.io_analysis import (
    IOPerformanceMetrics, IOBottleneckAnalysis, FileSystemAnalysis, 
    IOInsight, IOSummary
)
from app.core.analytics.io_analyzer import io_analyzer

router = APIRouter()


@router.get("/current-metrics", response_model=DataResponse)
async def get_current_io_metrics():
    """獲取當前 I/O 性能指標"""
    try:
        metrics = io_analyzer.collect_io_metrics()
        
        # 轉換為字典格式
        metrics_dict = metrics.dict()
        metrics_dict['timestamp'] = metrics_dict['timestamp'].isoformat()
        
        return DataResponse(
            data={
                "metrics": metrics_dict,
                "message": "成功收集 I/O 性能指標"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取 I/O 指標失敗: {str(e)}"
        )


@router.get("/bottlenecks", response_model=DataResponse)
async def get_io_bottlenecks(
    hours: int = Query(1, ge=1, le=24, description="分析時間範圍（小時）")
):
    """獲取 I/O 瓶頸分析"""
    try:
        bottlenecks = io_analyzer.analyze_io_bottlenecks(hours=hours)
        
        # 轉換為字典格式
        bottlenecks_data = [bottleneck.dict() for bottleneck in bottlenecks]
        
        return DataResponse(
            data={
                "bottlenecks": bottlenecks_data,
                "total_bottlenecks": len(bottlenecks_data),
                "critical_bottlenecks": len([b for b in bottlenecks if b.severity_score > 7]),
                "analysis_period_hours": hours,
                "message": f"識別了 {len(bottlenecks_data)} 個 I/O 瓶頸"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取 I/O 瓶頸分析失敗: {str(e)}"
        )


@router.get("/filesystem", response_model=DataResponse)
async def get_filesystem_analysis():
    """獲取檔案系統分析"""
    try:
        filesystem_stats = io_analyzer.analyze_filesystem()
        
        # 轉換為字典格式
        filesystem_data = [fs.dict() for fs in filesystem_stats]
        
        # 計算總體統計
        total_space = sum(fs.total_space for fs in filesystem_stats)
        total_used = sum(fs.used_space for fs in filesystem_stats)
        overall_usage = (total_used / total_space * 100) if total_space > 0 else 0
        
        return DataResponse(
            data={
                "filesystems": filesystem_data,
                "total_filesystems": len(filesystem_data),
                "overall_usage_percentage": overall_usage,
                "critical_filesystems": len([fs for fs in filesystem_stats if fs.usage_percentage > 90]),
                "warning_filesystems": len([fs for fs in filesystem_stats if 80 <= fs.usage_percentage <= 90]),
                "message": f"分析了 {len(filesystem_data)} 個檔案系統"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取檔案系統分析失敗: {str(e)}"
        )


@router.get("/insights", response_model=DataResponse)
async def get_io_insights(
    hours: int = Query(6, ge=1, le=24, description="分析時間範圍（小時）")
):
    """獲取 I/O 洞察"""
    try:
        insights = io_analyzer.generate_io_insights(hours=hours)
        
        # 轉換為字典格式
        insights_data = []
        for insight in insights:
            insight_dict = insight.dict()
            insight_dict['detected_at'] = insight_dict['detected_at'].isoformat()
            insights_data.append(insight_dict)
        
        # 按嚴重程度排序
        severity_order = {'critical': 3, 'warning': 2, 'info': 1}
        insights_data.sort(key=lambda x: severity_order.get(x['severity'], 0), reverse=True)
        
        return DataResponse(
            data={
                "insights": insights_data,
                "total_insights": len(insights_data),
                "critical_insights": len([i for i in insights if i.severity == 'critical']),
                "warning_insights": len([i for i in insights if i.severity == 'warning']),
                "analysis_period_hours": hours,
                "message": f"生成了 {len(insights_data)} 個 I/O 洞察"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取 I/O 洞察失敗: {str(e)}"
        )


@router.get("/history", response_model=DataResponse)
async def get_io_history(
    hours: int = Query(6, ge=1, le=24, description="歷史時間範圍（小時）")
):
    """獲取 I/O 歷史數據"""
    try:
        recent_metrics = io_analyzer._get_recent_metrics(hours)
        
        # 轉換為字典格式
        history_data = []
        for metrics in recent_metrics:
            metrics_dict = metrics.dict()
            metrics_dict['timestamp'] = metrics_dict['timestamp'].isoformat()
            history_data.append(metrics_dict)
        
        # 計算趨勢統計
        if history_data:
            disk_read_rates = [m['total_disk_read_rate'] for m in history_data]
            disk_write_rates = [m['total_disk_write_rate'] for m in history_data]
            network_in_rates = [m['total_network_in_rate'] for m in history_data]
            network_out_rates = [m['total_network_out_rate'] for m in history_data]
            
            import statistics
            
            trend_stats = {
                "avg_disk_read_rate": statistics.mean(disk_read_rates) if disk_read_rates else 0,
                "avg_disk_write_rate": statistics.mean(disk_write_rates) if disk_write_rates else 0,
                "avg_network_in_rate": statistics.mean(network_in_rates) if network_in_rates else 0,
                "avg_network_out_rate": statistics.mean(network_out_rates) if network_out_rates else 0,
                "peak_disk_read_rate": max(disk_read_rates) if disk_read_rates else 0,
                "peak_disk_write_rate": max(disk_write_rates) if disk_write_rates else 0,
                "peak_network_in_rate": max(network_in_rates) if network_in_rates else 0,
                "peak_network_out_rate": max(network_out_rates) if network_out_rates else 0
            }
        else:
            trend_stats = {}
        
        return DataResponse(
            data={
                "history": history_data,
                "total_data_points": len(history_data),
                "trend_statistics": trend_stats,
                "analysis_period_hours": hours,
                "message": f"載入了 {len(history_data)} 個歷史數據點"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取 I/O 歷史數據失敗: {str(e)}"
        )


@router.get("/summary", response_model=DataResponse)
async def get_io_summary(
    hours: int = Query(6, ge=1, le=24, description="摘要時間範圍（小時）")
):
    """獲取 I/O 摘要"""
    try:
        recent_metrics = io_analyzer._get_recent_metrics(hours)
        bottlenecks = io_analyzer.analyze_io_bottlenecks(hours)
        insights = io_analyzer.generate_io_insights(hours)
        
        if not recent_metrics:
            return DataResponse(
                data={
                    "summary": {},
                    "message": "沒有可用的 I/O 數據"
                }
            )
        
        # 計算摘要統計
        disk_read_total = sum(m.total_disk_read_rate for m in recent_metrics) * 0.5 / 1024  # 轉換為 GB，假設每個數據點間隔30分鐘
        disk_write_total = sum(m.total_disk_write_rate for m in recent_metrics) * 0.5 / 1024
        network_in_total = sum(m.total_network_in_rate for m in recent_metrics) * 0.5 / 1024
        network_out_total = sum(m.total_network_out_rate for m in recent_metrics) * 0.5 / 1024
        
        # 找出峰值時間
        peak_disk_metrics = max(recent_metrics, key=lambda x: x.total_disk_read_rate + x.total_disk_write_rate)
        peak_network_metrics = max(recent_metrics, key=lambda x: x.total_network_in_rate + x.total_network_out_rate)
        
        # 計算整體 I/O 健康分數
        io_health_score = 100.0
        if bottlenecks:
            avg_severity = sum(b.severity_score for b in bottlenecks) / len(bottlenecks)
            io_health_score = max(0, 100 - avg_severity * 10)
        
        summary = IOSummary(
            analysis_period=f"過去 {hours} 小時",
            total_disk_read=disk_read_total,
            total_disk_write=disk_write_total,
            total_network_in=network_in_total,
            total_network_out=network_out_total,
            peak_disk_io_time=peak_disk_metrics.timestamp,
            peak_network_io_time=peak_network_metrics.timestamp,
            bottlenecks_detected=len(bottlenecks),
            optimization_opportunities=len([i for i in insights if i.severity in ['warning', 'critical']]),
            overall_io_health_score=io_health_score
        )
        
        # 轉換為字典格式
        summary_dict = summary.dict()
        if summary_dict['peak_disk_io_time']:
            summary_dict['peak_disk_io_time'] = summary_dict['peak_disk_io_time'].isoformat()
        if summary_dict['peak_network_io_time']:
            summary_dict['peak_network_io_time'] = summary_dict['peak_network_io_time'].isoformat()
        
        return DataResponse(
            data={
                "summary": summary_dict,
                "analysis_period_hours": hours,
                "data_points_analyzed": len(recent_metrics),
                "message": f"I/O 健康分數: {io_health_score:.1f}/100"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取 I/O 摘要失敗: {str(e)}"
        )