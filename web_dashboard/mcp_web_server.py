#!/usr/bin/env python3
"""
MCP 監控系統 Web 伺服器
提供 REST API 介面來存取 MCP 監控資料
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import subprocess
import sys
import os

# 確保可以導入 MCP 模組
sys.path.insert(0, '/home/bao/mcp_use')

class MCPWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """處理 GET 請求"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/system':
            self.serve_system_info()
        elif path == '/api/processes':
            self.serve_process_info()
        elif path == '/api/network':
            self.serve_network_info()
        elif path == '/api/logs':
            self.serve_log_info()
        elif path == '/api/filesystem':
            self.serve_filesystem_info()
        elif path == '/api/services':
            self.serve_services_info(query)
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
        """提供監控儀表板"""
        html = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP 監控系統</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #2c3e50; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .refresh-btn:hover { background: #2980b9; }
        .status-green { color: #27ae60; }
        .status-red { color: #e74c3c; }
        .loading { text-align: center; color: #7f8c8d; }
        .services-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .services-table th, .services-table td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }
        .services-table th { background-color: #f8f9fa; font-weight: bold; color: #2c3e50; }
        .services-table tr:hover { background-color: #f8f9fa; }
        .cpu-high { color: #e74c3c; font-weight: bold; }
        .cpu-medium { color: #f39c12; }
        .cpu-low { color: #27ae60; }
        .memory-bar { width: 100px; height: 10px; background-color: #ecf0f1; border-radius: 5px; display: inline-block; position: relative; }
        .memory-fill { height: 100%; border-radius: 5px; transition: width 0.3s ease; }
        
        /* 響應式設計 */
        @media (max-width: 768px) {
            body { padding: 10px; }
            .header { padding: 15px; }
            .header h1 { font-size: 1.5em; margin: 0 0 10px 0; }
            .header p { margin: 0 0 15px 0; font-size: 0.9em; }
            .refresh-btn { padding: 8px 16px; font-size: 0.9em; }
            
            .dashboard { grid-template-columns: 1fr; gap: 15px; }
            .card { padding: 15px; }
            .card h3 { font-size: 1.1em; }
            
            /* 服務監控控制項優化 */
            .controls-container { 
                flex-direction: column; 
                gap: 10px !important; 
                align-items: stretch !important; 
            }
            .controls-container > div { 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
            }
            .controls-container select { 
                min-width: 120px; 
                flex: 1; 
                margin-left: 10px; 
            }
            .controls-container label {
                font-size: 0.9em;
            }
            .controls-container span {
                font-size: 0.75em !important;
                display: block;
                margin-top: 2px;
            }
            
            /* 表格響應式 - 卡片式布局 */
            .services-table-container {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            
            .services-table { display: none; }
            .services-cards { display: block; }
            
            .service-card {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin-bottom: 10px;
                padding: 12px;
            }
            
            .service-card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                padding-bottom: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            
            .service-name {
                font-weight: bold;
                color: #2c3e50;
                font-size: 1em;
            }
            
            .service-pid {
                background: #6c757d;
                color: white;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 0.8em;
            }
            
            .service-metrics {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-bottom: 8px;
            }
            
            .service-metric {
                display: flex;
                flex-direction: column;
                font-size: 0.85em;
            }
            
            .service-metric-label {
                color: #6c757d;
                font-size: 0.75em;
                margin-bottom: 2px;
            }
            
            .service-metric-value {
                font-weight: 500;
            }
            
            .service-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.8em;
                color: #6c757d;
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px solid #dee2e6;
            }
            
            .memory-bar-mobile {
                width: 60px;
                height: 6px;
                margin-top: 2px;
            }
        }
        
        @media (min-width: 769px) {
            .services-cards { display: none; }
            .services-table { display: table; }
        }
        
        /* 超小屏幕優化 */
        @media (max-width: 480px) {
            body { padding: 5px; }
            .header { padding: 10px; }
            .header h1 { font-size: 1.3em; }
            .card { padding: 10px; }
            
            .service-metrics {
                grid-template-columns: 1fr;
                gap: 6px;
            }
            
            .service-metric {
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            }
            
            .service-metric-label {
                margin-bottom: 0;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🖥️ MCP 監控系統儀表板</h1>
        <p>即時系統監控和資源管理</p>
        <button class="refresh-btn" onclick="refreshAll()">🔄 重新整理</button>
    </div>
    
    <div class="dashboard">
        <div class="card">
            <h3>📊 系統資源</h3>
            <div style="margin-bottom: 10px; padding: 8px; background-color: #e8f4fd; border-radius: 4px; font-size: 0.85em; color: #0c5460;">
                <strong>系統整體資源</strong>（1秒平均值）
            </div>
            <div id="system-info" class="loading">載入中...</div>
        </div>
        
        <div class="card">
            <h3>⚙️ 進程監控</h3>
            <div id="process-info" class="loading">載入中...</div>
        </div>
        
        <div class="card">
            <h3>🌐 網路狀態</h3>
            <div id="network-info" class="loading">載入中...</div>
        </div>
        
        <div class="card">
            <h3>📁 檔案系統</h3>
            <div id="filesystem-info" class="loading">載入中...</div>
        </div>
        
        <div class="card">
            <h3>📋 日誌摘要</h3>
            <div id="log-info" class="loading">載入中...</div>
        </div>
        
        <div class="card" style="grid-column: 1 / -1;">
            <h3>🔧 執行中服務資源監控</h3>
            <div class="controls-container" style="margin-bottom: 15px; display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                <div>
                    <label for="sort-select">排序方式: </label>
                    <select id="sort-select" onchange="updateServicesInfo()" style="padding: 5px; border-radius: 4px; border: 1px solid #ddd;">
                        <option value="cpu">CPU 使用率</option>
                        <option value="memory">記憶體使用率</option>
                        <option value="name">服務名稱</option>
                        <option value="pid">進程 ID</option>
                    </select>
                </div>
                <div>
                    <label for="limit-select">顯示筆數: </label>
                    <select id="limit-select" onchange="updateServicesInfo()" style="padding: 5px; border-radius: 4px; border: 1px solid #ddd;">
                        <option value="10" selected>10 筆</option>
                        <option value="20">20 筆</option>
                        <option value="50">50 筆</option>
                        <option value="100">100 筆</option>
                        <option value="200">200 筆</option>
                        <option value="0">全部</option>
                    </select>
                </div>
                <div>
                    <label>
                        <input type="checkbox" id="desc-order" onchange="updateServicesInfo()" checked> 降序排列
                    </label>
                </div>
                <div>
                    <label>
                        <input type="checkbox" id="hide-idle" onchange="updateServicesInfo()"> 隱藏閒置服務
                    </label>
                    <span style="font-size: 0.8em; color: #6c757d; margin-left: 5px;">(CPU=0 且 記憶體≤0.1%)</span>
                </div>
            </div>
            <div style="margin-bottom: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 4px; font-size: 0.9em; color: #6c757d;">
                <strong>💡 CPU 使用率說明：</strong><br>
                • <strong>系統 CPU</strong>：整體系統在 1 秒內的平均 CPU 使用率<br>
                • <strong>服務 CPU</strong>：各別進程的瞬時 CPU 使用率（0.1秒採樣），會有較大波動<br>
                • 服務 CPU 數值加總可能超過 100%（多核心系統）或與系統 CPU 不同（採樣時間差異）
            </div>
            <div id="services-info" class="loading">載入中...</div>
        </div>
    </div>

    <script>
        async function fetchData(endpoint) {
            try {
                const response = await fetch(endpoint);
                if (!response.ok) throw new Error('Network response was not ok');
                return await response.json();
            } catch (error) {
                console.error('Fetch error:', error);
                return { error: error.message };
            }
        }
        
        async function updateSystemInfo() {
            const data = await fetchData('/api/system');
            const container = document.getElementById('system-info');
            
            if (data.error) {
                container.innerHTML = `<div class="status-red">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span>CPU 使用率:</span><span>${data.cpu_percent || 'N/A'}%</span></div>
                <div class="metric"><span>記憶體使用率:</span><span>${data.memory_percent || 'N/A'}%</span></div>
                <div class="metric"><span>磁碟使用率:</span><span>${data.disk_percent || 'N/A'}%</span></div>
                <div class="metric"><span>系統負載:</span><span>${data.load_avg || 'N/A'}</span></div>
            `;
        }
        
        async function updateProcessInfo() {
            const data = await fetchData('/api/processes');
            const container = document.getElementById('process-info');
            
            if (data.error) {
                container.innerHTML = `<div class="status-red">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span>總進程數:</span><span>${data.total_processes || 'N/A'}</span></div>
                <div class="metric"><span>執行中:</span><span class="status-green">${data.running_processes || 'N/A'}</span></div>
                <div class="metric"><span>休眠中:</span><span>${data.sleeping_processes || 'N/A'}</span></div>
                <div class="metric"><span>殭屍進程:</span><span class="status-red">${data.zombie_processes || 0}</span></div>
            `;
        }
        
        async function updateNetworkInfo() {
            const data = await fetchData('/api/network');
            const container = document.getElementById('network-info');
            
            if (data.error) {
                container.innerHTML = `<div class="status-red">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span>已發送:</span><span>${formatBytes(data.bytes_sent || 0)}</span></div>
                <div class="metric"><span>已接收:</span><span>${formatBytes(data.bytes_recv || 0)}</span></div>
                <div class="metric"><span>網路介面:</span><span>${data.interface_count || 'N/A'}</span></div>
                <div class="metric"><span>活躍連線:</span><span>${data.connections || 'N/A'}</span></div>
            `;
        }
        
        async function updateFilesystemInfo() {
            const data = await fetchData('/api/filesystem');
            const container = document.getElementById('filesystem-info');
            
            if (data.error) {
                container.innerHTML = `<div class="status-red">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span>監控路徑:</span><span>${data.monitored_paths || 'N/A'}</span></div>
                <div class="metric"><span>總空間:</span><span>${formatBytes(data.total_space || 0)}</span></div>
                <div class="metric"><span>可用空間:</span><span>${formatBytes(data.free_space || 0)}</span></div>
                <div class="metric"><span>使用率:</span><span>${data.usage_percent || 'N/A'}%</span></div>
            `;
        }
        
        async function updateLogInfo() {
            const data = await fetchData('/api/logs');
            const container = document.getElementById('log-info');
            
            if (data.error) {
                container.innerHTML = `<div class="status-red">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span>錯誤數:</span><span class="status-red">${data.error_count || 0}</span></div>
                <div class="metric"><span>警告數:</span><span style="color: #f39c12">${data.warning_count || 0}</span></div>
                <div class="metric"><span>日誌檔案:</span><span>${data.log_files || 'N/A'}</span></div>
                <div class="metric"><span>最後更新:</span><span>${data.last_update || 'N/A'}</span></div>
            `;
        }
        
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        async function updateServicesInfo() {
            const sortBy = document.getElementById('sort-select').value;
            const descOrder = document.getElementById('desc-order').checked;
            const limit = document.getElementById('limit-select').value;
            const hideIdle = document.getElementById('hide-idle').checked;
            const data = await fetchData(`/api/services?sort=${sortBy}&desc=${descOrder}&limit=${limit}&hide_idle=${hideIdle}`);
            const container = document.getElementById('services-info');
            
            if (data.error) {
                container.innerHTML = `<div class="status-red">錯誤: ${data.error}</div>`;
                return;
            }
            
            if (!data.services || data.services.length === 0) {
                container.innerHTML = '<div>沒有找到執行中的服務</div>';
                return;
            }
            
            let tableHtml = `
                <div class="services-table-container">
                    <table class="services-table">
                        <thead>
                            <tr>
                                <th>服務名稱</th>
                                <th>PID</th>
                                <th>CPU % <small>(瞬時)</small></th>
                                <th>記憶體 %</th>
                                <th>記憶體使用</th>
                                <th>狀態</th>
                                <th>啟動時間</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            let cardsHtml = '<div class="services-cards">';
            
            data.services.forEach(service => {
                const cpuClass = service.cpu_percent > 50 ? 'cpu-high' : 
                               service.cpu_percent > 20 ? 'cpu-medium' : 'cpu-low';
                
                const memoryPercent = service.memory_percent || 0;
                const memoryColor = memoryPercent > 70 ? '#e74c3c' : 
                                  memoryPercent > 40 ? '#f39c12' : '#27ae60';
                
                // 桌面版表格行
                tableHtml += `
                    <tr>
                        <td><strong>${service.name}</strong></td>
                        <td>${service.pid}</td>
                        <td class="${cpuClass}">${service.cpu_percent.toFixed(2)}%</td>
                        <td>${memoryPercent.toFixed(2)}%</td>
                        <td>
                            <div class="memory-bar">
                                <div class="memory-fill" style="width: ${memoryPercent}%; background-color: ${memoryColor};"></div>
                            </div>
                            ${formatBytes(service.memory_rss || 0)}
                        </td>
                        <td><span class="status-green">${service.status}</span></td>
                        <td>${service.create_time}</td>
                    </tr>
                `;
                
                // 手機版卡片
                cardsHtml += `
                    <div class="service-card">
                        <div class="service-card-header">
                            <div class="service-name">${service.name}</div>
                            <div class="service-pid">PID: ${service.pid}</div>
                        </div>
                        <div class="service-metrics">
                            <div class="service-metric">
                                <div class="service-metric-label">CPU 使用率</div>
                                <div class="service-metric-value ${cpuClass}">${service.cpu_percent.toFixed(2)}%</div>
                            </div>
                            <div class="service-metric">
                                <div class="service-metric-label">記憶體 %</div>
                                <div class="service-metric-value">${memoryPercent.toFixed(2)}%</div>
                            </div>
                            <div class="service-metric">
                                <div class="service-metric-label">記憶體使用</div>
                                <div class="service-metric-value">
                                    <div class="memory-bar memory-bar-mobile">
                                        <div class="memory-fill" style="width: ${memoryPercent}%; background-color: ${memoryColor};"></div>
                                    </div>
                                    <div style="font-size: 0.8em; margin-top: 2px;">${formatBytes(service.memory_rss || 0)}</div>
                                </div>
                            </div>
                            <div class="service-metric">
                                <div class="service-metric-label">狀態</div>
                                <div class="service-metric-value status-green">${service.status}</div>
                            </div>
                        </div>
                        <div class="service-footer">
                            <span>啟動時間: ${service.create_time}</span>
                        </div>
                    </div>
                `;
            });
            
            tableHtml += '</tbody></table></div>';
            cardsHtml += '</div>';
            
            const combinedHtml = tableHtml + cardsHtml;
            
            const statusHtml = `<div style="margin-top: 10px; color: #7f8c8d; font-size: 0.9em;">
                顯示: ${data.services.length} 筆 (共 ${data.total_available || 'N/A'} 筆${data.hide_idle_enabled ? ', 已隱藏閒置服務' : ''}) | 
                排序: ${data.sort_by} ${data.desc_order ? '↓' : '↑'} | 
                最後更新: ${data.timestamp}
            </div>`;
            
            container.innerHTML = combinedHtml + statusHtml;
        }
        
        function refreshAll() {
            updateSystemInfo();
            updateProcessInfo();
            updateNetworkInfo();
            updateFilesystemInfo();
            updateLogInfo();
            updateServicesInfo();
        }
        
        // 初始載入
        refreshAll();
        
        // 每30秒自動重新整理
        setInterval(refreshAll, 30000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_system_info(self):
        """提供系統資訊 API"""
        try:
            import psutil
            
            # 獲取系統資訊
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            data = {
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory.percent, 2),
                'disk_percent': round((disk.used / disk.total) * 100, 2),
                'load_avg': f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}",
                'timestamp': self.get_timestamp()
            }
            
            self.send_json_response(data)
        except ImportError:
            self.send_json_response({'error': 'psutil 模組未安裝'})
        except Exception as e:
            print(f"系統資訊錯誤: {e}")
            self.send_json_response({'error': f'系統資訊獲取失敗: {str(e)}'})
    
    def serve_process_info(self):
        """提供進程資訊 API"""
        try:
            import psutil
            
            processes = list(psutil.process_iter(['status']))
            status_count = {}
            
            for proc in processes:
                try:
                    status = proc.info['status']
                    status_count[status] = status_count.get(status, 0) + 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            data = {
                'total_processes': len(processes),
                'running_processes': status_count.get('running', 0),
                'sleeping_processes': status_count.get('sleeping', 0),
                'zombie_processes': status_count.get('zombie', 0),
                'timestamp': self.get_timestamp()
            }
            
            self.send_json_response(data)
        except Exception as e:
            self.send_json_response({'error': str(e)})
    
    def serve_network_info(self):
        """提供網路資訊 API"""
        try:
            import psutil
            
            net_io = psutil.net_io_counters()
            interfaces = psutil.net_if_addrs()
            connections = len(psutil.net_connections())
            
            data = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'interface_count': len(interfaces),
                'connections': connections,
                'timestamp': self.get_timestamp()
            }
            
            self.send_json_response(data)
        except Exception as e:
            self.send_json_response({'error': str(e)})
    
    def serve_filesystem_info(self):
        """提供檔案系統資訊 API"""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            
            data = {
                'monitored_paths': '/home,/var/log,/etc',
                'total_space': disk.total,
                'free_space': disk.free,
                'usage_percent': round((disk.used / disk.total) * 100, 2),
                'timestamp': self.get_timestamp()
            }
            
            self.send_json_response(data)
        except Exception as e:
            self.send_json_response({'error': str(e)})
    
    def serve_log_info(self):
        """提供日誌資訊 API"""
        data = {
            'error_count': 0,
            'warning_count': 0,
            'log_files': '/var/log/syslog,/var/log/auth.log',
            'last_update': self.get_timestamp()
        }
        
        self.send_json_response(data)
    
    def serve_services_info(self, query):
        """提供服務資訊 API"""
        try:
            import psutil
            from datetime import datetime
            import time
            
            # 獲取查詢參數
            sort_by = query.get('sort', ['cpu'])[0]
            desc_order = query.get('desc', ['true'])[0].lower() == 'true'
            limit = int(query.get('limit', ['50'])[0])  # 預設顯示 50 筆
            hide_idle = query.get('hide_idle', ['false'])[0].lower() == 'true'  # 是否隱藏閒置服務
            
            services = []
            
            # 系統進程黑名單（更完整的過濾列表）
            system_processes = {
                'kthreadd', 'ksoftirqd', 'migration', 'watchdog', 'systemd',
                'kworker', 'ksoftirqd', 'rcu_gp', 'rcu_par_gp', 'kcompactd0',
                'khugepaged', 'kintegrityd', 'kblockd', 'blkcg_punt_bio',
                'tg3', 'edac-poller', 'devfreq_wq', 'kswapd0', 'khvcd',
                'scsi_eh_', 'scsi_tmf_', 'usb-storage', 'irq/', 'ktimer'
            }
            
            # 第一次遍歷：啟動 CPU 監控
            process_list = []
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    pinfo = proc.info
                    if (pinfo['status'] in ['running', 'sleeping'] and 
                        pinfo['name'] and 
                        not any(sys_proc in pinfo['name'] for sys_proc in system_processes)):
                        
                        # 啟動 CPU 監控（不阻塞）
                        try:
                            proc.cpu_percent()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        process_list.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 短暫等待以獲得有意義的 CPU 數據
            time.sleep(0.1)
            
            # 第二次遍歷：收集完整數據
            for proc in process_list:
                try:
                    # 安全地獲取進程資訊
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'status', 'memory_percent', 'memory_info', 'create_time'])
                    
                    # 獲取 CPU 使用率（非阻塞）
                    try:
                        cpu_percent = proc.cpu_percent()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        cpu_percent = 0.0
                    
                    # 安全地格式化啟動時間
                    try:
                        if pinfo['create_time']:
                            create_time = datetime.fromtimestamp(pinfo['create_time']).strftime('%H:%M:%S')
                        else:
                            create_time = 'N/A'
                    except (OSError, ValueError, TypeError):
                        create_time = 'N/A'
                    
                    # 安全地獲取記憶體資訊
                    memory_rss = 0
                    try:
                        if pinfo['memory_info'] and hasattr(pinfo['memory_info'], 'rss'):
                            memory_rss = pinfo['memory_info'].rss
                    except (AttributeError, TypeError):
                        memory_rss = 0
                    
                    # 安全地獲取記憶體百分比
                    memory_percent = 0.0
                    try:
                        memory_percent = float(pinfo['memory_percent'] or 0)
                    except (TypeError, ValueError):
                        memory_percent = 0.0
                    
                    service_info = {
                        'pid': pinfo['pid'],
                        'name': pinfo['name'] or 'Unknown',
                        'status': pinfo['status'],
                        'cpu_percent': float(cpu_percent),
                        'memory_percent': memory_percent,
                        'memory_rss': memory_rss,
                        'create_time': create_time
                    }
                    
                    # 如果啟用隱藏閒置服務，檢查是否為閒置服務
                    if hide_idle:
                        # 定義閒置服務：CPU 使用率為 0 且記憶體使用率 ≤ 0.1%
                        is_idle = (service_info['cpu_percent'] == 0.0 and 
                                 service_info['memory_percent'] <= 0.1)
                        if not is_idle:
                            services.append(service_info)
                    else:
                        services.append(service_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception):
                    continue
            
            # 排序服務列表
            try:
                if sort_by == 'cpu':
                    services.sort(key=lambda x: x.get('cpu_percent', 0), reverse=desc_order)
                elif sort_by == 'memory':
                    services.sort(key=lambda x: x.get('memory_percent', 0), reverse=desc_order)
                elif sort_by == 'name':
                    services.sort(key=lambda x: x.get('name', '').lower(), reverse=desc_order)
                elif sort_by == 'pid':
                    services.sort(key=lambda x: x.get('pid', 0), reverse=desc_order)
            except Exception as e:
                # 如果排序失敗，使用預設排序
                services.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            # 記錄總數量
            total_available = len(services)
            
            # 根據設定限制顯示筆數
            if limit > 0:
                services = services[:limit]
            
            data = {
                'services': services,
                'total_count': len(services),
                'total_available': total_available,
                'sort_by': sort_by,
                'desc_order': desc_order,
                'limit': limit,
                'hide_idle_enabled': hide_idle,
                'timestamp': self.get_timestamp()
            }
            
            self.send_json_response(data)
            
        except ImportError:
            self.send_json_response({'error': 'psutil 模組未安裝'})
        except Exception as e:
            import traceback
            error_detail = f"服務監控錯誤: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)  # 記錄到控制台
            self.send_json_response({'error': f'服務監控發生錯誤: {str(e)}'})
    
    def send_json_response(self, data):
        """發送 JSON 回應"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def get_timestamp(self):
        """獲取當前時間戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def run_server(port=8003):
    """啟動 Web 伺服器"""
    import socket
    import time
    
    # 檢查並清理可能的殭屍進程
    try:
        # 嘗試綁定埠來檢查是否可用
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('', port))
        test_socket.close()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"埠 {port} 已被佔用，嘗試尋找並終止相關進程...")
            import subprocess
            try:
                # 查找佔用埠的進程
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], check=True)
                            print(f"已終止進程 {pid}")
                        except subprocess.CalledProcessError:
                            pass
                    time.sleep(2)  # 等待進程完全終止
            except FileNotFoundError:
                print("lsof 命令未找到，請手動檢查埠使用情況")
    
    try:
        server_address = ('', port)
        httpd = HTTPServer(server_address, MCPWebHandler)
        # 設定 socket 選項以允許埠重用
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print(f"MCP 監控系統 Web 伺服器啟動在端口 {port}")
        print(f"存取網址: http://localhost:{port}")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:
            print(f"錯誤: 埠 {port} 仍然被佔用")
            print("請手動檢查: sudo lsof -i :8003")
            exit(1)
        else:
            print(f"伺服器啟動錯誤: {e}")
            exit(1)
    except KeyboardInterrupt:
        print("\n伺服器關閉")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
