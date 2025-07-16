#!/usr/bin/env python3
"""
基本測試模組
"""
import pytest
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_app_import():
    """測試 FastAPI 應用程式可以正常導入"""
    try:
        from app.main import app
        assert app is not None
        assert app.title == "MCP 監控系統"
    except ImportError as e:
        pytest.fail(f"無法導入 FastAPI 應用程式: {e}")

def test_discord_monitor_import():
    """測試 Discord 監控模組可以正常導入"""
    try:
        from app.core.monitors.discord import DiscordMonitor
        monitor = DiscordMonitor()
        assert monitor is not None
    except ImportError as e:
        pytest.fail(f"無法導入 Discord 監控模組: {e}")

def test_scheduler_import():
    """測試排程器可以正常導入"""
    try:
        from app.core.scheduler import DiscordScheduler
        scheduler = DiscordScheduler()
        assert scheduler is not None
    except ImportError as e:
        pytest.fail(f"無法導入排程器: {e}")

def test_schedule_model_import():
    """測試排程模型可以正常導入"""
    try:
        from app.api.models.schedule import ScheduleConfig, ScheduleType
        assert ScheduleConfig is not None
        assert ScheduleType is not None
    except ImportError as e:
        pytest.fail(f"無法導入排程模型: {e}")

def test_discord_integration_import():
    """測試 Discord 集成模組可以正常導入"""
    try:
        from discord_integration.mcp_discord_system_monitor import MCPDiscordMonitor
        assert MCPDiscordMonitor is not None
    except ImportError as e:
        pytest.fail(f"無法導入 Discord 集成模組: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])