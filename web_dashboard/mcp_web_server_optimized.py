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
    def do_POST(self):
        """處理 POST 請求"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # 檢查是否支援 gzip 壓縮
        accept_encoding = self.headers.get('Accept-Encoding', '')
        supports_gzip = 'gzip' in accept_encoding
        
        # 讀取請求體
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            request_data = json.loads(post_data)
        except json.JSONDecodeError:
            request_data = {}
        
        if path == '/api/service/control':
            self.handle_service_control(request_data, supports_gzip)
        elif path == '/api/thresholds':
            self.handle_threshold_update(request_data, supports_gzip)
        else:
            self.send_error(404, "Not Found")
    
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
        elif path == '/api/trends':
            self.serve_trend_data(query, supports_gzip)
        elif path == '/api/health':
            self.serve_health_score(supports_gzip)
        elif path == '/api/alerts':
            self.serve_alerts(supports_gzip)
        elif path == '/api/logs':
            self.serve_logs(query, supports_gzip)
        elif path == '/api/service/control':
            self.serve_service_control(query, supports_gzip)
        elif path == '/api/thresholds':
            self.serve_thresholds(supports_gzip)
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
        .card h3 { 
            margin-top: 0; 
            margin-bottom: 16px; 
            color: #2c3e50; 
            font-size: 18px;
            font-weight: 600;
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin: 12px 0; 
            padding: 10px 12px; 
            border-radius: 6px;
            background-color: #f8f9fa;
            font-size: 14px;
            line-height: 1.4;
        }
        .metric-label {
            color: #495057;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
        }
        .metric-value {
            font-weight: 600;
            color: #2c3e50;
            white-space: nowrap;
            min-width: fit-content;
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
            text-align: center; 
            color: #6c757d;
            display: flex; 
            align-items: center; 
            justify-content: center;
            min-height: 80px;
            font-size: 15px;
            font-weight: 500;
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
            padding: 15px 16px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            transition: background-color 0.15s ease;
            height: 110px;
            min-height: 110px;
            max-height: 110px;
            font-size: 14px;
            line-height: 1.5;
            box-sizing: border-box;
            overflow: hidden;
        }
        .virtual-item:hover {
            background-color: #f8f9fa;
        }
        .virtual-item-left {
            flex: 1;
            padding-right: 15px;
        }
        .virtual-item-name {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 6px;
            font-size: 15px;
            line-height: 1.4;
            word-break: break-word;
            overflow-wrap: break-word;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .virtual-item-details {
            font-size: 13px;
            color: #6c757d;
            display: flex;
            flex-direction: column;
            gap: 4px;
            line-height: 1.3;
        }
        .virtual-item-details div {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }
        .virtual-item-right {
            text-align: right;
            min-width: 80px;
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
            gap: 15px;
            margin: 18px 0;
            flex-wrap: wrap;
            font-size: 14px;
        }
        .pagination-controls label {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #495057;
            font-weight: 500;
        }
        .pagination-controls select {
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
            background-color: white;
        }
        .page-info {
            font-size: 13px;
            color: #6c757d;
            font-weight: 500;
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
        
        /* 健康度評分樣式 */
        .health-score {
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 10px 0;
        }
        .health-circle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 16px;
        }
        .health-excellent { background: #27ae60; }
        .health-good { background: #3498db; }
        .health-warning { background: #f39c12; }
        .health-critical { background: #e74c3c; }
        
        .health-details {
            flex: 1;
        }
        .health-metric {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 13px;
        }
        
        /* 警報樣式 */
        .alert-item {
            padding: 10px;
            margin: 8px 0;
            border-radius: 6px;
            border-left: 4px solid;
            font-size: 13px;
        }
        .alert-critical {
            background: #fdf2f2;
            border-color: #e74c3c;
            color: #c0392b;
        }
        .alert-warning {
            background: #fef9e7;
            border-color: #f39c12;
            color: #d68910;
        }
        .alert-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
        .alert-time {
            font-size: 11px;
            opacity: 0.8;
        }
        
        /* 日誌樣式 */
        .log-controls {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        .log-controls select {
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
        }
        .log-item {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        }
        .log-error { color: #e74c3c; }
        .log-warning { color: #f39c12; }
        .log-info { color: #3498db; }
        .log-debug { color: #6c757d; }
        .log-timestamp {
            color: #6c757d;
            margin-right: 10px;
        }
        
        /* 服務控制按鈕 */
        .service-controls {
            display: flex;
            gap: 5px;
            margin-top: 8px;
        }
        .control-btn {
            padding: 4px 8px;
            border: none;
            border-radius: 3px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .control-btn:hover {
            transform: translateY(-1px);
        }
        .btn-restart { background: #3498db; color: white; }
        .btn-stop { background: #e74c3c; color: white; }
        .btn-start { background: #27ae60; color: white; }
        .btn-terminate { background: #8e44ad; color: white; }
        
        /* 模態對話框樣式 */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 10% auto;
            padding: 20px;
            border-radius: 8px;
            width: 80%;
            max-width: 500px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .close {
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            color: #6c757d;
        }
        .close:hover {
            color: #495057;
        }
        .threshold-input {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
        }
        .threshold-input input {
            width: 80px;
            padding: 6px;
            border: 1px solid #ced4da;
            border-radius: 4px;
        }
        
        /* 響應式優化 */
        @media (max-width: 768px) {
            body { padding: 15px; }
            .dashboard { grid-template-columns: 1fr; gap: 18px; }
            .virtual-scroll-container { height: 350px; }
            .pagination-controls { 
                justify-content: flex-start;
                gap: 12px;
            }
            .pagination-controls label {
                font-size: 13px;
            }
            .virtual-item {
                padding: 16px;
                font-size: 13px;
            }
            .virtual-item-name {
                font-size: 14px;
                margin-bottom: 8px;
            }
            .virtual-item-details {
                font-size: 12px;
                gap: 5px;
            }
            .virtual-item-details div {
                padding: 2px 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
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
        
        <div class="card">
            <h3>❤️ 系統健康度</h3>
            <div id="health-info" class="loading">載入中...</div>
            <div id="health-chart" class="lazy-chart" data-chart="health">
                <div class="chart-placeholder">點擊載入健康度趨勢圖表</div>
            </div>
        </div>
        
        <div class="card">
            <h3>🚨 即時警報</h3>
            <div id="alerts-info" class="loading">載入中...</div>
            <div class="alert-controls" style="margin-top: 15px;">
                <button class="refresh-btn" onclick="showThresholdSettings()" style="font-size: 12px; padding: 6px 12px;">
                    ⚙️ 閾值設定
                </button>
            </div>
        </div>
        
        <div class="card" style="grid-column: 1 / -1;">
            <h3>📋 即時日誌監控</h3>
            <div class="log-controls" style="margin-bottom: 15px;">
                <select id="log-level-filter" onchange="updateLogs()">
                    <option value="">所有級別</option>
                    <option value="ERROR">錯誤</option>
                    <option value="WARNING">警告</option>
                    <option value="INFO">資訊</option>
                    <option value="DEBUG">除錯</option>
                </select>
                <select id="log-type-filter" onchange="updateLogs()">
                    <option value="">所有類型</option>
                    <option value="system">系統</option>
                    <option value="auth">認證</option>
                    <option value="kernel">核心</option>
                    <option value="mail">郵件</option>
                </select>
                <button class="refresh-btn" onclick="updateLogs()">🔄 重新整理</button>
            </div>
            <div id="logs-container" class="virtual-scroll-container" style="height: 300px;">
                <div id="logs-content" class="virtual-scroll-content">
                    <div class="loading">載入日誌...</div>
                </div>
            </div>
        </div>
        
        <div class="card" style="grid-column: 1 / -1;">
            <h3>🔧 服務監控與控制</h3>
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

    <!-- 閾值設定模態對話框 -->
    <div id="threshold-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>⚙️ 警報閾值設定</h3>
                <span class="close" onclick="closeThresholdModal()">&times;</span>
            </div>
            <div id="threshold-form">
                <div class="threshold-input">
                    <label>CPU 警告閾值 (%):</label>
                    <input type="number" id="cpu-warning" min="0" max="100" value="70">
                </div>
                <div class="threshold-input">
                    <label>CPU 嚴重閾值 (%):</label>
                    <input type="number" id="cpu-critical" min="0" max="100" value="85">
                </div>
                <div class="threshold-input">
                    <label>記憶體警告閾值 (%):</label>
                    <input type="number" id="memory-warning" min="0" max="100" value="80">
                </div>
                <div class="threshold-input">
                    <label>記憶體嚴重閾值 (%):</label>
                    <input type="number" id="memory-critical" min="0" max="100" value="90">
                </div>
                <div class="threshold-input">
                    <label>磁碟警告閾值 (%):</label>
                    <input type="number" id="disk-warning" min="0" max="100" value="85">
                </div>
                <div class="threshold-input">
                    <label>磁碟嚴重閾值 (%):</label>
                    <input type="number" id="disk-critical" min="0" max="100" value="95">
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <button class="refresh-btn" onclick="saveThresholds()">💾 儲存設定</button>
                    <button class="refresh-btn" onclick="closeThresholdModal()" style="background: #6c757d; margin-left: 10px;">❌ 取消</button>
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
                this.itemHeight = options.itemHeight || 110;
                this.bufferSize = options.bufferSize || 3;
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
                // 清除所有現有項目
                this.renderedItems.forEach(element => element.remove());
                this.renderedItems.clear();
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
                        element.style.left = '0';
                        element.style.right = '0';
                        element.style.width = 'calc(100% - 2px)';
                        element.style.height = this.itemHeight + 'px';
                        element.style.zIndex = '1';
                        
                        this.content.appendChild(element);
                        this.renderedItems.set(i, element);
                    }
                }
            }
            
            createItem(data, index) {
                const div = document.createElement('div');
                div.className = 'virtual-item';
                div.innerHTML = `
                    <div class="virtual-item-left">
                        <div class="virtual-item-name">${data.name}</div>
                        <div class="virtual-item-details">
                            <div>進程 ID: ${data.pid}</div>
                            <div>CPU 使用率: ${data.cpu_percent.toFixed(1)}%</div>
                            <div>記憶體使用率: ${data.memory_percent.toFixed(1)}%</div>
                        </div>
                    </div>
                    <div class="virtual-item-right">
                        <div class="memory-bar" style="width: 70px; height: 10px; background: #eee; border-radius: 5px; margin-bottom: 8px;">
                            <div style="width: ${Math.min(data.memory_percent, 100)}%; height: 100%; background: ${data.memory_percent > 80 ? '#e74c3c' : data.memory_percent > 50 ? '#f39c12' : '#27ae60'}; border-radius: 5px;"></div>
                        </div>
                        <div style="font-size: 12px; color: #6c757d; text-align: center;">${data.memory_percent.toFixed(1)}%</div>
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
            virtualScrollList = new VirtualScrollList(container, { itemHeight: 110 });
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
        // 新功能函數
        async function updateHealthInfo() {
            const data = await fetchData('/api/health');
            const container = document.getElementById('health-info');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            const overallScore = data.overall || 0;
            let healthClass = 'health-critical';
            let healthText = '危險';
            
            if (overallScore >= 80) {
                healthClass = 'health-excellent';
                healthText = '優秀';
            } else if (overallScore >= 60) {
                healthClass = 'health-good';
                healthText = '良好';
            } else if (overallScore >= 40) {
                healthClass = 'health-warning';
                healthText = '警告';
            }
            
            container.innerHTML = `
                <div class="health-score">
                    <div class="health-circle ${healthClass}">
                        ${overallScore.toFixed(0)}
                    </div>
                    <div class="health-details">
                        <div style="font-weight: 600; margin-bottom: 8px;">整體健康度: ${healthText}</div>
                        <div class="health-metric">
                            <span>CPU 評分:</span><span>${data.cpu?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div class="health-metric">
                            <span>記憶體評分:</span><span>${data.memory?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div class="health-metric">
                            <span>磁碟評分:</span><span>${data.disk?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div class="health-metric">
                            <span>進程評分:</span><span>${data.process?.toFixed(1) || 'N/A'}</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        async function updateAlertsInfo() {
            const data = await fetchData('/api/alerts');
            const container = document.getElementById('alerts-info');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            const currentAlerts = data.current_alerts || [];
            const alertCount = data.alert_count || 0;
            
            if (alertCount === 0) {
                container.innerHTML = `
                    <div style="color: #27ae60; text-align: center; padding: 20px;">
                        ✅ 系統運行正常<br>
                        <small>無活躍警報</small>
                    </div>
                `;
                return;
            }
            
            let alertsHtml = `<div style="margin-bottom: 10px; font-weight: 600;">活躍警報 (${alertCount})</div>`;
            
            currentAlerts.forEach(alert => {
                const alertClass = alert.severity === 'critical' ? 'alert-critical' : 'alert-warning';
                const timestamp = new Date(alert.timestamp).toLocaleTimeString();
                
                alertsHtml += `
                    <div class="alert-item ${alertClass}">
                        <div class="alert-title">${alert.title}</div>
                        <div>${alert.description}</div>
                        <div class="alert-time">${timestamp}</div>
                    </div>
                `;
            });
            
            container.innerHTML = alertsHtml;
        }
        
        let logsVirtualList;
        
        async function updateLogs() {
            const levelFilter = document.getElementById('log-level-filter').value;
            const typeFilter = document.getElementById('log-type-filter').value;
            
            const params = new URLSearchParams({
                action: 'recent',
                count: 100
            });
            
            if (levelFilter) params.append('level', levelFilter);
            if (typeFilter) params.append('type', typeFilter);
            
            const data = await fetchData(`/api/logs?${params}`);
            
            if (data.error) {
                document.getElementById('logs-content').innerHTML = 
                    `<div style="color: #e74c3c; padding: 20px;">錯誤: ${data.error}</div>`;
                return;
            }
            
            if (!logsVirtualList) {
                const container = document.getElementById('logs-container');
                logsVirtualList = new VirtualScrollList(container, { 
                    itemHeight: 50,
                    createItem: (log, index) => createLogItem(log, index)
                });
            }
            
            logsVirtualList.setData(data.logs || []);
        }
        
        function createLogItem(log, index) {
            const div = document.createElement('div');
            div.className = `log-item log-${log.level.toLowerCase()}`;
            
            const timestamp = log.original_timestamp || new Date(log.timestamp).toLocaleTimeString();
            
            div.innerHTML = `
                <span class="log-timestamp">[${timestamp}]</span>
                <span class="log-type">[${log.log_type}]</span>
                <span class="log-level">[${log.level}]</span>
                <span class="log-message">${log.message}</span>
            `;
            
            return div;
        }
        
        function showThresholdSettings() {
            document.getElementById('threshold-modal').style.display = 'block';
            loadCurrentThresholds();
        }
        
        function closeThresholdModal() {
            document.getElementById('threshold-modal').style.display = 'none';
        }
        
        async function loadCurrentThresholds() {
            try {
                const data = await fetchData('/api/thresholds');
                const thresholds = data.thresholds || {};
                
                document.getElementById('cpu-warning').value = thresholds.cpu_warning || 70;
                document.getElementById('cpu-critical').value = thresholds.cpu_critical || 85;
                document.getElementById('memory-warning').value = thresholds.memory_warning || 80;
                document.getElementById('memory-critical').value = thresholds.memory_critical || 90;
                document.getElementById('disk-warning').value = thresholds.disk_warning || 85;
                document.getElementById('disk-critical').value = thresholds.disk_critical || 95;
            } catch (error) {
                console.error('載入閾值設定失敗:', error);
            }
        }
        
        async function saveThresholds() {
            const thresholds = {
                cpu_warning: parseFloat(document.getElementById('cpu-warning').value),
                cpu_critical: parseFloat(document.getElementById('cpu-critical').value),
                memory_warning: parseFloat(document.getElementById('memory-warning').value),
                memory_critical: parseFloat(document.getElementById('memory-critical').value),
                disk_warning: parseFloat(document.getElementById('disk-warning').value),
                disk_critical: parseFloat(document.getElementById('disk-critical').value)
            };
            
            try {
                const response = await fetch('/api/thresholds', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ thresholds })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('閾值設定已儲存');
                    closeThresholdModal();
                } else {
                    alert('儲存失敗: ' + (result.error || result.message));
                }
            } catch (error) {
                alert('儲存失敗: ' + error.message);
            }
        }
        
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
                updateHealthInfo(),
                updateAlertsInfo(),
                updateLogs(),
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
    
    def serve_trend_data(self, query, supports_gzip=False):
        """提供趨勢數據"""
        try:
            from mcp_servers.mcp_history_manager import get_history_manager
            history_manager = get_history_manager()
            
            metric_type = query.get('type', ['system'])[0]
            hours = int(query.get('hours', ['24'])[0])
            
            data = history_manager.get_trend_data(metric_type, hours)
            self.send_json_response({'trends': data}, supports_gzip)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_health_score(self, supports_gzip=False):
        """提供健康度評分"""
        try:
            from mcp_servers.mcp_history_manager import get_history_manager
            history_manager = get_history_manager()
            
            health_score = history_manager.get_current_health_score()
            self.send_json_response(health_score, supports_gzip)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_alerts(self, supports_gzip=False):
        """提供警報資訊"""
        try:
            from mcp_servers.mcp_service_controller import get_service_controller
            from mcp_servers.mcp_history_manager import get_history_manager
            
            service_controller = get_service_controller()
            history_manager = get_history_manager()
            
            current_alerts = service_controller.get_current_alerts()
            recent_alerts = history_manager.get_recent_alerts(24)
            
            data = {
                'current_alerts': current_alerts,
                'recent_alerts': recent_alerts,
                'alert_count': len(current_alerts)
            }
            
            self.send_json_response(data, supports_gzip)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_logs(self, query, supports_gzip=False):
        """提供日誌資訊"""
        try:
            from mcp_servers.mcp_log_monitor import get_log_monitor
            log_monitor = get_log_monitor()
            
            action = query.get('action', ['recent'])[0]
            
            if action == 'recent':
                count = int(query.get('count', ['100'])[0])
                level_filter = query.get('level', [None])[0]
                log_type_filter = query.get('type', [None])[0]
                
                logs = log_monitor.get_recent_logs(count, level_filter, log_type_filter)
                data = {'logs': logs}
                
            elif action == 'search':
                search_query = query.get('q', [''])[0]
                log_type = query.get('type', [None])[0]
                hours = int(query.get('hours', ['24'])[0])
                
                logs = log_monitor.search_logs(search_query, log_type, hours)
                data = {'logs': logs}
                
            elif action == 'stats':
                stats = log_monitor.get_log_stats()
                error_analysis = log_monitor.analyze_error_patterns(24)
                data = {'stats': stats, 'error_analysis': error_analysis}
                
            elif action == 'tail':
                log_type = query.get('type', ['system'])[0]
                lines = int(query.get('lines', ['50'])[0])
                
                tail_lines = log_monitor.get_log_tail(log_type, lines)
                data = {'tail': tail_lines, 'log_type': log_type}
                
            else:
                data = {'error': 'Invalid action'}
            
            self.send_json_response(data, supports_gzip)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_service_control(self, query, supports_gzip=False):
        """提供服務控制資訊"""
        try:
            from mcp_servers.mcp_service_controller import get_service_controller
            service_controller = get_service_controller()
            
            action = query.get('action', ['list'])[0]
            
            if action == 'list':
                services = service_controller.get_systemd_services()
                data = {'services': services}
            elif action == 'info':
                pid = int(query.get('pid', ['0'])[0])
                info = service_controller.get_service_info(pid)
                data = {'service_info': info}
            else:
                data = {'error': 'Invalid action'}
            
            self.send_json_response(data, supports_gzip)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def serve_thresholds(self, supports_gzip=False):
        """提供警報閾值設定"""
        try:
            from mcp_servers.mcp_service_controller import get_service_controller
            service_controller = get_service_controller()
            
            thresholds = service_controller.get_alert_thresholds()
            self.send_json_response({'thresholds': thresholds}, supports_gzip)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, supports_gzip)
    
    def handle_service_control(self, request_data, supports_gzip=False):
        """處理服務控制請求"""
        try:
            from mcp_servers.mcp_service_controller import get_service_controller
            service_controller = get_service_controller()
            
            action = request_data.get('action')
            
            if action == 'terminate':
                pid = request_data.get('pid')
                force = request_data.get('force', False)
                success, message = service_controller.terminate_service(pid, force)
                
            elif action == 'restart':
                service_name = request_data.get('service_name')
                success, message = service_controller.restart_systemd_service(service_name)
                
            elif action == 'start':
                service_name = request_data.get('service_name')
                success, message = service_controller.start_systemd_service(service_name)
                
            elif action == 'stop':
                service_name = request_data.get('service_name')
                success, message = service_controller.stop_systemd_service(service_name)
                
            else:
                success = False
                message = "Invalid action"
            
            self.send_json_response({
                'success': success,
                'message': message
            }, supports_gzip)
            
        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, supports_gzip)
    
    def handle_threshold_update(self, request_data, supports_gzip=False):
        """處理閾值更新請求"""
        try:
            from mcp_servers.mcp_service_controller import get_service_controller
            service_controller = get_service_controller()
            
            thresholds = request_data.get('thresholds', {})
            success = service_controller.update_alert_thresholds(thresholds)
            
            self.send_json_response({
                'success': success,
                'message': '閾值更新成功' if success else '閾值更新失敗'
            }, supports_gzip)
            
        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, supports_gzip)

def run_optimized_server(port=8080):
    """運行優化的 MCP Web 伺服器"""
    # 啟動增強功能
    try:
        from mcp_servers.mcp_history_manager import start_history_collection
        from mcp_servers.mcp_service_controller import start_service_monitoring  
        from mcp_servers.mcp_log_monitor import start_log_monitoring
        
        start_history_collection()
        start_service_monitoring()
        start_log_monitoring(['system', 'auth'])
        print("✅ 增強功能已啟動 (歷史數據、警報系統、日誌監控)")
        
    except Exception as e:
        print(f"⚠️  啟動增強功能時發生錯誤: {e}")
        print("   基本監控功能仍可正常使用")
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, OptimizedMCPWebHandler)
    
    print(f"🚀 MCP 監控系統 Web 伺服器已啟動 (增強版)")
    print(f"📡 伺服器位址: http://localhost:{port}")
    print(f"🌐 功能特色:")
    print(f"   • 虛擬滾動技術處理大量數據")
    print(f"   • 懶載入圖表組件") 
    print(f"   • Gzip 壓縮優化")
    print(f"   • 響應式設計")
    print(f"   • 📊 歷史趨勢分析")
    print(f"   • ❤️  系統健康度評分")
    print(f"   • 🚨 即時警報系統")
    print(f"   • 🔧 服務啟停控制")
    print(f"   • 📋 即時日誌監控")
    print(f"💡 按 Ctrl+C 停止伺服器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 正在停止伺服器...")
        try:
            from mcp_servers.mcp_history_manager import stop_history_collection
            from mcp_servers.mcp_service_controller import stop_service_monitoring
            from mcp_servers.mcp_log_monitor import stop_log_monitoring
            
            stop_history_collection()
            stop_service_monitoring() 
            stop_log_monitoring()
            print("✅ 增強功能已停止")
        except:
            pass
        print("✅ 伺服器已停止")
        httpd.server_close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    run_optimized_server(port)
