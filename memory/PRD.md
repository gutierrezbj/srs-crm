# System Rapid Solutions CRM - PRD

## Información del Proyecto
- **Proyecto**: CRM Minimalista para System Rapid Solutions
- **Cliente**: Empresa de servicios IT y Drones
- **Fecha inicio**: Enero 2025
- **Versión actual**: 1.1
- **Stack**: FastAPI + React + MongoDB

## Problem Statement Original
CRM interno para gestión de leads/contactos con:
- Dashboard con métricas
- CRUD completo de leads
- Pipeline Kanban con drag & drop
- Importación/exportación CSV
- Integración Google OAuth (solo @systemrapidsolutions.com)
- 3 usuarios: JuanCho (admin), Andros, Adriana

## Core Requirements (Estáticos)
### Fase 1 (Completada)
- [x] Dashboard con KPIs
- [x] CRUD Leads completo
- [x] Pipeline Kanban con drag & drop
- [x] Importación CSV/Excel
- [x] Exportación CSV
- [x] API para Apollo.io
- [x] Timeline de actividades
- [x] Google OAuth con Emergent
- [x] Roles: admin, user
- [x] Light/Dark mode

### Fase 1.1 (Completada)
- [x] Drag & drop corregido
- [x] Propietario del lead (dropdown)
- [x] Sector (dropdown con opciones)
- [x] Servicios de interés (dropdown múltiple)
- [x] Fuente del lead (dropdown)
- [x] Urgencia del cliente (dropdown)
- [x] Motivo de pérdida (solo si perdido)
- [x] Próximo seguimiento (fecha + tipo)
- [x] Seguimientos del día en Dashboard
- [x] Panel Admin (gestión usuarios)

### Fase 2 (Pendiente)
- [ ] Integración Gmail embebida
- [ ] Integración Google Calendar embebida
- [ ] Mini calendario en sidebar

## Lo Implementado
### Backend Endpoints
- GET /api/ - Info API
- POST /api/auth/session - OAuth exchange
- GET /api/auth/me - Usuario actual
- POST /api/auth/logout - Logout
- GET /api/leads - Listar leads
- POST /api/leads - Crear lead
- GET /api/leads/stats - Stats dashboard
- GET /api/leads/export - Export CSV
- POST /api/leads/import - Import CSV/Excel
- GET /api/leads/{id} - Obtener lead
- PUT /api/leads/{id} - Actualizar lead
- PATCH /api/leads/{id}/stage - Cambiar etapa
- DELETE /api/leads/{id} - Eliminar lead
- GET /api/leads/{id}/activities - Actividades
- POST /api/leads/{id}/activities - Nueva actividad
- POST /api/leads/enrich - API Apollo.io
- GET /api/sectors - Sectores
- GET /api/options - Dropdown options
- GET /api/users - Lista usuarios
- POST /api/users - Crear usuario
- PUT /api/users/{id} - Actualizar usuario
- DELETE /api/users/{id} - Eliminar usuario

### Frontend Pages
- /login - Login con Google OAuth
- /dashboard - Dashboard con KPIs y seguimientos
- /leads - Lista de leads
- /pipeline - Kanban board
- /admin - Gestión de usuarios (solo admin)

### Campos del Lead
- empresa, contacto, email, telefono, cargo
- sector (dropdown)
- valor_estimado
- etapa
- notas
- propietario (dropdown usuarios)
- servicios (múltiple selección)
- fuente (dropdown)
- urgencia (dropdown)
- motivo_perdida (solo si perdido)
- proximo_seguimiento (fecha)
- tipo_seguimiento (dropdown)

## Next Action Items
1. Fase 2: Integración Gmail API
2. Fase 2: Integración Calendar API
3. Notificaciones automáticas de seguimientos
