#!/usr/bin/env python3
"""
MCP 監控系統 Web 伺服器 - 優化版本
提供高性能 REST API 介面和優化的前端渲染
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import subprocess
import sys
import os
import gzip
import io
import mimetypes

# 確保可以導入 MCP 模組
sys.path.insert(0, '/home/bao/mcp_use')

class OptimizedMCPWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """處理 GET 請求"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        
        # 檢查是否支援 gzip 壓縮
        accept_encoding = self.headers.get('Accept-Encoding', '')
        supports_gzip = 'gzip' in accept_encoding
        
        if path == '/':
            self.serve_optimized_dashboard(supports_gzip)
        elif path == '/api/system':
            self.serve_system_info(supports_gzip)
        elif path == '/api/processes':
            self.serve_process_info(supports_gzip)
        elif path == '/api/network':
            self.serve_network_info(supports_gzip)
        elif path == '/api/logs':
            self.serve_log_info(supports_gzip)
        elif path == '/api/filesystem':
            self.serve_filesystem_info(supports_gzip)
        elif path == '/api/services':
            self.serve_services_info(query, supports_gzip)
        elif path == '/api/services/paginated':
            self.serve_paginated_services(query, supports_gzip)
        elif path.startswith('/static/'):
            self.serve_static_file(path, supports_gzip)
        else:
            self.send_error(404, "Not Found")
    
    def compress_response(self, data, supports_gzip=False):
        """壓縮響應數據"""
        if supports_gzip and len(data) > 1024:  # 只壓縮大於 1KB 的內容
            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
                f.write(data.encode('utf-8') if isinstance(data, str) else data)
            return buffer.getvalue(), True
        return data.encode('utf-8') if isinstance(data, str) else data, False
    
    def send_json_response(self, data, supports_gzip=False):
        """發送 JSON 響應"""
        json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        compressed_data, is_compressed = self.compress_response(json_data, supports_gzip)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        if is_compressed:
            self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(compressed_data)))
        self.end_headers()
        self.wfile.write(compressed_data)
    
    def send_html_response(self, html, supports_gzip=False):
        """發送 HTML 響應"""
        compressed_data, is_compressed = self.compress_response(html, supports_gzip)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'public, max-age=300')  # 5分鐘快取
        if is_compressed:
            self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(compressed_data)))
        self.end_headers()
        self.wfile.write(compressed_data)
    
    def serve_optimized_dashboard(self, supports_gzip=False):
        """提供優化的監控儀表板"""
        html = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP 監控系統 - 優化版</title>
    <link rel="preload" href="/static/charts.min.js" as="script">
    <link rel="prefetch" href="/api/services/paginated">
    <style>
        /* 基本樣式 - 優化版 */
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background-color: #f5f5f5;
            line-height: 1.4;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .dashboard { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .card { 
            background: white; padding: 20px; border-radius: 8px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15); 
        }
        .card h3 { margin-top: 0; color: #2c3e50; }
        .metric { 
            display: flex; justify-content: space-between; 
            margin: 10px 0; padding: 8px; border-radius: 4px;
            background-color: #f8f9fa;
        }
        .refresh-btn { 
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white; border: none; padding: 10px 20px; 
            border-radius: 4px; cursor: pointer;
            transition: all 0.2s ease;
        }
        .refresh-btn:hover { 
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
        }
        .loading { 
            text-align: center; color: #7f8c8d;
            display: flex; align-items: center; justify-content: center;
            min-height: 60px;
        }
        .loading::after {
            content: '';
            width: 20px; height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 虛擬滾動容器 */
        .virtual-scroll-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            position: relative;
        }
        .virtual-scroll-content {
            position: relative;
        }
        .virtual-item {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.15s ease;
        }
        .virtual-item:hover {
            background-color: #f8f9fa;
        }
        
        /* 懶載入圖表容器 */
        .lazy-chart {
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
            border-radius: 6px;
            margin: 10px 0;
        }
        .chart-placeholder {
            color: #6c757d;
            font-style: italic;
        }
        
        /* 優化的表格樣式 */
        .optimized-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .optimized-table th, .optimized-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .optimized-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
            position: sticky;
            top: 0;
            z-index: 1;
        }
        
        /* 分頁控制 */
        .pagination-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 15px 0;
            flex-wrap: wrap;
        }
        .page-info {
            font-size: 0.9em;
            color: #6c757d;
        }
        .page-btn {
            padding: 6px 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .page-btn:hover:not(:disabled) {
            background: #f8f9fa;
            border-color: #3498db;
        }
        .page-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .page-btn.active {
            background: #3498db;
            color: white;
            border-color: #3498db;
        }
        
        /* 響應式優化 */
        @media (max-width: 768px) {
            body { padding: 10px; }
            .dashboard { grid-template-columns: 1fr; gap: 15px; }
            .virtual-scroll-container { height: 300px; }
            .pagination-controls { justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🖥️ MCP 監控系統儀表板 - 優化版</h1>
        <p>高性能即時系統監控 | 虛擬滾動 | 懶載入</p>
        <button class="refresh-btn" onclick="refreshAll()">🔄 重新整理</button>
    </div>
    
    <div class="dashboard">
        <div class="card">
            <h3>📊 系統資源</h3>
            <div id="system-info" class="loading">載入中...</div>
            <div id="system-chart" class="lazy-chart" data-chart="system">
                <div class="chart-placeholder">點擊載入系統資源圖表</div>
            </div>
        </div>
        
        <div class="card">
            <h3>⚙️ 進程監控</h3>
            <div id="process-info" class="loading">載入中...</div>
            <div id="process-chart" class="lazy-chart" data-chart="process">
                <div class="chart-placeholder">點擊載入進程統計圖表</div>
            </div>
        </div>
        
        <div class="card">
            <h3>🌐 網路狀態</h3>
            <div id="network-info" class="loading">載入中...</div>
        </div>
        
        <div class="card">
            <h3>📁 檔案系統</h3>
            <div id="filesystem-info" class="loading">載入中...</div>
        </div>
        
        <div class="card" style="grid-column: 1 / -1;">
            <h3>🔧 服務監控 - 虛擬滾動</h3>
            <div class="pagination-controls">
                <label>
                    排序: 
                    <select id="sort-select" onchange="resetPagination()">
                        <option value="cpu">CPU 使用率</option>
                        <option value="memory">記憶體使用率</option>
                        <option value="name">服務名稱</option>
                        <option value="pid">進程 ID</option>
                    </select>
                </label>
                <label>
                    <input type="checkbox" id="desc-order" onchange="resetPagination()" checked> 降序
                </label>
                <label>
                    <input type="checkbox" id="hide-idle" onchange="resetPagination()"> 隱藏閒置
                </label>
                <div class="page-info" id="page-info">載入中...</div>
            </div>
            <div id="services-virtual-container" class="virtual-scroll-container">
                <div id="services-virtual-content" class="virtual-scroll-content">
                    <div class="loading">載入服務數據...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 虛擬滾動實現
        class VirtualScrollList {
            constructor(container, options = {}) {
                this.container = container;
                this.content = container.querySelector('.virtual-scroll-content');
                this.itemHeight = options.itemHeight || 50;
                this.bufferSize = options.bufferSize || 5;
                this.data = [];
                this.visibleStart = 0;
                this.visibleEnd = 0;
                this.renderedItems = new Map();
                
                this.container.addEventListener('scroll', this.handleScroll.bind(this));
                this.render = this.render.bind(this);
            }
            
            setData(data) {
                this.data = data;
                this.content.style.height = (data.length * this.itemHeight) + 'px';
                this.render();
            }
            
            handleScroll() {
                requestAnimationFrame(this.render);
            }
            
            render() {
                const containerHeight = this.container.clientHeight;
                const scrollTop = this.container.scrollTop;
                
                const startIndex = Math.floor(scrollTop / this.itemHeight);
                const endIndex = Math.min(
                    startIndex + Math.ceil(containerHeight / this.itemHeight) + this.bufferSize,
                    this.data.length
                );
                
                this.visibleStart = Math.max(0, startIndex - this.bufferSize);
                this.visibleEnd = endIndex;
                
                // 移除不可見的項目
                for (let [index, element] of this.renderedItems) {
                    if (index < this.visibleStart || index >= this.visibleEnd) {
                        element.remove();
                        this.renderedItems.delete(index);
                    }
                }
                
                // 添加可見的項目
                for (let i = this.visibleStart; i < this.visibleEnd; i++) {
                    if (!this.renderedItems.has(i) && this.data[i]) {
                        const element = this.createItem(this.data[i], i);
                        element.style.position = 'absolute';
                        element.style.top = (i * this.itemHeight) + 'px';
                        element.style.width = '100%';
                        element.style.height = this.itemHeight + 'px';
                        
                        this.content.appendChild(element);
                        this.renderedItems.set(i, element);
                    }
                }
            }
            
            createItem(data, index) {
                const div = document.createElement('div');
                div.className = 'virtual-item';
                div.innerHTML = `
                    <div>
                        <strong>${data.name}</strong> (PID: ${data.pid})
                        <br><small>CPU: ${data.cpu_percent}% | 記憶體: ${data.memory_percent}%</small>
                    </div>
                    <div style="text-align: right;">
                        <div class="memory-bar" style="width: 60px; height: 8px; background: #eee; border-radius: 4px;">
                            <div style="width: ${Math.min(data.memory_percent, 100)}%; height: 100%; background: ${data.memory_percent > 80 ? '#e74c3c' : data.memory_percent > 50 ? '#f39c12' : '#27ae60'}; border-radius: 4px;"></div>
                        </div>
                    </div>
                `;
                return div;
            }
        }
        
        // 懶載入圖表管理
        class LazyChartManager {
            constructor() {
                this.charts = new Map();
                this.loadedCharts = new Set();
                this.initializeLazyCharts();
            }
            
            initializeLazyCharts() {
                document.querySelectorAll('.lazy-chart').forEach(chart => {
                    chart.addEventListener('click', () => this.loadChart(chart.dataset.chart));
                });
            }
            
            async loadChart(chartType) {
                if (this.loadedCharts.has(chartType)) return;
                
                const chartContainer = document.querySelector(`[data-chart="${chartType}"]`);
                chartContainer.innerHTML = '<div class="loading">載入圖表中...</div>';
                
                try {
                    // 動態載入圖表庫（如果還沒載入）
                    if (!window.Chart) {
                        await this.loadChartLibrary();
                    }
                    
                    // 根據圖表類型載入對應數據和創建圖表
                    const data = await this.fetchChartData(chartType);
                    const canvas = document.createElement('canvas');
                    canvas.style.maxHeight = '200px';
                    
                    chartContainer.innerHTML = '';
                    chartContainer.appendChild(canvas);
                    
                    this.createChart(canvas, chartType, data);
                    this.loadedCharts.add(chartType);
                    
                } catch (error) {
                    chartContainer.innerHTML = `<div style="color: #e74c3c;">圖表載入失敗: ${error.message}</div>`;
                }
            }
            
            async loadChartLibrary() {
                return new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            }
            
            async fetchChartData(chartType) {
                const endpoints = {
                    system: '/api/system',
                    process: '/api/processes',
                    network: '/api/network'
                };
                
                const response = await fetch(endpoints[chartType]);
                return await response.json();
            }
            
            createChart(canvas, chartType, data) {
                const configs = {
                    system: {
                        type: 'doughnut',
                        data: {
                            labels: ['已使用', '可用'],
                            datasets: [{
                                data: [data.cpu_percent || 0, 100 - (data.cpu_percent || 0)],
                                backgroundColor: ['#e74c3c', '#ecf0f1']
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: { display: true, text: 'CPU 使用率分布' }
                            }
                        }
                    },
                    process: {
                        type: 'bar',
                        data: {
                            labels: ['執行中', '休眠中', '殭屍進程'],
                            datasets: [{
                                data: [
                                    data.running_processes || 0,
                                    data.sleeping_processes || 0,
                                    data.zombie_processes || 0
                                ],
                                backgroundColor: ['#27ae60', '#3498db', '#e74c3c']
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: { display: true, text: '進程狀態分布' },
                                legend: { display: false }
                            }
                        }
                    }
                };
                
                new Chart(canvas, configs[chartType]);
            }
        }
        
        // 全局變量
        let virtualScrollList;
        let lazyChartManager;
        let currentPage = 1;
        let totalPages = 1;
        let pageSize = 50;
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.getElementById('services-virtual-container');
            virtualScrollList = new VirtualScrollList(container, { itemHeight: 50 });
            lazyChartManager = new LazyChartManager();
            
            refreshAll();
            
            // 每30秒自動刷新
            setInterval(refreshAll, 30000);
        });
        
        // API 請求函數
        async function fetchData(endpoint) {
            try {
                const response = await fetch(endpoint, {
                    headers: {
                        'Accept-Encoding': 'gzip, deflate'
                    }
                });
                if (!response.ok) throw new Error('Network response was not ok');
                return await response.json();
            } catch (error) {
                console.error('Fetch error:', error);
                return { error: error.message };
            }
        }
        
        // 更新函數
        async function updateSystemInfo() {
            const data = await fetchData('/api/system');
            const container = document.getElementById('system-info');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
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
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span>總進程數:</span><span>${data.total_processes || 'N/A'}</span></div>
                <div class="metric"><span>執行中:</span><span style="color: #27ae60">${data.running_processes || 'N/A'}</span></div>
                <div class="metric"><span>休眠中:</span><span>${data.sleeping_processes || 'N/A'}</span></div>
                <div class="metric"><span>殭屍進程:</span><span style="color: #e74c3c">${data.zombie_processes || 0}</span></div>
            `;
        }
        
        async function updateNetworkInfo() {
            const data = await fetchData('/api/network');
            const container = document.getElementById('network-info');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
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
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span>監控路徑:</span><span>${data.monitored_paths || 'N/A'}</span></div>
                <div class="metric"><span>總空間:</span><span>${formatBytes(data.total_space || 0)}</span></div>
                <div class="metric"><span>可用空間:</span><span>${formatBytes(data.free_space || 0)}</span></div>
                <div class="metric"><span>使用率:</span><span>${data.usage_percent || 'N/A'}%</span></div>
            `;
        }
        
        async function updateServicesInfo() {
            const sortBy = document.getElementById('sort-select').value;
            const descOrder = document.getElementById('desc-order').checked;
            const hideIdle = document.getElementById('hide-idle').checked;
            
            const params = new URLSearchParams({
                sort: sortBy,
                desc: descOrder,
                hide_idle: hideIdle,
                page: currentPage,
                page_size: pageSize
            });
            
            try {
                const data = await fetchData(`/api/services/paginated?${params}`);
                
                if (data.error) {
                    document.getElementById('services-virtual-content').innerHTML = 
                        `<div style="color: #e74c3c; padding: 20px;">錯誤: ${data.error}</div>`;
                    return;
                }
                
                // 更新虛擬滾動列表
                virtualScrollList.setData(data.services || []);
                
                // 更新分頁信息
                totalPages = data.total_pages || 1;
                document.getElementById('page-info').textContent = 
                    `第 ${currentPage} 頁，共 ${totalPages} 頁 (總計 ${data.total_count || 0} 個服務)`;
                
            } catch (error) {
                console.error('更新服務信息失敗:', error);
            }
        }
        
        function resetPagination() {
            currentPage = 1;
            updateServicesInfo();
        }
        
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        async function refreshAll() {
            console.log('刷新所有數據...');
            await Promise.all([
                updateSystemInfo(),
                updateProcessInfo(),
                updateNetworkInfo(),
                updateFilesystemInfo(),
                updateServicesInfo()
            ]);
        }
    </script>
</body>
</html>
        """
        self.send_html_response(html, supports_gzip)
    
    def serve_paginated_services(self, query, supports_gzip=False):
        """提供分頁的服務資訊"""
        try:
            import mcp_servers.mcp_process_monitor as process_monitor
            
            # 獲取查詢參數
            sort_by = query.get('sort', ['cpu'])[0]
            desc_order = query.get('desc', ['true'])[0].lower() == 'true'
            hide_idle = query.get('hide_idle', ['false'])[0].lower() == 'true'
            page = int(query.get('page', ['1'])[0])
            page_size = int(query.get('page_size', ['50'])[0])
            
            # 獲取進程資訊
            processes = process_monitor.get_detailed_processes()
            
            # 過濾閒置服務
            if hide_idle:
                processes = [p for p in processes 
                           if p.get('cpu_percent', 0) > 0 or p.get('memory_percent', 0) > 0.1]
            
            # 排序
            reverse = desc_order
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=reverse)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=reverse)
            elif sort_by == 'name':
                processes.sort(key=lambda x: x.get('name', '').lower(), reverse=reverse)
            elif sort_by == 'pid':
                processes.sort(key=lambda x: x.get('pid', 0), reverse=reverse)
            
            # 分頁
            total_count = len(processes)
            total_pages = max(1, (total_count + page_size - 1) // page_size)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_processes = processes[start_idx:end_idx]
            
            result = {
                'services': paginated_processes,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'page_size': page_size
            }
            
            self.send_json_response(result, supports_gzip)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_system_info(self, supports_gzip=False):
        """提供系統資訊"""
        try:
            import mcp_servers.mcp_system_monitor as system_monitor
            data = system_monitor.get_system_summary()
            self.send_json_response(data, supports_gzip)
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_process_info(self, supports_gzip=False):
        """提供進程資訊"""
        try:
            import mcp_servers.mcp_process_monitor as process_monitor
            data = process_monitor.get_process_summary()
            self.send_json_response(data, supports_gzip)
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_network_info(self, supports_gzip=False):
        """提供網路資訊"""
        try:
            import mcp_servers.mcp_network_monitor as network_monitor
            data = network_monitor.get_network_summary()
            self.send_json_response(data, supports_gzip)
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_log_info(self, supports_gzip=False):
        """提供日誌資訊"""
        try:
            import mcp_servers.mcp_log_analyzer as log_analyzer
            data = log_analyzer.get_log_summary()
            self.send_json_response(data, supports_gzip)
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_filesystem_info(self, supports_gzip=False):
        """提供檔案系統資訊"""
        try:
            import mcp_servers.mcp_filesystem_monitor as filesystem_monitor
            data = filesystem_monitor.get_filesystem_summary()
            self.send_json_response(data, supports_gzip)
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_services_info(self, query, supports_gzip=False):
        """提供服務資訊（向後相容）"""
        try:
            import mcp_servers.mcp_process_monitor as process_monitor
            data = process_monitor.get_detailed_processes()
            self.send_json_response({'services': data}, supports_gzip)
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_static_file(self, path, supports_gzip=False):
        """提供靜態檔案"""
        try:
            static_path = path[8:]  # 移除 '/static/' 前綴
            file_path = os.path.join('/home/bao/mcp_use/web_dashboard/static', static_path)
            
            if not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return
            
            # 檢查是否有 gzip 版本
            gzip_path = file_path + '.gz'
            if supports_gzip and os.path.exists(gzip_path):
                with open(gzip_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                content_type, _ = mimetypes.guess_type(file_path)
                self.send_header('Content-Type', content_type or 'application/octet-stream')
                self.send_header('Content-Encoding', 'gzip')
                self.send_header('Cache-Control', 'public, max-age=3600')  # 1小時快取
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                compressed_content, is_compressed = self.compress_response(content, supports_gzip)
                
                self.send_response(200)
                content_type, _ = mimetypes.guess_type(file_path)
                self.send_header('Content-Type', content_type or 'application/octet-stream')
                self.send_header('Cache-Control', 'public, max-age=3600')  # 1小時快取
                if is_compressed:
                    self.send_header('Content-Encoding', 'gzip')
                self.send_header('Content-Length', str(len(compressed_content)))
                self.end_headers()
                self.wfile.write(compressed_content)
                
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")

def run_optimized_server(port=8080):
    """運行優化的 MCP Web 伺服器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, OptimizedMCPWebHandler)
    
    print(f"🚀 MCP 監控系統 Web 伺服器已啟動 (優化版)")
    print(f"📡 伺服器位址: http://localhost:{port}")
    print(f"🌐 功能特色:")
    print(f"   • 虛擬滾動技術處理大量數據")
    print(f"   • 懶載入圖表組件")
    print(f"   • Gzip 壓縮優化")
    print(f"   • 響應式設計")
    print(f"💡 按 Ctrl+C 停止伺服器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ 伺服器已停止")
        httpd.server_close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_optimized_server(port)
