# SpotterSRS - Motor de Deteccion

## Vision General

SpotterSRS es el motor que detecta oportunidades de negocio escaneando licitaciones publicas adjudicadas en PLACSP (Plataforma de Contratacion del Sector Publico).

**Objetivo**: Identificar empresas que han ganado contratos publicos y pueden necesitar subcontratacion de servicios IT.

## Flujo Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                     CRON JOB (8:00 AM)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. SCRAPING PLACSP                                             │
│                                                                 │
│  - Descarga feed XML de adjudicaciones                         │
│  - Filtra por CPVs relevantes                                  │
│  - Extrae datos basicos (titulo, importe, empresa, cliente)    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. CLASIFICACION                                               │
│                                                                 │
│  - Analiza objeto del contrato con keywords                    │
│  - Asigna TipoOportunidad (Infra, Cloud, Ciber, etc.)         │
│  - Calcula score inicial (0-100)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. PERSISTENCIA                                                │
│                                                                 │
│  - Guarda en MongoDB (oportunidades_placsp)                    │
│  - Actualiza si ya existe (por oportunidad_id)                 │
│  - Estado inicial: sin_revisar                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. NOTIFICACION                                                │
│                                                                 │
│  - Frontend detecta nuevas oportunidades                       │
│  - Tabla se actualiza automaticamente                          │
└─────────────────────────────────────────────────────────────────┘
```

## Archivos Clave

| Archivo | Proposito |
|---------|-----------|
| `spotter_srs.py` | Scraper y clasificador principal |
| `run_spotter_cron.py` | Script para cron job |
| `reclasificar_oportunidades.py` | Reclasifica oportunidades existentes |

## Clasificacion por Tipo

### TipoOportunidad (Enum)

```python
class TipoOportunidad(Enum):
    # Pilares principales SRS
    INFRAESTRUCTURA_CPD = "Infraestructura / CPD"
    CLOUD_VIRTUALIZACION = "Cloud / Virtualizacion"
    CIBERSEGURIDAD = "Ciberseguridad"
    COMUNICACIONES_UC = "Comunicaciones Unificadas"
    HEALTHCARE_IT = "Healthcare IT (RIS/PACS)"
    FOTOVOLTAICA_ENERGIA = "Fotovoltaica / Energia"
    DRONES_CARTOGRAFIA = "Drones / Cartografia"

    # Diferencial
    SOPORTE_INTERNACIONAL = "Soporte Internacional"

    # Genericos
    IT_GENERICO = "IT Generico"
    NO_RELEVANTE = "No Relevante"
```

### Keywords por Tipo

**Infraestructura / CPD:**
```python
kw_infra = ["cpd", "centro de proceso", "data center", "datacenter",
            "cableado estructurado", "rack", "racks", "ups",
            "climatizacion", "sala tecnica", "instalacion electrica"]
```

**Cloud / Virtualizacion:**
```python
kw_cloud = ["cloud", "nube", "virtualizacion", "vmware", "hyper-v",
            "kubernetes", "contenedores", "docker", "azure", "aws",
            "iaas", "paas", "saas", "backup", "recuperacion"]
```

**Ciberseguridad:**
```python
kw_ciber = ["ciberseguridad", "seguridad informatica", "soc",
            "firewall", "antivirus", "edr", "siem", "pentesting",
            "auditoria seguridad", "ens", "iso 27001"]
```

**Comunicaciones Unificadas:**
```python
kw_uc = ["comunicaciones unificadas", "telefonia ip", "voip",
         "videoconferencia", "teams", "centralita", "pbx",
         "contact center", "call center"]
```

**Healthcare IT:**
```python
kw_health = ["ris", "pacs", "historia clinica", "hce", "his",
             "sanidad", "hospital", "imagenes medicas", "dicom",
             "radiologia", "telemedicina"]
```

**Fotovoltaica / Energia:**
```python
kw_fotovoltaica = ["fotovoltaica", "solar", "autoconsumo",
                   "paneles solares", "inversores", "energia renovable"]
```

**Drones / Cartografia:**
```python
kw_drones_captura = ["vuelo", "dron", "drones", "rpas", "uav",
                     "fotogrametria", "ortofoto", "topografia aerea"]
kw_lidar_contexto = ["lidar", "nube de puntos", "mdt", "mds"]
kw_contexto_cartografia = ["cartografia", "gemelo digital", "as-built",
                           "volumetria", "cubicacion"]
