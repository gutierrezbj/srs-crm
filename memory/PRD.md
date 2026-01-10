# System Rapid Solutions CRM - PRD

## Información del Proyecto
- **Proyecto**: CRM Minimalista para System Rapid Solutions
- **Cliente**: Empresa de servicios IT y Drones
- **Fecha inicio**: Enero 2025
- **Stack**: FastAPI + React + MongoDB

## Problem Statement Original
CRM interno para gestión de leads/contactos con:
- Dashboard con métricas
- CRUD completo de leads
- Pipeline Kanban con drag & drop
- Importación/exportación CSV
- Integración Google OAuth (solo @systemrapidsolutions.com)
- 3 usuarios: JuanCho (admin), Andros, Adriana

## User Personas
1. **JuanCho (Admin)**: Control total del CRM, gestión de configuración
2. **Andros (User)**: Gestión de leads comerciales IT
3. **Adriana (User)**: Gestión de leads comerciales drones

## Core Requirements (Estáticos)
### Fase 1 (Implementada)
- [x] Dashboard con KPIs (pipeline value, total leads, ganados, sin actividad)
- [x] CRUD Leads completo
- [x] Pipeline Kanban con drag & drop
- [x] Importación CSV/Excel
- [x] Exportación CSV
- [x] API para Apollo.io (/api/leads/enrich)
- [x] Timeline de actividades por lead
- [x] Google OAuth con Emergent (solo @systemrapidsolutions.com)
- [x] Roles: admin, user

### Fase 2 (Pendiente)
- [ ] Integración Gmail embebida
- [ ] Integración Google Calendar embebida
- [ ] Mini calendario en sidebar

## Lo Implementado
### Backend (/app/backend/server.py)
- GET /api/ - Info de la API
- POST /api/auth/session - Exchange session OAuth
- GET /api/auth/me - Usuario actual
- POST /api/auth/logout - Cerrar sesión
- GET /api/leads - Listar leads (con filtros)
- POST /api/leads - Crear lead
- GET /api/leads/stats - Stats para dashboard
- GET /api/leads/export - Exportar CSV
- POST /api/leads/import - Importar CSV/Excel
- GET /api/leads/{id} - Obtener lead
- PUT /api/leads/{id} - Actualizar lead
- PATCH /api/leads/{id}/stage - Cambiar etapa
- DELETE /api/leads/{id} - Eliminar lead
- GET /api/leads/{id}/activities - Actividades del lead
- POST /api/leads/{id}/activities - Añadir actividad
- POST /api/leads/enrich - API para Apollo.io
- GET /api/sectors - Sectores únicos

### Frontend
- /login - Página de login con Google OAuth
- /dashboard - Dashboard con KPIs y métricas
- /leads - Lista de leads con filtros y búsqueda
- /pipeline - Kanban board con drag & drop
- LeadModal - Modal para crear/editar leads y ver actividades
- Layout - Sidebar con navegación

## Backlog Priorizado
### P0 (Crítico) - COMPLETADO
- [x] CRUD Leads básico
- [x] Dashboard funcional
- [x] Pipeline Kanban

### P1 (Alta prioridad) - PENDIENTE
- [ ] Gmail API integration
- [ ] Google Calendar API integration
- [ ] Notificaciones de leads sin actividad

### P2 (Media prioridad)
- [ ] Reportes avanzados
- [ ] Búsqueda avanzada con más filtros
- [ ] Duplicados automáticos

## Arquitectura
```
/app
├── backend/
│   ├── server.py         # FastAPI app con todos los endpoints
│   ├── requirements.txt  # Dependencias Python
│   └── .env             # Variables de entorno
└── frontend/
    ├── src/
    │   ├── App.js        # Router principal con OAuth
    │   ├── pages/
    │   │   ├── Login.js
    │   │   ├── Dashboard.js
    │   │   ├── Leads.js
    │   │   └── Pipeline.js
    │   └── components/
    │       ├── Layout.js
    │       └── LeadModal.js
    ├── package.json
    └── .env
```

## Next Action Items
1. Configurar Google Cloud Console para Gmail y Calendar APIs
2. Implementar integración Gmail en ficha de lead
3. Implementar integración Calendar en sidebar y ficha de lead
4. Añadir notificaciones automáticas de leads sin actividad
