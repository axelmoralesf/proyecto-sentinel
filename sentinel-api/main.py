from fastapi import FastAPI
from database import init_db, close_db
from routers import telemetry

app = FastAPI(title="Sentinel API", description="Arquitectura Modular Multi-Agente")

# --- REGISTRO DE RUTAS ---
app.include_router(telemetry.router)

# --- EVENTOS DE CICLO DE VIDA ---
@app.on_event("startup")
def startup_event():
    print("========================================")
    print("INICIANDO API SENTINEL...")
    print("========================================")
    try:
        init_db()
    except Exception as e:
        print(f"[-] Error crítico en el arranque: {e}")

@app.on_event("shutdown")
def shutdown_event():
    close_db()

# --- HEALTH CHECK ---
@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok"}