```

### Jerarquia de Clasificacion

```python
# Orden de prioridad (primera coincidencia gana)
1. Fotovoltaica (CPV 09* o keywords)
2. Drones/Cartografia (keywords captura o lidar+contexto)
3. Healthcare IT (keywords sanidad)
4. Ciberseguridad (keywords seguridad)
5. Comunicaciones UC (keywords telefonia)
6. Soporte Internacional (keywords multisede + internacional)
7. Infraestructura/CPD (keywords cpd, cableado)
8. Cloud/Virtualizacion (keywords cloud)
9. IT Generico (tiene CPV IT pero sin keywords especificos)
10. No Relevante (sin coincidencias)
```

## CPVs Relevantes

| CPV | Descripcion | Puntos |
|-----|-------------|--------|
| 72* | Servicios informaticos | 25 |
| 48* | Paquetes de software | 20 |
| 32* | Equipos de telecomunicaciones | 20 |
| 30* | Maquinas de oficina | 18 |
| 50* | Servicios de reparacion/mantenimiento | 15 |
| 09* | Productos energeticos (fotovoltaica) | 20 |
| 77* | Servicios agricolas (drones) | 10 |

## Calculo de Score

El score (0-100) se calcula con:

```python
def calcular_dolor(objeto, fecha_adjudicacion, duracion_dias, cpv, keywords):
    score = 0
    indicadores = []

    # Base por CPV
    if cpv.startswith("72"):
        score += 25
    elif cpv.startswith("48"):
        score += 20
    # ... etc

    # Bonus por keywords de urgencia
    if any(kw in objeto_lower for kw in ["urgente", "critico", "inmediato"]):
        score += 15
        indicadores.append("Urgencia detectada")

    # Bonus por 24x7
    if "24x7" in objeto_lower or "24/7" in objeto_lower:
        score += 10
        indicadores.append("Soporte 24x7")

    # Bonus por certificaciones
    if "ens" in objeto_lower or "iso 27001" in objeto_lower:
        score += 12
        indicadores.append("Requiere certificaciones")

    # Bonus por multisede
    if "multisede" in objeto_lower or "nacional" in objeto_lower:
        score += 10
        indicadores.append("Cobertura nacional")

    # Normalizar a 0-100
    score = min(100, score)

    return DolorResult(
        tipo_oportunidad=tipo,
        score_dolor=score,
        indicadores_urgencia=indicadores
    )
```

## Ejecucion

### Cron Job (Produccion)

```bash
# En crontab del servidor
0 8 * * * cd /var/www/srs-crm/backend && source venv/bin/activate && python app/spotter/run_spotter_cron.py >> /var/log/spotter.log 2>&1
```

### Manual

```bash
cd backend/app/spotter
python run_spotter_cron.py
```

### Via API

```bash
curl -X POST https://crm.systemrapidsolutions.com:3001/api/oportunidades/spotter \
  -H "Authorization: Bearer $TOKEN"
```

## Reclasificacion

Cuando se actualizan las keywords o reglas de clasificacion, ejecutar:

```bash
# Ver cambios sin aplicar
python reclasificar_oportunidades.py --dry-run

# Aplicar cambios
python reclasificar_oportunidades.py
```

Output ejemplo:
```
╔════════════════════════════════════════════════════════════════════╗
║          RECLASIFICACION DE OPORTUNIDADES PLACSP                   ║
╚════════════════════════════════════════════════════════════════════╝

Modo: DRY RUN (sin cambios)

📊 Encontradas 500 oportunidades para analizar

═══════════════════════════════════════════════════════════════
📋 RESUMEN DE RECLASIFICACION
═══════════════════════════════════════════════════════════════
   Total oportunidades: 500
   ✅ Sin cambios: 480
   🔄 Con cambios: 20
   ❌ Errores: 0

📊 CAMBIOS POR TIPO
   Drones / Cartografia: 8
   Infraestructura / CPD: 7
   IT Generico: 5
```

## Deteccion Inteligente de LiDAR

LiDAR puede aparecer en dos contextos:

1. **Captura/Cartografia** (SRS Drones): vuelos, topografia, obras
2. **Procesamiento de datos** (IT generico): plataformas, data lakes

Logica de deteccion:

```python
# Keywords de exclusion (contexto solo datos)
kw_solo_datos = ["espacio de datos", "data space", "lago de datos",
                 "data lake", "plataforma de datos", "interoperabilidad"]

# Clasificar como Drones/Cartografia si:
es_drones_cartografia = (
    tiene_drones_captura or      # Keywords claros de vuelo
    tiene_contexto_cartografia or # Keywords de obra/gemelo digital
    (tiene_lidar and not tiene_solo_datos)  # LiDAR sin contexto datos
)
```

## Troubleshooting

### No detecta oportunidades nuevas

1. Verificar que PLACSP feed esta accesible:
```bash
curl -I https://contrataciondelestado.es/...
```

2. Revisar logs:
```bash
pm2 logs srs-crm-backend | grep -i spotter
```

3. Verificar CPVs en la oportunidad

### Clasificacion incorrecta

1. Revisar keywords detectados en el objeto
2. Verificar CPV de la licitacion
3. Ejecutar reclasificacion si se actualizaron reglas

### Score muy bajo/alto

1. Revisar indicadores_dolor del registro
2. Ajustar pesos en `calcular_dolor()`
3. Verificar que keywords se detectan correctamente

## Metricas

| Metrica | Valor tipico |
|---------|--------------|
| Oportunidades/dia | 100-300 |
| % Relevantes (no "No Relevante") | 40-60% |
| Tiempo ejecucion cron | 30-60 segundos |
| Oportunidades tipo A+B | 15-25% |
