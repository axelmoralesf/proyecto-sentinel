from fastapi import FastAPI
from contextlib import asynccontextmanager
import datetime

# Importamos los módulos locales
from database import init_db, close_db
from routers import telemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al encender la API
    try:
        init_db()
    except Exception as e:
        print(f"[-] Error crítico al conectar con Cassandra: {e}")
    
    yield  # La API corre aquí
    
    # Al apagar la API
    close_db()

app = FastAPI(title="Sentinel API", description="Arquitectura Modular Multi-Agente", lifespan=lifespan)

# --- REGISTRO DE RUTAS (ENDPOINTS) ---
app.include_router(telemetry.router)

# Endpoint público para monitoreo de vida (health check)
@app.get("/health", tags=["Sistema"])
def health_check():
    """Endpoint público de monitoreo de vida"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}