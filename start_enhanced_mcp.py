#!/usr/bin/env python3
"""
啟動增強版 MCP 監控系統
包含歷史數據收集、服務控制、警報系統和日誌監控
"""

import sys
import signal
import time
import threading

# 添加路徑
sys.path.insert(0, '/home/bao/mcp_use')

def signal_handler(signum, frame):
    """處理終止信號"""
    print("\n🛑 正在停止 MCP 監控系統...")
    
    # 停止各個服務
    try:
        from mcp_servers.mcp_history_manager import stop_history_collection
        from mcp_servers.mcp_service_controller import stop_service_monitoring
        from mcp_servers.mcp_log_monitor import stop_log_monitoring
        
        stop_history_collection()
        stop_service_monitoring()
        stop_log_monitoring()
        
        print("✅ 所有服務已停止")
    except Exception as e:
        print(f"停止服務時發生錯誤: {e}")
    
    sys.exit(0)

def start_monitoring_services():
    """啟動監控服務"""
    print("🚀 啟動 MCP 監控服務...")
    
    try:
        # 啟動歷史數據收集
        from mcp_servers.mcp_history_manager import start_history_collection
        start_history_collection()
        print("📊 歷史數據收集已啟動")
        
        # 啟動服務監控和警報
        from mcp_servers.mcp_service_controller import start_service_monitoring
        start_service_monitoring()
        print("🔍 服務監控和警報系統已啟動")
        
        # 啟動日誌監控
        from mcp_servers.mcp_log_monitor import start_log_monitoring
        start_log_monitoring(['system', 'auth'])
        print("📋 日誌監控已啟動")
        
        print("✅ 所有監控服務已啟動")
        
    except Exception as e:
        print(f"啟動監控服務時發生錯誤: {e}")
        return False
    
    return True

def start_web_server(port=8003):
    """啟動Web伺服器"""
    print(f"🌐 啟動 Web 伺服器 (端口: {port})...")
    
    try:
        from web_dashboard.mcp_web_server_optimized import run_optimized_server
        
        # 在新線程中啟動Web伺服器
        web_thread = threading.Thread(
            target=run_optimized_server, 
            args=(port,),
            daemon=True
        )
        web_thread.start()
        
        # 等待一下確保伺服器啟動
        time.sleep(2)
        print(f"✅ Web 伺服器已啟動: http://localhost:{port}")
        
        return web_thread
        
    except Exception as e:
        print(f"啟動 Web 伺服器時發生錯誤: {e}")
        return None

def main():
    """主函數"""
    print("=" * 60)
    print("🖥️  MCP 增強版監控系統")
    print("=" * 60)
    print("功能包含:")
    print("  📊 歷史趨勢圖表")
    print("  ❤️  系統健康度評分")
    print("  🚨 即時警報系統")
    print("  ⚙️  警告閾值設定")
    print("  🔧 服務啟停控制")
    print("  📋 即時日誌監控")
    print("=" * 60)
    
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 啟動監控服務
    if not start_monitoring_services():
        print("❌ 監控服務啟動失敗")
        return 1
    
    # 啟動Web伺服器
    web_thread = start_web_server()
    if not web_thread:
        print("❌ Web 伺服器啟動失敗")
        return 1
    
    print("\n🎉 MCP 增強版監控系統已完全啟動！")
    print("📱 請在瀏覽器中訪問: http://localhost:8003")
    print("💡 按 Ctrl+C 停止系統\n")
    
    try:
        # 主循環 - 保持程序運行
        while True:
            time.sleep(1)
            
            # 檢查Web線程是否還在運行
            if not web_thread.is_alive():
                print("⚠️  Web 伺服器線程已停止")
                break
                
    except KeyboardInterrupt:
        pass  # 信號處理器會處理
    
    return 0

if __name__ == "__main__":
    sys.exit(main())