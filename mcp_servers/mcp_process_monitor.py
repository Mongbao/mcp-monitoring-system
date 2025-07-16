#!/usr/bin/env python3
"""
進程監控 MCP Server
提供進程監控和管理功能
"""

import asyncio
import json
import os
import signal
from datetime import datetime
from mcp.server import Server
from mcp.types import Resource, Tool
from typing import Any, Dict, List
import psutil

app = Server("process-monitor")

# 從環境變數取得要監控的進程
MONITOR_PROCESSES = os.environ.get("MONITOR_PROCESSES", "apache2,nginx,mysql").split(",")

@app.list_resources()
async def list_resources() -> List[Resource]:
    """列出可用的進程監控資源"""
    return [
        Resource(
            uri="process://all",
            name="所有進程",
            mimeType="application/json",
            description="系統中所有進程的概覽"
        ),
        Resource(
            uri="process://monitored",
            name="監控進程",
            mimeType="application/json",
            description="配置監控的特定進程狀態"
        ),
        Resource(
            uri="process://top",
            name="TOP 進程",
            mimeType="application/json",
            description="CPU 和記憶體使用率最高的進程"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """讀取進程監控資源"""
    if uri == "process://all":
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    info = proc.info
                    info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
                    processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            processes = [{"error": f"無法獲取進程列表: {e}"}]
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "total_processes": len(processes),
            "processes": processes[:100]  # 限制結果數量
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    elif uri == "process://monitored":
        monitored_status = []
        
        for process_name in MONITOR_PROCESSES:
            found_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        info = proc.info.copy()
                        info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
                        found_processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            monitored_status.append({
                "process_name": process_name,
                "running": len(found_processes) > 0,
                "instance_count": len(found_processes),
                "instances": found_processes
            })
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "monitored_processes": monitored_status
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    elif uri == "process://top":
        # 獲取 CPU 和記憶體使用率最高的進程
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    info = proc.info
                    if info['cpu_percent'] is not None and info['memory_percent'] is not None:
                        processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            return json.dumps({"error": f"無法獲取進程資訊: {e}"}, ensure_ascii=False)
        
        # 依照 CPU 使用率排序
        top_cpu = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
        
        # 依照記憶體使用率排序
        top_memory = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:10]
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "top_cpu_processes": top_cpu,
            "top_memory_processes": top_memory
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f"未知的資源 URI: {uri}")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用的進程監控工具"""
    return [
        Tool(
            name="get_process_details",
            description="獲取特定進程的詳細資訊",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "進程 ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "進程名稱"
                    }
                },
                "anyOf": [
                    {"required": ["pid"]},
                    {"required": ["name"]}
                ]
            }
        ),
        Tool(
            name="kill_process",
            description="終止進程",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "要終止的進程 ID"
                    },
                    "signal": {
                        "type": "string",
                        "description": "發送的信號",
                        "enum": ["TERM", "KILL", "HUP", "USR1", "USR2"],
                        "default": "TERM"
                    }
                },
                "required": ["pid"]
            }
        ),
        Tool(
            name="monitor_process_tree",
            description="監控進程樹",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "父進程 ID"
                    }
                },
                "required": ["pid"]
            }
        ),
        Tool(
            name="check_service_health",
            description="檢查服務健康狀態",
            inputSchema={
                "type": "object",
                "properties": {
                    "services": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要檢查的服務名稱列表",
                        "default": ["apache2", "nginx", "mysql", "redis"]
                    }
                },
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """執行進程監控工具"""
    if name == "get_process_details":
        processes = []
        
        if "pid" in arguments:
            try:
                proc = psutil.Process(arguments["pid"])
                processes.append(proc)
            except psutil.NoSuchProcess:
                return [f"找不到 PID {arguments['pid']} 的進程"]
        
        elif "name" in arguments:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if arguments["name"].lower() in proc.info['name'].lower():
                        processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        if not processes:
            return ["找不到符合條件的進程"]
        
        detailed_info = []
        for proc in processes:
            try:
                info = proc.as_dict(attrs=[
                    'pid', 'name', 'exe', 'cmdline', 'status', 'username',
                    'create_time', 'cpu_percent', 'memory_percent', 'memory_info',
                    'num_threads', 'num_fds', 'connections'
                ])
                
                # 格式化時間
                info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
                
                # 格式化記憶體資訊
                if info['memory_info']:
                    memory_info = info['memory_info']
                    info['memory_info'] = {
                        'rss_mb': round(memory_info.rss / (1024 * 1024), 2),
                        'vms_mb': round(memory_info.vms / (1024 * 1024), 2)
                    }
                
                # 格式化連線資訊
                if info['connections']:
                    connections = []
                    for conn in info['connections'][:10]:  # 限制連線數量
                        conn_info = {
                            'family': str(conn.family),
                            'type': str(conn.type),
                            'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                            'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                            'status': conn.status
                        }
                        connections.append(conn_info)
                    info['connections'] = connections
                
                detailed_info.append(info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                detailed_info.append({
                    "pid": proc.pid,
                    "error": str(e)
                })
        
        return [json.dumps(detailed_info, indent=2, ensure_ascii=False)]
    
    elif name == "kill_process":
        pid = arguments["pid"]
        signal_name = arguments.get("signal", "TERM")
        
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            # 轉換信號名稱
            signal_map = {
                "TERM": signal.SIGTERM,
                "KILL": signal.SIGKILL,
                "HUP": signal.SIGHUP,
                "USR1": signal.SIGUSR1,
                "USR2": signal.SIGUSR2
            }
            
            if signal_name not in signal_map:
                return [f"不支援的信號: {signal_name}"]
            
            # 發送信號
            proc.send_signal(signal_map[signal_name])
            
            result = {
                "pid": pid,
                "process_name": process_name,
                "signal": signal_name,
                "success": True,
                "message": f"成功向進程 {pid} ({process_name}) 發送 {signal_name} 信號"
            }
            
            return [json.dumps(result, indent=2, ensure_ascii=False)]
            
        except psutil.NoSuchProcess:
            return [f"進程 {pid} 不存在"]
        except psutil.AccessDenied:
            return [f"沒有權限終止進程 {pid}"]
        except Exception as e:
            return [f"終止進程失敗: {e}"]
    
    elif name == "monitor_process_tree":
        pid = arguments["pid"]
        
        try:
            parent = psutil.Process(pid)
            
            def build_tree(proc, level=0):
                try:
                    info = proc.as_dict(attrs=['pid', 'name', 'status', 'cpu_percent', 'memory_percent'])
                    info['level'] = level
                    info['indent'] = "  " * level
                    
                    tree = [info]
                    
                    # 獲取子進程
                    for child in proc.children():
                        tree.extend(build_tree(child, level + 1))
                    
                    return tree
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return []
            
            tree = build_tree(parent)
            
            result = {
                "parent_pid": pid,
                "tree": tree,
                "total_processes": len(tree)
            }
            
            return [json.dumps(result, indent=2, ensure_ascii=False)]
            
        except psutil.NoSuchProcess:
            return [f"進程 {pid} 不存在"]
        except Exception as e:
            return [f"獲取進程樹失敗: {e}"]
    
    elif name == "check_service_health":
        services = arguments.get("services", ["apache2", "nginx", "mysql", "redis"])
        
        health_status = []
        
        for service in services:
            status = {
                "service": service,
                "running": False,
                "processes": [],
                "total_memory_mb": 0,
                "total_cpu_percent": 0
            }
            
            # 尋找相關進程
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'memory_info']):
                try:
                    if service.lower() in proc.info['name'].lower():
                        status["running"] = True
                        status["processes"].append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "status": proc.info['status'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": proc.info['memory_percent']
                        })
                        status["total_cpu_percent"] += proc.info['cpu_percent'] or 0
                        if proc.info['memory_info']:
                            status["total_memory_mb"] += proc.info['memory_info'].rss / (1024 * 1024)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            status["process_count"] = len(status["processes"])
            status["total_memory_mb"] = round(status["total_memory_mb"], 2)
            status["total_cpu_percent"] = round(status["total_cpu_percent"], 2)
            
            health_status.append(status)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "services_checked": len(services),
            "services_running": sum(1 for s in health_status if s["running"]),
            "service_status": health_status
        }
        
        return [json.dumps(result, indent=2, ensure_ascii=False)]
    
    else:
        raise ValueError(f"未知的工具: {name}")

# 同步函數用於 Web 伺服器
def get_process_summary():
    """獲取進程摘要信息"""
    try:
        total_processes = len(list(psutil.process_iter()))
        running_processes = len([p for p in psutil.process_iter() if p.status() == psutil.STATUS_RUNNING])
        sleeping_processes = len([p for p in psutil.process_iter() if p.status() == psutil.STATUS_SLEEPING])
        zombie_processes = len([p for p in psutil.process_iter() if p.status() == psutil.STATUS_ZOMBIE])
        
        return {
            "total_processes": total_processes,
            "running_processes": running_processes,
            "sleeping_processes": sleeping_processes,
            "zombie_processes": zombie_processes,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def get_detailed_processes():
    """獲取詳細的進程列表"""
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                info = proc.info
                # 計算進程運行時間
                create_time = datetime.fromtimestamp(info['create_time']).isoformat()
                
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'] or 'Unknown',
                    "status": info['status'],
                    "cpu_percent": round(info['cpu_percent'] or 0, 2),
                    "memory_percent": round(info['memory_percent'] or 0, 2),
                    "create_time": create_time
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(app)
