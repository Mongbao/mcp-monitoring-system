"""
智能警報系統 API 路由
"""
import sys
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Path

# 添加 MCP 模組路徑
sys.path.insert(0, '/home/bao/mcp_use')

from app.api.models.response import DataResponse
from app.api.models.alerts import (
    AlertRule, AlertIncident, AlertSummary, AlertLevel, AlertStatus,
    AlertRuleCreate, AlertRuleUpdate, AlertIncidentAction
)
from app.core.alerts.engine import alert_engine

router = APIRouter()


@router.get("/summary", response_model=DataResponse)
async def get_alert_summary():
    """獲取警報摘要"""
    try:
        summary = alert_engine.get_alert_summary()
        return DataResponse(data=summary.dict())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取警報摘要失敗: {str(e)}"
        )


@router.get("/incidents", response_model=DataResponse)
async def get_incidents(
    status: Optional[AlertStatus] = Query(None, description="按狀態過濾"),
    level: Optional[AlertLevel] = Query(None, description="按級別過濾"),
    hours: int = Query(24, ge=1, le=168, description="時間範圍（小時）"),
    limit: int = Query(50, ge=1, le=200, description="返回數量限制")
):
    """獲取警報事件列表"""
    try:
        if status == AlertStatus.ACTIVE:
            incidents = alert_engine.get_active_incidents()
        else:
            incidents = alert_engine.get_recent_incidents(hours=hours)
        
        # 過濾條件
        if status and status != AlertStatus.ACTIVE:
            incidents = [i for i in incidents if i.status == status]
        
        if level:
            incidents = [i for i in incidents if i.level == level]
        
        # 按時間排序（最新的在前）
        incidents.sort(key=lambda x: x.started_at, reverse=True)
        
        # 限制數量
        incidents = incidents[:limit]
        
        # 轉換為字典格式
        incidents_data = []
        for incident in incidents:
            incident_dict = incident.dict()
            # 轉換時間格式
            time_fields = ['started_at', 'resolved_at', 'acknowledged_at', 'last_notification', 'suppressed_until']
            for field in time_fields:
                if incident_dict.get(field):
                    incident_dict[field] = incident_dict[field].isoformat()
            incidents_data.append(incident_dict)
        
        return DataResponse(
            data={
                "incidents": incidents_data,
                "total": len(incidents_data),
                "message": f"已載入 {len(incidents_data)} 個警報事件"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取警報事件失敗: {str(e)}"
        )


@router.get("/incidents/{incident_id}", response_model=DataResponse)
async def get_incident(incident_id: str = Path(..., description="事件ID")):
    """獲取特定警報事件詳情"""
    try:
        if incident_id not in alert_engine.incidents:
            raise HTTPException(status_code=404, detail="警報事件不存在")
        
        incident = alert_engine.incidents[incident_id]
        incident_dict = incident.dict()
        
        # 轉換時間格式
        time_fields = ['started_at', 'resolved_at', 'acknowledged_at', 'last_notification', 'suppressed_until']
        for field in time_fields:
            if incident_dict.get(field):
                incident_dict[field] = incident_dict[field].isoformat()
        
        return DataResponse(data=incident_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取警報事件詳情失敗: {str(e)}"
        )


@router.post("/incidents/{incident_id}/action", response_model=DataResponse)
async def incident_action(
    incident_id: str = Path(..., description="事件ID"),
    action: AlertIncidentAction = ...
):
    """對警報事件執行操作"""
    try:
        if incident_id not in alert_engine.incidents:
            raise HTTPException(status_code=404, detail="警報事件不存在")
        
        if action.action == "acknowledge":
            await alert_engine.acknowledge_incident(
                incident_id, 
                user="web_user", 
                comment=action.comment
            )
            message = "警報事件已確認"
            
        elif action.action == "resolve":
            await alert_engine.resolve_incident(incident_id, comment=action.comment)
            message = "警報事件已解決"
            
        elif action.action == "suppress":
            duration = action.suppress_duration or 60
            await alert_engine.suppress_incident(incident_id, duration_minutes=duration)
            message = f"警報事件已抑制 {duration} 分鐘"
            
        else:
            raise HTTPException(status_code=400, detail="無效的操作類型")
        
        return DataResponse(data={"success": True, "message": message})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"執行警報操作失敗: {str(e)}"
        )


