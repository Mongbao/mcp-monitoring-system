"""
歷史數據收集器
負責定期收集系統指標並存儲到時間序列數據庫
"""
import json
import logging
import asyncio
import psutil
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import statistics

from app.api.models.metrics import MetricData, TrendAnalysis, PerformanceBaseline, AnomalyDetection

logger = logging.getLogger(__name__)


class MetricsCollector:
    """指標收集器"""
    
    def __init__(self, data_dir: str = "/home/bao/mcp_use/data"):
        self.data_dir = Path(data_dir)
        self.metrics_file = self.data_dir / "historical_metrics.json"
        self.baselines_file = self.data_dir / "performance_baselines.json"
        self.anomalies_file = self.data_dir / "anomalies.json"
        
        # 內存存儲（生產環境中應使用時間序列數據庫如 InfluxDB）
        self.metrics_data: List[MetricData] = []
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.anomalies: List[AnomalyDetection] = []
        
        # 確保數據目錄存在
        self.data_dir.mkdir(exist_ok=True)
        
        # 載入現有數據
        self._load_historical_data()
        self._load_baselines()
        self._load_anomalies()
        
        # 數據保留策略（預設保留30天的數據）
        self.retention_days = 30
        
        # 基線更新間隔（小時）
        self.baseline_update_interval = 24
    
    def _load_historical_data(self):
        """載入歷史數據"""
        try:
            # 確保必要屬性存在（向後兼容）
            if not hasattr(self, 'retention_days'):
                self.retention_days = 30
            if not hasattr(self, 'baseline_update_interval'):
                self.baseline_update_interval = 24
            
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        # 轉換時間戳
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                        self.metrics_data.append(MetricData(**item))
                
                # 清理過期數據
                self._cleanup_old_data()
                
                logger.info(f"載入了 {len(self.metrics_data)} 個歷史數據點")
        except Exception as e:
            logger.error(f"載入歷史數據失敗: {e}")
    
    def _save_historical_data(self):
        """保存歷史數據"""
        try:
            # 只保存最近的數據
            recent_data = self._get_recent_data(hours=24 * self.retention_days)
            
            data_to_save = []
            for metric in recent_data:
                metric_dict = metric.dict()
                metric_dict['timestamp'] = metric_dict['timestamp'].isoformat()
                data_to_save.append(metric_dict)
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存歷史數據失敗: {e}")
    
    def _load_baselines(self):
        """載入性能基線"""
        try:
            if self.baselines_file.exists():
                with open(self.baselines_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for metric_name, baseline_dict in data.items():
                        baseline_dict['last_updated'] = datetime.fromisoformat(baseline_dict['last_updated'])
                        self.baselines[metric_name] = PerformanceBaseline(**baseline_dict)
        except Exception as e:
            logger.error(f"載入性能基線失敗: {e}")
    
    def _save_baselines(self):
        """保存性能基線"""
        try:
            data_to_save = {}
            for metric_name, baseline in self.baselines.items():
                baseline_dict = baseline.dict()
                baseline_dict['last_updated'] = baseline_dict['last_updated'].isoformat()
                data_to_save[metric_name] = baseline_dict
            
            with open(self.baselines_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存性能基線失敗: {e}")
    
    def _load_anomalies(self):
        """載入異常記錄"""
        try:
            if self.anomalies_file.exists():
                with open(self.anomalies_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                        self.anomalies.append(AnomalyDetection(**item))
                
                # 只保留最近的異常記錄
                cutoff_time = datetime.now() - timedelta(days=7)
                self.anomalies = [a for a in self.anomalies if a.timestamp >= cutoff_time]
        except Exception as e:
            logger.error(f"載入異常記錄失敗: {e}")
    
    def _save_anomalies(self):
        """保存異常記錄"""
        try:
            data_to_save = []
            for anomaly in self.anomalies:
                anomaly_dict = anomaly.dict()
                anomaly_dict['timestamp'] = anomaly_dict['timestamp'].isoformat()
                data_to_save.append(anomaly_dict)
            
            with open(self.anomalies_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存異常記錄失敗: {e}")
    
    async def collect_metrics(self):
        """收集當前系統指標"""
        try:
            current_time = datetime.now()
            
            # 收集系統指標
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 網路統計
            net_io = psutil.net_io_counters()
            
            # 進程統計
            processes = list(psutil.process_iter(['pid', 'status']))
            process_count = len(processes)
            running_processes = len([p for p in processes if p.info['status'] == psutil.STATUS_RUNNING])
            zombie_processes = len([p for p in processes if p.info['status'] == psutil.STATUS_ZOMBIE])
            
            # 系統負載
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()
                load_avg_1min, load_avg_5min, load_avg_15min = load_avg
            else:
                load_avg_1min = load_avg_5min = load_avg_15min = 0.0
            
            # 創建指標數據點
            metric_data = MetricData(
                timestamp=current_time,
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=(disk.used / disk.total) * 100,
                load_avg_1min=load_avg_1min,
                load_avg_5min=load_avg_5min,
                load_avg_15min=load_avg_15min,
                network_bytes_sent=net_io.bytes_sent,
                network_bytes_recv=net_io.bytes_recv,
                process_count=process_count,
                running_processes=running_processes,
                zombie_processes=zombie_processes
            )
            
            # 添加到內存存儲
            self.metrics_data.append(metric_data)
            
            # 異常檢測
            await self._detect_anomalies(metric_data)
            
            # 定期保存數據
            if len(self.metrics_data) % 10 == 0:  # 每10個數據點保存一次
                self._save_historical_data()
            
            # 定期更新基線
            if self._should_update_baselines():
                await self._update_baselines()
            
            logger.debug(f"收集指標完成: CPU {cpu_percent:.1f}%, MEM {memory.percent:.1f}%, DISK {(disk.used/disk.total)*100:.1f}%")
            
        except Exception as e:
            logger.error(f"收集系統指標失敗: {e}")
    
    def _cleanup_old_data(self):
        """清理過期數據"""
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        original_count = len(self.metrics_data)
        self.metrics_data = [m for m in self.metrics_data if m.timestamp >= cutoff_time]
        cleaned_count = original_count - len(self.metrics_data)
        
        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 個過期數據點")
    
    def _get_recent_data(self, hours: int = 24) -> List[MetricData]:
        """獲取最近指定小時數的數據"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_data if m.timestamp >= cutoff_time]
    
    def get_historical_data(self, hours: int = 24, metrics: Optional[List[str]] = None) -> List[Dict]:
        """獲取歷史數據"""
        recent_data = self._get_recent_data(hours)
        
        if not recent_data:
            return []
        
        result = []
        for metric_data in recent_data:
            data_dict = metric_data.dict()
            data_dict['timestamp'] = data_dict['timestamp'].isoformat()
            
            # 如果指定了特定指標，只返回這些指標
            if metrics:
                filtered_dict = {'timestamp': data_dict['timestamp']}
                for metric in metrics:
                    if metric in data_dict:
                        filtered_dict[metric] = data_dict[metric]
                result.append(filtered_dict)
            else:
                result.append(data_dict)
        
        return result
    
    def get_trend_analysis(self, hours: int = 24) -> List[TrendAnalysis]:
        """獲取趨勢分析"""
        recent_data = self._get_recent_data(hours)
        
        if len(recent_data) < 2:
            return []
        
        # 需要分析的指標
        metrics_to_analyze = [
            'cpu_percent', 'memory_percent', 'disk_percent',
            'load_avg_1min', 'process_count'
        ]
        
        trends = []
        
        for metric_name in metrics_to_analyze:
            values = [getattr(data, metric_name) for data in recent_data]
            
            if not values:
                continue
            
            # 計算統計數據
            avg_value = statistics.mean(values)
            min_value = min(values)
            max_value = max(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            
            # 計算趨勢方向
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            if len(first_half) > 0 and len(second_half) > 0:
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                trend_percentage = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
                
                if abs(trend_percentage) < 5:
                    trend_direction = "穩定"
                elif trend_percentage > 0:
                    trend_direction = "上升"
                else:
                    trend_direction = "下降"
            else:
                trend_direction = "穩定"
                trend_percentage = 0
            
            # 簡單的線性預測
            if len(values) >= 3:
                # 使用最後幾個值進行線性回歸預測
                recent_values = values[-5:]  # 使用最後5個值
                time_points = list(range(len(recent_values)))
                
                # 簡單線性回歸
                n = len(recent_values)
                sum_x = sum(time_points)
                sum_y = sum(recent_values)
                sum_xy = sum(x * y for x, y in zip(time_points, recent_values))
                sum_x2 = sum(x * x for x in time_points)
                
                if n * sum_x2 - sum_x * sum_x != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    intercept = (sum_y - slope * sum_x) / n
                    prediction = slope * n + intercept  # 預測下一個時間點
                else:
                    prediction = avg_value
            else:
                prediction = avg_value
            
            trend = TrendAnalysis(
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_percentage=trend_percentage,
                average_value=avg_value,
                min_value=min_value,
                max_value=max_value,
                standard_deviation=std_dev,
                prediction_next_hour=prediction
            )
            
            trends.append(trend)
        
        return trends
    
    async def _detect_anomalies(self, metric_data: MetricData):
        """檢測異常"""
        metrics_to_check = {
            'cpu_percent': metric_data.cpu_percent,
            'memory_percent': metric_data.memory_percent,
            'disk_percent': metric_data.disk_percent,
            'load_avg_1min': metric_data.load_avg_1min
        }
        
        for metric_name, current_value in metrics_to_check.items():
            if metric_name in self.baselines:
                baseline = self.baselines[metric_name]
                
                # 計算異常分數
                deviation = abs(current_value - baseline.baseline_average)
                anomaly_score = deviation / (baseline.baseline_std + 1e-6)  # 避免除零
                
                # 判定是否為異常
                is_anomaly = (current_value > baseline.upper_threshold or 
                            current_value < baseline.lower_threshold)
                
                if is_anomaly:
                    # 確定嚴重程度
                    if anomaly_score > 3:
                        severity = "high"
                    elif anomaly_score > 2:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    # 生成描述
                    direction = "過高" if current_value > baseline.baseline_average else "過低"
                    description = f"{metric_name} 數值 {direction}: {current_value:.2f} (基線: {baseline.baseline_average:.2f})"
                    
                    anomaly = AnomalyDetection(
                        timestamp=metric_data.timestamp,
                        metric_name=metric_name,
                        actual_value=current_value,
                        expected_value=baseline.baseline_average,
                        anomaly_score=min(anomaly_score, 1.0),  # 限制在 0-1 範圍
                        is_anomaly=is_anomaly,
                        severity=severity,
                        description=description
                    )
                    
                    self.anomalies.append(anomaly)
                    logger.warning(f"檢測到異常: {description}")
    
    def _should_update_baselines(self) -> bool:
        """判斷是否應該更新基線"""
        if not self.baselines:
            return True
        
        # 檢查最後更新時間
        now = datetime.now()
        for baseline in self.baselines.values():
            if (now - baseline.last_updated).total_seconds() / 3600 >= self.baseline_update_interval:
                return True
        
        return False
    
    async def _update_baselines(self):
        """更新性能基線"""
        # 使用過去7天的數據建立基線
        baseline_data = self._get_recent_data(hours=24 * 7)
        
        if len(baseline_data) < 24:  # 至少需要24個數據點
            logger.info("數據點不足，跳過基線更新")
            return
        
        metrics_to_baseline = [
            'cpu_percent', 'memory_percent', 'disk_percent', 'load_avg_1min'
        ]
        
        now = datetime.now()
        
        for metric_name in metrics_to_baseline:
            values = [getattr(data, metric_name) for data in baseline_data]
            
            if not values:
                continue
            
            # 計算基線統計
            avg_value = statistics.mean(values)
            std_value = statistics.stdev(values) if len(values) > 1 else 0
            
            # 設定閾值（基於正態分佈的 95% 信心區間）
            upper_threshold = avg_value + 2 * std_value
            lower_threshold = max(0, avg_value - 2 * std_value)  # 不能為負數
            
            baseline = PerformanceBaseline(
                metric_name=metric_name,
                baseline_average=avg_value,
                baseline_std=std_value,
                upper_threshold=upper_threshold,
                lower_threshold=lower_threshold,
                confidence_level=0.95,
                sample_count=len(values),
                last_updated=now
            )
            
            self.baselines[metric_name] = baseline
            logger.info(f"更新基線 {metric_name}: 平均={avg_value:.2f}, 標準差={std_value:.2f}")
        
        self._save_baselines()
    
    def get_anomalies(self, hours: int = 24) -> List[AnomalyDetection]:
        """獲取最近的異常記錄"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.anomalies if a.timestamp >= cutoff_time]
    
    def get_baselines(self) -> Dict[str, PerformanceBaseline]:
        """獲取當前的性能基線"""
        return self.baselines.copy()


# 全局指標收集器實例
metrics_collector = MetricsCollector()