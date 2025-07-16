#!/usr/bin/env python3
"""
診斷健康度和警報功能
"""
import sys
import requests
import json
import time

def test_api_endpoints():
    """測試 API 端點"""
    base_url = "http://localhost:8003"
    
    endpoints = [
        "/api/health",
        "/api/alerts",
        "/api/trends?type=system",
        "/api/system",
        "/api/processes"
    ]
    
    print("🔍 測試 API 端點...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: {response.status_code} - {len(str(data))} 字符")
                if endpoint == "/api/health":
                    print(f"   健康度數據: {data}")
                elif endpoint == "/api/alerts":
                    print(f"   警報數據: {data}")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: 錯誤 - {e}")

def test_javascript_simulation():
    """模擬前端 JavaScript 請求"""
    print("\n🌐 模擬前端請求...")
    
    try:
        # 模擬 fetchData 函數
        response = requests.get("http://localhost:8003/api/health", 
                              timeout=5,
                              headers={'Accept': 'application/json'})
        
        print(f"健康度 API 響應時間: {response.elapsed.total_seconds():.2f}秒")
        print(f"健康度 API 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"健康度數據解析成功: {json.dumps(data, indent=2)}")
        else:
            print(f"健康度 API 失敗: {response.text}")
            
    except Exception as e:
        print(f"健康度 API 請求失敗: {e}")
    
    try:
        # 測試警報 API
        response = requests.get("http://localhost:8003/api/alerts", 
                              timeout=5,
                              headers={'Accept': 'application/json'})
        
        print(f"警報 API 響應時間: {response.elapsed.total_seconds():.2f}秒")
        print(f"警報 API 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"警報數據解析成功: {json.dumps(data, indent=2)}")
        else:
            print(f"警報 API 失敗: {response.text}")
            
    except Exception as e:
        print(f"警報 API 請求失敗: {e}")

def check_backend_services():
    """檢查後端服務狀態"""
    print("\n🔧 檢查後端服務...")
    
    try:
        # 檢查歷史管理器
        from mcp_servers.mcp_history_manager import get_history_manager
        history_manager = get_history_manager()
        
        health_score = history_manager.get_current_health_score()
        print(f"✅ 歷史管理器健康度: {health_score}")
        
        # 檢查服務控制器
        from mcp_servers.mcp_service_controller import get_service_controller
        service_controller = get_service_controller()
        
        alerts = service_controller.get_current_alerts()
        print(f"✅ 服務控制器警報: {len(alerts)} 個活躍警報")
        
        thresholds = service_controller.get_alert_thresholds()
        print(f"✅ 警報閾值: {thresholds}")
        
    except Exception as e:
        print(f"❌ 後端服務檢查失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 60)
    print("🩺 MCP 健康度和警報功能診斷工具")
    print("=" * 60)
    
    test_api_endpoints()
    test_javascript_simulation()
    check_backend_services()
    
    print("\n✅ 診斷完成")

if __name__ == "__main__":
    main()