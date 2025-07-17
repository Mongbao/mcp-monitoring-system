"""
資源依賴關係分析器
分析系統資源之間的相互依賴關係和影響
"""
import psutil
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import logging
from pathlib import Path

# 動態添加項目根目錄到 Python 路徑
import sys
current_path = Path(__file__).parent
project_root = current_path
while project_root.parent != project_root:
    if (project_root / "app").exists():
        break
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

from app.api.models.dependencies import (
    ResourceDependency, ResourceImpactAnalysis, ResourceBottleneck,
    SystemHealthIndex, ResourceOptimization, ProcessDependencyMap
)

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """資源依賴分析器"""
    
    def __init__(self):
        self.resource_history = defaultdict(list)
        self.correlation_cache = {}
        self.last_analysis_time = None
        
    def analyze_resource_dependencies(self, metrics_data: List[Dict]) -> List[ResourceDependency]:
        """分析資源依賴關係"""
        if len(metrics_data) < 10:  # 需要足夠的數據點
            return []
        
        dependencies = []
        
        # 主要資源指標
        resource_metrics = {
            'cpu_percent': [d.get('cpu_percent', 0) for d in metrics_data],
            'memory_percent': [d.get('memory_percent', 0) for d in metrics_data],
            'disk_percent': [d.get('disk_percent', 0) for d in metrics_data],
            'load_avg_1min': [d.get('load_avg_1min', 0) for d in metrics_data],
            'process_count': [d.get('process_count', 0) for d in metrics_data]
        }
        
        # 計算相關性矩陣
        correlations = self._calculate_correlations(resource_metrics)
        
        # 分析依賴關係
        for resource1, resource2, correlation in correlations:
            if abs(correlation) > 0.6:  # 強相關性閾值
                dependency_strength = abs(correlation)
                
                # 判斷依賴方向
                if correlation > 0:
                    description = f"{resource1} 與 {resource2} 呈正相關，當 {resource1} 增加時，{resource2} 也傾向增加"
                else:
                    description = f"{resource1} 與 {resource2} 呈負相關，當 {resource1} 增加時，{resource2} 傾向減少"
                
                dependency = ResourceDependency(
                    resource_name=resource1,
                    dependent_resources=[resource2],
                    dependency_strength=dependency_strength,
                    correlation_coefficient=correlation,
                    description=description
                )
                dependencies.append(dependency)
        
        return dependencies
    
    def _calculate_correlations(self, resource_metrics: Dict[str, List[float]]) -> List[Tuple[str, str, float]]:
        """計算資源間的相關性"""
        correlations = []
        resource_names = list(resource_metrics.keys())
        
        for i, resource1 in enumerate(resource_names):
            for j, resource2 in enumerate(resource_names[i+1:], i+1):
                try:
                    values1 = resource_metrics[resource1]
                    values2 = resource_metrics[resource2]
                    
                    if len(values1) == len(values2) and len(values1) > 1:
                        correlation = np.corrcoef(values1, values2)[0, 1]
                        if not np.isnan(correlation):
                            correlations.append((resource1, resource2, correlation))
                except Exception as e:
                    logger.warning(f"計算相關性失敗 {resource1}-{resource2}: {e}")
        
        return correlations
    
    def analyze_resource_impact(self, current_metrics: Dict[str, float]) -> List[ResourceImpactAnalysis]:
        """分析資源影響"""
        impacts = []
        
        # CPU 影響分析
        cpu_impact = self._analyze_cpu_impact(current_metrics)
        if cpu_impact:
            impacts.append(cpu_impact)
        
        # 記憶體影響分析
        memory_impact = self._analyze_memory_impact(current_metrics)
        if memory_impact:
            impacts.append(memory_impact)
        
        # 磁碟影響分析
        disk_impact = self._analyze_disk_impact(current_metrics)
        if disk_impact:
            impacts.append(disk_impact)
        
        return impacts
    
    def _analyze_cpu_impact(self, metrics: Dict[str, float]) -> Optional[ResourceImpactAnalysis]:
        """分析 CPU 影響"""
        cpu_percent = metrics.get('cpu_percent', 0)
        
        if cpu_percent < 70:
            return None
        
        # 計算影響分數
        impact_score = min(10, (cpu_percent / 10))
        
        # 確定風險等級
        if cpu_percent > 90:
            risk_level = "critical"
        elif cpu_percent > 80:
            risk_level = "high"
        else:
            risk_level = "medium"
        
        # 受影響的資源
        affected_resources = ["memory_usage", "disk_io", "network_performance"]
        
        # 連鎖效應
        cascade_effects = [
            "系統響應時間延遲",
            "進程排程延遲",
            "I/O 操作變慢"
        ]
        
        # 緩解建議
        mitigation_suggestions = [
            "檢查高 CPU 使用率的進程",
            "考慮進程優化或負載平衡",
            "評估是否需要硬體升級"
        ]
        
        return ResourceImpactAnalysis(
            resource_name="cpu_percent",
            impact_score=impact_score,
            affected_resources=affected_resources,
            cascade_effects=cascade_effects,
            risk_level=risk_level,
            mitigation_suggestions=mitigation_suggestions
        )
    
    def _analyze_memory_impact(self, metrics: Dict[str, float]) -> Optional[ResourceImpactAnalysis]:
        """分析記憶體影響"""
        memory_percent = metrics.get('memory_percent', 0)
        
        if memory_percent < 75:
            return None
        
        impact_score = min(10, (memory_percent / 10))
        
        if memory_percent > 95:
            risk_level = "critical"
        elif memory_percent > 85:
            risk_level = "high"
        else:
            risk_level = "medium"
        
        affected_resources = ["swap_usage", "disk_io", "system_performance"]
        
        cascade_effects = [
            "可能觸發 Swap 使用",
            "系統可能開始使用虛擬記憶體",
            "進程可能被終止 (OOM)"
        ]
        
        mitigation_suggestions = [
            "檢查記憶體消耗最高的進程",
            "清理不必要的進程",
            "考慮增加系統記憶體"
        ]
        
        return ResourceImpactAnalysis(
            resource_name="memory_percent",
            impact_score=impact_score,
            affected_resources=affected_resources,
            cascade_effects=cascade_effects,
            risk_level=risk_level,
            mitigation_suggestions=mitigation_suggestions
        )
    
    def _analyze_disk_impact(self, metrics: Dict[str, float]) -> Optional[ResourceImpactAnalysis]:
        """分析磁碟影響"""
        disk_percent = metrics.get('disk_percent', 0)
        
        if disk_percent < 80:
            return None
        
        impact_score = min(10, (disk_percent / 10))
        
        if disk_percent > 95:
            risk_level = "critical"
        elif disk_percent > 90:
            risk_level = "high"
        else:
            risk_level = "medium"
        
        affected_resources = ["file_operations", "logging", "cache_performance"]
        
        cascade_effects = [
            "檔案操作可能失敗",
            "日誌寫入可能受影響",
            "系統快取效能下降"
        ]
        
        mitigation_suggestions = [
            "清理臨時檔案和日誌",
            "檢查大型檔案",
            "考慮擴充磁碟空間"
        ]
        
        return ResourceImpactAnalysis(
            resource_name="disk_percent",
            impact_score=impact_score,
            affected_resources=affected_resources,
            cascade_effects=cascade_effects,
            risk_level=risk_level,
            mitigation_suggestions=mitigation_suggestions
        )
    
    def identify_bottlenecks(self, metrics_data: List[Dict]) -> List[ResourceBottleneck]:
        """識別資源瓶頸"""
        if not metrics_data:
            return []
        
        bottlenecks = []
        current_metrics = metrics_data[-1]  # 最新指標
        
        # 分析各資源的瓶頸情況
        resources_to_check = [
            ('cpu_percent', 85, 'CPU'),
            ('memory_percent', 90, 'Memory'),
            ('disk_percent', 95, 'Disk')
        ]
        
        for metric_name, threshold, resource_name in resources_to_check:
            current_value = current_metrics.get(metric_name, 0)
            
            if current_value > threshold:
                # 計算瓶頸嚴重程度
                severity = min(10, ((current_value - threshold) / (100 - threshold)) * 10)
                
                # 預測飽和時間
                predicted_time = self._predict_saturation_time(metrics_data, metric_name)
                
                # 優化建議
                recommendations = self._get_optimization_recommendations(metric_name, current_value)
                
                bottleneck = ResourceBottleneck(
                    resource_name=resource_name,
                    bottleneck_severity=severity,
                    current_utilization=current_value,
                    threshold_percentage=threshold,
                    predicted_saturation_time=predicted_time,
                    optimization_recommendations=recommendations
                )
                bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _predict_saturation_time(self, metrics_data: List[Dict], metric_name: str) -> Optional[datetime]:
        """預測資源飽和時間"""
        if len(metrics_data) < 5:
            return None
        
        values = [d.get(metric_name, 0) for d in metrics_data[-10:]]  # 使用最近10個數據點
        
        if len(values) < 3:
            return None
        
        # 簡單線性趨勢分析
        try:
            time_points = list(range(len(values)))
            slope = np.polyfit(time_points, values, 1)[0]
            
            if slope <= 0:  # 沒有上升趨勢
                return None
            
            current_value = values[-1]
            time_to_saturation = (98 - current_value) / slope  # 98% 作為飽和點
            
            if time_to_saturation > 0 and time_to_saturation < 24 * 7:  # 一週內
                return datetime.now() + timedelta(hours=time_to_saturation * 0.5)  # 假設每個數據點間隔30分鐘
        except Exception as e:
            logger.warning(f"預測飽和時間失敗: {e}")
        
        return None
    
    def _get_optimization_recommendations(self, metric_name: str, current_value: float) -> List[str]:
        """獲取優化建議"""
        recommendations = []
        
        if metric_name == 'cpu_percent':
            recommendations = [
                "分析高 CPU 使用率的進程",
                "考慮進程優化或負載分散",
                "檢查是否有異常進程",
                "評估硬體升級需求"
            ]
        elif metric_name == 'memory_percent':
            recommendations = [
                "檢查記憶體使用量最高的進程",
                "清理不必要的快取",
                "重啟記憶體洩漏的進程",
                "考慮增加系統記憶體"
            ]
        elif metric_name == 'disk_percent':
            recommendations = [
                "清理臨時檔案和日誌",
                "壓縮或歸檔舊檔案",
                "移除不必要的檔案",
                "考慮擴充儲存空間"
            ]
        
        return recommendations
    
    def calculate_system_health_index(self, current_metrics: Dict[str, float], 
                                    trend_data: List[Dict]) -> SystemHealthIndex:
        """計算系統健康指數"""
        
        # 計算各組件健康分數
        cpu_health = self._calculate_component_health(current_metrics.get('cpu_percent', 0), 80)
        memory_health = self._calculate_component_health(current_metrics.get('memory_percent', 0), 85)
        disk_health = self._calculate_component_health(current_metrics.get('disk_percent', 0), 90)
        
        # 網路健康分數（基於負載）
        load_avg = current_metrics.get('load_avg_1min', 0)
        cpu_count = psutil.cpu_count()
        network_health = max(0, 100 - (load_avg / cpu_count) * 50) if cpu_count > 0 else 100
        
        # 計算整體健康分數
        overall_score = (cpu_health + memory_health + disk_health + network_health) / 4
        
        # 分析穩定性趨勢
        stability_trend = self._analyze_stability_trend(trend_data)
        
        # 識別關鍵問題
        critical_issues = self._identify_critical_issues(current_metrics)
        
        return SystemHealthIndex(
            overall_score=overall_score,
            cpu_health=cpu_health,
            memory_health=memory_health,
            disk_health=disk_health,
            network_health=network_health,
            stability_trend=stability_trend,
            critical_issues=critical_issues
        )
    
    def _calculate_component_health(self, current_value: float, threshold: float) -> float:
        """計算組件健康分數"""
        if current_value <= threshold * 0.7:
            return 100.0
        elif current_value <= threshold:
            return 100 - ((current_value - threshold * 0.7) / (threshold * 0.3)) * 30
        else:
            return max(0, 70 - ((current_value - threshold) / (100 - threshold)) * 70)
    
    def _analyze_stability_trend(self, trend_data: List[Dict]) -> str:
        """分析穩定性趨勢"""
        if len(trend_data) < 5:
            return "stable"
        
        # 計算最近幾個數據點的變異係數
        recent_cpu = [d.get('cpu_percent', 0) for d in trend_data[-5:]]
        recent_memory = [d.get('memory_percent', 0) for d in trend_data[-5:]]
        
        try:
            cpu_cv = statistics.stdev(recent_cpu) / statistics.mean(recent_cpu) if statistics.mean(recent_cpu) > 0 else 0
            memory_cv = statistics.stdev(recent_memory) / statistics.mean(recent_memory) if statistics.mean(recent_memory) > 0 else 0
            
            avg_cv = (cpu_cv + memory_cv) / 2
            
            if avg_cv < 0.1:
                return "stable"
            elif avg_cv < 0.2:
                return "improving"
            else:
                return "declining"
        except Exception:
            return "stable"
    
    def _identify_critical_issues(self, current_metrics: Dict[str, float]) -> List[str]:
        """識別關鍵問題"""
        issues = []
        
        cpu_percent = current_metrics.get('cpu_percent', 0)
        memory_percent = current_metrics.get('memory_percent', 0)
        disk_percent = current_metrics.get('disk_percent', 0)
        
        if cpu_percent > 90:
            issues.append("CPU 使用率極高，可能影響系統響應")
        
        if memory_percent > 95:
            issues.append("記憶體使用率危險，可能觸發 OOM")
        
        if disk_percent > 95:
            issues.append("磁碟空間嚴重不足，可能影響系統操作")
        
        load_avg = current_metrics.get('load_avg_1min', 0)
        cpu_count = psutil.cpu_count()
        if load_avg > cpu_count * 2:
            issues.append("系統負載過高，處理能力不足")
        
        return issues


# 全局依賴分析器實例
dependency_analyzer = DependencyAnalyzer()