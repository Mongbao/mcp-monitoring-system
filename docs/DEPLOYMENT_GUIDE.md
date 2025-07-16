# MCP 監控系統 Apache 部署指南

## 🎯 目標
在 Apache 上設定 MCP 監控系統，使其可以透過 `bao.mengwei710.com` 存取。

## 📋 已建立的檔案

### Apache 配置
- `bao-ssl.conf` - Apache SSL 虛擬主機配置
- `deploy_apache.sh` - 自動化部署腳本

### Web 服務
- `mcp_web_server.py` - MCP 監控系統 Web 伺服器
- `mcp-web.service` - systemd 服務配置

### 測試工具
- `test_setup.sh` - 系統設定測試腳本

## 🚀 部署步驟

### 1. 安裝 Python 套件
```bash
cd /home/bao/mcp_use
source mcp_env/bin/activate
pip install psutil
```

### 2. 執行部署腳本
```bash
sudo ./deploy_apache.sh
```

這個腳本會自動：
- 複製 Apache 配置到 `/etc/apache2/sites-available/`
- 啟用必要的 Apache 模組 (ssl, proxy, headers)
- 啟用 `bao-ssl` 站台
- 安裝並啟動 systemd 服務
- 重新載入 Apache

### 3. 驗證部署
```bash
./test_setup.sh
```

## 🌐 存取方式

### 本地測試
- Web 介面: http://localhost:8003
- API 端點: http://localhost:8003/api/system

### 正式環境 (需要 DNS 設定)
- Web 介面: https://bao.mengwei710.com
- API 端點: https://bao.mengwei710.com/api/system

## 📊 監控功能

### 儀表板功能
- 📊 系統資源監控 (CPU, 記憶體, 磁碟)
- ⚙️ 進程狀態統計
- 🌐 網路流量統計
- 📁 檔案系統狀態
- 📋 日誌摘要

### API 端點
- `/api/system` - 系統資源資訊
- `/api/processes` - 進程統計
- `/api/network` - 網路狀態
- `/api/filesystem` - 檔案系統資訊
- `/api/logs` - 日誌摘要

## 🔧 管理指令

### 服務管理
```bash
# 檢查 MCP Web 服務狀態
sudo systemctl status mcp-web

# 重新啟動 MCP Web 服務
sudo systemctl restart mcp-web

# 檢視 MCP Web 日誌
sudo journalctl -u mcp-web -f

# 停止 MCP Web 服務
sudo systemctl stop mcp-web
```

### Apache 管理
```bash
# 檢查 Apache 狀態
sudo systemctl status apache2

# 重新載入 Apache 配置
sudo systemctl reload apache2

# 檢查 Apache 配置語法
sudo apache2ctl configtest

# 檢視 Apache 錯誤日誌
sudo tail -f /var/log/apache2/bao_error.log
```

### 站台管理
```bash
# 檢查已啟用的站台
sudo a2ensite

# 停用站台
sudo a2dissite bao-ssl

# 重新啟用站台
sudo a2ensite bao-ssl
```

## 🛠️ 故障排除

### 常見問題

#### 1. Web 服務無法啟動
```bash
# 檢查日誌
sudo journalctl -u mcp-web -n 50

# 檢查埠是否被佔用
sudo netstat -tlnp | grep :8003

# 手動測試 Web 服務
cd /home/bao/mcp_use
source mcp_env/bin/activate
python mcp_web_server.py
```

#### 2. Apache 配置錯誤
```bash
# 檢查配置語法
sudo apache2ctl configtest

# 檢查 SSL 憑證
sudo openssl x509 -in /etc/ssl/certs/mengwei710.com.pem -text -noout

# 檢查權限
ls -la /etc/apache2/sites-available/bao-ssl.conf
```

#### 3. 權限問題
```bash
# 確保檔案權限正確
sudo chown -R bao:bao /home/bao/mcp_use
chmod +x /home/bao/mcp_use/mcp_web_server.py
```

#### 4. Python 套件問題
```bash
# 重新安裝套件
cd /home/bao/mcp_use
source mcp_env/bin/activate
pip install --upgrade psutil
```

### 日誌位置
- MCP Web 服務: `sudo journalctl -u mcp-web`
- Apache 錯誤: `/var/log/apache2/bao_error.log`
- Apache 存取: `/var/log/apache2/bao_access.log`

## 🔒 安全注意事項

1. **SSL 憑證**: 確保 SSL 憑證有效且未過期
2. **防火牆**: 確保埠 443 和 8003 已開放
3. **權限**: Web 服務以 `bao` 使用者執行，避免權限過高
4. **存取控制**: 可在 Apache 配置中加入 IP 限制

## 📈 監控和維護

### 自動化監控
系統會自動：
- 每 30 秒重新整理儀表板資料
- 在服務失敗時自動重新啟動 (systemd 配置)
- 記錄所有存取和錯誤日誌

### 定期維護
建議定期：
1. 檢查磁碟空間
2. 清理舊日誌檔案
3. 更新 SSL 憑證
4. 檢查系統更新

部署完成後，您就可以透過瀏覽器存取完整的 MCP 監控系統儀表板了！
