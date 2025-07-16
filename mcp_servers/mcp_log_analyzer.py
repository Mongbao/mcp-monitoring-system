#!/usr/bin/env python3
"""
日誌分析 MCP Server
提供系統日誌分析和監控功能
"""

import asyncio
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from mcp.server import Server
from mcp.types import Resource, Tool
from typing import Any, Dict, List

app = Server("log-analyzer")

# 從環境變數取得日誌路徑
LOG_PATHS = os.environ.get("LOG_PATHS", "/var/log/syslog,/var/log/auth.log").split(",")

@app.list_resources()
async def list_resources() -> List[Resource]:
    """列出可用的日誌分析資源"""
    resources = []
    for log_path in LOG_PATHS:
        if os.path.exists(log_path) and os.path.isfile(log_path):
            resources.append(Resource(
                uri=f"log://{log_path}",
                name=f"日誌檔案 - {os.path.basename(log_path)}",
                mimeType="application/json",
                description=f"分析 {log_path} 日誌檔案"
            ))
    return resources

@app.read_resource()
async def read_resource(uri: str) -> str:
    """讀取日誌分析資源"""
    if not uri.startswith("log://"):
        raise ValueError(f"不支援的 URI: {uri}")
    
    log_path = uri[6:]  # 移除 "log://" 前綴
    
    if not os.path.exists(log_path):
        raise ValueError(f"日誌檔案不存在: {log_path}")
    
    try:
        # 獲取檔案基本資訊
        stat_info = os.stat(log_path)
        
        # 讀取最後幾行進行分析
        tail_lines = read_tail_lines(log_path, 100)
        
        # 分析日誌等級
        log_levels = analyze_log_levels(tail_lines)
        
        # 檢測錯誤和警告
        errors_warnings = detect_errors_warnings(tail_lines)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "log_file": log_path,
            "file_size": stat_info.st_size,
            "last_modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "recent_lines_analyzed": len(tail_lines),
            "log_levels": log_levels,
            "recent_errors_warnings": errors_warnings,
            "sample_lines": tail_lines[-10:] if tail_lines else []
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except (OSError, PermissionError) as e:
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "log_file": log_path,
            "error": str(e)
        }
        return json.dumps(error_info, indent=2, ensure_ascii=False)

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用的日誌分析工具"""
    return [
        Tool(
            name="search_logs",
            description="在日誌中搜尋特定模式",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_file": {
                        "type": "string",
                        "description": "要搜尋的日誌檔案路徑"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "搜尋模式 (支援正規表達式)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大結果數量",
                        "default": 50
                    },
                    "time_range_hours": {
                        "type": "integer",
                        "description": "時間範圍 (小時)",
                        "default": 24
                    }
                },
                "required": ["log_file", "pattern"]
            }
        ),
        Tool(
            name="analyze_error_trends",
            description="分析錯誤趨勢",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_file": {
                        "type": "string",
                        "description": "要分析的日誌檔案路徑"
                    },
                    "time_window_hours": {
                        "type": "integer",
                        "description": "分析時間窗口 (小時)",
                        "default": 24
                    }
                },
                "required": ["log_file"]
            }
        ),
        Tool(
            name="get_log_stats",
            description="獲取日誌統計資訊",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_file": {
                        "type": "string",
                        "description": "要統計的日誌檔案路徑"
                    },
                    "lines_to_analyze": {
                        "type": "integer",
                        "description": "要分析的行數",
                        "default": 1000
                    }
                },
                "required": ["log_file"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """執行日誌分析工具"""
    if name == "search_logs":
        log_file = arguments["log_file"]
        pattern = arguments["pattern"]
        max_results = arguments.get("max_results", 50)
        time_range_hours = arguments.get("time_range_hours", 24)
        
        if not os.path.exists(log_file):
            return [f"日誌檔案不存在: {log_file}"]
        
        try:
            # 計算時間範圍
            cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
            
            matches = []
            regex = re.compile(pattern, re.IGNORECASE)
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if len(matches) >= max_results:
                        break
                    
                    line = line.strip()
                    if regex.search(line):
                        # 嘗試解析時間戳記
                        log_time = parse_log_timestamp(line)
                        
                        if log_time is None or log_time >= cutoff_time:
                            matches.append({
                                "line_number": line_num,
                                "content": line,
                                "timestamp": log_time.isoformat() if log_time else None
                            })
            
            result = {
                "log_file": log_file,
                "pattern": pattern,
                "time_range_hours": time_range_hours,
                "matches_found": len(matches),
                "matches": matches
            }
            
            return [json.dumps(result, indent=2, ensure_ascii=False)]
            
        except Exception as e:
            return [f"搜尋失敗: {e}"]
    
    elif name == "analyze_error_trends":
        log_file = arguments["log_file"]
        time_window_hours = arguments.get("time_window_hours", 24)
        
        if not os.path.exists(log_file):
            return [f"日誌檔案不存在: {log_file}"]
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            
            # 錯誤關鍵字
            error_patterns = [
                r'\berror\b', r'\bfail\b', r'\bexception\b',
                r'\bcrash\b', r'\btimeout\b', r'\bdenied\b'
            ]
            
            hourly_counts = {}
            error_types = {}
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    log_time = parse_log_timestamp(line)
                    
                    if log_time and log_time >= cutoff_time:
                        hour_key = log_time.strftime("%Y-%m-%d %H:00")
                        
                        # 檢查是否包含錯誤
                        for pattern in error_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1
                                
                                # 統計錯誤類型
                                error_type = extract_error_type(line)
                                error_types[error_type] = error_types.get(error_type, 0) + 1
                                break
            
            result = {
                "log_file": log_file,
                "time_window_hours": time_window_hours,
                "total_errors": sum(hourly_counts.values()),
                "hourly_error_counts": hourly_counts,
                "error_types": error_types,
                "peak_hour": max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
            }
            
            return [json.dumps(result, indent=2, ensure_ascii=False)]
            
        except Exception as e:
            return [f"分析失敗: {e}"]
    
    elif name == "get_log_stats":
        log_file = arguments["log_file"]
        lines_to_analyze = arguments.get("lines_to_analyze", 1000)
        
        if not os.path.exists(log_file):
            return [f"日誌檔案不存在: {log_file}"]
        
        try:
            lines = read_tail_lines(log_file, lines_to_analyze)
            
            # 統計各種資訊
            log_levels = analyze_log_levels(lines)
            
            # 統計來源/服務
            sources = {}
            for line in lines:
                source = extract_source(line)
                if source:
                    sources[source] = sources.get(source, 0) + 1
            
            # 統計時間分佈
            hourly_distribution = {}
            for line in lines:
                log_time = parse_log_timestamp(line)
                if log_time:
                    hour = log_time.hour
                    hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            
            file_stat = os.stat(log_file)
            
            result = {
                "log_file": log_file,
                "file_size_bytes": file_stat.st_size,
                "file_size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                "lines_analyzed": len(lines),
                "log_levels": log_levels,
                "top_sources": dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]),
                "hourly_distribution": hourly_distribution,
                "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            }
            
            return [json.dumps(result, indent=2, ensure_ascii=False)]
            
        except Exception as e:
            return [f"統計失敗: {e}"]
    
    else:
        raise ValueError(f"未知的工具: {name}")

def read_tail_lines(file_path, num_lines):
    """讀取檔案最後幾行"""
    try:
        with open(file_path, 'rb') as f:
            # 移到檔案末尾
            f.seek(0, 2)
            file_size = f.tell()
            
            lines = []
            buffer_size = 8192
            position = file_size
            
            while len(lines) < num_lines and position > 0:
                # 計算讀取位置
                read_size = min(buffer_size, position)
                position -= read_size
                f.seek(position)
                
                # 讀取並分割行
                chunk = f.read(read_size).decode('utf-8', errors='ignore')
                chunk_lines = chunk.split('\n')
                
                # 合併第一行到之前的行
                if lines and chunk_lines:
                    lines[0] = chunk_lines[-1] + lines[0]
                    chunk_lines = chunk_lines[:-1]
                
                # 添加新行到開頭
                lines = chunk_lines + lines
            
            # 移除空行並返回指定數量
            lines = [line for line in lines if line.strip()]
            return lines[-num_lines:] if len(lines) > num_lines else lines
            
    except Exception:
        return []

def analyze_log_levels(lines):
    """分析日誌等級"""
    levels = {}
    for line in lines:
        level = extract_log_level(line)
        if level:
            levels[level] = levels.get(level, 0) + 1
    return levels

def extract_log_level(line):
    """從日誌行中提取日誌等級"""
    patterns = [
        r'\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b',
        r'\[(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\]'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None

def detect_errors_warnings(lines):
    """檢測錯誤和警告"""
    issues = []
    for line in lines:
        if re.search(r'\b(error|fail|exception|critical|fatal)\b', line, re.IGNORECASE):
            issues.append({
                "type": "error",
                "content": line
            })
        elif re.search(r'\b(warn|warning)\b', line, re.IGNORECASE):
            issues.append({
                "type": "warning", 
                "content": line
            })
    return issues[-20:]  # 返回最近20個問題

def parse_log_timestamp(line):
    """解析日誌時間戳記"""
    # 常見的時間戳記格式
    patterns = [
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',  # ISO format
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # Standard format
        r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})',      # Syslog format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            timestamp_str = match.group(1)
            try:
                if 'T' in timestamp_str:
                    return datetime.fromisoformat(timestamp_str.replace('T', ' '))
                elif len(timestamp_str) == 19:  # YYYY-MM-DD HH:MM:SS
                    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                else:  # Syslog format
                    current_year = datetime.now().year
                    return datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
            except:
                continue
    return None

def extract_source(line):
    """從日誌行中提取來源/服務名稱"""
    # 嘗試提取常見的服務名稱模式
    patterns = [
        r'\b(\w+)\[\d+\]:',  # service[pid]:
        r'\b(\w+):',         # service:
        r'\[(\w+)\]'         # [service]
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            return match.group(1)
    return "unknown"

def extract_error_type(line):
    """從錯誤行中提取錯誤類型"""
    if re.search(r'\btimeout\b', line, re.IGNORECASE):
        return "timeout"
    elif re.search(r'\bconnection\b', line, re.IGNORECASE):
        return "connection"
    elif re.search(r'\bpermission\b', line, re.IGNORECASE):
        return "permission"
    elif re.search(r'\bauthentication\b', line, re.IGNORECASE):
        return "authentication"
    elif re.search(r'\bfile|directory\b', line, re.IGNORECASE):
        return "filesystem"
    else:
        return "general"

if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(app)
