"""
I/O 性能分析器
深入分析系統的輸入/輸出性能
"""
import psutil
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import logging

import sys
# 動態添加項目根目錄到 Python 路徑
from pathlib import Path
current_path = Path(__file__).parent
project_root = current_path
while project_root.parent != project_root:
    if (project_root / "app").exists():
        break
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

from app.api.models.io_analysis import (
    DiskIOStats, NetworkIOStats, ProcessIOStats, IOPerformanceMetrics,
    IOBottleneckAnalysis, IOTrendAnalysis, FileSystemAnalysis, IOInsight, IOSummary
)

logger = logging.getLogger(__name__)


class IOAnalyzer:
    """I/O 性能分析器"""
    
    def __init__(self):
        self.io_history = []
        self.last_disk_io = None
        self.last_network_io = None
        self.last_measurement_time = None
        
    def collect_io_metrics(self) -> IOPerformanceMetrics:
        """收集 I/O 性能指標"""
        current_time = datetime.now()
        
        # 收集磁碟 I/O 統計
        disk_stats = self._collect_disk_io_stats()
        
        # 收集網路 I/O 統計
        network_stats = self._collect_network_io_stats()
        
        # 收集進程 I/O 統計
        process_stats = self._collect_process_io_stats()
        
        # 計算速率
        disk_read_rate, disk_write_rate = self._calculate_disk_rates(disk_stats)
        network_in_rate, network_out_rate = self._calculate_network_rates(network_stats)
        
        metrics = IOPerformanceMetrics(
            timestamp=current_time,
            disk_io_stats=disk_stats,
            network_io_stats=network_stats,
            top_io_processes=process_stats,
            total_disk_read_rate=disk_read_rate,
            total_disk_write_rate=disk_write_rate,
            total_network_in_rate=network_in_rate,
            total_network_out_rate=network_out_rate
        )
        
        # 保存到歷史記錄
        self.io_history.append(metrics)
        
        # 只保留最近24小時的數據
        cutoff_time = current_time - timedelta(hours=24)
        self.io_history = [m for m in self.io_history if m.timestamp >= cutoff_time]
        
        return metrics
    
    def _collect_disk_io_stats(self) -> List[DiskIOStats]:
        """收集磁碟 I/O 統計"""
        disk_stats = []
        
        try:
            disk_io = psutil.disk_io_counters(perdisk=True)
            
            for device, counters in disk_io.items():
                stat = DiskIOStats(
                    device_name=device,
                    read_bytes=counters.read_bytes,
                    write_bytes=counters.write_bytes,
                    read_ops=counters.read_count,
                    write_ops=counters.write_count,
                    read_time_ms=counters.read_time,
                    write_time_ms=counters.write_time,
                    io_in_progress=0  # psutil 沒有直接提供此資訊
                )
                disk_stats.append(stat)
                
        except Exception as e:
            logger.warning(f"收集磁碟 I/O 統計失敗: {e}")
        
        return disk_stats
    
    def _collect_network_io_stats(self) -> List[NetworkIOStats]:
        """收集網路 I/O 統計"""
        network_stats = []
        
        try:
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface, counters in net_io.items():
                if interface.startswith('lo'):  # 跳過回環介面
                    continue
                    
                stat = NetworkIOStats(
                    interface_name=interface,
                    bytes_sent=counters.bytes_sent,
                    bytes_recv=counters.bytes_recv,
                    packets_sent=counters.packets_sent,
                    packets_recv=counters.packets_recv,
                    errors_in=counters.errin,
                    errors_out=counters.errout,
                    drops_in=counters.dropin,
                    drops_out=counters.dropout
                )
                network_stats.append(stat)
                
        except Exception as e:
            logger.warning(f"收集網路 I/O 統計失敗: {e}")
        
        return network_stats
    
    def _collect_process_io_stats(self) -> List[ProcessIOStats]:
        """收集進程 I/O 統計"""
        process_stats = []
        
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    io_counters = proc.io_counters()
                    
                    stat = ProcessIOStats(
                        pid=proc.info['pid'],
                        process_name=proc.info['name'],
                        read_bytes=io_counters.read_bytes,
                        write_bytes=io_counters.write_bytes,
                        read_chars=io_counters.read_chars,
                        write_chars=io_counters.write_chars,
                        read_syscalls=io_counters.read_count,
                        write_syscalls=io_counters.write_count
                    )
                    processes.append(stat)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 按總 I/O 量排序，取前10個
            processes.sort(key=lambda x: x.read_bytes + x.write_bytes, reverse=True)
            process_stats = processes[:10]
            
        except Exception as e:
            logger.warning(f"收集進程 I/O 統計失敗: {e}")
        
        return process_stats
    
    def _calculate_disk_rates(self, current_stats: List[DiskIOStats]) -> Tuple[float, float]:
        """計算磁碟讀寫速率"""
        current_time = time.time()
        
        if self.last_disk_io is None or self.last_measurement_time is None:
            self.last_disk_io = current_stats
            self.last_measurement_time = current_time
            return 0.0, 0.0
        
        time_diff = current_time - self.last_measurement_time
        if time_diff <= 0:
            return 0.0, 0.0
        
        total_read_diff = 0
        total_write_diff = 0
        
        # 計算所有磁碟的讀寫差值
        current_disk_map = {stat.device_name: stat for stat in current_stats}
        last_disk_map = {stat.device_name: stat for stat in self.last_disk_io}
        
        for device, current_stat in current_disk_map.items():
            if device in last_disk_map:
                last_stat = last_disk_map[device]
                read_diff = max(0, current_stat.read_bytes - last_stat.read_bytes)
                write_diff = max(0, current_stat.write_bytes - last_stat.write_bytes)
                total_read_diff += read_diff
                total_write_diff += write_diff
        
        # 轉換為 MB/s
        read_rate = (total_read_diff / time_diff) / (1024 * 1024)
        write_rate = (total_write_diff / time_diff) / (1024 * 1024)
        
        self.last_disk_io = current_stats
        self.last_measurement_time = current_time
        
        return read_rate, write_rate
    
    def _calculate_network_rates(self, current_stats: List[NetworkIOStats]) -> Tuple[float, float]:
        """計算網路傳輸速率"""
        current_time = time.time()
        
        if self.last_network_io is None:
            self.last_network_io = current_stats
            return 0.0, 0.0
        
        time_diff = current_time - self.last_measurement_time if self.last_measurement_time else 0
        if time_diff <= 0:
            return 0.0, 0.0
        
        total_in_diff = 0
        total_out_diff = 0
        
        # 計算所有網路介面的傳輸差值
        current_net_map = {stat.interface_name: stat for stat in current_stats}
        last_net_map = {stat.interface_name: stat for stat in self.last_network_io}
        
        for interface, current_stat in current_net_map.items():
            if interface in last_net_map:
                last_stat = last_net_map[interface]
                in_diff = max(0, current_stat.bytes_recv - last_stat.bytes_recv)
                out_diff = max(0, current_stat.bytes_sent - last_stat.bytes_sent)
                total_in_diff += in_diff
                total_out_diff += out_diff
        
        # 轉換為 MB/s
        in_rate = (total_in_diff / time_diff) / (1024 * 1024)
        out_rate = (total_out_diff / time_diff) / (1024 * 1024)
        
        self.last_network_io = current_stats
        
        return in_rate, out_rate
    
    def analyze_io_bottlenecks(self, hours: int = 1) -> List[IOBottleneckAnalysis]:
        """分析 I/O 瓶頸"""
        if not self.io_history:
            return []
        
        bottlenecks = []
        recent_metrics = self._get_recent_metrics(hours)
        
        if not recent_metrics:
            return []
        
        # 分析磁碟 I/O 瓶頸
        disk_bottlenecks = self._analyze_disk_bottlenecks(recent_metrics)
        bottlenecks.extend(disk_bottlenecks)
        
        # 分析網路 I/O 瓶頸
        network_bottlenecks = self._analyze_network_bottlenecks(recent_metrics)
        bottlenecks.extend(network_bottlenecks)
        
        return bottlenecks
    
    def _get_recent_metrics(self, hours: int) -> List[IOPerformanceMetrics]:
        """獲取最近的指標"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.io_history if m.timestamp >= cutoff_time]
    
    def _analyze_disk_bottlenecks(self, metrics: List[IOPerformanceMetrics]) -> List[IOBottleneckAnalysis]:
        """分析磁碟瓶頸"""
        bottlenecks = []
        
        if not metrics:
            return bottlenecks
        
        # 分析磁碟讀寫速率
        read_rates = [m.total_disk_read_rate for m in metrics]
        write_rates = [m.total_disk_write_rate for m in metrics]
        
        if read_rates:
            max_read_rate = max(read_rates)
            avg_read_rate = statistics.mean(read_rates)
            
            # 如果讀取速率持續很高，可能是瓶頸
            if avg_read_rate > 50:  # 50 MB/s 閾值
                severity = min(10, avg_read_rate / 10)
                utilization = (avg_read_rate / 100) * 100  # 假設100MB/s為滿載
                
                bottleneck = IOBottleneckAnalysis(
                    bottleneck_type="disk",
                    resource_name="磁碟讀取",
                    severity_score=severity,
                    current_utilization=min(100, utilization),
                    max_throughput=100.0,
                    current_throughput=avg_read_rate,
                    impact_description=f"磁碟讀取速率過高 ({avg_read_rate:.1f} MB/s)，可能影響系統響應",
                    optimization_suggestions=[
                        "檢查大量讀取檔案的進程",
                        "考慮使用 SSD 替代 HDD",
                        "優化檔案存取模式",
                        "增加系統記憶體以提高快取效率"
                    ]
                )
                bottlenecks.append(bottleneck)
        
        if write_rates:
            max_write_rate = max(write_rates)
            avg_write_rate = statistics.mean(write_rates)
            
            if avg_write_rate > 30:  # 30 MB/s 閾值
                severity = min(10, avg_write_rate / 10)
                utilization = (avg_write_rate / 100) * 100
                
                bottleneck = IOBottleneckAnalysis(
                    bottleneck_type="disk",
                    resource_name="磁碟寫入",
                    severity_score=severity,
                    current_utilization=min(100, utilization),
                    max_throughput=100.0,
                    current_throughput=avg_write_rate,
                    impact_description=f"磁碟寫入速率過高 ({avg_write_rate:.1f} MB/s)，可能影響系統性能",
                    optimization_suggestions=[
                        "檢查大量寫入檔案的進程",
                        "優化日誌寫入策略",
                        "考慮使用更快的儲存設備",
                        "實施寫入快取策略"
                    ]
                )
                bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _analyze_network_bottlenecks(self, metrics: List[IOPerformanceMetrics]) -> List[IOBottleneckAnalysis]:
        """分析網路瓶頸"""
        bottlenecks = []
        
        if not metrics:
            return bottlenecks
        
        # 分析網路傳輸速率
        in_rates = [m.total_network_in_rate for m in metrics]
        out_rates = [m.total_network_out_rate for m in metrics]
        
        if in_rates:
            avg_in_rate = statistics.mean(in_rates)
            
            if avg_in_rate > 10:  # 10 MB/s 閾值
                severity = min(10, avg_in_rate / 5)
                utilization = (avg_in_rate / 125) * 100  # 假設 1Gbps = 125MB/s
                
                bottleneck = IOBottleneckAnalysis(
                    bottleneck_type="network",
                    resource_name="網路接收",
                    severity_score=severity,
                    current_utilization=min(100, utilization),
                    max_throughput=125.0,
                    current_throughput=avg_in_rate,
                    impact_description=f"網路接收速率過高 ({avg_in_rate:.1f} MB/s)，可能影響網路性能",
                    optimization_suggestions=[
                        "檢查大量網路接收的進程",
                        "優化網路封包處理",
                        "考慮升級網路頻寬",
                        "實施網路流量控制"
                    ]
                )
                bottlenecks.append(bottleneck)
        
        if out_rates:
            avg_out_rate = statistics.mean(out_rates)
            
            if avg_out_rate > 10:  # 10 MB/s 閾值
                severity = min(10, avg_out_rate / 5)
                utilization = (avg_out_rate / 125) * 100
                
                bottleneck = IOBottleneckAnalysis(
                    bottleneck_type="network",
                    resource_name="網路發送",
                    severity_score=severity,
                    current_utilization=min(100, utilization),
                    max_throughput=125.0,
                    current_throughput=avg_out_rate,
                    impact_description=f"網路發送速率過高 ({avg_out_rate:.1f} MB/s)，可能影響網路性能",
                    optimization_suggestions=[
                        "檢查大量網路發送的進程",
                        "優化資料傳輸策略",
                        "考慮壓縮網路傳輸資料",
                        "實施帶寬管理"
                    ]
                )
                bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def analyze_filesystem(self) -> List[FileSystemAnalysis]:
        """分析檔案系統"""
        filesystem_analysis = []
        
        try:
            disk_partitions = psutil.disk_partitions()
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # 嘗試獲取 inode 資訊（Linux 系統）
                    inode_total = 0
                    inode_used = 0
                    inode_usage = 0.0
                    
                    try:
                        statvfs = psutil.disk_usage(partition.mountpoint)
                        # 注意：psutil 的 disk_usage 不直接提供 inode 資訊
                        # 這裡使用模擬數據
                        inode_total = usage.total // 4096  # 假設平均檔案大小 4KB
                        inode_used = usage.used // 4096
                        inode_usage = (inode_used / inode_total) * 100 if inode_total > 0 else 0
                    except:
                        pass
                    
                    analysis = FileSystemAnalysis(
                        mount_point=partition.mountpoint,
                        file_system_type=partition.fstype,
                        total_space=usage.total,
                        used_space=usage.used,
                        free_space=usage.free,
                        usage_percentage=(usage.used / usage.total) * 100,
                        inode_total=inode_total,
                        inode_used=inode_used,
                        inode_usage_percentage=inode_usage,
                        fragmentation_level=None  # 需要特殊工具檢測
                    )
                    filesystem_analysis.append(analysis)
                    
                except (PermissionError, FileNotFoundError):
                    continue
                    
        except Exception as e:
            logger.warning(f"分析檔案系統失敗: {e}")
        
        return filesystem_analysis
    
    def generate_io_insights(self, hours: int = 6) -> List[IOInsight]:
        """生成 I/O 洞察"""
        insights = []
        recent_metrics = self._get_recent_metrics(hours)
        
        if not recent_metrics:
            return insights
        
        # 分析磁碟 I/O 模式
        disk_insights = self._analyze_disk_patterns(recent_metrics)
        insights.extend(disk_insights)
        
        # 分析網路 I/O 模式
        network_insights = self._analyze_network_patterns(recent_metrics)
        insights.extend(network_insights)
        
        # 分析檔案系統狀況
        filesystem_insights = self._analyze_filesystem_health()
        insights.extend(filesystem_insights)
        
        return insights
    
    def _analyze_disk_patterns(self, metrics: List[IOPerformanceMetrics]) -> List[IOInsight]:
        """分析磁碟 I/O 模式"""
        insights = []
        
        read_rates = [m.total_disk_read_rate for m in metrics]
        write_rates = [m.total_disk_write_rate for m in metrics]
        
        if read_rates and write_rates:
            avg_read = statistics.mean(read_rates)
            avg_write = statistics.mean(write_rates)
            
            # 檢查讀寫比例
            if avg_read > avg_write * 3:
                insight = IOInsight(
                    insight_type="disk_pattern",
                    title="磁碟讀取密集",
                    description=f"系統呈現讀取密集模式，讀取速率 ({avg_read:.1f} MB/s) 遠高於寫入速率 ({avg_write:.1f} MB/s)",
                    severity="info",
                    affected_resources=["disk_performance", "cache_efficiency"],
                    recommended_actions=[
                        "考慮增加系統記憶體以提高快取效率",
                        "優化資料庫查詢模式",
                        "使用 SSD 提高讀取性能"
                    ],
                    confidence=0.8
                )
                insights.append(insight)
            elif avg_write > avg_read * 3:
                insight = IOInsight(
                    insight_type="disk_pattern",
                    title="磁碟寫入密集",
                    description=f"系統呈現寫入密集模式，寫入速率 ({avg_write:.1f} MB/s) 遠高於讀取速率 ({avg_read:.1f} MB/s)",
                    severity="warning",
                    affected_resources=["disk_performance", "system_responsiveness"],
                    recommended_actions=[
                        "檢查日誌寫入策略",
                        "優化資料庫寫入操作",
                        "考慮使用寫入快取"
                    ],
                    confidence=0.8
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_network_patterns(self, metrics: List[IOPerformanceMetrics]) -> List[IOInsight]:
        """分析網路 I/O 模式"""
        insights = []
        
        in_rates = [m.total_network_in_rate for m in metrics]
        out_rates = [m.total_network_out_rate for m in metrics]
        
        if in_rates and out_rates:
            avg_in = statistics.mean(in_rates)
            avg_out = statistics.mean(out_rates)
            
            # 檢查網路使用模式
            if avg_in > 20:  # 20 MB/s
                insight = IOInsight(
                    insight_type="network_pattern",
                    title="高網路接收流量",
                    description=f"檢測到高網路接收流量 ({avg_in:.1f} MB/s)，可能是下載或同步操作",
                    severity="info" if avg_in < 50 else "warning",
                    affected_resources=["network_bandwidth", "system_performance"],
                    recommended_actions=[
                        "檢查大量下載的應用程式",
                        "監控網路使用情況",
                        "考慮實施流量控制"
                    ],
                    confidence=0.9
                )
                insights.append(insight)
            
            if avg_out > 20:  # 20 MB/s
                insight = IOInsight(
                    insight_type="network_pattern",
                    title="高網路發送流量",
                    description=f"檢測到高網路發送流量 ({avg_out:.1f} MB/s)，可能是上傳或備份操作",
                    severity="info" if avg_out < 50 else "warning",
                    affected_resources=["network_bandwidth", "upstream_capacity"],
                    recommended_actions=[
                        "檢查大量上傳的應用程式",
                        "監控備份任務",
                        "優化資料傳輸時間"
                    ],
                    confidence=0.9
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_filesystem_health(self) -> List[IOInsight]:
        """分析檔案系統健康狀況"""
        insights = []
        
        try:
            filesystem_stats = self.analyze_filesystem()
            
            for fs in filesystem_stats:
                if fs.usage_percentage > 90:
                    insight = IOInsight(
                        insight_type="filesystem_health",
                        title=f"檔案系統空間不足: {fs.mount_point}",
                        description=f"檔案系統 {fs.mount_point} 使用率達到 {fs.usage_percentage:.1f}%，空間即將耗盡",
                        severity="critical",
                        affected_resources=[fs.mount_point, "file_operations"],
                        recommended_actions=[
                            "清理不必要的檔案",
                            "移動大型檔案到其他位置",
                            "擴充儲存空間",
                            "設定檔案清理策略"
                        ],
                        confidence=0.95
                    )
                    insights.append(insight)
                elif fs.usage_percentage > 80:
                    insight = IOInsight(
                        insight_type="filesystem_health",
                        title=f"檔案系統空間警告: {fs.mount_point}",
                        description=f"檔案系統 {fs.mount_point} 使用率達到 {fs.usage_percentage:.1f}%，建議清理空間",
                        severity="warning",
                        affected_resources=[fs.mount_point],
                        recommended_actions=[
                            "檢查大型檔案",
                            "清理臨時檔案",
                            "壓縮舊日誌檔案"
                        ],
                        confidence=0.9
                    )
                    insights.append(insight)
        
        except Exception as e:
            logger.warning(f"分析檔案系統健康狀況失敗: {e}")
        
        return insights


# 全局 I/O 分析器實例
io_analyzer = IOAnalyzer()