# Analisis con IA

## Modulos

| Modulo | Proposito |
|--------|-----------|
| `pain_analyzer.py` | Analisis rapido sin PDF (~10 segundos) |
| `pliego_analyzer.py` | Analisis de PDF con IA (~2 minutos) |
| `analisis_comercial.py` | Orquestacion del analisis completo |
| `modelos_analisis.py` | Estructuras Pydantic de salida |

---

## Pain Analyzer (Analisis Rapido)

### Proposito
Generar un score rapido de la oportunidad sin necesidad de descargar y analizar el PDF del pliego.

### Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT                                                          │
│  - oportunidad_id                                               │
│  - objeto (descripcion del contrato)                           │
│  - cpv                                                         │
│  - importe                                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  ANALISIS CON IA (fallback chain)                               │
│                                                                 │
│  1. Intenta Claude (Anthropic)                                  │
│  2. Si falla → Gemini (Google)                                  │
│  3. Si falla → OpenAI                                           │
│  4. Si falla → Analisis basico (regex + heuristicas)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                         │
│  {                                                              │
│    "pain_score": 75,                                           │
│    "nivel_urgencia": "alto",                                   │
│    "componentes_detectados": ["Cableado", "Soporte IT"],       │
│    "probabilidad_subcontratacion": "media",                    │
│    "tecnologias": ["Cisco", "VMware"],                         │
│    "zonas_cobertura": ["Madrid", "Andalucia"]                  │
│  }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Criterios de Scoring

```python
# Puntuacion base por palabras clave
scoring_keywords = {
    "urgente": +15,
    "critico": +15,
    "inmediato": +15,
    "24x7": +10,
    "24/7": +10,
    "ens": +12,
    "iso 27001": +12,
    "certificacion": +10,
    "multisede": +10,
    "nacional": +10,
    "infraestructura critica": +20,
    "mantenimiento": +8,
    "soporte": +8,
    "instalacion": +8
}

# Bonus por CPV
cpv_bonus = {
    "72": 25,  # Servicios IT
    "48": 20,  # Software
    "32": 20,  # Telecomunicaciones
    "50": 15,  # Mantenimiento
}
```

### Analisis Basico (Fallback)

Cuando ninguna IA esta disponible:

```python
def analisis_basico(objeto: str, cpv: str) -> dict:
    """Analisis sin IA usando heuristicas."""

    score = 0
    componentes = []
    objeto_lower = objeto.lower()

    # Detectar componentes
    if "cableado" in objeto_lower:
        componentes.append("Cableado estructurado")
        score += 15

    if "soporte" in objeto_lower or "mantenimiento" in objeto_lower:
        componentes.append("Soporte IT")
        score += 12

    if "instalacion" in objeto_lower:
        componentes.append("Instalacion equipos")
        score += 10

    # Detectar urgencia
    urgencia = "bajo"
    if any(kw in objeto_lower for kw in ["urgente", "critico", "inmediato"]):
        urgencia = "alto"
        score += 15

    # CPV bonus
    for prefix, bonus in cpv_bonus.items():
        if cpv.startswith(prefix):
            score += bonus
            break

    return {
        "pain_score": min(100, score),
        "nivel_urgencia": urgencia,
        "componentes_detectados": componentes,
        "probabilidad_subcontratacion": "media" if score > 50 else "baja"
    }
```

---

## Pliego Analyzer (Analisis PDF)

### Proposito
Extraer informacion detallada del PDF del pliego tecnico usando IA.

### Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DESCARGA PDF                                                │
│                                                                 │
│  - URL desde PLACSP                                            │
│  - Manejo de certificados SSL                                  │
│  - Timeout: 30 segundos                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. EXTRACCION TEXTO                                            │
│                                                                 │
│  - Libreria: pdfplumber                                        │
│  - Pagina por pagina                                           │
│  - Limpieza de caracteres especiales                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. CHUNKING                                                    │
│                                                                 │
│  - Dividir en chunks de max 20KB                               │
│  - Preservar contexto entre chunks                             │
│  - Priorizar primeras paginas (suelen tener lo importante)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. ANALISIS CON CLAUDE                                         │
│                                                                 │
│  Modelo: claude-opus-4-5-20251101                                 │
│  Prompt: estructurado para extraer informacion especifica      │
│  Max tokens: 4096                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. OUTPUT ESTRUCTURADO                                         │
│                                                                 │
│  - Certificaciones requeridas                                  │
│  - SLAs y penalizaciones                                       │
│  - Personal minimo                                             │
│  - Equipamiento especifico                                     │
│  - Zonas geograficas                                           │
│  - Requisitos de solvencia                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Prompt de Extraccion

```python
PROMPT_PLIEGO = """
Analiza el siguiente extracto del pliego tecnico de una licitacion publica.

EXTRACTO:
{texto_pliego}

Extrae la siguiente informacion en formato JSON:

{
  "certificaciones_requeridas": [
    {"nombre": "ISO 27001", "obligatoria": true}
  ],
  "slas": [
    {"metrica": "Tiempo respuesta", "valor": "4 horas", "penalizacion": "5% factura"}
  ],
  "personal_requerido": {
    "minimo": 5,
    "perfiles": ["Tecnico nivel 2", "Coordinador"]
  },
  "equipamiento": ["Herramientas certificadas", "Vehiculo propio"],
  "zonas_geograficas": ["Madrid", "Barcelona", "Valencia"],
  "duracion_contrato": {
    "meses": 24,
    "prorrogable": true,
    "meses_prorroga": 12
  },
  "presupuesto_licitacion": 500000.00
}

Solo incluye informacion que encuentres explicitamente en el texto.
"""
```

