#!/usr/bin/env python3
import subprocess
import requests
import time
import os
import argparse
import json
from datetime import datetime
import platform
import psutil

API_BASE_URL = 'http://localhost:8000'

def get_system_info():
    """Get basic system information"""
    info = {
        'os': platform.platform(),
        'cpu': platform.processor(),
        'python': platform.python_version(),
        'hostname': platform.node(),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # Get memory info
    memory = psutil.virtual_memory()
    info['memory'] = {
        'total': f"{memory.total / (1024**3):.2f} GB",
        'available': f"{memory.available / (1024**3):.2f} GB",
        'percent_used': f"{memory.percent}%"
    }
    
    # CPU usage
    info['cpu_percent'] = f"{psutil.cpu_percent()}%"
    
    return info

def get_gpu_info():
    """Get NVIDIA GPU information using nvidia-smi"""
    try:
        nvidia_smi = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu', 
             '--format=csv,noheader,nounits']
        ).decode('utf-8').strip()
        
        gpu_data = []
        for i, line in enumerate(nvidia_smi.split('\n')):
            name, total, used, free, temp, util = [x.strip() for x in line.split(',')]
            gpu_data.append({
                'id': i,
                'name': name,
                'memory_total_gb': float(total) / 1024,
                'memory_used_gb': float(used) / 1024,
                'memory_free_gb': float(free) / 1024, 
                'memory_used_percent': (float(used) / float(total)) * 100,
                'temperature_c': float(temp),
                'utilization_percent': float(util)
            })
        
        return gpu_data
    except (subprocess.SubprocessError, FileNotFoundError):
        return []

def get_api_health():
    """Get WhisperX API health information"""
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {'status': 'error', 'code': response.status_code}
    except requests.exceptions.RequestException:
        return {'status': 'unreachable'}

def get_api_models():
    """Get WhisperX API models information"""
    try:
        response = requests.get(f'{API_BASE_URL}/models/info', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {'status': 'error', 'code': response.status_code}
    except requests.exceptions.RequestException:
        return {'status': 'unreachable'}

def get_gunicorn_processes():
    """Get information about running Gunicorn processes"""
    gunicorn_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            if 'gunicorn' in proc.info['name'] or (proc.info['cmdline'] and 'gunicorn' in ' '.join(proc.info['cmdline'])):
                process_info = {
                    'pid': proc.info['pid'],
                    'user': proc.info['username'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent'],
                    'uptime': time.time() - proc.info['create_time'],
                }
                gunicorn_processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return gunicorn_processes

def format_uptime(seconds):
    """Format seconds into a human-readable uptime string"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{int(days)}d")
    if hours > 0 or days > 0:
        parts.append(f"{int(hours)}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{int(minutes)}m")
    parts.append(f"{int(seconds)}s")
    
    return " ".join(parts)

def display_dashboard(interval=5, continuous=False):
    """Display a monitoring dashboard"""
    try:
        iteration = 0
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            iteration += 1
            
            print("=" * 80)
            print(f"📊 WHISPERX API MONITOR {'(CONTINUOUS MODE)' if continuous else ''}")
            print(f"⏱️  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🔄 Update #{iteration} (Refresh every {interval}s)")
            print("=" * 80)
            
            # System Information
            system_info = get_system_info()
            print("\n📌 SYSTEM INFORMATION")
            print(f"OS:      {system_info['os']}")
            print(f"CPU:     {system_info['cpu']} (Usage: {system_info['cpu_percent']})")
            print(f"Memory:  {system_info['memory']['available']} available of {system_info['memory']['total']} ({system_info['memory']['percent_used']} used)")
            print(f"Python:  {system_info['python']}")
            
            # GPU Information
            gpu_info = get_gpu_info()
            if gpu_info:
                print("\n📌 GPU INFORMATION")
                for gpu in gpu_info:
                    print(f"GPU {gpu['id']}: {gpu['name']}")
                    print(f"  Memory:      {gpu['memory_used_gb']:.2f}GB / {gpu['memory_total_gb']:.2f}GB ({gpu['memory_used_percent']:.1f}%)")
                    print(f"  Temperature: {gpu['temperature_c']}°C")
                    print(f"  Utilization: {gpu['utilization_percent']:.1f}%")
            
            # API Status
            print("\n📌 API STATUS")
            api_health = get_api_health()
            if api_health.get('status') == 'healthy':
                print("✅ API is healthy")
                print(f"  Device:    {api_health.get('device', 'unknown')}")
                if api_health.get('gpu_memory'):
                    print(f"  GPU Memory: {api_health.get('gpu_memory'):.2f} GB")
                print("  Models:")
                print(f"    WhisperX: {'Loaded' if api_health.get('whisperx_loaded') else 'Not loaded'}")
                print(f"    Align:    {'Loaded' if api_health.get('align_loaded') else 'Not loaded'}")
                print(f"    Diarize:  {'Loaded' if api_health.get('diarize_loaded') else 'Not loaded'}")
            elif api_health.get('status') == 'unreachable':
                print("❌ API is unreachable - check if the server is running")
            else:
                print(f"❌ API returned error: {api_health}")
            
            # Gunicorn Processes
            gunicorn_processes = get_gunicorn_processes()
            if gunicorn_processes:
                print("\n📌 GUNICORN PROCESSES")
                for i, proc in enumerate(gunicorn_processes):
                    print(f"Process {i+1}: PID {proc['pid']}")
                    print(f"  User:    {proc['user']}")
                    print(f"  CPU:     {proc['cpu_percent']:.1f}%")
                    print(f"  Memory:  {proc['memory_percent']:.1f}%")
                    print(f"  Uptime:  {format_uptime(proc['uptime'])}")
            
            print("\n" + "=" * 80)
            print("Press Ctrl+C to exit")
            
            if not continuous:
                break
                
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

def main():
    parser = argparse.ArgumentParser(description='Monitor WhisperX API')
    parser.add_argument('--port', '-p', type=int, default=8000, 
                        help='API port (default: 8000)')
    parser.add_argument('--interval', '-i', type=int, default=5,
                        help='Refresh interval in seconds (default: 5)')
    parser.add_argument('--continuous', '-c', action='store_true',
                        help='Run in continuous monitoring mode')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output results as JSON')
    
    args = parser.parse_args()
    
    global API_BASE_URL
    API_BASE_URL = f'http://localhost:{args.port}'
    
    if args.json:
        # Output data as JSON
        data = {
            'timestamp': datetime.now().isoformat(),
            'system': get_system_info(),
            'gpu': get_gpu_info(),
            'api_health': get_api_health(),
            'api_models': get_api_models(),
            'gunicorn_processes': get_gunicorn_processes()
        }
        print(json.dumps(data, indent=2))
    else:
        # Display interactive dashboard
        display_dashboard(interval=args.interval, continuous=args.continuous)

if __name__ == "__main__":
    main()