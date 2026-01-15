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

### SpotterSRS - Detector de Oportunidades
- Monitorización automática de PLACSP (licitaciones públicas españolas)
- Filtrado por CPVs relevantes para SRS
- Scoring de oportunidades
- Conversión de oportunidades a leads
- Cron job diario (8:00 AM)

## Estructura del Proyecto
```
srs-crm/
├── backend/
│   ├── server.py              # API FastAPI principal
│   ├── app/
│   │   └── spotter/
│   │       ├── spotter_srs.py      # Detector PLACSP
│   │       └── run_spotter_cron.py # Script para cron
│   └── start.sh               # Script de inicio
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── LeadModal.js   # Modal con botón Apollo
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

# Ejecutar SpotterSRS manualmente
cd /var/www/srs-crm/backend
source venv/bin/activate
python app/spotter/run_spotter_cron.py
```

## URLs

- **Producción:** https://crm.systemrapidsolutions.com:3001
- **API Health:** https://crm.systemrapidsolutions.com:3001/api/health

## Equipo

- JuanCho (Admin)
- Andros (Ops)
- Adriana (Ops)

## Changelog

### v1.0.0 (Enero 2026)
- MVP completo: leads, pipeline, dashboard
- Integración Apollo.io (enrich personas y empresas)
- SpotterSRS con cron diario
- Google OAuth
- SSL + dominio propio

---

*Desarrollado por System Rapid Solutions - Enero 2026*
