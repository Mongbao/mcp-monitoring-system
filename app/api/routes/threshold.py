"""
警報閾值 API 路由
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.api.models.threshold import AlertThresholds, ThresholdUpdateRequest
from app.api.models.response import BaseResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["thresholds"])

# 閾值配置文件路徑
THRESHOLD_FILE = Path("data/alert_thresholds.json")

def load_thresholds() -> Dict[str, Any]:
    """載入閾值配置"""
    try:
        if THRESHOLD_FILE.exists():
            with open(THRESHOLD_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 預設閾值配置
            default_config = {
                "cpu": {"warning": 70.0, "critical": 85.0},
                "memory": {"warning": 80.0, "critical": 90.0},
                "disk": {"warning": 85.0, "critical": 95.0},
                "load": {"warning": 2.0, "critical": 4.0}
            }
            save_thresholds(default_config)
            return default_config
    except Exception as e:
        logger.error(f"載入閾值配置失敗: {e}")
        raise HTTPException(status_code=500, detail="載入閾值配置失敗")

def save_thresholds(thresholds: Dict[str, Any]) -> None:
    """保存閾值配置"""
    try:
        # 確保目錄存在
        THRESHOLD_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(THRESHOLD_FILE, 'w', encoding='utf-8') as f:
            json.dump(thresholds, f, ensure_ascii=False, indent=2)
        
        logger.info("閾值配置已保存")
    except Exception as e:
        logger.error(f"保存閾值配置失敗: {e}")
        raise HTTPException(status_code=500, detail="保存閾值配置失敗")

@router.get("/thresholds")
async def get_thresholds():
    """獲取當前閾值配置"""
    try:
        thresholds = load_thresholds()
        return JSONResponse(content={
            "success": True,
            "data": thresholds
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取閾值配置失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "獲取閾值配置失敗"}
        )

@router.post("/thresholds")
async def update_thresholds(request: ThresholdUpdateRequest):
    """更新閾值配置"""
    try:
        # 驗證閾值邏輯（警告閾值應該小於嚴重閾值）
        if request.cpu_warning >= request.cpu_critical:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "CPU 警告閾值必須小於嚴重閾值"}
            )
        
        if request.memory_warning >= request.memory_critical:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "記憶體警告閾值必須小於嚴重閾值"}
            )
        
        if request.disk_warning >= request.disk_critical:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "磁碟警告閾值必須小於嚴重閾值"}
            )
        
        if request.load_warning >= request.load_critical:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "負載警告閾值必須小於嚴重閾值"}
            )
        
        # 構建新的閾值配置
        new_thresholds = {
            "cpu": {
                "warning": request.cpu_warning,
                "critical": request.cpu_critical
            },
            "memory": {
                "warning": request.memory_warning,
                "critical": request.memory_critical
            },
            "disk": {
                "warning": request.disk_warning,
                "critical": request.disk_critical
            },
            "load": {
                "warning": request.load_warning,
                "critical": request.load_critical
            }
        }
        
        # 保存配置
        save_thresholds(new_thresholds)
        
        return JSONResponse(content={
            "success": True,
            "message": "閾值配置已更新",
            "data": new_thresholds
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新閾值配置失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "更新閾值配置失敗"}
        )