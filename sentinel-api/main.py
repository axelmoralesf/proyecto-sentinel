from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import datetime
import os

app = FastAPI(title="Sentinel API", description="API de Telemetría y Seguridad Multi-Agente")

# --- SEGURIDAD: API Key ---
API_KEY = os.getenv("SENTINEL_API_KEY")

if not API_KEY:
    raise RuntimeError("La variable de entorno SENTINEL_API_KEY no está configurada. Por favor, configúrala antes de iniciar el servidor.")

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso Denegado: API Key inválida"
        )
    return api_key

# --- VALIDACIÓN: Datos a recibir ---
class TelemetryData(BaseModel):
    server_name: str
    cpu_usage: float
    ram_usage: float      
    gpu_usage: float      
    failed_ssh_attempts: int

# --- ENDPOINTS ---
@app.get("/health")
def health_check():
    """Endpoint público para saber si el servidor está vivo"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/telemetry")
def receive_telemetry(data: TelemetryData, api_key: str = Depends(get_api_key)):
    """Endpoint privado para recibir métricas de los agentes"""
    # En la Fase 4, cambiaremos este print por la conexión a Cassandra
    print(f"\n[TELEMETRÍA - {data.server_name}] CPU: {data.cpu_usage}% | RAM: {data.ram_usage}% | GPU: {data.gpu_usage}% | SSH Fails: {data.failed_ssh_attempts}\n")
    
    return {"status": "success", "message": "Telemetría recibida correctamente", "data": data}