# Arquitectura SRS-CRM

## Vision General

SRS-CRM es un sistema modular que combina gestion comercial tradicional (CRM) con deteccion automatica de oportunidades de negocio mediante scraping de licitaciones publicas y analisis con IA.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React 19)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Dashboard │ │  Leads   │ │ Pipeline │ │Oportuni- │ │  Admin   │          │
│  │  (KPIs)  │ │  (CRUD)  │ │ (Kanban) │ │  dades   │ │ (Users)  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    shadcn/ui Components (50+)                          │ │
│  │  Button, Card, Dialog, DropdownMenu, Table, Tabs, Toast, etc.         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTPS (REST API)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI + Python 3.11)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         server.py (API REST)                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │  /auth   │ │  /leads  │ │/oportuni-│ │ /apollo  │ │ /reports │  │   │
│  │  │  (3)    │ │  (13)    │ │  dades   │ │  (4)     │ │  (2)     │  │   │
│  │  │         │ │          │ │  (10+)   │ │          │ │          │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      app/spotter/ (Motor Analisis)                   │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │   │
│  │  │  spotter_srs   │  │ pliego_analyzer│  │ pain_analyzer  │         │   │
│  │  │  (Scraper)     │  │ (PDF + IA)     │  │ (Quick Score)  │         │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │   │
│  │  │ adjudicatario_ │  │analisis_       │  │ catalogo_srs   │         │   │
│  │  │ enricher       │  │comercial       │  │ (Servicios)    │         │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────┬──────────────────────┬────────────────────┘
           │                      │                      │
           ▼                      ▼                      ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   MongoDB Atlas  │   │    Apollo.io     │   │   IA Providers   │
│   (Persistencia) │   │   (B2B Data)     │   │                  │
│                  │   │                  │   │  ┌────────────┐  │
│  ┌────────────┐  │   │  - Personas      │   │  │  Claude    │  │
│  │   users    │  │   │  - Empresas      │   │  │  (Primary) │  │
│  ├────────────┤  │   │  - Tecnograficos │   │  └────────────┘  │
│  │   leads    │  │   │                  │   │  ┌────────────┐  │
│  ├────────────┤  │   │                  │   │  │  Gemini    │  │
│  │ activities │  │   │                  │   │  │ (Fallback) │  │
│  ├────────────┤  │   │                  │   │  └────────────┘  │
│  │oportunida- │  │   │                  │   │  ┌────────────┐  │
│  │des_placsp  │  │   │                  │   │  │  OpenAI    │  │
│  └────────────┘  │   │                  │   │  │ (Fallback) │  │
└──────────────────┘   └──────────────────┘   │  └────────────┘  │
                                              └──────────────────┘
           ▲
           │ Feed XML (Cron 8:00 AM)
           │
┌──────────────────┐
│     PLACSP       │
│  (Licitaciones   │
│   Publicas)      │
└──────────────────┘
```

## Flujos de Datos

### 1. Flujo SpotterSRS (Deteccion Automatica)

```
[PLACSP Feed XML] ──► [SpotterSRS Scraper] ──► [Clasificador CPV]
                                                      │
                                                      ▼
                                              [MongoDB: oportunidades_placsp]
                                                      │
                                                      ▼
                                              [Frontend: Tabla Oportunidades]
                                                      │
                                           ┌──────────┼──────────┐
                                           ▼          ▼          ▼
                                    [Analisis   [Analisis   [Analisis
                                     Rapido]    Completo]    Pain]
```

### 2. Flujo Analisis Completo

```
[Usuario: Click "Analizar"]
        │
        ▼
