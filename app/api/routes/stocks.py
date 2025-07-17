"""
股票管理 API 路由
"""
import sys
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi import Path as FastAPIPath
from datetime import datetime, date

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

from app.api.models.response import DataResponse, PaginatedResponse
from app.api.models.stocks import (
    StockBasicInfo, StockCreate, StockUpdate, StockSummary,
    MarketType, StockCategory, StockPriceData
)

router = APIRouter()

# 模擬資料儲存（後續會改為檔案或資料庫儲存）
_stocks_data = {}

@router.get("/overview", response_model=DataResponse)
async def get_stocks_overview():
    """獲取股票投資總覽"""
    try:
        total_stocks = len(_stocks_data)
        
        # 計算總市值和今日漲跌
        total_value = 0
        daily_change_sum = 0
        active_stocks = 0
        
        for stock in _stocks_data.values():
            if stock.get('is_active', True):
                active_stocks += 1
                current_price = stock.get('current_price', 0)
                market_cap = stock.get('market_cap', 0)
                daily_change = stock.get('daily_change', 0)
                
                total_value += market_cap
                daily_change_sum += daily_change
        
        # 計算平均漲跌幅
        avg_daily_change = daily_change_sum / active_stocks if active_stocks > 0 else 0
        
        # 模擬活躍警報數量
        active_alerts = 0
        
        overview_data = {
            "total_stocks": total_stocks,
            "active_stocks": active_stocks,
            "total_value": total_value,
            "daily_change": avg_daily_change,
            "active_alerts": active_alerts,
            "last_updated": datetime.now().isoformat()
        }
        
        return DataResponse(data=overview_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取股票總覽失敗: {str(e)}"
        )


@router.get("/summary", response_model=DataResponse)
async def get_stocks_summary():
    """獲取股票投資總覽"""
    try:
        # 計算統計資料
        total_stocks = len(_stocks_data)
        active_stocks = sum(1 for stock in _stocks_data.values() if stock.is_active)
        
        # 模擬市值計算
        total_market_value = 1250000.0  # 暫時使用固定值
        total_cost = 1200000.0
        total_pnl = total_market_value - total_cost
        total_return_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # 尋找最佳和最差表現
        best_performer = {
            "symbol": "2330",
            "name": "台積電", 
            "return_percent": 6.03
        } if _stocks_data else None
        
        worst_performer = {
            "symbol": "2454",
            "name": "聯發科",
            "return_percent": -2.1
        } if _stocks_data else None
        
        summary = StockSummary(
            total_stocks=total_stocks,
            active_stocks=active_stocks,
            total_market_value=total_market_value,
            total_cost=total_cost,
            total_pnl=total_pnl,
            total_return_percent=total_return_percent,
            best_performer=best_performer,
            worst_performer=worst_performer
        )
        
        return DataResponse(data=summary.dict())
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取股票總覽失敗: {str(e)}"
        )


@router.get("/list", response_model=PaginatedResponse)
async def get_stocks_list(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(50, ge=1, le=200, description="每頁數量"),
    search: Optional[str] = Query(None, description="搜尋股票代碼或名稱"),
    market: Optional[MarketType] = Query(None, description="按市場篩選"),
    category: Optional[StockCategory] = Query(None, description="按類別篩選"),
    is_active: Optional[bool] = Query(None, description="是否活躍追蹤"),
    sort_by: str = Query("symbol", description="排序欄位"),
    desc: bool = Query(False, description="是否降序排列")
):
    """獲取股票清單（支援分頁、搜尋、篩選）"""
    try:
        stocks = list(_stocks_data.values())
        
        # 篩選條件
        if search:
            search_lower = search.lower()
            stocks = [s for s in stocks if 
                     search_lower in s.symbol.lower() or 
                     search_lower in s.name.lower()]
        
        if market:
            stocks = [s for s in stocks if s.market == market]
            
        if category:
            stocks = [s for s in stocks if s.category == category]
            
        if is_active is not None:
            stocks = [s for s in stocks if s.is_active == is_active]
        
        # 排序
        reverse = desc
        if sort_by == "symbol":
            stocks.sort(key=lambda x: x.symbol, reverse=reverse)
        elif sort_by == "name":
            stocks.sort(key=lambda x: x.name, reverse=reverse)
        elif sort_by == "created_at":
            stocks.sort(key=lambda x: x.created_at, reverse=reverse)
        elif sort_by == "updated_at":
            stocks.sort(key=lambda x: x.updated_at, reverse=reverse)
        
        # 分頁
        total = len(stocks)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_stocks = stocks[start_idx:end_idx]
        
        # 轉換為字典格式
        stocks_data = []
        for stock in page_stocks:
            stock_dict = stock.dict()
            # 轉換時間格式
            stock_dict['created_at'] = stock_dict['created_at'].isoformat()
            stock_dict['updated_at'] = stock_dict['updated_at'].isoformat()
            stocks_data.append(stock_dict)
        
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        return PaginatedResponse(
            data=stocks_data,
            count=len(stocks_data),
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取股票清單失敗: {str(e)}"
        )


