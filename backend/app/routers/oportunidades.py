from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from app.models.oportunidad import (
    OportunidadCreate, OportunidadUpdate, OportunidadResponse,
    OportunidadListResponse, OportunidadStats,
    EstadoUpdate, AsignarUpdate, MessageResponse,
    ESTADOS_LICITACION, ESTADOS_ADJUDICACION
)
from app.services.oportunidades import (
    get_oportunidades, get_oportunidad_by_expediente,
    create_oportunidad, update_oportunidad,
    update_estado, update_propietario, delete_oportunidad,
    get_stats, bulk_update_estado, bulk_update_propietario
)
from app.auth.dependencies import get_current_user, require_operador, require_admin

router = APIRouter(prefix="/api/oportunidades", tags=["oportunidades"])

# === List & Stats ===

@router.get("", response_model=OportunidadListResponse)
async def list_oportunidades(
    tipo: Optional[str] = Query(None, description="adjudicacion | licitacion"),
    sector: Optional[str] = Query(None, description="it | drones | energia | all"),
    estado: Optional[str] = Query(None),
    propietario: Optional[str] = Query(None, description="user_id | me | null | all"),
    score_min: Optional[int] = Query(None, ge=0, le=100),
    nivel: Optional[str] = Query(None, description="oro | plata | bronce | all"),
    dias_max: Optional[int] = Query(None),
    categoria: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Búsqueda en título/descripción"),
    sort: str = Query("scoring.total", description="Campo para ordenar"),
    order: str = Query("desc", description="asc | desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Listar oportunidades con filtros y paginación."""
    result = get_oportunidades(
        tipo=tipo,
        sector=sector,
        estado=estado,
        propietario=propietario,
        score_min=score_min,
        nivel=nivel,
        dias_max=dias_max,
        categoria=categoria,
        q=q,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
        current_user_id=current_user["user_id"]
    )
    return result

@router.get("/stats", response_model=OportunidadStats)
async def get_oportunidades_stats(
    tipo: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Obtener estadísticas de oportunidades."""
    return get_stats(tipo=tipo, sector=sector)

# === CRUD ===

@router.get("/{expediente}", response_model=OportunidadResponse)
async def get_oportunidad(
    expediente: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener oportunidad por expediente."""
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    return op

@router.post("", response_model=OportunidadResponse)
async def create_new_oportunidad(
    data: OportunidadCreate,
    current_user: dict = Depends(require_operador)
):
    """Crear nueva oportunidad."""
    # Verificar que no exista
    existing = get_oportunidad_by_expediente(data.expediente)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una oportunidad con ese expediente")
    
    op_dict = data.model_dump()
    op_dict["creado_por"] = current_user["user_id"]
    
    return create_oportunidad(op_dict)

@router.patch("/{expediente}", response_model=OportunidadResponse)
async def update_existing_oportunidad(
    expediente: str,
    data: OportunidadUpdate,
    current_user: dict = Depends(require_operador)
):
    """Actualizar oportunidad."""
    update_dict = data.model_dump(exclude_unset=True)
    
    result = update_oportunidad(expediente, update_dict, current_user["user_id"])
    if not result:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    return result

@router.delete("/{expediente}", response_model=MessageResponse)
async def delete_existing_oportunidad(
    expediente: str,
    current_user: dict = Depends(require_admin)
):
    """Eliminar oportunidad (solo admin)."""
    success = delete_oportunidad(expediente)
    if not success:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    return MessageResponse(message="Oportunidad eliminada correctamente")

# === Estado & Asignación ===

@router.patch("/{expediente}/estado", response_model=OportunidadResponse)
async def change_estado(
    expediente: str,
    data: EstadoUpdate,
    current_user: dict = Depends(require_operador)
):
    """Cambiar estado de oportunidad."""
    # Obtener oportunidad para validar estado
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    # Validar estado según tipo
    estados_validos = ESTADOS_LICITACION if op["tipo"] == "licitacion" else ESTADOS_ADJUDICACION
    if data.estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Estados válidos para {op['tipo']}: {estados_validos}"
        )
    
    result = update_estado(expediente, data.estado, current_user["user_id"])
    return result

@router.patch("/{expediente}/asignar", response_model=OportunidadResponse)
async def asignar_oportunidad(
    expediente: str,
    data: AsignarUpdate,
    current_user: dict = Depends(require_operador)
):
    """Asignar propietario a oportunidad."""
    # Operadores solo pueden asignarse a sí mismos
    if current_user["rol"] != "admin" and data.propietario and data.propietario != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes asignarte a ti mismo"
        )
    
    result = update_propietario(expediente, data.propietario, current_user["user_id"])
    if not result:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    return result

# === Bulk Operations ===

class BulkEstadoRequest(BaseModel):
    expedientes: List[str]
    estado: str

class BulkAsignarRequest(BaseModel):
    expedientes: List[str]
    propietario: str

@router.post("/bulk-estado", response_model=MessageResponse)
async def bulk_estado(
    data: BulkEstadoRequest,
    current_user: dict = Depends(require_operador)
):
    """Cambiar estado de múltiples oportunidades."""
    count = bulk_update_estado(data.expedientes, data.estado, current_user["user_id"])
    return MessageResponse(message=f"{count} oportunidades actualizadas")

@router.post("/bulk-asignar", response_model=MessageResponse)
async def bulk_asignar(
    data: BulkAsignarRequest,
    current_user: dict = Depends(require_admin)
):
    """Asignar propietario a múltiples oportunidades (solo admin)."""
    count = bulk_update_propietario(data.expedientes, data.propietario, current_user["user_id"])
    return MessageResponse(message=f"{count} oportunidades actualizadas")
