# SRS-CRM

Sistema de Gestion Comercial y Deteccion de Oportunidades para **System Rapid Solutions**.

## Descripcion

SRS-CRM combina un CRM tradicional con un detector inteligente de oportunidades (**SpotterSRS**) que monitoriza diariamente PLACSP (Portal de Licitaciones del Sector Publico) para identificar empresas adjudicatarias con potencial necesidad de servicios IT.

### Modulos Principales

| Modulo | Descripcion |
|--------|-------------|
| **CRM Core** | Gestion de leads, pipeline Kanban, actividades comerciales |
| **SpotterSRS** | Detector automatico de oportunidades de subcontratacion en PLACSP |
| **Apollo Enricher** | Enriquecimiento de datos B2B via Apollo.io |
| **Pain Analyzer** | Analisis de dolor con IA multi-proveedor (Claude/Gemini/OpenAI) |
| **Pliego Analyzer** | Extraccion y analisis de Pliegos Tecnicos PDF |

## Arquitectura

```
                                    +------------------+
                                    |   Frontend       |
                                    |   React 19       |
                                    |   Tailwind CSS   |
                                    +--------+---------+
                                             |
                                             | HTTPS :3001
                                             v
+------------------+              +------------------+              +------------------+
|   PLACSP         |   Feed XML  |   Backend        |   Motor      |   MongoDB        |
|   (Licitaciones) | ----------> |   FastAPI        | <----------> |   Atlas          |
+------------------+              |   Python 3.11    |              +------------------+
                                  +--------+---------+
                                           |
                    +----------------------+----------------------+
                    |                      |                      |
                    v                      v                      v
            +-------------+        +-------------+        +-------------+
            |  Apollo.io  |        |  Claude AI  |        |  Gemini AI  |
            |  (B2B Data) |        |  (Analisis) |        |  (Fallback) |
            +-------------+        +-------------+        +-------------+
```

## Stack Tecnologico

| Capa | Tecnologia |
|------|------------|
| Backend | FastAPI (Python 3.11) + Uvicorn |
| Frontend | React 19 + Tailwind CSS + shadcn/ui |
| Base de datos | MongoDB Atlas |
| Autenticacion | Google OAuth 2.0 |
| IA | Claude (Anthropic), Gemini (Google), OpenAI |
| Hosting | VPS Hostinger + Nginx + PM2 |
| SSL | Let's Encrypt |

## Requisitos

- Python 3.11+
- Node.js 18+ / Yarn 1.22+
- MongoDB Atlas (o local)
- Claves API: Apollo.io, Anthropic (Claude), Google (Gemini/OAuth)

## Instalacion Local

### 1. Clonar repositorio

```bash
git clone https://github.com/gutierrezbj/srs-crm.git
cd srs-crm
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
python server.py
```

El backend estara disponible en `http://localhost:8000`

### 3. Frontend

```bash
cd frontend
yarn install
cp .env.example .env
# Editar .env con la URL del backend
yarn start
```

El frontend estara disponible en `http://localhost:3000`

## Variables de Entorno

Ver `.env.example` en cada directorio para la lista completa. Variables criticas:

```env
# MongoDB
MONGO_URL=mongodb+srv://...

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# Apollo.io
APOLLO_API_KEY=xxx

# IA (al menos uno requerido)
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=xxx
OPENAI_API_KEY=sk-xxx
```

## Comandos de Desarrollo

```bash
# Backend
cd backend
python server.py                    # Servidor desarrollo
python -m pytest tests/             # Tests

# Frontend
cd frontend
yarn start                          # Servidor desarrollo
yarn build                          # Build produccion
yarn test                           # Tests
```

## Estructura del Proyecto

```
srs-crm/
├── backend/
│   ├── server.py                 # API FastAPI (40+ endpoints)
│   ├── requirements.txt
│   ├── app/spotter/              # Motor de analisis
│   │   ├── spotter_srs.py        # Scraper PLACSP + clasificacion
│   │   ├── pliego_analyzer.py    # Analisis PDFs con IA
│   │   ├── pain_analyzer.py      # Analisis de dolor rapido
│   │   ├── adjudicatario_enricher.py  # Extraccion datos PLACSP
│   │   ├── analisis_comercial.py # Orquestacion analisis completo
│   │   ├── catalogo_srs.py       # Catalogo servicios SRS
│   │   ├── modelos_analisis.py   # Modelos Pydantic
│   │   └── run_spotter_cron.py   # Script para cron job
│   └── docs/                     # Documentacion backend
├── frontend/
│   ├── src/
│   │   ├── pages/                # Paginas principales
│   │   │   ├── Dashboard.js      # KPIs y metricas
│   │   │   ├── Leads.js          # Gestion leads CRM
│   │   │   ├── Pipeline.js       # Vista Kanban
│   │   │   ├── Oportunidades.jsx # Gestor PLACSP
│   │   │   └── Admin.js          # Panel administracion
│   │   ├── components/           # Componentes React
│   │   │   ├── Layout.js         # Sidebar + header
│   │   │   ├── LeadModal.js      # Modal crear/editar lead
│   │   │   └── ui/               # 50+ componentes shadcn/ui
│   │   └── context/              # Contextos (tema, auth)
│   └── docs/                     # Documentacion frontend
├── docs/
│   ├── architecture.md           # Arquitectura detallada
│   ├── deployment/               # Guias de deployment
│   │   ├── vps-setup.md
│   │   ├── nginx.md
│   │   ├── pm2.md
│   │   └── ssl.md
│   └── api/
│       └── endpoints.md          # Referencia API
└── README.md
```

