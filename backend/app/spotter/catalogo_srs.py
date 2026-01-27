"""
Catálogo de servicios y componentes IT de SRS (System Rapid Solutions)

Este catálogo define todos los servicios que SRS puede ofrecer,
organizados por categoría. Se usa para:
1. Detectar oportunidades en pliegos de licitaciones
2. Clasificar componentes IT detectados
3. Generar prompts para análisis con IA
4. Evaluar zonas de cobertura geográfica

Versión: 2.0.0
Fecha: 2026-01-19
Total servicios: 186
"""

from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# ZONAS DE COBERTURA GEOGRÁFICA
# ═══════════════════════════════════════════════════════════════════════════════

ZONAS_COBERTURA = {
    "base": {
        "descripcion": "Presencia directa, respuesta inmediata, sin coste desplazamiento",
        "tiempo_respuesta": "mismo día",
        "coste_desplazamiento": "incluido",
        "prioridad_score": 20,
        "provincias": [
            "Madrid",
            "Sevilla",
            "Málaga",
            "Cádiz",
            "Granada",
            "Córdoba",
            "Huelva",
            "Jaén",
            "Almería"
        ]
    },
    "cercana": {
        "descripcion": "Desplazamiento corto, respuesta 24-48h",
        "tiempo_respuesta": "24-48h",
        "coste_desplazamiento": "reducido",
        "prioridad_score": 10,
        "provincias": [
            "Toledo",
            "Ciudad Real",
            "Guadalajara",
            "Cuenca",
            "Albacete",
            "Badajoz",
            "Cáceres",
            "Ávila",
            "Segovia",
            "Murcia"
        ]
    },
    "expansion": {
        "descripcion": "Cobertura nacional, planificación previa",
        "tiempo_respuesta": "48-72h",
        "coste_desplazamiento": "estándar",
        "prioridad_score": 0,
        "provincias": [
            "Barcelona",
            "Valencia",
            "Alicante",
            "Castellón",
            "Tarragona",
            "Girona",
            "Lleida",
            "Zaragoza",
            "Huesca",
            "Teruel",
            "Navarra",
            "La Rioja",
            "Álava",
            "Vizcaya",
            "Guipúzcoa",
            "Cantabria",
            "Asturias",
            "León",
            "Palencia",
            "Burgos",
            "Soria",
            "Valladolid",
            "Zamora",
            "Salamanca",
            "A Coruña",
            "Lugo",
            "Ourense",
            "Pontevedra",
            "Islas Baleares",
            "Las Palmas",
            "Santa Cruz de Tenerife",
            "Ceuta",
            "Melilla"
        ]
    }
}


def obtener_zona_cobertura(provincia: str) -> dict:
    """
    Determina la zona de cobertura para una provincia.
    Retorna info de la zona o None si no se encuentra.
    """
    provincia_normalizada = provincia.strip().title()

    for zona, datos in ZONAS_COBERTURA.items():
        if provincia_normalizada in datos["provincias"]:
            return {
                "zona": zona,
                "tiempo_respuesta": datos["tiempo_respuesta"],
                "coste_desplazamiento": datos["coste_desplazamiento"],
                "prioridad_score": datos["prioridad_score"],
                "descripcion": datos["descripcion"]
            }

    # Si no está en ninguna zona conocida
    return {
        "zona": "expansion",
        "tiempo_respuesta": "a determinar",
        "coste_desplazamiento": "a cotizar",
        "prioridad_score": -5,
        "descripcion": "Zona no habitual, requiere evaluación"
    }


def es_zona_prioritaria(provincia: str) -> bool:
    """Retorna True si la provincia está en zona base o cercana"""
    zona = obtener_zona_cobertura(provincia)
    return zona["zona"] in ["base", "cercana"]


# ═══════════════════════════════════════════════════════════════════════════════
# CATÁLOGO DE SERVICIOS COMPLETO v2.0
# ═══════════════════════════════════════════════════════════════════════════════

