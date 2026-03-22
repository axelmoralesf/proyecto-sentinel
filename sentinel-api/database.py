import boto3
import os
from botocore.exceptions import ClientError

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "sentinel_data")
dynamodb = None

def init_db():
    global dynamodb
    print(f"[*] Conectando a DynamoDB en región: {AWS_REGION}...")
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        # Verificar que la tabla existe
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.load()
        print(f"[+] Conexión a DynamoDB establecida con éxito. Tabla: {DYNAMODB_TABLE}")
    except ClientError as e:
        print(f"[-] Error conectando a DynamoDB: {e}")
        raise Exception(f"No se pudo conectar a DynamoDB: {e}")

def close_db():
    global dynamodb
    if dynamodb:
        print("[*] Cerrando conexión a DynamoDB...")
        # boto3 maneja conexiones automáticamente
        dynamodb = None

def get_db():
    if dynamodb is None:
        raise Exception("La base de datos no está inicializada")
    return dynamodb

def get_table():
    """Obtiene la tabla de DynamoDB"""
    db = get_db()
    return db.Table(DYNAMODB_TABLE)