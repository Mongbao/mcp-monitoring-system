"""
MCP 監控系統 FastAPI 主應用程式
"""
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings
from app.api.routes import system, processes, network, logs, services, health, filesystem, discord, schedule, threshold, alerts, analytics, dependencies, io_analysis, stocks

# 創建 FastAPI 應用程式
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="高性能 MCP 監控系統 API",
    debug=settings.DEBUG,
)

# 添加中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENABLE_GZIP:
    app.add_middleware(GZipMiddleware, minimum_size=settings.GZIP_MIN_SIZE)

# 設定靜態檔案
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# 設定模板
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# 註冊 API 路由
app.include_router(system.router, prefix="/api", tags=["系統監控"])
app.include_router(processes.router, prefix="/api", tags=["進程監控"])
app.include_router(network.router, prefix="/api", tags=["網路監控"])
app.include_router(logs.router, prefix="/api", tags=["日誌監控"])
app.include_router(services.router, prefix="/api", tags=["服務監控"])
app.include_router(health.router, prefix="/api", tags=["健康檢查"])
app.include_router(filesystem.router, prefix="/api", tags=["檔案系統監控"])
app.include_router(discord.router, prefix="/api/discord", tags=["Discord 監控"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["排程管理"])
app.include_router(threshold.router, tags=["警報閾值"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["智能警報系統"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["歷史數據分析"])
app.include_router(dependencies.router, prefix="/api/dependencies", tags=["資源依賴分析"])
app.include_router(io_analysis.router, prefix="/api/io-analysis", tags=["I/O性能分析"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["股票分析管理"])

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """主監控儀表板"""
    return templates.TemplateResponse("dashboard_content.html", {
        "request": request,
        "title": "系統監控",
        "page_title": "系統總覽"
    })

@app.get("/stocks", response_class=HTMLResponse)
async def stocks_page(request: Request):
    """股票分析頁面"""
    return templates.TemplateResponse("stocks_content.html", {
        "request": request,
        "title": "股票分析",
        "page_title": "股票投資分析"
    })

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "version": settings.VERSION}


async def alert_monitoring_task():
    """智能警報監控背景任務"""
    import asyncio
    import psutil
    from app.core.alerts.engine import alert_engine
    from app.core.analytics.collector import metrics_collector
    
    print("🔍 啟動智能警報監控任務...")
    
    while True:
        try:
            # 收集系統指標到歷史數據庫
            await metrics_collector.collect_metrics()
            
            # 收集指標用於警報評估
            metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_avg_1min": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
                "load_avg_5min": psutil.getloadavg()[1] if hasattr(psutil, 'getloadavg') else 0.0,
                "load_avg_15min": psutil.getloadavg()[2] if hasattr(psutil, 'getloadavg') else 0.0,
            }
            
            # 評估警報規則
            await alert_engine.evaluate_metrics(metrics)
            
            # 每 30 秒檢查一次
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"警報監控任務錯誤: {e}")
            await asyncio.sleep(60)  # 錯誤時等待更長時間

@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件"""
    print(f"🚀 {settings.APP_NAME} v{settings.VERSION} 啟動中...")
    print(f"📍 伺服器地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📁 靜態檔案目錄: {settings.STATIC_DIR}")
    print(f"🔧 除錯模式: {settings.DEBUG}")
    
    # 啟動 Discord 排程器
    from app.core.scheduler import scheduler
    scheduler.start()
    print("📅 Discord 排程器已啟動")
    
    # 啟動智能警報系統和歷史數據收集
    print("🚨 智能警報系統已啟動")
    print("📊 歷史數據收集器已啟動")
    import asyncio
    asyncio.create_task(alert_monitoring_task())

@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉事件"""
    print(f"👋 {settings.APP_NAME} 關閉中...")
    
    # 停止 Discord 排程器
    from app.core.scheduler import scheduler
    scheduler.stop()
    print("📅 Discord 排程器已停止")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )