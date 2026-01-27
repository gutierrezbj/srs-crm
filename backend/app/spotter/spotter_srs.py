#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║                         SPOTTER SRS                               ║
║              "El que ve lo que otros no ven"                      ║
╠═══════════════════════════════════════════════════════════════════╣
║  Detector de oportunidades de subcontratación en PLACSP           ║
║  Identifica empresas con contratos adjudicados que necesitan      ║
║  capacidad de ejecución en los pilares de servicio SRS.           ║
╠═══════════════════════════════════════════════════════════════════╣
║  Pilares SRS:                                                     ║
║    1. Field Services / Soporte Onsite / Cableado                  ║
║    2. Cloud & Virtualización                                      ║
║    3. Ciberseguridad / ENS                                        ║
║    4. Comunicaciones Unificadas                                   ║
║    5. Healthcare IT (RIS/PACS)                                    ║
║  Diferencial: Soporte Internacional (10+ países)                  ║
╠═══════════════════════════════════════════════════════════════════╣
║  NO vendemos servicios. RESOLVEMOS problemas que YA tienen.       ║
╚═══════════════════════════════════════════════════════════════════╝

Autor: SRS - System Rapid Solutions
Web: www.systemrapidsolutions.com
Versión: 1.0
Fecha: Enero 2026
"""

import requests
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import re
import json
from enum import Enum

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

class NivelDolor(Enum):
    """Clasificación del nivel de urgencia/dolor del adjudicatario"""
    CRITICO = "🔴 CRÍTICO"      # < 30 días para ejecutar
    ALTO = "🟠 ALTO"            # 30-60 días
    MEDIO = "🟡 MEDIO"          # 60-90 días
    BAJO = "🟢 BAJO"            # > 90 días
    DESCONOCIDO = "⚪ SIN FECHA"


class TipoOportunidad(Enum):
    """Tipo de oportunidad para SRS - basado en pilares del portfolio"""
    # Pilares principales SRS
    SOPORTE_IT_HELPDESK = "🔧 Soporte IT / Helpdesk"           # Pilar 1
    SUBCONTRATACION_CABLEADO = "🔌 Cableado Estructurado"      # Pilar 1
    INFRAESTRUCTURA_CPD = "🖥️ Infraestructura / CPD"           # Pilar 1
    CLOUD_VIRTUALIZACION = "☁️ Cloud & Virtualización"         # Pilar 2
    CIBERSEGURIDAD_ENS = "🛡️ Ciberseguridad / ENS"             # Pilar 3
    COMUNICACIONES_UC = "📞 Comunicaciones Unificadas"         # Pilar 4
    HEALTHCARE_IT = "🏥 Healthcare IT (RIS/PACS)"              # Pilar 5
    FOTOVOLTAICA_ENERGIA = "☀️ Fotovoltaica / Energía"         # Pilar 6
    DRONES_CARTOGRAFIA = "🚁 Drones / Cartografía"             # Pilar 7 - LiDAR, fotogrametría, topografía
    # Diferenciales
    SOPORTE_INTERNACIONAL = "🌍 Soporte Internacional"         # Diferencial único
    # Genéricos
    REFUERZO_EJECUCION = "👥 Refuerzo Ejecución"
    CONSULTORIA_TECNICA = "📋 Consultoría Técnica"


# ============================================================================
# CPVs Y KEYWORDS (ampliados)
# ============================================================================

CPVS_DIGITALIZACION = {
    # Servicios IT generales
    "72000000": "Servicios TI general",
    "72100000": "Consultoría equipo informático",
    "72130000": "Consultoría planificación instalaciones informáticas",
    "72140000": "Pruebas aceptación equipo informático",
    "72150000": "Auditoría informática",
    "72200000": "Programación software",
    "72210000": "Programación paquetes software",
    "72220000": "Consultoría sistemas y técnica",
    "72230000": "Desarrollo software personalizado",
    "72240000": "Análisis sistemas y programación",
    "72250000": "Sistemas y apoyo",
    "72260000": "Servicios software",
    "72300000": "Servicios de datos",
    "72310000": "Proceso de datos",
    "72320000": "Servicios base de datos",
    "72400000": "Servicios Internet",
    "72500000": "Servicios informáticos",
    "72510000": "Gestión informática",
    "72600000": "Apoyo informático y consultoría",
    "72700000": "Servicios red informática",
    "72800000": "Auditoría informática",
    "72900000": "Backup y recuperación",
    # Instalación
    "51600000": "Instalación ordenadores y equipo oficina",
}

CPVS_CABLEADO = {
    # Cableado de red (del filtro de JuanCho)
    "32421000": "Cableado de red",
    "32521000": "Cable telecomunicaciones",
    "32551000": "Cables telefónicos y equipo asociado",
    "32551500": "Cables telefónicos",
    "32562000": "Cables fibra óptica",
    "32562100": "Fibra óptica transmisión información",
    "32562200": "Fibra óptica telecomunicación",
    "32562300": "Fibra óptica transmisión datos",
    "32581100": "Cable transmisión datos",
    "32581110": "Cable datos conductores múltiples",
    "32581120": "Cable datos conductores coaxiales",
    "32581130": "Cable datos aplicaciones especiales",
    # Instalaciones eléctricas/telecom
    "45310000": "Instalación eléctrica",
    "45311000": "Instalación cableado",
    "45311100": "Cableado eléctrico",
    "45311200": "Instalación eléctrica",
    "45314000": "Instalación telecomunicaciones",
    "45314300": "Infraestructura cableado",
    "45314310": "Tendido de cables",
    "45314320": "Instalación cableado informático",
    # Equipos de red
    "32400000": "Redes",
    "32410000": "Red de área local",
    "32420000": "Equipos de red",
    "32500000": "Telecomunicaciones",
    "32510000": "Sistema telecomunicaciones",
    "32520000": "Cables telecomunicaciones",
}

# CPVs de audiovisual que pueden tener cableado embebido (caso DXC/Salas Vistas ECON/000161/2022)
# Estos CPVs esconden trabajo de cableado/IT cuando el objeto menciona "comunicaciones", "red", etc.
CPVS_AUDIOVISUAL_RIESGO = {
    # Grupo 323xx - Audiovisual (CASO DXC: 32321300-2)
    "32320000": "Equipos audiovisuales",
    "32321000": "Proyección audiovisual",
    "32321300": "Equipos visualización audiovisual",  # CPV exacto caso DXC
    "32322000": "Equipos multimedia",
    "32323000": "Monitores vídeo",
    "32330000": "Grabación/reproducción vídeo",
    "32340000": "Micrófonos y altavoces",
    "32350000": "Equipos audio",
    # Videoconferencia
    "32232000": "Equipos videoconferencia",
    "48510000": "Software comunicaciones",
    "48515000": "Software videoconferencia",
    # Instalación AV
    "51310000": "Instalación equipos radio/TV/audio",
    "51311000": "Instalación equipos radio",
    "51312000": "Instalación equipos vídeo",
    "51313000": "Instalación equipos audio",
    # Cámaras
    "38651000": "Cámaras fotográficas",
    "38651600": "Cámaras digitales",
}

CPVS_OBRA_RIESGO = {
    "45210000": "Construcción edificios",
    "45212000": "Edificios varios",
    "45213000": "Edificios comerciales",
    "45214000": "Edificios educativos",
    "45215000": "Edificios sanitarios",
    "45216000": "Edificios servicios orden público",
    "45220000": "Obras ingeniería",
    "45300000": "Instalación en edificios",
    "45310000": "Instalación eléctrica",
    "45330000": "Fontanería",
    "45400000": "Acabado edificios",
}

# Keywords para detectar IT/cableado embebido en contratos de obra
# PESOS AJUSTADOS A SERVICIOS CORE DE SRS (basado en portfolio oficial)
KEYWORDS_DOLOR_IT = {
    # ═══════════════════════════════════════════════════════════════
    # PILAR 1: FIELD SERVICES / SOPORTE ONSITE (máxima prioridad)
    # Clientes: DXC, Telxius, Inditex
    # ═══════════════════════════════════════════════════════════════
    "soporte técnico": 10,
    "soporte tecnico": 10,
    "soporte onsite": 10,
    "soporte on-site": 10,
    "soporte on site": 10,
    "soporte presencial": 10,
    "field services": 10,
    "field service": 10,
    "smart hands": 10,
    "manos remotas": 10,
    "helpdesk": 10,
    "help desk": 10,
    "help-desk": 10,
    "service desk": 10,
    "centro de atención": 8,
    "centro de atencion": 8,
    "atención al usuario": 10,
    "atencion al usuario": 10,
    "mantenimiento informático": 10,
    "mantenimiento informatico": 10,
    "mantenimiento preventivo": 9,
    "mantenimiento correctivo": 9,
    "microinformática": 10,
    "microinformatica": 10,
    "puesto de trabajo": 8,
    "puestos de trabajo": 8,
    "soporte de usuarios": 10,
    "soporte a usuarios": 10,
    "incidencias": 6,
    "gestión de incidencias": 8,
    "gestion de incidencias": 8,
    "resolución de incidencias": 10,
    "resolucion de incidencias": 10,
    "soporte remoto": 8,
    "soporte nivel 1": 10,
    "soporte nivel 2": 10,
    "soporte nivel 3": 10,
    "soporte n1": 9,
    "soporte n2": 9,
    "soporte n3": 9,
    "wintel": 10,
    "o365": 9,
    "office 365": 8,
    
    # ═══════════════════════════════════════════════════════════════
    # PILAR 2: INFRAESTRUCTURA CLOUD Y VIRTUALIZACIÓN
    # Clientes: Allfunds, Madrid Digital
    # ═══════════════════════════════════════════════════════════════
    "servidor": 8,
    "servidores": 8,
    "virtualización": 9,
    "virtualizacion": 9,
    "vmware": 10,
    "vsphere": 10,
    "vcenter": 10,
    "esxi": 10,
    "vsan": 10,
    "hyper-v": 9,
    "proxmox": 9,
    "datacenter": 9,
    "data center": 9,
    "centro de datos": 9,
    "cpd": 9,
    "sala técnica": 8,
    "sala tecnica": 8,
    "montaje de servidores": 10,
    "desmontaje de servidores": 10,
    "rackeo": 10,
    "instalación de hardware": 10,
    "instalacion de hardware": 10,
    
    # Cloud (GCP, Azure, AWS)
    "cloud": 7,
    "nube": 7,
    "azure": 9,
    "aws": 9,
    "amazon web services": 9,
    "google cloud": 9,
    "gcp": 9,
    "migración cloud": 10,
    "migracion cloud": 10,
    "migración a la nube": 10,
    "migracion a la nube": 10,
    "cloud híbrido": 9,
    "cloud hibrido": 9,
    
    # Almacenamiento
    "storage": 7,
    "almacenamiento": 7,
    "dell poweredge": 9,
    "hpe": 8,
    "lenovo": 7,
    
    # ═══════════════════════════════════════════════════════════════
    # PILAR 3: CIBERSEGURIDAD Y ENS (diferencial sector público)
    # ═══════════════════════════════════════════════════════════════
    "ciberseguridad": 9,
    "seguridad informática": 9,
    "seguridad informatica": 9,
    "seguridad de la información": 9,
    "seguridad de la informacion": 9,
    "esquema nacional de seguridad": 10,
    "ens": 10,
    "iso 27001": 10,
    "iso 27701": 10,
    "soc 24/7": 10,
    "soc": 8,
    "monitorización": 7,
    "monitorizacion": 7,
    "detección de amenazas": 9,
    "deteccion de amenazas": 9,
    "backup": 8,
    "veeam": 10,
    "disaster recovery": 10,
    "plan de contingencia": 9,
    "hardening": 10,
    "bastionado": 10,
    "firewall": 7,
    "antivirus": 6,
    "copia de seguridad": 8,
    "copias de seguridad": 8,
    
    # ═══════════════════════════════════════════════════════════════
    # PILAR 4: COMUNICACIONES UNIFICADAS
    # ═══════════════════════════════════════════════════════════════
    "comunicaciones unificadas": 10,
    "microsoft teams": 9,
    "ms teams": 9,
    "teams": 7,
    "zoom": 7,
    "google workspace": 9,
    "microsoft 365": 8,
    "m365": 8,
    
    # ═══════════════════════════════════════════════════════════════
    # PILAR 5: HEALTHCARE IT (nicho especializado)
    # ═══════════════════════════════════════════════════════════════
    "dicom": 10,
    "ris": 8,
    "pacs": 10,
    "ris/pacs": 10,
    "imagen médica": 10,
    "imagen medica": 10,
    "healthcare": 8,
    "sanidad": 6,
    "hospital": 5,
    "clínica": 5,
    "clinica": 5,
    
    # ═══════════════════════════════════════════════════════════════
    # SERVICIOS GESTIONADOS (MSP) - modelo de negocio SRS
    # ═══════════════════════════════════════════════════════════════
    "servicios gestionados": 10,
    "msp": 10,
    "managed services": 10,
    "outsourcing": 8,
    "externalización": 8,
    "externalizacion": 8,
    "team augmentation": 10,
    "refuerzo de equipo": 9,
    "sla": 7,
    "acuerdo de nivel de servicio": 8,
    
    # ═══════════════════════════════════════════════════════════════
    # DIGITALIZACIÓN (oportunidad pero revisar alcance)
    # ═══════════════════════════════════════════════════════════════
    "digitalización": 6,
    "digitalizacion": 6,
    "transformación digital": 6,
    "transformacion digital": 6,
    
    # ═══════════════════════════════════════════════════════════════
    # DESARROLLO SOFTWARE - BAJA PRIORIDAD (no es core SRS)
    # ═══════════════════════════════════════════════════════════════
    "software": 2,
    "aplicación": 2,
    "aplicacion": 2,
    "desarrollo": 2,
    "programación": 2,
    "programacion": 2,
    "web": 1,
    "app": 2,
    "erp": 3,
    "crm": 3,
    "sap": 3,
}

KEYWORDS_DOLOR_CABLEADO = {
    # ═══════════════════════════════════════════════════════════════
    # CORE SRS - CABLEADO ESTRUCTURADO (máxima prioridad)
    # ═══════════════════════════════════════════════════════════════
    "cableado estructurado": 10,
    "cableado de red": 10,
    "cableado": 7,
    "cable utp": 10,
    "cat5": 8,
    "cat5e": 9,
    "cat6": 10,
    "cat6a": 10,
    "cat7": 10,
    "categoría 6": 10,
    "categoria 6": 10,
    
    # Fibra óptica
    "fibra óptica": 10,
    "fibra optica": 10,
    "fibra monomodo": 10,
    "fibra multimodo": 10,
    "tendido de fibra": 10,
    "fusión de fibra": 10,
    "fusion de fibra": 10,
    
    # Componentes pasivos
    "patch panel": 10,
    "panel de parcheo": 10,
    "roseta": 8,
    "rosetas": 8,
    "toma de datos": 10,
    "tomas de datos": 10,
    "punto de red": 10,
    "puntos de red": 10,
    "conectores rj45": 8,
    "rj45": 7,
    "latiguillos": 7,
    
    # ═══════════════════════════════════════════════════════════════
    # CORE SRS - INFRAESTRUCTURA RACK/CPD
    # ═══════════════════════════════════════════════════════════════
    "rack": 8,
    "armario rack": 10,
    "armario de comunicaciones": 10,
    "rack de comunicaciones": 10,
    "bastidor": 7,
    
    # Canalizaciones
    "canalización": 6,
    "canalizacion": 6,
    "bandeja": 5,
    "bandeja portacables": 8,
    "tubo corrugado": 5,
    "canaleta": 5,
    "canal protector": 6,
    
    # ═══════════════════════════════════════════════════════════════
    # CORE SRS - RED Y WIFI
    # ═══════════════════════════════════════════════════════════════
    "red de datos": 10,
    "red local": 8,
    "lan": 7,
    "wlan": 8,
    "wifi": 8,
    "wi-fi": 8,
    "red inalámbrica": 8,
    "red inalambrica": 8,
    "punto de acceso": 8,
    "puntos de acceso": 8,
    "access point": 8,
    "switch": 7,
    "switches": 7,
    "router": 6,
    "electrónica de red": 9,
    "electronica de red": 9,
    
    # Telefonía/Voz
    "telecomunicaciones": 7,
    "voz y datos": 10,
    "telefonía ip": 8,
    "telefonia ip": 8,
    "voip": 7,
    
    # ═══════════════════════════════════════════════════════════════
    # CERTIFICACIÓN (valor añadido SRS)
    # ═══════════════════════════════════════════════════════════════
    "certificación": 8,
    "certificacion": 8,
    "certificado": 6,
    "medición": 6,
    "medicion": 6,
    "fluke": 9,
    "test de certificación": 10,
    "test de certificacion": 10,
}

# Keywords AUDIOVISUAL que implican cableado (caso Salas de Vistas DXC - ECON/000161/2022)
KEYWORDS_AUDIOVISUAL_CON_CABLEADO = {
    # Salas judiciales (caso exacto DXC 5.9M EUR)
    "salas de vistas": 5,
    "sala de vistas": 5,
    "juicios telemáticos": 5,
    "juicios telematicos": 5,
    "grabación de vistas": 5,
    "grabacion de vistas": 5,
    
    # Audiovisual con infraestructura
    "acondicionamiento audiovisual": 5,
    "audiovisual y comunicaciones": 5,
    "audiovisual y de comunicaciones": 5,
    "equipamiento audiovisual": 4,
    "sistema audiovisual": 4,
    "instalación audiovisual": 5,
    "instalacion audiovisual": 5,
    
    # Videoconferencia (implica cableado de red)
    "videoconferencia": 5,
    "video conferencia": 5,
    "telepresencia": 5,
    "streaming": 4,
    "retransmisión": 4,
    "retransmision": 4,
    
    # Salas de reuniones/conferencias
    "sala de reuniones": 4,
    "sala de conferencias": 4,
    "sala polivalente": 3,
    "salón de actos": 4,
    "salon de actos": 4,
    "auditorio": 3,
}

# Indicadores de FONDOS EUROPEOS (presión de plazos GARANTIZADA)
KEYWORDS_FONDOS_EU = {
    "next generation": 5,
    "nextgeneration": 5,
    "plan de recuperación": 5,
    "plan de recuperacion": 5,
    "prtr": 5,
    "fondos europeos": 4,
    "mecanismo de recuperación": 4,
    "mecanismo de recuperacion": 4,
    "transformación y resiliencia": 5,
    "transformacion y resiliencia": 5,
}

# Keywords de ALCANCE INTERNACIONAL (diferencial único SRS: 10+ países)
KEYWORDS_INTERNACIONAL = {
    # Indicadores generales
    "internacional": 8,
    "multi-país": 10,
    "multi-pais": 10,
    "multipais": 10,
    "multinacional": 8,
    "multisede": 10,
    "multi-sede": 10,
    "múltiples sedes": 10,
    "multiples sedes": 10,
    "múltiples ubicaciones": 9,
    "multiples ubicaciones": 9,
    "sedes internacionales": 10,
    "oficinas internacionales": 10,
    "delegaciones": 7,
    "filiales": 7,
    "subsidiarias": 7,
    "global": 6,
    "worldwide": 8,
    
    # Regiones donde opera SRS
    "latam": 10,
    "latinoamérica": 10,
    "latinoamerica": 10,
    "américa latina": 10,
    "america latina": 10,
    "europa": 6,
    "estados unidos": 8,
    "usa": 7,
    "eeuu": 7,
    
    # Países específicos donde SRS tiene presencia
    "méxico": 8,
    "mexico": 8,
    "perú": 8,
    "peru": 8,
    "colombia": 8,
    "chile": 8,
    "argentina": 8,
    "brasil": 8,
    "venezuela": 8,
    "uruguay": 8,
    "florida": 8,
    "reino unido": 7,
    "uk": 7,
    "arabia saudí": 8,
    "arabia saudi": 8,
    "saudi arabia": 8,
    
    # Idiomas (SRS ofrece ES/EN/PT)
    "multilingüe": 9,
    "multilingue": 9,
    "bilingüe": 7,
    "bilingue": 7,
    "español e inglés": 9,
    "espanol e ingles": 9,
    "portugués": 7,
    "portugues": 7,
}

# ═══════════════════════════════════════════════════════════════
# PILAR 6: FOTOVOLTAICA / ENERGÍA
# ═══════════════════════════════════════════════════════════════
KEYWORDS_FOTOVOLTAICA = {
    # Instalaciones solares
    "fotovoltaica": 10,
    "fotovoltaico": 10,
    "solar": 8,
    "paneles solares": 10,
    "placas solares": 10,
    "módulos fotovoltaicos": 10,
    "modulos fotovoltaicos": 10,
    "autoconsumo": 10,
    "autoconsumo solar": 10,
    "autoconsumo fotovoltaico": 10,

    # Componentes
    "inversor solar": 9,
    "inversores": 7,
    "string inverter": 9,
    "microinversor": 9,
    "optimizador": 7,
    "monitorización solar": 9,
    "monitorizacion solar": 9,

    # Potencia
    "kwp": 8,
    "mwp": 9,
    "kilovatios pico": 8,
    "megavatios pico": 9,

    # Tipos de instalación
    "cubierta solar": 10,
    "marquesina fotovoltaica": 10,
    "pérgola fotovoltaica": 10,
    "pergola fotovoltaica": 10,
    "parking solar": 10,
    "huerto solar": 8,
    "planta fotovoltaica": 9,

    # Almacenamiento
    "baterías": 7,
    "baterias": 7,
    "almacenamiento energético": 9,
    "almacenamiento energetico": 9,
    "sistema de almacenamiento": 8,

    # Eficiencia energética relacionada
    "eficiencia energética": 7,
    "eficiencia energetica": 7,
    "certificación energética": 6,
    "certificacion energetica": 6,
    "ahorro energético": 7,
    "ahorro energetico": 7,
}

# CPVs de energía solar/fotovoltaica
CPVS_FOTOVOLTAICA = {
    "09331200": "Módulos solares fotovoltaicos",
    "09332000": "Instalación solar",
    "45261215": "Trabajos de instalación de paneles solares",
    "45311000": "Instalación de cableado y accesorios eléctricos",  # Cuando incluye solar
    "45251100": "Construcción de centrales eléctricas",
    "31712331": "Células fotovoltaicas",
    "31712332": "Paneles fotovoltaicos",
    "09331000": "Paneles solares",
    "09330000": "Energía solar",
    "71314000": "Energía y servicios conexos",
    "45251160": "Instalación de energía solar",
}

# Indicadores de plazos cortos (DOLOR ALTO)
KEYWORDS_URGENCIA = [
    "urgente", "urgencia", "inmediato", "inmediata",
    "plazo improrrogable", "fecha límite", "fecha limite",
    "penalización", "penalizacion", "penalidad",
    "ejecución rápida", "ejecucion rapida",
]

# ═══════════════════════════════════════════════════════════════
# KEYWORDS QUE DEBEN MATCHEAR COMO PALABRAS COMPLETAS
# (evitar falsos positivos como "potencia" → "ens")
# ═══════════════════════════════════════════════════════════════
KEYWORDS_PALABRA_COMPLETA = {
    "ens",      # Esquema Nacional de Seguridad, no "pot-ens-ia"
    "soc",      # Security Operations Center, no "a-soc-iación"
    "ris",      # Radiology Information System, no "tu-ris-mo"
    "cpd",      # Centro de Proceso de Datos
    "lan",      # Local Area Network, no "p-lan"
    "msp",      # Managed Service Provider
    "gcp",      # Google Cloud Platform
    "aws",      # Amazon Web Services
    "erp",      # Enterprise Resource Planning
    "crm",      # Customer Relationship Management
    "sap",      # SAP software
    "app",      # Aplicación
    "web",      # Web
}


# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class PliegoInfo:
    """Información extraída de los pliegos"""
    url_pliego_tecnico: Optional[str] = None
    url_pliego_administrativo: Optional[str] = None
    url_otros_documentos: List[str] = field(default_factory=list)
    

@dataclass
class AnalisisDolor:
    """Análisis del dolor/urgencia del adjudicatario"""
    nivel: NivelDolor
    dias_hasta_fin: Optional[int]
    fecha_fin_contrato: Optional[str]
    duracion_meses: Optional[int]
    indicadores_urgencia: List[str]
    score_dolor: int  # 0-100
    tipo_oportunidad: TipoOportunidad
    

@dataclass 
class Adjudicacion:
    """Adjudicación detectada con análisis completo"""
    # Datos básicos
    expediente: str
    objeto: str
    adjudicatario: str
    nif_adjudicatario: Optional[str]
    importe: float
    fecha_adjudicacion: str
    organo_contratacion: str
    cpv: str
    cpv_descripcion: str
    url: str
    
    # Clasificación
    tipo_match: str
    keywords_encontradas: Dict[str, int]  # keyword -> peso
    es_pyme: bool
    
    # Análisis de dolor
    dolor: AnalisisDolor
    
    # Documentación
    pliegos: PliegoInfo
    
    # Datos para contacto
    email_organo: Optional[str] = None
    telefono_organo: Optional[str] = None
    
    def score_total(self) -> int:
        """Calcula score total de la oportunidad (0-100)"""
        score = self.dolor.score_dolor
        
        # Bonus por importe
        if self.importe > 500000:
            score += 15
        elif self.importe > 200000:
            score += 10
        elif self.importe > 100000:
            score += 5
            
        # Bonus si es PYME (más probable que necesite ayuda)
        if self.es_pyme:
            score += 10
            
        # Bonus por keywords de alto valor
        for kw, peso in self.keywords_encontradas.items():
            if peso >= 5:
                score += 3
                
        return min(100, score)


# ============================================================================
# NAMESPACES XML
# ============================================================================

NS = {
    'cac-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2',
    'cbc-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2',
    'atom': 'http://www.w3.org/2005/Atom',
    'cbc': 'urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2',
    'cfs': 'urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2',
}


# ============================================================================
# FUNCIONES DE ANÁLISIS DE DOLOR
# ============================================================================

def calcular_dolor(
    objeto: str,
    fecha_adjudicacion: str,
    duracion_dias: Optional[int],
    cpv: str,
    keywords: Dict[str, int]
) -> AnalisisDolor:
    """
    Calcula el nivel de dolor/urgencia basado en múltiples factores.
    """
    objeto_lower = objeto.lower()
    indicadores = []
    score = 0
    
    # 1. Análisis de plazos
    dias_hasta_fin = None
    fecha_fin = None
    duracion_meses = None
    
    if duracion_dias and fecha_adjudicacion:
        try:
            fecha_adj = datetime.strptime(fecha_adjudicacion, "%Y-%m-%d")
            fecha_fin_dt = fecha_adj + timedelta(days=duracion_dias)
            fecha_fin = fecha_fin_dt.strftime("%Y-%m-%d")
            dias_hasta_fin = (fecha_fin_dt - datetime.now()).days
            duracion_meses = duracion_dias // 30
            
            if dias_hasta_fin < 30:
                score += 40
                indicadores.append(f"⚠️ Solo {dias_hasta_fin} días para fin de contrato")
            elif dias_hasta_fin < 60:
                score += 30
                indicadores.append(f"Plazo ajustado: {dias_hasta_fin} días")
            elif dias_hasta_fin < 90:
                score += 20
                indicadores.append(f"Plazo moderado: {dias_hasta_fin} días")
            else:
                score += 10
        except:
            pass
    
    # 2. Keywords de urgencia en objeto
    for kw in KEYWORDS_URGENCIA:
        if kw in objeto_lower:
            score += 15
            indicadores.append(f"Urgencia detectada: '{kw}'")
    
    # 3. Score por keywords técnicas
    keyword_score = sum(keywords.values())
    if keyword_score > 20:
        score += 20
        indicadores.append("Alta complejidad técnica")
    elif keyword_score > 10:
        score += 10
        indicadores.append("Complejidad técnica media")
    
    # 4. Determinar tipo de oportunidad (priorizado para pilares SRS)
    cpv_base = cpv[:5] if cpv else ""
    cpv_8 = cpv[:8] if cpv else ""
    keywords_lower = {k.lower(): v for k, v in keywords.items()}

    # ═══════════════════════════════════════════════════════════════
    # FUNCIÓN HELPER PARA DETECTAR KEYWORDS CON VALIDACIÓN
    # ═══════════════════════════════════════════════════════════════
    def tiene_keyword(texto: str, lista_keywords: list) -> bool:
        """
        Detecta si alguna keyword de la lista está en el texto.
        Para keywords cortas (en KEYWORDS_PALABRA_COMPLETA), valida palabra completa.
        """
        import re
        for kw in lista_keywords:
            kw_lower = kw.lower()
            if kw_lower in KEYWORDS_PALABRA_COMPLETA:
                # Validar como palabra completa
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, texto, re.IGNORECASE):
                    return True
            else:
                # Búsqueda normal por subcadena
                if kw_lower in texto:
                    return True
        return False

    # ═══════════════════════════════════════════════════════════════
    # DETECCIÓN POR KEYWORDS (basado en pilares del portfolio SRS)
    # ═══════════════════════════════════════════════════════════════

    # PILAR 6: Fotovoltaica / Energía (NUEVO - alta prioridad)
    kw_fotovoltaica = ["fotovoltaica", "fotovoltaico", "paneles solares", "placas solares",
                       "autoconsumo", "solar", "módulos fotovoltaicos", "modulos fotovoltaicos",
                       "inversor solar", "kwp", "mwp", "cubierta solar", "planta fotovoltaica",
                       "marquesina fotovoltaica", "pérgola fotovoltaica", "pergola fotovoltaica"]

    # PILAR 1: Field Services / Soporte Onsite
    kw_soporte = ["soporte técnico", "soporte tecnico", "helpdesk", "help desk",
                  "microinformática", "microinformatica", "atención al usuario",
                  "atencion al usuario", "service desk", "mantenimiento informático",
                  "mantenimiento informatico", "soporte a usuarios", "soporte de usuarios",
                  "soporte onsite", "soporte on-site", "field service", "smart hands",
                  "wintel", "soporte nivel", "soporte n1", "soporte n2"]

    # PILAR 1: Cableado e Infraestructura Física
    kw_cableado = ["cableado", "fibra", "red de datos", "cat6", "cat6a",
                   "puntos de red", "tomas de datos", "rack", "patch panel",
                   "cableado estructurado", "fibra óptica", "fibra optica",
                   "rackeo", "instalación de hardware", "certificación de red"]

    # PILAR 1: CPD / Data Center (cpd requiere palabra completa)
    kw_cpd = ["datacenter", "data center", "centro de datos", "cpd", "sala técnica",
              "montaje de servidores", "desmontaje", "servidor", "servidores"]

    # PILAR 2: Cloud & Virtualización (aws, gcp requieren palabra completa)
    kw_cloud = ["vmware", "vsphere", "vcenter", "esxi", "vsan", "hyper-v", "proxmox",
                "azure", "aws", "google cloud", "gcp", "migración cloud", "cloud híbrido",
                "virtualización", "virtualizacion"]

    # PILAR 3: Ciberseguridad / ENS (ens, soc requieren palabra completa)
    kw_ciber = ["ciberseguridad", "seguridad informática", "seguridad informatica",
                "ens", "esquema nacional de seguridad",
                "iso 27001", "soc 24/7", "soc", "veeam", "backup", "disaster recovery",
                "hardening", "bastionado", "monitorización de seguridad"]

    # PILAR 4: Comunicaciones Unificadas
    kw_uc = ["comunicaciones unificadas", "microsoft teams", "ms teams", "zoom",
             "google workspace", "videoconferencia", "telepresencia"]

    # PILAR 5: Healthcare IT (ris requiere palabra completa)
    kw_health = ["dicom", "pacs", "ris/pacs", "ris", "imagen médica", "imagen medica",
                 "healthcare", "radiología", "radiologia"]

    # DIFERENCIAL: Internacional
    kw_internacional = ["internacional", "multi-país", "multi-pais", "multinacional",
                        "multisede", "múltiples sedes", "sedes internacionales",
                        "latam", "latinoamérica", "latinoamerica", "worldwide"]

    # PILAR 7: Drones / Cartografía (LiDAR, fotogrametría, topografía aérea)
    # Keywords que indican captura/vuelo (contexto SRS)
    kw_drones_captura = ["vuelo", "vuelos", "dron", "drones", "rpas", "uav",
                         "fotogrametría", "fotogrametria", "ortofoto", "ortofotos",
                         "topografía aérea", "topografia aerea", "levantamiento aéreo",
                         "captura aérea", "captura aerea", "escáner láser", "escaner laser"]
    # Keywords que pueden ser LiDAR de captura o LiDAR de procesamiento
    kw_lidar_contexto = ["lidar", "nube de puntos", "nubes de puntos", "laser escáner",
                         "mdt", "mds", "modelo digital", "punto kilométrico"]
    # Keywords que confirman contexto de cartografía/obra (no solo datos)
    kw_contexto_cartografia = ["cartografía", "cartografia", "cartográfico", "cartografico",
                               "seguimiento de obra", "control de obra", "avance de obra",
                               "gemelo digital", "as-built", "asbuilt", "volumetría", "volumetria",
                               "cubicación", "cubicacion", "estereoscop", "restitución", "restitucion"]
    # Keywords que indican que es solo procesamiento/almacenamiento de datos (NO es SRS drones)
    kw_solo_datos = ["espacio de datos", "data space", "almacenamiento de datos",
                     "procesamiento de datos", "gestión de datos", "plataforma de datos",
                     "lago de datos", "data lake", "big data", "interoperabilidad"]

    # ═══════════════════════════════════════════════════════════════
    # CLASIFICACIÓN POR PRIORIDAD (usando validación de palabra completa)
    # ═══════════════════════════════════════════════════════════════
    tiene_fotovoltaica = tiene_keyword(objeto_lower, kw_fotovoltaica)
    tiene_soporte = tiene_keyword(objeto_lower, kw_soporte)
    tiene_cableado = tiene_keyword(objeto_lower, kw_cableado)
    tiene_cpd = tiene_keyword(objeto_lower, kw_cpd)

    # Detección inteligente de Drones/Cartografía
    tiene_drones_captura = tiene_keyword(objeto_lower, kw_drones_captura)
    tiene_lidar = tiene_keyword(objeto_lower, kw_lidar_contexto)
    tiene_contexto_cartografia = tiene_keyword(objeto_lower, kw_contexto_cartografia)
    tiene_solo_datos = tiene_keyword(objeto_lower, kw_solo_datos)

    # LiDAR + contexto de vuelo/cartografía = Drones/Cartografía
    # LiDAR + contexto de datos/almacenamiento = NO es Drones (es IT)
    es_drones_cartografia = (
        tiene_drones_captura or  # Keywords claras de vuelo/captura
        tiene_contexto_cartografia or  # Keywords de cartografía/obra
        (tiene_lidar and not tiene_solo_datos)  # LiDAR sin contexto de "solo datos"
    )
    tiene_cloud = tiene_keyword(objeto_lower, kw_cloud)
    tiene_ciber = tiene_keyword(objeto_lower, kw_ciber)
    tiene_uc = tiene_keyword(objeto_lower, kw_uc)
    tiene_health = tiene_keyword(objeto_lower, kw_health)
    tiene_internacional = tiene_keyword(objeto_lower, kw_internacional)

    # Verificar CPV de fotovoltaica
    es_cpv_fotovoltaica = any(cpv_8.startswith(code[:5]) for code in CPVS_FOTOVOLTAICA.keys())

    # Clasificación jerárquica (fotovoltaica tiene alta prioridad)
    if tiene_fotovoltaica or es_cpv_fotovoltaica:
        tipo = TipoOportunidad.FOTOVOLTAICA_ENERGIA
        indicadores.append("☀️ Pilar 6 SRS: Fotovoltaica / Energía")
    elif es_drones_cartografia:
        tipo = TipoOportunidad.DRONES_CARTOGRAFIA
        indicadores.append("🚁 Pilar 7 SRS: Drones / Cartografía")
    elif tiene_health:
        tipo = TipoOportunidad.HEALTHCARE_IT
        indicadores.append("🏥 Pilar SRS: Healthcare IT")
    elif tiene_soporte and tiene_internacional:
        tipo = TipoOportunidad.SOPORTE_INTERNACIONAL
        indicadores.append("🌍 Diferencial SRS: Soporte Internacional")
    elif tiene_soporte:
        tipo = TipoOportunidad.SOPORTE_IT_HELPDESK
        indicadores.append("🔧 Pilar 1 SRS: Soporte IT / Helpdesk")
    elif tiene_cableado:
        tipo = TipoOportunidad.SUBCONTRATACION_CABLEADO
        indicadores.append("🔌 Pilar 1 SRS: Cableado Estructurado")
    elif tiene_cpd:
        tipo = TipoOportunidad.INFRAESTRUCTURA_CPD
        indicadores.append("🖥️ Pilar 1 SRS: Infraestructura CPD")
    elif tiene_cloud:
        tipo = TipoOportunidad.CLOUD_VIRTUALIZACION
        indicadores.append("☁️ Pilar 2 SRS: Cloud & Virtualización")
    elif tiene_ciber:
        tipo = TipoOportunidad.CIBERSEGURIDAD_ENS
        indicadores.append("🛡️ Pilar 3 SRS: Ciberseguridad / ENS")
    elif tiene_uc:
        tipo = TipoOportunidad.COMUNICACIONES_UC
        indicadores.append("📞 Pilar 4 SRS: Comunicaciones Unificadas")
    elif cpv_base.startswith("72"):
        tipo = TipoOportunidad.REFUERZO_EJECUCION
    elif cpv_base.startswith("453") or cpv_base.startswith("324") or cpv_base.startswith("325"):
        tipo = TipoOportunidad.SUBCONTRATACION_CABLEADO
        indicadores.append("🔌 Pilar 1 SRS: Cableado (por CPV)")
    else:
        tipo = TipoOportunidad.CONSULTORIA_TECNICA
    
    # 5. Determinar nivel de dolor
    if dias_hasta_fin is not None:
        if dias_hasta_fin < 30:
            nivel = NivelDolor.CRITICO
        elif dias_hasta_fin < 60:
            nivel = NivelDolor.ALTO
        elif dias_hasta_fin < 90:
            nivel = NivelDolor.MEDIO
        else:
            nivel = NivelDolor.BAJO
    elif score > 50:
        nivel = NivelDolor.ALTO
    elif score > 30:
        nivel = NivelDolor.MEDIO
    else:
        nivel = NivelDolor.DESCONOCIDO
    
    return AnalisisDolor(
        nivel=nivel,
        dias_hasta_fin=dias_hasta_fin,
        fecha_fin_contrato=fecha_fin,
        duracion_meses=duracion_meses,
        indicadores_urgencia=indicadores,
        score_dolor=min(100, score),
        tipo_oportunidad=tipo
    )


def es_palabra_completa(texto: str, keyword: str) -> bool:
    """
    Verifica si la keyword aparece como palabra completa en el texto.
    Evita falsos positivos como "potencia" matcheando con "ens".
    """
    import re
    # \b marca límite de palabra (word boundary)
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, texto, re.IGNORECASE))


def extraer_keywords(objeto: str) -> Dict[str, int]:
    """Extrae keywords con sus pesos del objeto del contrato"""
    objeto_lower = objeto.lower()
    encontradas = {}

    # Buscar en todos los diccionarios de keywords
    todos_keywords = {
        **KEYWORDS_DOLOR_IT,
        **KEYWORDS_DOLOR_CABLEADO,
        **KEYWORDS_AUDIOVISUAL_CON_CABLEADO,
        **KEYWORDS_FONDOS_EU,
        **KEYWORDS_INTERNACIONAL,
        **KEYWORDS_FOTOVOLTAICA,  # Añadir keywords de fotovoltaica
    }

    for kw, peso in todos_keywords.items():
        kw_lower = kw.lower()

        # Para keywords cortas que pueden causar falsos positivos,
        # verificar que sea palabra completa
        if kw_lower in KEYWORDS_PALABRA_COMPLETA:
            if es_palabra_completa(objeto_lower, kw_lower):
                encontradas[kw] = peso
        else:
            # Para keywords normales, búsqueda por subcadena
            if kw_lower in objeto_lower:
                encontradas[kw] = peso

    return encontradas


def clasificar_cpv(cpv: str) -> tuple:
    """Retorna (tipo_match, descripcion_cpv)"""
    cpv_base = cpv[:8] if cpv else ""
    cpv_5 = cpv[:5] if cpv else ""
    
    # Buscar en digitalizacion
    for code, desc in CPVS_DIGITALIZACION.items():
        if cpv_base.startswith(code[:5]):
            return ("CPV_IT", desc)
    
    # Buscar en cableado
    for code, desc in CPVS_CABLEADO.items():
        if cpv_base.startswith(code[:5]):
            return ("CPV_CABLEADO", desc)
    
    # Buscar en audiovisual (puede tener cableado embebido)
    for code, desc in CPVS_AUDIOVISUAL_RIESGO.items():
        if cpv_base.startswith(code[:5]):
            return ("CPV_AUDIOVISUAL", desc)
    
    # Buscar en obra
    for code, desc in CPVS_OBRA_RIESGO.items():
        if cpv_base.startswith(code[:5]):
            return ("CPV_OBRA", desc)
    
    return ("OTRO", "No clasificado")


# ============================================================================
# PARSING DE FEED
# ============================================================================

def parse_entry(entry: ET.Element) -> Optional[Adjudicacion]:
    """Parsea un entry del feed ATOM de PLACSP"""
    try:
        # Extraer título (objeto)
        title = entry.find('{http://www.w3.org/2005/Atom}title')
        objeto = title.text.strip() if title is not None and title.text else ""
        
        # Extraer URL
        link = entry.find('{http://www.w3.org/2005/Atom}link')
        url = link.get('href', '') if link is not None else ""
        
        # Buscar ContractFolderStatus directamente en entry (formato PLACSP real)
        cfs = None
        for child in entry.iter():
            if 'ContractFolderStatus' in child.tag:
                cfs = child
                break
        
        if cfs is None:
            return None
        
        # Extraer estado
        estado = ""
        for elem in cfs.iter():
            if 'ContractFolderStatusCode' in elem.tag:
                estado = elem.text or ""
                break
        
        # Solo ADJUDICADA o RESUELTA
        if estado not in ["ADJ", "RES", "ADJUDICADA", "RESUELTA"]:
            return None
        
        # Extraer expediente
        expediente = ""
        for elem in cfs.iter():
            if 'ContractFolderID' in elem.tag:
                expediente = elem.text or ""
                break
        
        # Extraer CPV
        cpv = ""
        for elem in cfs.iter():
            if 'ItemClassificationCode' in elem.tag:
                cpv = elem.text or ""
                break
        
        # Extraer adjudicatario
        adjudicatario = "No especificado"
        nif = None
        es_pyme = False
        
        for elem in cfs.iter():
            if 'WinningParty' in elem.tag:
                for sub in elem.iter():
                    if sub.tag.endswith('Name') and sub.text:
                        adjudicatario = sub.text.strip()
                    if sub.tag.endswith('ID') and sub.text and len(sub.text) == 9:
                        nif = sub.text
                    if 'SMEAwardedIndicator' in sub.tag:
                        es_pyme = sub.text == "true"
                break
        
        # Extraer importe
        importe = 0.0
        for elem in cfs.iter():
            if 'TotalAmount' in elem.tag or 'TaxExclusiveAmount' in elem.tag:
                try:
                    importe = float(elem.text)
                except:
                    pass
                break
        
        # Extraer fecha adjudicación
        fecha = ""
        for elem in cfs.iter():
            if 'AwardDate' in elem.tag and elem.text:
                fecha = elem.text
                break
        
        # Extraer órgano
        organo = ""
        for elem in cfs.iter():
            if 'LocatedContractingParty' in elem.tag:
                for sub in elem.iter():
                    if sub.tag.endswith('Name') and sub.text:
                        organo = sub.text.strip()
                        break
                break
        
        # Extraer duración
        duracion_dias = None
        for elem in cfs.iter():
            if 'DurationMeasure' in elem.tag and elem.text:
                try:
                    duracion_dias = int(float(elem.text))
                    # Comprobar unidad
                    unit = elem.get('unitCode', 'DAY')
                    if unit == 'MON':
                        duracion_dias *= 30
                    elif unit == 'ANN':
                        duracion_dias *= 365
                except:
                    pass
                break
        
        # Extraer URLs de pliegos
        pliegos = PliegoInfo()
        for elem in cfs.iter():
            if 'DocumentReference' in elem.tag:
                doc_url = ""
                doc_type = ""
                for sub in elem.iter():
                    if sub.tag.endswith('URI') and sub.text:
                        doc_url = sub.text
                    if 'DocumentTypeCode' in sub.tag and sub.text:
                        doc_type = sub.text
                
                if doc_url:
                    if "PCAP" in doc_type or "administrativo" in doc_url.lower():
                        pliegos.url_pliego_administrativo = doc_url
                    elif "PPT" in doc_type or "técnico" in doc_url.lower() or "tecnico" in doc_url.lower():
                        pliegos.url_pliego_tecnico = doc_url
                    else:
                        pliegos.url_otros_documentos.append(doc_url)
        
        # Clasificar y analizar
        keywords = extraer_keywords(objeto)
        tipo_match, cpv_desc = clasificar_cpv(cpv)
        
        # Si es CPV de obra, necesita keywords para ser relevante
        if tipo_match == "CPV_OBRA" and not keywords:
            return None
        
        # Si es CPV de audiovisual, necesita keywords de cableado/comunicaciones para ser relevante
        if tipo_match == "CPV_AUDIOVISUAL" and not keywords:
            return None
        
        # Si no es CPV relevante y no hay keywords, descartar
        if tipo_match == "OTRO" and not keywords:
            return None
        
        # Si es obra con keywords, cambiar tipo
        if tipo_match == "CPV_OBRA" and keywords:
            tipo_match = "CPV_OBRA_EMBEBIDO"
        
        # Si es audiovisual con keywords, cambiar tipo (caso DXC Salas de Vistas)
        if tipo_match == "CPV_AUDIOVISUAL" and keywords:
            tipo_match = "CPV_AUDIOVISUAL_CON_CABLEADO"
        
        # Calcular dolor
        dolor = calcular_dolor(objeto, fecha, duracion_dias, cpv, keywords)
        
        return Adjudicacion(
            expediente=expediente,
            objeto=objeto,
            adjudicatario=adjudicatario,
            nif_adjudicatario=nif,
            importe=importe,
            fecha_adjudicacion=fecha,
            organo_contratacion=organo,
            cpv=cpv,
            cpv_descripcion=cpv_desc,
            url=url,
            tipo_match=tipo_match,
            keywords_encontradas=keywords,
            es_pyme=es_pyme,
            dolor=dolor,
            pliegos=pliegos,
        )
        
    except Exception as e:
        print(f"Error parseando entry: {e}")
        return None


def procesar_feed(xml_content: str) -> List[Adjudicacion]:
    """Procesa feed completo"""
    adjudicaciones = []
    
    try:
        root = ET.fromstring(xml_content)
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        print(f"📡 Procesando {len(entries)} entries...")
        
        for entry in entries:
            adj = parse_entry(entry)
            if adj:
                adjudicaciones.append(adj)
        
    except ET.ParseError as e:
        print(f"❌ Error XML: {e}")
    
    return adjudicaciones


# ============================================================================
# GENERACIÓN DE REPORTES
# ============================================================================

def generar_reporte_dolor(adjudicaciones: List[Adjudicacion]) -> str:
    """Genera reporte priorizado por nivel de dolor"""
    
    if not adjudicaciones:
        return "No se encontraron oportunidades."
    
    # Ordenar por score total (mayor dolor primero)
    adjudicaciones.sort(key=lambda x: x.score_total(), reverse=True)
    
    lineas = [
        "",
        "█" * 70,
        "█  DETECTOR DE DOLOR - OPORTUNIDADES DE SUBCONTRATACIÓN",
        "█" * 70,
        f"   Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"   Total oportunidades: {len(adjudicaciones)}",
        "",
    ]
    
    # Resumen por nivel de dolor
    por_nivel = {}
    for adj in adjudicaciones:
        nivel = adj.dolor.nivel.value
        por_nivel[nivel] = por_nivel.get(nivel, 0) + 1
    
    lineas.append("   DISTRIBUCIÓN POR URGENCIA:")
    for nivel, count in sorted(por_nivel.items(), key=lambda x: x[0]):
        lineas.append(f"   {nivel}: {count}")
    
    # Importe total
    total = sum(adj.importe for adj in adjudicaciones)
    lineas.append(f"\n   💰 VALOR TOTAL EN CONTRATOS: {total:,.0f} EUR")
    lineas.append("")
    lineas.append("=" * 70)
    
    # Detalle de cada oportunidad
    for i, adj in enumerate(adjudicaciones, 1):
        score = adj.score_total()
        
        lineas.extend([
            "",
            f"┌{'─' * 68}┐",
            f"│ [{i}] SCORE: {score}/100  {adj.dolor.nivel.value}",
            f"├{'─' * 68}┤",
            f"│ 📋 {adj.objeto[:64]}",
        ])
        
        if len(adj.objeto) > 64:
            lineas.append(f"│    {adj.objeto[64:128]}")
        
        lineas.extend([
            f"│",
            f"│ 🏢 ADJUDICATARIO: {adj.adjudicatario}" + (" (PYME)" if adj.es_pyme else ""),
            f"│    NIF: {adj.nif_adjudicatario or 'No disponible'}",
            f"│",
            f"│ 💶 IMPORTE: {adj.importe:,.0f} EUR",
            f"│ 📅 ADJUDICADO: {adj.fecha_adjudicacion}",
        ])
        
        if adj.dolor.dias_hasta_fin:
            lineas.append(f"│ ⏱️  DÍAS RESTANTES: {adj.dolor.dias_hasta_fin}")
        if adj.dolor.fecha_fin_contrato:
            lineas.append(f"│ 🏁 FIN CONTRATO: {adj.dolor.fecha_fin_contrato}")
        
        lineas.extend([
            f"│",
            f"│ 🏛️  ÓRGANO: {adj.organo_contratacion[:60]}",
            f"│ 📁 EXPEDIENTE: {adj.expediente}",
            f"│ 🏷️  CPV: {adj.cpv} ({adj.cpv_descripcion})",
            f"│ 🎯 TIPO: {adj.dolor.tipo_oportunidad.value}",
        ])
        
        # Keywords detectadas
        if adj.keywords_encontradas:
            kws = ", ".join([f"{k}({v})" for k, v in 
                           sorted(adj.keywords_encontradas.items(), 
                                  key=lambda x: x[1], reverse=True)[:5]])
            lineas.append(f"│ 🔍 KEYWORDS: {kws}")
        
        # Indicadores de dolor
        if adj.dolor.indicadores_urgencia:
            lineas.append(f"│")
            lineas.append(f"│ 🚨 INDICADORES DE DOLOR:")
            for ind in adj.dolor.indicadores_urgencia:
                lineas.append(f"│    • {ind}")
        
        # URLs de pliegos
        lineas.append(f"│")
        lineas.append(f"│ 📎 DOCUMENTACIÓN:")
        lineas.append(f"│    Licitación: {adj.url}")
        if adj.pliegos.url_pliego_tecnico:
            lineas.append(f"│    Pliego Técnico: {adj.pliegos.url_pliego_tecnico}")
        if adj.pliegos.url_pliego_administrativo:
            lineas.append(f"│    Pliego Admin: {adj.pliegos.url_pliego_administrativo}")
        
        lineas.append(f"└{'─' * 68}┘")
    
    # Recomendaciones de acción
    criticos = [a for a in adjudicaciones if a.dolor.nivel == NivelDolor.CRITICO]
    altos = [a for a in adjudicaciones if a.dolor.nivel == NivelDolor.ALTO]
    
    if criticos or altos:
        lineas.extend([
            "",
            "=" * 70,
            "🎯 ACCIONES RECOMENDADAS",
            "=" * 70,
        ])
        
        if criticos:
            lineas.append(f"\n🔴 CONTACTAR HOY ({len(criticos)} oportunidades críticas):")
            for adj in criticos[:3]:
                lineas.append(f"   → {adj.adjudicatario}: {adj.objeto[:50]}...")
        
        if altos:
            lineas.append(f"\n🟠 CONTACTAR ESTA SEMANA ({len(altos)} oportunidades altas):")
            for adj in altos[:3]:
                lineas.append(f"   → {adj.adjudicatario}: {adj.objeto[:50]}...")
    
    return "\n".join(lineas)


def generar_ficha_comercial(adj: Adjudicacion) -> str:
    """Genera ficha comercial para contacto con adjudicatario"""
    
    return f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    FICHA COMERCIAL - OPORTUNIDAD                     ║
╠══════════════════════════════════════════════════════════════════════╣

EMPRESA TARGET
══════════════
Nombre: {adj.adjudicatario}
NIF: {adj.nif_adjudicatario or "Buscar en base de datos"}
Tipo: {"PYME - Mayor probabilidad de necesitar refuerzo" if adj.es_pyme else "Gran empresa"}

CONTRATO ADJUDICADO
═══════════════════
Objeto: {adj.objeto}

Importe: {adj.importe:,.0f} EUR
Fecha adjudicación: {adj.fecha_adjudicacion}
{"Días restantes: " + str(adj.dolor.dias_hasta_fin) if adj.dolor.dias_hasta_fin else ""}
{"Fecha fin: " + adj.dolor.fecha_fin_contrato if adj.dolor.fecha_fin_contrato else ""}

Órgano contratante: {adj.organo_contratacion}
Expediente: {adj.expediente}

ANÁLISIS DE NECESIDADES (basado en keywords detectadas)
══════════════════════════════════════════════════════
{chr(10).join(['• ' + k for k in adj.keywords_encontradas.keys()]) if adj.keywords_encontradas else "Revisar pliego técnico para detallar"}

TIPO DE OPORTUNIDAD
═══════════════════
{adj.dolor.tipo_oportunidad.value}

NIVEL DE URGENCIA: {adj.dolor.nivel.value}
{chr(10).join(['⚠️ ' + i for i in adj.dolor.indicadores_urgencia]) if adj.dolor.indicadores_urgencia else ""}

DOCUMENTACIÓN PARA ESTUDIAR
═══════════════════════════
🔗 Licitación: {adj.url}
{"🔗 Pliego Técnico: " + adj.pliegos.url_pliego_tecnico if adj.pliegos.url_pliego_tecnico else "⚠️ Pliego técnico: Descargar de PLACSP"}
{"🔗 Pliego Admin: " + adj.pliegos.url_pliego_administrativo if adj.pliegos.url_pliego_administrativo else ""}

PROPUESTA DE CONTACTO
═════════════════════
Asunto sugerido: "Colaboración para {adj.expediente} - {adj.organo_contratacion[:30]}"

Mensaje base:
"Buenos días,

Hemos visto que han sido adjudicatarios del contrato {adj.expediente} 
de {adj.organo_contratacion}.

En SRS somos especialistas en [ESPECIFICAR SEGÚN KEYWORDS] y hemos 
ejecutado proyectos similares para [REFERENCIAS].

¿Podríamos agendar una llamada para explorar cómo podemos ayudarles 
en la ejecución?"

╚══════════════════════════════════════════════════════════════════════╝
"""


