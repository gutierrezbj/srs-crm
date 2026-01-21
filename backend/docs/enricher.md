# Extraccion y Enriquecimiento de Datos

## Modulos

| Modulo | Proposito |
|--------|-----------|
| `adjudicatario_enricher.py` | Extrae datos del HTML de adjudicacion PLACSP |
| Apollo.io Integration | Enriquece con datos B2B (telefono, cargo, empresa) |

---

## Adjudicatario Enricher

### Flujo de Extraccion

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SCRAPE PAGINA PRINCIPAL PLACSP                              │
│                                                                 │
│  URL: https://contrataciondelestado.es/wps/poc?uri=...          │
│                                                                 │
│  Extrae:                                                        │
│  - Titulo licitacion                                            │
│  - Cliente (organismo)                                          │
│  - Importe                                                      │
│  - URL pliego tecnico                                           │
│  - URL pliego administrativo                                    │
│  - URL HTML adjudicacion  ◄── CLAVE                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. PARSE HTML ADJUDICACION                                     │
│                                                                 │
│  Estructura del HTML:                                           │
│  ├── Adjudicatario                                              │
│  │   ├── Nombre empresa                                         │
│  │   ├── NIF                                                    │
│  │   ├── Es PYME (Si/No)                                        │
│  │   └── Pais Origen                                            │
│  ├── Direccion Fisica                                           │
│  │   ├── Calle                                                  │
│  │   └── CP/Localidad                                           │
│  ├── Contacto                                                   │
│  │   ├── Telefono                                               │
│  │   └── Correo Electronico  ◄── EMAIL ADJUDICATARIO            │
│  ├── Importes de Adjudicacion                                   │
│  │   ├── Sin impuestos                                          │
│  │   └── Con impuestos                                          │
│  ├── Motivacion                                                 │
│  │   ├── Razon                                                  │
│  │   └── Fecha del Acuerdo                                      │
│  └── Informacion Sobre las Ofertas                              │
│      ├── Ofertas recibidas                                      │
│      ├── Ofertas PYMEs                                          │
│      ├── Precio mas bajo                                        │
│      └── Precio mas alto                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. RESULTADO                                                   │
│                                                                 │
│  {                                                              │
│    "nombre": "NTT DATA SPAIN, S.L.U.",                         │
│    "nif": "B82387770",                                         │
│    "es_pyme": false,                                           │
│    "pais_origen": "España",                                    │
│    "direccion": {                                              │
│      "calle": "Calle ejemplo 123",                             │
│      "cp": "28050",                                            │
│      "localidad": "Madrid"                                     │
│    },                                                          │
│    "contacto": {                                               │
│      "telefono": "+34 91 XXX XXXX",                           │
│      "email": "spain.proposals.office@nttdata.com"            │
│    },                                                          │
│    "importes": {                                               │
│      "sin_impuestos": 1500000.00,                             │
│      "con_impuestos": 1815000.00                              │
│    }                                                           │
│  }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Metodos Principales

```python
# Punto de entrada publico
async def extraer_datos_placsp(url_licitacion: str) -> dict:
    """
    Extrae todos los datos de una licitacion PLACSP.

    Args:
        url_licitacion: URL de la pagina principal de la licitacion

    Returns:
        Dict con todos los datos extraidos
    """
    pass

# Scrape pagina principal
def _scrape_placsp(html: str) -> dict:
    """
    Parsea el HTML de la pagina principal.
    Busca enlaces a pliegos y adjudicacion.
    """
    pass

# Parse HTML adjudicacion
def _parse_html_adjudicacion(html: str) -> dict:
    """
    Extrae datos del HTML de adjudicacion.
    Usa regex para buscar secciones especificas.
    """
    pass
```

### Regex de Extraccion

```python
# Limpiar HTML
texto = re.sub(r'<[^>]+>', ' ', html)
texto = re.sub(r'\s+', ' ', texto)

# Buscar seccion Adjudicatario
adj_pattern = r'Adjudicatario\s+(.{200,500}?)\s+(?:Direccion|Contacto)'
match = re.search(adj_pattern, texto, re.I | re.S)

# Extraer email
email_pattern = r'Correo\s+Electr[oó]nico[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
email_match = re.search(email_pattern, texto, re.I)

# Extraer telefono
tel_pattern = r'Tel[eé]fono[:\s]+([+\d\s\-\.]+)'
tel_match = re.search(tel_pattern, texto, re.I)

# Extraer importes
importe_pattern = r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(?:€|EUR)'
importes = re.findall(importe_pattern, texto)
```