[Backend: /analisis-comercial]
        │
        ├──► [1. adjudicatario_enricher]
        │         │
        │         └──► Scrape HTML PLACSP
        │              - Datos empresa
        │              - Email, telefono
        │              - Importe adjudicacion
        │
        ├──► [2. pliego_analyzer]
        │         │
        │         └──► Descarga PDF
        │              - Extrae texto (pdfplumber)
        │              - Chunks de 20KB
        │
        └──► [3. analisis_comercial]
                  │
                  └──► Claude AI (Opus 4.5)
                       - Prompt estructurado
                       - Output JSON (18 secciones)
                       │
                       ▼
               [ResumenOperador]
               - Score 0-100
               - Dolores detectados
               - Gancho comercial
               - Objeciones + respuestas
```

### 3. Flujo CRM (Lead Lifecycle)

```
[Fuentes de Leads]
    │
    ├── Importacion Excel
    ├── Creacion manual
    ├── Conversion desde Oportunidad PLACSP
    └── Enriquecimiento Apollo
            │
            ▼
┌───────────────────────────────────────────────────────┐
│                    PIPELINE KANBAN                     │
│                                                        │
│  Nuevo → Contactado → Calificado → Propuesta →        │
│                        Negociacion → Ganado/Perdido   │
│                                                        │
└───────────────────────────────────────────────────────┘
            │
            ▼
    [Actividades: llamadas, emails, reuniones]
            │
            ▼
    [Dashboard: KPIs y metricas]
```

## Componentes del Motor de Analisis

### spotter_srs.py
**Responsabilidad**: Scraping y clasificacion de licitaciones PLACSP

```python
# Tipos de oportunidad detectados
class TipoOportunidad(Enum):
    INFRAESTRUCTURA_CPD = "Infraestructura / CPD"
    CLOUD_VIRTUALIZACION = "Cloud / Virtualizacion"
    CIBERSEGURIDAD = "Ciberseguridad"
    COMUNICACIONES_UC = "Comunicaciones Unificadas"
    HEALTHCARE_IT = "Healthcare IT (RIS/PACS)"
    FOTOVOLTAICA_ENERGIA = "Fotovoltaica / Energia"
    DRONES_CARTOGRAFIA = "Drones / Cartografia"
    SOPORTE_INTERNACIONAL = "Soporte Internacional"
    IT_GENERICO = "IT Generico"
    NO_RELEVANTE = "No Relevante"
```

**Clasificacion por CPV**:
- `72*`: Servicios IT (25 puntos)
- `48*`: Software (20 puntos)
- `32*`: Telecomunicaciones (20 puntos)
- `50*`: Mantenimiento (15 puntos)
- `09*`: Energia (fotovoltaica)

### adjudicatario_enricher.py
**Responsabilidad**: Extraccion de datos del HTML de adjudicacion

```python
# Datos extraidos
{
    "nombre": "NTT DATA SPAIN, S.L.U.",
    "nif": "B82387770",
    "es_pyme": False,
    "pais_origen": "Espana",
    "direccion": {
        "calle": "...",
        "cp": "28050",
        "localidad": "Madrid"
    },
    "contacto": {
        "telefono": "...",
        "email": "spain.proposals.office@nttdata.com"
    },
    "importes": {
        "sin_impuestos": 1500000.00,
        "con_impuestos": 1815000.00
    }
}
```

### pliego_analyzer.py
**Responsabilidad**: Analisis de PDFs con IA

```python
# Proceso de analisis
1. Descarga PDF desde URL PLACSP
2. Extrae texto con pdfplumber
3. Divide en chunks (max 20KB)
4. Envia a Claude con prompt estructurado
5. Extrae:
   - Certificaciones requeridas (ISO 27001, ENS, etc.)
   - SLAs y penalizaciones
   - Personal minimo
   - Equipamiento especifico
   - Zonas geograficas
```

### catalogo_srs.py
**Responsabilidad**: Definicion de servicios SRS para matching

```python
CATALOGO_SRS = {
    "field_services": {
        "cableado_estructurado": {
            "nombre": "Cableado estructurado",
            "descripcion": "Instalacion de redes cableadas",
            "certificaciones": ["ISO 27001"],
            "zonas": ["Madrid", "Andalucia", "Levante"]
        },
        "soporte_onsite": {...},
        "instalacion_equipos": {...}
    },
    "cloud_virtualizacion": {...},
    "ciberseguridad": {...},
    "comunicaciones": {...},
    "healthcare": {...},
    "drones": {...}
}

