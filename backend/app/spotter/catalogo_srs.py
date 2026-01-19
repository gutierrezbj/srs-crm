"""
Catálogo de servicios y componentes IT de SRS (System Rapid Solutions)

Este catálogo define todos los servicios que SRS puede ofrecer,
organizados por categoría. Se usa para:
1. Detectar oportunidades en pliegos de licitaciones
2. Clasificar componentes IT detectados
3. Generar prompts para análisis con IA
4. Evaluar zonas de cobertura geográfica
"""

# ═══════════════════════════════════════════════════════════════════════════════
# ZONAS DE COBERTURA GEOGRÁFICA
# ═══════════════════════════════════════════════════════════════════════════════

ZONAS_COBERTURA = {
    "base": {
        "descripcion": "Presencia directa, respuesta inmediata, sin coste desplazamiento",
        "tiempo_respuesta": "mismo día",
        "coste_desplazamiento": "incluido",
        "prioridad_score": 20,  # Bonus para scoring de oportunidad
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
# CATÁLOGO DE SERVICIOS
# ═══════════════════════════════════════════════════════════════════════════════

CATALOGO_SRS = [
    # ═══════════════════════════════════════════════════════════════════════════
    # SERVICIOS
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "servicios", "nombre": "Soporte técnico Nivel 1", "descripcion": "Atención primera línea: incidencias básicas, reseteo contraseñas, troubleshooting inicial, gestión tickets", "urgencia": "critica"},
    {"tipo": "servicios", "nombre": "Soporte técnico Nivel 2", "descripcion": "Resolución incidencias complejas, administración sistemas, escalado técnico especializado", "urgencia": "critica"},
    {"tipo": "servicios", "nombre": "Soporte técnico Nivel 3", "descripcion": "Ingeniería avanzada, resolución problemas críticos, diseño soluciones, escalado fabricante", "urgencia": "alta"},
    {"tipo": "servicios", "nombre": "Helpdesk 24x7", "descripcion": "Centro de atención multicanal (teléfono, email, chat, portal) con cobertura horaria completa", "urgencia": "critica"},
    {"tipo": "servicios", "nombre": "Smart Hands / Manos Remotas", "descripcion": "Ojos y manos en data centers: rack & stack, cableado, verificaciones físicas, reinicio equipos", "urgencia": "alta"},
    {"tipo": "servicios", "nombre": "Field Services / Soporte Onsite", "descripcion": "Técnicos desplazados a ubicación cliente para intervenciones presenciales", "urgencia": "alta"},
    {"tipo": "servicios", "nombre": "Mantenimiento preventivo", "descripcion": "Revisiones programadas, actualizaciones firmware, limpieza equipos, verificación estado", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "Mantenimiento correctivo", "descripcion": "Reparación y sustitución de equipos averiados, diagnóstico fallos hardware", "urgencia": "alta"},
    {"tipo": "servicios", "nombre": "Gestión de incidencias (ITIL)", "descripcion": "Proceso completo: registro, clasificación, priorización, resolución, cierre según ITIL", "urgencia": "alta"},
    {"tipo": "servicios", "nombre": "Gestión de cambios", "descripcion": "Control de cambios en infraestructura: CAB, aprobaciones, ventanas de mantenimiento", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "Gestión de problemas", "descripcion": "Análisis causa raíz, eliminación incidencias recurrentes, documentación soluciones", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "Administración remota de sistemas", "descripcion": "Gestión continua de servidores, aplicaciones y servicios vía conexión remota segura", "urgencia": "critica"},
    {"tipo": "servicios", "nombre": "Monitorización 24x7", "descripcion": "Vigilancia proactiva de infraestructura, alertas, dashboards, informes disponibilidad", "urgencia": "critica"},
    {"tipo": "servicios", "nombre": "Staff Augmentation", "descripcion": "Refuerzo equipos cliente con técnicos dedicados bajo su dirección", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "Consultoría tecnológica", "descripcion": "Asesoramiento estratégico, diseño arquitecturas, roadmaps tecnológicos", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "vCIO / CIO Virtual", "descripcion": "Dirección tecnológica externalizada: estrategia, presupuestos, governance IT", "urgencia": "baja"},
    {"tipo": "servicios", "nombre": "Auditoría IT", "descripcion": "Evaluación estado infraestructura, identificación riesgos, recomendaciones mejora", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "Formación técnica", "descripcion": "Capacitación usuarios y técnicos en herramientas, plataformas y procedimientos", "urgencia": "baja"},
    {"tipo": "servicios", "nombre": "Gestión de proveedores / Vendor Liaison", "descripcion": "Coordinación con fabricantes, gestión contratos, escalados, renovaciones", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "Procurement / Gestión de compras IT", "descripcion": "Adquisición hardware y software, comparativas, negociación, logística", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "Roll-out / Despliegue masivo", "descripcion": "Instalación equipos a escala: puestos de trabajo, dispositivos, configuración estándar", "urgencia": "alta"},
    {"tipo": "servicios", "nombre": "Tech Refresh / Renovación tecnológica", "descripcion": "Sustitución planificada de equipos obsoletos, migración datos, retirada RAEE", "urgencia": "media"},
    {"tipo": "servicios", "nombre": "IMAC (Install, Move, Add, Change)", "descripcion": "Servicios de instalación, movimiento, adición y cambio de equipos", "urgencia": "media"},

    # ═══════════════════════════════════════════════════════════════════════════
    # INFRAESTRUCTURA
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "infraestructura", "nombre": "Servidores físicos", "descripcion": "Suministro, instalación y mantenimiento servidores rack/torre (Dell, HPE, Lenovo)", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Virtualización VMware", "descripcion": "Diseño, implementación y gestión entornos vSphere, ESXi, vCenter, clusters HA/DRS", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Virtualización Hyper-V", "descripcion": "Implementación y administración Microsoft Hyper-V, failover clustering", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Virtualización Proxmox", "descripcion": "Entornos virtualizados open source, gestión VMs y contenedores", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Almacenamiento SAN/NAS", "descripcion": "Diseño e implementación storage enterprise, cabinas, expansiones, tiering", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Almacenamiento hiperconvergente (HCI)", "descripcion": "Soluciones vSAN, Nutanix, Azure Stack HCI", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Infraestructura Cloud AWS", "descripcion": "Diseño, migración y gestión workloads en Amazon Web Services", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Infraestructura Cloud Azure", "descripcion": "Implementación y administración Microsoft Azure, híbrido con on-premise", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Infraestructura Cloud GCP", "descripcion": "Servicios Google Cloud Platform, Compute Engine, Kubernetes", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Cloud híbrido / Multi-cloud", "descripcion": "Arquitecturas combinando on-premise con múltiples proveedores cloud", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Migración a cloud", "descripcion": "Planificación y ejecución migraciones on-premise a cloud, lift & shift, refactoring", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Cableado estructurado cobre", "descripcion": "Diseño, instalación y certificación cableado Cat6/Cat6A/Cat7, horizontal y vertical", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Cableado estructurado fibra óptica", "descripcion": "Tendido, fusión, terminación y certificación fibra óptica monomodo y multimodo", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Replanteo de red", "descripcion": "Estudio previo, diseño de recorridos, planificación de tiradas y puntos de red", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Certificación de cableado", "descripcion": "Medición y certificación de enlaces con equipos Fluke/equivalente, informes de cumplimiento", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Fusión de fibra óptica", "descripcion": "Empalme por fusión, instalación cajas de empalme, pigtails y latiguillos", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Canalizaciones y bandejas", "descripcion": "Instalación de bandejas portacables, canaletas, tubos y conductos para cableado", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Patch panels y distribuidores", "descripcion": "Instalación y terminación de paneles de parcheo cobre y fibra, organizadores", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Rosetas y tomas de red", "descripcion": "Instalación de rosetas RJ45, cajas de superficie/empotrar, tomas de usuario", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Cableado vertical / troncal", "descripcion": "Backbone entre plantas, conexión armarios distribuidores, fibra/cobre troncal", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Etiquetado y documentación de red", "descripcion": "Etiquetado normalizado de puntos, paneles y cables, planos as-built, documentación técnica", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "FTTH / FTTD", "descripcion": "Fibra hasta el hogar o hasta el puesto, despliegue última milla, ONTs", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Testing y medición de red", "descripcion": "Pruebas de continuidad, atenuación, OTDR, certificación de enlaces", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Armarios rack y distribuidores", "descripcion": "Suministro e instalación de armarios de comunicaciones, distribuidores de planta", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Obra civil para telecomunicaciones", "descripcion": "Canalizaciones enterradas, arquetas, pedestales, acometidas, paso de muros", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Racks y PDUs", "descripcion": "Suministro e instalación armarios rack, regletas inteligentes, gestión energía", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "SAI/UPS", "descripcion": "Sistemas alimentación ininterrumpida, dimensionamiento, instalación, mantenimiento", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Climatización CPD", "descripcion": "Sistemas refrigeración data centers, monitorización temperatura/humedad", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Data Center - Diseño y construcción", "descripcion": "Diseño salas técnicas, distribución, redundancia, certificación Tier", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Colocation", "descripcion": "Gestión espacios en data centers terceros, housing equipos cliente", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Puestos de trabajo / Endpoints", "descripcion": "Suministro, configuración y soporte PCs, portátiles, thin clients", "urgencia": "alta"},
    {"tipo": "infraestructura", "nombre": "Dispositivos móviles", "descripcion": "Gestión tablets, smartphones corporativos, MDM", "urgencia": "media"},
    {"tipo": "infraestructura", "nombre": "Impresoras y periféricos", "descripcion": "Gestión parque impresoras, multifuncionales, escáneres, plotters", "urgencia": "baja"},

    # ═══════════════════════════════════════════════════════════════════════════
    # COMUNICACIONES
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "comunicaciones", "nombre": "Redes LAN - Switches", "descripcion": "Diseño, instalación y gestión switches capa 2/3, VLANs, QoS", "urgencia": "critica"},
    {"tipo": "comunicaciones", "nombre": "Redes WiFi - Access Points", "descripcion": "Diseño cobertura, instalación APs, controladores wireless, site surveys", "urgencia": "alta"},
    {"tipo": "comunicaciones", "nombre": "Redes WAN - Routers", "descripcion": "Configuración y gestión routers, enrutamiento, BGP, OSPF", "urgencia": "critica"},
    {"tipo": "comunicaciones", "nombre": "Firewalls perimetrales", "descripcion": "Implementación y gestión firewalls (Fortinet, Palo Alto, Cisco, Sophos)", "urgencia": "critica"},
    {"tipo": "comunicaciones", "nombre": "VPN Site-to-Site", "descripcion": "Túneles seguros entre sedes, IPSec, configuración redundancia", "urgencia": "alta"},
    {"tipo": "comunicaciones", "nombre": "VPN Client / Acceso remoto", "descripcion": "Conexiones seguras usuarios remotos, SSL VPN, always-on VPN", "urgencia": "alta"},
    {"tipo": "comunicaciones", "nombre": "SD-WAN", "descripcion": "Redes definidas por software, optimización tráfico, failover automático", "urgencia": "media"},
    {"tipo": "comunicaciones", "nombre": "MPLS", "descripcion": "Gestión circuitos MPLS operador, QoS, SLAs", "urgencia": "media"},
    {"tipo": "comunicaciones", "nombre": "Internet dedicado", "descripcion": "Gestión líneas dedicadas, fibra, redundancia, balanceo", "urgencia": "alta"},
    {"tipo": "comunicaciones", "nombre": "Backup 4G/5G", "descripcion": "Líneas móviles de respaldo, routers LTE, failover automático", "urgencia": "media"},
    {"tipo": "comunicaciones", "nombre": "Radioenlaces", "descripcion": "Enlaces punto a punto microondas, conexión sedes sin fibra", "urgencia": "baja"},
    {"tipo": "comunicaciones", "nombre": "Telefonía IP / VoIP", "descripcion": "Centralitas virtuales, SIP trunks, gestión numeración", "urgencia": "media"},
    {"tipo": "comunicaciones", "nombre": "Comunicaciones unificadas", "descripcion": "Integración voz, video, chat, presencia en plataforma única", "urgencia": "media"},
    {"tipo": "comunicaciones", "nombre": "Microsoft Teams - Administración", "descripcion": "Gestión Teams: usuarios, políticas, telefonía, salas, integraciones", "urgencia": "alta"},
    {"tipo": "comunicaciones", "nombre": "Videoconferencia / Salas", "descripcion": "Equipamiento salas reuniones, integración Teams/Zoom, gestión reservas", "urgencia": "media"},

    # ═══════════════════════════════════════════════════════════════════════════
    # SOFTWARE
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "software", "nombre": "Windows Server", "descripcion": "Instalación, configuración y administración Windows Server 2016/2019/2022", "urgencia": "critica"},
    {"tipo": "software", "nombre": "Linux Server", "descripcion": "Administración servidores Linux (RHEL, Ubuntu, CentOS, Debian)", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Active Directory", "descripcion": "Diseño, implementación y gestión AD DS, GPOs, estructura OUs", "urgencia": "critica"},
    {"tipo": "software", "nombre": "Azure AD / Entra ID", "descripcion": "Identidad cloud, sincronización híbrida, conditional access", "urgencia": "alta"},
    {"tipo": "software", "nombre": "DNS", "descripcion": "Servicios resolución nombres, zonas internas/externas, split DNS", "urgencia": "critica"},
    {"tipo": "software", "nombre": "DHCP", "descripcion": "Asignación dinámica IPs, reservas, scopes, failover", "urgencia": "critica"},
    {"tipo": "software", "nombre": "Microsoft 365", "descripcion": "Administración tenant M365: Exchange Online, SharePoint, OneDrive, licencias", "urgencia": "critica"},
    {"tipo": "software", "nombre": "Google Workspace", "descripcion": "Gestión entorno Google: Gmail, Drive, Calendar, Admin Console", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Exchange Server On-Premise", "descripcion": "Administración Exchange local, migraciones, coexistencia híbrida", "urgencia": "media"},
    {"tipo": "software", "nombre": "Bases de datos SQL Server", "descripcion": "Administración SQL Server, backups, optimización, alta disponibilidad", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Bases de datos MySQL/PostgreSQL", "descripcion": "Gestión bases datos open source, replicación, tuning", "urgencia": "alta"},
    {"tipo": "software", "nombre": "ITSM - ServiceNow", "descripcion": "Plataforma gestión servicios IT, tickets, CMDB, workflows", "urgencia": "media"},
    {"tipo": "software", "nombre": "ITSM - Jira Service Management", "descripcion": "Gestión incidencias, peticiones, cambios, SLAs", "urgencia": "media"},
    {"tipo": "software", "nombre": "ITSM - Freshservice/Freshdesk", "descripcion": "Helpdesk cloud, gestión tickets, base conocimiento", "urgencia": "media"},
    {"tipo": "software", "nombre": "Monitorización - Zabbix", "descripcion": "Monitorización infraestructura open source, alertas, dashboards", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Monitorización - PRTG", "descripcion": "Monitorización red y sistemas, sensores, reporting", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Monitorización - Nagios", "descripcion": "Monitorización infraestructura, plugins, alertas", "urgencia": "media"},
    {"tipo": "software", "nombre": "Monitorización - Datadog/New Relic", "descripcion": "Observabilidad cloud, APM, logs, métricas", "urgencia": "media"},
    {"tipo": "software", "nombre": "RMM - Gestión remota endpoints", "descripcion": "Herramientas administración remota (ConnectWise, Datto, NinjaRMM)", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Backup - Veeam", "descripcion": "Backup y replicación VMs, recuperación granular, cloud connect", "urgencia": "critica"},
    {"tipo": "software", "nombre": "Backup - Commvault", "descripcion": "Backup enterprise, deduplicación, archivado", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Backup - Acronis", "descripcion": "Backup endpoints y servidores, disaster recovery", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Backup cloud (M365, Google)", "descripcion": "Backup datos SaaS: correo, SharePoint, Drive, Teams", "urgencia": "alta"},
    {"tipo": "software", "nombre": "DRaaS - Disaster Recovery as a Service", "descripcion": "Replicación offsite, failover automatizado, RTO/RPO definidos", "urgencia": "alta"},
    {"tipo": "software", "nombre": "Automatización - Ansible", "descripcion": "Automatización configuración servidores, playbooks, IaC", "urgencia": "media"},
    {"tipo": "software", "nombre": "Automatización - Terraform", "descripcion": "Infrastructure as Code, provisioning cloud, versionado", "urgencia": "media"},
    {"tipo": "software", "nombre": "Automatización - Power Automate", "descripcion": "Flujos automatizados Microsoft, integración M365, conectores", "urgencia": "media"},
    {"tipo": "software", "nombre": "Contenedores - Docker", "descripcion": "Containerización aplicaciones, imágenes, registries", "urgencia": "media"},
    {"tipo": "software", "nombre": "Orquestación - Kubernetes", "descripcion": "Gestión clusters K8s, deployments, scaling, helm charts", "urgencia": "media"},
    {"tipo": "software", "nombre": "CI/CD - Pipelines", "descripcion": "Integración y despliegue continuo (Azure DevOps, GitHub Actions, GitLab)", "urgencia": "media"},

    # ═══════════════════════════════════════════════════════════════════════════
    # SEGURIDAD
    # ═══════════════════════════════════════════════════════════════════════════
    {"tipo": "seguridad", "nombre": "Firewall Next-Gen (NGFW)", "descripcion": "Firewalls con inspección profunda, IPS integrado, application control", "urgencia": "critica"},
    {"tipo": "seguridad", "nombre": "IDS/IPS", "descripcion": "Sistemas detección y prevención intrusiones, análisis tráfico", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "WAF - Web Application Firewall", "descripcion": "Protección aplicaciones web, OWASP, reglas personalizadas", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Antivirus / Antimalware", "descripcion": "Protección endpoints, consola centralizada, actualizaciones", "urgencia": "critica"},
    {"tipo": "seguridad", "nombre": "EDR - Endpoint Detection & Response", "descripcion": "Detección avanzada amenazas endpoints, respuesta automatizada (CrowdStrike, SentinelOne, Defender)", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "XDR - Extended Detection & Response", "descripcion": "Correlación eventos múltiples fuentes, respuesta unificada", "urgencia": "media"},
    {"tipo": "seguridad", "nombre": "SIEM", "descripcion": "Correlación eventos seguridad, análisis logs, alertas (Splunk, Sentinel, QRadar)", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "SOC - Centro Operaciones Seguridad", "descripcion": "Monitorización 24x7 seguridad, análisis alertas, respuesta incidentes", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Gestión vulnerabilidades", "descripcion": "Escaneo periódico, priorización CVEs, seguimiento remediación (Qualys, Nessus)", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Pentesting / Test intrusión", "descripcion": "Pruebas penetración infraestructura y aplicaciones, informes", "urgencia": "media"},
    {"tipo": "seguridad", "nombre": "Hardening sistemas", "descripcion": "Bastionado servidores y endpoints según CIS benchmarks", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Cifrado datos en reposo", "descripcion": "Encriptación discos, bases datos, almacenamiento (BitLocker, LUKS)", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Cifrado datos en tránsito", "descripcion": "TLS/SSL, certificados, gestión PKI", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "DLP - Data Loss Prevention", "descripcion": "Prevención fuga datos, políticas clasificación, monitorización", "urgencia": "media"},
    {"tipo": "seguridad", "nombre": "IAM - Identity & Access Management", "descripcion": "Gestión identidades, provisioning, lifecycle usuarios", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "PAM - Privileged Access Management", "descripcion": "Gestión accesos privilegiados, bóveda contraseñas, grabación sesiones (CyberArk, BeyondTrust)", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "MFA - Autenticación multifactor", "descripcion": "Segundo factor autenticación, tokens, apps authenticator", "urgencia": "critica"},
    {"tipo": "seguridad", "nombre": "SSO - Single Sign-On", "descripcion": "Autenticación única, federación identidades, SAML/OAuth", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Zero Trust Network Access", "descripcion": "Acceso basado en identidad, microsegmentación, verificación continua", "urgencia": "media"},
    {"tipo": "seguridad", "nombre": "Email Security", "descripcion": "Protección correo: antispam, antiphishing, sandboxing adjuntos", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Concienciación seguridad / Awareness", "descripcion": "Formación usuarios, simulaciones phishing, campañas", "urgencia": "media"},
    {"tipo": "seguridad", "nombre": "Backup inmutable / Air-gapped", "descripcion": "Copias seguridad protegidas contra ransomware, WORM", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Plan continuidad negocio (BCP)", "descripcion": "Documentación, procedimientos, pruebas recuperación", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Plan recuperación desastres (DRP)", "descripcion": "Procedimientos recuperación IT, RTO/RPO, pruebas periódicas", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Cumplimiento ENS", "descripcion": "Adecuación Esquema Nacional Seguridad niveles Bajo/Medio/Alto", "urgencia": "critica"},
    {"tipo": "seguridad", "nombre": "Cumplimiento ISO 27001", "descripcion": "Sistema gestión seguridad información, auditorías, certificación", "urgencia": "alta"},
    {"tipo": "seguridad", "nombre": "Cumplimiento GDPR/LOPD", "descripcion": "Protección datos personales, DPO, registros tratamiento", "urgencia": "alta"},
]


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
                resultado.append(f"  • {s['nombre']}: {s['descripcion'][:80]}...")

    return "\n".join(resultado)


def generar_keywords_deteccion() -> dict:
    """
    Genera un diccionario de keywords para detección rápida de componentes.
    Mapea palabras clave a servicios SRS.
    """
    keywords = {}

    # Keywords por servicio
    mappings = {
        # Servicios
        "soporte": ["Soporte técnico Nivel 1", "Soporte técnico Nivel 2"],
        "helpdesk": ["Helpdesk 24x7", "Soporte técnico Nivel 1"],
        "24x7": ["Helpdesk 24x7", "Monitorización 24x7", "SOC - Centro Operaciones Seguridad"],
        "incidencias": ["Gestión de incidencias (ITIL)", "Soporte técnico Nivel 1"],
        "mantenimiento": ["Mantenimiento preventivo", "Mantenimiento correctivo"],
        "smart hands": ["Smart Hands / Manos Remotas"],
        "manos remotas": ["Smart Hands / Manos Remotas"],
        "onsite": ["Field Services / Soporte Onsite"],
        "presencial": ["Field Services / Soporte Onsite"],
        "itil": ["Gestión de incidencias (ITIL)", "Gestión de cambios", "Gestión de problemas"],
        "monitorización": ["Monitorización 24x7"],
        "roll-out": ["Roll-out / Despliegue masivo"],
        "despliegue": ["Roll-out / Despliegue masivo"],
        "imac": ["IMAC (Install, Move, Add, Change)"],

        # Infraestructura
        "servidor": ["Servidores físicos", "Windows Server", "Linux Server"],
        "vmware": ["Virtualización VMware"],
        "hyper-v": ["Virtualización Hyper-V"],
        "virtualización": ["Virtualización VMware", "Virtualización Hyper-V"],
        "san": ["Almacenamiento SAN/NAS"],
        "nas": ["Almacenamiento SAN/NAS"],
        "aws": ["Infraestructura Cloud AWS"],
        "azure": ["Infraestructura Cloud Azure"],
        "cloud": ["Infraestructura Cloud AWS", "Infraestructura Cloud Azure", "Migración a cloud"],
        "cableado": ["Cableado estructurado cobre", "Cableado estructurado fibra óptica"],
        "fibra": ["Cableado estructurado fibra óptica", "Fusión de fibra óptica"],
        "cat6": ["Cableado estructurado cobre"],
        "rack": ["Armarios rack y distribuidores", "Racks y PDUs"],
        "sai": ["SAI/UPS"],
        "ups": ["SAI/UPS"],
        "cpd": ["Data Center - Diseño y construcción", "Climatización CPD"],
        "data center": ["Data Center - Diseño y construcción"],
        "puesto de trabajo": ["Puestos de trabajo / Endpoints"],
        "endpoint": ["Puestos de trabajo / Endpoints"],

        # Comunicaciones
        "switch": ["Redes LAN - Switches"],
        "lan": ["Redes LAN - Switches"],
        "wifi": ["Redes WiFi - Access Points"],
        "wireless": ["Redes WiFi - Access Points"],
        "router": ["Redes WAN - Routers"],
        "wan": ["Redes WAN - Routers"],
        "firewall": ["Firewalls perimetrales", "Firewall Next-Gen (NGFW)"],
        "vpn": ["VPN Site-to-Site", "VPN Client / Acceso remoto"],
        "sd-wan": ["SD-WAN"],
        "voip": ["Telefonía IP / VoIP"],
        "telefonía": ["Telefonía IP / VoIP"],
        "teams": ["Microsoft Teams - Administración"],

        # Software
        "windows server": ["Windows Server"],
        "linux": ["Linux Server"],
        "active directory": ["Active Directory"],
        "directorio activo": ["Active Directory"],
        "microsoft 365": ["Microsoft 365"],
        "m365": ["Microsoft 365"],
        "office 365": ["Microsoft 365"],
        "exchange": ["Microsoft 365", "Exchange Server On-Premise"],
        "sharepoint": ["Microsoft 365"],
        "sql server": ["Bases de datos SQL Server"],
        "base de datos": ["Bases de datos SQL Server", "Bases de datos MySQL/PostgreSQL"],
        "backup": ["Backup - Veeam", "Backup - Acronis", "Backup cloud (M365, Google)"],
        "veeam": ["Backup - Veeam"],
        "zabbix": ["Monitorización - Zabbix"],
        "prtg": ["Monitorización - PRTG"],

        # Seguridad
        "antivirus": ["Antivirus / Antimalware"],
        "edr": ["EDR - Endpoint Detection & Response"],
        "siem": ["SIEM"],
        "soc": ["SOC - Centro Operaciones Seguridad"],
        "vulnerabilidades": ["Gestión vulnerabilidades"],
        "pentesting": ["Pentesting / Test intrusión"],
        "hardening": ["Hardening sistemas"],
        "cifrado": ["Cifrado datos en reposo", "Cifrado datos en tránsito"],
        "mfa": ["MFA - Autenticación multifactor"],
        "doble factor": ["MFA - Autenticación multifactor"],
        "sso": ["SSO - Single Sign-On"],
        "ens": ["Cumplimiento ENS"],
        "esquema nacional": ["Cumplimiento ENS"],
        "iso 27001": ["Cumplimiento ISO 27001"],
        "lopd": ["Cumplimiento GDPR/LOPD"],
        "rgpd": ["Cumplimiento GDPR/LOPD"],
        "gdpr": ["Cumplimiento GDPR/LOPD"],
        "drp": ["Plan recuperación desastres (DRP)"],
        "bcp": ["Plan continuidad negocio (BCP)"],
        "continuidad": ["Plan continuidad negocio (BCP)"],
        "disaster recovery": ["Plan recuperación desastres (DRP)", "DRaaS - Disaster Recovery as a Service"],
    }

    return mappings


# Lista resumida para el prompt (más compacta)
SERVICIOS_RESUMEN_PROMPT = """
CATÁLOGO DE SERVICIOS SRS (detecta estos en el pliego):

SERVICIOS GESTIONADOS:
- Soporte técnico N1/N2/N3 (helpdesk, incidencias, troubleshooting)
- Helpdesk 24x7 (multicanal, cobertura completa)
- Smart Hands / Manos remotas (data centers)
- Field Services / Soporte onsite (presencial)
- Mantenimiento preventivo y correctivo
- Gestión ITIL (incidencias, cambios, problemas)
- Monitorización 24x7 (proactiva, alertas)
- Administración remota de sistemas
- Staff Augmentation (refuerzo equipos)
- Roll-out / Despliegue masivo
- IMAC (Install, Move, Add, Change)

INFRAESTRUCTURA:
- Servidores físicos (Dell, HPE, Lenovo)
- Virtualización (VMware, Hyper-V, Proxmox)
- Almacenamiento SAN/NAS/HCI
- Cloud (AWS, Azure, GCP, híbrido)
- Cableado estructurado (cobre Cat6/7, fibra óptica)
- Fusión fibra, certificación, patch panels
- CPD (diseño, climatización, SAI/UPS)
- Racks, PDUs, canalizaciones
- Puestos de trabajo / Endpoints

COMUNICACIONES:
- Redes LAN (switches, VLANs)
- Redes WiFi (APs, controladores)
- Redes WAN (routers, MPLS, SD-WAN)
- Firewalls perimetrales
- VPN (site-to-site, acceso remoto)
- Telefonía IP / VoIP
- Comunicaciones unificadas / Teams

SOFTWARE:
- Windows Server / Linux
- Active Directory / Azure AD
- Microsoft 365 / Google Workspace
- Bases de datos (SQL Server, MySQL, PostgreSQL)
- Backup (Veeam, Acronis, cloud)
- Monitorización (Zabbix, PRTG, Nagios)
- ITSM (ServiceNow, Jira, Freshservice)
- Automatización (Ansible, Terraform)
- Contenedores (Docker, Kubernetes)

SEGURIDAD:
- Firewall NGFW, IDS/IPS, WAF
- Antivirus / EDR / XDR
- SIEM, SOC 24x7
- Gestión vulnerabilidades, pentesting
- Cifrado (reposo, tránsito)
- IAM, PAM, MFA, SSO
- Cumplimiento (ENS, ISO 27001, GDPR)
- BCP/DRP, backup inmutable

ZONAS DE COBERTURA SRS (evalúa ubicación):
- ZONA BASE (respuesta mismo día, sin coste desplazamiento):
  Madrid, Sevilla, Málaga, Cádiz, Granada, Córdoba, Huelva, Jaén, Almería
- ZONA CERCANA (respuesta 24-48h, coste reducido):
  Toledo, Ciudad Real, Guadalajara, Cuenca, Albacete, Badajoz, Cáceres, Ávila, Segovia, Murcia
- ZONA EXPANSIÓN (respuesta 48-72h, coste estándar):
  Resto de España (Cataluña, Valencia, País Vasco, Galicia, etc.)
"""
