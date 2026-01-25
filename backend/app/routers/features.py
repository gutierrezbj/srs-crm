"""Router para features avanzados."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from typing import Optional, List
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_operador
from app.services.oportunidades import (
    get_oportunidades, get_oportunidad_by_expediente, update_oportunidad
)
from app.services.checklist import (
    crear_checklist_default, actualizar_documento, actualizar_hito,
    calcular_progreso, agregar_documento_custom
)
from app.services.analisis_ia import analizar_pliego, extraer_texto_pliego
from app.services.export import export_to_excel, export_to_csv

router = APIRouter(tags=["features"])

# === Checklist ===

class DocumentoUpdate(BaseModel):
    doc_id: str
    completado: bool
    archivo: Optional[str] = None

class HitoUpdate(BaseModel):
    hito_id: str
    completado: bool

class DocumentoCustom(BaseModel):
    nombre: str
    requerido: bool = False

@router.post("/api/oportunidades/{expediente}/iniciar-preparacion")
async def iniciar_preparacion(
    expediente: str,
    current_user: dict = Depends(require_operador)
):
    """Iniciar preparación de licitación (crea checklist)."""
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    if op.get("tipo") != "licitacion":
        raise HTTPException(status_code=400, detail="Solo licitaciones pueden tener checklist")
    
    checklist = crear_checklist_default()
    
    result = update_oportunidad(
        expediente,
        {
            "estado": "en_preparacion",
            "checklist": checklist,
            "propietario": op.get("propietario") or current_user["user_id"]
        },
        current_user["user_id"]
    )
    
    return {"message": "Preparación iniciada", "checklist": checklist}

@router.patch("/api/oportunidades/{expediente}/checklist/documento")
async def update_checklist_documento(
    expediente: str,
    data: DocumentoUpdate,
    current_user: dict = Depends(require_operador)
):
    """Actualizar documento del checklist."""
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    checklist = op.get("checklist")
    if not checklist:
        raise HTTPException(status_code=400, detail="No hay checklist. Inicia preparación primero.")
    
    checklist = actualizar_documento(checklist, data.doc_id, data.completado, data.archivo)
    progreso = calcular_progreso(checklist)
    
    update_oportunidad(expediente, {"checklist": checklist}, current_user["user_id"])
    
    return {"checklist": checklist, "progreso": progreso}

@router.patch("/api/oportunidades/{expediente}/checklist/hito")
async def update_checklist_hito(
    expediente: str,
    data: HitoUpdate,
    current_user: dict = Depends(require_operador)
):
    """Actualizar hito del checklist."""
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    checklist = op.get("checklist")
    if not checklist:
        raise HTTPException(status_code=400, detail="No hay checklist")
    
    checklist = actualizar_hito(checklist, data.hito_id, data.completado)
    progreso = calcular_progreso(checklist)
    
    update_oportunidad(expediente, {"checklist": checklist}, current_user["user_id"])
    
    return {"checklist": checklist, "progreso": progreso}

@router.post("/api/oportunidades/{expediente}/checklist/documento-custom")
async def add_documento_custom(
    expediente: str,
    data: DocumentoCustom,
    current_user: dict = Depends(require_operador)
):
    """Agregar documento personalizado al checklist."""
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    checklist = op.get("checklist")
    if not checklist:
        raise HTTPException(status_code=400, detail="No hay checklist")
    
    checklist = agregar_documento_custom(checklist, data.nombre, data.requerido)
    
    update_oportunidad(expediente, {"checklist": checklist}, current_user["user_id"])
    
    return {"checklist": checklist}

@router.get("/api/oportunidades/{expediente}/checklist/progreso")
async def get_progreso(
    expediente: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener progreso del checklist."""
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    checklist = op.get("checklist")
    if not checklist:
        return {"progreso": None, "mensaje": "Sin checklist"}
    
    return {"progreso": calcular_progreso(checklist)}

# === Análisis IA ===

class AnalisisRequest(BaseModel):
    texto: Optional[str] = None
    provider: str = "auto"

