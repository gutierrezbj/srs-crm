# System Rapid Solutions CRM - PRD

## Información del Proyecto
- **Proyecto**: CRM Minimalista para System Rapid Solutions
- **Cliente**: Empresa de servicios IT y Drones
- **Fecha inicio**: Enero 2025
- **Versión actual**: 1.2
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

### Fase 1.2 (Completada - 10 Enero 2025)
- [x] Módulo de Reportes completo con 6 gráficos
- [x] Filtro de rango de fechas (Este mes, Trimestre, Año, Personalizado)
- [x] Exportación CSV por reporte
- [x] Contraste dropdowns modo oscuro corregido
  - Placeholder: Slate 400 (#94a3b8)
  - Texto seleccionado: Slate 200 (#e2e8f0)
  - Fondo dropdown: Slate 800 (#1e293b)
  - Hover opciones: Slate 700 (#334155)
- [x] Mejora campo Próximo Seguimiento:
  - Date picker visual (calendario clickeable)
  - Auto-sugerencia de fecha basada en Urgencia:
    - Inmediata → +1 día (mañana)
    - Corto plazo → +3 días
    - Medio plazo → +7 días
    - Largo plazo → +14 días
    - Sin definir → hoy
  - Muestra día de la semana junto a la fecha

### Fase 2 (Pendiente - P1)
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
- **GET /api/reports** - Datos agregados para reportes
- **GET /api/reports/export/{type}** - Exportar reporte a CSV

### Frontend Pages
- /login - Login con Google OAuth
- /dashboard - Dashboard con KPIs y seguimientos
- /leads - Lista de leads
- /pipeline - Kanban board
- **/reports - Módulo de reportes con 6 gráficos**
- /admin - Gestión de usuarios (solo admin)

### Reportes Disponibles (Fase 1.2)
1. Pipeline por Etapa (gráfico de barras horizontal + tabla)
2. Leads por Fuente (gráfico de dona)
3. Leads por Sector (gráfico de barras)
4. Servicios Demandados (gráfico de barras horizontal)
5. Leads por Propietario (gráfico de barras + tabla)
6. Motivos de Pérdida (gráfico de dona)

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

## Testing Status
- Backend: 15/15 tests pasados
- Frontend: 100% funcional
- Test file: /app/tests/test_reports_api.py

## Next Action Items
1. **Fase 2 - P1**: Integración Gmail API (ver/enviar emails desde ficha de lead)
2. **Fase 2 - P1**: Integración Google Calendar API (agenda y eventos vinculados)
3. Notificaciones automáticas de seguimientos

## Backlog / Future
- Mini calendario en sidebar
- Dashboard de productividad por vendedor
- Reportes automatizados por email
- Integraciones adicionales (WhatsApp, Teams)
