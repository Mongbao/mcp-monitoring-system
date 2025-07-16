"""
API 響應模型
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class BaseResponse(BaseModel):
    """基礎響應模型"""
    success: bool = True
    message: str = "操作成功"
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseResponse):
    """錯誤響應模型"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class DataResponse(BaseResponse):
    """數據響應模型"""
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    count: Optional[int] = None

class PaginatedResponse(DataResponse):
    """分頁響應模型"""
    page: int = 1
    page_size: int = 50
    total_pages: int = 1
    has_next: bool = False
    has_prev: bool = False