def generar_json_crm(adjudicaciones: List[Adjudicacion]) -> str:
    """Genera JSON para importar en CRM"""
    
    data = {
        "meta": {
            "generado": datetime.now().isoformat(),
            "total": len(adjudicaciones),
            "importe_total": sum(a.importe for a in adjudicaciones),
            "criticos": len([a for a in adjudicaciones if a.dolor.nivel == NivelDolor.CRITICO]),
            "altos": len([a for a in adjudicaciones if a.dolor.nivel == NivelDolor.ALTO]),
        },
        "oportunidades": [
            {
                "id": f"PLACSP-{a.expediente}",
                "empresa": a.adjudicatario,
                "nif": a.nif_adjudicatario,
                "es_pyme": a.es_pyme,
                "contrato": {
                    "expediente": a.expediente,
                    "objeto": a.objeto,
                    "importe": a.importe,
                    "fecha_adjudicacion": a.fecha_adjudicacion,
                    "organo": a.organo_contratacion,
                    "cpv": a.cpv,
                },
                "analisis": {
                    "score": a.score_total(),
                    "nivel_dolor": a.dolor.nivel.name,
                    "dias_restantes": a.dolor.dias_hasta_fin,
                    "tipo_oportunidad": a.dolor.tipo_oportunidad.value,
                    "keywords": list(a.keywords_encontradas.keys()),
                },
                "documentacion": {
                    "url_licitacion": a.url,
                    "url_pliego_tecnico": a.pliegos.url_pliego_tecnico,
                    "url_pliego_admin": a.pliegos.url_pliego_administrativo,
                },
                "accion": {
                    "prioridad": "URGENTE" if a.dolor.nivel in [NivelDolor.CRITICO, NivelDolor.ALTO] else "NORMAL",
                    "siguiente_paso": "Contactar" if a.dolor.nivel == NivelDolor.CRITICO else "Estudiar pliego",
                }
            }
            for a in adjudicaciones
        ]
    }
    
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


