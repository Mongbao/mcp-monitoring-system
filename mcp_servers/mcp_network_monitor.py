#!/usr/bin/env python3
"""
網路監控 MCP Server
提供網路連線和流量監控功能
"""

import asyncio
import json
import os
import socket
import subprocess
from datetime import datetime
from mcp.server import Server
from mcp.types import Resource, Tool
from typing import Any, Dict, List
import psutil

app = Server("network-monitor")

# 從環境變數取得監控介面
MONITOR_INTERFACES = os.environ.get("MONITOR_INTERFACES", "eth0,wlan0").split(",")

@app.list_resources()
async def list_resources() -> List[Resource]:
    """列出可用的網路監控資源"""
    return [
        Resource(
            uri="network://interfaces",
            name="網路介面",
            mimeType="application/json",
            description="所有網路介面的狀態和統計"
        ),
        Resource(
            uri="network://connections",
            name="網路連線",
            mimeType="application/json",
            description="當前活躍的網路連線"
        ),
        Resource(
            uri="network://traffic",
            name="網路流量",
            mimeType="application/json",
            description="網路流量統計"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """讀取網路監控資源"""
    if uri == "network://interfaces":
        interfaces = {}
        
        # 獲取所有網路介面
        for interface, addrs in psutil.net_if_addrs().items():
            interfaces[interface] = {
                "addresses": []
            }
            
            for addr in addrs:
                addr_info = {
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                }
                interfaces[interface]["addresses"].append(addr_info)
        
        # 獲取介面統計
        stats = psutil.net_if_stats()
        for interface in interfaces:
            if interface in stats:
                stat = stats[interface]
                interfaces[interface]["stats"] = {
                    "isup": stat.isup,
                    "duplex": str(stat.duplex),
                    "speed": stat.speed,
                    "mtu": stat.mtu
                }
        
        # 獲取 I/O 統計
        io_counters = psutil.net_io_counters(pernic=True)
        for interface in interfaces:
            if interface in io_counters:
                counter = io_counters[interface]
                interfaces[interface]["io"] = {
                    "bytes_sent": counter.bytes_sent,
                    "bytes_recv": counter.bytes_recv,
                    "packets_sent": counter.packets_sent,
                    "packets_recv": counter.packets_recv,
                    "errin": counter.errin,
                    "errout": counter.errout,
                    "dropin": counter.dropin,
                    "dropout": counter.dropout
                }
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "interfaces": interfaces
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    elif uri == "network://connections":
        connections = []
        
        try:
            for conn in psutil.net_connections():
                conn_info = {
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid
                }
                connections.append(conn_info)
        except (psutil.AccessDenied, PermissionError):
            # 如果權限不足，嘗試只獲取基本資訊
            try:
                for conn in psutil.net_connections(kind='inet'):
                    conn_info = {
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status
                    }
                    connections.append(conn_info)
            except:
                connections = [{"error": "權限不足，無法獲取連線資訊"}]
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "connection_count": len(connections),
            "connections": connections[:100]  # 限制結果數量
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    elif uri == "network://traffic":
        # 獲取總體流量統計
        net_io = psutil.net_io_counters()
        
        # 獲取各介面流量
        per_nic = psutil.net_io_counters(pernic=True)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "total": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout
            },
            "per_interface": {}
        }
        
        for nic, counter in per_nic.items():
            result["per_interface"][nic] = {
                "bytes_sent": counter.bytes_sent,
                "bytes_recv": counter.bytes_recv,
                "packets_sent": counter.packets_sent,
                "packets_recv": counter.packets_recv,
                "errin": counter.errin,
                "errout": counter.errout,
                "dropin": counter.dropin,
                "dropout": counter.dropout
            }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f"未知的資源 URI: {uri}")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用的網路監控工具"""
    return [
        Tool(
            name="ping_host",
            description="Ping 主機測試連通性",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "要 ping 的主機 IP 或域名"
                    },
                    "count": {
                        "type": "integer",
                        "description": "ping 次數",
                        "default": 4
                    }
                },
                "required": ["host"]
            }
        ),
        Tool(
            name="port_scan",
            description="掃描主機開放的埠",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "要掃描的主機 IP"
                    },
                    "ports": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要掃描的埠列表",
                        "default": [22, 80, 443, 3306, 5432, 6379]
                    }
                },
                "required": ["host"]
            }
        ),
        Tool(
            name="get_routing_table",
            description="獲取路由表",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """執行網路監控工具"""
    if name == "ping_host":
        host = arguments["host"]
        count = arguments.get("count", 4)
        
        try:
            # 使用 ping 命令
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            ping_result = {
                "host": host,
                "count": count,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
            return [json.dumps(ping_result, indent=2, ensure_ascii=False)]
            
        except subprocess.TimeoutExpired:
            return [json.dumps({"error": f"Ping {host} 超時"}, ensure_ascii=False)]
        except Exception as e:
            return [json.dumps({"error": f"Ping 失敗: {e}"}, ensure_ascii=False)]
    
    elif name == "port_scan":
        host = arguments["host"]
        ports = arguments.get("ports", [22, 80, 443, 3306, 5432, 6379])
        
        scan_results = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                sock.close()
                
                scan_results.append({
                    "port": port,
                    "open": result == 0,
                    "service": get_service_name(port)
                })
            except Exception as e:
                scan_results.append({
                    "port": port,
                    "open": False,
                    "error": str(e)
                })
        
        result = {
            "host": host,
            "scan_results": scan_results,
            "open_ports": [r["port"] for r in scan_results if r.get("open")]
        }
        
        return [json.dumps(result, indent=2, ensure_ascii=False)]
    
    elif name == "get_routing_table":
        try:
            # 使用 ip route 命令獲取路由表
            result = subprocess.run(
                ["ip", "route", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                routes = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        routes.append(line.strip())
                
                routing_info = {
                    "timestamp": datetime.now().isoformat(),
                    "routes": routes
                }
            else:
                routing_info = {
                    "error": "無法獲取路由表",
                    "stderr": result.stderr
                }
            
            return [json.dumps(routing_info, indent=2, ensure_ascii=False)]
            
        except Exception as e:
            return [json.dumps({"error": f"獲取路由表失敗: {e}"}, ensure_ascii=False)]
    
    else:
        raise ValueError(f"未知的工具: {name}")

def get_service_name(port):
    """根據埠號獲取常見服務名稱"""
    services = {
        22: "SSH",
        23: "Telnet", 
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB"
    }
    return services.get(port, "Unknown")

# 同步函數用於 Web 伺服器
def get_network_summary():
    """獲取網路摘要信息"""
    try:
        # 獲取網路統計
        net_io = psutil.net_io_counters()
        connections = len(psutil.net_connections())
        interfaces = psutil.net_if_addrs()
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "interface_count": len(interfaces),
            "connections": connections,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(app)
