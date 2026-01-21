#!/usr/bin/env python3
"""
Análisis Comercial Completo - Estructura enriquecida para el operador comercial

Este módulo define la estructura completa del análisis de oportunidades,
orientado 100% a la acción comercial con toda la información necesaria
para contactar al adjudicatario y cerrar la subcontratación.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# CLASIFICACIÓN Y SCORING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ScoreDesglose:
    """Desglose del score de la oportunidad"""
    alineacion_servicios_srs: int = 0  # 0-30
    urgencia_temporal: int = 0  # 0-25
    volumen_economico: int = 0  # 0-20
    intensidad_dolor: int = 0  # 0-25
    cobertura_geografica: int = 0  # -10 a +20
    probabilidad_subcontratacion: int = 0  # 0-10


@dataclass
class Clasificacion:
    """Clasificación de la oportunidad"""
    nivel: str  # oro, plata, bronce, descartar
    score_total: int  # 0-100
    score_desglose: ScoreDesglose
    confianza_clasificacion: float  # 0.0-1.0


# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN EJECUTIVO (30 SEGUNDOS)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class En30Segundos:
    """Lo que el comercial necesita saber en 30 segundos"""
    que_es: str  # Descripción en una frase
    por_que_interesa: str  # Por qué es relevante para SRS
    por_que_ahora: str  # Urgencia temporal
    valor_estimado: str  # Rango de valor para SRS


# ═══════════════════════════════════════════════════════════════════════════════
# ADJUDICATARIO (NUESTRO CLIENTE POTENCIAL)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContactoPrevio:
    """Información de contacto previo con el adjudicatario"""
    nombre: str = ""
    cargo: str = ""
    email: str = ""
    telefono: str = ""
    ultima_interaccion: Optional[str] = None  # Fecha ISO
    resultado: str = ""  # Cómo fue la última interacción


@dataclass
class Adjudicatario:
    """Información del adjudicatario (nuestro cliente potencial)"""
    nombre: str
    cif: str = ""
    conocemos: bool = False
    historico_srs: str = ""  # Historial de colaboración
    contacto_previo: Optional[ContactoPrevio] = None
    notas_crm: str = ""  # Notas del CRM sobre este cliente


# ═══════════════════════════════════════════════════════════════════════════════
# CONTACTOS DETALLADOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PersonaContacto:
    """Datos de la persona de contacto"""
    nombre_completo: str
    nombre: str = ""
    apellidos: str = ""
    cargo: str = ""
    departamento: str = ""
    antiguedad_estimada: str = ""


@dataclass
class EmpresaContacto:
    """Empresa del contacto"""
    nombre: str
    cif: str = ""
    rol_en_contrato: str = ""  # Adjudicatario principal, UTE miembro, etc.


@dataclass
class DatosContactoDirecto:
    """Datos de contacto directo"""
    email_profesional: str = ""
    email_alternativo: Optional[str] = None
    telefono_movil: Optional[str] = None
    telefono_fijo: Optional[str] = None
    extension: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None


@dataclass
class DisponibilidadContacto:
    """Preferencias de disponibilidad"""
    horario_preferido: str = ""  # mañanas, tardes, etc.
    mejor_dia: str = ""
    canal_preferido: str = ""  # whatsapp, email, llamada
    notas: str = ""


@dataclass
class HistorialSRS:
    """Historial de relación con SRS"""
    contacto_previo: bool = False
    ultima_interaccion: Optional[str] = None  # Fecha ISO
    tipo_ultima_interaccion: str = ""  # cierre_proyecto, llamada, email, etc.
    resultado: str = ""  # positivo, neutral, negativo
    proyectos_juntos: List[str] = field(default_factory=list)
    importe_historico: float = 0.0
    incidencias: List[str] = field(default_factory=list)
    nivel_relacion: str = "nueva"  # buena, neutral, fria, nueva
    quien_lo_conoce_srs: str = ""  # Nombre de quien lo conoce en SRS
    notas_relacion: str = ""


@dataclass
class PerfilComportamental:
    """Perfil de comportamiento para adaptar la comunicación"""
    estilo_comunicacion: str = ""  # directo, detallista, relacional, analitico
    sensibilidad_precio: str = ""  # alta, media, baja
    velocidad_decision: str = ""  # rapida, normal, lenta
    que_valora: List[str] = field(default_factory=list)
    que_le_molesta: List[str] = field(default_factory=list)
    como_ganarselo: str = ""


@dataclass
class OrigenExtraccion:
    """De dónde se extrajo el contacto"""
    documento: str = ""
    pagina: Optional[int] = None
    texto_original: str = ""
    fecha_extraccion: str = ""
    verificado: bool = False
    fecha_verificacion: Optional[str] = None


@dataclass
class DatosEnriquecimiento:
    """Datos de enriquecimiento del contacto"""
    fuente: str = ""  # apollo, linkedin, manual
    fecha: str = ""
    datos_añadidos: List[str] = field(default_factory=list)
    confianza: float = 0.0


@dataclass
class Contacto:
    """Contacto completo con toda la información"""
    id: str
    fuente: str  # pliego, adjudicacion, perfil_contratante, web_empresa, linkedin, apollo, historico_crm
    tipo_entidad: str  # adjudicatario, cliente_final, ute_miembro, subcontratista_actual
    rol_decisor: str  # decisor, influenciador, tecnico, administrativo, usuario
    nivel_jerarquico: str  # c_level, direccion, gerencia, mando_intermedio, tecnico

    persona: PersonaContacto
    empresa: EmpresaContacto
    contacto_directo: DatosContactoDirecto

    disponibilidad: Optional[DisponibilidadContacto] = None
    historial_srs: Optional[HistorialSRS] = None
    perfil_comportamental: Optional[PerfilComportamental] = None
    extraido_de: Optional[OrigenExtraccion] = None
    enriquecimiento: Optional[DatosEnriquecimiento] = None

    notas: str = ""
    confianza_contacto: float = 0.5  # 0.0-1.0


@dataclass
class ContactoPendienteBuscar:
    """Contacto que falta por buscar"""
    rol: str
    empresa: str
    sugerencia_busqueda: str = ""


@dataclass
class ContactosOportunidad:
    """Todos los contactos de una oportunidad"""
    contactos: List[Contacto] = field(default_factory=list)
    contacto_recomendado_id: Optional[str] = None
    razon_recomendacion: str = ""
    contactos_pendientes_buscar: List[ContactoPendienteBuscar] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# CLIENTE FINAL (QUIEN LICITA)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ClienteFinal:
    """Información del cliente final (el que publica la licitación)"""
    nombre: str
    tipo: str = ""  # Administración Central, Autonómica, Local, etc.
    sector: str = ""  # Sanidad, Educación, Justicia, etc.
    tamaño: str = ""  # Pequeño, Mediano, Grande
    ubicacion_principal: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# DOLORES (NECESIDADES DETECTADAS)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DolorPrincipal:
    """El dolor principal detectado"""
    descripcion: str
    por_que_duele: str  # Por qué es un problema para el adjudicatario
    intensidad: str  # critico, alto, medio, bajo
    fecha_limite: Optional[str] = None


@dataclass
class DolorSecundario:
    """Dolor secundario con servicio SRS asociado"""
    descripcion: str
    servicio_srs: str  # Servicio del catálogo SRS que lo resuelve


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICIOS SRS APLICABLES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ServicioSRSAplicable:
    """Servicio SRS que encaja con la oportunidad"""
    servicio: str  # Nombre del servicio del catálogo
    encaje: str  # perfecto, alto, medio, bajo
    volumen_estimado: str  # Cantidad estimada
    valor_estimado: str  # Rango de valor en euros


# ═══════════════════════════════════════════════════════════════════════════════
# VALOR DE LA OPORTUNIDAD
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ValorOportunidad:
    """Valoración económica de la oportunidad"""
    contrato_total: str  # Valor total del contrato
    estimacion_subcontratacion: str  # Lo que podría facturar SRS
    margen_tipico: str  # Margen esperado
    recurrencia: str  # Posibilidad de trabajo recurrente


# ═══════════════════════════════════════════════════════════════════════════════
# COMPETENCIA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Competencia:
    """Análisis de competencia"""
    competidores_probables: List[str] = field(default_factory=list)
    ventaja_srs: str = ""  # Nuestra ventaja competitiva
    incumbente_anterior: str = ""  # Quién tenía el contrato antes
    por_que_ganamos: str = ""  # Argumento de por qué deberían elegirnos


# ═══════════════════════════════════════════════════════════════════════════════
# REQUISITOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Requisito:
    """Requisito del pliego"""
    requisito: str
    cumple: bool
    evidencia: str = ""


@dataclass
class RequisitosCumplimos:
    """Análisis de requisitos que cumplimos"""
    tecnicos: List[Requisito] = field(default_factory=list)
    economicos: List[Requisito] = field(default_factory=list)
    no_cumplimos: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# ALERTAS Y RED FLAGS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Alerta:
    """Alerta sobre la oportunidad"""
    tipo: str  # temporal, economico, logistico, legal, tecnico
    icono: str  # Emoji representativo
    mensaje: str
    prioridad: str  # alta, media, baja


# ═══════════════════════════════════════════════════════════════════════════════
# COMUNICACIÓN (COPY LISTO PARA USAR)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GanchoInicial:
    """Mensajes de primer contacto listos para usar"""
    whatsapp: str = ""
    email_asunto: str = ""
    llamada: str = ""  # Script de apertura para llamada


@dataclass
class ObjecionRespuesta:
    """Objeción esperada con respuesta preparada"""
    objecion: str
    respuesta: str


@dataclass
class Comunicacion:
    """Todo lo necesario para la comunicación comercial"""
    gancho_inicial: GanchoInicial
    puntos_clave_conversacion: List[str] = field(default_factory=list)
    propuesta_valor: List[str] = field(default_factory=list)
    preguntas_cualificacion: List[str] = field(default_factory=list)
    objeciones_probables: List[ObjecionRespuesta] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# SIGUIENTES PASOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SiguientesPasos:
    """Plan de acción para el comercial"""
    accion_inmediata: str  # Qué hacer ahora mismo
    fecha_limite_contacto: str  # Fecha máxima para contactar
    si_no_responde: str  # Plan B si no hay respuesta
    preparar_antes: List[str] = field(default_factory=list)
    reunirse_con: str = ""  # Próximo paso si hay interés


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTOS RELACIONADOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DocumentoRelacionado:
    """Documento relacionado con la oportunidad"""
    tipo: str  # pliego_tecnico, adjudicacion, anuncio, etc.
    url: str
    paginas_clave: List[int] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# COPIAR Y PEGAR (ACCESO RÁPIDO)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CopiarPegar:
    """Textos listos para copiar y pegar"""
    whatsapp_listo: str = ""
    email_asunto_listo: str = ""
    email_cuerpo_listo: str = ""
    bullets_propuesta: str = ""
    telefono_directo: str = ""
    linkedin_url: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# METADATA Y TRAZABILIDAD
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WarningAnalisis:
    """Warning durante el análisis"""
    codigo: str
    mensaje: str
    impacto: str = ""
    pagina: Optional[int] = None


@dataclass
class MetadataAnalisis:
    """Metadata del proceso de análisis"""
    id: str
    version_sistema: str = "1.0.0"
    timestamp_inicio: str = ""
    timestamp_fin: str = ""
    tiempo_total_segundos: float = 0.0
    estado: str = "completado"  # completado, error, parcial
    errores: List[str] = field(default_factory=list)
    warnings: List[WarningAnalisis] = field(default_factory=list)


@dataclass
class DocumentoProcesado:
    """Documento procesado en el análisis"""
    tipo: str  # pliego_tecnico, pliego_administrativo, anexo_tecnico, adjudicacion
    nombre_archivo: str = ""
    url_origen: str = ""
    url_local: str = ""
    hash_sha256: str = ""
    tamaño_bytes: int = 0
    paginas_totales: int = 0
    paginas_analizadas: int = 0
    paginas_relevantes: List[int] = field(default_factory=list)
    palabras_totales: int = 0
    idioma_detectado: str = "es"
    calidad_ocr_media: float = 1.0
    tiene_tablas: bool = False
    tiene_imagenes: bool = False
    tiene_anexos_embebidos: bool = False


@dataclass
class LlamadaIA:
    """Desglose de una llamada a la IA"""
    paso: str
    tokens_in: int = 0
    tokens_out: int = 0
    tiempo_ms: int = 0


@dataclass
class ProcesamientoIA:
    """Metadata del procesamiento con IA"""
    proveedor: str  # anthropic, openai, gemini
    modelo: str
    version_prompt: str = "1.0.0"
    version_catalogo_servicios: str = "1.0.0"
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_totales: int = 0
    coste_estimado_usd: float = 0.0
    llamadas_api: int = 1
    desglose_llamadas: List[LlamadaIA] = field(default_factory=list)
    temperatura: float = 0.3
    fallback_usado: bool = False


@dataclass
class FuenteExterna:
    """Fuente externa de enriquecimiento"""
    fuente: str  # apollo, einforma, linkedin, infocif
    timestamp: str = ""
    datos_obtenidos: List[str] = field(default_factory=list)
    exito: bool = True
    error: str = ""


@dataclass
class MetadataEnriquecimiento:
    """Metadata del enriquecimiento de datos"""
    apollo_llamadas: int = 0
    apollo_creditos_usados: int = 0
    linkedin_consultas: int = 0
    datos_enriquecidos: List[str] = field(default_factory=list)
    fuentes_externas: List[FuenteExterna] = field(default_factory=list)


@dataclass
class MetadataPLACSP:
    """Metadata de PLACSP"""
    expediente: str = ""
    url_licitacion: str = ""
    url_adjudicacion: str = ""
    fecha_publicacion: str = ""
    fecha_adjudicacion: str = ""
    fecha_formalizacion: Optional[str] = None
    estado_contrato: str = ""  # adjudicado, formalizado, en_ejecucion
    codice_procesado: bool = False
    atom_feed_id: str = ""


@dataclass
class CompletitudDatos:
    """Completitud de datos extraídos"""
    adjudicatario: float = 0.0
    cliente_final: float = 0.0
    importe: float = 0.0
    plazo: float = 0.0
    contactos: float = 0.0
    requisitos_tecnicos: float = 0.0
    requisitos_solvencia: float = 0.0


@dataclass
class CalidadAnalisis:
    """Métricas de calidad del análisis"""
    score_calidad: float = 0.0  # 0.0-1.0
    completitud_datos: Optional[CompletitudDatos] = None
    confianza_componentes_it: float = 0.0
    confianza_dolores: float = 0.0
    confianza_scoring: float = 0.0
    revision_humana_recomendada: bool = False
    motivo_revision: Optional[str] = None


@dataclass
class Trazabilidad:
    """Trazabilidad del procesamiento"""
    pipeline_version: str = "1.0.0"
    worker_id: str = ""
    cola_origen: str = ""
    job_id: str = ""
    trigger: str = ""  # cron_diario, manual, webhook
    usuario_trigger: Optional[str] = None
    tiempo_en_cola_ms: int = 0
    reintentos: int = 0


@dataclass
class Almacenamiento:
    """Referencias de almacenamiento"""
    mongo_collection: str = ""
    mongo_id: str = ""
    elastic_index: str = ""
    elastic_id: str = ""
    s3_bucket: str = ""
    s3_path: str = ""
    backup_realizado: bool = False


@dataclass
class NotaOperador:
    """Nota del operador comercial"""
    fecha: str
    usuario: str
    nota: str


@dataclass
class Auditoria:
    """Auditoría de acciones sobre la oportunidad"""
    acciones_operador: List[str] = field(default_factory=list)
    fecha_primera_vista: Optional[str] = None
    fecha_contacto_realizado: Optional[str] = None
    resultado_contacto: Optional[str] = None
    notas_operador: List[NotaOperador] = field(default_factory=list)
    estado_comercial: str = "pendiente_revision"  # pendiente_revision, en_contacto, propuesta_enviada, ganado, perdido, descartado


@dataclass
class Metadata:
    """Metadata completa del análisis"""
    analisis: MetadataAnalisis
    documentos_procesados: List[DocumentoProcesado] = field(default_factory=list)
    procesamiento_ia: Optional[ProcesamientoIA] = None
    enriquecimiento: Optional[MetadataEnriquecimiento] = None
    placsp: Optional[MetadataPLACSP] = None
    calidad_analisis: Optional[CalidadAnalisis] = None
    trazabilidad: Optional[Trazabilidad] = None
    almacenamiento: Optional[Almacenamiento] = None
    auditoria: Optional[Auditoria] = None


# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISIS COMERCIAL COMPLETO
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AnalisisComercialCompleto:
    """
    Estructura completa del análisis comercial de una oportunidad.
    Diseñada para que el operador comercial tenga TODO lo necesario
    para contactar al adjudicatario y cerrar la subcontratación.
    """
    # Identificación
    id_oportunidad: str
    fecha_analisis: str

    # Clasificación
    clasificacion: Clasificacion

    # Resumen ejecutivo
    en_30_segundos: En30Segundos

    # Actores
    adjudicatario: Adjudicatario
    cliente_final: ClienteFinal

    # Contactos
    contactos: ContactosOportunidad

    # Dolores
    dolor_principal: DolorPrincipal
    dolores_secundarios: List[DolorSecundario]

    # Servicios y valor
    servicios_srs_aplicables: List[ServicioSRSAplicable]
    valor_oportunidad: ValorOportunidad

    # Análisis competitivo
    competencia: Competencia
    requisitos_cumplimos: RequisitosCumplimos

    # Alertas
    alertas: List[Alerta]
    red_flags: List[str]

    # Comunicación
    comunicacion: Comunicacion
    siguientes_pasos: SiguientesPasos

    # Documentación
    documentos_relacionados: List[DocumentoRelacionado]
    notas_analisis: List[str]

    # Acceso rápido
    copiar_pegar: CopiarPegar

    # Metadata y trazabilidad (opcional, se añade en el procesamiento)
    metadata: Optional[Metadata] = None

    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización JSON"""
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CONSTRUCCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def construir_analisis_comercial(data: Dict, oportunidad_id: str) -> AnalisisComercialCompleto:
    """
    Construye un AnalisisComercialCompleto a partir de los datos de la IA.
    Maneja valores por defecto para campos faltantes.
    """
    # Clasificación
    clasificacion_data = data.get("clasificacion", {})
    score_desglose_data = clasificacion_data.get("score_desglose", {})

    clasificacion = Clasificacion(
        nivel=clasificacion_data.get("nivel", "bronce"),
        score_total=clasificacion_data.get("score_total", 50),
        score_desglose=ScoreDesglose(
            alineacion_servicios_srs=score_desglose_data.get("alineacion_servicios_srs", 0),
            urgencia_temporal=score_desglose_data.get("urgencia_temporal", 0),
            volumen_economico=score_desglose_data.get("volumen_economico", 0),
            intensidad_dolor=score_desglose_data.get("intensidad_dolor", 0),
            cobertura_geografica=score_desglose_data.get("cobertura_geografica", 0),
            probabilidad_subcontratacion=score_desglose_data.get("probabilidad_subcontratacion", 0)
        ),
        confianza_clasificacion=clasificacion_data.get("confianza_clasificacion", 0.5)
    )

    # En 30 segundos
    en_30_data = data.get("en_30_segundos", {})
    en_30_segundos = En30Segundos(
        que_es=en_30_data.get("que_es", ""),
        por_que_interesa=en_30_data.get("por_que_interesa", ""),
        por_que_ahora=en_30_data.get("por_que_ahora", ""),
        valor_estimado=en_30_data.get("valor_estimado", "")
    )

    # Adjudicatario
    adj_data = data.get("adjudicatario", {})
    contacto_data = adj_data.get("contacto_previo", {})
    contacto_previo = None
    if contacto_data:
        contacto_previo = ContactoPrevio(
            nombre=contacto_data.get("nombre", ""),
            cargo=contacto_data.get("cargo", ""),
            email=contacto_data.get("email", ""),
            telefono=contacto_data.get("telefono", ""),
            ultima_interaccion=contacto_data.get("ultima_interaccion"),
            resultado=contacto_data.get("resultado", "")
        )

    adjudicatario = Adjudicatario(
        nombre=adj_data.get("nombre", "Por identificar"),
        cif=adj_data.get("cif", ""),
        conocemos=adj_data.get("conocemos", False),
        historico_srs=adj_data.get("historico_srs", ""),
        contacto_previo=contacto_previo,
        notas_crm=adj_data.get("notas_crm", "")
    )

    # Cliente final
    cliente_data = data.get("cliente_final", {})
    cliente_final = ClienteFinal(
        nombre=cliente_data.get("nombre", ""),
        tipo=cliente_data.get("tipo", ""),
        sector=cliente_data.get("sector", ""),
        tamaño=cliente_data.get("tamaño", ""),
        ubicacion_principal=cliente_data.get("ubicacion_principal", "")
    )

    # Dolor principal
    dolor_data = data.get("dolor_principal", {})
    dolor_principal = DolorPrincipal(
        descripcion=dolor_data.get("descripcion", ""),
        por_que_duele=dolor_data.get("por_que_duele", ""),
        intensidad=dolor_data.get("intensidad", "medio"),
        fecha_limite=dolor_data.get("fecha_limite")
    )

    # Dolores secundarios
    dolores_secundarios = []
    for d in data.get("dolores_secundarios", []):
        dolores_secundarios.append(DolorSecundario(
            descripcion=d.get("descripcion", ""),
            servicio_srs=d.get("servicio_srs", "")
        ))

    # Servicios SRS aplicables
    servicios_srs = []
    for s in data.get("servicios_srs_aplicables", []):
        servicios_srs.append(ServicioSRSAplicable(
            servicio=s.get("servicio", ""),
            encaje=s.get("encaje", "medio"),
            volumen_estimado=s.get("volumen_estimado", ""),
            valor_estimado=s.get("valor_estimado", "")
        ))

    # Valor oportunidad
    valor_data = data.get("valor_oportunidad", {})
    valor_oportunidad = ValorOportunidad(
        contrato_total=valor_data.get("contrato_total", ""),
        estimacion_subcontratacion=valor_data.get("estimacion_subcontratacion", ""),
        margen_tipico=valor_data.get("margen_tipico", ""),
        recurrencia=valor_data.get("recurrencia", "")
    )

    # Competencia
    comp_data = data.get("competencia", {})
    competencia = Competencia(
        competidores_probables=comp_data.get("competidores_probables", []),
        ventaja_srs=comp_data.get("ventaja_srs", ""),
        incumbente_anterior=comp_data.get("incumbente_anterior", ""),
        por_que_ganamos=comp_data.get("por_que_ganamos", "")
    )

    # Requisitos
    req_data = data.get("requisitos_cumplimos", {})
    requisitos_tecnicos = []
    for r in req_data.get("tecnicos", []):
        requisitos_tecnicos.append(Requisito(
            requisito=r.get("requisito", ""),
            cumple=r.get("cumple", False),
            evidencia=r.get("evidencia", "")
        ))
    requisitos_economicos = []
    for r in req_data.get("economicos", []):
        requisitos_economicos.append(Requisito(
            requisito=r.get("requisito", ""),
            cumple=r.get("cumple", False),
            evidencia=r.get("evidencia", "")
        ))
    requisitos_cumplimos = RequisitosCumplimos(
        tecnicos=requisitos_tecnicos,
        economicos=requisitos_economicos,
        no_cumplimos=req_data.get("no_cumplimos", [])
    )

    # Alertas
    alertas = []
    for a in data.get("alertas", []):
        alertas.append(Alerta(
            tipo=a.get("tipo", "info"),
            icono=a.get("icono", "ℹ️"),
            mensaje=a.get("mensaje", ""),
            prioridad=a.get("prioridad", "media")
        ))

    # Comunicación
    com_data = data.get("comunicacion", {})
    gancho_data = com_data.get("gancho_inicial", {})
    gancho_inicial = GanchoInicial(
        whatsapp=gancho_data.get("whatsapp", ""),
        email_asunto=gancho_data.get("email_asunto", ""),
        llamada=gancho_data.get("llamada", "")
    )
    objeciones = []
    for o in com_data.get("objeciones_probables", []):
        objeciones.append(ObjecionRespuesta(
            objecion=o.get("objecion", ""),
            respuesta=o.get("respuesta", "")
        ))
    comunicacion = Comunicacion(
        gancho_inicial=gancho_inicial,
        puntos_clave_conversacion=com_data.get("puntos_clave_conversacion", []),
        propuesta_valor=com_data.get("propuesta_valor", []),
        preguntas_cualificacion=com_data.get("preguntas_cualificacion", []),
        objeciones_probables=objeciones
    )

    # Siguientes pasos
    pasos_data = data.get("siguientes_pasos", {})
    siguientes_pasos = SiguientesPasos(
        accion_inmediata=pasos_data.get("accion_inmediata", ""),
        fecha_limite_contacto=pasos_data.get("fecha_limite_contacto", ""),
        si_no_responde=pasos_data.get("si_no_responde", ""),
        preparar_antes=pasos_data.get("preparar_antes", []),
        reunirse_con=pasos_data.get("reunirse_con", "")
    )

    # Documentos
    documentos = []
    for d in data.get("documentos_relacionados", []):
        documentos.append(DocumentoRelacionado(
            tipo=d.get("tipo", ""),
            url=d.get("url", ""),
            paginas_clave=d.get("paginas_clave", [])
        ))

    # Copiar y pegar
    cp_data = data.get("copiar_pegar", {})
    copiar_pegar = CopiarPegar(
        whatsapp_listo=cp_data.get("whatsapp_listo", gancho_data.get("whatsapp", "")),
        email_asunto_listo=cp_data.get("email_asunto_listo", gancho_data.get("email_asunto", "")),
        email_cuerpo_listo=cp_data.get("email_cuerpo_listo", ""),
        bullets_propuesta=cp_data.get("bullets_propuesta", ""),
        telefono_directo=cp_data.get("telefono_directo", ""),
        linkedin_url=cp_data.get("linkedin_url", "")
    )

    # Contactos
    contactos_lista = []
    contactos_data = data.get("contactos", [])
    for c in contactos_data:
        # Persona
        persona_data = c.get("persona", {})
        persona = PersonaContacto(
            nombre_completo=persona_data.get("nombre_completo", ""),
            nombre=persona_data.get("nombre", ""),
            apellidos=persona_data.get("apellidos", ""),
            cargo=persona_data.get("cargo", ""),
            departamento=persona_data.get("departamento", ""),
            antiguedad_estimada=persona_data.get("antiguedad_estimada", "")
        )

        # Empresa
        empresa_data = c.get("empresa", {})
        empresa = EmpresaContacto(
            nombre=empresa_data.get("nombre", ""),
            cif=empresa_data.get("cif", ""),
            rol_en_contrato=empresa_data.get("rol_en_contrato", "")
        )

        # Contacto directo
        cd_data = c.get("contacto_directo", {})
        contacto_directo = DatosContactoDirecto(
            email_profesional=cd_data.get("email_profesional", ""),
            email_alternativo=cd_data.get("email_alternativo"),
            telefono_movil=cd_data.get("telefono_movil"),
            telefono_fijo=cd_data.get("telefono_fijo"),
            extension=cd_data.get("extension"),
            linkedin=cd_data.get("linkedin"),
            twitter=cd_data.get("twitter")
        )

        # Disponibilidad (opcional)
        disp_data = c.get("disponibilidad")
        disponibilidad = None
        if disp_data:
            disponibilidad = DisponibilidadContacto(
                horario_preferido=disp_data.get("horario_preferido", ""),
                mejor_dia=disp_data.get("mejor_dia", ""),
                canal_preferido=disp_data.get("canal_preferido", ""),
                notas=disp_data.get("notas", "")
            )

        # Historial SRS (opcional)
        hist_data = c.get("historial_srs")
        historial_srs = None
        if hist_data:
            historial_srs = HistorialSRS(
                contacto_previo=hist_data.get("contacto_previo", False),
                ultima_interaccion=hist_data.get("ultima_interaccion"),
                tipo_ultima_interaccion=hist_data.get("tipo_ultima_interaccion", ""),
                resultado=hist_data.get("resultado", ""),
                proyectos_juntos=hist_data.get("proyectos_juntos", []),
                importe_historico=hist_data.get("importe_historico", 0.0),
                incidencias=hist_data.get("incidencias", []),
                nivel_relacion=hist_data.get("nivel_relacion", "nueva"),
                quien_lo_conoce_srs=hist_data.get("quien_lo_conoce_srs", ""),
                notas_relacion=hist_data.get("notas_relacion", "")
            )

        # Perfil comportamental (opcional)
        perfil_data = c.get("perfil_comportamental")
        perfil_comportamental = None
        if perfil_data:
            perfil_comportamental = PerfilComportamental(
                estilo_comunicacion=perfil_data.get("estilo_comunicacion", ""),
                sensibilidad_precio=perfil_data.get("sensibilidad_precio", ""),
                velocidad_decision=perfil_data.get("velocidad_decision", ""),
                que_valora=perfil_data.get("que_valora", []),
                que_le_molesta=perfil_data.get("que_le_molesta", []),
                como_ganarselo=perfil_data.get("como_ganarselo", "")
            )

        # Origen extracción (opcional)
        origen_data = c.get("extraido_de")
        extraido_de = None
        if origen_data:
            extraido_de = OrigenExtraccion(
                documento=origen_data.get("documento", ""),
                pagina=origen_data.get("pagina"),
                texto_original=origen_data.get("texto_original", ""),
                fecha_extraccion=origen_data.get("fecha_extraccion", ""),
                verificado=origen_data.get("verificado", False),
                fecha_verificacion=origen_data.get("fecha_verificacion")
            )

        # Enriquecimiento (opcional)
        enr_data = c.get("enriquecimiento")
        enriquecimiento = None
        if enr_data:
            enriquecimiento = DatosEnriquecimiento(
                fuente=enr_data.get("fuente", ""),
                fecha=enr_data.get("fecha", ""),
                datos_añadidos=enr_data.get("datos_añadidos", []),
                confianza=enr_data.get("confianza", 0.0)
            )

        contactos_lista.append(Contacto(
            id=c.get("id", f"contacto_{len(contactos_lista)+1:03d}"),
            fuente=c.get("fuente", "pliego"),
            tipo_entidad=c.get("tipo_entidad", "adjudicatario"),
            rol_decisor=c.get("rol_decisor", "tecnico"),
            nivel_jerarquico=c.get("nivel_jerarquico", "mando_intermedio"),
            persona=persona,
            empresa=empresa,
            contacto_directo=contacto_directo,
            disponibilidad=disponibilidad,
            historial_srs=historial_srs,
            perfil_comportamental=perfil_comportamental,
            extraido_de=extraido_de,
            enriquecimiento=enriquecimiento,
            notas=c.get("notas", ""),
            confianza_contacto=c.get("confianza_contacto", 0.5)
        ))

    # Contactos pendientes de buscar
    contactos_pendientes = []
    for cp in data.get("contactos_pendientes_buscar", []):
        contactos_pendientes.append(ContactoPendienteBuscar(
            rol=cp.get("rol", ""),
            empresa=cp.get("empresa", ""),
            sugerencia_busqueda=cp.get("sugerencia_busqueda", "")
        ))

    # Contacto recomendado
    contacto_rec_data = data.get("contacto_recomendado", {})
    contactos_oportunidad = ContactosOportunidad(
        contactos=contactos_lista,
        contacto_recomendado_id=contacto_rec_data.get("id"),
        razon_recomendacion=contacto_rec_data.get("razon", ""),
        contactos_pendientes_buscar=contactos_pendientes
    )

    return AnalisisComercialCompleto(
        id_oportunidad=oportunidad_id,
        fecha_analisis=datetime.now().isoformat(),
        clasificacion=clasificacion,
        en_30_segundos=en_30_segundos,
        adjudicatario=adjudicatario,
        cliente_final=cliente_final,
        contactos=contactos_oportunidad,
        dolor_principal=dolor_principal,
        dolores_secundarios=dolores_secundarios,
        servicios_srs_aplicables=servicios_srs,
        valor_oportunidad=valor_oportunidad,
        competencia=competencia,
        requisitos_cumplimos=requisitos_cumplimos,
        alertas=alertas,
        red_flags=data.get("red_flags", []),
        comunicacion=comunicacion,
        siguientes_pasos=siguientes_pasos,
        documentos_relacionados=documentos,
        notas_analisis=data.get("notas_analisis", []),
        copiar_pegar=copiar_pegar
    )


