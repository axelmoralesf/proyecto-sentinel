from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from models import TelemetryData
from database import get_table
from botocore.exceptions import ClientError
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
        table = get_table()
    except Exception:
         raise HTTPException(status_code=500, detail="Base de datos no disponible")

    timestamp = datetime.datetime.now().isoformat()
    # agent_id es la partition key (server_name)
    # timestamp es la sort key
    item = {
        "agent_id": data.server_name,
        "timestamp": timestamp,
        "cpu_usage": data.cpu_usage,
        "ram_usage": data.ram_usage,
        "gpu_usage": data.gpu_usage,
        "failed_ssh_attempts": data.failed_ssh_attempts
    }
    
    try:
        table.put_item(Item=item)
        print(f"[+] Datos guardados en DynamoDB | Agent: {data.server_name} | Timestamp: {timestamp}")
        return {"status": "success", "message": "Telemetría guardada en DynamoDB"}
    except ClientError as e:
        print(f"[-] Error en DynamoDB: {e}")
        raise HTTPException(status_code=500, detail="Error interno al escribir en DynamoDB")