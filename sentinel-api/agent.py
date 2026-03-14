import psutil
import platform
import requests
import os
import time
from dotenv import load_dotenv

# Cargar las variables del archivo .env oculto
load_dotenv()

# Como tu API está corriendo localmente en Docker, usamos localhost
API_URL = "http://127.0.0.1:8000/telemetry"
API_KEY = os.getenv("SENTINEL_API_KEY") 

def obtener_metricas():
    # Extraemos el estado real de tu Arch Linux
    return {
        "server_name": platform.node(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram_usage": psutil.virtual_memory().percent,
        "gpu_usage": 0.0, # Lo dejamos en 0 por ahora para la prueba
        "failed_ssh_attempts": 0 # Simulamos 0 ataques
    }

def enviar_datos():
    if not API_KEY:
        print("[!] Error: No se encontró la SENTINEL_API_KEY en el archivo .env")
        return

    headers = {"X-API-Key": API_KEY}
    payload = obtener_metricas()
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"[+] ÉXITO | Datos enviados desde {payload['server_name']} | CPU: {payload['cpu_usage']}% | RAM: {payload['ram_usage']}%")
        else:
            print(f"[-] RECHAZADO | Código: {response.status_code} | Detalle: {response.text}")
    except Exception as e:
        print(f"[!] No se pudo conectar a la API: {e}")

if __name__ == "__main__":
    # Enviamos una sola ráfaga de datos
    enviar_datos()