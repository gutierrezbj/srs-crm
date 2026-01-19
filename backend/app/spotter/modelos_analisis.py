#!/usr/bin/env python3
"""
Modelos de Datos para Análisis de Oportunidades - SpotterSRS v2

Este módulo define las estructuras de datos (dataclasses) que coinciden exactamente
con el JSON de salida del prompt SpotterSRS v2. Permite parsear la respuesta de la IA
y trabajar con objetos Python tipados.

Versión: 2.0.0
Alineado con: prompt_spotter_v2.py
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json


# ═══════════════════════════════════════════════════════════════════════════════
# OPORTUNIDAD (Datos básicos del contrato)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DuracionContrato:
    """Duración y prórrogas del contrato"""
    meses: int = 0
    prorrogable: bool = False
    meses_prorroga: int = 0


@dataclass
class Oportunidad:
    """Datos básicos de la oportunidad/contrato"""
    id_expediente: str = ""
    titulo: str = ""
    resumen_ejecutivo: str = ""  # máx 200 caracteres
    fecha_adjudicacion: Optional[str] = None  # YYYY-MM-DD
    fecha_formalizacion: Optional[str] = None
    fecha_inicio_ejecucion: Optional[str] = None
    duracion_contrato: Optional[DuracionContrato] = None


# ═══════════════════════════════════════════════════════════════════════════════
# ADJUDICATARIO (Nuestro cliente potencial)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CapacidadInterna:
    """Evaluación de capacidad interna del adjudicatario"""
    cableado: str = "desconocido"  # si|no|probable|improbable|desconocido
    field_services: str = "desconocido"
    cloud: str = "desconocido"
    seguridad: str = "desconocido"
    helpdesk: str = "desconocido"


@dataclass
class Adjudicatario:
    """Información del adjudicatario (empresa que ganó el contrato)"""
    nombre: str = ""
    cif: Optional[str] = None
    es_ute: bool = False
    miembros_ute: Optional[List[str]] = None
    perfil_empresa: str = "desconocido"  # integrador|consultora|telco|fabricante|generalista|especialista|desconocido
    tamaño_estimado: str = "desconocido"  # grande|mediana|pequeña|desconocido
    capacidad_interna_estimada: Optional[CapacidadInterna] = None
    probabilidad_subcontratacion: str = "media"  # alta|media|baja
    razon_subcontratacion: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# CLIENTE FINAL (Organismo contratante)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ClienteFinal:
    """Información del organismo que contrata (cliente final del adjudicatario)"""
    nombre: str = ""
    cif: Optional[str] = None
    tipo: str = ""  # AGE|CCAA|local|universidad|sanidad|otro
    sector: str = ""
    comunidad_autonoma: str = ""
    provincia: str = ""
    localidad: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# ECONÓMICO
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ValorEstimadoSubcontratacion:
    """Estimación del valor de subcontratación para SRS"""
    minimo: float = 0.0
    maximo: float = 0.0
    justificacion: str = ""


@dataclass
class Economico:
    """Datos económicos del contrato"""
    importe_adjudicacion: float = 0.0
    importe_adjudicacion_con_iva: float = 0.0
    presupuesto_base: float = 0.0
    baja_porcentaje: Optional[float] = None
    valor_estimado_subcontratacion: Optional[ValorEstimadoSubcontratacion] = None


# ═══════════════════════════════════════════════════════════════════════════════
# COMPONENTES IT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UbicacionComponente:
    """Ubicación geográfica de un componente IT"""
    localidad: Optional[str] = None
    provincia: str = ""
    comunidad: str = ""
    zona_srs: str = ""  # base|cercana|expansion


@dataclass
class CoberturaGeografica:
    """Cobertura geográfica requerida para un componente"""
    ambito: str = ""  # local|provincial|autonomico|nacional|multisede
    num_ubicaciones: int = 1
    provincias_implicadas: List[str] = field(default_factory=list)
    requiere_desplazamiento: bool = False


@dataclass
class ComponenteIT:
    """Componente IT detectado en el pliego"""
    tipo: str = ""  # infraestructura|software|servicios|comunicaciones|seguridad
    subtipo: str = ""  # del catálogo SRS
    nombre: str = ""
    descripcion: str = ""
    urgencia: str = "media"  # critica|alta|media|baja
    cantidad: Optional[str] = None
    ubicaciones: List[UbicacionComponente] = field(default_factory=list)
    cobertura_geografica: Optional[CoberturaGeografica] = None
    tecnologias_especificas: List[str] = field(default_factory=list)
    fabricantes_mencionados: List[str] = field(default_factory=list)
    normativas_aplicables: List[str] = field(default_factory=list)
    srs_capacidad: str = "media"  # alta|media|baja|no
    srs_cobertura: str = "total"  # total|parcial|requiere_partner
    extracto_pliego: str = ""  # máx 500 chars
    pagina: Optional[int] = None
    confianza: float = 0.8


# ═══════════════════════════════════════════════════════════════════════════════
# DOLORES (Pain points del adjudicatario)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ImpactoNegocio:
    """Impacto del dolor en el negocio"""
    descripcion: str = ""
    nivel: str = "medio"  # critico|alto|medio|bajo
    cuantificable: bool = False
    estimacion: Optional[str] = None


@dataclass
class UrgenciaTemporal:
    """Urgencia temporal del dolor"""
    fecha_limite: Optional[str] = None  # YYYY-MM-DD
    dias_restantes: Optional[int] = None
    margen_maniobra: str = "moderado"  # escaso|moderado|amplio


@dataclass
class SRSSolucion:
    """Solución que SRS puede ofrecer para el dolor"""
    servicio_principal: str = ""  # del catálogo
    servicios_complementarios: List[str] = field(default_factory=list)
    argumento_venta: str = ""


@dataclass
class Dolor:
    """Dolor/problema detectado que SRS puede resolver"""
    categoria: str = ""  # temporal|tecnico|cumplimiento|recursos|economico|operativo|estrategico
    subcategoria: str = ""  # plazo_ajustado|falta_personal|certificacion|presupuesto|capacidad|conocimiento|regulatorio|obsolescencia|integracion
    severidad: str = "media"  # critica|alta|media|baja
    descripcion: str = ""
    sintomas_detectados: List[str] = field(default_factory=list)
    impacto_negocio: Optional[ImpactoNegocio] = None
    urgencia_temporal: Optional[UrgenciaTemporal] = None
    extracto_pliego: str = ""  # máx 500 chars
    pagina: Optional[int] = None
    srs_solucion: Optional[SRSSolucion] = None
    confianza: float = 0.8


# ═══════════════════════════════════════════════════════════════════════════════
# REQUISITOS DE SOLVENCIA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SolvenciaEconomica:
    """Requisitos de solvencia económica"""
    facturacion_minima: Optional[float] = None
    patrimonio_neto: Optional[float] = None
    ratio_endeudamiento: Optional[float] = None
    seguro_rc: Optional[float] = None
    otros: List[str] = field(default_factory=list)


@dataclass
class SolvenciaTecnica:
    """Requisitos de solvencia técnica"""
    proyectos_similares: Optional[int] = None
    importe_proyectos: Optional[float] = None
    certificaciones_requeridas: List[str] = field(default_factory=list)
    personal_minimo: Optional[int] = None
    titulaciones_requeridas: List[str] = field(default_factory=list)
    otros: List[str] = field(default_factory=list)


@dataclass
class SRSCumple:
    """Evaluación de si SRS cumple los requisitos"""
    economica: bool = True
    tecnica: bool = True
    notas: Optional[str] = None


@dataclass
class RequisitosSolvencia:
    """Requisitos de solvencia del contrato"""
    economica: Optional[SolvenciaEconomica] = None
    tecnica: Optional[SolvenciaTecnica] = None
    srs_cumple: Optional[SRSCumple] = None


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACTOS EXTRAÍDOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContactoExtraido:
    """Contacto extraído del pliego"""
    tipo_entidad: str = ""  # adjudicatario|cliente_final|ute_miembro
    rol: str = ""  # decisor|tecnico|administrativo
    nombre: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fuente: str = ""  # documento y página
    confianza: float = 0.5


# ═══════════════════════════════════════════════════════════════════════════════
# ALERTAS Y RED FLAGS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Alerta:
    """Alerta importante para el comercial"""
    tipo: str = ""  # temporal|economico|logistico|tecnico|legal
    prioridad: str = "media"  # alta|media|baja
    mensaje: str = ""
    fecha_relevante: Optional[str] = None  # YYYY-MM-DD


@dataclass
class RedFlag:
    """Señal de alerta que puede afectar la oportunidad"""
    tipo: str = ""  # presupuesto_bajo|plazo_irreal|requisitos_excesivos|competencia_fuerte|otro
    descripcion: str = ""
    impacto: str = "precaucion"  # descarta|reduce_prioridad|precaucion


# ═══════════════════════════════════════════════════════════════════════════════
# COMPETENCIA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Competencia:
    """Análisis de competencia"""
    incumbente_anterior: Optional[str] = None
    motivo_cambio: Optional[str] = None
    competidores_probables: List[str] = field(default_factory=list)
    ventaja_srs: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN OPERADOR (Lo más importante para el comercial)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ScoreDesglose:
    """Desglose del score de la oportunidad"""
    alineacion_servicios_srs: int = 0  # 0-25
    urgencia_temporal: int = 0  # 0-20
    volumen_economico: int = 0  # 0-15
    intensidad_dolor: int = 0  # 0-20
    cobertura_geografica: int = 0  # 0-10
    probabilidad_subcontratacion: int = 0  # 0-10


@dataclass
class En30Segundos:
    """Lo que el comercial necesita saber en 30 segundos"""
    que_es: str = ""  # máx 100 chars
    por_que_interesa: str = ""  # máx 150 chars
    por_que_ahora: str = ""  # máx 100 chars


@dataclass
class ServicioSRSAplicable:
    """Servicio SRS que aplica a la oportunidad"""
    servicio: str = ""
    encaje: str = "medio"  # perfecto|alto|medio
    valor_estimado: str = ""


@dataclass
class GanchoInicial:
    """Mensajes de apertura para contactar al adjudicatario"""
    whatsapp: str = ""  # mensaje corto, directo
    email_asunto: str = ""
    llamada: str = ""  # pitch 30 segundos


@dataclass
class ObjecionRespuesta:
    """Objeción probable y cómo responderla"""
    objecion: str = ""
    respuesta: str = ""


@dataclass
class ResumenOperador:
    """Resumen ejecutivo para el operador comercial"""
    nivel_oportunidad: str = "bronce"  # oro|plata|bronce|descartar
    score_total: int = 0  # 0-100
    score_desglose: Optional[ScoreDesglose] = None
    en_30_segundos: Optional[En30Segundos] = None
    dolor_principal: str = ""
    dolores_secundarios: List[str] = field(default_factory=list)
    servicios_srs_aplicables: List[ServicioSRSAplicable] = field(default_factory=list)
    gancho_inicial: Optional[GanchoInicial] = None
    puntos_clave_conversacion: List[str] = field(default_factory=list)
    propuesta_valor: List[str] = field(default_factory=list)
    preguntas_cualificacion: List[str] = field(default_factory=list)
    objeciones_probables: List[ObjecionRespuesta] = field(default_factory=list)
    siguiente_accion: str = ""
    fecha_limite_contacto: Optional[str] = None  # YYYY-MM-DD


# ═══════════════════════════════════════════════════════════════════════════════
# METADATA DEL ANÁLISIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetadataAnalisisIA:
    """Metadata del análisis realizado por la IA"""
    confianza_global: float = 0.8
    calidad_documento: str = "media"  # alta|media|baja
    paginas_analizadas: int = 0
    paginas_relevantes: List[int] = field(default_factory=list)
    datos_incompletos: List[str] = field(default_factory=list)
    requiere_revision_humana: bool = False
    motivo_revision: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# METADATA COMPLETA DE TRAZABILIDAD
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DocumentoProcesado:
    """Documento procesado en el análisis"""
    tipo: str = ""  # pliego_tecnico, pliego_administrativo, anexo_tecnico
    nombre_archivo: str = ""
    url_origen: str = ""
    hash_sha256: str = ""
    paginas_totales: int = 0
    palabras_totales: int = 0


@dataclass
class ProcesamientoIA:
    """Metadata del procesamiento con IA"""
    proveedor: str = ""  # anthropic, openai, gemini
    modelo: str = ""
    version_prompt: str = "2.0.0"
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_totales: int = 0
    coste_estimado_usd: float = 0.0
    tiempo_ms: int = 0


@dataclass
class AuditoriaComercial:
    """Auditoría de acciones comerciales sobre la oportunidad"""
    estado_comercial: str = "pendiente_revision"  # pendiente_revision|en_contacto|propuesta_enviada|ganado|perdido|descartado
    fecha_primera_vista: Optional[str] = None
    fecha_contacto_realizado: Optional[str] = None
    resultado_contacto: Optional[str] = None
    notas_operador: List[str] = field(default_factory=list)


@dataclass
class MetadataCompleta:
    """Metadata completa de trazabilidad del análisis"""
    id_analisis: str = ""
    timestamp_inicio: str = ""
    timestamp_fin: str = ""
    tiempo_total_segundos: float = 0.0
    documentos_procesados: List[DocumentoProcesado] = field(default_factory=list)
    procesamiento_ia: Optional[ProcesamientoIA] = None
    url_pliego: str = ""
    expediente: str = ""
    auditoria: Optional[AuditoriaComercial] = None


# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISIS COMPLETO (Estructura raíz)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AnalisisComercial:
    """
    Estructura completa del análisis de una oportunidad.
    Coincide exactamente con el JSON de salida del prompt SpotterSRS v2.
    """
    # Datos del contrato
    oportunidad: Optional[Oportunidad] = None
    adjudicatario: Optional[Adjudicatario] = None
    cliente_final: Optional[ClienteFinal] = None
    economico: Optional[Economico] = None

    # Componentes y dolores detectados
    componentes_it: List[ComponenteIT] = field(default_factory=list)
    dolores: List[Dolor] = field(default_factory=list)

    # Requisitos
    requisitos_solvencia: Optional[RequisitosSolvencia] = None

    # Tecnologías y certificaciones
    tecnologias_mencionadas: List[str] = field(default_factory=list)
    fabricantes_mencionados: List[str] = field(default_factory=list)
    certificaciones_requeridas: List[str] = field(default_factory=list)

    # Contactos
    contactos_extraidos: List[ContactoExtraido] = field(default_factory=list)

    # Alertas y riesgos
    alertas: List[Alerta] = field(default_factory=list)
    red_flags: List[RedFlag] = field(default_factory=list)

    # Competencia
    competencia: Optional[Competencia] = None

    # Resumen para el comercial
    resumen_operador: Optional[ResumenOperador] = None

    # Metadata del análisis IA
    metadata_analisis: Optional[MetadataAnalisisIA] = None

    # Metadata de trazabilidad (añadida después del análisis)
    metadata: Optional[MetadataCompleta] = None

    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización JSON"""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convierte a JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CONSTRUCCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def construir_desde_json(data: Dict) -> AnalisisComercial:
    """
    Construye un AnalisisComercial a partir del JSON de respuesta de la IA.
    Maneja valores por defecto para campos faltantes.
    """

    # Oportunidad
    opp_data = data.get("oportunidad", {})
    duracion_data = opp_data.get("duracion_contrato", {})
    oportunidad = Oportunidad(
        id_expediente=opp_data.get("id_expediente", ""),
        titulo=opp_data.get("titulo", ""),
        resumen_ejecutivo=opp_data.get("resumen_ejecutivo", ""),
        fecha_adjudicacion=opp_data.get("fecha_adjudicacion"),
        fecha_formalizacion=opp_data.get("fecha_formalizacion"),
        fecha_inicio_ejecucion=opp_data.get("fecha_inicio_ejecucion"),
        duracion_contrato=DuracionContrato(
            meses=duracion_data.get("meses", 0),
            prorrogable=duracion_data.get("prorrogable", False),
            meses_prorroga=duracion_data.get("meses_prorroga", 0)
        ) if duracion_data else None
    )

    # Adjudicatario
    adj_data = data.get("adjudicatario", {})
    cap_data = adj_data.get("capacidad_interna_estimada", {})
    adjudicatario = Adjudicatario(
        nombre=adj_data.get("nombre", ""),
        cif=adj_data.get("cif"),
        es_ute=adj_data.get("es_ute", False),
        miembros_ute=adj_data.get("miembros_ute"),
        perfil_empresa=adj_data.get("perfil_empresa", "desconocido"),
        tamaño_estimado=adj_data.get("tamaño_estimado", "desconocido"),
        capacidad_interna_estimada=CapacidadInterna(
            cableado=cap_data.get("cableado", "desconocido"),
            field_services=cap_data.get("field_services", "desconocido"),
            cloud=cap_data.get("cloud", "desconocido"),
            seguridad=cap_data.get("seguridad", "desconocido"),
            helpdesk=cap_data.get("helpdesk", "desconocido")
        ) if cap_data else None,
        probabilidad_subcontratacion=adj_data.get("probabilidad_subcontratacion", "media"),
        razon_subcontratacion=adj_data.get("razon_subcontratacion", "")
    )

    # Cliente final
    cli_data = data.get("cliente_final", {})
    cliente_final = ClienteFinal(
        nombre=cli_data.get("nombre", ""),
        cif=cli_data.get("cif"),
        tipo=cli_data.get("tipo", ""),
        sector=cli_data.get("sector", ""),
        comunidad_autonoma=cli_data.get("comunidad_autonoma", ""),
        provincia=cli_data.get("provincia", ""),
        localidad=cli_data.get("localidad")
    )

    # Económico
    eco_data = data.get("economico", {})
    val_sub_data = eco_data.get("valor_estimado_subcontratacion", {})
    economico = Economico(
        importe_adjudicacion=eco_data.get("importe_adjudicacion", 0),
        importe_adjudicacion_con_iva=eco_data.get("importe_adjudicacion_con_iva", 0),
        presupuesto_base=eco_data.get("presupuesto_base", 0),
        baja_porcentaje=eco_data.get("baja_porcentaje"),
        valor_estimado_subcontratacion=ValorEstimadoSubcontratacion(
            minimo=val_sub_data.get("minimo", 0),
            maximo=val_sub_data.get("maximo", 0),
            justificacion=val_sub_data.get("justificacion", "")
        ) if val_sub_data else None
    )

    # Componentes IT
    componentes_it = []
    for comp_data in data.get("componentes_it", []):
        ubicaciones = []
        for ub_data in comp_data.get("ubicaciones", []):
            ubicaciones.append(UbicacionComponente(
                localidad=ub_data.get("localidad"),
                provincia=ub_data.get("provincia", ""),
                comunidad=ub_data.get("comunidad", ""),
                zona_srs=ub_data.get("zona_srs", "")
            ))

        cob_data = comp_data.get("cobertura_geografica", {})
        cobertura = CoberturaGeografica(
            ambito=cob_data.get("ambito", ""),
            num_ubicaciones=cob_data.get("num_ubicaciones", 1),
            provincias_implicadas=cob_data.get("provincias_implicadas", []),
            requiere_desplazamiento=cob_data.get("requiere_desplazamiento", False)
        ) if cob_data else None

        componentes_it.append(ComponenteIT(
            tipo=comp_data.get("tipo", ""),
            subtipo=comp_data.get("subtipo", ""),
            nombre=comp_data.get("nombre", ""),
            descripcion=comp_data.get("descripcion", ""),
            urgencia=comp_data.get("urgencia", "media"),
            cantidad=comp_data.get("cantidad"),
            ubicaciones=ubicaciones,
            cobertura_geografica=cobertura,
            tecnologias_especificas=comp_data.get("tecnologias_especificas", []),
            fabricantes_mencionados=comp_data.get("fabricantes_mencionados", []),
            normativas_aplicables=comp_data.get("normativas_aplicables", []),
            srs_capacidad=comp_data.get("srs_capacidad", "media"),
            srs_cobertura=comp_data.get("srs_cobertura", "total"),
            extracto_pliego=comp_data.get("extracto_pliego", ""),
            pagina=comp_data.get("pagina"),
            confianza=comp_data.get("confianza", 0.8)
        ))

    # Dolores
    dolores = []
    for dolor_data in data.get("dolores", []):
        impacto_data = dolor_data.get("impacto_negocio", {})
        impacto = ImpactoNegocio(
            descripcion=impacto_data.get("descripcion", ""),
            nivel=impacto_data.get("nivel", "medio"),
            cuantificable=impacto_data.get("cuantificable", False),
            estimacion=impacto_data.get("estimacion")
        ) if impacto_data else None

        urgencia_data = dolor_data.get("urgencia_temporal", {})
        urgencia = UrgenciaTemporal(
            fecha_limite=urgencia_data.get("fecha_limite"),
            dias_restantes=urgencia_data.get("dias_restantes"),
            margen_maniobra=urgencia_data.get("margen_maniobra", "moderado")
        ) if urgencia_data else None

        solucion_data = dolor_data.get("srs_solucion", {})
        solucion = SRSSolucion(
            servicio_principal=solucion_data.get("servicio_principal", ""),
            servicios_complementarios=solucion_data.get("servicios_complementarios", []),
            argumento_venta=solucion_data.get("argumento_venta", "")
        ) if solucion_data else None

        dolores.append(Dolor(
            categoria=dolor_data.get("categoria", ""),
            subcategoria=dolor_data.get("subcategoria", ""),
            severidad=dolor_data.get("severidad", "media"),
            descripcion=dolor_data.get("descripcion", ""),
            sintomas_detectados=dolor_data.get("sintomas_detectados", []),
            impacto_negocio=impacto,
            urgencia_temporal=urgencia,
            extracto_pliego=dolor_data.get("extracto_pliego", ""),
            pagina=dolor_data.get("pagina"),
            srs_solucion=solucion,
            confianza=dolor_data.get("confianza", 0.8)
        ))

    # Requisitos de solvencia
    req_data = data.get("requisitos_solvencia", {})
    eco_solv_data = req_data.get("economica", {})
    tec_solv_data = req_data.get("tecnica", {})
    cumple_data = req_data.get("srs_cumple", {})

    requisitos_solvencia = RequisitosSolvencia(
        economica=SolvenciaEconomica(
            facturacion_minima=eco_solv_data.get("facturacion_minima"),
            patrimonio_neto=eco_solv_data.get("patrimonio_neto"),
            ratio_endeudamiento=eco_solv_data.get("ratio_endeudamiento"),
            seguro_rc=eco_solv_data.get("seguro_rc"),
            otros=eco_solv_data.get("otros", [])
        ) if eco_solv_data else None,
        tecnica=SolvenciaTecnica(
            proyectos_similares=tec_solv_data.get("proyectos_similares"),
            importe_proyectos=tec_solv_data.get("importe_proyectos"),
            certificaciones_requeridas=tec_solv_data.get("certificaciones_requeridas", []),
            personal_minimo=tec_solv_data.get("personal_minimo"),
            titulaciones_requeridas=tec_solv_data.get("titulaciones_requeridas", []),
            otros=tec_solv_data.get("otros", [])
        ) if tec_solv_data else None,
        srs_cumple=SRSCumple(
            economica=cumple_data.get("economica", True),
            tecnica=cumple_data.get("tecnica", True),
            notas=cumple_data.get("notas")
        ) if cumple_data else None
    ) if req_data else None

    # Contactos extraídos
    contactos = []
    for cont_data in data.get("contactos_extraidos", []):
        contactos.append(ContactoExtraido(
            tipo_entidad=cont_data.get("tipo_entidad", ""),
            rol=cont_data.get("rol", ""),
            nombre=cont_data.get("nombre"),
            cargo=cont_data.get("cargo"),
            departamento=cont_data.get("departamento"),
            email=cont_data.get("email"),
            telefono=cont_data.get("telefono"),
            fuente=cont_data.get("fuente", ""),
            confianza=cont_data.get("confianza", 0.5)
        ))

    # Alertas
    alertas = []
    for alerta_data in data.get("alertas", []):
        alertas.append(Alerta(
            tipo=alerta_data.get("tipo", ""),
            prioridad=alerta_data.get("prioridad", "media"),
            mensaje=alerta_data.get("mensaje", ""),
            fecha_relevante=alerta_data.get("fecha_relevante")
        ))

    # Red flags
    red_flags = []
    for rf_data in data.get("red_flags", []):
        red_flags.append(RedFlag(
            tipo=rf_data.get("tipo", ""),
            descripcion=rf_data.get("descripcion", ""),
            impacto=rf_data.get("impacto", "precaucion")
        ))

    # Competencia
    comp_data = data.get("competencia", {})
    competencia = Competencia(
        incumbente_anterior=comp_data.get("incumbente_anterior"),
        motivo_cambio=comp_data.get("motivo_cambio"),
        competidores_probables=comp_data.get("competidores_probables", []),
        ventaja_srs=comp_data.get("ventaja_srs")
    ) if comp_data else None

    # Resumen operador
    res_data = data.get("resumen_operador", {})
    score_data = res_data.get("score_desglose", {})
    en30_data = res_data.get("en_30_segundos", {})
    gancho_data = res_data.get("gancho_inicial", {})

    servicios_aplicables = []
    for serv_data in res_data.get("servicios_srs_aplicables", []):
        servicios_aplicables.append(ServicioSRSAplicable(
            servicio=serv_data.get("servicio", ""),
            encaje=serv_data.get("encaje", "medio"),
            valor_estimado=serv_data.get("valor_estimado", "")
        ))

    objeciones = []
    for obj_data in res_data.get("objeciones_probables", []):
        objeciones.append(ObjecionRespuesta(
            objecion=obj_data.get("objecion", ""),
            respuesta=obj_data.get("respuesta", "")
        ))

    resumen_operador = ResumenOperador(
        nivel_oportunidad=res_data.get("nivel_oportunidad", "bronce"),
        score_total=res_data.get("score_total", 0),
        score_desglose=ScoreDesglose(
            alineacion_servicios_srs=score_data.get("alineacion_servicios_srs", 0),
            urgencia_temporal=score_data.get("urgencia_temporal", 0),
            volumen_economico=score_data.get("volumen_economico", 0),
            intensidad_dolor=score_data.get("intensidad_dolor", 0),
            cobertura_geografica=score_data.get("cobertura_geografica", 0),
            probabilidad_subcontratacion=score_data.get("probabilidad_subcontratacion", 0)
        ) if score_data else None,
        en_30_segundos=En30Segundos(
            que_es=en30_data.get("que_es", ""),
            por_que_interesa=en30_data.get("por_que_interesa", ""),
            por_que_ahora=en30_data.get("por_que_ahora", "")
        ) if en30_data else None,
        dolor_principal=res_data.get("dolor_principal", ""),
        dolores_secundarios=res_data.get("dolores_secundarios", []),
        servicios_srs_aplicables=servicios_aplicables,
        gancho_inicial=GanchoInicial(
            whatsapp=gancho_data.get("whatsapp", ""),
            email_asunto=gancho_data.get("email_asunto", ""),
            llamada=gancho_data.get("llamada", "")
        ) if gancho_data else None,
        puntos_clave_conversacion=res_data.get("puntos_clave_conversacion", []),
        propuesta_valor=res_data.get("propuesta_valor", []),
        preguntas_cualificacion=res_data.get("preguntas_cualificacion", []),
        objeciones_probables=objeciones,
        siguiente_accion=res_data.get("siguiente_accion", ""),
        fecha_limite_contacto=res_data.get("fecha_limite_contacto")
    ) if res_data else None

    # Metadata del análisis IA
    meta_data = data.get("metadata_analisis", {})
    metadata_analisis = MetadataAnalisisIA(
        confianza_global=meta_data.get("confianza_global", 0.8),
        calidad_documento=meta_data.get("calidad_documento", "media"),
        paginas_analizadas=meta_data.get("paginas_analizadas", 0),
        paginas_relevantes=meta_data.get("paginas_relevantes", []),
        datos_incompletos=meta_data.get("datos_incompletos", []),
        requiere_revision_humana=meta_data.get("requiere_revision_humana", False),
        motivo_revision=meta_data.get("motivo_revision")
    ) if meta_data else None

    return AnalisisComercial(
        oportunidad=oportunidad,
        adjudicatario=adjudicatario,
        cliente_final=cliente_final,
        economico=economico,
        componentes_it=componentes_it,
        dolores=dolores,
        requisitos_solvencia=requisitos_solvencia,
        tecnologias_mencionadas=data.get("tecnologias_mencionadas", []),
        fabricantes_mencionados=data.get("fabricantes_mencionados", []),
        certificaciones_requeridas=data.get("certificaciones_requeridas", []),
        contactos_extraidos=contactos,
        alertas=alertas,
        red_flags=red_flags,
        competencia=competencia,
        resumen_operador=resumen_operador,
        metadata_analisis=metadata_analisis
    )