@router.post("/api/oportunidades/{expediente}/analizar-ia")
async def analizar_oportunidad_ia(
    expediente: str,
    data: Optional[AnalisisRequest] = None,
    current_user: dict = Depends(require_operador)
):
    """Analizar oportunidad con IA."""
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    # Obtener texto a analizar
    texto = None
    if data and data.texto:
        texto = data.texto
    elif op.get("url_pliego"):
        texto = await extraer_texto_pliego(op["url_pliego"])
    
    if not texto:
        # Usar título + descripción como fallback
        texto = f"{op.get('titulo', '')} {op.get('descripcion', '')}"
    
    if len(texto) < 50:
        raise HTTPException(status_code=400, detail="No hay suficiente texto para analizar")
    
    provider = data.provider if data else "auto"
    resultado = await analizar_pliego(texto, provider)
    
    if resultado.get("procesado"):
        update_oportunidad(expediente, {"analisis_ia": resultado}, current_user["user_id"])
    
    return resultado

# === Alertas ===

@router.get("/api/oportunidades/alertas")
async def get_alertas(
    current_user: dict = Depends(get_current_user)
):
    """Obtener oportunidades urgentes."""
    # Licitaciones con pocos días y en preparación
    result = get_oportunidades(
        tipo="licitacion",
        estado="en_preparacion",
        dias_max=7,
        limit=50,
        current_user_id=current_user["user_id"]
    )
    
    urgentes = result.get("items", [])
    
    # Licitaciones nuevas oro/plata sin asignar
    result_nuevas = get_oportunidades(
        tipo="licitacion",
        estado="nueva",
        propietario="null",
        nivel="oro",
        limit=20,
        current_user_id=current_user["user_id"]
    )
    
    sin_asignar = result_nuevas.get("items", [])
    
    return {
        "urgentes": urgentes,
        "urgentes_count": len(urgentes),
        "sin_asignar_oro": sin_asignar,
        "sin_asignar_count": len(sin_asignar)
    }

# === Conversión a Lead ===

@router.post("/api/oportunidades/{expediente}/convertir-lead")
async def convertir_a_lead(
    expediente: str,
    current_user: dict = Depends(require_operador)
):
    """Convertir adjudicación en lead."""
    from app.services.oportunidades import oportunidades_collection
    from pymongo import MongoClient
    import os
    
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client.srs_crm
    leads_collection = db.leads
    
    op = get_oportunidad_by_expediente(expediente)
    if not op:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    if op.get("tipo") != "adjudicacion":
        raise HTTPException(status_code=400, detail="Solo adjudicaciones pueden convertirse en leads")
    
    adjudicatario = op.get("adjudicatario")
    if not adjudicatario or not adjudicatario.get("nombre"):
        raise HTTPException(status_code=400, detail="No hay datos de adjudicatario")
    
    # Crear lead
    from datetime import datetime, timezone
    import uuid
    
    lead_data = {
        "lead_id": f"lead_{uuid.uuid4().hex[:12]}",
        "empresa": adjudicatario.get("nombre"),
        "nif": adjudicatario.get("nif"),
        "contacto": adjudicatario.get("contacto", {}),
        "fuente": "PLACSP",
        "fuente_detalle": f"Adjudicación {expediente}",
        "oportunidad_origen": expediente,
        "importe_contrato": op.get("importe"),
        "sector": op.get("sector"),
        "estado": "nuevo",
        "propietario": current_user["user_id"],
        "creado_at": datetime.now(timezone.utc),
        "creado_por": current_user["user_id"],
        "notas": f"Lead generado desde adjudicación: {op.get('titulo', '')}"
    }
    
    result = leads_collection.insert_one(lead_data)
    lead_data["_id"] = str(result.inserted_id)
    
    # Marcar oportunidad como convertida
    update_oportunidad(
        expediente,
        {"estado": "convertida", "lead_id": lead_data["lead_id"]},
        current_user["user_id"]
    )
    
    return {"message": "Lead creado", "lead": lead_data}

# === Export ===

@router.get("/api/oportunidades/export")
async def export_oportunidades(
    tipo: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    nivel: Optional[str] = Query(None),
    formato: str = Query("xlsx", description="xlsx | csv"),
    current_user: dict = Depends(get_current_user)
):
    """Exportar oportunidades a Excel/CSV."""
    result = get_oportunidades(
        tipo=tipo,
        sector=sector,
        estado=estado,
        nivel=nivel,
        limit=1000,
        current_user_id=current_user["user_id"]
    )
    
    oportunidades = result.get("items", [])
    
    if not oportunidades:
        raise HTTPException(status_code=404, detail="No hay oportunidades para exportar")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    if formato == "csv":
        content = export_to_csv(oportunidades)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=oportunidades_{timestamp}.csv"}
        )
    else:
        content = export_to_excel(oportunidades)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=oportunidades_{timestamp}.xlsx"}
        )