CATALOGO_SRS = [
    # ═══════════════════════════════════════════════════════════════════════════
    # SERVICIOS (31)
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "servicios", "subtipo": "soporte", "nombre": "Soporte técnico Nivel 1", "descripcion": "Atención primera línea: incidencias básicas, reseteo contraseñas, troubleshooting inicial, gestión tickets", "urgencia": "critica", "es_core_srs": True, "keywords": ["helpdesk", "nivel 1", "N1", "primera línea", "incidencias", "tickets", "soporte básico"]},
    {"tipo": "servicios", "subtipo": "soporte", "nombre": "Soporte técnico Nivel 2", "descripcion": "Resolución incidencias complejas, administración sistemas, escalado técnico especializado", "urgencia": "critica", "es_core_srs": True, "keywords": ["nivel 2", "N2", "administración", "escalado", "incidencias complejas"]},
    {"tipo": "servicios", "subtipo": "soporte", "nombre": "Soporte técnico Nivel 3", "descripcion": "Ingeniería avanzada, resolución problemas críticos, diseño soluciones, escalado fabricante", "urgencia": "alta", "es_core_srs": True, "keywords": ["nivel 3", "N3", "ingeniería", "escalado fabricante", "problemas críticos"]},
    {"tipo": "servicios", "subtipo": "soporte", "nombre": "Helpdesk 24x7", "descripcion": "Centro de atención multicanal (teléfono, email, chat, portal) con cobertura horaria completa", "urgencia": "critica", "es_core_srs": True, "keywords": ["24x7", "24/7", "helpdesk", "CAU", "centro atención", "multicanal", "service desk"]},
    {"tipo": "servicios", "subtipo": "soporte", "nombre": "Service Desk dedicado", "descripcion": "Equipo de service desk exclusivo para cliente, SPOC, gestión integral ITSM", "urgencia": "alta", "es_core_srs": True, "keywords": ["service desk", "SPOC", "dedicado", "exclusivo", "ITSM"]},
    {"tipo": "servicios", "subtipo": "campo", "nombre": "Smart Hands / Manos Remotas", "descripcion": "Ojos y manos en data centers: rack & stack, cableado, verificaciones físicas, reinicio equipos", "urgencia": "alta", "es_core_srs": True, "keywords": ["smart hands", "manos remotas", "data center", "rack", "stack", "verificación física"]},
    {"tipo": "servicios", "subtipo": "campo", "nombre": "Field Services / Soporte Onsite", "descripcion": "Técnicos desplazados a ubicación cliente para intervenciones presenciales", "urgencia": "alta", "es_core_srs": True, "keywords": ["field services", "onsite", "presencial", "desplazamiento", "in situ", "técnico de campo"]},
    {"tipo": "servicios", "subtipo": "campo", "nombre": "Servicio de guardia / On-call", "descripcion": "Disponibilidad técnica fuera de horario laboral, escalado urgente, intervención crítica", "urgencia": "alta", "es_core_srs": True, "keywords": ["guardia", "on-call", "fuera de horario", "urgente", "emergencia", "retén"]},
    {"tipo": "servicios", "subtipo": "mantenimiento", "nombre": "Mantenimiento preventivo", "descripcion": "Revisiones programadas, actualizaciones firmware, limpieza equipos, verificación estado", "urgencia": "media", "es_core_srs": True, "keywords": ["preventivo", "revisiones", "firmware", "programado", "verificación"]},
    {"tipo": "servicios", "subtipo": "mantenimiento", "nombre": "Mantenimiento correctivo", "descripcion": "Reparación y sustitución de equipos averiados, diagnóstico fallos hardware", "urgencia": "alta", "es_core_srs": True, "keywords": ["correctivo", "reparación", "avería", "sustitución", "fallo hardware"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Gestión de incidencias (ITIL)", "descripcion": "Proceso completo: registro, clasificación, priorización, resolución, cierre según ITIL", "urgencia": "alta", "es_core_srs": True, "keywords": ["ITIL", "incidencias", "tickets", "SLA", "priorización"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Gestión de cambios", "descripcion": "Control de cambios en infraestructura: CAB, aprobaciones, ventanas de mantenimiento", "urgencia": "media", "es_core_srs": False, "keywords": ["cambios", "CAB", "change management", "ventana mantenimiento"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Gestión de problemas", "descripcion": "Análisis causa raíz, eliminación incidencias recurrentes, documentación soluciones", "urgencia": "media", "es_core_srs": False, "keywords": ["problemas", "causa raíz", "RCA", "recurrentes", "problem management"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Gestión de proyectos / PMO", "descripcion": "Coordinación proyectos IT, metodologías, planificación, seguimiento, reporting", "urgencia": "media", "es_core_srs": False, "keywords": ["PMO", "project manager", "proyectos", "coordinación", "planificación"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Gestión de SLAs", "descripcion": "Definición, medición, reporting de niveles de servicio, penalizaciones", "urgencia": "media", "es_core_srs": False, "keywords": ["SLA", "niveles de servicio", "KPI", "penalizaciones", "reporting"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Inventario y gestión de activos", "descripcion": "CMDB, control de licencias, ciclo de vida activos, gestión de configuración", "urgencia": "media", "es_core_srs": False, "keywords": ["CMDB", "inventario", "activos", "licencias", "configuración", "asset management"]},
    {"tipo": "servicios", "subtipo": "operaciones", "nombre": "Administración remota de sistemas", "descripcion": "Gestión continua de servidores, aplicaciones y servicios vía conexión remota segura", "urgencia": "critica", "es_core_srs": True, "keywords": ["administración remota", "gestión servidores", "remoto", "sistemas"]},
    {"tipo": "servicios", "subtipo": "operaciones", "nombre": "Monitorización 24x7", "descripcion": "Vigilancia proactiva de infraestructura, alertas, dashboards, informes disponibilidad", "urgencia": "critica", "es_core_srs": True, "keywords": ["monitorización", "24x7", "alertas", "dashboards", "disponibilidad", "NOC"]},
    {"tipo": "servicios", "subtipo": "operaciones", "nombre": "NOC - Centro de Operaciones de Red", "descripcion": "Centro de operaciones 24x7, gestión de alertas, coordinación incidencias, escalado", "urgencia": "critica", "es_core_srs": True, "keywords": ["NOC", "centro operaciones", "red", "alertas", "24x7"]},
    {"tipo": "servicios", "subtipo": "consultoria", "nombre": "Staff Augmentation", "descripcion": "Refuerzo equipos cliente con técnicos dedicados bajo su dirección", "urgencia": "media", "es_core_srs": True, "keywords": ["staff augmentation", "refuerzo", "técnicos dedicados", "outsourcing"]},
    {"tipo": "servicios", "subtipo": "consultoria", "nombre": "Consultoría tecnológica", "descripcion": "Asesoramiento estratégico, diseño arquitecturas, roadmaps tecnológicos", "urgencia": "media", "es_core_srs": False, "keywords": ["consultoría", "asesoramiento", "arquitectura", "roadmap", "estrategia"]},
    {"tipo": "servicios", "subtipo": "consultoria", "nombre": "vCIO / CIO Virtual", "descripcion": "Dirección tecnológica externalizada: estrategia, presupuestos, governance IT", "urgencia": "baja", "es_core_srs": False, "keywords": ["vCIO", "CIO virtual", "dirección tecnológica", "governance"]},
    {"tipo": "servicios", "subtipo": "consultoria", "nombre": "Auditoría IT", "descripcion": "Evaluación estado infraestructura, identificación riesgos, recomendaciones mejora", "urgencia": "media", "es_core_srs": False, "keywords": ["auditoría", "evaluación", "riesgos", "assessment", "diagnóstico"]},
    {"tipo": "servicios", "subtipo": "consultoria", "nombre": "Documentación técnica", "descripcion": "Creación y mantenimiento documentación AS-IS/TO-BE, procedimientos, runbooks", "urgencia": "media", "es_core_srs": False, "keywords": ["documentación", "AS-IS", "TO-BE", "procedimientos", "runbooks"]},
    {"tipo": "servicios", "subtipo": "consultoria", "nombre": "Formación técnica", "descripcion": "Capacitación usuarios y técnicos en herramientas, plataformas y procedimientos", "urgencia": "baja", "es_core_srs": False, "keywords": ["formación", "capacitación", "training", "usuarios", "técnicos"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Gestión de proveedores / Vendor Liaison", "descripcion": "Coordinación con fabricantes, gestión contratos, escalados, renovaciones", "urgencia": "media", "es_core_srs": False, "keywords": ["vendor", "proveedores", "fabricantes", "contratos", "escalado"]},
    {"tipo": "servicios", "subtipo": "gestion", "nombre": "Procurement / Gestión de compras IT", "descripcion": "Adquisición hardware y software, comparativas, negociación, logística", "urgencia": "media", "es_core_srs": False, "keywords": ["procurement", "compras", "adquisición", "logística", "suministro"]},
    {"tipo": "servicios", "subtipo": "despliegue", "nombre": "Roll-out / Despliegue masivo", "descripcion": "Instalación equipos a escala: puestos de trabajo, dispositivos, configuración estándar", "urgencia": "alta", "es_core_srs": True, "keywords": ["rollout", "roll-out", "despliegue", "masivo", "instalación", "puestos"]},
    {"tipo": "servicios", "subtipo": "despliegue", "nombre": "Tech Refresh / Renovación tecnológica", "descripcion": "Sustitución planificada de equipos obsoletos, migración datos, retirada RAEE", "urgencia": "media", "es_core_srs": True, "keywords": ["tech refresh", "renovación", "obsoleto", "RAEE", "sustitución"]},
    {"tipo": "servicios", "subtipo": "despliegue", "nombre": "IMAC (Install, Move, Add, Change)", "descripcion": "Servicios de instalación, movimiento, adición y cambio de equipos", "urgencia": "media", "es_core_srs": True, "keywords": ["IMAC", "instalación", "movimiento", "traslado", "cambio equipo"]},
    {"tipo": "servicios", "subtipo": "transicion", "nombre": "Transición de servicios / Takeover", "descripcion": "Takeover/handover de contratos, due diligence técnica, transferencia conocimiento", "urgencia": "alta", "es_core_srs": False, "keywords": ["transición", "takeover", "handover", "due diligence", "transferencia"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # INFRAESTRUCTURA (50)
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "infraestructura", "subtipo": "servidores", "nombre": "Servidores físicos", "descripcion": "Suministro, instalación y mantenimiento servidores rack/torre (Dell, HPE, Lenovo)", "urgencia": "alta", "es_core_srs": True, "keywords": ["servidores", "rack", "torre", "Dell", "HPE", "Lenovo", "PowerEdge", "ProLiant"]},
    {"tipo": "infraestructura", "subtipo": "virtualizacion", "nombre": "Virtualización VMware", "descripcion": "Diseño, implementación y gestión entornos vSphere, ESXi, vCenter, clusters HA/DRS", "urgencia": "alta", "es_core_srs": True, "keywords": ["VMware", "vSphere", "ESXi", "vCenter", "HA", "DRS", "virtualización"]},
    {"tipo": "infraestructura", "subtipo": "virtualizacion", "nombre": "Virtualización Hyper-V", "descripcion": "Implementación y administración Microsoft Hyper-V, failover clustering", "urgencia": "alta", "es_core_srs": True, "keywords": ["Hyper-V", "Microsoft", "failover", "clustering", "virtualización"]},
    {"tipo": "infraestructura", "subtipo": "virtualizacion", "nombre": "Virtualización Proxmox", "descripcion": "Entornos virtualizados open source, gestión VMs y contenedores", "urgencia": "media", "es_core_srs": False, "keywords": ["Proxmox", "open source", "VMs", "contenedores", "KVM"]},
    {"tipo": "infraestructura", "subtipo": "almacenamiento", "nombre": "Almacenamiento SAN/NAS", "descripcion": "Diseño e implementación storage enterprise, cabinas, expansiones, tiering", "urgencia": "alta", "es_core_srs": True, "keywords": ["SAN", "NAS", "storage", "cabina", "NetApp", "EMC", "Pure", "almacenamiento"]},
    {"tipo": "infraestructura", "subtipo": "almacenamiento", "nombre": "Almacenamiento hiperconvergente (HCI)", "descripcion": "Soluciones vSAN, Nutanix, Azure Stack HCI", "urgencia": "media", "es_core_srs": False, "keywords": ["HCI", "hiperconvergente", "vSAN", "Nutanix", "Azure Stack"]},
    {"tipo": "infraestructura", "subtipo": "cloud", "nombre": "Infraestructura Cloud AWS", "descripcion": "Diseño, migración y gestión workloads en Amazon Web Services", "urgencia": "alta", "es_core_srs": True, "keywords": ["AWS", "Amazon", "EC2", "S3", "cloud", "migración"]},
    {"tipo": "infraestructura", "subtipo": "cloud", "nombre": "Infraestructura Cloud Azure", "descripcion": "Implementación y administración Microsoft Azure, híbrido con on-premise", "urgencia": "alta", "es_core_srs": True, "keywords": ["Azure", "Microsoft", "cloud", "híbrido", "migración"]},
    {"tipo": "infraestructura", "subtipo": "cloud", "nombre": "Infraestructura Cloud GCP", "descripcion": "Servicios Google Cloud Platform, Compute Engine, Kubernetes", "urgencia": "media", "es_core_srs": True, "keywords": ["GCP", "Google Cloud", "Compute Engine", "GKE", "cloud"]},
    {"tipo": "infraestructura", "subtipo": "cloud", "nombre": "Cloud híbrido / Multi-cloud", "descripcion": "Arquitecturas combinando on-premise con múltiples proveedores cloud", "urgencia": "media", "es_core_srs": False, "keywords": ["híbrido", "multi-cloud", "on-premise", "arquitectura"]},
    {"tipo": "infraestructura", "subtipo": "cloud", "nombre": "Migración a cloud", "descripcion": "Planificación y ejecución migraciones on-premise a cloud, lift & shift, refactoring", "urgencia": "media", "es_core_srs": True, "keywords": ["migración", "cloud", "lift and shift", "refactoring", "modernización"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Cableado estructurado cobre", "descripcion": "Diseño, instalación y certificación cableado Cat5e/Cat6/Cat6A/Cat7, horizontal y vertical", "urgencia": "alta", "es_core_srs": True, "keywords": ["cableado", "cobre", "Cat6", "Cat6A", "Cat7", "UTP", "STP", "estructurado", "red"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Cableado estructurado fibra óptica", "descripcion": "Tendido, fusión, terminación y certificación fibra óptica monomodo y multimodo", "urgencia": "alta", "es_core_srs": True, "keywords": ["fibra óptica", "monomodo", "multimodo", "OM3", "OM4", "OS2", "fusión"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Replanteo de red", "descripcion": "Estudio previo, diseño de recorridos, planificación de tiradas y puntos de red", "urgencia": "alta", "es_core_srs": True, "keywords": ["replanteo", "diseño", "recorridos", "planificación", "puntos de red"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Certificación de cableado", "descripcion": "Medición y certificación de enlaces con equipos Fluke/equivalente, informes de cumplimiento", "urgencia": "alta", "es_core_srs": True, "keywords": ["certificación", "Fluke", "DSX", "medición", "cumplimiento", "informes"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Fusión de fibra óptica", "descripcion": "Empalme por fusión, instalación cajas de empalme, pigtails y latiguillos", "urgencia": "alta", "es_core_srs": True, "keywords": ["fusión", "empalme", "pigtails", "latiguillos", "caja empalme"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Canalizaciones y bandejas", "descripcion": "Instalación de bandejas portacables, canaletas, tubos y conductos para cableado", "urgencia": "alta", "es_core_srs": True, "keywords": ["bandejas", "canaletas", "conductos", "tubos", "portacables", "canalización"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Patch panels y distribuidores", "descripcion": "Instalación y terminación de paneles de parcheo cobre y fibra, organizadores", "urgencia": "alta", "es_core_srs": True, "keywords": ["patch panel", "panel de parcheo", "distribuidor", "organizador", "terminación"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Rosetas y tomas de red", "descripcion": "Instalación de rosetas RJ45, cajas de superficie/empotrar, tomas de usuario", "urgencia": "alta", "es_core_srs": True, "keywords": ["rosetas", "RJ45", "tomas", "cajas", "puntos de red", "usuario"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Cableado vertical / troncal", "descripcion": "Backbone entre plantas, conexión armarios distribuidores, fibra/cobre troncal", "urgencia": "alta", "es_core_srs": True, "keywords": ["backbone", "vertical", "troncal", "entre plantas", "riser"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Etiquetado y documentación de red", "descripcion": "Etiquetado normalizado de puntos, paneles y cables, planos as-built, documentación técnica", "urgencia": "media", "es_core_srs": True, "keywords": ["etiquetado", "documentación", "as-built", "planos", "identificación"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "FTTH / FTTD", "descripcion": "Fibra hasta el hogar o hasta el puesto, despliegue última milla, ONTs", "urgencia": "alta", "es_core_srs": True, "keywords": ["FTTH", "FTTD", "FTTP", "última milla", "ONT", "fibra al hogar"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Testing y medición de red", "descripcion": "Pruebas de continuidad, atenuación, OTDR, certificación de enlaces", "urgencia": "alta", "es_core_srs": True, "keywords": ["testing", "OTDR", "atenuación", "continuidad", "medición"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Armarios rack y distribuidores", "descripcion": "Suministro e instalación de armarios de comunicaciones, distribuidores de planta", "urgencia": "alta", "es_core_srs": True, "keywords": ["armario", "rack", "distribuidor", "comunicaciones", "19 pulgadas"]},
    {"tipo": "infraestructura", "subtipo": "cableado", "nombre": "Obra civil para telecomunicaciones", "descripcion": "Canalizaciones enterradas, arquetas, pedestales, acometidas, paso de muros", "urgencia": "media", "es_core_srs": False, "keywords": ["obra civil", "arquetas", "canalización enterrada", "acometida", "ICT"]},
    {"tipo": "infraestructura", "subtipo": "datacenter", "nombre": "Racks y PDUs", "descripcion": "Suministro e instalación armarios rack, regletas inteligentes, gestión energía", "urgencia": "media", "es_core_srs": True, "keywords": ["rack", "PDU", "regleta", "energía", "armario"]},
    {"tipo": "infraestructura", "subtipo": "datacenter", "nombre": "SAI/UPS", "descripcion": "Sistemas alimentación ininterrumpida, dimensionamiento, instalación, mantenimiento", "urgencia": "alta", "es_core_srs": True, "keywords": ["SAI", "UPS", "alimentación ininterrumpida", "baterías", "Eaton", "APC"]},
    {"tipo": "infraestructura", "subtipo": "datacenter", "nombre": "Climatización CPD", "descripcion": "Sistemas refrigeración data centers, monitorización temperatura/humedad", "urgencia": "alta", "es_core_srs": False, "keywords": ["climatización", "refrigeración", "CPD", "temperatura", "humedad", "CRAC"]},
    {"tipo": "infraestructura", "subtipo": "datacenter", "nombre": "Data Center - Diseño y construcción", "descripcion": "Diseño salas técnicas, distribución, redundancia, certificación Tier", "urgencia": "media", "es_core_srs": False, "keywords": ["data center", "CPD", "sala técnica", "Tier", "diseño", "Uptime"]},
    {"tipo": "infraestructura", "subtipo": "datacenter", "nombre": "Colocation", "descripcion": "Gestión espacios en data centers terceros, housing equipos cliente", "urgencia": "media", "es_core_srs": False, "keywords": ["colocation", "housing", "data center", "alojamiento"]},
    {"tipo": "infraestructura", "subtipo": "puesto", "nombre": "Puestos de trabajo / Endpoints", "descripcion": "Suministro, configuración y soporte PCs, portátiles, thin clients", "urgencia": "alta", "es_core_srs": True, "keywords": ["puesto de trabajo", "PC", "portátil", "endpoint", "thin client", "desktop"]},
    {"tipo": "infraestructura", "subtipo": "puesto", "nombre": "Dispositivos móviles", "descripcion": "Gestión tablets, smartphones corporativos, MDM", "urgencia": "media", "es_core_srs": False, "keywords": ["móviles", "tablets", "smartphones", "MDM", "dispositivos"]},
    {"tipo": "infraestructura", "subtipo": "puesto", "nombre": "Impresoras y periféricos", "descripcion": "Gestión parque impresoras, multifuncionales, escáneres, plotters", "urgencia": "baja", "es_core_srs": False, "keywords": ["impresoras", "multifuncionales", "escáneres", "plotters", "periféricos"]},
    {"tipo": "infraestructura", "subtipo": "puesto", "nombre": "Estaciones de trabajo alto rendimiento", "descripcion": "Workstations para procesamiento cartográfico, LiDAR, renderizado 3D, IA", "urgencia": "alta", "es_core_srs": False, "keywords": ["workstation", "alto rendimiento", "CAD", "renderizado", "LiDAR"]},
    {"tipo": "infraestructura", "subtipo": "puesto", "nombre": "GPUs / Aceleración gráfica", "descripcion": "Tarjetas gráficas profesionales para procesamiento imágenes, LiDAR, IA (NVIDIA Quadro/Tesla)", "urgencia": "alta", "es_core_srs": False, "keywords": ["GPU", "NVIDIA", "Quadro", "Tesla", "aceleración", "gráfica"]},
    {"tipo": "infraestructura", "subtipo": "almacenamiento", "nombre": "Almacenamiento masivo datos geoespaciales", "descripcion": "Storage de alta capacidad para ortofotos, nubes de puntos LiDAR, modelos 3D", "urgencia": "alta", "es_core_srs": False, "keywords": ["geoespacial", "ortofotos", "LiDAR", "almacenamiento masivo"]},
    {"tipo": "infraestructura", "subtipo": "edge", "nombre": "Edge Computing", "descripcion": "Procesamiento en el borde, IoT gateways, mini CPDs, computación distribuida", "urgencia": "media", "es_core_srs": False, "keywords": ["edge", "borde", "IoT", "gateway", "distribuido", "micro CPD"]},
    {"tipo": "infraestructura", "subtipo": "edge", "nombre": "IoT / Sensórica", "descripcion": "Dispositivos conectados, sensores, plataformas IoT, telemetría", "urgencia": "media", "es_core_srs": False, "keywords": ["IoT", "sensores", "telemetría", "dispositivos conectados", "M2M"]},
    {"tipo": "infraestructura", "subtipo": "seguridad_fisica", "nombre": "Control de acceso físico", "descripcion": "Tornos, lectores biométricos, tarjetas proximidad, control puertas", "urgencia": "media", "es_core_srs": False, "keywords": ["control acceso", "biométrico", "tarjetas", "tornos", "proximidad"]},
    {"tipo": "infraestructura", "subtipo": "seguridad_fisica", "nombre": "CCTV / Videovigilancia IP", "descripcion": "Cámaras IP, grabadores NVR, analítica de video, integración con control acceso", "urgencia": "media", "es_core_srs": False, "keywords": ["CCTV", "videovigilancia", "cámaras", "NVR", "grabación", "IP"]},
    {"tipo": "infraestructura", "subtipo": "seguridad_fisica", "nombre": "Sistemas de intrusión", "descripcion": "Alarmas, detectores de movimiento, centrales de alarma, monitorización", "urgencia": "media", "es_core_srs": False, "keywords": ["intrusión", "alarmas", "detectores", "central alarma"]},
    {"tipo": "infraestructura", "subtipo": "seguridad_fisica", "nombre": "Control de presencia", "descripcion": "Fichaje, gestión horaria, terminales de control, integración RRHH", "urgencia": "baja", "es_core_srs": False, "keywords": ["presencia", "fichaje", "control horario", "RRHH"]},
    {"tipo": "infraestructura", "subtipo": "audiovisual", "nombre": "Digital signage", "descripcion": "Cartelería digital, pantallas informativas, gestión de contenidos", "urgencia": "baja", "es_core_srs": False, "keywords": ["digital signage", "cartelería", "pantallas", "contenidos"]},
    {"tipo": "infraestructura", "subtipo": "audiovisual", "nombre": "Kioscos interactivos", "descripcion": "Puntos de atención automatizados, terminales autoservicio", "urgencia": "baja", "es_core_srs": False, "keywords": ["kiosco", "interactivo", "autoservicio", "terminal"]},
    {"tipo": "infraestructura", "subtipo": "audiovisual", "nombre": "Sistemas de cola / Turnos", "descripcion": "Gestión de espera, dispensadores de turno, pantallas de llamada", "urgencia": "baja", "es_core_srs": False, "keywords": ["turnos", "cola", "espera", "dispensador"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # COMUNICACIONES (24)
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "comunicaciones", "subtipo": "red_local", "nombre": "Redes LAN - Switches", "descripcion": "Diseño, instalación y gestión switches capa 2/3, VLANs, QoS, stacking", "urgencia": "critica", "es_core_srs": True, "keywords": ["switch", "LAN", "VLAN", "QoS", "Cisco", "HPE", "Aruba", "capa 2", "capa 3"]},
    {"tipo": "comunicaciones", "subtipo": "red_local", "nombre": "Redes WiFi - Access Points", "descripcion": "Diseño cobertura, instalación APs, controladores wireless, site surveys", "urgencia": "alta", "es_core_srs": True, "keywords": ["WiFi", "wireless", "AP", "access point", "controlador", "site survey"]},
    {"tipo": "comunicaciones", "subtipo": "red_wan", "nombre": "Redes WAN - Routers", "descripcion": "Configuración y gestión routers, enrutamiento, BGP, OSPF, EIGRP", "urgencia": "critica", "es_core_srs": True, "keywords": ["WAN", "router", "BGP", "OSPF", "enrutamiento", "Cisco"]},
    {"tipo": "comunicaciones", "subtipo": "seguridad_red", "nombre": "Firewalls perimetrales", "descripcion": "Implementación y gestión firewalls (Fortinet, Palo Alto, Cisco, Sophos, Check Point)", "urgencia": "critica", "es_core_srs": True, "keywords": ["firewall", "Fortinet", "Palo Alto", "Cisco ASA", "Sophos", "Check Point"]},
    {"tipo": "comunicaciones", "subtipo": "seguridad_red", "nombre": "NAC - Network Access Control", "descripcion": "Control de acceso a red, 802.1X, posturing, segmentación por identidad", "urgencia": "alta", "es_core_srs": False, "keywords": ["NAC", "802.1X", "control acceso red", "posturing", "Cisco ISE", "Aruba ClearPass"]},
    {"tipo": "comunicaciones", "subtipo": "seguridad_red", "nombre": "Segmentación de red", "descripcion": "Microsegmentación, zonas DMZ, separación de entornos, zero trust network", "urgencia": "alta", "es_core_srs": False, "keywords": ["segmentación", "DMZ", "microsegmentación", "zonas", "zero trust"]},
    {"tipo": "comunicaciones", "subtipo": "vpn", "nombre": "VPN Site-to-Site", "descripcion": "Túneles seguros entre sedes, IPSec, configuración redundancia", "urgencia": "alta", "es_core_srs": True, "keywords": ["VPN", "site-to-site", "IPSec", "túnel", "sede a sede"]},
    {"tipo": "comunicaciones", "subtipo": "vpn", "nombre": "VPN Client / Acceso remoto", "descripcion": "Conexiones seguras usuarios remotos, SSL VPN, always-on VPN, GlobalProtect", "urgencia": "alta", "es_core_srs": True, "keywords": ["VPN", "remoto", "SSL VPN", "GlobalProtect", "AnyConnect", "acceso remoto"]},
    {"tipo": "comunicaciones", "subtipo": "wan", "nombre": "SD-WAN", "descripcion": "Redes definidas por software, optimización tráfico, failover automático", "urgencia": "media", "es_core_srs": False, "keywords": ["SD-WAN", "software defined", "optimización", "failover", "Meraki", "Viptela"]},
    {"tipo": "comunicaciones", "subtipo": "wan", "nombre": "MPLS", "descripcion": "Gestión circuitos MPLS operador, QoS, SLAs, troubleshooting", "urgencia": "media", "es_core_srs": False, "keywords": ["MPLS", "circuito", "operador", "QoS", "VPN MPLS"]},
    {"tipo": "comunicaciones", "subtipo": "wan", "nombre": "Internet dedicado", "descripcion": "Gestión líneas dedicadas, fibra, redundancia, balanceo, failover", "urgencia": "alta", "es_core_srs": False, "keywords": ["internet", "dedicado", "fibra", "redundancia", "balanceo"]},
    {"tipo": "comunicaciones", "subtipo": "wan", "nombre": "Backup 4G/5G", "descripcion": "Líneas móviles de respaldo, routers LTE/5G, failover automático", "urgencia": "media", "es_core_srs": False, "keywords": ["4G", "5G", "LTE", "backup", "respaldo", "móvil"]},
    {"tipo": "comunicaciones", "subtipo": "wan", "nombre": "Comunicaciones satelitales", "descripcion": "Enlace satélite para zonas remotas, VSAT, Starlink", "urgencia": "media", "es_core_srs": False, "keywords": ["satélite", "VSAT", "Starlink", "remoto", "comunicaciones"]},
    {"tipo": "comunicaciones", "subtipo": "wan", "nombre": "Radioenlaces", "descripcion": "Enlaces punto a punto microondas, conexión sedes sin fibra", "urgencia": "baja", "es_core_srs": False, "keywords": ["radioenlace", "microondas", "punto a punto", "wireless bridge"]},
    {"tipo": "comunicaciones", "subtipo": "balanceo", "nombre": "Balanceadores de carga", "descripcion": "Distribución tráfico, alta disponibilidad aplicaciones, F5, HAProxy, Citrix ADC", "urgencia": "alta", "es_core_srs": False, "keywords": ["balanceador", "F5", "HAProxy", "Citrix ADC", "load balancer", "ADC"]},
    {"tipo": "comunicaciones", "subtipo": "proxy", "nombre": "Proxy / Filtrado web", "descripcion": "Control navegación, caché, reporting, categorización, Zscaler, Bluecoat", "urgencia": "media", "es_core_srs": False, "keywords": ["proxy", "filtrado", "navegación", "Zscaler", "Bluecoat", "web filter"]},
    {"tipo": "comunicaciones", "subtipo": "dns", "nombre": "DNS/DHCP avanzado (DDI)", "descripcion": "DDI enterprise, IPAM, gestión direccionamiento, Infoblox, BlueCat", "urgencia": "media", "es_core_srs": False, "keywords": ["DDI", "IPAM", "Infoblox", "BlueCat", "DNS", "DHCP", "direccionamiento"]},
    {"tipo": "comunicaciones", "subtipo": "qos", "nombre": "Gestión de ancho de banda", "descripcion": "Traffic shaping, QoS avanzado, priorización tráfico, NetFlow", "urgencia": "media", "es_core_srs": False, "keywords": ["QoS", "traffic shaping", "ancho de banda", "priorización", "NetFlow"]},
    {"tipo": "comunicaciones", "subtipo": "telefonia", "nombre": "Telefonía IP / VoIP", "descripcion": "Centralitas virtuales, SIP trunks, gestión numeración, Cisco CUCM, Avaya", "urgencia": "media", "es_core_srs": False, "keywords": ["VoIP", "telefonía IP", "SIP", "centralita", "CUCM", "Avaya"]},
    {"tipo": "comunicaciones", "subtipo": "telefonia", "nombre": "Contact Center", "descripcion": "Plataformas ACD, IVR, grabación llamadas, omnicanal, Genesys, Five9", "urgencia": "media", "es_core_srs": False, "keywords": ["contact center", "call center", "ACD", "IVR", "Genesys", "omnicanal"]},
    {"tipo": "comunicaciones", "subtipo": "colaboracion", "nombre": "Comunicaciones unificadas", "descripcion": "Integración voz, video, chat, presencia en plataforma única", "urgencia": "media", "es_core_srs": False, "keywords": ["UC", "comunicaciones unificadas", "colaboración", "presencia"]},
    {"tipo": "comunicaciones", "subtipo": "colaboracion", "nombre": "Microsoft Teams - Administración", "descripcion": "Gestión Teams: usuarios, políticas, telefonía, salas, integraciones, Teams Rooms", "urgencia": "alta", "es_core_srs": True, "keywords": ["Teams", "Microsoft Teams", "colaboración", "telefonía Teams", "Teams Rooms"]},
    {"tipo": "comunicaciones", "subtipo": "colaboracion", "nombre": "Videoconferencia / Salas", "descripcion": "Equipamiento salas reuniones, integración Teams/Zoom/Webex, gestión reservas", "urgencia": "media", "es_core_srs": False, "keywords": ["videoconferencia", "salas", "Zoom", "Webex", "Poly", "Logitech"]},
    {"tipo": "comunicaciones", "subtipo": "especializado", "nombre": "Transmisión datos drones en tiempo real", "descripcion": "Streaming video/telemetría desde drones, enlaces dedicados, latencia mínima", "urgencia": "alta", "es_core_srs": False, "keywords": ["drones", "streaming", "telemetría", "tiempo real", "video"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # SOFTWARE (52)
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "software", "subtipo": "sistemas_operativos", "nombre": "Windows Server", "descripcion": "Instalación, configuración y administración Windows Server 2016/2019/2022/2025", "urgencia": "critica", "es_core_srs": True, "keywords": ["Windows Server", "2019", "2022", "Microsoft", "servidor"]},
    {"tipo": "software", "subtipo": "sistemas_operativos", "nombre": "Linux Server", "descripcion": "Administración servidores Linux (RHEL, Ubuntu, CentOS, Rocky, Debian, SUSE)", "urgencia": "alta", "es_core_srs": True, "keywords": ["Linux", "RHEL", "Ubuntu", "CentOS", "Rocky", "Debian", "SUSE"]},
    {"tipo": "software", "subtipo": "directorio", "nombre": "Active Directory", "descripcion": "Diseño, implementación y gestión AD DS, GPOs, estructura OUs, Sites", "urgencia": "critica", "es_core_srs": True, "keywords": ["Active Directory", "AD", "GPO", "dominio", "LDAP", "directorio"]},
    {"tipo": "software", "subtipo": "directorio", "nombre": "Azure AD / Entra ID", "descripcion": "Identidad cloud, sincronización híbrida, conditional access, PIM", "urgencia": "alta", "es_core_srs": True, "keywords": ["Azure AD", "Entra ID", "identidad", "cloud", "híbrido", "conditional access"]},
    {"tipo": "software", "subtipo": "red", "nombre": "DNS", "descripcion": "Servicios resolución nombres, zonas internas/externas, split DNS, DNSSEC", "urgencia": "critica", "es_core_srs": True, "keywords": ["DNS", "resolución", "zonas", "DNSSEC"]},
    {"tipo": "software", "subtipo": "red", "nombre": "DHCP", "descripcion": "Asignación dinámica IPs, reservas, scopes, failover, opciones DHCP", "urgencia": "critica", "es_core_srs": True, "keywords": ["DHCP", "IP", "direccionamiento", "scopes"]},
    {"tipo": "software", "subtipo": "productividad", "nombre": "Microsoft 365", "descripcion": "Administración tenant M365: Exchange Online, SharePoint, OneDrive, Teams, licencias", "urgencia": "critica", "es_core_srs": True, "keywords": ["Microsoft 365", "M365", "Office 365", "O365", "Exchange Online", "SharePoint"]},
    {"tipo": "software", "subtipo": "productividad", "nombre": "Google Workspace", "descripcion": "Gestión entorno Google: Gmail, Drive, Calendar, Admin Console, Vault", "urgencia": "alta", "es_core_srs": True, "keywords": ["Google Workspace", "Gmail", "Drive", "G Suite", "Google"]},
    {"tipo": "software", "subtipo": "correo", "nombre": "Exchange Server On-Premise", "descripcion": "Administración Exchange local, migraciones, coexistencia híbrida, DAG", "urgencia": "media", "es_core_srs": False, "keywords": ["Exchange", "correo", "on-premise", "DAG", "híbrido"]},
    {"tipo": "software", "subtipo": "bbdd", "nombre": "Bases de datos SQL Server", "descripcion": "Administración SQL Server, backups, optimización, Always On, replicación", "urgencia": "alta", "es_core_srs": True, "keywords": ["SQL Server", "MSSQL", "base de datos", "Always On", "Microsoft SQL"]},
    {"tipo": "software", "subtipo": "bbdd", "nombre": "Bases de datos MySQL/PostgreSQL", "descripcion": "Gestión bases datos open source, replicación, tuning, alta disponibilidad", "urgencia": "alta", "es_core_srs": False, "keywords": ["MySQL", "PostgreSQL", "MariaDB", "base de datos", "open source"]},
    {"tipo": "software", "subtipo": "bbdd", "nombre": "Bases de datos Oracle", "descripcion": "Administración Oracle Database, RAC, Data Guard, tuning", "urgencia": "alta", "es_core_srs": False, "keywords": ["Oracle", "RAC", "Data Guard", "base de datos"]},
    {"tipo": "software", "subtipo": "bbdd", "nombre": "Bases de datos geoespaciales (PostGIS)", "descripcion": "Almacenamiento y consulta datos geográficos, integración GIS", "urgencia": "alta", "es_core_srs": False, "keywords": ["PostGIS", "geoespacial", "GIS", "PostgreSQL", "geográfico"]},
    {"tipo": "software", "subtipo": "erp_crm", "nombre": "ERP (SAP, Oracle, Dynamics)", "descripcion": "Implementación, soporte y administración sistemas ERP enterprise", "urgencia": "alta", "es_core_srs": False, "keywords": ["ERP", "SAP", "Oracle ERP", "Dynamics 365", "gestión empresarial"]},
    {"tipo": "software", "subtipo": "erp_crm", "nombre": "CRM (Salesforce, Dynamics)", "descripcion": "Plataformas gestión comercial y relación con clientes", "urgencia": "media", "es_core_srs": False, "keywords": ["CRM", "Salesforce", "Dynamics CRM", "HubSpot", "comercial"]},
    {"tipo": "software", "subtipo": "desarrollo", "nombre": "Desarrollo a medida", "descripcion": "Aplicaciones custom, integraciones, APIs, desarrollo software", "urgencia": "media", "es_core_srs": False, "keywords": ["desarrollo", "custom", "aplicaciones", "programación", "software"]},
    {"tipo": "software", "subtipo": "desarrollo", "nombre": "Aplicaciones legacy", "descripcion": "Mantenimiento sistemas antiguos, COBOL, AS400, modernización", "urgencia": "media", "es_core_srs": False, "keywords": ["legacy", "COBOL", "AS400", "mainframe", "antiguo"]},
    {"tipo": "software", "subtipo": "virtualizacion_apps", "nombre": "Virtualización de aplicaciones", "descripcion": "Citrix Virtual Apps, AVD, RemoteApp, publicación aplicaciones", "urgencia": "alta", "es_core_srs": False, "keywords": ["Citrix", "AVD", "RemoteApp", "virtualización", "VDI", "escritorio virtual"]},
    {"tipo": "software", "subtipo": "gestion_documental", "nombre": "Gestión documental (ECM)", "descripcion": "Alfresco, SharePoint avanzado, workflows documentales, digitalización", "urgencia": "media", "es_core_srs": False, "keywords": ["ECM", "gestión documental", "Alfresco", "SharePoint", "documentos"]},
    {"tipo": "software", "subtipo": "bi", "nombre": "Business Intelligence", "descripcion": "Power BI, Tableau, Qlik, reporting, dashboards, analítica", "urgencia": "media", "es_core_srs": False, "keywords": ["BI", "Power BI", "Tableau", "Qlik", "reporting", "analítica"]},
    {"tipo": "software", "subtipo": "bi", "nombre": "ETL / Integración datos", "descripcion": "Talend, SSIS, Azure Data Factory, pipelines datos, datawarehouse", "urgencia": "media", "es_core_srs": False, "keywords": ["ETL", "Talend", "SSIS", "Data Factory", "integración", "datos"]},
    {"tipo": "software", "subtipo": "automatizacion", "nombre": "RPA - Automatización robótica", "descripcion": "UiPath, Blue Prism, Power Automate Desktop, automatización procesos", "urgencia": "media", "es_core_srs": False, "keywords": ["RPA", "UiPath", "Blue Prism", "automatización", "robot"]},
    {"tipo": "software", "subtipo": "automatizacion", "nombre": "Low-code / No-code", "descripcion": "Power Apps, OutSystems, Mendix, desarrollo ciudadano", "urgencia": "media", "es_core_srs": False, "keywords": ["low-code", "no-code", "Power Apps", "OutSystems", "Mendix"]},
    {"tipo": "software", "subtipo": "firma", "nombre": "Firma electrónica", "descripcion": "Certificados digitales, firma avanzada/cualificada, validación, sello tiempo", "urgencia": "media", "es_core_srs": False, "keywords": ["firma electrónica", "certificado", "digital", "validación", "sello tiempo"]},
    {"tipo": "software", "subtipo": "impresion", "nombre": "Gestión de impresión", "descripcion": "PrinterLogic, PaperCut, pull printing, control costes impresión", "urgencia": "baja", "es_core_srs": False, "keywords": ["impresión", "PrinterLogic", "PaperCut", "pull printing"]},
    {"tipo": "software", "subtipo": "email_security", "nombre": "Antispam dedicado", "descripcion": "Proofpoint, Mimecast, Barracuda, protección correo avanzada", "urgencia": "alta", "es_core_srs": False, "keywords": ["antispam", "Proofpoint", "Mimecast", "Barracuda", "correo"]},
    {"tipo": "software", "subtipo": "itsm", "nombre": "ITSM - ServiceNow", "descripcion": "Plataforma gestión servicios IT, tickets, CMDB, workflows, ITOM", "urgencia": "media", "es_core_srs": False, "keywords": ["ServiceNow", "ITSM", "tickets", "CMDB", "gestión servicios"]},
    {"tipo": "software", "subtipo": "itsm", "nombre": "ITSM - Jira Service Management", "descripcion": "Gestión incidencias, peticiones, cambios, SLAs, Confluence", "urgencia": "media", "es_core_srs": False, "keywords": ["Jira", "Atlassian", "Service Management", "tickets", "Confluence"]},
    {"tipo": "software", "subtipo": "itsm", "nombre": "ITSM - Freshservice/Freshdesk", "descripcion": "Helpdesk cloud, gestión tickets, base conocimiento, autoservicio", "urgencia": "media", "es_core_srs": False, "keywords": ["Freshservice", "Freshdesk", "helpdesk", "tickets", "cloud"]},
    {"tipo": "software", "subtipo": "monitorizacion", "nombre": "Monitorización - Zabbix", "descripcion": "Monitorización infraestructura open source, alertas, dashboards, templates", "urgencia": "alta", "es_core_srs": True, "keywords": ["Zabbix", "monitorización", "alertas", "open source"]},
    {"tipo": "software", "subtipo": "monitorizacion", "nombre": "Monitorización - PRTG", "descripcion": "Monitorización red y sistemas, sensores, reporting, mapas", "urgencia": "alta", "es_core_srs": True, "keywords": ["PRTG", "monitorización", "sensores", "Paessler"]},
    {"tipo": "software", "subtipo": "monitorizacion", "nombre": "Monitorización - Nagios", "descripcion": "Monitorización infraestructura, plugins, alertas, Nagios XI", "urgencia": "media", "es_core_srs": False, "keywords": ["Nagios", "monitorización", "plugins", "alertas"]},
    {"tipo": "software", "subtipo": "monitorizacion", "nombre": "Monitorización - Datadog/New Relic", "descripcion": "Observabilidad cloud, APM, logs, métricas, trazas", "urgencia": "media", "es_core_srs": False, "keywords": ["Datadog", "New Relic", "APM", "observabilidad", "cloud"]},
    {"tipo": "software", "subtipo": "rmm", "nombre": "RMM - Gestión remota endpoints", "descripcion": "Herramientas administración remota (ConnectWise, Datto, NinjaRMM, N-able)", "urgencia": "alta", "es_core_srs": True, "keywords": ["RMM", "ConnectWise", "Datto", "NinjaRMM", "gestión remota"]},
    {"tipo": "software", "subtipo": "backup", "nombre": "Backup - Veeam", "descripcion": "Backup y replicación VMs, recuperación granular, cloud connect, inmutabilidad", "urgencia": "critica", "es_core_srs": True, "keywords": ["Veeam", "backup", "replicación", "recuperación", "VMs"]},
    {"tipo": "software", "subtipo": "backup", "nombre": "Backup - Commvault", "descripcion": "Backup enterprise, deduplicación, archivado, gestión datos", "urgencia": "alta", "es_core_srs": False, "keywords": ["Commvault", "backup", "enterprise", "archivado"]},
    {"tipo": "software", "subtipo": "backup", "nombre": "Backup - Acronis", "descripcion": "Backup endpoints y servidores, disaster recovery, cyber protect", "urgencia": "alta", "es_core_srs": True, "keywords": ["Acronis", "backup", "disaster recovery", "cyber protect"]},
    {"tipo": "software", "subtipo": "backup", "nombre": "Backup cloud (M365, Google)", "descripcion": "Backup datos SaaS: correo, SharePoint, Drive, Teams (Veeam, AvePoint, Spanning)", "urgencia": "alta", "es_core_srs": True, "keywords": ["backup SaaS", "M365 backup", "AvePoint", "Spanning", "cloud backup"]},
    {"tipo": "software", "subtipo": "dr", "nombre": "DRaaS - Disaster Recovery as a Service", "descripcion": "Replicación offsite, failover automatizado, RTO/RPO definidos, Zerto, Azure Site Recovery", "urgencia": "alta", "es_core_srs": False, "keywords": ["DRaaS", "disaster recovery", "Zerto", "replicación", "failover"]},
    {"tipo": "software", "subtipo": "automatizacion", "nombre": "Automatización - Ansible", "descripcion": "Automatización configuración servidores, playbooks, IaC, Red Hat", "urgencia": "media", "es_core_srs": False, "keywords": ["Ansible", "automatización", "playbooks", "IaC", "configuración"]},
    {"tipo": "software", "subtipo": "automatizacion", "nombre": "Automatización - Terraform", "descripcion": "Infrastructure as Code, provisioning cloud, versionado, HashiCorp", "urgencia": "media", "es_core_srs": False, "keywords": ["Terraform", "IaC", "HashiCorp", "provisioning", "infraestructura"]},
    {"tipo": "software", "subtipo": "automatizacion", "nombre": "Automatización - Power Automate", "descripcion": "Flujos automatizados Microsoft, integración M365, conectores, cloud flows", "urgencia": "media", "es_core_srs": False, "keywords": ["Power Automate", "Microsoft", "flujos", "automatización", "Flow"]},
    {"tipo": "software", "subtipo": "automatizacion", "nombre": "Automatización - n8n/Make", "descripcion": "Automatización procesos, integración APIs, workflows, Zapier alternativo", "urgencia": "media", "es_core_srs": False, "keywords": ["n8n", "Make", "Integromat", "Zapier", "automatización", "workflows"]},
    {"tipo": "software", "subtipo": "contenedores", "nombre": "Contenedores - Docker", "descripcion": "Containerización aplicaciones, imágenes, registries, Docker Compose", "urgencia": "media", "es_core_srs": False, "keywords": ["Docker", "contenedores", "imágenes", "registry", "containerización"]},
    {"tipo": "software", "subtipo": "contenedores", "nombre": "Orquestación - Kubernetes", "descripcion": "Gestión clusters K8s, deployments, scaling, helm charts, AKS, EKS, GKE", "urgencia": "media", "es_core_srs": False, "keywords": ["Kubernetes", "K8s", "AKS", "EKS", "GKE", "orquestación", "helm"]},
    {"tipo": "software", "subtipo": "devops", "nombre": "CI/CD - Pipelines", "descripcion": "Integración y despliegue continuo (Azure DevOps, GitHub Actions, GitLab CI, Jenkins)", "urgencia": "media", "es_core_srs": False, "keywords": ["CI/CD", "DevOps", "Azure DevOps", "GitHub Actions", "GitLab", "Jenkins"]},
    {"tipo": "software", "subtipo": "drones", "nombre": "Software fotogrametría (Pix4D)", "descripcion": "Procesamiento imágenes drones, generación ortofotos, modelos 3D", "urgencia": "critica", "es_core_srs": False, "keywords": ["Pix4D", "fotogrametría", "ortofotos", "3D", "drones"]},
    {"tipo": "software", "subtipo": "drones", "nombre": "Software fotogrametría (Agisoft Metashape)", "descripcion": "Procesamiento fotogramétrico, nubes de puntos, texturas", "urgencia": "alta", "es_core_srs": False, "keywords": ["Agisoft", "Metashape", "fotogrametría", "nubes de puntos"]},
    {"tipo": "software", "subtipo": "drones", "nombre": "Software fotogrametría (DroneDeploy)", "descripcion": "Plataforma cloud para procesamiento y análisis datos drones", "urgencia": "alta", "es_core_srs": False, "keywords": ["DroneDeploy", "cloud", "drones", "análisis"]},
    {"tipo": "software", "subtipo": "drones", "nombre": "APIs integración datos drones", "descripcion": "Desarrollo APIs REST para consumo datos cartográficos, ortofotos, modelos", "urgencia": "alta", "es_core_srs": False, "keywords": ["API", "drones", "integración", "cartográfico", "REST"]},

    # ═══════════════════════════════════════════════════════════════════════════
    # SEGURIDAD (41)
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "seguridad", "subtipo": "perimetral", "nombre": "Firewall Next-Gen (NGFW)", "descripcion": "Firewalls con inspección profunda, IPS integrado, application control, SSL inspection", "urgencia": "critica", "es_core_srs": True, "keywords": ["NGFW", "firewall", "next-gen", "IPS", "Fortinet", "Palo Alto"]},
    {"tipo": "seguridad", "subtipo": "perimetral", "nombre": "IDS/IPS", "descripcion": "Sistemas detección y prevención intrusiones, análisis tráfico, Snort, Suricata", "urgencia": "alta", "es_core_srs": False, "keywords": ["IDS", "IPS", "intrusiones", "detección", "Snort", "Suricata"]},
    {"tipo": "seguridad", "subtipo": "perimetral", "nombre": "WAF - Web Application Firewall", "descripcion": "Protección aplicaciones web, OWASP, reglas personalizadas, Cloudflare, Imperva", "urgencia": "alta", "es_core_srs": False, "keywords": ["WAF", "web application firewall", "OWASP", "Cloudflare", "Imperva"]},
    {"tipo": "seguridad", "subtipo": "endpoint", "nombre": "Antivirus / Antimalware", "descripcion": "Protección endpoints, consola centralizada, actualizaciones, cuarentena", "urgencia": "critica", "es_core_srs": True, "keywords": ["antivirus", "antimalware", "endpoint", "protección", "Kaspersky", "ESET"]},
    {"tipo": "seguridad", "subtipo": "endpoint", "nombre": "EDR - Endpoint Detection & Response", "descripcion": "Detección avanzada amenazas endpoints, respuesta automatizada (CrowdStrike, SentinelOne, Defender)", "urgencia": "alta", "es_core_srs": True, "keywords": ["EDR", "CrowdStrike", "SentinelOne", "Defender", "endpoint", "detección"]},
    {"tipo": "seguridad", "subtipo": "endpoint", "nombre": "XDR - Extended Detection & Response", "descripcion": "Correlación eventos múltiples fuentes, respuesta unificada, Palo Alto Cortex, Microsoft Sentinel", "urgencia": "media", "es_core_srs": False, "keywords": ["XDR", "Cortex", "detección extendida", "correlación"]},
    {"tipo": "seguridad", "subtipo": "soc", "nombre": "SIEM", "descripcion": "Correlación eventos seguridad, análisis logs, alertas (Splunk, Sentinel, QRadar, Elastic)", "urgencia": "alta", "es_core_srs": False, "keywords": ["SIEM", "Splunk", "Sentinel", "QRadar", "logs", "correlación"]},
    {"tipo": "seguridad", "subtipo": "soc", "nombre": "SOC - Centro Operaciones Seguridad", "descripcion": "Monitorización 24x7 seguridad, análisis alertas, respuesta incidentes, threat hunting", "urgencia": "alta", "es_core_srs": False, "keywords": ["SOC", "centro operaciones", "seguridad", "24x7", "monitorización"]},
    {"tipo": "seguridad", "subtipo": "soc", "nombre": "Respuesta a incidentes (IR)", "descripcion": "Equipo respuesta, contención, erradicación, recuperación, lecciones aprendidas", "urgencia": "alta", "es_core_srs": False, "keywords": ["incident response", "IR", "respuesta", "incidentes", "contención"]},
    {"tipo": "seguridad", "subtipo": "soc", "nombre": "Análisis forense", "descripcion": "Investigación post-incidente, preservación evidencias, cadena de custodia, informes periciales", "urgencia": "media", "es_core_srs": False, "keywords": ["forense", "forensic", "investigación", "evidencias", "pericial"]},
    {"tipo": "seguridad", "subtipo": "soc", "nombre": "Threat Intelligence", "descripcion": "Feeds de amenazas, IOCs, análisis proactivo, MITRE ATT&CK", "urgencia": "media", "es_core_srs": False, "keywords": ["threat intelligence", "IOC", "amenazas", "MITRE", "inteligencia"]},
    {"tipo": "seguridad", "subtipo": "ofensivo", "nombre": "Red Team / Blue Team", "descripcion": "Simulación ataques, defensa activa, ejercicios purple team", "urgencia": "media", "es_core_srs": False, "keywords": ["red team", "blue team", "purple team", "simulación", "ataque"]},
    {"tipo": "seguridad", "subtipo": "vulnerabilidades", "nombre": "Gestión vulnerabilidades", "descripcion": "Escaneo periódico, priorización CVEs, seguimiento remediación (Qualys, Nessus, Rapid7)", "urgencia": "alta", "es_core_srs": False, "keywords": ["vulnerabilidades", "Qualys", "Nessus", "Rapid7", "CVE", "escaneo"]},
    {"tipo": "seguridad", "subtipo": "vulnerabilidades", "nombre": "Pentesting / Test intrusión", "descripcion": "Pruebas penetración infraestructura y aplicaciones, informes, OWASP", "urgencia": "media", "es_core_srs": False, "keywords": ["pentesting", "penetration test", "intrusión", "ethical hacking"]},
    {"tipo": "seguridad", "subtipo": "vulnerabilidades", "nombre": "Gestión de parches", "descripcion": "Patch management, WSUS, SCCM, Intune, automatización actualizaciones", "urgencia": "alta", "es_core_srs": True, "keywords": ["parches", "patch management", "WSUS", "SCCM", "Intune", "actualizaciones"]},
    {"tipo": "seguridad", "subtipo": "hardening", "nombre": "Hardening sistemas", "descripcion": "Bastionado servidores y endpoints según CIS benchmarks, GPOs seguridad", "urgencia": "alta", "es_core_srs": True, "keywords": ["hardening", "bastionado", "CIS", "benchmarks", "seguridad"]},
    {"tipo": "seguridad", "subtipo": "cifrado", "nombre": "Cifrado datos en reposo", "descripcion": "Encriptación discos, bases datos, almacenamiento (BitLocker, LUKS, TDE)", "urgencia": "alta", "es_core_srs": False, "keywords": ["cifrado", "encriptación", "BitLocker", "LUKS", "TDE", "reposo"]},
    {"tipo": "seguridad", "subtipo": "cifrado", "nombre": "Cifrado datos en tránsito", "descripcion": "TLS/SSL, certificados, gestión PKI, Let's Encrypt, certificados internos", "urgencia": "alta", "es_core_srs": False, "keywords": ["TLS", "SSL", "certificados", "PKI", "cifrado", "tránsito"]},
    {"tipo": "seguridad", "subtipo": "cifrado", "nombre": "Certificados y PKI", "descripcion": "Gestión certificados SSL/TLS, CA interna, renovaciones, HSM", "urgencia": "media", "es_core_srs": False, "keywords": ["PKI", "certificados", "CA", "HSM", "SSL", "renovación"]},
    {"tipo": "seguridad", "subtipo": "datos", "nombre": "DLP - Data Loss Prevention", "descripcion": "Prevención fuga datos, políticas clasificación, monitorización, Microsoft Purview", "urgencia": "media", "es_core_srs": False, "keywords": ["DLP", "data loss prevention", "fuga datos", "Purview", "clasificación"]},
    {"tipo": "seguridad", "subtipo": "datos", "nombre": "Clasificación de información", "descripcion": "Etiquetado datos, políticas sensibilidad, Microsoft AIP, Titus", "urgencia": "media", "es_core_srs": False, "keywords": ["clasificación", "etiquetado", "AIP", "sensibilidad", "información"]},
    {"tipo": "seguridad", "subtipo": "datos", "nombre": "Borrado seguro", "descripcion": "Destrucción datos, certificación, RAEE, desmagnetización, sobreescritura", "urgencia": "media", "es_core_srs": False, "keywords": ["borrado seguro", "destrucción", "RAEE", "certificación", "datos"]},
    {"tipo": "seguridad", "subtipo": "identidad", "nombre": "IAM - Identity & Access Management", "descripcion": "Gestión identidades, provisioning, lifecycle usuarios, gobernanza", "urgencia": "alta", "es_core_srs": False, "keywords": ["IAM", "identidad", "acceso", "provisioning", "gobernanza"]},
    {"tipo": "seguridad", "subtipo": "identidad", "nombre": "PAM - Privileged Access Management", "descripcion": "Gestión accesos privilegiados, bóveda contraseñas, grabación sesiones (CyberArk, BeyondTrust, Delinea)", "urgencia": "alta", "es_core_srs": False, "keywords": ["PAM", "privilegiado", "CyberArk", "BeyondTrust", "bóveda", "contraseñas"]},
    {"tipo": "seguridad", "subtipo": "identidad", "nombre": "MFA - Autenticación multifactor", "descripcion": "Segundo factor autenticación, tokens, apps authenticator, passwordless", "urgencia": "critica", "es_core_srs": True, "keywords": ["MFA", "2FA", "multifactor", "autenticación", "token", "authenticator"]},
    {"tipo": "seguridad", "subtipo": "identidad", "nombre": "SSO - Single Sign-On", "descripcion": "Autenticación única, federación identidades, SAML, OAuth, OIDC", "urgencia": "alta", "es_core_srs": False, "keywords": ["SSO", "single sign-on", "SAML", "OAuth", "federación", "OIDC"]},
    {"tipo": "seguridad", "subtipo": "zero_trust", "nombre": "Zero Trust Network Access", "descripcion": "Acceso basado en identidad, microsegmentación, verificación continua, ZTNA", "urgencia": "media", "es_core_srs": False, "keywords": ["zero trust", "ZTNA", "microsegmentación", "acceso", "identidad"]},
    {"tipo": "seguridad", "subtipo": "cloud", "nombre": "CASB - Cloud Access Security Broker", "descripcion": "Seguridad acceso cloud, shadow IT, DLP cloud, Microsoft Defender for Cloud Apps", "urgencia": "media", "es_core_srs": False, "keywords": ["CASB", "cloud security", "shadow IT", "Defender Cloud Apps"]},
    {"tipo": "seguridad", "subtipo": "email", "nombre": "Email Security", "descripcion": "Protección correo: antispam, antiphishing, sandboxing adjuntos, DMARC, SPF, DKIM", "urgencia": "alta", "es_core_srs": True, "keywords": ["email security", "antiphishing", "DMARC", "SPF", "DKIM", "correo"]},
    {"tipo": "seguridad", "subtipo": "awareness", "nombre": "Concienciación seguridad / Awareness", "descripcion": "Formación usuarios, simulaciones phishing, campañas, KnowBe4", "urgencia": "media", "es_core_srs": False, "keywords": ["awareness", "concienciación", "phishing", "formación", "KnowBe4"]},
    {"tipo": "seguridad", "subtipo": "backup", "nombre": "Backup inmutable / Air-gapped", "descripcion": "Copias seguridad protegidas contra ransomware, WORM, aislamiento", "urgencia": "alta", "es_core_srs": True, "keywords": ["inmutable", "air-gapped", "ransomware", "WORM", "backup"]},
    {"tipo": "seguridad", "subtipo": "continuidad", "nombre": "Plan continuidad negocio (BCP)", "descripcion": "Documentación, procedimientos, pruebas recuperación, análisis impacto", "urgencia": "alta", "es_core_srs": False, "keywords": ["BCP", "continuidad", "negocio", "BIA", "procedimientos"]},
    {"tipo": "seguridad", "subtipo": "continuidad", "nombre": "Plan recuperación desastres (DRP)", "descripcion": "Procedimientos recuperación IT, RTO/RPO, pruebas periódicas, failover", "urgencia": "alta", "es_core_srs": False, "keywords": ["DRP", "disaster recovery", "RTO", "RPO", "recuperación"]},
    {"tipo": "seguridad", "subtipo": "cumplimiento", "nombre": "Cumplimiento ENS", "descripcion": "Adecuación Esquema Nacional Seguridad niveles Bajo/Medio/Alto, auditoría, certificación", "urgencia": "critica", "es_core_srs": True, "keywords": ["ENS", "Esquema Nacional Seguridad", "cumplimiento", "certificación", "público"]},
    {"tipo": "seguridad", "subtipo": "cumplimiento", "nombre": "Cumplimiento ISO 27001", "descripcion": "Sistema gestión seguridad información, auditorías, certificación, controles", "urgencia": "alta", "es_core_srs": False, "keywords": ["ISO 27001", "SGSI", "certificación", "auditoría", "controles"]},
    {"tipo": "seguridad", "subtipo": "cumplimiento", "nombre": "Cumplimiento GDPR/LOPD", "descripcion": "Protección datos personales, DPO, registros tratamiento, evaluaciones impacto", "urgencia": "alta", "es_core_srs": False, "keywords": ["GDPR", "LOPD", "RGPD", "datos personales", "DPO", "privacidad"]},
    {"tipo": "seguridad", "subtipo": "cumplimiento", "nombre": "Auditoría de cumplimiento", "descripcion": "NIS2, DORA, PCI-DSS, SOX, auditorías regulatorias, gap analysis", "urgencia": "alta", "es_core_srs": False, "keywords": ["NIS2", "DORA", "PCI-DSS", "SOX", "auditoría", "cumplimiento"]},
    {"tipo": "seguridad", "subtipo": "cumplimiento", "nombre": "Gestión de riesgos IT", "descripcion": "Análisis riesgos, frameworks (NIST, ISO 31000), reporting, mitigación", "urgencia": "media", "es_core_srs": False, "keywords": ["riesgos", "NIST", "ISO 31000", "análisis", "mitigación"]},
    {"tipo": "seguridad", "subtipo": "ot", "nombre": "Seguridad OT/ICS", "descripcion": "Sistemas industriales, SCADA, PLCs, redes OT, Purdue model", "urgencia": "alta", "es_core_srs": False, "keywords": ["OT", "ICS", "SCADA", "industrial", "PLC", "Purdue"]},
    {"tipo": "seguridad", "subtipo": "ot", "nombre": "Seguridad IoT", "descripcion": "Dispositivos conectados, protocolos IoT, segmentación, firmware", "urgencia": "media", "es_core_srs": False, "keywords": ["IoT", "dispositivos", "conectados", "seguridad", "firmware"]},
    {"tipo": "seguridad", "subtipo": "desarrollo", "nombre": "Seguridad en desarrollo (DevSecOps)", "descripcion": "SAST, DAST, análisis código, seguridad pipeline, shift left", "urgencia": "media", "es_core_srs": False, "keywords": ["DevSecOps", "SAST", "DAST", "código", "desarrollo", "shift left"]},
]


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════════════════════════

def generar_lista_servicios_para_prompt() -> str:
    """
    Genera una lista formateada de servicios SRS para incluir en el prompt de IA.
    Agrupa por tipo y muestra nombre + descripción corta.
    """
    servicios_por_tipo = {}
    for item in CATALOGO_SRS:
        tipo = item["tipo"]
        if tipo not in servicios_por_tipo:
            servicios_por_tipo[tipo] = []
        servicios_por_tipo[tipo].append(item)

    resultado = []
    for tipo in ["servicios", "infraestructura", "comunicaciones", "software", "seguridad"]:
        if tipo in servicios_por_tipo:
            resultado.append(f"\n{tipo.upper()}:")
            for s in servicios_por_tipo[tipo]:
                core = " [CORE]" if s.get("es_core_srs") else ""
                resultado.append(f"  • {s['nombre']}{core}: {s['descripcion'][:80]}...")

    return "\n".join(resultado)


def get_servicios_core() -> List[Dict]:
    """Retorna solo los servicios marcados como core de SRS"""
    return [s for s in CATALOGO_SRS if s.get("es_core_srs", False)]


def get_servicios_por_tipo(tipo: str) -> List[Dict]:
    """Retorna servicios filtrados por tipo"""
    return [s for s in CATALOGO_SRS if s["tipo"] == tipo]


def get_servicios_por_subtipo(subtipo: str) -> List[Dict]:
    """Retorna servicios filtrados por subtipo"""
    return [s for s in CATALOGO_SRS if s.get("subtipo") == subtipo]


def buscar_servicios_por_keyword(keyword: str) -> List[Dict]:
    """
    Busca servicios que contengan la keyword en su nombre, descripción o keywords.
    Case-insensitive.
    """
    keyword_lower = keyword.lower()
    resultados = []

    for servicio in CATALOGO_SRS:
        # Buscar en nombre
        if keyword_lower in servicio["nombre"].lower():
            resultados.append(servicio)
            continue

        # Buscar en descripción
        if keyword_lower in servicio["descripcion"].lower():
            resultados.append(servicio)
            continue

        # Buscar en keywords
        for kw in servicio.get("keywords", []):
            if keyword_lower in kw.lower():
                resultados.append(servicio)
                break

    return resultados


def generar_keywords_deteccion() -> dict:
    """
    Genera un diccionario de keywords para detección rápida de componentes.
    Mapea palabras clave a servicios SRS.
    """
    keywords = {}

    for servicio in CATALOGO_SRS:
        nombre = servicio["nombre"]
        for kw in servicio.get("keywords", []):
            kw_lower = kw.lower()
            if kw_lower not in keywords:
                keywords[kw_lower] = []
            if nombre not in keywords[kw_lower]:
                keywords[kw_lower].append(nombre)

    return keywords


def get_estadisticas_catalogo() -> Dict:
    """Retorna estadísticas del catálogo"""
    total = len(CATALOGO_SRS)
    por_tipo = {}
    core_count = 0

    for s in CATALOGO_SRS:
        tipo = s["tipo"]
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        if s.get("es_core_srs"):
            core_count += 1

    return {
        "version": "2.0.0",
        "total_servicios": total,
        "servicios_core": core_count,
        "por_tipo": por_tipo
    }


# Lista resumida para el prompt (más compacta)
SERVICIOS_RESUMEN_PROMPT = """
CATÁLOGO DE SERVICIOS SRS (detecta estos en el pliego):

SERVICIOS GESTIONADOS:
- Soporte técnico N1/N2/N3 (helpdesk, incidencias, troubleshooting) [CORE]
- Helpdesk 24x7 (multicanal, cobertura completa) [CORE]
- Service Desk dedicado (SPOC, ITSM) [CORE]
- Smart Hands / Manos remotas (data centers) [CORE]
- Field Services / Soporte onsite (presencial) [CORE]
- Servicio de guardia / On-call [CORE]
- Mantenimiento preventivo y correctivo [CORE]
- Gestión ITIL (incidencias, cambios, problemas)
- NOC - Centro de Operaciones de Red [CORE]
- Monitorización 24x7 (proactiva, alertas) [CORE]
- Administración remota de sistemas [CORE]
- Staff Augmentation (refuerzo equipos) [CORE]
- Roll-out / Despliegue masivo [CORE]
- IMAC (Install, Move, Add, Change) [CORE]
- Tech Refresh / Renovación tecnológica [CORE]

INFRAESTRUCTURA:
- Servidores físicos (Dell, HPE, Lenovo) [CORE]
- Virtualización (VMware, Hyper-V, Proxmox) [CORE]
- Almacenamiento SAN/NAS/HCI [CORE]
- Cloud (AWS, Azure, GCP, híbrido) [CORE]
- Cableado estructurado (cobre Cat6/7, fibra óptica) [CORE]
- Fusión fibra, certificación Fluke, patch panels [CORE]
- CPD (diseño, climatización, SAI/UPS)
- Racks, PDUs, canalizaciones [CORE]
- Puestos de trabajo / Endpoints [CORE]
- Edge Computing, IoT/Sensórica
- Seguridad física (control acceso, CCTV)

COMUNICACIONES:
- Redes LAN (switches, VLANs, QoS) [CORE]
- Redes WiFi (APs, controladores, site surveys) [CORE]
- Redes WAN (routers, BGP, OSPF) [CORE]
- Firewalls perimetrales (Fortinet, Palo Alto, Cisco) [CORE]
- VPN (site-to-site, acceso remoto) [CORE]
- SD-WAN, MPLS, backup 4G/5G
- NAC, segmentación de red
- Telefonía IP / VoIP, Contact Center
- Comunicaciones unificadas / Teams [CORE]
- Balanceadores, proxy, DDI

SOFTWARE:
- Windows Server / Linux [CORE]
- Active Directory / Azure AD (Entra ID) [CORE]
- Microsoft 365 / Google Workspace [CORE]
- DNS, DHCP [CORE]
- Bases de datos (SQL Server, MySQL, PostgreSQL, Oracle) [CORE]
- Backup (Veeam, Acronis, cloud M365/Google) [CORE]
- Monitorización (Zabbix, PRTG, Nagios) [CORE]
- RMM gestión remota endpoints [CORE]
- ITSM (ServiceNow, Jira, Freshservice)
- Automatización (Ansible, Terraform, Power Automate)
- Contenedores (Docker, Kubernetes)
- CI/CD, DevOps

SEGURIDAD:
- Firewall NGFW, IDS/IPS, WAF [CORE]
- Antivirus / EDR / XDR [CORE]
- SIEM, SOC 24x7
- Gestión vulnerabilidades, pentesting
- Gestión de parches [CORE]
- Hardening sistemas [CORE]
- Cifrado (reposo, tránsito), PKI
- IAM, PAM, MFA [CORE], SSO
- DLP, clasificación información
- Email Security [CORE]
- Backup inmutable [CORE]
- Cumplimiento (ENS [CORE], ISO 27001, GDPR, NIS2, DORA)
- BCP/DRP
- Seguridad OT/ICS, IoT
- DevSecOps

ZONAS DE COBERTURA SRS (evalúa ubicación):
- ZONA BASE (respuesta mismo día, sin coste desplazamiento):
  Madrid, Sevilla, Málaga, Cádiz, Granada, Córdoba, Huelva, Jaén, Almería
- ZONA CERCANA (respuesta 24-48h, coste reducido):
  Toledo, Ciudad Real, Guadalajara, Cuenca, Albacete, Badajoz, Cáceres, Ávila, Segovia, Murcia
- ZONA EXPANSIÓN (respuesta 48-72h, coste estándar):
  Resto de España (Cataluña, Valencia, País Vasco, Galicia, etc.)
"""
