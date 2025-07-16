#!/usr/bin/env python3
"""
系統監控 MCP Server
提供系統資源監控功能 (CPU, 記憶體, 磁碟等)
"""

import asyncio
import json
import psutil
import platform
from datetime import datetime
from mcp.server import Server
from mcp.types import Resource, Tool
from typing import Any, Dict, List

app = Server("system-monitor")

@app.list_resources()
async def list_resources() -> List[Resource]:
    """列出可用的系統監控資源"""
    return [
        Resource(
            uri="system://cpu",
            name="CPU 使用率",
            mimeType="application/json",
            description="當前 CPU 使用率資訊"
        ),
        Resource(
            uri="system://memory", 
            name="記憶體使用率",
            mimeType="application/json",
            description="當前記憶體使用率資訊"
        ),
        Resource(
            uri="system://disk",
            name="磁碟使用率",
            mimeType="application/json", 
            description="當前磁碟使用率資訊"
        ),
        Resource(
            uri="system://network",
            name="網路統計",
            mimeType="application/json",
            description="網路 I/O 統計資訊"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """讀取系統監控資源"""
    if uri == "system://cpu":
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_info = {
            "timestamp": datetime.now().isoformat(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent_total": psutil.cpu_percent(interval=1),
            "cpu_percent_per_core": cpu_percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        return json.dumps(cpu_info, indent=2, ensure_ascii=False)
    
    elif uri == "system://memory":
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = {
            "timestamp": datetime.now().isoformat(),
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent
        }
        return json.dumps(memory_info, indent=2, ensure_ascii=False)
    
    elif uri == "system://disk":
        disk_usage = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100
                })
            except PermissionError:
                continue
        
        disk_info = {
            "timestamp": datetime.now().isoformat(),
            "partitions": disk_usage
        }
        return json.dumps(disk_info, indent=2, ensure_ascii=False)
    
    elif uri == "system://network":
        net_io = psutil.net_io_counters()
        network_info = {
            "timestamp": datetime.now().isoformat(),
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout,
            "dropin": net_io.dropin,
            "dropout": net_io.dropout
        }
        return json.dumps(network_info, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f"未知的資源 URI: {uri}")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用的系統監控工具"""
    return [
        Tool(
            name="get_system_summary",
            description="獲取系統整體摘要資訊",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="monitor_process",
            description="監控特定程序",
            inputSchema={
                "type": "object", 
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "程序 ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "程序名稱"
                    }
                },
                "anyOf": [
                    {"required": ["pid"]},
                    {"required": ["name"]}
                ]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """執行系統監控工具"""
    if name == "get_system_summary":
        # 獲取系統整體摘要
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "processor": platform.processor()
            },
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "percent": round((disk_usage.used / disk_usage.total) * 100, 2)
            }
        }
        
        return [json.dumps(summary, indent=2, ensure_ascii=False)]
    
    elif name == "monitor_process":
        processes = []
        
        if "pid" in arguments:
            try:
                process = psutil.Process(arguments["pid"])
                processes.append(process)
            except psutil.NoSuchProcess:
                return [f"找不到 PID {arguments['pid']} 的程序"]
                
        elif "name" in arguments:
            for proc in psutil.process_iter(['pid', 'name']):
                if arguments["name"].lower() in proc.info['name'].lower():
                    processes.append(proc)
        
        if not processes:
            return ["找不到符合條件的程序"]
        
        process_info = []
        for proc in processes:
            try:
                info = proc.as_dict(attrs=[
                    'pid', 'name', 'status', 'cpu_percent', 
                    'memory_percent', 'memory_info', 'create_time'
                ])
                info['create_time'] = datetime.fromtimestamp(info['create_time']).isoformat()
                process_info.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return [json.dumps(process_info, indent=2, ensure_ascii=False)]
    
    else:
        raise ValueError(f"未知的工具: {name}")

# 同步函數用於 Web 伺服器
def get_system_summary():
    """獲取系統摘要信息"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        load_avg = psutil.getloadavg()
        
        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory.percent, 2),
            "disk_percent": round((disk_usage.used / disk_usage.total) * 100, 2),
            "load_avg": f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}",
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2)
            },
            "disk": {
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(app)
