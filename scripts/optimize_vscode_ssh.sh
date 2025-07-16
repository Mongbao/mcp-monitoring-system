#!/bin/bash
"""
SSH 和 VS Code 記憶體優化配置腳本
"""

echo "=== VS Code SSH 記憶體優化配置 ==="

# 1. 優化 SSH 配置
echo "1. 優化 SSH 服務配置..."
sudo bash -c 'cat >> /etc/ssh/sshd_config << EOF

# VS Code 記憶體優化配置
ClientAliveInterval 60
ClientAliveCountMax 3
MaxSessions 10
MaxStartups 5:30:10
LoginGraceTime 60
TCPKeepAlive yes
EOF'

# 2. 設置系統記憶體限制
echo "2. 配置系統記憶體限制..."
sudo bash -c 'cat >> /etc/security/limits.conf << EOF

# VS Code 記憶體限制
* soft memlock 4194304
* hard memlock 4194304
* soft as 8388608
* hard as 8388608
EOF'

# 3. 優化系統 swappiness
echo "3. 優化系統記憶體管理..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
echo 'vm.dirty_ratio=15' | sudo tee -a /etc/sysctl.conf
echo 'vm.dirty_background_ratio=5' | sudo tee -a /etc/sysctl.conf

# 4. 創建 VS Code Server 清理服務
echo "4. 創建 VS Code 記憶體監控服務..."
sudo tee /etc/systemd/system/vscode-memory-monitor.service > /dev/null << EOF
[Unit]
Description=VS Code Memory Monitor
After=network.target

[Service]
Type=simple
User=bao
ExecStart=/usr/bin/python3 /home/bao/mcp_use/scripts/vscode_memory_monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 5. 創建定時清理 cron 任務
echo "5. 設置定時清理任務..."
(crontab -l 2>/dev/null; echo "*/30 * * * * /usr/bin/python3 /home/bao/mcp_use/scripts/vscode_memory_monitor.py cleanup >> /home/bao/mcp_use/logs/vscode_cleanup.log 2>&1") | crontab -

# 6. 創建記憶體監控腳本
echo "6. 創建快速檢查腳本..."
cat > /home/bao/mcp_use/scripts/check_memory.sh << 'EOF'
#!/bin/bash
echo "=== 系統記憶體狀況 ==="
free -h
echo ""
echo "=== VS Code 相關進程 ==="
ps aux | grep -E "(code|node|copilot|typescript)" | grep -v grep | sort -k4 -nr
echo ""
echo "=== 記憶體使用前10 ==="
ps aux --sort=-%mem | head -11
EOF

chmod +x /home/bao/mcp_use/scripts/check_memory.sh
chmod +x /home/bao/mcp_use/scripts/vscode_memory_monitor.py

# 7. 重啟服務以應用配置
echo "7. 重啟相關服務..."
sudo systemctl restart ssh
sudo sysctl -p
sudo systemctl enable vscode-memory-monitor.service
sudo systemctl start vscode-memory-monitor.service

echo ""
echo "=== 配置完成！==="
echo "記憶體監控服務已啟動，每30分鐘自動清理一次"
echo "使用以下命令監控："
echo "  /home/bao/mcp_use/scripts/check_memory.sh"
echo "  python3 /home/bao/mcp_use/scripts/vscode_memory_monitor.py status"
echo "  sudo systemctl status vscode-memory-monitor"
