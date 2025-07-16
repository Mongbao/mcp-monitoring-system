#!/bin/bash

echo "=== VS Code SSH 記憶體問題排查 ==="
echo "時間: $(date)"
echo ""

echo "1. 系統記憶體狀況:"
free -h
echo ""

echo "2. 系統負載:"
uptime
echo ""

echo "3. 最耗記憶體的進程 (前10名):"
ps aux --sort=-%mem | head -11
echo ""

echo "4. VS Code 相關進程:"
ps aux | grep -E "(code|node|copilot|typescript)" | grep -v grep
echo ""

echo "5. SSH 連接狀況:"
ss -tnlp | grep :22
echo ""

echo "6. 系統磁碟使用:"
df -h | head -5
echo ""

echo "7. 記憶體詳細資訊:"
cat /proc/meminfo | head -10
echo ""

echo "8. 最近的系統錯誤 (OOM 相關):"
dmesg | grep -i "killed\|oom\|memory" | tail -5
echo ""

echo "=== 建議解決方案 ==="
echo "1. 如果記憶體使用率 > 80%，立即執行:"
echo "   sudo systemctl restart ssh"
echo "   pkill -f 'code-server'"
echo ""
echo "2. 優化 VS Code 設置:"
echo "   - 關閉不必要的擴展"
echo "   - 限制 Copilot 功能"
echo "   - 減少檔案監控範圍"
echo ""
echo "3. 系統級優化:"
echo "   bash /home/bao/mcp_use/scripts/optimize_vscode_ssh.sh"
echo ""
echo "4. 定期清理:"
echo "   python3 /home/bao/mcp_use/scripts/vscode_memory_monitor.py cleanup"
