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
from app.api.routes import system, processes, network, logs, services, health, filesystem

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

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """主監控儀表板"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "version": settings.VERSION}

@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件"""
    print(f"🚀 {settings.APP_NAME} v{settings.VERSION} 啟動中...")
    print(f"📍 伺服器地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📁 靜態檔案目錄: {settings.STATIC_DIR}")
    print(f"🔧 除錯模式: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉事件"""
    print(f"👋 {settings.APP_NAME} 關閉中...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )