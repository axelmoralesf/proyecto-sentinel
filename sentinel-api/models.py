from pydantic import BaseModel

class TelemetryData(BaseModel):
    server_name: str
    cpu_usage: float
    ram_usage: float
    gpu_usage: float
    failed_ssh_attempts: int