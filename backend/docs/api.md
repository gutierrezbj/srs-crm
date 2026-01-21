# API Backend - Referencia de Endpoints

Base URL: `https://crm.systemrapidsolutions.com:3001/api`

## Autenticacion

Todos los endpoints (excepto `/auth/session`) requieren header:
```
Authorization: Bearer <session_token>
```

---

## Auth

### POST /auth/session
Crea sesion desde Google OAuth.

**Request:**
```json
{
  "credential": "google_id_token"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user": {
    "email": "user@example.com",
    "name": "Usuario",
    "picture": "https://...",
    "role": "admin"
  }
}
```

### GET /auth/me
Obtiene usuario actual.

**Response:**
```json
{
  "email": "user@example.com",
  "name": "Usuario",
  "role": "admin"
}
```

### POST /auth/logout
Cierra sesion actual.

**Response:**
```json
{
  "message": "Logged out"
}
```

---

## Leads

### GET /leads
Lista leads con filtros y paginacion.

**Query params:**
- `page` (int): Pagina (default: 1)
- `limit` (int): Items por pagina (default: 20)
- `etapa` (string): Filtrar por etapa
- `sector` (string): Filtrar por sector
- `propietario` (string): Filtrar por user_id
- `search` (string): Busqueda full-text
- `sort_by` (string): Campo para ordenar
- `sort_order` (string): "asc" o "desc"