@router.get("/{stock_id}", response_model=DataResponse)
async def get_stock_detail(stock_id: str = FastAPIPath(..., description="股票ID")):
    """獲取股票詳細資料"""
    try:
        if stock_id not in _stocks_data:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        stock = _stocks_data[stock_id]
        stock_dict = stock.dict()
        stock_dict['created_at'] = stock_dict['created_at'].isoformat()
        stock_dict['updated_at'] = stock_dict['updated_at'].isoformat()
        
        return DataResponse(data=stock_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取股票詳情失敗: {str(e)}"
        )


@router.post("/", response_model=DataResponse)
async def create_stock(stock_data: StockCreate):
    """新增股票"""
    try:
        import uuid
        
        # 檢查股票代碼是否已存在
        for existing_stock in _stocks_data.values():
            if existing_stock.symbol == stock_data.symbol.upper():
                raise HTTPException(
                    status_code=400, 
                    detail=f"股票代碼 {stock_data.symbol} 已存在"
                )
        
        stock_id = str(uuid.uuid4())
        
        # 創建股票記錄
        stock = StockBasicInfo(
            id=stock_id,
            **stock_data.dict()
        )
        
        _stocks_data[stock_id] = stock
        
        return DataResponse(
            data={"stock_id": stock_id, "message": "股票新增成功"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"新增股票失敗: {str(e)}"
        )


@router.put("/{stock_id}", response_model=DataResponse)
async def update_stock(
    stock_id: str = FastAPIPath(..., description="股票ID"),
    stock_update: StockUpdate = ...
):
    """更新股票資料"""
    try:
        if stock_id not in _stocks_data:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        stock = _stocks_data[stock_id]
        
        # 更新字段
        update_data = stock_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stock, field, value)
        
        # 更新時間戳
        stock.updated_at = datetime.now()
        
        return DataResponse(data={"message": "股票資料更新成功"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新股票失敗: {str(e)}"
        )


@router.delete("/{stock_id}", response_model=DataResponse)
async def delete_stock(stock_id: str = FastAPIPath(..., description="股票ID")):
    """刪除股票"""
    try:
        if stock_id not in _stocks_data:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        stock_name = _stocks_data[stock_id].name
        del _stocks_data[stock_id]
        
        return DataResponse(data={"message": f"股票 '{stock_name}' 已刪除"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刪除股票失敗: {str(e)}"
        )


@router.post("/{stock_id}/toggle", response_model=DataResponse)
async def toggle_stock_active(stock_id: str = FastAPIPath(..., description="股票ID")):
    """切換股票追蹤狀態"""
    try:
        if stock_id not in _stocks_data:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        stock = _stocks_data[stock_id]
        stock.is_active = not stock.is_active
        stock.updated_at = datetime.now()
        
        status = "啟用" if stock.is_active else "停用"
        return DataResponse(
            data={"message": f"股票追蹤已{status}", "is_active": stock.is_active}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"切換股票狀態失敗: {str(e)}"
        )


@router.get("/{stock_id}/price", response_model=DataResponse)
async def get_stock_price_history(
    stock_id: str = FastAPIPath(..., description="股票ID"),
    start_date: Optional[date] = Query(None, description="開始日期"),
    end_date: Optional[date] = Query(None, description="結束日期"),
    limit: int = Query(100, ge=1, le=1000, description="返回數量限制")
):
    """獲取股票價格歷史資料"""
    try:
        if stock_id not in _stocks_data:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        # 模擬價格資料
        price_history = []
        stock = _stocks_data[stock_id]
        
        # 這裡可以整合真實的股價資料源
        mock_prices = [
            {"date": "2024-01-15", "open": 610, "high": 620, "low": 605, "close": 615, "volume": 12500000},
            {"date": "2024-01-14", "open": 605, "high": 612, "low": 600, "close": 610, "volume": 15200000},
            {"date": "2024-01-13", "open": 600, "high": 608, "low": 595, "close": 605, "volume": 18900000}
        ]
        
        return DataResponse(
            data={
                "stock_id": stock_id,
                "symbol": stock.symbol,
                "price_history": mock_prices,
                "total": len(mock_prices)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取價格歷史失敗: {str(e)}"
        )


@router.post("/import", response_model=DataResponse)
async def import_stocks_data():
    """匯入股票資料"""
    try:
        # 模擬匯入一些預設股票資料
        import uuid
        
        default_stocks = [
            {
                "symbol": "2330",
                "name": "台積電",
                "market": MarketType.TSE,
                "category": StockCategory.TECHNOLOGY,
                "industry": "半導體",
                "description": "全球最大的晶圓代工製造商",
                "market_cap": 15000000,
                "tags": ["藍籌股", "半導體", "台股"]
            },
            {
                "symbol": "2317",
                "name": "鴻海",
                "market": MarketType.TSE,
                "category": StockCategory.ELECTRONICS,
                "industry": "電子製造服務",
                "description": "全球最大的電子製造服務商",
                "market_cap": 2100000,
                "tags": ["代工", "電子製造", "蘋果供應鏈"]
            },
            {
                "symbol": "2454",
                "name": "聯發科",
                "market": MarketType.TSE,
                "category": StockCategory.TECHNOLOGY,
                "industry": "半導體",
                "description": "全球手機晶片主要供應商",
                "market_cap": 900000,
                "tags": ["IC設計", "手機晶片", "5G"]
            }
        ]
        
        imported_count = 0
        for stock_data in default_stocks:
            # 檢查是否已存在
            exists = any(s.symbol == stock_data["symbol"] for s in _stocks_data.values())
            if not exists:
                stock_id = str(uuid.uuid4())
                stock = StockBasicInfo(id=stock_id, **stock_data)
                _stocks_data[stock_id] = stock
                imported_count += 1
        
        return DataResponse(
            data={
                "message": f"成功匯入 {imported_count} 支股票",
                "imported_count": imported_count
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"匯入股票資料失敗: {str(e)}"
        )


@router.get("/export/csv", response_model=DataResponse)
async def export_stocks_csv():
    """匯出股票資料為CSV格式"""
    try:
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 寫入標題行
        writer.writerow([
            "股票代碼", "股票名稱", "交易市場", "產業類別", 
            "市值(億)", "標籤", "創建時間", "更新時間"
        ])
        
        # 寫入股票資料
        for stock in _stocks_data.values():
            writer.writerow([
                stock.symbol,
                stock.name,
                stock.market.value,
                stock.category.value,
                stock.market_cap or 0,
                ",".join(stock.tags),
                stock.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                stock.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return DataResponse(
            data={
                "csv_data": csv_content,
                "filename": f"stocks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "total_records": len(_stocks_data)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"匯出股票資料失敗: {str(e)}"
        )


@router.get("/markets/stats", response_model=DataResponse)
async def get_market_statistics():
    """獲取各市場統計資料"""
    try:
        market_stats = {}
        
        for stock in _stocks_data.values():
            market = stock.market.value
            if market not in market_stats:
                market_stats[market] = {
                    "count": 0,
                    "active_count": 0,
                    "categories": {}
                }
            
            market_stats[market]["count"] += 1
            if stock.is_active:
                market_stats[market]["active_count"] += 1
            
            category = stock.category.value
            if category not in market_stats[market]["categories"]:
                market_stats[market]["categories"][category] = 0
            market_stats[market]["categories"][category] += 1
        
        return DataResponse(
            data={
                "market_statistics": market_stats,
                "total_markets": len(market_stats),
                "message": f"已統計 {len(market_stats)} 個市場的資料"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取市場統計失敗: {str(e)}"
        )