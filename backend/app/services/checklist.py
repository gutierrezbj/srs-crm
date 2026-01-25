"""Gestión de checklist de preparación de licitaciones."""
from datetime import datetime, timezone
from typing import Optional
import uuid

# Templates de documentos por defecto
DOCUMENTOS_DEFAULT = [
    {"id": "doc_solvencia_tecnica", "nombre": "Solvencia técnica", "requerido": True},
    {"id": "doc_solvencia_economica", "nombre": "Solvencia económica", "requerido": True},
    {"id": "doc_declaracion_responsable", "nombre": "Declaración responsable", "requerido": True},
    {"id": "doc_memoria_tecnica", "nombre": "Memoria técnica", "requerido": True},
    {"id": "doc_oferta_economica", "nombre": "Oferta económica", "requerido": True},
    {"id": "doc_certificado_ens", "nombre": "Certificado ENS", "requerido": False},
    {"id": "doc_iso_27001", "nombre": "Certificado ISO 27001", "requerido": False},
    {"id": "doc_referencias", "nombre": "Referencias/Experiencia", "requerido": False}
]

HITOS_DEFAULT = [
    {"id": "hito_analisis_pliego", "nombre": "Análisis del pliego"},
    {"id": "hito_equipo_asignado", "nombre": "Equipo de trabajo asignado"},
    {"id": "hito_borrador_tecnico", "nombre": "Borrador memoria técnica"},
    {"id": "hito_revision_juridica", "nombre": "Revisión jurídica"},
    {"id": "hito_aprobacion_direccion", "nombre": "Aprobación dirección"},
    {"id": "hito_firma_documentos", "nombre": "Firma de documentos"},
    {"id": "hito_presentacion", "nombre": "Presentación en plataforma"}
]

def crear_checklist_default() -> dict:
    """Crear checklist con valores por defecto."""
    return {
        "documentos": [
            {**doc, "completado": False, "archivo": None, "fecha_completado": None}
            for doc in DOCUMENTOS_DEFAULT
        ],
        "hitos": [
            {**hito, "completado": False, "fecha_completado": None}
            for hito in HITOS_DEFAULT
        ]
    }

def actualizar_documento(checklist: dict, doc_id: str, completado: bool, archivo: str = None) -> dict:
    """Marcar documento como completado."""
    for doc in checklist.get("documentos", []):
        if doc["id"] == doc_id:
            doc["completado"] = completado
            doc["archivo"] = archivo
            doc["fecha_completado"] = datetime.now(timezone.utc) if completado else None
            break
    return checklist

def actualizar_hito(checklist: dict, hito_id: str, completado: bool) -> dict:
    """Marcar hito como completado."""
    for hito in checklist.get("hitos", []):
        if hito["id"] == hito_id:
            hito["completado"] = completado
            hito["fecha_completado"] = datetime.now(timezone.utc) if completado else None
            break
    return checklist

def calcular_progreso(checklist: dict) -> dict:
    """Calcular progreso del checklist."""
    docs = checklist.get("documentos", [])
    hitos = checklist.get("hitos", [])
    
    docs_requeridos = [d for d in docs if d.get("requerido")]
    docs_completados = [d for d in docs if d.get("completado")]
    docs_requeridos_completados = [d for d in docs_requeridos if d.get("completado")]
    
    hitos_completados = [h for h in hitos if h.get("completado")]
    
    total_items = len(docs) + len(hitos)
    completados = len(docs_completados) + len(hitos_completados)
    
    return {
        "porcentaje": round((completados / total_items * 100) if total_items > 0 else 0),
        "documentos_total": len(docs),
        "documentos_completados": len(docs_completados),
        "documentos_requeridos_pendientes": len(docs_requeridos) - len(docs_requeridos_completados),
        "hitos_total": len(hitos),
        "hitos_completados": len(hitos_completados),
        "listo_para_enviar": len(docs_requeridos_completados) == len(docs_requeridos)
    }

def agregar_documento_custom(checklist: dict, nombre: str, requerido: bool = False) -> dict:
    """Agregar documento personalizado al checklist."""
    nuevo_doc = {
        "id": f"doc_custom_{uuid.uuid4().hex[:8]}",
        "nombre": nombre,
        "requerido": requerido,
        "completado": False,
        "archivo": None,
        "fecha_completado": None
    }
    checklist.setdefault("documentos", []).append(nuevo_doc)
    return checklist
