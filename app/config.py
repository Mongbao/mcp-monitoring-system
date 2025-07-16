"""
MCP 監控系統配置
"""
import os
from pathlib import Path
from typing import Optional

class Settings:
    """應用程式設定"""
    
    # 基本設定
    APP_NAME: str = "MCP 監控系統"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 伺服器設定
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8003"))
    
    # 路徑設定
    BASE_DIR: Path = Path(__file__).parent.parent
    STATIC_DIR: Path = BASE_DIR / "app" / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "app" / "static" / "templates"
    
    # MCP 模組路徑
    MCP_SERVERS_PATH: str = os.getenv("MCP_SERVERS_PATH", "/home/bao/mcp_use")
    
    # 監控設定
    REFRESH_INTERVAL: int = int(os.getenv("REFRESH_INTERVAL", "30"))  # 秒
    MAX_LOG_ENTRIES: int = int(os.getenv("MAX_LOG_ENTRIES", "1000"))
    
    # 壓縮設定
    ENABLE_GZIP: bool = True
    GZIP_MIN_SIZE: int = 1024  # bytes
    
    # CORS 設定
    ALLOWED_ORIGINS: list = ["*"]  # 在生產環境中應該更嚴格
    
    # 資料庫設定 (如果需要)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # 日誌設定
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

# 全域設定實例
settings = Settings()