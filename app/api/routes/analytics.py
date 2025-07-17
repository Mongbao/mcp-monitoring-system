"""
歷史數據分析和趨勢預測 API 路由
"""
import sys
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta

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
from app.api.models.metrics import (
    MetricsSummary, TrendAnalysis, PerformanceBaseline,
    AnomalyDetection, CapacityForecast, SystemInsight
)
from app.core.analytics.collector import metrics_collector

router = APIRouter()


@router.get("/historical", response_model=DataResponse)
async def get_historical_data(
    hours: int = Query(24, ge=1, le=168, description="時間範圍（小時）"),
    metrics: Optional[str] = Query(None, description="指定指標，逗號分隔"),
    aggregation: str = Query("raw", description="聚合方式 (raw/hour)")
):
    """獲取歷史數據"""
    try:
        # 解析指標參數
        metric_list = None
        if metrics:
            metric_list = [m.strip() for m in metrics.split(',') if m.strip()]
        
        # 獲取歷史數據
        historical_data = metrics_collector.get_historical_data(
            hours=hours, 
            metrics=metric_list
        )
        
        # 如果需要聚合
        if aggregation == "hour" and len(historical_data) > 0:
            historical_data = _aggregate_by_hour(historical_data)
        
        return DataResponse(
            data={
                "data_points": historical_data,
                "total_points": len(historical_data),
                "time_range_hours": hours,
                "aggregation": aggregation,
                "message": f"已載入 {len(historical_data)} 個數據點"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取歷史數據失敗: {str(e)}"
        )


@router.get("/trends", response_model=DataResponse)
async def get_trend_analysis(
    hours: int = Query(24, ge=1, le=168, description="分析時間範圍（小時）")
):
    """獲取趨勢分析"""
    try:
        trends = metrics_collector.get_trend_analysis(hours=hours)
        
        # 轉換為字典格式
        trends_data = [trend.dict() for trend in trends]
        
        return DataResponse(
            data={
                "trends": trends_data,
                "analysis_period_hours": hours,
                "total_metrics": len(trends_data),
                "message": f"分析了 {len(trends_data)} 個指標的趨勢"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取趨勢分析失敗: {str(e)}"
        )


@router.get("/baselines", response_model=DataResponse)
async def get_performance_baselines():
    """獲取性能基線"""
    try:
        baselines = metrics_collector.get_baselines()
        
        # 轉換為字典格式
        baselines_data = {}
        for metric_name, baseline in baselines.items():
            baseline_dict = baseline.dict()
            baseline_dict['last_updated'] = baseline_dict['last_updated'].isoformat()
            baselines_data[metric_name] = baseline_dict
        
        return DataResponse(
            data={
                "baselines": baselines_data,
                "total_baselines": len(baselines_data),
                "message": f"已載入 {len(baselines_data)} 個性能基線"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取性能基線失敗: {str(e)}"
        )


@router.get("/anomalies", response_model=DataResponse)
async def get_anomaly_detection(
    hours: int = Query(24, ge=1, le=168, description="時間範圍（小時）"),
    severity: Optional[str] = Query(None, description="嚴重程度過濾 (low/medium/high)")
):
    """獲取異常檢測結果"""
    try:
        anomalies = metrics_collector.get_anomalies(hours=hours)
        
        # 按嚴重程度過濾
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        # 轉換為字典格式
        anomalies_data = []
        for anomaly in anomalies:
            anomaly_dict = anomaly.dict()
            anomaly_dict['timestamp'] = anomaly_dict['timestamp'].isoformat()
            anomalies_data.append(anomaly_dict)
        
        # 按時間排序（最新的在前）
        anomalies_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return DataResponse(
            data={
                "anomalies": anomalies_data,
                "total_anomalies": len(anomalies_data),
                "time_range_hours": hours,
                "severity_filter": severity,
                "message": f"檢測到 {len(anomalies_data)} 個異常"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取異常檢測結果失敗: {str(e)}"
        )


@router.get("/summary", response_model=DataResponse)
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=168, description="統計時間範圍（小時）")
):
    """獲取指標摘要"""
    try:
        # 獲取歷史數據
        historical_data = metrics_collector.get_historical_data(hours=hours)
        
        # 獲取趨勢分析
        trends = metrics_collector.get_trend_analysis(hours=hours)
        
        # 獲取異常
        anomalies = metrics_collector.get_anomalies(hours=hours)
        
        # 計算指標概覽
        metrics_overview = {}
        if historical_data:
            # 分析每個指標
            metrics_to_analyze = ['cpu_percent', 'memory_percent', 'disk_percent', 'load_avg_1min']
            
            for metric in metrics_to_analyze:
                values = []
                for data_point in historical_data:
                    if metric in data_point and data_point[metric] is not None:
                        values.append(data_point[metric])
                
                if values:
                    import statistics
                    metrics_overview[metric] = {
                        "average": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "current": values[-1] if values else 0,
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                    }
        
        # 計算整體性能分數
        performance_score = _calculate_performance_score(metrics_overview, anomalies)
        
        # 創建摘要
        summary = MetricsSummary(
            time_range=f"過去 {hours} 小時",
            total_data_points=len(historical_data),
            metrics_overview=metrics_overview,
            trend_analysis=trends,
            anomalies_detected=len(anomalies),
            performance_score=performance_score
        )
        
        return DataResponse(data=summary.dict())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取指標摘要失敗: {str(e)}"
        )


@router.get("/capacity-forecast", response_model=DataResponse)
async def get_capacity_forecast():
    """獲取容量預測"""
    try:
        # 獲取最近30天的數據用於預測
        historical_data = metrics_collector.get_historical_data(hours=24 * 30)
        
        if len(historical_data) < 24:  # 至少需要一天的數據
            raise HTTPException(
                status_code=400,
                detail="數據不足，無法進行容量預測"
            )
        
        # 分析需要預測的指標
        metrics_to_forecast = ['cpu_percent', 'memory_percent', 'disk_percent']
        forecasts = []
        
        for metric in metrics_to_forecast:
            forecast = _generate_capacity_forecast(historical_data, metric)
            if forecast:
                forecasts.append(forecast.dict())
        
        return DataResponse(
            data={
                "forecasts": forecasts,
                "total_metrics": len(forecasts),
                "based_on_days": min(30, len(historical_data) // 24),
                "message": f"生成了 {len(forecasts)} 個容量預測"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取容量預測失敗: {str(e)}"
        )


@router.get("/insights", response_model=DataResponse)
async def get_system_insights():
    """獲取系統洞察"""
    try:
        insights = []
        
        # 獲取最近數據
        recent_data = metrics_collector.get_historical_data(hours=24)
        trends = metrics_collector.get_trend_analysis(hours=24)
        anomalies = metrics_collector.get_anomalies(hours=24)
        
        # 生成洞察
        insights.extend(_generate_performance_insights(recent_data, trends))
        insights.extend(_generate_anomaly_insights(anomalies))
        insights.extend(_generate_trend_insights(trends))
        
        # 按影響級別和信心度排序
        insights.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}.get(x['impact_level'], 0),
            x['confidence']
        ), reverse=True)
        
        return DataResponse(
            data={
                "insights": insights,
                "total_insights": len(insights),
                "high_impact_count": len([i for i in insights if i['impact_level'] == 'high']),
                "message": f"生成了 {len(insights)} 個系統洞察"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取系統洞察失敗: {str(e)}"
        )


def _aggregate_by_hour(data_points: List[dict]) -> List[dict]:
    """按小時聚合數據"""
    if not data_points:
        return []
    
    # 按小時分組
    hourly_groups = {}
    for point in data_points:
        timestamp = datetime.fromisoformat(point['timestamp'])
        hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
        
        if hour_key not in hourly_groups:
            hourly_groups[hour_key] = []
        hourly_groups[hour_key].append(point)
    
    # 計算每小時的平均值
    aggregated = []
    for hour_key, group in sorted(hourly_groups.items()):
        avg_point = {'timestamp': hour_key.isoformat()}
        
        # 計算數值字段的平均值
        numeric_fields = [
            'cpu_percent', 'memory_percent', 'disk_percent',
            'load_avg_1min', 'load_avg_5min', 'load_avg_15min',
            'process_count', 'running_processes', 'zombie_processes'
        ]
        
        for field in numeric_fields:
            values = [p[field] for p in group if field in p and p[field] is not None]
            if values:
                import statistics
                avg_point[field] = statistics.mean(values)
        
        aggregated.append(avg_point)
    
    return aggregated


def _calculate_performance_score(metrics_overview: dict, anomalies: List) -> float:
    """計算整體性能分數"""
    if not metrics_overview:
        return 0.0
    
    score = 100.0
    
    # 基於當前指標值扣分
    if 'cpu_percent' in metrics_overview:
        cpu_current = metrics_overview['cpu_percent']['current']
        if cpu_current > 80:
            score -= (cpu_current - 80) * 0.5
    
    if 'memory_percent' in metrics_overview:
        mem_current = metrics_overview['memory_percent']['current']
        if mem_current > 85:
            score -= (mem_current - 85) * 0.7
    
    if 'disk_percent' in metrics_overview:
        disk_current = metrics_overview['disk_percent']['current']
        if disk_current > 90:
            score -= (disk_current - 90) * 1.0
    
    # 基於異常數量扣分
    high_anomalies = len([a for a in anomalies if a.severity == 'high'])
    medium_anomalies = len([a for a in anomalies if a.severity == 'medium'])
    
    score -= high_anomalies * 10
    score -= medium_anomalies * 5
    
    return max(0.0, min(100.0, score))


def _generate_capacity_forecast(historical_data: List[dict], metric: str) -> Optional[CapacityForecast]:
    """生成容量預測"""
    values = []
    timestamps = []
    
    for point in historical_data:
        if metric in point and point[metric] is not None:
            values.append(point[metric])
            timestamps.append(datetime.fromisoformat(point['timestamp']))
    
    if len(values) < 7:  # 至少需要一週的數據
        return None
    
    # 簡單線性趨勢分析
    import statistics
    current_usage = values[-1]
    
    # 計算每日變化率
    if len(values) >= 7:
        week_ago_avg = statistics.mean(values[-168:-144]) if len(values) >= 168 else statistics.mean(values[:24])
        recent_avg = statistics.mean(values[-24:])
        daily_change_rate = (recent_avg - week_ago_avg) / 7
    else:
        daily_change_rate = 0
    
    # 預測7天和30天後的使用率
    predicted_7d = current_usage + daily_change_rate * 7
    predicted_30d = current_usage + daily_change_rate * 30
    
    # 計算容量耗盡日期（如果趨勢持續）
    capacity_exhaustion_date = None
    if daily_change_rate > 0:
        days_to_exhaustion = (95 - current_usage) / daily_change_rate  # 假設95%為容量上限
        if days_to_exhaustion > 0 and days_to_exhaustion < 365:  # 一年內
            capacity_exhaustion_date = datetime.now() + timedelta(days=days_to_exhaustion)
    
    # 生成建議
    if predicted_30d > 90:
        recommended_action = "緊急：建議立即擴容或優化"
    elif predicted_30d > 80:
        recommended_action = "警告：建議規劃擴容"
    elif predicted_7d > 85:
        recommended_action = "注意：監控使用趨勢"
    else:
        recommended_action = "正常：繼續監控"
    
    # 計算預測信心度
    confidence = min(0.95, len(values) / (24 * 30))  # 基於數據量
    
    return CapacityForecast(
        metric_name=metric,
        current_usage=current_usage,
        predicted_usage_7d=predicted_7d,
        predicted_usage_30d=predicted_30d,
        capacity_exhaustion_date=capacity_exhaustion_date,
        recommended_action=recommended_action,
        confidence=confidence
    )


def _generate_performance_insights(recent_data: List[dict], trends: List[TrendAnalysis]) -> List[dict]:
    """生成性能洞察"""
    insights = []
    
    if recent_data:
        latest = recent_data[-1]
        
        # CPU 洞察
        if latest.get('cpu_percent', 0) > 85:
            insights.append({
                "insight_type": "performance",
                "title": "CPU 使用率過高",
                "description": f"當前 CPU 使用率為 {latest['cpu_percent']:.1f}%，超過建議閾值",
                "impact_level": "high",
                "recommendation": "檢查高 CPU 使用率的進程，考慮優化或擴容",
                "confidence": 0.9,
                "detected_at": datetime.now().isoformat()
            })
        
        # 記憶體洞察
        if latest.get('memory_percent', 0) > 90:
            insights.append({
                "insight_type": "performance",
                "title": "記憶體使用率危險",
                "description": f"當前記憶體使用率為 {latest['memory_percent']:.1f}%，接近耗盡",
                "impact_level": "high",
                "recommendation": "立即清理記憶體或增加記憶體容量",
                "confidence": 0.95,
                "detected_at": datetime.now().isoformat()
            })
    
    return insights


def _generate_anomaly_insights(anomalies: List[AnomalyDetection]) -> List[dict]:
    """生成異常洞察"""
    insights = []
    
    if anomalies:
        high_severity_count = len([a for a in anomalies if a.severity == 'high'])
        
        if high_severity_count > 0:
            insights.append({
                "insight_type": "anomaly",
                "title": f"檢測到 {high_severity_count} 個高嚴重性異常",
                "description": "系統出現多個高嚴重性異常，需要立即關注",
                "impact_level": "high",
                "recommendation": "檢查異常詳情並採取相應措施",
                "confidence": 0.9,
                "detected_at": datetime.now().isoformat()
            })
    
    return insights


def _generate_trend_insights(trends: List[TrendAnalysis]) -> List[dict]:
    """生成趨勢洞察"""
    insights = []
    
    for trend in trends:
        if trend.trend_direction == "上升" and abs(trend.trend_percentage) > 20:
            if trend.metric_name in ['cpu_percent', 'memory_percent']:
                insights.append({
                    "insight_type": "trend",
                    "title": f"{trend.metric_name} 呈現上升趨勢",
                    "description": f"過去24小時 {trend.metric_name} 上升了 {trend.trend_percentage:.1f}%",
                    "impact_level": "medium",
                    "recommendation": "監控趨勢發展，必要時採取預防措施",
                    "confidence": 0.8,
                    "detected_at": datetime.now().isoformat()
                })
    
    return insights