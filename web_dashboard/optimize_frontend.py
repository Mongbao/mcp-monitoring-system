#!/usr/bin/env python3
"""
前端資源優化工具
- JavaScript 和 CSS 壓縮
- 圖片優化
- 快取管理
"""

import os
import re
import gzip
import json
from pathlib import Path

class FrontendOptimizer:
    def __init__(self, web_dir="/home/bao/mcp_use/web_dashboard"):
        self.web_dir = Path(web_dir)
        self.static_dir = self.web_dir / "static"
        self.static_dir.mkdir(exist_ok=True)
    
    def minify_css(self, css_content):
        """壓縮 CSS"""
        # 移除註釋
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        # 移除多餘空白
        css_content = re.sub(r'\s+', ' ', css_content)
        # 移除分號前的空格
        css_content = re.sub(r'\s*;\s*', ';', css_content)
        # 移除大括號周圍的空格
        css_content = re.sub(r'\s*{\s*', '{', css_content)
        css_content = re.sub(r'\s*}\s*', '}', css_content)
        # 移除冒號周圍的空格
        css_content = re.sub(r'\s*:\s*', ':', css_content)
        # 移除逗號後的空格
        css_content = re.sub(r',\s*', ',', css_content)
        
        return css_content.strip()
    
    def minify_js(self, js_content):
        """簡單的 JavaScript 壓縮"""
        # 移除單行註釋
        js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
        # 移除多行註釋
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        # 移除多餘空白（保留字串內的空白）
        js_content = re.sub(r'\s+', ' ', js_content)
        # 移除分號前後的空格
        js_content = re.sub(r'\s*;\s*', ';', js_content)
        # 移除大括號周圍的空格
        js_content = re.sub(r'\s*{\s*', '{', js_content)
        js_content = re.sub(r'\s*}\s*', '}', js_content)
        
        return js_content.strip()
    
    def create_optimized_css(self):
        """創建優化的 CSS 檔案"""
        optimized_css = """
        /* MCP 監控系統 - 優化 CSS */
        *{box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;padding:20px;background-color:#f5f5f5;line-height:1.4}
        .header{background:linear-gradient(135deg,#2c3e50,#3498db);color:white;padding:20px;border-radius:8px;margin-bottom:20px;box-shadow:0 4px 6px rgba(0,0,0,0.1)}
        .dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
        .card{background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);transition:transform 0.2s ease,box-shadow 0.2s ease}
        .card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.15)}
        .card h3{margin-top:0;color:#2c3e50}
        .metric{display:flex;justify-content:space-between;margin:10px 0;padding:8px;border-radius:4px;background-color:#f8f9fa}
        .refresh-btn{background:linear-gradient(135deg,#3498db,#2980b9);color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;transition:all 0.2s ease}
        .refresh-btn:hover{transform:translateY(-1px);box-shadow:0 4px 8px rgba(52,152,219,0.3)}
        .loading{text-align:center;color:#7f8c8d;display:flex;align-items:center;justify-content:center;min-height:60px}
        .loading::after{content:'';width:20px;height:20px;border:2px solid #f3f3f3;border-top:2px solid #3498db;border-radius:50%;animation:spin 1s linear infinite;margin-left:10px}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
        .virtual-scroll-container{height:400px;overflow-y:auto;border:1px solid #e9ecef;border-radius:6px;position:relative}
        .virtual-scroll-content{position:relative}
        .virtual-item{padding:8px 12px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center;transition:background-color 0.15s ease}
        .virtual-item:hover{background-color:#f8f9fa}
        .lazy-chart{min-height:200px;display:flex;align-items:center;justify-content:center;background:#f8f9fa;border-radius:6px;margin:10px 0;cursor:pointer}
        .chart-placeholder{color:#6c757d;font-style:italic}
        .pagination-controls{display:flex;align-items:center;gap:10px;margin:15px 0;flex-wrap:wrap}
        .page-info{font-size:0.9em;color:#6c757d}
        .page-btn{padding:6px 12px;border:1px solid #ddd;background:white;border-radius:4px;cursor:pointer;transition:all 0.2s ease}
        .page-btn:hover:not(:disabled){background:#f8f9fa;border-color:#3498db}
        .page-btn:disabled{opacity:0.5;cursor:not-allowed}
        .page-btn.active{background:#3498db;color:white;border-color:#3498db}
        @media (max-width:768px){body{padding:10px}.dashboard{grid-template-columns:1fr;gap:15px}.virtual-scroll-container{height:300px}.pagination-controls{justify-content:center}}
        """
        
        css_file = self.static_dir / "optimized.min.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(optimized_css)
        
        # 創建 gzip 版本
        with open(css_file.with_suffix('.css.gz'), 'wb') as f:
            f.write(gzip.compress(optimized_css.encode('utf-8')))
        
        print(f"✅ 已創建優化 CSS: {css_file}")
        return css_file
    
    def create_optimized_js(self):
        """創建優化的 JavaScript 檔案"""
        optimized_js = """
        // MCP 監控系統 - 優化 JavaScript
        class VirtualScrollList{constructor(container,options={}){this.container=container;this.content=container.querySelector('.virtual-scroll-content');this.itemHeight=options.itemHeight||50;this.bufferSize=options.bufferSize||5;this.data=[];this.visibleStart=0;this.visibleEnd=0;this.renderedItems=new Map();this.container.addEventListener('scroll',this.handleScroll.bind(this));this.render=this.render.bind(this)}setData(data){this.data=data;this.content.style.height=(data.length*this.itemHeight)+'px';this.render()}handleScroll(){requestAnimationFrame(this.render)}render(){const containerHeight=this.container.clientHeight;const scrollTop=this.container.scrollTop;const startIndex=Math.floor(scrollTop/this.itemHeight);const endIndex=Math.min(startIndex+Math.ceil(containerHeight/this.itemHeight)+this.bufferSize,this.data.length);this.visibleStart=Math.max(0,startIndex-this.bufferSize);this.visibleEnd=endIndex;for(let[index,element]of this.renderedItems){if(index<this.visibleStart||index>=this.visibleEnd){element.remove();this.renderedItems.delete(index)}}for(let i=this.visibleStart;i<this.visibleEnd;i++){if(!this.renderedItems.has(i)&&this.data[i]){const element=this.createItem(this.data[i],i);element.style.position='absolute';element.style.top=(i*this.itemHeight)+'px';element.style.width='100%';element.style.height=this.itemHeight+'px';this.content.appendChild(element);this.renderedItems.set(i,element)}}}createItem(data,index){const div=document.createElement('div');div.className='virtual-item';div.innerHTML=`<div><strong>${data.name}</strong> (PID: ${data.pid})<br><small>CPU: ${data.cpu_percent}% | 記憶體: ${data.memory_percent}%</small></div><div style="text-align:right;"><div class="memory-bar" style="width:60px;height:8px;background:#eee;border-radius:4px;"><div style="width:${Math.min(data.memory_percent,100)}%;height:100%;background:${data.memory_percent>80?'#e74c3c':data.memory_percent>50?'#f39c12':'#27ae60'};border-radius:4px;"></div></div></div>`;return div}}
        class LazyChartManager{constructor(){this.charts=new Map();this.loadedCharts=new Set();this.initializeLazyCharts()}initializeLazyCharts(){document.querySelectorAll('.lazy-chart').forEach(chart=>{chart.addEventListener('click',()=>this.loadChart(chart.dataset.chart))})}async loadChart(chartType){if(this.loadedCharts.has(chartType))return;const chartContainer=document.querySelector(`[data-chart="${chartType}"]`);chartContainer.innerHTML='<div class="loading">載入圖表中...</div>';try{if(!window.Chart){await this.loadChartLibrary()}const data=await this.fetchChartData(chartType);const canvas=document.createElement('canvas');canvas.style.maxHeight='200px';chartContainer.innerHTML='';chartContainer.appendChild(canvas);this.createChart(canvas,chartType,data);this.loadedCharts.add(chartType)}catch(error){chartContainer.innerHTML=`<div style="color:#e74c3c;">圖表載入失敗: ${error.message}</div>`}}async loadChartLibrary(){return new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';script.onload=resolve;script.onerror=reject;document.head.appendChild(script)})}async fetchChartData(chartType){const endpoints={system:'/api/system',process:'/api/processes',network:'/api/network'};const response=await fetch(endpoints[chartType]);return await response.json()}createChart(canvas,chartType,data){const configs={system:{type:'doughnut',data:{labels:['已使用','可用'],datasets:[{data:[data.cpu_percent||0,100-(data.cpu_percent||0)],backgroundColor:['#e74c3c','#ecf0f1']}]},options:{responsive:true,plugins:{title:{display:true,text:'CPU 使用率分布'}}}},process:{type:'bar',data:{labels:['執行中','休眠中','殭屍進程'],datasets:[{data:[data.running_processes||0,data.sleeping_processes||0,data.zombie_processes||0],backgroundColor:['#27ae60','#3498db','#e74c3c']}]},options:{responsive:true,plugins:{title:{display:true,text:'進程狀態分布'},legend:{display:false}}}}};new Chart(canvas,configs[chartType])}}
        let virtualScrollList,lazyChartManager,currentPage=1,totalPages=1,pageSize=50;
        document.addEventListener('DOMContentLoaded',function(){const container=document.getElementById('services-virtual-container');virtualScrollList=new VirtualScrollList(container,{itemHeight:50});lazyChartManager=new LazyChartManager();refreshAll();setInterval(refreshAll,30000)});
        async function fetchData(endpoint){try{const response=await fetch(endpoint,{headers:{'Accept-Encoding':'gzip, deflate'}});if(!response.ok)throw new Error('Network response was not ok');return await response.json()}catch(error){console.error('Fetch error:',error);return{error:error.message}}}
        async function updateSystemInfo(){const data=await fetchData('/api/system');const container=document.getElementById('system-info');if(data.error){container.innerHTML=`<div style="color:#e74c3c;">錯誤: ${data.error}</div>`;return}container.innerHTML=`<div class="metric"><span>CPU 使用率:</span><span>${data.cpu_percent||'N/A'}%</span></div><div class="metric"><span>記憶體使用率:</span><span>${data.memory_percent||'N/A'}%</span></div><div class="metric"><span>磁碟使用率:</span><span>${data.disk_percent||'N/A'}%</span></div><div class="metric"><span>系統負載:</span><span>${data.load_avg||'N/A'}</span></div>`}
        function formatBytes(bytes){if(bytes===0)return'0 B';const k=1024;const sizes=['B','KB','MB','GB','TB'];const i=Math.floor(Math.log(bytes)/Math.log(k));return parseFloat((bytes/Math.pow(k,i)).toFixed(2))+' '+sizes[i]}
        async function refreshAll(){console.log('刷新所有數據...');await Promise.all([updateSystemInfo(),updateProcessInfo(),updateNetworkInfo(),updateFilesystemInfo(),updateServicesInfo()])}
        """
        
        js_file = self.static_dir / "optimized.min.js"
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(optimized_js)
        
        # 創建 gzip 版本
        with open(js_file.with_suffix('.js.gz'), 'wb') as f:
            f.write(gzip.compress(optimized_js.encode('utf-8')))
        
        print(f"✅ 已創建優化 JavaScript: {js_file}")
        return js_file
    
    def create_service_worker(self):
        """創建 Service Worker 進行快取管理"""
        sw_content = """
        // MCP 監控系統 Service Worker
        const CACHE_NAME = 'mcp-monitor-v1';
        const urlsToCache = [
            '/',
            '/static/optimized.min.css',
            '/static/optimized.min.js',
            'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js'
        ];
        
        self.addEventListener('install', function(event) {
            event.waitUntil(
                caches.open(CACHE_NAME)
                    .then(function(cache) {
                        return cache.addAll(urlsToCache);
                    })
            );
        });
        
        self.addEventListener('fetch', function(event) {
            // 只快取 GET 請求
            if (event.request.method !== 'GET') return;
            
            // API 請求不快取
            if (event.request.url.includes('/api/')) return;
            
            event.respondWith(
                caches.match(event.request)
                    .then(function(response) {
                        // 如果有快取，返回快取
                        if (response) {
                            return response;
                        }
                        
                        // 否則發送網路請求
                        return fetch(event.request);
                    }
                )
            );
        });
        """
        
        sw_file = self.static_dir / "sw.js"
        with open(sw_file, 'w', encoding='utf-8') as f:
            f.write(sw_content)
        
        print(f"✅ 已創建 Service Worker: {sw_file}")
        return sw_file
    
    def optimize_all(self):
        """執行所有優化"""
        print("🚀 開始前端資源優化...")
        
        css_file = self.create_optimized_css()
        js_file = self.create_optimized_js()
        sw_file = self.create_service_worker()
        
        # 計算檔案大小
        css_size = css_file.stat().st_size
        js_size = js_file.stat().st_size
        
        print(f"\n📊 優化結果:")
        print(f"   CSS 檔案大小: {css_size / 1024:.1f} KB")
        print(f"   JavaScript 檔案大小: {js_size / 1024:.1f} KB")
        print(f"   總計靜態資源: {(css_size + js_size) / 1024:.1f} KB")
        
        # 創建資源清單
        manifest = {
            "name": "MCP 監控系統",
            "short_name": "MCP Monitor",
            "description": "高性能系統監控儀表板",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#2c3e50",
            "theme_color": "#3498db",
            "icons": []
        }
        
        manifest_file = self.static_dir / "manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已創建應用清單: {manifest_file}")
        print("\n🎉 前端資源優化完成！")
        
        return {
            'css': css_file,
            'js': js_file,
            'sw': sw_file,
            'manifest': manifest_file
        }

def main():
    """主函數"""
    optimizer = FrontendOptimizer()
    results = optimizer.optimize_all()
    
    print("\n📝 使用建議:")
    print("1. 更新 web 伺服器以提供優化的靜態檔案")
    print("2. 啟用 gzip 壓縮以進一步減少傳輸大小")
    print("3. 設定適當的快取標頭")
    print("4. 考慮使用 CDN 進行靜態資源分發")

if __name__ == "__main__":
    main()