@router.get("/rules", response_model=DataResponse)
async def get_alert_rules():
    """獲取所有警報規則"""
    try:
        rules_data = []
        for rule in alert_engine.rules.values():
            rule_dict = rule.dict()
            # 轉換時間格式
            rule_dict['created_at'] = rule_dict['created_at'].isoformat()
            rule_dict['updated_at'] = rule_dict['updated_at'].isoformat()
            rules_data.append(rule_dict)
        
        # 按名稱排序
        rules_data.sort(key=lambda x: x['name'])
        
        return DataResponse(
            data={
                "rules": rules_data,
                "total": len(rules_data),
                "message": f"已載入 {len(rules_data)} 個警報規則"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取警報規則失敗: {str(e)}"
        )


@router.get("/rules/{rule_id}", response_model=DataResponse)
async def get_alert_rule(rule_id: str = Path(..., description="規則ID")):
    """獲取特定警報規則"""
    try:
        if rule_id not in alert_engine.rules:
            raise HTTPException(status_code=404, detail="警報規則不存在")
        
        rule = alert_engine.rules[rule_id]
        rule_dict = rule.dict()
        rule_dict['created_at'] = rule_dict['created_at'].isoformat()
        rule_dict['updated_at'] = rule_dict['updated_at'].isoformat()
        
        return DataResponse(data=rule_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取警報規則失敗: {str(e)}"
        )


@router.post("/rules", response_model=DataResponse)
async def create_alert_rule(rule_data: AlertRuleCreate):
    """創建新的警報規則"""
    try:
        import uuid
        from datetime import datetime
        
        rule_id = str(uuid.uuid4())
        
        # 創建警報規則
        rule = AlertRule(
            id=rule_id,
            **rule_data.dict()
        )
        
        alert_engine.rules[rule_id] = rule
        alert_engine._save_rules()
        
        return DataResponse(
            data={"rule_id": rule_id, "message": "警報規則創建成功"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"創建警報規則失敗: {str(e)}"
        )


@router.put("/rules/{rule_id}", response_model=DataResponse)
async def update_alert_rule(
    rule_id: str = Path(..., description="規則ID"),
    rule_update: AlertRuleUpdate = ...
):
    """更新警報規則"""
    try:
        if rule_id not in alert_engine.rules:
            raise HTTPException(status_code=404, detail="警報規則不存在")
        
        rule = alert_engine.rules[rule_id]
        
        # 更新字段
        update_data = rule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        # 更新時間戳
        from datetime import datetime
        rule.updated_at = datetime.now()
        
        alert_engine._save_rules()
        
        return DataResponse(data={"message": "警報規則更新成功"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新警報規則失敗: {str(e)}"
        )


@router.delete("/rules/{rule_id}", response_model=DataResponse)
async def delete_alert_rule(rule_id: str = Path(..., description="規則ID")):
    """刪除警報規則"""
    try:
        if rule_id not in alert_engine.rules:
            raise HTTPException(status_code=404, detail="警報規則不存在")
        
        rule_name = alert_engine.rules[rule_id].name
        del alert_engine.rules[rule_id]
        alert_engine._save_rules()
        
        return DataResponse(data={"message": f"警報規則 '{rule_name}' 已刪除"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刪除警報規則失敗: {str(e)}"
        )


@router.post("/rules/{rule_id}/toggle", response_model=DataResponse)
async def toggle_alert_rule(rule_id: str = Path(..., description="規則ID")):
    """切換警報規則啟用狀態"""
    try:
        if rule_id not in alert_engine.rules:
            raise HTTPException(status_code=404, detail="警報規則不存在")
        
        rule = alert_engine.rules[rule_id]
        rule.enabled = not rule.enabled
        
        from datetime import datetime
        rule.updated_at = datetime.now()
        
        alert_engine._save_rules()
        
        status = "啟用" if rule.enabled else "禁用"
        return DataResponse(data={"message": f"警報規則已{status}", "enabled": rule.enabled})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"切換警報規則狀態失敗: {str(e)}"
        )


@router.get("/metrics", response_model=DataResponse)
async def get_alert_metrics():
    """獲取警報系統指標"""
    try:
        from datetime import datetime, timedelta
        
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        
        # 統計指標
        total_rules = len(alert_engine.rules)
        enabled_rules = sum(1 for rule in alert_engine.rules.values() if rule.enabled)
        active_incidents = len(alert_engine.active_incidents)
        
        # 今日新增事件
        today_incidents = sum(1 for incident in alert_engine.incidents.values() 
                            if incident.started_at >= today_start)
        
        # 本週趨勢
        week_incidents = sum(1 for incident in alert_engine.incidents.values() 
                           if incident.started_at >= week_start)
        
        # 按級別統計
        level_stats = {}
        for incident in alert_engine.active_incidents.values():
            level = incident.level.value
            level_stats[level] = level_stats.get(level, 0) + 1
        
        # 按類別統計
        category_stats = {}
        for incident in alert_engine.active_incidents.values():
            category = incident.category.value
            category_stats[category] = category_stats.get(category, 0) + 1
        
        return DataResponse(
            data={
                "total_rules": total_rules,
                "enabled_rules": enabled_rules,
                "active_incidents": active_incidents,
                "today_incidents": today_incidents,
                "week_incidents": week_incidents,
                "level_statistics": level_stats,
                "category_statistics": category_stats,
                "last_updated": now.isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取警報系統指標失敗: {str(e)}"
        )