# Resumen para Actualizar Notion

## Pagina: CRM SRS (ID: 2e47981f08ef81ff9346c5a964047f76)

### Contenido Sugerido

---

# CRM SRS - Sistema de Gestion Comercial

## Estado: Produccion v1.1.0

**URL**: https://crm.systemrapidsolutions.com:3001
**Repositorio**: github.com/gutierrezbj/srs-crm

## Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| Frontend | React 19 + Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python 3.11) |
| Base de datos | MongoDB Atlas |
| Autenticacion | Google OAuth 2.0 |
| Hosting | VPS Hostinger |
| SSL | Let's Encrypt |

## Modulos

### 1. CRM Core
- Gestion de leads (CRUD completo)
- Pipeline Kanban con 7 etapas
- Historial de actividades
- Importacion desde Excel
- Dashboard con KPIs

### 2. SpotterSRS
Motor de deteccion automatica de oportunidades PLACSP.
- Escaneo diario a las 8:00 AM
- Clasificacion por tipo (Infra, Cloud, Ciber, Health, etc.)
- Scoring automatico (0-100)
- Conversion a leads

### 3. Integraciones
- **Apollo.io**: Enriquecimiento de datos B2B
- **Claude AI**: Analisis de pliegos tecnicos
- **Gemini/OpenAI**: Fallback para analisis

## Equipo
- JuanCho (Admin)
- Andros (Operador)
- Adriana (Operador)

## Documentacion
Ver `/docs/` en el repositorio:
- architecture.md - Arquitectura del sistema
- backend/docs/ - API y modelos
- frontend/docs/ - Componentes y paginas
- deployment/ - Guias de despliegue

## Changelog v1.1.0
- Clasificacion Drones/Cartografia con deteccion LiDAR
- Asignacion de oportunidades a usuarios
- Abreviaciones de tipos SRS
- Analisis de pliegos con Claude

---

## Pagina: SpotterSRS (ID: 2e77981f08ef813ab4afd1e520aa6a76)

### Contenido Sugerido

---

# SpotterSRS - Detector de Oportunidades

## Que es

SpotterSRS es el motor de deteccion automatica de oportunidades de negocio. Escanea diariamente las licitaciones adjudicadas en PLACSP para identificar empresas que pueden necesitar subcontratacion de servicios IT.

## Como funciona

```
PLACSP Feed XML → Scraping → Clasificacion → MongoDB → Frontend
         ↓
    Filtrado CPV
         ↓
    Deteccion keywords
         ↓
    Scoring (0-100)
```

## Tipos de Oportunidad Detectados

| Tipo | Icono | Descripcion |
|------|-------|-------------|
| Infraestructura/CPD | 🏢 | Centros de datos, cableado, racks |
| Cloud/Virtualizacion | ☁️ | AWS, Azure, VMware, Kubernetes |
| Ciberseguridad | 🔒 | SOC, auditorias, ENS, ISO 27001 |
| Comunicaciones UC | 📞 | Telefonia IP, Teams, contact center |
| Healthcare IT | 🏥 | RIS, PACS, historia clinica |
| Fotovoltaica | ☀️ | Paneles solares, autoconsumo |
| Drones/Cartografia | 🚁 | LiDAR, fotogrametria, ortofotos |
| Soporte Internacional | 🌍 | Cobertura multisede, LATAM |
| IT Generico | 💻 | Servicios IT generales |

## Ejecucion

### Automatica
Cron job diario a las 8:00 AM

### Manual
```bash
cd backend/app/spotter
python run_spotter_cron.py
```

## Analisis Disponibles

1. **Analisis Rapido** (~10 seg)
   - Score basico
   - Keywords detectados
   - Sin descargar PDF

2. **Analisis Completo** (~2 min)
   - Descarga pliego PDF
   - Analisis con Claude AI
   - Requisitos, SLAs, certificaciones
   - Gancho comercial personalizado

## Metricas Tipicas

- 100-300 oportunidades nuevas/dia
- 40-60% clasificadas como relevantes
- 15-25% clasificadas como A o B

## Archivos Clave

| Archivo | Proposito |
|---------|-----------|
| spotter_srs.py | Scraper y clasificador |
| pliego_analyzer.py | Analisis de PDFs |
| adjudicatario_enricher.py | Extraccion datos empresa |
| catalogo_srs.py | Servicios SRS para matching |

## Reclasificacion

Cuando se actualizan las reglas:
```bash
python reclasificar_oportunidades.py --dry-run  # Preview
python reclasificar_oportunidades.py            # Aplicar
```

---

## Instrucciones para Actualizar Notion

### Opcion 1: Manual
1. Abrir cada pagina en Notion
2. Copiar el contenido sugerido arriba
3. Formatear segun el estilo de Notion

### Opcion 2: Via API (usando el MCP de Notion disponible)

```javascript
// Actualizar pagina CRM SRS
notion-update-page({
  page_id: "2e47981f08ef81ff9346c5a964047f76",
  command: "replace_content",
  new_str: "..." // Contenido en Markdown
})

// Actualizar pagina SpotterSRS
notion-update-page({
  page_id: "2e77981f08ef813ab4afd1e520aa6a76",
  command: "replace_content",
  new_str: "..." // Contenido en Markdown
})
```
