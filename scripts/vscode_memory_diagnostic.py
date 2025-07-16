#!/usr/bin/env python3
"""
VS Code SSH 記憶體問題診斷工具
分析和診斷 VS Code 在 SSH 連接中的記憶體問題
"""

import psutil
import time
import json
import subprocess
import os
from datetime import datetime, timedelta
import sys

class VSCodeMemoryDiagnostic:
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'memory_analysis': {},
            'vscode_processes': [],
            'ssh_connections': [],
            'recommendations': []
        }
    
    def collect_system_info(self):
        """收集系統基本資訊"""
        try:
            import platform
            
            # 系統資訊
            uname = platform.uname()
            self.report['system_info'] = {
                'system': uname.system,
                'node': uname.node,
                'release': uname.release,
                'version': uname.version,
                'machine': uname.machine,
                'processor': uname.processor
            }
            
            # CPU 資訊
            self.report['system_info']['cpu_count'] = psutil.cpu_count()
            self.report['system_info']['cpu_percent'] = psutil.cpu_percent(interval=1)
            
            # 記憶體資訊
            memory = psutil.virtual_memory()
            self.report['system_info']['memory'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'percent': memory.percent
            }
            
            # 交換空間
            swap = psutil.swap_memory()
            self.report['system_info']['swap'] = {
                'total_gb': round(swap.total / (1024**3), 2),
                'used_gb': round(swap.used / (1024**3), 2),
                'percent': swap.percent
            }
            
        except Exception as e:
            self.report['system_info']['error'] = str(e)
    
    def analyze_memory_usage(self):
        """分析記憶體使用情況"""
        try:
            # 獲取所有進程的記憶體使用
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent', 'cmdline']):
                try:
                    pinfo = proc.info
                    memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    if memory_mb > 10:  # 只記錄使用超過10MB的進程
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'memory_mb': round(memory_mb, 1),
                            'memory_percent': round(pinfo['memory_percent'], 2),
                            'cmdline': ' '.join(pinfo['cmdline'][:3]) if pinfo['cmdline'] else ''
                        })
                except:
                    continue
            
            # 按記憶體使用排序
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            self.report['memory_analysis'] = {
                'top_processes': processes[:20],
                'total_processes': len(processes),
                'high_memory_processes': len([p for p in processes if p['memory_mb'] > 500])
            }
            
        except Exception as e:
            self.report['memory_analysis']['error'] = str(e)
    
    def analyze_vscode_processes(self):
        """分析VS Code相關進程"""
        try:
            vscode_keywords = ['code', 'node', 'copilot', 'typescript', 'eslint', 'electron']
            vscode_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'memory_percent', 'create_time']):
                try:
                    pinfo = proc.info
                    cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                    
                    # 檢查是否為VS Code相關進程
                    is_vscode = any(keyword in cmdline.lower() or keyword in pinfo['name'].lower() 
                                  for keyword in vscode_keywords)
                    
                    if is_vscode:
                        memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                        runtime_hours = (time.time() - pinfo['create_time']) / 3600
                        
                        vscode_processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'memory_mb': round(memory_mb, 1),
                            'memory_percent': round(pinfo['memory_percent'], 2),
                            'runtime_hours': round(runtime_hours, 1),
                            'cmdline': cmdline[:150] + '...' if len(cmdline) > 150 else cmdline
                        })
                        
                except:
                    continue
            
            # 按記憶體使用排序
            vscode_processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            # 統計資訊
            total_vscode_memory = sum(p['memory_mb'] for p in vscode_processes)
            avg_memory = total_vscode_memory / len(vscode_processes) if vscode_processes else 0
            
            self.report['vscode_processes'] = vscode_processes
            self.report['vscode_summary'] = {
                'process_count': len(vscode_processes),
                'total_memory_mb': round(total_vscode_memory, 1),
                'average_memory_mb': round(avg_memory, 1),
                'max_memory_mb': max([p['memory_mb'] for p in vscode_processes]) if vscode_processes else 0
            }
            
        except Exception as e:
            self.report['vscode_processes'] = []
            self.report['vscode_summary'] = {'error': str(e)}
    
    def check_ssh_connections(self):
        """檢查SSH連接狀況"""
        try:
            # 檢查網路連接
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr and conn.laddr.port == 22:  # SSH port
                    connections.append({
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        'status': conn.status,
                        'pid': conn.pid
                    })
            
            self.report['ssh_connections'] = connections
            
            # 檢查SSH進程
            ssh_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
                try:
                    if 'sshd' in proc.info['name'] or 'ssh' in proc.info['name']:
                        memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        ssh_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory_mb': round(memory_mb, 1),
                            'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        })
                except:
                    continue
            
            self.report['ssh_processes'] = ssh_processes
            
        except Exception as e:
            self.report['ssh_connections'] = []
            self.report['ssh_processes'] = []
    
    def generate_recommendations(self):
        """生成建議"""
        recommendations = []
        
        # 記憶體使用分析
        memory_percent = self.report['system_info'].get('memory', {}).get('percent', 0)
        if memory_percent > 80:
            recommendations.append({
                'level': 'critical',
                'issue': '系統記憶體使用率過高',
                'current': f"{memory_percent}%",
                'recommendation': '立即清理記憶體或重啟部分服務'
            })
        elif memory_percent > 60:
            recommendations.append({
                'level': 'warning',
                'issue': '系統記憶體使用率偏高',
                'current': f"{memory_percent}%",
                'recommendation': '監控記憶體使用並考慮優化'
            })
        
        # VS Code 進程分析
        vscode_summary = self.report.get('vscode_summary', {})
        if vscode_summary.get('total_memory_mb', 0) > 2048:
            recommendations.append({
                'level': 'warning',
                'issue': 'VS Code 進程記憶體使用過高',
                'current': f"{vscode_summary['total_memory_mb']}MB",
                'recommendation': '重啟 VS Code Server 或清理進程'
            })
        
        if vscode_summary.get('process_count', 0) > 20:
            recommendations.append({
                'level': 'info',
                'issue': 'VS Code 進程數量較多',
                'current': f"{vscode_summary['process_count']} 個進程",
                'recommendation': '檢查是否有重複或殭屍進程'
            })
        
        # 單個進程記憶體檢查
        for proc in self.report.get('vscode_processes', [])[:5]:
            if proc['memory_mb'] > 1024:
                recommendations.append({
                    'level': 'warning',
                    'issue': f'進程 {proc["name"]} (PID: {proc["pid"]}) 記憶體使用過高',
                    'current': f"{proc['memory_mb']}MB",
                    'recommendation': f'考慮重啟此進程，運行時間: {proc["runtime_hours"]}小時'
                })
        
        # 系統配置建議
        if not any(rec['issue'].startswith('已配置') for rec in recommendations):
            recommendations.extend([
                {
                    'level': 'info',
                    'issue': '系統配置優化',
                    'recommendation': '執行 /home/bao/mcp_use/scripts/optimize_vscode_ssh.sh 進行系統優化'
                },
                {
                    'level': 'info',
                    'issue': 'VS Code 設置優化',
                    'recommendation': '應用 /home/bao/mcp_use/config/vscode-memory-optimized-settings.json 中的設置'
                },
                {
                    'level': 'info',
                    'issue': '定期監控',
                    'recommendation': '啟用記憶體監控服務: sudo systemctl enable vscode-memory-monitor'
                }
            ])
        
        self.report['recommendations'] = recommendations
    
    def print_report(self):
        """打印診斷報告"""
        print("=" * 80)
        print("VS CODE SSH 記憶體診斷報告")
        print("=" * 80)
        print(f"生成時間: {self.report['timestamp']}")
        print()
        
        # 系統資訊
        print("🖥️  系統資訊:")
        sys_info = self.report['system_info']
        print(f"   系統: {sys_info.get('system', 'N/A')} {sys_info.get('release', 'N/A')}")
        print(f"   CPU: {sys_info.get('cpu_count', 'N/A')} 核心, 使用率: {sys_info.get('cpu_percent', 'N/A')}%")
        
        memory = sys_info.get('memory', {})
        print(f"   記憶體: {memory.get('used_gb', 'N/A')}GB / {memory.get('total_gb', 'N/A')}GB ({memory.get('percent', 'N/A')}%)")
        
        swap = sys_info.get('swap', {})
        if swap.get('total_gb', 0) > 0:
            print(f"   交換空間: {swap.get('used_gb', 'N/A')}GB / {swap.get('total_gb', 'N/A')}GB ({swap.get('percent', 'N/A')}%)")
        print()
        
        # VS Code 進程摘要
        print("📝 VS Code 進程摘要:")
        vscode_summary = self.report.get('vscode_summary', {})
        print(f"   進程數: {vscode_summary.get('process_count', 'N/A')}")
        print(f"   總記憶體: {vscode_summary.get('total_memory_mb', 'N/A')} MB")
        print(f"   平均記憶體: {vscode_summary.get('average_memory_mb', 'N/A')} MB")
        print(f"   最大記憶體: {vscode_summary.get('max_memory_mb', 'N/A')} MB")
        print()
        
        # VS Code 進程詳情
        if self.report.get('vscode_processes'):
            print("🔍 VS Code 進程詳情 (前10個):")
            print(f"{'PID':<8} {'名稱':<20} {'記憶體':<10} {'運行時間':<10} {'命令行'}")
            print("-" * 80)
            for proc in self.report['vscode_processes'][:10]:
                cmdline = proc['cmdline'][:40] + '...' if len(proc['cmdline']) > 40 else proc['cmdline']
                print(f"{proc['pid']:<8} {proc['name']:<20} {proc['memory_mb']:<10} {proc['runtime_hours']:<10} {cmdline}")
            print()
        
        # SSH 連接
        if self.report.get('ssh_connections'):
            print("🌐 SSH 連接:")
            for conn in self.report['ssh_connections'][:5]:
                print(f"   {conn['remote_address']} -> {conn['local_address']} ({conn['status']})")
            print()
        
        # 建議
        print("💡 建議和解決方案:")
        recommendations = self.report.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                level_icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(rec['level'], '⚪')
                print(f"{i:2d}. {level_icon} {rec['issue']}")
                if 'current' in rec:
                    print(f"     當前狀況: {rec['current']}")
                print(f"     建議: {rec['recommendation']}")
                print()
        else:
            print("   ✅ 系統狀況良好，無特殊建議")
        
        print("=" * 80)
    
    def save_report(self, filename=None):
        """保存報告到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/bao/mcp_use/logs/vscode_diagnostic_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"📁 詳細報告已保存到: {filename}")
    
    def run_diagnostic(self):
        """執行完整診斷"""
        print("🔍 正在進行 VS Code SSH 記憶體診斷...")
        
        print("   收集系統資訊...")
        self.collect_system_info()
        
        print("   分析記憶體使用...")
        self.analyze_memory_usage()
        
        print("   分析 VS Code 進程...")
        self.analyze_vscode_processes()
        
        print("   檢查 SSH 連接...")
        self.check_ssh_connections()
        
        print("   生成建議...")
        self.generate_recommendations()
        
        print("✅ 診斷完成！\n")

def main():
    diagnostic = VSCodeMemoryDiagnostic()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--json-only':
        # 只輸出 JSON 格式
        diagnostic.run_diagnostic()
        diagnostic.save_report()
    else:
        # 執行診斷並顯示報告
        diagnostic.run_diagnostic()
        diagnostic.print_report()
        diagnostic.save_report()

if __name__ == '__main__':
    main()
