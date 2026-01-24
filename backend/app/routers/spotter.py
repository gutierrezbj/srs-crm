"""Router para ejecutar SpotterEngine desde API."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel

from app.auth.dependencies import require_admin
from app.spotter.engine import SpotterEngine, ConfigLoader

router = APIRouter(prefix="/api/spotter", tags=["spotter"])

class SpotterRunRequest(BaseModel):
    sector: str
    tipo: str = "licitacion"
    limit: Optional[int] = None

class SpotterResult(BaseModel):
    sector: str
    tipo: str
    ejecutado_at: str
    total_procesadas: int
    nuevas: int
    actualizadas: int
    descartadas: int
    errores: int
    por_nivel: dict

@router.get("/sectors")
async def list_sectors(current_user: dict = Depends(require_admin)):
    """Listar sectores configurados."""
    sectors = ConfigLoader.get_active_sectors()
    return {
        "sectors": [
            {
                "sector": s.get("sector"),
                "nombre": s.get("nombre"),
                "activo": s.get("activo", True),
                "tipos": s.get("tipos", [])
            }
            for s in sectors
        ]
    }

@router.get("/config/{sector}")
async def get_sector_config(sector: str, current_user: dict = Depends(require_admin)):
    """Obtener configuración de un sector."""
    config = ConfigLoader.get_sector_config(sector)
    if not config:
        raise HTTPException(status_code=404, detail="Sector no encontrado")
    return config

@router.post("/run", response_model=SpotterResult)
async def run_spotter(
    request: SpotterRunRequest,
    current_user: dict = Depends(require_admin)
):
    """Ejecutar spotter manualmente."""
    try:
        engine = SpotterEngine(sector=request.sector, tipo=request.tipo)
        result = await engine.ejecutar(limit=request.limit)
        return SpotterResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando spotter: {e}")

@router.post("/run-all")
async def run_all_spotters(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_admin)
):
    """Ejecutar todos los spotters en background."""
    async def run_all():
        from cron.spotter_job import run_spotter_all
        await run_spotter_all()
    
    background_tasks.add_task(run_all)
    return {"message": "Spotter iniciado en background para todos los sectores"}
