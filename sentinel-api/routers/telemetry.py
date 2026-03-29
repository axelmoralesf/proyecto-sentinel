from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from models import TelemetryData
from database import get_table
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from decimal import Decimal
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

def _convert_numbers_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return float(value)
    if isinstance(value, list):
        return [_convert_numbers_to_float(item) for item in value]
    if isinstance(value, dict):
        return {k: _convert_numbers_to_float(v) for k, v in value.items()}
    return value

def _get_all_agent_ids(table):
    agent_ids = set()
    exclusive_start_key = None

    while True:
        scan_kwargs = {
            "ProjectionExpression": "agent_id",
        }
        if exclusive_start_key:
            scan_kwargs["ExclusiveStartKey"] = exclusive_start_key

        response = table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            agent_id = item.get("agent_id")
            if agent_id:
                agent_ids.add(agent_id)

        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            break

    return agent_ids

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
        "cpu_usage": Decimal(str(data.cpu_usage)),
        "ram_usage": Decimal(str(data.ram_usage)),
        "gpu_usage": Decimal(str(data.gpu_usage)),
        "failed_ssh_attempts": data.failed_ssh_attempts
    }
    
    try:
        table.put_item(Item=item)
        print(f"[+] Datos guardados en DynamoDB | Agent: {data.server_name} | Timestamp: {timestamp}")
        return {"status": "success", "message": "Telemetría guardada en DynamoDB"}
    except ClientError as e:
        print(f"[-] Error en DynamoDB: {e}")
        raise HTTPException(status_code=500, detail="Error interno al escribir en DynamoDB")
    
@router.get("/")
def get_telemetry(api_key: str = Depends(get_api_key)):
    try:
        table = get_table()
    except Exception:
        raise HTTPException(status_code=500, detail="Base de datos no disponible")

    try:
        items = []
        agent_ids = _get_all_agent_ids(table)

        for agent_id in agent_ids:
            exclusive_start_key = None
            while True:
                query_kwargs = {
                    "KeyConditionExpression": Key("agent_id").eq(agent_id)
                }
                if exclusive_start_key:
                    query_kwargs["ExclusiveStartKey"] = exclusive_start_key

                response = table.query(**query_kwargs)
                items.extend(response.get("Items", []))

                exclusive_start_key = response.get("LastEvaluatedKey")
                if not exclusive_start_key:
                    break

        return {"status": "success", "data": _convert_numbers_to_float(items)}
    except ClientError as e:
        print(f"[-] Error en DynamoDB: {e}")
        raise HTTPException(status_code=500, detail="Error interno al leer de DynamoDB")