def construir_metadata_trazabilidad(
    oportunidad_id: str,
    timestamp_inicio: datetime,
    timestamp_fin: datetime,
    proveedor_ia: str,
    modelo_ia: str,
    tokens_entrada: int = 0,
    tokens_salida: int = 0,
    tiempo_ms: int = 0,
    url_pliego: str = "",
    expediente: str = "",
    documentos: List[Dict] = None,
) -> MetadataCompleta:
    """
    Construye el objeto MetadataCompleta con toda la trazabilidad del análisis.
    """
    import uuid

    analisis_id = f"analisis_{oportunidad_id}_{timestamp_inicio.strftime('%Y%m%d%H%M%S')}"

    # Documentos procesados
    docs_procesados = []
    if documentos:
        for d in documentos:
            docs_procesados.append(DocumentoProcesado(
                tipo=d.get("tipo", "pliego"),
                nombre_archivo=d.get("nombre_archivo", ""),
                url_origen=d.get("url_origen", ""),
                hash_sha256=d.get("hash_sha256", ""),
                paginas_totales=d.get("paginas_totales", 0),
                palabras_totales=d.get("palabras_totales", 0)
            ))

    # Procesamiento IA
    tokens_totales = tokens_entrada + tokens_salida

    # Estimación de coste
    if proveedor_ia == "anthropic":
        coste_estimado = (tokens_entrada * 0.003 + tokens_salida * 0.015) / 1000
    elif proveedor_ia == "openai":
        coste_estimado = (tokens_entrada * 0.005 + tokens_salida * 0.015) / 1000
    elif proveedor_ia == "gemini":
        coste_estimado = tokens_totales * 0.0001 / 1000
    else:
        coste_estimado = 0.0

    procesamiento_ia = ProcesamientoIA(
        proveedor=proveedor_ia,
        modelo=modelo_ia,
        version_prompt="2.0.0",
        tokens_entrada=tokens_entrada,
        tokens_salida=tokens_salida,
        tokens_totales=tokens_totales,
        coste_estimado_usd=round(coste_estimado, 4),
        tiempo_ms=tiempo_ms
    )

    # Auditoría inicial
    auditoria = AuditoriaComercial(
        estado_comercial="pendiente_revision"
    )

    return MetadataCompleta(
        id_analisis=analisis_id,
        timestamp_inicio=timestamp_inicio.isoformat(),
        timestamp_fin=timestamp_fin.isoformat(),
        tiempo_total_segundos=(timestamp_fin - timestamp_inicio).total_seconds(),
        documentos_procesados=docs_procesados,
        procesamiento_ia=procesamiento_ia,
        url_pliego=url_pliego,
        expediente=expediente,
        auditoria=auditoria
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ÍNDICES PARA BÚSQUEDA EN CRM
# ═══════════════════════════════════════════════════════════════════════════════

INDICES_BUSQUEDA = {
    "texto_libre": [
        "adjudicatario.nombre",
        "adjudicatario.cif",
        "cliente_final.nombre",
        "oportunidad.titulo",
        "oportunidad.resumen_ejecutivo",
        "dolores[].descripcion",
        "componentes_it[].nombre",
        "componentes_it[].descripcion",
        "resumen_operador.dolor_principal",
        "tecnologias_mencionadas[]",
        "contactos_extraidos[].nombre",
    ],
    "filtros_exactos": [
        "resumen_operador.nivel_oportunidad",
        "cliente_final.comunidad_autonoma",
        "cliente_final.provincia",
        "cliente_final.sector",
        "adjudicatario.perfil_empresa",
        "adjudicatario.probabilidad_subcontratacion",
        "metadata.auditoria.estado_comercial",
        "dolores[].severidad",
        "componentes_it[].tipo",
    ],
    "filtros_rango": [
        "resumen_operador.score_total",
        "economico.importe_adjudicacion",
        "economico.valor_estimado_subcontratacion.minimo",
        "economico.valor_estimado_subcontratacion.maximo",
        "metadata.timestamp_fin",
    ],
    "ordenacion_default": [
        {"campo": "resumen_operador.score_total", "orden": "desc"},
        {"campo": "resumen_operador.fecha_limite_contacto", "orden": "asc"},
    ],
}
