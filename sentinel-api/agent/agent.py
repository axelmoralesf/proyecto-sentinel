import psutil
import platform
import requests
import os
import subprocess
import sys
import json
import time
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("SENTINEL_API_KEY")

def detect_nvidia_gpu():
    """Detecta si hay GPU NVIDIA disponible"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--list-gpus"],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def detect_amd_gpu():
    """Detecta si hay GPU AMD (ROCm) disponible"""
    try:
        result = subprocess.run(
            ["rocm-smi", "--showid"],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.returncode == 0 and "GPU" in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def detect_intel_gpu():
    """Detecta si hay GPU Intel Arc disponible"""
    try:
        result = subprocess.run(
            ["intel_gpu_monitor", "-h"],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def get_gpu_usage_nvidia():
    """Obtiene uso de GPU NVIDIA con nvidia-smi (solo si está detectada)"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            gpu_usage = float(result.stdout.strip().split('\n')[0])
            return gpu_usage
    except (subprocess.TimeoutExpired, ValueError, IndexError):
        pass
    return 0.0

def get_gpu_usage_amd():
    """Obtiene uso de GPU AMD (solo si está detectada)"""
    try:
        result = subprocess.run(
            ["rocm-smi", "--json"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                gpu_load = data[0].get("gpu_use%", 0)
                return float(gpu_load)
    except (subprocess.TimeoutExpired, ValueError, Exception):
        pass
    return 0.0

def get_gpu_usage_intel():
    """Obtiene uso de GPU Intel Arc (solo si está detectada)"""
    try:
        result = subprocess.run(
            ["intel_gpu_monitor", "-e"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "Render/Compute" in result.stdout:
            for line in result.stdout.split('\n'):
                if "Render/Compute" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if '%' in part:
                            return float(part.replace('%', ''))
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return 0.0

def get_gpu_usage():
    """Detecta GPU disponible y obtiene su uso. Si no hay GPU, devuelve 0.0"""
    # Detecta NVIDIA primero (más común)
    if detect_nvidia_gpu():
        return get_gpu_usage_nvidia()
    
    # Detecta AMD
    if detect_amd_gpu():
        return get_gpu_usage_amd()
    
    # Detecta Intel Arc
    if detect_intel_gpu():
        return get_gpu_usage_intel()
    
    # Si no hay GPU detectada, devuelve 0
    return 0.0

def get_failed_ssh_attempts():
    """Obtiene intentos fallidos de SSH (Devuelve 0 si no es posible)"""
    try:
        os_name = sys.platform
        
        # Linux
        if os_name.startswith('linux'):
            try:
                result = subprocess.run(
                    ["grep", "Failed password", "/var/log/auth.log"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return len(result.stdout.strip().split('\n'))
            except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
                pass
        
        # macOS
        elif os_name == 'darwin':
            try:
                result = subprocess.run(
                    ["log", "show", "--predicate", 'process == "sshd"', "--last", "1h"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    failed = len([l for l in result.stdout.split('\n') if 'Failed password' in l or 'Disconnected' in l])
                    return failed
            except (subprocess.TimeoutExpired, PermissionError):
                pass
        
        # Windows (Event Viewer)
        elif os_name == 'win32':
            try:
                result = subprocess.run(
                    ["powershell", "-Command", 
                     "Get-EventLog -LogName Security -Source Microsoft-Windows-Security-SPP -EventId 4625 -After (Get-Date).AddHours(-1) | Measure-Object | Select-Object -ExpandProperty Count"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return int(result.stdout.strip())
            except (subprocess.TimeoutExpired, ValueError, PermissionError):
                pass
    except Exception:
        pass
    
    return 0

def obtener_metricas():
    """Recopila métricas del sistema (multi-OS, multi-GPU)"""
    return {
        "server_name": platform.node(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram_usage": psutil.virtual_memory().percent,
        "gpu_usage": get_gpu_usage(),
        "failed_ssh_attempts": get_failed_ssh_attempts()
    }

def enviar_datos():
    """Envía las métricas a la API remota"""
    if not API_KEY:
        print("[!] Error: No se encontró SENTINEL_API_KEY en .env")
        return
    
    if not API_URL:
        print("[!] Error: No se encontró API_URL en .env")
        return

    headers = {"X-API-Key": API_KEY}
    payload = obtener_metricas()
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"[+] ÉXITO | Datos enviados desde {payload['server_name']} | CPU: {payload['cpu_usage']:.1f}% | RAM: {payload['ram_usage']:.1f}% | GPU: {payload['gpu_usage']:.1f}%")
        else:
            print(f"[-] RECHAZADO | Código: {response.status_code} | Detalle: {response.text}")
    except requests.exceptions.Timeout:
        print(f"[!] Error: Timeout conectando a {API_URL}")
    except requests.exceptions.ConnectionError:
        print(f"[!] Error: No se pudo conectar a {API_URL}")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")

if __name__ == "__main__":
    while True:
        enviar_datos()
        time.sleep(60)