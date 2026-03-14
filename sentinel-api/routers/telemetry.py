from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from models import TelemetryData
from database import get_db
import datetime
import os

# Creamos el router. Todas las rutas aquí empezarán con /telemetry automáticamente
router = APIRouter(prefix="/telemetry", tags=["Telemetría"])

# --- SEGURIDAD ---
API_KEY = os.getenv("SENTINEL_API_KEY")
if not API_KEY:
    raise RuntimeError("CRÍTICO: SENTINEL_API_KEY no configurada.")

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key inválida")
    return api_key

# --- ENDPOINTS ---
# Como el router ya tiene el prefijo, la ruta final será POST /telemetry
@router.post("/")
def receive_telemetry(data: TelemetryData, api_key: str = Depends(get_api_key)):
    try:
        session = get_db()
    except Exception:
         raise HTTPException(status_code=500, detail="Base de datos no disponible")

    recorded_at = datetime.datetime.now()
    query = """
        INSERT INTO telemetry (server_name, recorded_at, cpu_usage, ram_usage, gpu_usage, failed_ssh_attempts)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        session.execute(query, (
            data.server_name, recorded_at, data.cpu_usage, 
            data.ram_usage, data.gpu_usage, data.failed_ssh_attempts
        ))
        print(f"[+] Datos guardados | Servidor: {data.server_name}")
        return {"status": "success", "message": "Telemetría guardada en Cassandra"}
    except Exception as e:
        print(f"[-] Error en BD: {e}")
        raise HTTPException(status_code=500, detail="Error interno al escribir en BD")