ZONAS_COBERTURA = {
    "base": ["Madrid", "Andalucia (9 provincias)"],
    "cercana": ["Toledo", "Ciudad Real", "Murcia"],
    "expansion": ["resto Espana"]
}
```

## Modelos de Datos

### Lead (CRM)
```javascript
{
  _id: ObjectId,
  empresa: String,
  contacto: String,
  email: String,
  telefono: String,
  cargo: String,
  sector: Enum,
  valor_estimado: Float,
  etapa: Enum["nuevo", "contactado", "calificado",
              "propuesta", "negociacion", "ganado", "perdido"],
  servicios: [String],
  fuente: Enum,
  urgencia: Enum,
  propietario: ObjectId,
  proximo_seguimiento: DateTime,
  notas: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### OportunidadPLACSP
```javascript
{
  _id: ObjectId,
  oportunidad_id: String (PLACSP expediente),
  titulo: String,
  objeto: String,
  fecha_publicacion: DateTime,
  fecha_adjudicacion: DateTime,
  url_licitacion: String,
  url_pliego_tecnico: String,

  // Cliente
  cliente_nombre: String,
  cliente_sector: String,

  // Adjudicatario
  adjudicatario_nombre: String,
  adjudicatario_nif: String,
  importe_adjudicacion: Float,

  // Clasificacion
  cpv: String,
  tipo_srs: Enum[TipoOportunidad],
  keywords: [String],
  score: Int (0-100),

  // Analisis
  datos_adjudicatario: Object,
  analisis_rapido: Object,
  analisis_comercial: Object,

  // Estado comercial
  estado_revision: Enum["sin_revisar", "en_revision",
                        "descartada", "contactado"],
  asignado_a: ObjectId,
  asignado_nombre: String,

  created_at: DateTime,
  updated_at: DateTime
}
```

## Seguridad

### Autenticacion
- Google OAuth 2.0 para login
- JWT para sesiones (24h expiry)
- Whitelist de usuarios autorizados

### CORS
```python
CORS_ORIGINS = [
    "https://crm.systemrapidsolutions.com:3001",
    "http://localhost:3000"  # Solo desarrollo
]
```

### Variables Sensibles
Todas las credenciales en `.env` (no versionado):
- MongoDB connection string
- API keys (Apollo, Claude, Gemini, OpenAI)
- Google OAuth credentials
- JWT secret

## Escalabilidad

### Actual (MVP)
- 1 VPS Hostinger
- MongoDB Atlas M0 (shared)
- ~500 oportunidades/mes
- ~100 leads activos

### Futuro
- Horizontal scaling con containers
- MongoDB Atlas dedicated
- Redis para cache
- Queue system (Celery) para analisis async

## Integraciones Externas

| Servicio | Uso | Rate Limits |
|----------|-----|-------------|
| PLACSP | Feed XML licitaciones | Sin limite |
| Apollo.io | Enriquecimiento B2B | 200 req/dia |
| Claude (Anthropic) | Analisis principal | Pay-per-use |
| Gemini (Google) | Fallback IA | 60 req/min |
| OpenAI | Fallback IA | Pay-per-use |
| Google OAuth | Autenticacion | Sin limite |

## Monitoreo

### PM2
```bash
pm2 status              # Estado procesos
pm2 logs srs-crm-backend  # Logs en tiempo real
pm2 monit               # Monitor recursos
```

### Health Check
```bash
curl https://crm.systemrapidsolutions.com:3001/api/health
# {"status": "ok", "timestamp": "..."}
```

### Metricas Clave
- Oportunidades detectadas/dia
- Tiempo de respuesta API
- Tasa de conversion oportunidad->lead
- Uso de tokens IA
