# Handoff - SRS CRM SpotterSRS

## Fecha: 2025-01-21

## Estado Actual del Proyecto

### Problema Principal Pendiente
**Los datos del adjudicatario no se están cargando correctamente desde el HTML de adjudicación de PLACSP.**

El sistema extrae datos del HTML de adjudicación (email, teléfono, dirección, importes, motivación, ofertas) pero estos NO se están mostrando en el frontend.

**Ejemplo del bug:**
- En el CRM aparece: Empresa "tias", NIF "B76158401"
- En el HTML de PLACSP aparece: "NTT DATA SPAIN, S.L.U.", NIF "B82387770", email "spain.proposals.office@nttdata.com"

### Diagnóstico Realizado
1. El código de extracción (`_parse_html_adjudicacion`) funciona correctamente - extrae el email correcto cuando se prueba aislado
2. El problema está en el flujo del endpoint `/analisis-rapido`:
   - Se llama a `extraer_datos_placsp()` que obtiene datos de la página principal de licitación
   - Se llama a `_parse_html_adjudicacion()` para obtener datos detallados del HTML de adjudicación
   - **Pero los datos del HTML no se estaban mezclando con datos_placsp** (esto se corrigió en commit 44a2386)
   - Sin embargo, sigue sin funcionar - puede que `html_adjudicacion_url` no se esté obteniendo correctamente

### Archivos Clave

```
backend/
├── server.py                           # Endpoint /analisis-rapido (líneas ~2467-2620)
├── app/spotter/
│   ├── adjudicatario_enricher.py       # Extracción de datos PLACSP
│   │   ├── extraer_datos_placsp()      # Método público (línea 211)
│   │   ├── _scrape_placsp()            # Scrape página principal (línea 397)
│   │   ├── _parse_html_adjudicacion()  # Parsea HTML adjudicación (línea 1355)
│   │   └── Extracción de secciones     # Líneas 1441-1600
│   ├── pliego_analyzer.py              # Análisis de pliegos con IA
│   └── catalogo_srs.py                 # Catálogo de servicios SRS

frontend/
├── src/pages/Oportunidades.jsx         # Página principal de oportunidades
```

### Commits Recientes
```
44a2386 fix: incorporar datos del HTML de adjudicación al análisis rápido
491acf2 feat: extraer datos completos del HTML de adjudicación PLACSP
b7f469b feat: añadir más campos del adjudicatario al análisis rápido
c6659bd fix: limpiar nombres de empresas competidoras
```

### Lo que funciona
- Extracción de competidores del PDF del Acta de Resolución
- Detección de componente IT
- URLs de pliegos (PPT, PCAP)
- Extracción del HTML cuando se prueba directamente (el regex funciona)

### Lo que NO funciona
- Los datos del HTML de adjudicación no llegan al frontend
- El nombre de empresa mostrado es incorrecto ("tias" en lugar de "NTT DATA SPAIN")
- El email del adjudicatario no se muestra

## Para Depurar

### 1. Ver logs del servidor
```bash
ssh usuario@servidor
cd /var/www/srs-crm
pm2 logs --lines 200
```

### 2. Reiniciar backend
```bash
pm2 list                    # Ver nombre del proceso
pm2 restart <nombre>        # Reiniciar
```

### 3. Test de extracción manual
```python
# Probar extracción del HTML de adjudicación
import urllib.request
import ssl
import re

url = 'URL_DEL_HTML_ADJUDICACION'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
html = resp.read().decode('utf-8')

# Ver sección Adjudicatario
texto = re.sub(r'<[^>]+>', ' ', html)
adj_match = re.search(r'Adjudicatario(.{500})', texto, re.I)
print(adj_match.group(0) if adj_match else "No encontrado")
```

## Estructura del HTML de Adjudicación PLACSP

El HTML tiene esta estructura:
```
Adjudicado
├── Adjudicatario
│   ├── Nombre (ej: "NTT DATA SPAIN, S.L.U.")
│   ├── NIF
│   ├── Es PYME: Sí/No
│   └── País Origen
├── Dirección Física
│   ├── Calle
│   └── CP/Localidad
├── Contacto
│   ├── Teléfono
│   └── Correo Electrónico  <-- EMAIL CORRECTO DEL ADJUDICATARIO
├── Importes de Adjudicación
│   ├── Sin impuestos
│   └── Con impuestos
├── Motivación
│   ├── Razón
│   └── Fecha del Acuerdo
└── Información Sobre las Ofertas
    ├── Ofertas recibidas
    ├── Ofertas PYMEs
    ├── Precio más bajo
    └── Precio más alto
```

## Próximos Pasos

1. **CRÍTICO**: Verificar por qué `html_adjudicacion_url` no se está obteniendo para algunas licitaciones
   - Añadir logging en `_scrape_placsp()` para ver qué URLs encuentra
   - Verificar que la estructura HTML de PLACSP no ha cambiado

2. **Verificar flujo completo**:
   - Endpoint recibe request
   - `extraer_datos_placsp()` retorna con `html_adjudicacion_url`?
   - `_parse_html_adjudicacion()` extrae datos correctos?
   - Los datos se mezclan con `datos_placsp`?
   - La respuesta del endpoint incluye los datos?

3. **Posible problema**: El frontend puede estar usando datos de la BD en lugar de los datos frescos del análisis

## Conexión al Servidor

El servidor se accede via SSH. Revisar `~/.ssh/config` del usuario para el alias correcto.
El repositorio está en: `/var/www/srs-crm`
El backend usa PM2 para gestión de procesos.

## Base de Datos

MongoDB - colección principal: `oportunidades_placsp`
Campos relevantes:
- `datos_adjudicatario`: Dict con datos del adjudicatario
- `analisis_rapido`: Resultado del último análisis rápido
- `empresas_competidoras`: Lista de competidores

## Branch Actual
`admiring-hamilton` (worktree)