def construir_metadata(
    oportunidad_id: str,
    timestamp_inicio: datetime,
    timestamp_fin: datetime,
    proveedor_ia: str,
    modelo_ia: str,
    tokens_entrada: int = 0,
    tokens_salida: int = 0,
    documentos: List[Dict] = None,
    errores: List[str] = None,
    warnings: List[Dict] = None,
    url_pliego: str = "",
    expediente: str = "",
) -> Metadata:
    """
    Construye el objeto Metadata con toda la trazabilidad del análisis.
    """
    import uuid

    analisis_id = f"analisis_{oportunidad_id}_{timestamp_inicio.strftime('%Y%m%d%H%M%S')}"

    # Warnings
    warnings_list = []
    if warnings:
        for w in warnings:
            warnings_list.append(WarningAnalisis(
                codigo=w.get("codigo", "WARN_GENERAL"),
                mensaje=w.get("mensaje", ""),
                impacto=w.get("impacto", ""),
                pagina=w.get("pagina")
            ))

    # Metadata del análisis
    metadata_analisis = MetadataAnalisis(
        id=analisis_id,
        version_sistema="1.0.0",
        timestamp_inicio=timestamp_inicio.isoformat(),
        timestamp_fin=timestamp_fin.isoformat(),
        tiempo_total_segundos=(timestamp_fin - timestamp_inicio).total_seconds(),
        estado="completado" if not errores else "error",
        errores=errores or [],
        warnings=warnings_list
    )

    # Documentos procesados
    docs_procesados = []
    if documentos:
        for d in documentos:
            docs_procesados.append(DocumentoProcesado(
                tipo=d.get("tipo", "pliego_tecnico"),
                nombre_archivo=d.get("nombre_archivo", ""),
                url_origen=d.get("url_origen", ""),
                url_local=d.get("url_local", ""),
                hash_sha256=d.get("hash_sha256", ""),
                tamaño_bytes=d.get("tamaño_bytes", 0),
                paginas_totales=d.get("paginas_totales", 0),
                paginas_analizadas=d.get("paginas_analizadas", 0),
                paginas_relevantes=d.get("paginas_relevantes", []),
                palabras_totales=d.get("palabras_totales", 0),
                idioma_detectado=d.get("idioma_detectado", "es"),
                calidad_ocr_media=d.get("calidad_ocr_media", 1.0),
                tiene_tablas=d.get("tiene_tablas", False),
                tiene_imagenes=d.get("tiene_imagenes", False),
                tiene_anexos_embebidos=d.get("tiene_anexos_embebidos", False)
            ))

    # Procesamiento IA
    tokens_totales = tokens_entrada + tokens_salida
    # Estimación de coste (aproximado)
    if proveedor_ia == "anthropic":
        coste_estimado = (tokens_entrada * 0.003 + tokens_salida * 0.015) / 1000
    elif proveedor_ia == "openai":
        coste_estimado = (tokens_entrada * 0.005 + tokens_salida * 0.015) / 1000
    elif proveedor_ia == "gemini":
        coste_estimado = tokens_totales * 0.0001 / 1000  # Gemini es más barato
    else:
        coste_estimado = 0.0

    procesamiento_ia = ProcesamientoIA(
        proveedor=proveedor_ia,
        modelo=modelo_ia,
        version_prompt="1.0.0",
        version_catalogo_servicios="1.0.0",
        tokens_entrada=tokens_entrada,
        tokens_salida=tokens_salida,
        tokens_totales=tokens_totales,
        coste_estimado_usd=round(coste_estimado, 4),
        llamadas_api=1,
        desglose_llamadas=[],
        temperatura=0.3,
        fallback_usado=False
    )

    # PLACSP
    placsp = MetadataPLACSP(
        expediente=expediente,
        url_licitacion=url_pliego,
        estado_contrato="adjudicado"
    )

    # Calidad
    calidad = CalidadAnalisis(
        score_calidad=0.85,  # Por defecto, se puede ajustar
        revision_humana_recomendada=False
    )

    # Trazabilidad
    trazabilidad = Trazabilidad(
        pipeline_version="1.0.0",
        job_id=str(uuid.uuid4())[:8],
        trigger="manual"
    )

    # Auditoría inicial
    auditoria = Auditoria(
        estado_comercial="pendiente_revision"
    )

    return Metadata(
        analisis=metadata_analisis,
        documentos_procesados=docs_procesados,
        procesamiento_ia=procesamiento_ia,
        placsp=placsp,
        calidad_analisis=calidad,
        trazabilidad=trazabilidad,
        auditoria=auditoria
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ÍNDICES Y CAMPOS CLAVE PARA BÚSQUEDA EN CRM
# ═══════════════════════════════════════════════════════════════════════════════

INDICES_BUSQUEDA = {
    # Campos para búsqueda de texto libre (full-text search)
    "texto_libre": [
        "adjudicatario.nombre",
        "adjudicatario.cif",
        "cliente_final.nombre",
        "dolor_principal.descripcion",
        "dolor_principal.por_que_duele",
        "servicios_srs_aplicables[].servicio",
        "en_30_segundos.que_es",
        "en_30_segundos.por_que_interesa",
        "contactos.contactos[].nombre",
        "contactos.contactos[].cargo",
        "comunicacion.tecnologias_mencionadas[]",
        "notas_analisis[]",
    ],

    # Campos para filtros exactos (match exacto)
    "filtros_exactos": [
        "clasificacion.nivel",                          # oro, plata, bronce
        "cobertura_geografica.zona_srs",                # norte, sur, este, oeste, centro, nacional
        "cobertura_geografica.provincias[]",            # Lista de provincias
        "cobertura_geografica.dentro_cobertura",        # true/false
        "metadata.auditoria.estado_comercial",          # pendiente_revision, en_contacto, propuesta_enviada, ganado, perdido, descartado
        "cliente_final.sector",                         # sanidad, educacion, administracion, etc.
        "cliente_final.tipo",                           # publico, privado
        "adjudicatario.conocemos",                      # true/false
        "dolor_principal.intensidad",                   # critico, alto, medio, bajo
        "servicios_srs_aplicables[].encaje",            # perfecto, alto, medio, bajo
        "metadata.procesamiento_ia.proveedor",          # anthropic, openai, gemini
    ],

    # Campos para filtros de rango numérico/fecha
    "filtros_rango": [
        "clasificacion.score_total",                    # 0-100
        "clasificacion.score_desglose.alineacion_servicios_srs",
        "clasificacion.score_desglose.urgencia_temporal",
        "clasificacion.score_desglose.volumen_economico",
        "clasificacion.score_desglose.cobertura_geografica",
        "valor_oportunidad.contrato_total",             # Euros
        "dolor_principal.urgencia_temporal.dias_restantes",
        "metadata.analisis.timestamp_fin",              # Fecha ISO
        "metadata.analisis.tiempo_total_segundos",
        "metadata.calidad_analisis.score_calidad",      # 0.0-1.0
    ],

    # Ordenación por defecto para listados
    "ordenacion_default": [
        {"campo": "clasificacion.score_total", "orden": "desc"},
        {"campo": "dolor_principal.urgencia_temporal.dias_restantes", "orden": "asc"},
    ],

    # Agregaciones útiles para dashboards
    "agregaciones": [
        {"campo": "clasificacion.nivel", "tipo": "terms"},
        {"campo": "cobertura_geografica.provincias", "tipo": "terms"},
        {"campo": "metadata.auditoria.estado_comercial", "tipo": "terms"},
        {"campo": "cliente_final.sector", "tipo": "terms"},
        {"campo": "clasificacion.score_total", "tipo": "histogram", "intervalo": 10},
    ],

    # Campos para exportación a Excel/CSV
    "campos_exportacion": [
        "id_oportunidad",
        "fecha_analisis",
        "clasificacion.nivel",
        "clasificacion.score_total",
        "adjudicatario.nombre",
        "adjudicatario.cif",
        "cliente_final.nombre",
        "valor_oportunidad.contrato_total",
        "valor_oportunidad.estimacion_subcontratacion",
        "dolor_principal.descripcion",
        "dolor_principal.intensidad",
        "cobertura_geografica.provincias",
        "contactos.contacto_recomendado.nombre",
        "contactos.contacto_recomendado.telefono",
        "contactos.contacto_recomendado.email",
        "metadata.auditoria.estado_comercial",
    ],
}


@dataclass
class ConfiguracionIndices:
    """Configuración de índices para búsqueda en CRM"""
    texto_libre: List[str] = field(default_factory=lambda: INDICES_BUSQUEDA["texto_libre"])
    filtros_exactos: List[str] = field(default_factory=lambda: INDICES_BUSQUEDA["filtros_exactos"])
    filtros_rango: List[str] = field(default_factory=lambda: INDICES_BUSQUEDA["filtros_rango"])
    ordenacion_default: List[Dict] = field(default_factory=lambda: INDICES_BUSQUEDA["ordenacion_default"])
    agregaciones: List[Dict] = field(default_factory=lambda: INDICES_BUSQUEDA["agregaciones"])
    campos_exportacion: List[str] = field(default_factory=lambda: INDICES_BUSQUEDA["campos_exportacion"])


def get_indices_busqueda() -> Dict:
    """Retorna la configuración de índices para búsqueda"""
    return INDICES_BUSQUEDA


def get_mapping_elasticsearch() -> Dict:
    """
    Genera un mapping de Elasticsearch basado en los índices definidos.
    Útil para crear el índice en Elastic.
    """
    mapping = {
        "mappings": {
            "properties": {
                # Campos de texto libre
                "adjudicatario": {
                    "properties": {
                        "nombre": {"type": "text", "analyzer": "spanish"},
                        "cif": {"type": "keyword"},
                        "conocemos": {"type": "boolean"},
                    }
                },
                "cliente_final": {
                    "properties": {
                        "nombre": {"type": "text", "analyzer": "spanish"},
                        "sector": {"type": "keyword"},
                        "tipo": {"type": "keyword"},
                    }
                },
                "clasificacion": {
                    "properties": {
                        "nivel": {"type": "keyword"},
                        "score_total": {"type": "integer"},
                        "score_desglose": {
                            "properties": {
                                "alineacion_servicios_srs": {"type": "integer"},
                                "urgencia_temporal": {"type": "integer"},
                                "volumen_economico": {"type": "integer"},
                                "cobertura_geografica": {"type": "integer"},
                            }
                        },
                    }
                },
                "cobertura_geografica": {
                    "properties": {
                        "zona_srs": {"type": "keyword"},
                        "provincias": {"type": "keyword"},
                        "dentro_cobertura": {"type": "boolean"},
                    }
                },
                "dolor_principal": {
                    "properties": {
                        "descripcion": {"type": "text", "analyzer": "spanish"},
                        "intensidad": {"type": "keyword"},
                        "urgencia_temporal": {
                            "properties": {
                                "dias_restantes": {"type": "integer"},
                            }
                        },
                    }
                },
                "valor_oportunidad": {
                    "properties": {
                        "contrato_total": {"type": "keyword"},  # Se parsea en queries
                    }
                },
                "servicios_srs_aplicables": {
                    "type": "nested",
                    "properties": {
                        "servicio": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "encaje": {"type": "keyword"},
                    }
                },
                "contactos": {
                    "properties": {
                        "contactos": {
                            "type": "nested",
                            "properties": {
                                "nombre": {"type": "text"},
                                "cargo": {"type": "text"},
                                "email": {"type": "keyword"},
                                "telefono": {"type": "keyword"},
                            }
                        }
                    }
                },
                "metadata": {
                    "properties": {
                        "analisis": {
                            "properties": {
                                "timestamp_fin": {"type": "date"},
                                "tiempo_total_segundos": {"type": "float"},
                            }
                        },
                        "auditoria": {
                            "properties": {
                                "estado_comercial": {"type": "keyword"},
                                "fecha_primera_vista": {"type": "date"},
                                "fecha_contacto_realizado": {"type": "date"},
                            }
                        },
                        "calidad_analisis": {
                            "properties": {
                                "score_calidad": {"type": "float"},
                            }
                        },
                    }
                },
                "fecha_analisis": {"type": "date"},
                "id_oportunidad": {"type": "keyword"},
            }
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "spanish": {
                        "type": "spanish"
                    }
                }
            },
            "number_of_shards": 1,
            "number_of_replicas": 1
        }
    }
    return mapping


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PARA IA
# ═══════════════════════════════════════════════════════════════════════════════