**Response:**
```json
{
  "leads": [...],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### GET /leads/{lead_id}
Obtiene detalle de un lead.

**Response:**
```json
{
  "id": "...",
  "empresa": "Empresa S.L.",
  "contacto": "Juan Perez",
  "email": "juan@empresa.com",
  "telefono": "+34 600 000 000",
  "cargo": "Director IT",
  "sector": "IT/Soporte",
  "valor_estimado": 50000,
  "etapa": "propuesta",
  "servicios": ["Cableado", "Soporte IT"],
  "fuente": "Licitacion",
  "urgencia": "Corto plazo",
  "propietario": "user_id",
  "proximo_seguimiento": "2026-02-01T10:00:00Z",
  "notas": "...",
  "created_at": "2026-01-15T08:00:00Z",
  "updated_at": "2026-01-20T14:30:00Z"
}
```

### POST /leads
Crea nuevo lead.

**Request:**
```json
{
  "empresa": "Nueva Empresa S.L.",
  "contacto": "Maria Garcia",
  "email": "maria@nueva.com",
  "sector": "IT/Soporte",
  "fuente": "Web",
  "valor_estimado": 25000
}
```

**Response:** Lead creado con `id`

### PUT /leads/{lead_id}
Actualiza lead completo.

**Request:** Objeto lead completo

### PATCH /leads/{lead_id}/stage
Cambia etapa del lead.

**Request:**
```json
{
  "etapa": "calificado"
}
```

### DELETE /leads/{lead_id}
Elimina lead.

### GET /leads/stats
Obtiene estadisticas KPIs.

**Response:**
```json
{
  "total_leads": 150,
  "por_etapa": {
    "nuevo": 25,
    "contactado": 30,
    "calificado": 20,
    "propuesta": 15,
    "negociacion": 10,
    "ganado": 40,
    "perdido": 10
  },
  "valor_pipeline": 500000,
  "tasa_conversion": 0.27,
  "por_sector": {...},
  "por_fuente": {...}
}
```

### GET /leads/export
Exporta leads a CSV.

**Query params:**
- `etapa` (string): Filtrar por etapa
- `fecha_desde` (date): Desde fecha
- `fecha_hasta` (date): Hasta fecha

**Response:** Archivo CSV

### POST /leads/import
Importa leads desde Excel.

**Request:** `multipart/form-data` con archivo Excel

**Response:**
```json
{
  "preview": [...],
  "columns": ["empresa", "contacto", "email"],
  "total_rows": 50
}
```

### POST /leads/import-mapped
Importa con mapeo de columnas.

**Request:**
```json
{
  "file_id": "...",
  "mapping": {
    "Nombre Empresa": "empresa",
    "Email contacto": "email"
  }
}
```

### POST /leads/check-duplicates
Detecta duplicados antes de importar.

**Request:**
```json
{
  "emails": ["a@b.com", "c@d.com"]
}
```

**Response:**
```json
{
  "duplicados": ["a@b.com"],
  "nuevos": ["c@d.com"]
}
```

### POST /leads/bulk-update
Actualiza multiples leads.

**Request:**
```json
{
  "lead_ids": ["id1", "id2"],
  "updates": {
    "etapa": "contactado",
    "propietario": "user_id"
  }
}
```

### POST /leads/bulk-delete
Elimina multiples leads.

**Request:**
```json
{
  "lead_ids": ["id1", "id2"]
}
```

---

## Actividades

### GET /leads/{lead_id}/activities
Obtiene historial de actividades.

**Response:**
```json
{
  "activities": [
    {
      "id": "...",
      "tipo": "llamada",
      "descripcion": "Llamada inicial",
      "resultado": "Interesado",
      "fecha": "2026-01-20T10:00:00Z",
      "created_by": "user_id"
    }
  ]
}
```

### POST /leads/{lead_id}/activities
Registra nueva actividad.

**Request:**
```json
{
  "tipo": "email",
  "descripcion": "Envio propuesta",
  "resultado": "Pendiente respuesta"
}
```

---

## Oportunidades PLACSP

### POST /oportunidades/spotter
Ejecuta SpotterSRS manualmente.

**Response:**
```json
{
  "nuevas": 15,
  "actualizadas": 5,
  "errores": 0,
  "tiempo_segundos": 45
}
```

### GET /oportunidades
Lista oportunidades con filtros.

**Query params:**
- `page`, `limit`: Paginacion
- `tipo_srs` (string): Filtrar por tipo
- `estado_revision` (string): Filtrar por estado
- `score_min` (int): Score minimo
- `asignado_a` (string): Filtrar por usuario asignado
- `search` (string): Busqueda

**Response:**
```json
{
  "oportunidades": [...],
  "total": 500,
  "page": 1
}
```

### GET /oportunidades/{oportunidad_id}
Detalle de oportunidad.

### PATCH /oportunidades/{oportunidad_id}/asignar
Asigna oportunidad a usuario.

**Request:**
```json
{
  "user_id": "abc123",
  "nombre": "Juan"
}
```

### POST /oportunidades/analisis-rapido
Analisis rapido sin PDF (~10 segundos).

**Request:**
```json
{
  "oportunidad_id": "...",
  "url_licitacion": "https://contrataciondelestado.es/..."
}
```

**Response:**
```json
{
  "pain_score": 75,
  "nivel_urgencia": "alto",
  "componentes_detectados": ["Cableado", "Soporte IT"],
  "probabilidad_subcontratacion": "media",
  "datos_adjudicatario": {
    "nombre": "Empresa Adjudicataria S.L.",
    "email": "contacto@empresa.com",
    "telefono": "..."
  }
}
```

### POST /oportunidades/analisis-comercial
Analisis completo con PDF (~2 minutos).

**Request:**
```json
{
  "oportunidad_id": "...",
  "url_pliego": "https://..."
}
```

**Response:** Objeto `AnalisisComercial` completo (ver models.md)

### POST /oportunidades/analizar-pain
Analisis de dolor especifico.

**Request:**
```json
{
  "oportunidad_id": "...",
  "objeto": "Descripcion del contrato..."
}
```

### GET /oportunidades/resumen-operador/{oportunidad_id}
Obtiene resumen para comercial.

**Response:**
```json
{
  "nivel_oportunidad": "A",
  "score_total": 85,
  "dolor_principal": {
    "categoria": "temporal",
    "descripcion": "Fecha limite inminente"
  },
  "gancho_inicial": {
    "whatsapp": "Hola, vi que ganaron...",
    "email": "Asunto: Servicios complementarios...",
    "llamada": "Script para llamada..."
  },
  "objeciones": [
    {
      "objecion": "Ya tenemos equipo interno",
      "respuesta": "Entiendo, pero para picos..."
    }
  ],
  "siguiente_accion": "Llamar manana 10:00"
}
```

### POST /oportunidades/{id}/convertir-lead
Convierte oportunidad a lead CRM.

**Response:**
```json
{
  "lead_id": "...",
  "message": "Lead creado correctamente"
}
```

---

## Apollo.io

### POST /apollo/enrich/person
Enriquece datos de persona.

**Request:**
```json
{
  "email": "contacto@empresa.com"
}
```

**Response:**
```json
{
  "nombre": "Juan Perez",
  "cargo": "Director IT",
  "telefono": "+34 600 000 000",
  "linkedin": "https://linkedin.com/in/...",
  "empresa": {
    "nombre": "Empresa S.L.",
    "sector": "Technology",
    "empleados": 250
  }
}
```

### POST /apollo/enrich/company
Enriquece datos de empresa.

**Request:**
```json
{
  "domain": "empresa.com"
}
```

### POST /apollo/search
Busqueda en Apollo.

**Request:**
```json
{
  "query": "Director IT Madrid",
  "limit": 10
}
```

### POST /leads/{lead_id}/enrich-apollo
Enriquece lead existente con Apollo.

**Response:** Lead actualizado con datos enriquecidos

### GET /apollo/health
Health check de Apollo.

**Response:**
```json
{
  "status": "ok",
  "credits_remaining": 150
}
```

---

## Reportes

### GET /reports
Obtiene reportes generales.

**Query params:**
- `tipo` (string): Tipo de reporte
- `fecha_desde` (date): Desde
- `fecha_hasta` (date): Hasta

**Response:**
```json
{
  "conversiones": {...},
  "por_sector": {...},
  "por_fuente": {...},
  "tendencias": [...]
}
```

### GET /reports/export/{report_type}
Exporta reporte.

**Response:** PDF o Excel segun tipo

---

## Usuarios

### GET /users
Lista usuarios (solo admin).

**Response:**
```json
{
  "users": [
    {
      "id": "...",
      "email": "user@srs.com",
      "name": "Usuario",
      "role": "user"
    }
  ]
}
```

### POST /users
Crea usuario (solo admin).

**Request:**
```json
{
  "email": "nuevo@srs.com",
  "name": "Nuevo Usuario",
  "role": "user"
}
```

### PUT /users/{user_id}
Actualiza usuario.

### DELETE /users/{user_id}
Elimina usuario.

---

## Configuracion

### GET /sectors
Lista sectores disponibles.

**Response:**
```json
["IT/Soporte", "Fotovoltaica", "Drones", "Sanidad", "Retail"]
```

### GET /options
Obtiene todas las opciones para dropdowns.

**Response:**
```json
{
  "etapas": [...],
  "sectores": [...],
  "fuentes": [...],
  "urgencias": [...],
  "tipos_actividad": [...]
}
```

### GET /health
Health check general.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-21T10:00:00Z",
  "version": "1.1.0"
}
```

---

## Codigos de Error

| Codigo | Descripcion |
|--------|-------------|
| 400 | Bad Request - Datos invalidos |
| 401 | Unauthorized - Token invalido o expirado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Validacion fallida |
| 500 | Internal Server Error |

**Formato de error:**
```json
{
  "detail": "Descripcion del error",
  "code": "ERROR_CODE"
}
```
