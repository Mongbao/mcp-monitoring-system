// 在瀏覽器控制台中執行此腳本來測試功能
console.log('開始測試 MCP 功能...');

// 測試 API 端點
async function testAPIs() {
    console.log('測試 API 端點...');
    
    try {
        const healthResponse = await fetch('/api/health');
        const healthData = await healthResponse.json();
        console.log('健康度 API 成功:', healthData);
        
        const alertsResponse = await fetch('/api/alerts');
        const alertsData = await alertsResponse.json();
        console.log('警報 API 成功:', alertsData);
    } catch (error) {
        console.error('API 測試失敗:', error);
    }
}

// 手動更新健康度
async function manualUpdateHealth() {
    console.log('手動更新健康度...');
    
    const container = document.getElementById('health-info');
    if (!container) {
        console.error('找不到 health-info 元素');
        return;
    }
    
    container.className = ''; // 移除loading class
    
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        console.log('健康度數據:', data);
        
        if (data.error) {
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #6c757d;">
                    <div style="font-size: 16px; margin-bottom: 10px;">⏳</div>
                    <div>健康度評分功能準備中...</div>
                    <small style="opacity: 0.7;">增強功能可能需要額外啟動時間</small>
                </div>
            `;
            return;
        }
        
        const overallScore = data.overall || 0;
        let healthText = '危險';
        
        if (overallScore >= 80) {
            healthText = '優秀';
        } else if (overallScore >= 60) {
            healthText = '良好';
        } else if (overallScore >= 40) {
            healthText = '警告';
        }
        
        container.innerHTML = `
            <div style="display: flex; align-items: center; gap: 20px; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 12px;">
                <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #3498db, #5dade2); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px;">
                    ${overallScore.toFixed(0)}
                </div>
                <div style="flex: 1;">
                    <div style="font-size: 1.2rem; font-weight: 700; color: #2c3e50; margin-bottom: 10px;">🎯 整體健康度: ${healthText}</div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding: 4px 8px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <span style="color: #495057;">🔥 CPU 評分:</span>
                        <span style="color: #2c3e50; font-weight: 700;">${data.cpu?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding: 4px 8px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <span style="color: #495057;">🧠 記憶體評分:</span>
                        <span style="color: #2c3e50; font-weight: 700;">${data.memory?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding: 4px 8px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <span style="color: #495057;">💾 磁碟評分:</span>
                        <span style="color: #2c3e50; font-weight: 700;">${data.disk?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 8px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <span style="color: #495057;">⚡ 進程評分:</span>
                        <span style="color: #2c3e50; font-weight: 700;">${data.process?.toFixed(1) || 'N/A'}</span>
                    </div>
                </div>
            </div>
        `;
        
        console.log('健康度更新成功');
    } catch (error) {
        console.error('健康度更新失敗:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #e74c3c;">
                <div style="font-size: 16px; margin-bottom: 10px;">⚠️</div>
                <div>健康度評分暫時無法使用</div>
                <small style="opacity: 0.7;">錯誤: ${error.message}</small>
            </div>
        `;
    }
}

// 手動更新警報
async function manualUpdateAlerts() {
    console.log('手動更新警報...');
    
    const container = document.getElementById('alerts-info');
    if (!container) {
        console.error('找不到 alerts-info 元素');
        return;
    }
    
    container.className = ''; // 移除loading class
    
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        
        console.log('警報數據:', data);
        
        if (data.error) {
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #6c757d;">
                    <div style="font-size: 16px; margin-bottom: 10px;">⏳</div>
                    <div>警報系統準備中...</div>
                    <small style="opacity: 0.7;">增強功能可能需要額外啟動時間</small>
                </div>
            `;
            return;
        }
        
        const currentAlerts = data.current_alerts || [];
        const alertCount = data.alert_count || 0;
        
        if (alertCount === 0) {
            container.innerHTML = `
                <div style="color: #27ae60; text-align: center; padding: 20px; background: rgba(39, 174, 96, 0.1); border-radius: 12px; border: 1px solid rgba(39, 174, 96, 0.3);">
                    <div style="font-size: 18px; margin-bottom: 8px;">✅</div>
                    <div style="font-weight: 600;">系統運行正常</div>
                    <small style="opacity: 0.8;">無活躍警報</small>
                </div>
            `;
            console.log('警報更新成功 - 無活躍警報');
            return;
        }
        
        let alertsHtml = `<div style="margin-bottom: 10px; font-weight: 600; color: #e74c3c;">活躍警報 (${alertCount})</div>`;
        
        currentAlerts.forEach(alert => {
            const alertColor = alert.severity === 'critical' ? '#e74c3c' : '#f39c12';
            const timestamp = new Date(alert.timestamp).toLocaleTimeString();
            
            alertsHtml += `
                <div style="margin-bottom: 8px; padding: 12px; border-left: 4px solid ${alertColor}; background: rgba(255,255,255,0.1); border-radius: 8px;">
                    <div style="font-weight: 600; color: ${alertColor};">${alert.title}</div>
                    <div style="margin: 4px 0; color: #2c3e50;">${alert.description}</div>
                    <div style="font-size: 12px; opacity: 0.8; color: #6c757d;">${timestamp}</div>
                </div>
            `;
        });
        
        container.innerHTML = alertsHtml;
        console.log('警報更新成功');
    } catch (error) {
        console.error('警報更新失敗:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #e74c3c;">
                <div style="font-size: 16px; margin-bottom: 10px;">⚠️</div>
                <div>警報系統暫時無法使用</div>
                <small style="opacity: 0.7;">錯誤: ${error.message}</small>
            </div>
        `;
    }
}

// 運行所有測試
async function runAllTests() {
    console.log('=== 開始完整測試 ===');
    
    await testAPIs();
    await manualUpdateHealth();
    await manualUpdateAlerts();
    
    console.log('=== 測試完成 ===');
}

// 執行測試
runAllTests();

// 提供手動函數
window.manualUpdateHealth = manualUpdateHealth;
window.manualUpdateAlerts = manualUpdateAlerts;
window.testAPIs = testAPIs;

console.log('測試腳本已載入，可以在控制台中調用:');
console.log('- manualUpdateHealth() - 手動更新健康度');
console.log('- manualUpdateAlerts() - 手動更新警報');
console.log('- testAPIs() - 測試 API 端點');