PROMPT_ANALISIS_COMERCIAL = """Eres un analista comercial experto de SRS (System Rapid Solutions), empresa especializada en servicios de soporte IT, cableado estructurado e infraestructura.

Tu objetivo es analizar esta oportunidad de licitación y generar un informe COMPLETO orientado 100% a la ACCIÓN COMERCIAL. El operador comercial debe tener TODO lo necesario para contactar al adjudicatario y cerrar la subcontratación.

{catalogo_servicios}

DATOS DE LA OPORTUNIDAD:
- Objeto: {objeto}
- Importe: {importe:,.0f}€
- Adjudicatario: {adjudicatario_nombre} (CIF: {adjudicatario_cif})
- Órgano contratante: {organo_contratante}
- Fecha adjudicación: {fecha_adjudicacion}

TEXTO DEL PLIEGO:
---
{texto_pliego}
---

Genera un JSON con la siguiente estructura EXACTA:

{{
  "clasificacion": {{
    "nivel": "oro|plata|bronce|descartar",
    "score_total": 0-100,
    "score_desglose": {{
      "alineacion_servicios_srs": 0-30,
      "urgencia_temporal": 0-25,
      "volumen_economico": 0-20,
      "intensidad_dolor": 0-25,
      "cobertura_geografica": -10 a +20,
      "probabilidad_subcontratacion": 0-10
    }},
    "confianza_clasificacion": 0.0-1.0
  }},

  "en_30_segundos": {{
    "que_es": "Descripción clara en una frase de qué trata el contrato",
    "por_que_interesa": "Por qué es relevante para SRS (zona, servicios, urgencia)",
    "por_que_ahora": "Por qué hay que actuar ya (deadline, competencia)",
    "valor_estimado": "Rango de valor estimado para SRS como subcontratista"
  }},

  "adjudicatario": {{
    "nombre": "Nombre de la empresa adjudicataria",
    "cif": "CIF si está disponible",
    "conocemos": false,
    "historico_srs": "",
    "contacto_previo": null,
    "notas_crm": ""
  }},

  "cliente_final": {{
    "nombre": "Nombre del órgano contratante",
    "tipo": "Administración Central|Autonómica|Local|Universidad|Sanidad|etc.",
    "sector": "Sanidad|Educación|Justicia|Defensa|etc.",
    "tamaño": "Pequeño|Mediano|Grande",
    "ubicacion_principal": "Ciudad/Provincia"
  }},

  "dolor_principal": {{
    "descripcion": "El dolor principal que tiene el adjudicatario con este contrato",
    "por_que_duele": "Por qué esto es un problema para ellos (no tienen equipo, no es su core, plazo ajustado...)",
    "intensidad": "critico|alto|medio|bajo",
    "fecha_limite": "YYYY-MM-DD si existe"
  }},

  "dolores_secundarios": [
    {{
      "descripcion": "Descripción del dolor secundario",
      "servicio_srs": "Servicio del catálogo SRS que lo resuelve"
    }}
  ],

  "servicios_srs_aplicables": [
    {{
      "servicio": "Nombre EXACTO del servicio del catálogo SRS",
      "encaje": "perfecto|alto|medio|bajo",
      "volumen_estimado": "Cantidad estimada (ej: '500 puntos de red', '200 horas')",
      "valor_estimado": "Rango en euros (ej: '25.000€ - 35.000€')"
    }}
  ],

  "valor_oportunidad": {{
    "contrato_total": "Valor total del contrato",
    "estimacion_subcontratacion": "Rango de lo que podría facturar SRS",
    "margen_tipico": "Margen esperado (ej: '18-22%')",
    "recurrencia": "Posibilidad de trabajo recurrente posterior"
  }},

  "competencia": {{
    "competidores_probables": ["Lista de competidores que podrían ofertar"],
    "ventaja_srs": "Nuestra principal ventaja competitiva",
    "incumbente_anterior": "Quién tenía el contrato antes (si se sabe)",
    "por_que_ganamos": "Argumento principal de por qué deberían elegirnos"
  }},

  "requisitos_cumplimos": {{
    "tecnicos": [
      {{"requisito": "Requisito técnico del pliego", "cumple": true, "evidencia": "Por qué lo cumplimos"}}
    ],
    "economicos": [
      {{"requisito": "Requisito económico", "cumple": true, "evidencia": ""}}
    ],
    "no_cumplimos": ["Lista de requisitos que NO cumplimos (red flags)"]
  }},

  "alertas": [
    {{
      "tipo": "temporal|economico|logistico|legal|tecnico",
      "icono": "⏰|💰|🚗|⚖️|🔧",
      "mensaje": "Mensaje de alerta",
      "prioridad": "alta|media|baja"
    }}
  ],

  "red_flags": ["Lista de señales de alarma que podrían hacer descartar la oportunidad"],

  "comunicacion": {{
    "gancho_inicial": {{
      "whatsapp": "Mensaje corto y directo para WhatsApp (máx 200 caracteres)",
      "email_asunto": "Asunto del email",
      "llamada": "Script de apertura para llamada telefónica"
    }},
    "puntos_clave_conversacion": [
      "Punto 1: Problema → Nuestra solución",
      "Punto 2: Problema → Nuestra solución"
    ],
    "propuesta_valor": [
      "Bullet 1 de nuestra propuesta",
      "Bullet 2"
    ],
    "preguntas_cualificacion": [
      "¿Pregunta para cualificar la oportunidad?",
      "¿Otra pregunta?"
    ],
    "objeciones_probables": [
      {{
        "objecion": "Objeción esperada del cliente",
        "respuesta": "Respuesta preparada"
      }}
    ]
  }},

  "siguientes_pasos": {{
    "accion_inmediata": "Qué hacer ahora mismo",
    "fecha_limite_contacto": "YYYY-MM-DD fecha máxima para contactar",
    "si_no_responde": "Plan B si no hay respuesta",
    "preparar_antes": ["Lista de cosas a preparar antes de contactar"],
    "reunirse_con": "Próximo paso si hay interés"
  }},

  "documentos_relacionados": [
    {{
      "tipo": "pliego_tecnico|adjudicacion|anuncio",
      "url": "URL del documento",
      "paginas_clave": [12, 23, 45]
    }}
  ],

  "notas_analisis": [
    "Nota 1: Observación importante del análisis",
    "Nota 2: Otra observación"
  ],

  "copiar_pegar": {{
    "whatsapp_listo": "Mensaje completo de WhatsApp listo para copiar",
    "email_asunto_listo": "Asunto del email",
    "email_cuerpo_listo": "Cuerpo completo del email",
    "bullets_propuesta": "• Bullet 1\\n• Bullet 2\\n• Bullet 3",
    "telefono_directo": "Teléfono si está disponible",
    "linkedin_url": ""
  }},

  "contactos": [
    {{
      "id": "contacto_001",
      "fuente": "pliego|adjudicacion|perfil_contratante|web_empresa",
      "tipo_entidad": "adjudicatario|cliente_final|ute_miembro",
      "rol_decisor": "decisor|influenciador|tecnico|administrativo",
      "nivel_jerarquico": "c_level|direccion|gerencia|mando_intermedio|tecnico",
      "persona": {{
        "nombre_completo": "Nombre completo de la persona",
        "nombre": "Nombre",
        "apellidos": "Apellidos",
        "cargo": "Cargo en la empresa",
        "departamento": "Departamento",
        "antiguedad_estimada": "Si se puede estimar"
      }},
      "empresa": {{
        "nombre": "Nombre de la empresa",
        "cif": "CIF si disponible",
        "rol_en_contrato": "Adjudicatario principal|UTE miembro|etc."
      }},
      "contacto_directo": {{
        "email_profesional": "email@empresa.es",
        "email_alternativo": null,
        "telefono_movil": "+34 6XX XXX XXX si disponible",
        "telefono_fijo": "+34 9XX XXX XXX si disponible",
        "extension": "Extensión si disponible",
        "linkedin": "URL de LinkedIn si disponible",
        "twitter": null
      }},
      "disponibilidad": {{
        "horario_preferido": "mañanas|tardes|cualquiera",
        "mejor_dia": "lunes a viernes|martes a jueves|etc.",
        "canal_preferido": "whatsapp|email|llamada",
        "notas": "Notas sobre cómo contactar"
      }},
      "extraido_de": {{
        "documento": "Nombre del documento donde se encontró",
        "pagina": 45,
        "texto_original": "Fragmento literal donde aparece el contacto",
        "fecha_extraccion": "YYYY-MM-DD",
        "verificado": false
      }},
      "notas": "Notas adicionales sobre el contacto",
      "confianza_contacto": 0.0-1.0
    }}
  ],

  "contacto_recomendado": {{
    "id": "contacto_001",
    "razon": "Por qué recomendamos contactar a esta persona primero"
  }},

  "contactos_pendientes_buscar": [
    {{
      "rol": "Rol que falta por identificar",
      "empresa": "En qué empresa buscar",
      "sugerencia_busqueda": "Cómo buscar este contacto (ej: LinkedIn, web corporativa)"
    }}
  ]
}}

CRITERIOS DE SCORING:
- alineacion_servicios_srs: ¿Los servicios necesarios son core de SRS?
- urgencia_temporal: ¿Hay plazos ajustados que creen urgencia?
- volumen_economico: ¿El volumen justifica el esfuerzo comercial?
- intensidad_dolor: ¿El adjudicatario tiene un problema real?
- cobertura_geografica: +20 zona base, +10 zona cercana, 0 expansión, -10 islas/extranjero
- probabilidad_subcontratacion: ¿Es probable que necesiten subcontratar?

IMPORTANTE:
- USA NOMBRES EXACTOS DEL CATÁLOGO SRS para los servicios
- El gancho de WhatsApp debe ser CORTO y DIRECTO (no más de 200 caracteres)
- Las objeciones deben ser REALISTAS y las respuestas CONCRETAS
- La fecha_limite_contacto debe ser ANTES de que cierren con la competencia

EXTRACCIÓN DE CONTACTOS (MUY IMPORTANTE):
- Busca EXHAUSTIVAMENTE nombres, cargos, emails, teléfonos en el pliego
- Lugares donde buscar: responsables del contrato, contactos para dudas, firmas, anexos
- Incluye el fragmento LITERAL del pliego donde encontraste cada contacto
- Evalúa el rol: ¿es decisor? ¿influenciador? ¿técnico? ¿administrativo?
- Prioriza contactos del ADJUDICATARIO sobre los del órgano contratante
- Si no encuentras contactos del adjudicatario, sugiere cómo buscarlos (LinkedIn, web)
- El contacto_recomendado debe ser la MEJOR opción para el primer contacto comercial

RESPONDE SOLO JSON, sin explicaciones adicionales."""
