# SRS CRM

Sistema CRM interno de System Rapid Solutions para gestión de leads, pipeline comercial y detección de oportunidades de contratación pública.

## Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Frontend | React + Tailwind CSS |
| Backend | Python FastAPI |
| Base de datos | MongoDB Atlas |
| Autenticación | Google OAuth 2.0 |
| Hosting | VPS Hostinger |
| SSL | Let's Encrypt |

## Funcionalidades

### Core CRM
- Gestión de leads (CRUD completo)
- Pipeline visual Kanban con etapas personalizadas
- Historial de actividades por lead
- Importación de leads desde Excel
- Dashboard con métricas de conversión

### Integración Apollo.io
- Enriquecimiento de leads (teléfono, cargo, LinkedIn)
- Enriquecimiento de empresas (sector, tamaño, revenue)
- Botón "Enriquecer" en vista de lead

### SpotterSRS - Detector de Oportunidades (Adjudicaciones)
- Monitorización automática de PLACSP (licitaciones públicas españolas)
- Filtrado por CPVs relevantes para SRS
- Scoring de oportunidades
- Conversión de oportunidades a leads
- Cron job diario (8:00 AM)

### SpotterSRS-Licitaciones (Drones) - NUEVO
Módulo para detectar licitaciones ABIERTAS relacionadas con servicios de drones.

**Diferencia con SpotterSRS principal:**
| Aspecto | SpotterSRS (principal) | SpotterSRS-Licitaciones |
|---------|------------------------|-------------------------|
| Objetivo | Adjudicaciones (subcontratación) | Licitaciones abiertas (pujar) |
| Target | Empresas que ganaron contratos | Licitaciones sin adjudicar |
| Acción | Contactar adjudicatario | Preparar oferta |

**Funcionalidades:**
- Consulta feed ATOM de PLACSP con certificado FNMT
- Motor de análisis con scoring 0-100 basado en CPVs y keywords
- Mapeo CPV drones v2.0-TALADRO (11 categorías)
- Vista frontend con filtros y código de colores por score
- Estados: nueva, vista, en_seguimiento, descartada

**CPV principal:** 35613000 (Vehículos aéreos no tripulados)

**Categorías de CPV soportadas:**
- Topografía y cartografía
- Inspección técnica de infraestructuras
- Agricultura y medio ambiente
- Energía (fotovoltaica, eólica)
- Emergencias y seguridad
- Audiovisual y patrimonio
- Formación RPAS
- Suministro de equipos
- Gemelos digitales / BIM
- I+D
- Telecomunicaciones

## Estructura del Proyecto
```
srs-crm/
├── backend/
│   ├── server.py                    # API FastAPI principal
│   ├── ecosystem.config.js          # Config PM2
│   ├── app/
│   │   └── spotter/
│   │       ├── spotter_srs.py       # Detector PLACSP (adjudicaciones)
│   │       └── run_spotter_cron.py  # Script para cron
│   ├── services/
│   │   ├── spotter_licitaciones_drones.py  # Scraper licitaciones drones
│   │   └── spotter_licitaciones.py         # Motor de análisis (LicitacionAnalyzer)
│   ├── config/
│   │   └── cpv_drone_mapping.json   # Mapeo CPV drones v2.0-TALADRO
│   └── start.sh                     # Script de inicio
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LicitacionesDrones.jsx  # Vista lista licitaciones drones
│   │   │   └── AnalizarDrones.jsx      # Análisis manual de licitaciones
│   │   ├── components/
│   │   │   └── LeadModal.js         # Modal con botón Apollo
│   │   └── ...
│   └── package.json
└── README.md
```

## Configuración

### Variables de entorno (backend/.env)
```env
MONGODB_URI=mongodb+srv://...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
APOLLO_API_KEY=...
JWT_SECRET=...
```

### Comandos útiles
```bash
# Estado del backend
pm2 status
pm2 logs srs-backend

# Reiniciar backend
pm2 restart srs-backend

# Rebuild frontend
cd /var/www/srs-crm/frontend
npm run build
systemctl reload nginx

# Ejecutar SpotterSRS (adjudicaciones) manualmente
cd /var/www/srs-crm/backend
source venv/bin/activate
python app/spotter/run_spotter_cron.py

# Ejecutar SpotterSRS-Licitaciones (drones) manualmente
cd /var/www/srs-crm/backend
source venv/bin/activate
python -m services.spotter_licitaciones_drones
```

## URLs

- **Producción:** https://crm.systemrapidsolutions.com:3001
- **API Health:** https://crm.systemrapidsolutions.com:3001/api/health

## Equipo

- JuanCho (Admin)
- Andros (Ops)
- Adriana (Ops)

## API Endpoints

### Licitaciones Drones
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/licitaciones/analizar` | Analizar una licitación individual |
| POST | `/api/licitaciones/analizar-batch` | Analizar lote de licitaciones |
| GET | `/api/licitaciones-drones` | Lista con filtros (score_min, dias_restantes, categoria, estado) |
| GET | `/api/licitaciones-drones/{id}` | Detalle de licitación |
| PATCH | `/api/licitaciones-drones/{id}/estado` | Actualizar estado |
| POST | `/api/licitaciones-drones/importar` | Importar licitaciones (auth requerida) |
| POST | `/api/licitaciones-drones/importar-interno` | Importar desde cron (sin auth) |

### Colección MongoDB
```
licitaciones_drones: {
  licitacion_id, expediente, titulo, descripcion, cpv,
  presupuesto, organo_contratacion, fecha_publicacion,
  fecha_limite, dias_restantes, url_licitacion, url_pliego,
  score, relevante, cpv_matches, keywords_detectados,
  categoria_principal, estado, fecha_deteccion, notas
}
```

## Notas Técnicas

### Fix word boundaries (spotter_licitaciones.py)
Keywords cortas (<=4 chars) usan regex `\b` para evitar falsos positivos:
- "uas" no detecta "ag**uas**" ni "d**uas**"
- "rpas", "bim", "gps" funcionan correctamente

### Pendiente de implementar
- [ ] Cron job diario 7:00 AM para SpotterSRS-Licitaciones
- [ ] Afinar scoring para reducir falsos positivos
- [ ] Revisar CPVs de categoría "Emergencias" que generan ruido

## Changelog

### v1.1.0 (Enero 2026)
- **SpotterSRS-Licitaciones (Drones):** Nuevo módulo para detectar licitaciones abiertas
- Motor de análisis con scoring basado en CPVs y keywords
- Mapeo CPV drones v2.0-TALADRO (11 categorías)
- Vista frontend LicitacionesDrones.jsx con filtros y código colores
- Análisis manual en AnalizarDrones.jsx
- CPV 35613000 (Vehículos aéreos no tripulados) añadido

### v1.0.0 (Enero 2026)
- MVP completo: leads, pipeline, dashboard
- Integración Apollo.io (enrich personas y empresas)
- SpotterSRS con cron diario
- Google OAuth
- SSL + dominio propio

---

*Desarrollado por System Rapid Solutions - Enero 2026*