# ============================================================================
# DATOS DE EJEMPLO AMPLIADOS
# ============================================================================

def generar_feed_ejemplo() -> str:
    """Feed de ejemplo con casos realistas de dolor"""
    
    return '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>PLACSP - Feed de prueba</title>
    <updated>2026-01-12T12:00:00+01:00</updated>
    
    <!-- CASO 1: IT directo, PYME, plazo corto -->
    <entry>
        <id>https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST001</id>
        <title>Servicio de soporte técnico helpdesk y mantenimiento de sistemas informáticos para el Ayuntamiento</title>
        <link href="https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST001"/>
        <content type="application/xml">
            <cfs:ContractFolderStatus xmlns:cfs="urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2"
                                      xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
                                      xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2">
                <cbc:ContractFolderID>2026/SERV/0042</cbc:ContractFolderID>
                <cbc:ContractFolderStatusCode>ADJ</cbc:ContractFolderStatusCode>
                <cac:ProcurementProject>
                    <cbc:Name>Servicio de soporte técnico helpdesk y mantenimiento de sistemas informáticos</cbc:Name>
                    <cac:PlannedPeriod>
                        <cbc:DurationMeasure unitCode="MON">6</cbc:DurationMeasure>
                    </cac:PlannedPeriod>
                    <cac:RequiredCommodityClassification>
                        <cbc:ItemClassificationCode>72500000</cbc:ItemClassificationCode>
                    </cac:RequiredCommodityClassification>
                </cac:ProcurementProject>
                <cac:LocatedContractingParty>
                    <cac:Party>
                        <cac:PartyName><cbc:Name>Ayuntamiento de Villanueva del Fresno</cbc:Name></cac:PartyName>
                    </cac:Party>
                </cac:LocatedContractingParty>
                <cac:TenderResult>
                    <cbc:AwardDate>2026-01-05</cbc:AwardDate>
                    <cac:WinningParty>
                        <cac:PartyName><cbc:Name>Soluciones Informáticas del Sur SL</cbc:Name></cac:PartyName>
                        <cac:PartyIdentification><cbc:ID>B41234567</cbc:ID></cac:PartyIdentification>
                        <cbc:SMEAwardedIndicator>true</cbc:SMEAwardedIndicator>
                    </cac:WinningParty>
                    <cac:AwardedTenderedProject>
                        <cbc:TotalAmount currencyID="EUR">85000.00</cbc:TotalAmount>
                    </cac:AwardedTenderedProject>
                </cac:TenderResult>
            </cfs:ContractFolderStatus>
        </content>
    </entry>
    
    <!-- CASO 2: Obra con cableado embebido, gran empresa, alto importe -->
    <entry>
        <id>https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST002</id>
        <title>Obras de construcción de nuevo edificio administrativo con instalación completa de cableado estructurado Cat6A, fibra óptica y centro de proceso de datos</title>
        <link href="https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST002"/>
        <content type="application/xml">
            <cfs:ContractFolderStatus xmlns:cfs="urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2"
                                      xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
                                      xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2">
                <cbc:ContractFolderID>2025/OBR/1847</cbc:ContractFolderID>
                <cbc:ContractFolderStatusCode>ADJ</cbc:ContractFolderStatusCode>
                <cac:ProcurementProject>
                    <cbc:Name>Obras de construcción de nuevo edificio administrativo con instalación completa de cableado estructurado Cat6A, fibra óptica y centro de proceso de datos</cbc:Name>
                    <cac:PlannedPeriod>
                        <cbc:DurationMeasure unitCode="MON">18</cbc:DurationMeasure>
                    </cac:PlannedPeriod>
                    <cac:RequiredCommodityClassification>
                        <cbc:ItemClassificationCode>45210000</cbc:ItemClassificationCode>
                    </cac:RequiredCommodityClassification>
                </cac:ProcurementProject>
                <cac:LocatedContractingParty>
                    <cac:Party>
                        <cac:PartyName><cbc:Name>Diputación Provincial de Badajoz</cbc:Name></cac:PartyName>
                    </cac:Party>
                </cac:LocatedContractingParty>
                <cac:TenderResult>
                    <cbc:AwardDate>2025-11-20</cbc:AwardDate>
                    <cac:WinningParty>
                        <cac:PartyName><cbc:Name>CONSTRUCCIONES GARCIA-MONTERO SA</cbc:Name></cac:PartyName>
                        <cac:PartyIdentification><cbc:ID>A06123456</cbc:ID></cac:PartyIdentification>
                        <cbc:SMEAwardedIndicator>false</cbc:SMEAwardedIndicator>
                    </cac:WinningParty>
                    <cac:AwardedTenderedProject>
                        <cbc:TotalAmount currencyID="EUR">2340000.00</cbc:TotalAmount>
                    </cac:AwardedTenderedProject>
                </cac:TenderResult>
                <cac:TechnicalDocumentReference>
                    <cbc:ID>PPT-2025-1847</cbc:ID>
                    <cbc:DocumentTypeCode>PPT</cbc:DocumentTypeCode>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://contrataciondelestado.es/docs/PPT_2025_1847.pdf</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:TechnicalDocumentReference>
            </cfs:ContractFolderStatus>
        </content>
    </entry>
    
    <!-- CASO 3: Transformación digital urgente -->
    <entry>
        <id>https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST003</id>
        <title>Servicios de transformación digital urgente: migración cloud, implementación Microsoft 365 y ciberseguridad - Plazo improrrogable</title>
        <link href="https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST003"/>
        <content type="application/xml">
            <cfs:ContractFolderStatus xmlns:cfs="urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2"
                                      xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
                                      xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2">
                <cbc:ContractFolderID>2026/DIGIT/0015</cbc:ContractFolderID>
                <cbc:ContractFolderStatusCode>ADJ</cbc:ContractFolderStatusCode>
                <cac:ProcurementProject>
                    <cbc:Name>Servicios de transformación digital urgente: migración cloud, implementación Microsoft 365 y ciberseguridad - Plazo improrrogable por fondos europeos</cbc:Name>
                    <cac:PlannedPeriod>
                        <cbc:DurationMeasure unitCode="DAY">45</cbc:DurationMeasure>
                    </cac:PlannedPeriod>
                    <cac:RequiredCommodityClassification>
                        <cbc:ItemClassificationCode>72200000</cbc:ItemClassificationCode>
                    </cac:RequiredCommodityClassification>
                </cac:ProcurementProject>
                <cac:LocatedContractingParty>
                    <cac:Party>
                        <cac:PartyName><cbc:Name>Consejería de Economía Digital - Junta de Extremadura</cbc:Name></cac:PartyName>
                    </cac:Party>
                </cac:LocatedContractingParty>
                <cac:TenderResult>
                    <cbc:AwardDate>2026-01-10</cbc:AwardDate>
                    <cac:WinningParty>
                        <cac:PartyName><cbc:Name>EVERIS SPAIN SLU</cbc:Name></cac:PartyName>
                        <cac:PartyIdentification><cbc:ID>B82387770</cbc:ID></cac:PartyIdentification>
                        <cbc:SMEAwardedIndicator>false</cbc:SMEAwardedIndicator>
                    </cac:WinningParty>
                    <cac:AwardedTenderedProject>
                        <cbc:TotalAmount currencyID="EUR">890000.00</cbc:TotalAmount>
                    </cac:AwardedTenderedProject>
                </cac:TenderResult>
            </cfs:ContractFolderStatus>
        </content>
    </entry>
    
    <!-- CASO 4: Cableado puro, PYME -->
    <entry>
        <id>https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST004</id>
        <title>Instalación de red de datos y cableado estructurado para 3 centros educativos: 450 puntos de red Cat6, wifi y rack de comunicaciones</title>
        <link href="https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST004"/>
        <content type="application/xml">
            <cfs:ContractFolderStatus xmlns:cfs="urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2"
                                      xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
                                      xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2">
                <cbc:ContractFolderID>2026/INF/0089</cbc:ContractFolderID>
                <cbc:ContractFolderStatusCode>ADJ</cbc:ContractFolderStatusCode>
                <cac:ProcurementProject>
                    <cbc:Name>Instalación de red de datos y cableado estructurado para 3 centros educativos: 450 puntos de red Cat6, wifi y rack de comunicaciones</cbc:Name>
                    <cac:PlannedPeriod>
                        <cbc:DurationMeasure unitCode="MON">3</cbc:DurationMeasure>
                    </cac:PlannedPeriod>
                    <cac:RequiredCommodityClassification>
                        <cbc:ItemClassificationCode>45314320</cbc:ItemClassificationCode>
                    </cac:RequiredCommodityClassification>
                </cac:ProcurementProject>
                <cac:LocatedContractingParty>
                    <cac:Party>
                        <cac:PartyName><cbc:Name>Ayuntamiento de Mérida - Concejalía de Educación</cbc:Name></cac:PartyName>
                    </cac:Party>
                </cac:LocatedContractingParty>
                <cac:TenderResult>
                    <cbc:AwardDate>2026-01-08</cbc:AwardDate>
                    <cac:WinningParty>
                        <cac:PartyName><cbc:Name>INSTALACIONES ELECTRICAS MERIDA SL</cbc:Name></cac:PartyName>
                        <cac:PartyIdentification><cbc:ID>B06987654</cbc:ID></cac:PartyIdentification>
                        <cbc:SMEAwardedIndicator>true</cbc:SMEAwardedIndicator>
                    </cac:WinningParty>
                    <cac:AwardedTenderedProject>
                        <cbc:TotalAmount currencyID="EUR">127500.00</cbc:TotalAmount>
                    </cac:AwardedTenderedProject>
                </cac:TenderResult>
            </cfs:ContractFolderStatus>
        </content>
    </entry>
    
    <!-- CASO 5: No relevante (mobiliario) - debe descartarse -->
    <entry>
        <id>https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST005</id>
        <title>Suministro de mobiliario de oficina y equipamiento</title>
        <link href="https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST005"/>
        <content type="application/xml">
            <cfs:ContractFolderStatus xmlns:cfs="urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2"
                                      xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
                                      xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2">
                <cbc:ContractFolderID>2026/SUM/0234</cbc:ContractFolderID>
                <cbc:ContractFolderStatusCode>ADJ</cbc:ContractFolderStatusCode>
                <cac:ProcurementProject>
                    <cbc:Name>Suministro de mobiliario de oficina y equipamiento</cbc:Name>
                    <cac:RequiredCommodityClassification>
                        <cbc:ItemClassificationCode>39100000</cbc:ItemClassificationCode>
                    </cac:RequiredCommodityClassification>
                </cac:ProcurementProject>
                <cac:TenderResult>
                    <cbc:AwardDate>2026-01-02</cbc:AwardDate>
                    <cac:WinningParty>
                        <cac:PartyName><cbc:Name>MUEBLES OFICINA SL</cbc:Name></cac:PartyName>
                    </cac:WinningParty>
                </cac:TenderResult>
            </cfs:ContractFolderStatus>
        </content>
    </entry>
    
    <!-- CASO 6: TIPO DXC - Audiovisual con cableado embebido + Next Generation (ECON/000161/2022) -->
    <entry>
        <id>https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST006</id>
        <title>Acondicionamiento audiovisual y de comunicaciones de las Salas de Vistas de la Comunidad de Madrid, en el marco del Plan de Recuperación, Transformación y Resiliencia - Next Generation EU</title>
        <link href="https://contrataciondelestado.es/wps/poc?uri=deeplink&amp;idEvl=TEST006"/>
        <content type="application/xml">
            <cfs:ContractFolderStatus xmlns:cfs="urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2"
                                      xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
                                      xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2">
                <cbc:ContractFolderID>ECON/000161/2022</cbc:ContractFolderID>
                <cbc:ContractFolderStatusCode>RES</cbc:ContractFolderStatusCode>
                <cac:ProcurementProject>
                    <cbc:Name>Acondicionamiento audiovisual y de comunicaciones de las Salas de Vistas de la Comunidad de Madrid, en el marco del Plan de Recuperación, Transformación y Resiliencia - Next Generation EU</cbc:Name>
                    <cac:PlannedPeriod>
                        <cbc:DurationMeasure unitCode="MON">18</cbc:DurationMeasure>
                    </cac:PlannedPeriod>
                    <cac:RequiredCommodityClassification>
                        <cbc:ItemClassificationCode>32321300</cbc:ItemClassificationCode>
                    </cac:RequiredCommodityClassification>
                </cac:ProcurementProject>
                <cac:LocatedContractingParty>
                    <cac:Party>
                        <cac:PartyName><cbc:Name>Agencia para la Administración Digital de la Comunidad de Madrid</cbc:Name></cac:PartyName>
                    </cac:Party>
                </cac:LocatedContractingParty>
                <cac:TenderResult>
                    <cbc:AwardDate>2023-11-03</cbc:AwardDate>
                    <cac:WinningParty>
                        <cac:PartyName><cbc:Name>DXC TECHNOLOGY SERVICIOS ESPAÑA S.L.U.</cbc:Name></cac:PartyName>
                        <cac:PartyIdentification><cbc:ID>B87615100</cbc:ID></cac:PartyIdentification>
                        <cbc:SMEAwardedIndicator>false</cbc:SMEAwardedIndicator>
                    </cac:WinningParty>
                    <cac:AwardedTenderedProject>
                        <cbc:TotalAmount currencyID="EUR">4880208.80</cbc:TotalAmount>
                    </cac:AwardedTenderedProject>
                </cac:TenderResult>
                <cac:TechnicalDocumentReference>
                    <cbc:ID>PPT-ECON-000161-2022</cbc:ID>
                    <cbc:DocumentTypeCode>PPT</cbc:DocumentTypeCode>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://comunidad.madrid/contratacion/ppt_econ_000161_2022.pdf</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:TechnicalDocumentReference>
            </cfs:ContractFolderStatus>
        </content>
    </entry>
    
