#!/usr/bin/env python3
"""
檔案系統監控 MCP Server
提供檔案系統監控功能 (檔案變更、權限、目錄大小等)
"""

import asyncio
import json
import os
import stat
import time
from datetime import datetime
from pathlib import Path
from mcp.server import Server
from mcp.types import Resource, Tool
from typing import Any, Dict, List

app = Server("filesystem-monitor")

# 從環境變數取得監控路徑
WATCH_PATHS = os.environ.get("WATCH_PATHS", "/home,/var/log").split(",")

@app.list_resources()
async def list_resources() -> List[Resource]:
    """列出可用的檔案系統監控資源"""
    resources = []
    for path in WATCH_PATHS:
        if os.path.exists(path):
            resources.append(Resource(
                uri=f"filesystem://{path}",
                name=f"檔案系統監控 - {path}",
                mimeType="application/json",
                description=f"監控 {path} 目錄的檔案系統狀態"
            ))
    return resources

@app.read_resource()
async def read_resource(uri: str) -> str:
    """讀取檔案系統監控資源"""
    if not uri.startswith("filesystem://"):
        raise ValueError(f"不支援的 URI: {uri}")
    
    path = uri[13:]  # 移除 "filesystem://" 前綴
    
    if not os.path.exists(path):
        raise ValueError(f"路徑不存在: {path}")
    
    try:
        # 獲取基本資訊
        stat_info = os.stat(path)
        
        info = {
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "exists": True,
            "is_file": os.path.isfile(path),
            "is_dir": os.path.isdir(path),
            "size": stat_info.st_size,
            "mode": oct(stat_info.st_mode),
            "uid": stat_info.st_uid,
            "gid": stat_info.st_gid,
            "atime": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            "mtime": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "ctime": datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        }
        
        # 如果是目錄，獲取子項目數量和總大小
        if os.path.isdir(path):
            try:
                items = list(os.listdir(path))
                info["item_count"] = len(items)
                
                total_size = 0
                for item in items[:100]:  # 限制前100個項目避免太慢
                    item_path = os.path.join(path, item)
                    if os.path.exists(item_path):
                        try:
                            total_size += os.path.getsize(item_path)
                        except (OSError, PermissionError):
                            continue
                info["total_size_sample"] = total_size
            except PermissionError:
                info["permission_error"] = True
        
        return json.dumps(info, indent=2, ensure_ascii=False)
        
    except (OSError, PermissionError) as e:
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "error": str(e),
            "exists": False
        }
        return json.dumps(error_info, indent=2, ensure_ascii=False)

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用的檔案系統監控工具"""
    return [
        Tool(
            name="scan_directory",
            description="掃描目錄內容和大小",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "要掃描的目錄路徑"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "最大掃描深度",
                        "default": 2
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="check_permissions",
            description="檢查檔案或目錄權限",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "要檢查的檔案或目錄路徑"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="find_large_files",
            description="尋找大型檔案",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "搜尋目錄路徑"
                    },
                    "min_size_mb": {
                        "type": "number",
                        "description": "最小檔案大小 (MB)",
                        "default": 100
                    }
                },
                "required": ["path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """執行檔案系統監控工具"""
    if name == "scan_directory":
        path = arguments["path"]
        max_depth = arguments.get("max_depth", 2)
        
        if not os.path.exists(path) or not os.path.isdir(path):
            return [f"目錄不存在或不是目錄: {path}"]
        
        def scan_dir(dir_path, current_depth=0):
            if current_depth > max_depth:
                return {}
            
            try:
                items = []
                total_size = 0
                
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    try:
                        stat_info = os.stat(item_path)
                        item_info = {
                            "name": item,
                            "path": item_path,
                            "is_dir": os.path.isdir(item_path),
                            "size": stat_info.st_size,
                            "mtime": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                        }
                        
                        if os.path.isdir(item_path) and current_depth < max_depth:
                            subdir_info = scan_dir(item_path, current_depth + 1)
                            item_info["subdirectory"] = subdir_info
                        
                        items.append(item_info)
                        total_size += stat_info.st_size
                    except (OSError, PermissionError):
                        continue
                
                return {
                    "items": items,
                    "total_size": total_size,
                    "item_count": len(items)
                }
            except PermissionError:
                return {"error": "權限不足"}
        
        result = scan_dir(path)
        return [json.dumps(result, indent=2, ensure_ascii=False)]
    
    elif name == "check_permissions":
        path = arguments["path"]
        
        if not os.path.exists(path):
            return [f"路徑不存在: {path}"]
        
        try:
            stat_info = os.stat(path)
            mode = stat_info.st_mode
            
            permissions = {
                "path": path,
                "mode": oct(mode),
                "owner": {
                    "read": bool(mode & stat.S_IRUSR),
                    "write": bool(mode & stat.S_IWUSR),
                    "execute": bool(mode & stat.S_IXUSR)
                },
                "group": {
                    "read": bool(mode & stat.S_IRGRP),
                    "write": bool(mode & stat.S_IWGRP),
                    "execute": bool(mode & stat.S_IXGRP)
                },
                "others": {
                    "read": bool(mode & stat.S_IROTH),
                    "write": bool(mode & stat.S_IWOTH),
                    "execute": bool(mode & stat.S_IXOTH)
                },
                "uid": stat_info.st_uid,
                "gid": stat_info.st_gid
            }
            
            return [json.dumps(permissions, indent=2, ensure_ascii=False)]
        except (OSError, PermissionError) as e:
            return [f"無法檢查權限: {e}"]
    
    elif name == "find_large_files":
        path = arguments["path"]
        min_size_mb = arguments.get("min_size_mb", 100)
        min_size_bytes = min_size_mb * 1024 * 1024
        
        if not os.path.exists(path):
            return [f"路徑不存在: {path}"]
        
        large_files = []
        
        def find_files(dir_path):
            try:
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            if size >= min_size_bytes:
                                stat_info = os.stat(file_path)
                                large_files.append({
                                    "path": file_path,
                                    "size_bytes": size,
                                    "size_mb": round(size / (1024 * 1024), 2),
                                    "mtime": datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                                })
                        except (OSError, PermissionError):
                            continue
                    
                    # 限制結果數量
                    if len(large_files) >= 50:
                        break
            except (OSError, PermissionError):
                pass
        
        find_files(path)
        large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        
        result = {
            "search_path": path,
            "min_size_mb": min_size_mb,
            "found_count": len(large_files),
            "files": large_files
        }
        
        return [json.dumps(result, indent=2, ensure_ascii=False)]
    
    else:
        raise ValueError(f"未知的工具: {name}")

if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(app)