---

## Analisis Comercial (Orquestador)

### Proposito
Combinar todas las fuentes de datos y generar el analisis completo para el comercial.

### Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT                                                          │
│  - oportunidad_id                                               │
│  - url_pliego (opcional)                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
┌───────────────────┐ ┌───────────────┐ ┌───────────────────┐
│ Adjudicatario     │ │ Pliego        │ │ Catalogo SRS      │
│ Enricher          │ │ Analyzer      │ │ (servicios)       │
│                   │ │               │ │                   │
│ - Datos empresa   │ │ - Requisitos  │ │ - Matching        │
│ - Email/telefono  │ │ - SLAs        │ │ - Cobertura       │
│ - Importes        │ │ - Personal    │ │ - Precios ref.    │
└───────────────────┘ └───────────────┘ └───────────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROMPT ESTRUCTURADO → CLAUDE                                   │
│                                                                 │
│  Incluye:                                                      │
│  - Contexto SRS (pilares, zonas, clientes referencia)          │
│  - Datos del adjudicatario                                     │
│  - Extracto del pliego                                         │
│  - Catalogo de servicios SRS                                   │
│  - Estructura JSON esperada                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT: AnalisisComercial                                      │
│                                                                 │
│  - oportunidad: datos basicos                                  │
│  - adjudicatario: empresa ganadora                             │
│  - cliente_final: organismo contratante                        │
│  - componentes_it[]: tecnologias detectadas                    │
│  - dolores[]: pain points identificados                        │
│  - requisitos_solvencia: economica + tecnica                   │
│  - alertas[]: riesgos y oportunidades                          │
│  - resumen_operador: lo mas importante para el comercial       │
└─────────────────────────────────────────────────────────────────┘
```

### ResumenOperador (Output Clave)

```python
class ResumenOperador(BaseModel):
    # Clasificacion
    nivel_oportunidad: str  # "A", "B", "C", "D"
    score_total: int        # 0-100

    # Desglose del score
    score_desglose: ScoreDesglose  # {
        # alineacion_servicios: 0-25,
        # urgencia_temporal: 0-20,
        # volumen_economico: 0-15,
        # dolor_detectado: 0-20,
        # cobertura_geografica: 0-10,
        # probabilidad_subcontratacion: 0-10
    # }

    # Dolor principal
    dolor_principal: Dolor

    # Pitch de 30 segundos
    en_30_segundos: En30Segundos  # {
        # que_es: "Contrato de...",
        # por_que_interesa: "Necesitan...",
        # por_que_ahora: "Plazo de..."
    # }

    # Servicios que aplican
    servicios_aplicables: List[ServicioSRSAplicable]

    # Mensajes de apertura
    gancho_inicial: GanchoInicial  # {
        # whatsapp: "Hola, vi que...",
        # email: "Asunto:...",
        # llamada: "Script..."
    # }

    # Objeciones probables
    objeciones: List[ObjecionRespuesta]

    # Siguiente paso
    siguiente_accion: str
    fecha_limite_contacto: Optional[datetime]
```

---

## Proveedores IA

### Jerarquia de Fallback

```
1. Claude (Anthropic) - Principal
   ├── Modelo: claude-opus-4-5-20251101
   ├── Max tokens: 4096
   └── Uso: Analisis completo, mejor calidad

2. Gemini (Google) - Fallback 1
   ├── Modelo: gemini-pro
   ├── Max tokens: 4096
   └── Uso: Si Claude no disponible

3. OpenAI - Fallback 2
   ├── Modelo: gpt-4-turbo
   ├── Max tokens: 4096
   └── Uso: Si Gemini no disponible

4. Analisis basico - Fallback 3
   └── Heuristicas + regex, sin IA
```

### Configuracion

```python
# En .env
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=xxx
OPENAI_API_KEY=sk-xxx

# Prioridad configurable
AI_PROVIDER_ORDER=["anthropic", "google", "openai", "basic"]
```

### Costes Estimados

| Proveedor | Modelo | Input | Output |
|-----------|--------|-------|--------|
| Anthropic | Claude Opus 4.5 | $15/1M | $75/1M |
| Google | Gemini Pro | $0.50/1M | $1.50/1M |
| OpenAI | GPT-4 Turbo | $10/1M | $30/1M |

**Coste por analisis completo:**
- Claude: ~$0.10-0.30
- Gemini: ~$0.01-0.03
- OpenAI: ~$0.05-0.15

---

## Troubleshooting

### Claude no responde

```bash
# Verificar API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-opus-4-5-20251101","max_tokens":10,"messages":[{"role":"user","content":"Test"}]}'
```

### PDF no se descarga

1. Verificar URL accesible
2. Algunos PDFs requieren certificado FNMT
3. Timeout puede ser muy corto

```python
# Aumentar timeout
response = requests.get(url, timeout=60, verify=False)
```

### Respuesta JSON mal formada

1. Claude a veces incluye texto extra
2. Limpiar respuesta antes de parsear:

```python
import json
import re

def limpiar_json(texto):
    # Buscar JSON en la respuesta
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found")
```

### Score muy bajo/alto

1. Revisar prompt (puede estar sesgado)
2. Verificar que datos de entrada estan completos
3. Ajustar pesos en ScoreDesglose
