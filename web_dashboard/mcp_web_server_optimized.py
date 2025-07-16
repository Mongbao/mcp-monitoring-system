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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans TC', sans-serif;
            margin: 0; padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            line-height: 1.5;
            color: #2c3e50;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 {
            margin: 0 0 8px 0;
            font-size: 2.2rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            margin: 0;
            opacity: 0.9;
            font-size: 1.1rem;
            font-weight: 300;
        }
        .dashboard { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); 
            gap: 24px; 
        }
        .card { 
            background: rgba(255,255,255,0.95); 
            padding: 24px; 
            border-radius: 16px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3498db, #2980b9);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .card:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 16px 48px rgba(0,0,0,0.2);
        }
        .card:hover::before {
            opacity: 1;
        }
        .card h3 { 
            margin-top: 0; 
            margin-bottom: 16px; 
            color: #2c3e50; 
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f8f9fa;
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin: 10px 0; 
            padding: 12px 16px; 
            border-radius: 12px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid rgba(52, 152, 219, 0.1);
            font-size: 15px;
            line-height: 1.5;
            transition: all 0.2s ease;
        }
        .metric:hover {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-color: rgba(52, 152, 219, 0.3);
            transform: translateX(4px);
        }
        .metric-label {
            color: #495057;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .metric-label::before {
            content: '●';
            color: #3498db;
            font-size: 12px;
        }
        .metric-value {
            font-weight: 700;
            color: #2c3e50;
            white-space: nowrap;
            min-width: fit-content;
            background: linear-gradient(135deg, #3498db, #2980b9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .refresh-btn { 
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white; border: none; padding: 12px 24px; 
            border-radius: 10px; cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 600;
            font-size: 14px;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2);
            position: relative;
            overflow: hidden;
        }
        .refresh-btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
            background: linear-gradient(135deg, #2980b9, #3498db);
        }
        .refresh-btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
        }
        .loading { 
            text-align: center; 
            color: #6c757d;
            display: flex; 
            align-items: center; 
            justify-content: center;
            min-height: 120px;
            font-size: 16px;
            font-weight: 600;
            flex-direction: column;
            gap: 20px;
        }
        .loading::after {
            content: '';
            width: 32px; 
            height: 32px;
            border: 3px solid rgba(52, 152, 219, 0.1);
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 數據載入骨架屏 */
        .skeleton {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 8px;
            height: 20px;
            margin: 10px 0;
        }
        .skeleton.wide { width: 100%; }
        .skeleton.medium { width: 60%; }
        .skeleton.narrow { width: 40%; }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* 虛擬滾動容器 */
        .virtual-scroll-container {
            height: 400px;
            overflow-y: auto;
            border: 2px solid rgba(52, 152, 219, 0.1);
            border-radius: 16px;
            position: relative;
            background: rgba(255,255,255,0.5);
            backdrop-filter: blur(10px);
        }
        .virtual-scroll-container::-webkit-scrollbar {
            width: 8px;
        }
        .virtual-scroll-container::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.05);
            border-radius: 4px;
        }
        .virtual-scroll-container::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #3498db, #2980b9);
            border-radius: 4px;
        }
        .virtual-scroll-container::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #2980b9, #3498db);
        }
        .virtual-scroll-content {
            position: relative;
        }
        .virtual-item {
            padding: 18px 20px;
            border-bottom: 1px solid rgba(0,0,0,0.06);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 110px;
            min-height: 110px;
            max-height: 110px;
            font-size: 14px;
            line-height: 1.5;
            box-sizing: border-box;
            overflow: hidden;
            background: rgba(255,255,255,0.8);
            margin: 2px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .virtual-item:hover {
            background: linear-gradient(135deg, rgba(52, 152, 219, 0.05) 0%, rgba(46, 204, 113, 0.05) 100%);
            transform: translateX(4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border-color: rgba(52, 152, 219, 0.2);
        }
        .virtual-item-left {
            flex: 1;
            padding-right: 15px;
        }
        .virtual-item-name {
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 16px;
            line-height: 1.4;
            word-break: break-word;
            overflow-wrap: break-word;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .virtual-item-name::before {
            content: '⚙️';
            font-size: 14px;
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
            gap: 20px;
            margin: 15px 0;
            padding: 18px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.3);
        }
        .health-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            color: white;
            font-size: 1.4rem;
            position: relative;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .health-circle::before {
            content: '';
            position: absolute;
            inset: -3px;
            border-radius: 50%;
            padding: 3px;
            background: linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1));
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask-composite: exclude;
        }
        .health-excellent { 
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
        }
        .health-good { 
            background: linear-gradient(135deg, #3498db, #5dade2);
            box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
        }
        .health-warning { 
            background: linear-gradient(135deg, #f39c12, #f4d03f);
            box-shadow: 0 8px 25px rgba(243, 156, 18, 0.3);
        }
        .health-critical { 
            background: linear-gradient(135deg, #e74c3c, #ec7063);
            box-shadow: 0 8px 25px rgba(231, 76, 60, 0.3);
        }
        
        .health-details {
            flex: 1;
        }
        .health-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .health-metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 8px 0;
            padding: 8px 12px;
            background: rgba(255,255,255,0.7);
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.5);
        }
        .health-metric-label {
            color: #495057;
        }
        .health-metric-value {
            color: #2c3e50;
            font-weight: 700;
        }
        
        /* 警報樣式 */
        .alert-item {
            padding: 14px 18px;
            margin: 10px 0;
            border-radius: 12px;
            border-left: 6px solid;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        .alert-item:hover {
            transform: translateX(4px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        .alert-critical {
            background: linear-gradient(135deg, #fdf2f2 0%, #faddd7 100%);
            border-color: #e74c3c;
            color: #c0392b;
        }
        .alert-warning {
            background: linear-gradient(135deg, #fef9e7 0%, #fef5cd 100%);
            border-color: #f39c12;
            color: #d68910;
        }
        .alert-title {
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .alert-title::before {
            content: '⚠️';
            font-size: 16px;
        }
        .alert-time {
            font-size: 12px;
            opacity: 0.8;
            font-weight: 500;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(0,0,0,0.1);
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
        
        /* 響應式設計 - 手機版佈局優化 */
        @media (max-width: 768px) {
            .header {
                padding: 15px 10px;
                text-align: center;
            }
            .header h1 {
                font-size: 1.8rem;
                margin-bottom: 8px;
            }
            .header p {
                font-size: 0.9rem;
                margin-bottom: 12px;
            }
            .refresh-btn {
                padding: 8px 16px;
                font-size: 14px;
            }
            
            /* 主要佈局 */
            .dashboard {
                grid-template-columns: 1fr;
                gap: 15px;
                padding: 10px;
            }
            
            /* 卡片樣式 */
            .card {
                padding: 15px;
                border-radius: 12px;
            }
            .card h3 {
                font-size: 1.1rem;
                margin-bottom: 12px;
            }
            
            /* 健康度分數 */
            .health-score {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            .health-circle {
                width: 70px;
                height: 70px;
                font-size: 16px;
            }
            .health-title {
                font-size: 1.1rem;
            }
            .health-metric {
                padding: 6px 12px;
                margin-bottom: 6px;
            }
            
            /* 服務項目 */
            .service-item {
                padding: 12px;
                border-radius: 8px;
            }
            .service-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }
            .service-name {
                font-size: 14px;
                font-weight: 600;
            }
            .service-pid {
                font-size: 12px;
            }
            .service-metrics {
                gap: 8px;
                margin-top: 8px;
            }
            .metric {
                padding: 4px 8px;
                font-size: 12px;
            }
            .metric-label {
                font-size: 11px;
            }
            .metric-value {
                font-size: 12px;
                font-weight: 600;
            }
            
            /* 分頁控制 */
            .pagination-controls {
                flex-direction: column;
                gap: 10px;
                align-items: stretch;
            }
            .pagination-controls label {
                justify-content: space-between;
            }
            .page-info {
                text-align: center;
            }
            
            /* 虛擬滾動容器 */
            .virtual-scroll-container {
                height: 400px;
            }
            
            /* 日誌項目 */
            .log-item {
                padding: 10px;
                font-size: 12px;
            }
            
            /* 圖表 */
            .lazy-chart {
                height: 200px;
            }
            .chart-placeholder {
                font-size: 14px;
                padding: 40px 20px;
            }
        }
        
        /* 響應式設計 - 平板電腦適配 */
        @media (min-width: 769px) and (max-width: 1024px) {
            .dashboard {
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                padding: 15px;
            }
            
            .card {
                padding: 18px;
            }
            
            .health-score {
                gap: 18px;
            }
            .health-circle {
                width: 75px;
                height: 75px;
                font-size: 18px;
            }
            
            .service-item {
                padding: 14px;
            }
            
            .virtual-scroll-container {
                height: 450px;
            }
            
            .lazy-chart {
                height: 250px;
            }
        }
        
        /* 響應式設計 - 不同解析度下的文字大小調整 */
        @media (max-width: 480px) {
            .header h1 {
                font-size: 1.5rem;
            }
            .header p {
                font-size: 0.8rem;
            }
            
            .card h3 {
                font-size: 1rem;
            }
            
            .health-title {
                font-size: 1rem;
            }
            .health-metric {
                font-size: 13px;
            }
            
            .service-name {
                font-size: 13px;
            }
            .service-pid {
                font-size: 11px;
            }
            .metric {
                font-size: 11px;
            }
            
            .log-item {
                font-size: 11px;
            }
        }
        
        /* 高解析度螢幕優化 */
        @media (min-width: 1440px) {
            .dashboard {
                grid-template-columns: repeat(4, 1fr);
                max-width: 1600px;
                margin: 0 auto;
            }
            
            .card {
                padding: 25px;
            }
            
            .health-circle {
                width: 90px;
                height: 90px;
                font-size: 22px;
            }
            
            .service-item {
                padding: 18px;
            }
            
            .virtual-scroll-container {
                height: 600px;
            }
        }
        
        /* 互動性增強 - 服務詳細資訊模態框 */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .modal-overlay.active {
            opacity: 1;
            visibility: visible;
        }
        
        .modal-content {
            background: white;
            border-radius: 16px;
            padding: 24px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }
        
        .modal-overlay.active .modal-content {
            transform: scale(1);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f1f3f4;
        }
        
        .modal-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin: 0;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #6c757d;
            padding: 5px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }
        
        .modal-close:hover {
            background: #f8f9fa;
            color: #495057;
        }
        
        .service-detail-section {
            margin-bottom: 20px;
        }
        
        .service-detail-section h4 {
            color: #495057;
            margin-bottom: 10px;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .service-detail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }
        
        .service-detail-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        
        .service-detail-label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 4px;
        }
        
        .service-detail-value {
            font-size: 1rem;
            font-weight: 600;
            color: #2c3e50;
            word-break: break-all;
        }
        
        .service-actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .service-action-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .service-action-btn.primary {
            background: #3498db;
            color: white;
        }
        
        .service-action-btn.primary:hover {
            background: #2980b9;
        }
        
        .service-action-btn.danger {
            background: #e74c3c;
            color: white;
        }
        
        .service-action-btn.danger:hover {
            background: #c0392b;
        }
        
        .service-action-btn.warning {
            background: #f39c12;
            color: white;
        }
        
        .service-action-btn.warning:hover {
            background: #e67e22;
        }
        
        /* 搜尋/篩選功能 */
        .search-filter-bar {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .search-input {
            flex: 1;
            min-width: 200px;
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #3498db;
        }
        
        .filter-select {
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            cursor: pointer;
            transition: border-color 0.2s ease;
        }
        
        .filter-select:focus {
            outline: none;
            border-color: #3498db;
        }
        
        .clear-filters-btn {
            padding: 10px 15px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s ease;
        }
        
        .clear-filters-btn:hover {
            background: #5a6268;
        }
        
        .search-results-info {
            margin-bottom: 15px;
            padding: 8px 15px;
            background: #e3f2fd;
            border-radius: 8px;
            font-size: 14px;
            color: #1976d2;
        }
        
        /* 服務狀態即時通知 */
        .notification-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1100;
            pointer-events: none;
        }
        
        .notification {
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-left: 4px solid #3498db;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            pointer-events: auto;
            max-width: 300px;
        }
        
        .notification.show {
            opacity: 1;
            transform: translateX(0);
        }
        
        .notification.success {
            border-left-color: #27ae60;
        }
        
        .notification.warning {
            border-left-color: #f39c12;
        }
        
        .notification.error {
            border-left-color: #e74c3c;
        }
        
        .notification-title {
            font-weight: 600;
            margin-bottom: 5px;
            color: #2c3e50;
        }
        
        .notification-message {
            font-size: 14px;
            color: #6c757d;
            line-height: 1.4;
        }
        
        .notification-close {
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #6c757d;
            padding: 2px;
        }
        
        .notification-close:hover {
            color: #495057;
        }
        
        /* 服務項目點擊效果 */
        .service-item {
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .service-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .service-item:active {
            transform: translateY(0);
        }
        
        /* 載入狀態指示器 */
        .loading-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 響應式調整 */
        @media (max-width: 768px) {
            .modal-content {
                width: 95%;
                padding: 20px;
            }
            
            .service-detail-grid {
                grid-template-columns: 1fr;
            }
            
            .service-actions {
                flex-direction: column;
            }
            
            .search-filter-bar {
                flex-direction: column;
                align-items: stretch;
            }
            
            .search-input {
                min-width: auto;
            }
            
            .notification-container {
                right: 10px;
                left: 10px;
            }
            
            .notification {
                max-width: none;
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
            
            <!-- 搜尋/篩選功能 -->
            <div class="search-filter-bar">
                <input type="text" id="service-search" class="search-input" placeholder="🔍 搜尋服務名稱、PID或命令..." onkeyup="handleServiceSearch()">
                <select id="status-filter" class="filter-select" onchange="handleStatusFilter()">
                    <option value="">所有狀態</option>
                    <option value="running">運行中</option>
                    <option value="sleeping">休眠中</option>
                    <option value="stopped">已停止</option>
                    <option value="zombie">殭屍進程</option>
                </select>
                <select id="cpu-filter" class="filter-select" onchange="handleCpuFilter()">
                    <option value="">CPU 使用率</option>
                    <option value="high">高 (>10%)</option>
                    <option value="medium">中 (1-10%)</option>
                    <option value="low">低 (<1%)</option>
                </select>
                <select id="memory-filter" class="filter-select" onchange="handleMemoryFilter()">
                    <option value="">記憶體使用率</option>
                    <option value="high">高 (>5%)</option>
                    <option value="medium">中 (1-5%)</option>
                    <option value="low">低 (<1%)</option>
                </select>
                <button class="clear-filters-btn" onclick="clearAllFilters()">清除篩選</button>
            </div>
            
            <div id="search-results-info" class="search-results-info" style="display: none;"></div>
            
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
                
                // 清除載入狀態和所有內容
                this.content.className = 'virtual-scroll-content';
                this.content.innerHTML = ''; // 完全清空內容
                
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
                    network: '/api/network',
                    health: '/api/trends?type=health'
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
                    },
                    health: {
                        type: 'line',
                        data: {
                            labels: data.trends?.map(item => {
                                const date = new Date(item.timestamp);
                                return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
                            }) || [],
                            datasets: [{
                                label: '整體健康度',
                                data: data.trends?.map(item => item.overall_score) || [],
                                borderColor: '#3498db',
                                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                                fill: true,
                                tension: 0.4
                            }, {
                                label: 'CPU 評分',
                                data: data.trends?.map(item => item.cpu_score) || [],
                                borderColor: '#e74c3c',
                                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                                fill: false,
                                tension: 0.4
                            }, {
                                label: '記憶體評分',
                                data: data.trends?.map(item => item.memory_score) || [],
                                borderColor: '#27ae60',
                                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                                fill: false,
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                title: { display: true, text: '健康度趨勢 (最近24小時)' },
                                legend: { display: true, position: 'top' }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100,
                                    title: { display: true, text: '評分' }
                                },
                                x: {
                                    title: { display: true, text: '時間' }
                                }
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
        async function fetchData(endpoint, timeout = 10000) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), timeout);
                
                const response = await fetch(endpoint, {
                    headers: {
                        'Accept-Encoding': 'gzip, deflate'
                    },
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Fetch error for', endpoint, ':', error);
                
                if (error.name === 'AbortError') {
                    return { error: '請求超時，請檢查服務是否正常運行' };
                }
                
                return { error: `無法連接到服務: ${error.message}` };
            }
        }
        
        // 更新函數
        // 新功能函數
        async function updateHealthInfo() {
            const container = document.getElementById('health-info');
            container.className = ''; // 移除loading class
            
            let data;
            try {
                data = await fetchData('/api/health', 5000);
                
                if (data.error) {
                    // 降級顯示：顯示基本訊息而不是錯誤
                    container.innerHTML = `
                        <div style="text-align: center; padding: 20px; color: #6c757d;">
                            <div style="font-size: 16px; margin-bottom: 10px;">⏳</div>
                            <div>健康度評分功能準備中...</div>
                            <small style="opacity: 0.7;">增強功能可能需要額外啟動時間</small>
                        </div>
                    `;
                    return;
                }
                
                // 確保 data 是有效的對象
                if (!data || typeof data !== 'object') {
                    throw new Error('無效的健康度數據');
                }
                
            } catch (error) {
                console.error('健康度功能錯誤:', error);
                container.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #6c757d;">
                        <div style="font-size: 16px; margin-bottom: 10px;">⚠️</div>
                        <div>健康度評分暫時無法使用</div>
                        <small style="opacity: 0.7;">錯誤: ${error.message}</small>
                    </div>
                `;
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
                        <div class="health-title">🎯 整體健康度: ${healthText}</div>
                        <div class="health-metric">
                            <span class="health-metric-label">🔥 CPU 評分:</span>
                            <span class="health-metric-value">${data.cpu?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div class="health-metric">
                            <span class="health-metric-label">🧠 記憶體評分:</span>
                            <span class="health-metric-value">${data.memory?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div class="health-metric">
                            <span class="health-metric-label">💾 磁碟評分:</span>
                            <span class="health-metric-value">${data.disk?.toFixed(1) || 'N/A'}</span>
                        </div>
                        <div class="health-metric">
                            <span class="health-metric-label">⚡ 進程評分:</span>
                            <span class="health-metric-value">${data.process?.toFixed(1) || 'N/A'}</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        async function updateAlertsInfo() {
            const container = document.getElementById('alerts-info');
            container.className = ''; // 移除loading class
            
            let data;
            try {
                data = await fetchData('/api/alerts', 5000);
                
                if (data.error) {
                    container.innerHTML = `
                        <div style="text-align: center; padding: 20px; color: #6c757d;">
                            <div style="font-size: 16px; margin-bottom: 10px;">⏳</div>
                            <div>警報系統準備中...</div>
                            <small style="opacity: 0.7;">增強功能可能需要額外啟動時間</small>
                        </div>
                    `;
                    return;
                }
                
                // 確保 data 是有效的對象
                if (!data || typeof data !== 'object') {
                    throw new Error('無效的警報數據');
                }
                
            } catch (error) {
                console.error('警報功能錯誤:', error);
                container.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #6c757d;">
                        <div style="font-size: 16px; margin-bottom: 10px;">⚠️</div>
                        <div>警報系統暫時無法使用</div>
                        <small style="opacity: 0.7;">錯誤: ${error.message}</small>
                    </div>
                `;
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
            const logsContent = document.getElementById('logs-content');
            
            // 移除loading class
            logsContent.className = 'virtual-scroll-content';
            
            const params = new URLSearchParams({
                action: 'recent',
                count: 100
            });
            
            if (levelFilter) params.append('level', levelFilter);
            if (typeFilter) params.append('type', typeFilter);
            
            let data;
            try {
                data = await fetchData(`/api/logs?${params}`, 5000);
                
                if (data.error) {
                    logsContent.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: #6c757d;">
                            <div style="font-size: 20px; margin-bottom: 15px;">⏳</div>
                            <div style="font-size: 16px; margin-bottom: 10px;">日誌監控系統準備中...</div>
                            <small style="opacity: 0.7;">增強功能可能需要額外啟動時間</small>
                        </div>
                    `;
                    return;
                }
                
                // 確保 data 是有效的對象
                if (!data || typeof data !== 'object') {
                    throw new Error('無效的日誌數據');
                }
                
            } catch (error) {
                console.error('日誌功能錯誤:', error);
                logsContent.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #6c757d;">
                        <div style="font-size: 20px; margin-bottom: 15px;">⚠️</div>
                        <div style="font-size: 16px;">日誌監控暫時無法使用</div>
                        <small style="opacity: 0.7;">錯誤: ${error.message}</small>
                    </div>
                `;
                return;
            }
            
            // 檢查是否有日誌數據
            const logs = data.logs || [];
            if (logs.length === 0) {
                logsContent.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #6c757d;">
                        <div style="font-size: 20px; margin-bottom: 15px;">📋</div>
                        <div style="font-size: 16px; margin-bottom: 10px;">暫無日誌數據</div>
                        <small style="opacity: 0.7;">
                            可能原因:<br/>
                            • 日誌文件為空<br/>
                            • 需要系統權限讀取日誌文件<br/>
                            • 日誌監控服務未啟動
                        </small>
                    </div>
                `;
                return;
            }
            
            if (!logsVirtualList) {
                const container = document.getElementById('logs-container');
                logsVirtualList = new VirtualScrollList(container, { 
                    itemHeight: 50,
                    createItem: (log, index) => createLogItem(log, index)
                });
            }
            
            logsVirtualList.setData(logs);
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
            const container = document.getElementById('system-info');
            container.className = ''; // 移除loading class
            
            const data = await fetchData('/api/system');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span class="metric-label">CPU 使用率:</span><span class="metric-value">${data.cpu_percent || 'N/A'}%</span></div>
                <div class="metric"><span class="metric-label">記憶體使用率:</span><span class="metric-value">${data.memory_percent || 'N/A'}%</span></div>
                <div class="metric"><span class="metric-label">磁碟使用率:</span><span class="metric-value">${data.disk_percent || 'N/A'}%</span></div>
                <div class="metric"><span class="metric-label">系統負載:</span><span class="metric-value">${data.load_avg || 'N/A'}</span></div>
            `;
        }
        
        async function updateProcessInfo() {
            const container = document.getElementById('process-info');
            container.className = ''; // 移除loading class
            
            const data = await fetchData('/api/processes');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span class="metric-label">總進程數:</span><span class="metric-value">${data.total_processes || 'N/A'}</span></div>
                <div class="metric"><span class="metric-label">執行中:</span><span class="metric-value" style="color: #27ae60">${data.running_processes || 'N/A'}</span></div>
                <div class="metric"><span class="metric-label">休眠中:</span><span class="metric-value">${data.sleeping_processes || 'N/A'}</span></div>
                <div class="metric"><span class="metric-label">殭屍進程:</span><span class="metric-value" style="color: #e74c3c">${data.zombie_processes || 0}</span></div>
            `;
        }
        
        async function updateNetworkInfo() {
            const container = document.getElementById('network-info');
            container.className = ''; // 移除loading class
            
            const data = await fetchData('/api/network');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span class="metric-label">已發送:</span><span class="metric-value">${formatBytes(data.bytes_sent || 0)}</span></div>
                <div class="metric"><span class="metric-label">已接收:</span><span class="metric-value">${formatBytes(data.bytes_recv || 0)}</span></div>
                <div class="metric"><span class="metric-label">網路介面:</span><span class="metric-value">${data.interface_count || 'N/A'}</span></div>
                <div class="metric"><span class="metric-label">活躍連線:</span><span class="metric-value">${data.connections || 'N/A'}</span></div>
            `;
        }
        
        async function updateFilesystemInfo() {
            const container = document.getElementById('filesystem-info');
            container.className = ''; // 移除loading class
            
            const data = await fetchData('/api/filesystem');
            
            if (data.error) {
                container.innerHTML = `<div style="color: #e74c3c;">錯誤: ${data.error}</div>`;
                return;
            }
            
            container.innerHTML = `
                <div class="metric"><span class="metric-label">監控路徑:</span><span class="metric-value">${data.monitored_paths || 'N/A'}</span></div>
                <div class="metric"><span class="metric-label">總空間:</span><span class="metric-value">${formatBytes(data.total_space || 0)}</span></div>
                <div class="metric"><span class="metric-label">可用空間:</span><span class="metric-value">${formatBytes(data.free_space || 0)}</span></div>
                <div class="metric"><span class="metric-label">使用率:</span><span class="metric-value">${data.usage_percent || 'N/A'}%</span></div>
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
            
            let data;
            try {
                data = await fetchData(`/api/services/paginated?${params}`);
                
                if (data.error) {
                    const servicesContent = document.getElementById('services-virtual-content');
                    servicesContent.className = 'virtual-scroll-content'; // 移除loading class
                    servicesContent.innerHTML = 
                        `<div style="color: #e74c3c; padding: 20px;">錯誤: ${data.error}</div>`;
                    return;
                }
                
                // 確保 data 是有效的對象
                if (!data || typeof data !== 'object') {
                    throw new Error('無效的服務數據');
                }
                
            } catch (error) {
                console.error('更新服務信息失敗:', error);
                const servicesContent = document.getElementById('services-virtual-content');
                servicesContent.className = 'virtual-scroll-content'; // 移除loading class
                servicesContent.innerHTML = 
                    `<div style="color: #e74c3c; padding: 20px;">載入服務信息失敗: ${error.message}</div>`;
                return;
            }
            
            // 明確移除載入狀態
            const servicesContent = document.getElementById('services-virtual-content');
            servicesContent.className = 'virtual-scroll-content'; // 移除loading class
            
            // 更新虛擬滾動列表
            virtualScrollList.setData(data.services || []);
            
            // 更新分頁信息
            totalPages = data.total_pages || 1;
            document.getElementById('page-info').textContent = 
                `第 ${currentPage} 頁，共 ${totalPages} 頁 (總計 ${data.total_count || 0} 個服務)`;
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
            
            // 基本功能（必須成功）
            const basicUpdates = [
                updateSystemInfo(),
                updateProcessInfo(),
                updateNetworkInfo(),
                updateFilesystemInfo(),
                updateServicesInfo()
            ];
            
            // 增強功能（允許失敗）
            const enhancedUpdates = [
                updateHealthInfo().catch(e => {
                    console.log('健康度功能暫時無法使用:', e);
                    const container = document.getElementById('health-info');
                    if (container) {
                        container.className = '';
                        container.innerHTML = `
                            <div style="text-align: center; padding: 20px; color: #6c757d;">
                                <div style="font-size: 16px; margin-bottom: 10px;">⚠️</div>
                                <div>健康度功能暫時無法使用</div>
                                <small style="opacity: 0.7;">錯誤: ${e.message}</small>
                            </div>
                        `;
                    }
                }),
                updateAlertsInfo().catch(e => {
                    console.log('警報功能暫時無法使用:', e);
                    const container = document.getElementById('alerts-info');
                    if (container) {
                        container.className = '';
                        container.innerHTML = `
                            <div style="text-align: center; padding: 20px; color: #6c757d;">
                                <div style="font-size: 16px; margin-bottom: 10px;">⚠️</div>
                                <div>警報功能暫時無法使用</div>
                                <small style="opacity: 0.7;">錯誤: ${e.message}</small>
                            </div>
                        `;
                    }
                }),
                updateLogs().catch(e => {
                    console.log('日誌功能暫時無法使用:', e);
                    const logsContent = document.getElementById('logs-content');
                    if (logsContent) {
                        logsContent.className = 'virtual-scroll-content';
                        logsContent.innerHTML = `
                            <div style="text-align: center; padding: 40px; color: #6c757d;">
                                <div style="font-size: 20px; margin-bottom: 15px;">⚠️</div>
                                <div style="font-size: 16px; margin-bottom: 10px;">日誌監控暫時無法使用</div>
                                <small style="opacity: 0.7;">需要系統權限才能讀取日誌文件<br/>
                                錯誤: ${e.message}</small>
                            </div>
                        `;
                    }
                })
            ];
            
            // 並行執行，但分開處理
            await Promise.all([
                Promise.all(basicUpdates),
                Promise.allSettled(enhancedUpdates)
            ]);
            
            console.log('數據刷新完成');
        }
    </script>
    
    <!-- 服務詳細資訊模態框 -->
    <div id="service-modal" class="modal-overlay" onclick="closeServiceModal(event)">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title" id="modal-service-name">服務詳細資訊</h3>
                <button class="modal-close" onclick="closeServiceModal()">&times;</button>
            </div>
            <div id="modal-service-content">
                <!-- 服務詳細資訊將在這裡動態載入 -->
            </div>
        </div>
    </div>
    
    <!-- 通知容器 -->
    <div id="notification-container" class="notification-container"></div>
    
    <script>
        // 搜尋和篩選功能
        let searchFilters = {
            search: '',
            status: '',
            cpu: '',
            memory: ''
        };
        
        let filteredServices = [];
        let originalServices = [];
        
        function handleServiceSearch() {
            const searchValue = document.getElementById('service-search').value.toLowerCase();
            searchFilters.search = searchValue;
            applyFilters();
        }
        
        function handleStatusFilter() {
            const statusValue = document.getElementById('status-filter').value;
            searchFilters.status = statusValue;
            applyFilters();
        }
        
        function handleCpuFilter() {
            const cpuValue = document.getElementById('cpu-filter').value;
            searchFilters.cpu = cpuValue;
            applyFilters();
        }
        
        function handleMemoryFilter() {
            const memoryValue = document.getElementById('memory-filter').value;
            searchFilters.memory = memoryValue;
            applyFilters();
        }
        
        function clearAllFilters() {
            document.getElementById('service-search').value = '';
            document.getElementById('status-filter').value = '';
            document.getElementById('cpu-filter').value = '';
            document.getElementById('memory-filter').value = '';
            
            searchFilters = {
                search: '',
                status: '',
                cpu: '',
                memory: ''
            };
            
            applyFilters();
        }
        
        function applyFilters() {
            if (!originalServices.length) {
                originalServices = virtualScrollList.data || [];
            }
            
            filteredServices = originalServices.filter(service => {
                // 文字搜尋
                if (searchFilters.search) {
                    const searchText = searchFilters.search;
                    const matchesSearch = (
                        service.name.toLowerCase().includes(searchText) ||
                        service.pid.toString().includes(searchText) ||
                        (service.cmdline && service.cmdline.toLowerCase().includes(searchText))
                    );
                    if (!matchesSearch) return false;
                }
                
                // 狀態篩選
                if (searchFilters.status) {
                    const status = service.status.toLowerCase();
                    if (searchFilters.status === 'running' && status !== 'running') return false;
                    if (searchFilters.status === 'sleeping' && status !== 'sleeping') return false;
                    if (searchFilters.status === 'stopped' && status !== 'stopped') return false;
                    if (searchFilters.status === 'zombie' && status !== 'zombie') return false;
                }
                
                // CPU 篩選
                if (searchFilters.cpu) {
                    const cpuPercent = service.cpu_percent || 0;
                    if (searchFilters.cpu === 'high' && cpuPercent <= 10) return false;
                    if (searchFilters.cpu === 'medium' && (cpuPercent <= 1 || cpuPercent > 10)) return false;
                    if (searchFilters.cpu === 'low' && cpuPercent >= 1) return false;
                }
                
                // 記憶體篩選
                if (searchFilters.memory) {
                    const memoryPercent = service.memory_percent || 0;
                    if (searchFilters.memory === 'high' && memoryPercent <= 5) return false;
                    if (searchFilters.memory === 'medium' && (memoryPercent <= 1 || memoryPercent > 5)) return false;
                    if (searchFilters.memory === 'low' && memoryPercent >= 1) return false;
                }
                
                return true;
            });
            
            // 更新搜尋結果資訊
            const resultsInfo = document.getElementById('search-results-info');
            const hasActiveFilters = Object.values(searchFilters).some(filter => filter !== '');
            
            if (hasActiveFilters) {
                resultsInfo.style.display = 'block';
                resultsInfo.textContent = `找到 ${filteredServices.length} 個符合條件的服務 (共 ${originalServices.length} 個)`;
            } else {
                resultsInfo.style.display = 'none';
            }
            
            // 更新虛擬滾動列表
            virtualScrollList.setData(filteredServices);
            
            // 重置分頁
            currentPage = 1;
            updatePaginationInfo();
        }
        
        function updatePaginationInfo() {
            const totalCount = filteredServices.length || originalServices.length;
            document.getElementById('page-info').textContent = 
                `第 ${currentPage} 頁，共 ${totalPages} 頁 (總計 ${totalCount} 個服務)`;
        }
        
        // 服務詳細資訊模態框
        async function showServiceDetails(serviceData) {
            const modal = document.getElementById('service-modal');
            const modalTitle = document.getElementById('modal-service-name');
            const modalContent = document.getElementById('modal-service-content');
            
            modalTitle.textContent = serviceData.name;
            modalContent.innerHTML = '<div class="loading-indicator"></div>';
            
            modal.classList.add('active');
            
            try {
                // 獲取詳細資訊
                const response = await fetch(`/api/services/control?action=info&pid=${serviceData.pid}`);
                const detailData = await response.json();
                
                if (detailData.service_info) {
                    const info = detailData.service_info;
                    const createTime = new Date(info.create_time * 1000);
                    
                    modalContent.innerHTML = `
                        <div class="service-detail-section">
                            <h4>基本資訊</h4>
                            <div class="service-detail-grid">
                                <div class="service-detail-item">
                                    <div class="service-detail-label">服務名稱</div>
                                    <div class="service-detail-value">${info.name}</div>
                                </div>
                                <div class="service-detail-item">
                                    <div class="service-detail-label">進程 ID</div>
                                    <div class="service-detail-value">${info.pid}</div>
                                </div>
                                <div class="service-detail-item">
                                    <div class="service-detail-label">狀態</div>
                                    <div class="service-detail-value">${info.status}</div>
                                </div>
                                <div class="service-detail-item">
                                    <div class="service-detail-label">建立時間</div>
                                    <div class="service-detail-value">${createTime.toLocaleString()}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="service-detail-section">
                            <h4>資源使用</h4>
                            <div class="service-detail-grid">
                                <div class="service-detail-item">
                                    <div class="service-detail-label">CPU 使用率</div>
                                    <div class="service-detail-value">${info.cpu_percent?.toFixed(2) || 0}%</div>
                                </div>
                                <div class="service-detail-item">
                                    <div class="service-detail-label">記憶體使用率</div>
                                    <div class="service-detail-value">${info.memory_percent?.toFixed(2) || 0}%</div>
                                </div>
                                <div class="service-detail-item">
                                    <div class="service-detail-label">工作目錄</div>
                                    <div class="service-detail-value">${info.cwd || 'N/A'}</div>
                                </div>
                                <div class="service-detail-item">
                                    <div class="service-detail-label">用戶</div>
                                    <div class="service-detail-value">${info.username || 'N/A'}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="service-detail-section">
                            <h4>命令行</h4>
                            <div class="service-detail-item">
                                <div class="service-detail-label">完整命令</div>
                                <div class="service-detail-value">${info.cmdline || 'N/A'}</div>
                            </div>
                        </div>
                        
                        <div class="service-actions">
                            <button class="service-action-btn warning" onclick="terminateService(${info.pid}, false)">
                                ⏹️ 正常終止
                            </button>
                            <button class="service-action-btn danger" onclick="terminateService(${info.pid}, true)">
                                🛑 強制終止
                            </button>
                            <button class="service-action-btn primary" onclick="refreshServiceDetails(${info.pid})">
                                🔄 重新整理
                            </button>
                        </div>
                    `;
                } else {
                    modalContent.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: #6c757d;">
                            <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                            <div>無法獲取服務詳細資訊</div>
                        </div>
                    `;
                }
            } catch (error) {
                modalContent.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #e74c3c;">
                        <div style="font-size: 48px; margin-bottom: 20px;">❌</div>
                        <div>載入失敗: ${error.message}</div>
                    </div>
                `;
            }
        }
        
        function closeServiceModal(event) {
            if (event && event.target !== event.currentTarget) return;
            
            const modal = document.getElementById('service-modal');
            modal.classList.remove('active');
        }
        
        async function terminateService(pid, force = false) {
            const action = force ? '強制終止' : '正常終止';
            
            if (!confirm(`確定要${action}進程 ${pid} 嗎？`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/services/control', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'terminate',
                        pid: pid,
                        force: force
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification('成功', result.message, 'success');
                    closeServiceModal();
                    // 重新載入服務列表
                    setTimeout(() => {
                        updateServicesInfo();
                    }, 1000);
                } else {
                    showNotification('錯誤', result.message, 'error');
                }
            } catch (error) {
                showNotification('錯誤', `操作失敗: ${error.message}`, 'error');
            }
        }
        
        async function refreshServiceDetails(pid) {
            const modalContent = document.getElementById('modal-service-content');
            modalContent.innerHTML = '<div class="loading-indicator"></div>';
            
            // 重新載入服務詳細資訊
            const serviceData = { pid: pid };
            setTimeout(() => {
                showServiceDetails(serviceData);
            }, 500);
        }
        
        // 通知系統
        function showNotification(title, message, type = 'info') {
            const container = document.getElementById('notification-container');
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            
            notification.innerHTML = `
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
                <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
            `;
            
            container.appendChild(notification);
            
            // 觸發顯示動畫
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);
            
            // 自動移除
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }, 5000);
        }
        
        // 修改服務項目點擊事件
        function createServiceItem(service, index) {
            const div = document.createElement('div');
            div.className = 'service-item';
            div.onclick = () => showServiceDetails(service);
            
            const statusClass = service.status === 'running' ? 'status-running' : 
                               service.status === 'sleeping' ? 'status-sleeping' : 'status-stopped';
            
            div.innerHTML = `
                <div class="service-header">
                    <span class="service-name">${service.name}</span>
                    <span class="service-pid">PID: ${service.pid}</span>
                </div>
                <div class="service-metrics">
                    <div class="metric">
                        <span class="metric-label">狀態:</span>
                        <span class="metric-value ${statusClass}">${service.status}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CPU:</span>
                        <span class="metric-value">${service.cpu_percent?.toFixed(1) || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">記憶體:</span>
                        <span class="metric-value">${service.memory_percent?.toFixed(1) || 0}%</span>
                    </div>
                </div>
            `;
            
            return div;
        }
        
        // 重寫 updateServicesInfo 函數以支援篩選
        const originalUpdateServicesInfo = updateServicesInfo;
        updateServicesInfo = async function() {
            await originalUpdateServicesInfo();
            
            // 保存原始數據
            if (virtualScrollList && virtualScrollList.data) {
                originalServices = [...virtualScrollList.data];
                
                // 如果有篩選條件，重新應用篩選
                const hasActiveFilters = Object.values(searchFilters).some(filter => filter !== '');
                if (hasActiveFilters) {
                    applyFilters();
                }
            }
        };
        
        // 服務狀態變化監控
        let previousServiceStates = {};
        
        function monitorServiceChanges() {
            if (!originalServices.length) return;
            
            originalServices.forEach(service => {
                const serviceKey = `${service.name}-${service.pid}`;
                const currentState = {
                    status: service.status,
                    cpu_percent: service.cpu_percent,
                    memory_percent: service.memory_percent
                };
                
                if (previousServiceStates[serviceKey]) {
                    const prevState = previousServiceStates[serviceKey];
                    
                    // 檢查狀態變化
                    if (prevState.status !== currentState.status) {
                        showNotification(
                            '服務狀態變化',
                            `${service.name} (PID: ${service.pid}) 狀態從 ${prevState.status} 變為 ${currentState.status}`,
                            currentState.status === 'running' ? 'success' : 'warning'
                        );
                    }
                    
                    // 檢查高 CPU 使用率
                    if (currentState.cpu_percent > 80 && prevState.cpu_percent <= 80) {
                        showNotification(
                            '高 CPU 使用率警告',
                            `${service.name} (PID: ${service.pid}) CPU 使用率達到 ${currentState.cpu_percent.toFixed(1)}%`,
                            'warning'
                        );
                    }
                    
                    // 檢查高記憶體使用率
                    if (currentState.memory_percent > 80 && prevState.memory_percent <= 80) {
                        showNotification(
                            '高記憶體使用率警告',
                            `${service.name} (PID: ${service.pid}) 記憶體使用率達到 ${currentState.memory_percent.toFixed(1)}%`,
                            'warning'
                        );
                    }
                }
                
                previousServiceStates[serviceKey] = currentState;
            });
        }
        
        // 定期監控服務狀態變化
        setInterval(monitorServiceChanges, 5000);
        
        // 鍵盤快捷鍵
        document.addEventListener('keydown', function(e) {
            // ESC 鍵關閉模態框
            if (e.key === 'Escape') {
                closeServiceModal();
            }
            
            // Ctrl+F 聚焦搜尋框
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                document.getElementById('service-search').focus();
            }
        });
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
            
            # 如果沒有歷史數據，提供預設值
            if not health_score or health_score.get('overall', 0) == 0:
                # 使用當前系統數據計算基本健康度
                try:
                    import mcp_servers.mcp_system_monitor as system_monitor
                    import mcp_servers.mcp_process_monitor as process_monitor
                    
                    system_data = system_monitor.get_system_summary()
                    process_data = process_monitor.get_process_summary()
                    
                    # 簡單的健康度計算
                    cpu_score = max(0, 100 - (system_data.get('cpu_percent', 0)))
                    memory_score = max(0, 100 - (system_data.get('memory_percent', 0)))
                    disk_score = max(0, 100 - (system_data.get('disk_percent', 0)))
                    process_score = max(0, 100 - (process_data.get('zombie_processes', 0)))
                    
                    overall_score = (cpu_score * 0.3 + memory_score * 0.3 + 
                                   disk_score * 0.2 + process_score * 0.2)
                    
                    health_score = {
                        'overall': round(overall_score, 2),
                        'cpu': round(cpu_score, 2),
                        'memory': round(memory_score, 2),
                        'disk': round(disk_score, 2),
                        'process': round(process_score, 2)
                    }
                except Exception as calc_error:
                    print(f"健康度計算錯誤: {calc_error}")
                    health_score = {
                        'overall': 50.0,
                        'cpu': 50.0,
                        'memory': 50.0,
                        'disk': 50.0,
                        'process': 50.0
                    }
            
            self.send_json_response(health_score, supports_gzip)
            
        except Exception as e:
            print(f"健康度評分錯誤: {e}")
            self.send_json_response({'error': f'健康度功能暫時無法使用: {str(e)}'}, supports_gzip)
    
    def serve_alerts(self, supports_gzip=False):
        """提供警報資訊"""
        from datetime import datetime
        
        try:
            # 嘗試使用增強功能
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
                
            except Exception as enhanced_error:
                print(f"增強警報功能錯誤: {enhanced_error}")
                
                # 降級：提供基本的警報檢查
                try:
                    import mcp_servers.mcp_system_monitor as system_monitor
                    system_data = system_monitor.get_system_summary()
                    
                    current_alerts = []
                    
                    # 基本的警報檢查
                    cpu_percent = system_data.get('cpu_percent', 0)
                    memory_percent = system_data.get('memory_percent', 0)
                    disk_percent = system_data.get('disk_percent', 0)
                    
                    if cpu_percent > 85:
                        current_alerts.append({
                            'title': 'CPU 使用率過高',
                            'description': f'CPU 使用率達到 {cpu_percent:.1f}%',
                            'severity': 'critical',
                            'timestamp': datetime.now().isoformat()
                        })
                    elif cpu_percent > 70:
                        current_alerts.append({
                            'title': 'CPU 使用率警告',
                            'description': f'CPU 使用率達到 {cpu_percent:.1f}%',
                            'severity': 'warning',
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    if memory_percent > 90:
                        current_alerts.append({
                            'title': '記憶體使用率過高',
                            'description': f'記憶體使用率達到 {memory_percent:.1f}%',
                            'severity': 'critical',
                            'timestamp': datetime.now().isoformat()
                        })
                    elif memory_percent > 80:
                        current_alerts.append({
                            'title': '記憶體使用率警告',
                            'description': f'記憶體使用率達到 {memory_percent:.1f}%',
                            'severity': 'warning',
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    if disk_percent > 95:
                        current_alerts.append({
                            'title': '磁碟空間不足',
                            'description': f'磁碟使用率達到 {disk_percent:.1f}%',
                            'severity': 'critical',
                            'timestamp': datetime.now().isoformat()
                        })
                    elif disk_percent > 85:
                        current_alerts.append({
                            'title': '磁碟空間警告',
                            'description': f'磁碟使用率達到 {disk_percent:.1f}%',
                            'severity': 'warning',
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    data = {
                        'current_alerts': current_alerts,
                        'recent_alerts': [],
                        'alert_count': len(current_alerts)
                    }
                    
                except Exception as basic_error:
                    print(f"基本警報功能錯誤: {basic_error}")
                    data = {
                        'current_alerts': [],
                        'recent_alerts': [],
                        'alert_count': 0
                    }
            
            self.send_json_response(data, supports_gzip)
            
        except Exception as e:
            print(f"警報系統錯誤: {e}")
            self.send_json_response({'error': f'警報功能暫時無法使用: {str(e)}'}, supports_gzip)
    
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
    # 嘗試啟動增強功能
    enhanced_features = []
    
    # 歷史數據收集
    try:
        from mcp_servers.mcp_history_manager import start_history_collection
        start_history_collection()
        enhanced_features.append("歷史數據收集")
    except Exception as e:
        print(f"⚠️  歷史數據功能啟動失敗: {e}")
    
    # 服務監控和警報（需要psutil）
    try:
        from mcp_servers.mcp_service_controller import start_service_monitoring
        start_service_monitoring()
        enhanced_features.append("警報系統")
    except Exception as e:
        print(f"⚠️  警報系統啟動失敗: {e}")
    
    # 日誌監控
    try:
        from mcp_servers.mcp_log_monitor import start_log_monitoring
        start_log_monitoring(['system', 'auth'])
        enhanced_features.append("日誌監控")
    except Exception as e:
        print(f"⚠️  日誌監控啟動失敗: {e}")
    
    if enhanced_features:
        print(f"✅ 已啟動增強功能: {', '.join(enhanced_features)}")
    else:
        print("ℹ️  基本監控功能可用，增強功能將在API調用時動態載入")
    
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
        
        # 嘗試停止各個增強功能
        try:
            from mcp_servers.mcp_history_manager import stop_history_collection
            stop_history_collection()
            print("✅ 歷史數據收集已停止")
        except Exception as e:
            print(f"⚠️  停止歷史數據功能失敗: {e}")
        
        try:
            from mcp_servers.mcp_service_controller import stop_service_monitoring
            stop_service_monitoring()
            print("✅ 警報系統已停止")
        except Exception as e:
            print(f"⚠️  停止警報系統失敗: {e}")
        
        try:
            from mcp_servers.mcp_log_monitor import stop_log_monitoring
            stop_log_monitoring()
            print("✅ 日誌監控已停止")
        except Exception as e:
            print(f"⚠️  停止日誌監控失敗: {e}")
        
        print("✅ 伺服器已停止")
        httpd.server_close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    run_optimized_server(port)