## Funcionalidades

### CRM Core
- Gestion de leads (CRUD completo)
- Pipeline visual Kanban con 7 etapas
- Historial de actividades por lead
- Importacion de leads desde Excel
- Dashboard con metricas de conversion
- Exportacion CSV

### SpotterSRS - Detector de Oportunidades
- Monitorización automatica de PLACSP (licitaciones publicas)
- Filtrado por CPVs relevantes (IT, telecomunicaciones, energia)
- Clasificacion inteligente por tipo:
  - Infraestructura / CPD
  - Cloud / Virtualizacion
  - Ciberseguridad
  - Comunicaciones Unificadas
  - Healthcare IT
  - Fotovoltaica / Energia
  - Drones / Cartografia
- Scoring de oportunidades (0-100)
- Conversion de oportunidades a leads

### Integracion Apollo.io
- Enriquecimiento de leads (telefono, cargo, LinkedIn)
- Enriquecimiento de empresas (sector, tamanio, revenue)
- Boton "Enriquecer" en modal de lead

### Analisis con IA
- **Analisis Rapido** (~10s): Score basico sin descargar PDFs
- **Analisis Completo** (~2min): Descarga pliego + analisis Claude
- **Analisis de Pain**: Identificacion de dolores especificos

## Documentacion

| Documento | Descripcion |
|-----------|-------------|
| [Arquitectura](/docs/architecture.md) | Diseno del sistema |
| [API Backend](/backend/docs/api.md) | Referencia de endpoints |
| [Modelos](/backend/docs/models.md) | Esquemas MongoDB |
| [SpotterSRS](/backend/docs/spotter.md) | Motor de deteccion |
| [Enricher](/backend/docs/enricher.md) | Extraccion de datos |
| [Analyzer](/backend/docs/analyzer.md) | Analisis con IA |
| [Componentes](/frontend/docs/components.md) | Componentes React |
| [Paginas](/frontend/docs/pages.md) | Rutas y vistas |
| [Deployment](/docs/deployment/) | Guias de despliegue |

## URLs de Produccion

- **CRM**: https://crm.systemrapidsolutions.com:3001
- **API**: https://crm.systemrapidsolutions.com:3001/api
- **Health**: https://crm.systemrapidsolutions.com:3001/api/health

## Cron Jobs

| Job | Horario | Descripcion |
|-----|---------|-------------|
| SpotterSRS | 8:00 AM diario | Escanea PLACSP por nuevas adjudicaciones |

## Deployment a Produccion

```bash
# En el servidor VPS
ssh usuario@72.62.41.234
cd /var/www/srs-crm
git pull origin main

# Backend
cd backend && source venv/bin/activate
pip install -r requirements.txt
pm2 restart srs-crm-backend

# Frontend
cd ../frontend
yarn install && yarn build
systemctl reload nginx
```

Ver documentacion detallada en `/docs/deployment/`

## Troubleshooting

### Backend no inicia
```bash
pm2 logs srs-crm-backend --lines 100
# Verificar MONGO_URL y API keys en .env
```

### Frontend no carga datos
```bash
# Verificar REACT_APP_BACKEND_URL en frontend/.env
# Verificar CORS en backend
```

### SpotterSRS no detecta oportunidades
```bash
# Ejecutar manualmente para debug
cd backend/app/spotter
python run_spotter_cron.py
```

### Reclasificar oportunidades existentes
```bash
cd backend/app/spotter
python reclasificar_oportunidades.py --dry-run  # Ver cambios sin aplicar
python reclasificar_oportunidades.py            # Aplicar cambios
```

## Equipo

- JuanCho (Admin)
- Andros (Ops)
- Adriana (Ops)

## Changelog

### v1.1.0 (Enero 2026)
- Clasificacion Drones/Cartografia con deteccion inteligente LiDAR
- Asignacion de oportunidades a usuarios
- Abreviaciones de tipos SRS (FV, Infra, etc.)
- Analisis de pliegos tecnicos con Claude

### v1.0.0 (Enero 2026)
- MVP completo: leads, pipeline, dashboard
- Integracion Apollo.io
- SpotterSRS con cron diario
- Google OAuth + SSL

---

*Desarrollado por System Rapid Solutions - 2026*
