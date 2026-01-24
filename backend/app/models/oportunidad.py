from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class TipoEnum(str, Enum):
    adjudicacion = "adjudicacion"
    licitacion = "licitacion"

class SectorEnum(str, Enum):
    it = "it"
    drones = "drones"
    energia = "energia"

class NivelEnum(str, Enum):
    oro = "oro"
    plata = "plata"
    bronce = "bronce"
    descarte = "descarte"

# === Estados por tipo ===

ESTADOS_LICITACION = ["nueva", "revisada", "descartada", "en_preparacion", "enviada", "adjudicada", "no_adjudicada"]
ESTADOS_ADJUDICACION = ["nueva", "revisada", "descartada", "contactando", "convertida"]

# === Sub-models ===

class Fechas(BaseModel):
    publicacion: Optional[datetime] = None
    limite: Optional[datetime] = None
    adjudicacion: Optional[datetime] = None
    fin_contrato: Optional[datetime] = None
    deteccion: Optional[datetime] = None
    actualizacion: Optional[datetime] = None

class Contacto(BaseModel):
    telefono: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None
    direccion: Optional[str] = None

class DatosEmpresa(BaseModel):
    empleados: Optional[int] = None
    facturacion: Optional[float] = None
    cnae: Optional[str] = None
    fecha_constitucion: Optional[datetime] = None

class Adjudicatario(BaseModel):
    nombre: Optional[str] = None
    nif: Optional[str] = None
    es_pyme: Optional[bool] = None
    contacto: Optional[Contacto] = None
    datos_empresa: Optional[DatosEmpresa] = None

class ScoringDesglose(BaseModel):
    cpv: int = 0
    keywords: int = 0
    importe: int = 0
    urgencia: int = 0

class Scoring(BaseModel):
    total: int = 0
    nivel: str = "descarte"
    desglose: Optional[ScoringDesglose] = None

class CPVMatch(BaseModel):
    cpv: str
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_match: Optional[str] = None

class Analisis(BaseModel):
    cpv_matches: List[CPVMatch] = []
    keywords: List[str] = []
    categoria: Optional[str] = None
    indicadores_urgencia: List[str] = []

class DocumentoChecklist(BaseModel):
    id: str
    nombre: str
    requerido: bool = False
    completado: bool = False
    archivo: Optional[str] = None
    fecha_completado: Optional[datetime] = None

class HitoChecklist(BaseModel):
    id: str
    nombre: str
    completado: bool = False
    fecha_completado: Optional[datetime] = None

class Checklist(BaseModel):
    documentos: List[DocumentoChecklist] = []
    hitos: List[HitoChecklist] = []

class AnalisisIA(BaseModel):
    procesado: bool = False
    procesado_at: Optional[datetime] = None
    pain_score: Optional[int] = None
    resumen: Optional[str] = None
    puntos_dolor: List[str] = []
    requisitos_clave: List[str] = []
    recomendacion: Optional[str] = None

class HistorialEntry(BaseModel):
    campo: str
    valor_anterior: Optional[Any] = None
    valor_nuevo: Optional[Any] = None
    usuario: Optional[str] = None
    fecha: datetime

# === Main Models ===

class OportunidadBase(BaseModel):
    expediente: str
    tipo: TipoEnum
    sector: SectorEnum
    estado_placsp: Optional[str] = None
    titulo: str
    descripcion: Optional[str] = None
    cpv: Optional[str] = None
    cpv_descripcion: Optional[str] = None
    importe: Optional[float] = None
    organo_contratacion: Optional[str] = None
    url_licitacion: Optional[str] = None
    url_pliego: Optional[str] = None

class OportunidadCreate(OportunidadBase):
    fechas: Optional[Fechas] = None
    adjudicatario: Optional[Adjudicatario] = None
    scoring: Optional[Scoring] = None
    analisis: Optional[Analisis] = None
    estado: str = "nueva"

class OportunidadUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    propietario: Optional[str] = None
    notas: Optional[str] = None
    adjudicatario: Optional[Adjudicatario] = None
    checklist: Optional[Checklist] = None
    analisis_ia: Optional[AnalisisIA] = None

class OportunidadResponse(OportunidadBase):
    fechas: Optional[Fechas] = None
    dias_restantes: Optional[int] = None
    adjudicatario: Optional[Adjudicatario] = None
    scoring: Optional[Scoring] = None
    analisis: Optional[Analisis] = None
    estado: str = "nueva"
    propietario: Optional[str] = None
    propietario_nombre: Optional[str] = None
    notas: Optional[str] = None
    checklist: Optional[Checklist] = None
    analisis_ia: Optional[AnalisisIA] = None
    lead_id: Optional[str] = None
    creado_at: Optional[datetime] = None
    actualizado_at: Optional[datetime] = None

class OportunidadListResponse(BaseModel):
    total: int
    page: int
    pages: int
    items: List[OportunidadResponse]

class OportunidadStats(BaseModel):
    total: int
    por_estado: dict
    por_nivel: dict
    por_categoria: dict
    score_promedio: float
    importe_total: float
    urgentes: int

class EstadoUpdate(BaseModel):
    estado: str

class AsignarUpdate(BaseModel):
    propietario: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
