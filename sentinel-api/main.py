from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import datetime

app = FastAPI(title="Sentinel API", description="API de Telemetría y Seguridad")

# --- SEGURIDAD: API Key ---
API_KEY = "super_secret_key_123" 
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso Denegado: API Key inválida"
        )
    return api_key

# --- VALIDACIÓN: Lo que esperamos recibir ---
class TelemetryData(BaseModel):
    server_name: str
    cpu_usage: float
    failed_ssh_attempts: int

# --- ENDPOINTS ---
@app.get("/health")
def health_check():
    """Endpoint público para saber si el servidor está vivo"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/telemetry")
def receive_telemetry(data: TelemetryData, api_key: str = Depends(get_api_key)):
    """Endpoint privado para recibir alertas de los servidores"""
    # Aquí es donde, en el mundo real, guardaríamos esto en MongoDB
    print(f"\n[ALERTA] Servidor: {data.server_name} | Intentos SSH fallidos: {data.failed_ssh_attempts}\n")
    
    return {"status": "success", "message": "Datos procesados correctamente", "data": data}