---

## Apollo.io Integration

### Endpoints Disponibles

| Endpoint | Proposito |
|----------|-----------|
| `POST /apollo/enrich/person` | Enriquece datos de persona por email |
| `POST /apollo/enrich/company` | Enriquece datos de empresa por dominio |
| `POST /apollo/search` | Busca personas en Apollo |
| `POST /leads/{id}/enrich-apollo` | Enriquece lead existente |

### Flujo de Enriquecimiento

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USUARIO SOLICITA ENRIQUECIMIENTO                            │
│                                                                 │
│  - Click "Enriquecer" en LeadModal                              │
│  - Proporciona email del contacto                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. LLAMADA A APOLLO API                                        │
│                                                                 │
│  POST https://api.apollo.io/v1/people/match                     │
│  Headers: { "Api-Key": APOLLO_API_KEY }                         │
│  Body: { "email": "contacto@empresa.com" }                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. RESPUESTA APOLLO                                            │
│                                                                 │
│  {                                                              │
│    "person": {                                                  │
│      "first_name": "Juan",                                     │
│      "last_name": "Perez",                                     │
│      "title": "Director de IT",                                │
│      "linkedin_url": "https://linkedin.com/in/...",            │
│      "phone_numbers": ["+34 600 XXX XXX"],                     │
│      "organization": {                                         │
│        "name": "Empresa S.L.",                                 │
│        "industry": "Information Technology",                   │
│        "estimated_num_employees": 250,                         │
│        "annual_revenue": "10M-50M"                             │
│      }                                                         │
│    }                                                           │
│  }                                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. ACTUALIZACION DEL LEAD                                      │
│                                                                 │
│  Lead actualizado con:                                          │
│  - Telefono directo                                            │
│  - Cargo confirmado                                            │
│  - LinkedIn URL                                                │
│  - Datos de empresa (sector, tamaño)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Implementacion Backend

```python
@api_router.post("/apollo/enrich/person")
async def enrich_person(data: ApolloEnrichRequest):
    """Enriquece datos de persona via Apollo."""

    apollo_url = "https://api.apollo.io/v1/people/match"
    headers = {"Api-Key": APOLLO_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            apollo_url,
            headers=headers,
            json={"email": data.email}
        )

    if response.status_code != 200:
        raise HTTPException(502, "Apollo API error")

    apollo_data = response.json()

    # Mapear a formato interno
    return {
        "nombre": f"{apollo_data['person']['first_name']} {apollo_data['person']['last_name']}",
        "cargo": apollo_data['person'].get('title'),
        "telefono": apollo_data['person'].get('phone_numbers', [None])[0],
        "linkedin": apollo_data['person'].get('linkedin_url'),
        "empresa": {
            "nombre": apollo_data['person']['organization'].get('name'),
            "sector": apollo_data['person']['organization'].get('industry'),
            "empleados": apollo_data['person']['organization'].get('estimated_num_employees')
        }
    }
```

### Rate Limits Apollo

| Plan | Limite |
|------|--------|
| Free | 200 creditos/mes |
| Basic | 2,400 creditos/mes |
| Professional | 10,000 creditos/mes |

**Consumo por operacion:**
- Person match: 1 credito
- Company enrich: 1 credito
- Search: 1 credito por resultado

### Health Check

```bash
curl https://crm.systemrapidsolutions.com:3001/api/apollo/health

# Response:
{
  "status": "ok",
  "credits_remaining": 150
}
```

---

## Troubleshooting

### Email no se extrae de PLACSP

1. Verificar estructura HTML de la pagina
2. El HTML de adjudicacion puede tener formato diferente
3. Revisar regex en `_parse_html_adjudicacion()`

```python
# Debug: imprimir texto limpio
texto = re.sub(r'<[^>]+>', ' ', html)
print(texto[texto.find('Contacto'):texto.find('Contacto')+500])
```

### Apollo no retorna datos

1. Verificar API key valida
2. Email puede no estar en base de datos Apollo
3. Verificar creditos restantes

```bash
curl -X POST https://api.apollo.io/v1/people/match \
  -H "Api-Key: $APOLLO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@empresa.com"}'
```

### Datos incompletos

Apollo puede no tener todos los campos:
- Telefono: ~60% de cobertura
- LinkedIn: ~80% de cobertura
- Cargo: ~90% de cobertura

Siempre validar respuesta y manejar campos opcionales.
