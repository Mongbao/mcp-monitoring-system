#!/usr/bin/env python3
"""
Discord 排程 API 路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import logging
from datetime import datetime

from app.core.scheduler import scheduler
from app.api.models.schedule import (
    ScheduleConfig, ScheduleCreateRequest, ScheduleUpdateRequest, 
    ScheduleExecutionLog, ScheduleStatus
)
from app.api.models.response import DataResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def list_schedules():
    """列出所有排程"""
    try:
        schedules = scheduler.list_schedules()
        return DataResponse(
            success=True,
            data=[schedule.dict() for schedule in schedules],
            message=f"獲取 {len(schedules)} 個排程"
        )
    except Exception as e:
        logger.error(f"列出排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_schedule(request: ScheduleCreateRequest):
    """建立新排程"""
    try:
        schedule = scheduler.create_schedule(request.dict())
        return DataResponse(
            success=True,
            data=schedule.dict(),
            message=f"排程 '{schedule.name}' 建立成功"
        )
    except Exception as e:
        logger.error(f"建立排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str):
    """獲取單個排程"""
    try:
        schedule = scheduler.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="排程不存在")
        
        return DataResponse(
            success=True,
            data=schedule.dict(),
            message="排程獲取成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{schedule_id}")
async def update_schedule(schedule_id: str, request: ScheduleUpdateRequest):
    """更新排程"""
    try:
        # 過濾 None 值
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        schedule = scheduler.update_schedule(schedule_id, update_data)
        if not schedule:
            raise HTTPException(status_code=404, detail="排程不存在")
        
        return DataResponse(
            success=True,
            data=schedule.dict(),
            message=f"排程 '{schedule.name}' 更新成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """刪除排程"""
    try:
        success = scheduler.delete_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="排程不存在")
        
        return DataResponse(
            success=True,
            data={"schedule_id": schedule_id},
            message="排程刪除成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{schedule_id}/execute")
async def execute_schedule(schedule_id: str, background_tasks: BackgroundTasks):
    """手動執行排程"""
    try:
        schedule = scheduler.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="排程不存在")
        
        # 在背景執行排程
        background_tasks.add_task(scheduler._execute_schedule, schedule_id)
        
        return DataResponse(
            success=True,
            data={"schedule_id": schedule_id},
            message=f"排程 '{schedule.name}' 已開始執行"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"執行排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{schedule_id}/pause")
async def pause_schedule(schedule_id: str):
    """暫停排程"""
    try:
        schedule = scheduler.update_schedule(schedule_id, {"status": ScheduleStatus.PAUSED})
        if not schedule:
            raise HTTPException(status_code=404, detail="排程不存在")
        
        return DataResponse(
            success=True,
            data=schedule.dict(),
            message=f"排程 '{schedule.name}' 已暫停"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"暫停排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{schedule_id}/resume")
async def resume_schedule(schedule_id: str):
    """恢復排程"""
    try:
        schedule = scheduler.update_schedule(schedule_id, {"status": ScheduleStatus.ACTIVE})
        if not schedule:
            raise HTTPException(status_code=404, detail="排程不存在")
        
        return DataResponse(
            success=True,
            data=schedule.dict(),
            message=f"排程 '{schedule.name}' 已恢復"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"恢復排程失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{schedule_id}/logs")
async def get_schedule_logs(schedule_id: str, limit: int = 50):
    """獲取排程執行日誌"""
    try:
        schedule = scheduler.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="排程不存在")
        
        logs = scheduler.get_execution_logs(schedule_id, limit)
        return DataResponse(
            success=True,
            data=[log.dict() for log in logs],
            message=f"獲取 {len(logs)} 條執行日誌"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取執行日誌失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/all")
async def get_all_logs(limit: int = 100):
    """獲取所有排程執行日誌"""
    try:
        logs = scheduler.get_execution_logs(limit=limit)
        return DataResponse(
            success=True,
            data=[log.dict() for log in logs],
            message=f"獲取 {len(logs)} 條執行日誌"
        )
    except Exception as e:
        logger.error(f"獲取所有執行日誌失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/overview")
async def get_schedule_overview():
    """獲取排程概覽"""
    try:
        schedules = scheduler.list_schedules()
        
        # 統計資訊
        total_schedules = len(schedules)
        active_schedules = len([s for s in schedules if s.status == ScheduleStatus.ACTIVE])
        paused_schedules = len([s for s in schedules if s.status == ScheduleStatus.PAUSED])
        inactive_schedules = len([s for s in schedules if s.status == ScheduleStatus.INACTIVE])
        
        # 最近執行日誌
        recent_logs = scheduler.get_execution_logs(limit=10)
        
        # 下次執行時間
        next_executions = []
        for schedule in schedules:
            if schedule.status == ScheduleStatus.ACTIVE and schedule.next_run:
                next_executions.append({
                    "schedule_id": schedule.id,
                    "schedule_name": schedule.name,
                    "next_run": schedule.next_run.isoformat(),
                    "type": schedule.type
                })
        
        # 按下次執行時間排序
        next_executions.sort(key=lambda x: x["next_run"])
        
        overview = {
            "total_schedules": total_schedules,
            "active_schedules": active_schedules,
            "paused_schedules": paused_schedules,
            "inactive_schedules": inactive_schedules,
            "recent_logs": [log.dict() for log in recent_logs],
            "next_executions": next_executions[:5],  # 只顯示前5個
            "scheduler_running": scheduler.running
        }
        
        return DataResponse(
            success=True,
            data=overview,
            message="排程概覽獲取成功"
        )
    except Exception as e:
        logger.error(f"獲取排程概覽失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))