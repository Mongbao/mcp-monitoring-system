#!/bin/bash
echo "=== 系統記憶體狀況 ==="
free -h
echo ""
echo "=== VS Code 相關進程 ==="
ps aux | grep -E "(code|node|copilot|typescript)" | grep -v grep | sort -k4 -nr
echo ""
echo "=== 記憶體使用前10 ==="
ps aux --sort=-%mem | head -11