</feed>'''


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("""
    ███████╗██████╗  ██████╗ ████████╗████████╗███████╗██████╗ 
    ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
    ███████╗██████╔╝██║   ██║   ██║      ██║   █████╗  ██████╔╝
    ╚════██║██╔═══╝ ██║   ██║   ██║      ██║   ██╔══╝  ██╔══██╗
    ███████║██║     ╚██████╔╝   ██║      ██║   ███████╗██║  ██║
    ╚══════╝╚═╝      ╚═════╝    ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                         SRS
    "El que ve lo que otros no ven"
    ═══════════════════════════════════════════════════════════
    """)
    
    # Cargar feed (ejemplo o real)
    print("📡 Cargando feed de PLACSP...")
    xml_content = generar_feed_ejemplo()
    
    # Procesar
    adjudicaciones = procesar_feed(xml_content)
    
    print(f"✅ Detectadas {len(adjudicaciones)} oportunidades relevantes")
    print(f"   (de {xml_content.count('<entry>')} entries totales)")
    
    # Generar reporte principal
    reporte = generar_reporte_dolor(adjudicaciones)
    print(reporte)
    
    # Guardar outputs
    import os
    os.makedirs("/home/claude/placsp_detector/output", exist_ok=True)
    
    # JSON para CRM
    json_crm = generar_json_crm(adjudicaciones)
    with open("/home/claude/placsp_detector/output/oportunidades_crm.json", "w", encoding="utf-8") as f:
        f.write(json_crm)
    
    # Fichas comerciales individuales
    for adj in adjudicaciones:
        if adj.dolor.nivel in [NivelDolor.CRITICO, NivelDolor.ALTO]:
            ficha = generar_ficha_comercial(adj)
            filename = f"/home/claude/placsp_detector/output/ficha_{adj.expediente.replace('/', '_')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(ficha)
    
    # Reporte completo
    with open("/home/claude/placsp_detector/output/reporte_dolor.txt", "w", encoding="utf-8") as f:
        f.write(reporte)
    
    print(f"""
    ════════════════════════════════════════════
    📁 ARCHIVOS GENERADOS:
       • output/oportunidades_crm.json (para CRM)
       • output/reporte_dolor.txt (reporte completo)
       • output/ficha_*.txt (fichas comerciales)
    ════════════════════════════════════════════
    """)


if __name__ == "__main__":
    main()
