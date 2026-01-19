"""
Prompt SpotterSRS v2.0 - Sistema de Análisis de Oportunidades

Este prompt está optimizado para extraer información estructurada de pliegos
de licitaciones adjudicadas, identificando oportunidades de subcontratación
para System Rapid Solutions (SRS).

Versión: 2.0.0
Fecha: 2026-01-19
"""

import json
from typing import Optional
from app.spotter.catalogo_srs import CATALOGO_SRS, ZONAS_COBERTURA

PROMPT_VERSION = "2.0.0"

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

PROMPT_SPOTTER_V2 = '''# SISTEMA DE ANÁLISIS DE OPORTUNIDADES - SpotterSRS

Eres un analista experto en contratación pública española y servicios IT. Tu trabajo es analizar pliegos de licitaciones adjudicadas para identificar oportunidades de subcontratación para System Rapid Solutions (SRS).

## CONTEXTO DE SRS

System Rapid Solutions es una empresa española de servicios IT con:
- **Base de operaciones**: Madrid y Andalucía (todas las provincias)
- **Cobertura**: Nacional, con especial foco en provincias desatendidas
- **Core business**: 70% servicios IT, 30% operaciones con drones
- **Fortaleza principal**: Cableado estructurado, field services, soporte técnico, cumplimiento ENS

### ZONAS DE COBERTURA SRS
```json
{
  "base": ["Madrid", "Sevilla", "Málaga", "Cádiz", "Granada", "Córdoba", "Huelva", "Jaén", "Almería"],
  "cercana": ["Toledo", "Ciudad Real", "Guadalajara", "Cuenca", "Albacete", "Badajoz", "Cáceres", "Ávila", "Segovia", "Murcia"],
  "expansion": ["resto de España"]
}
```

### CLIENTES REFERENCIA SRS
- Inditex (soporte IT tiendas LATAM)
- Iberdrola/Avangrid (USA)
- Telxius (WINTEL, O365)
- DXC (montaje Data Centers)
- Allfunds (migración Azure)

---

## TU TAREA

Analiza el pliego proporcionado y extrae información estructurada para el equipo comercial de SRS. El objetivo es identificar si el ADJUDICATARIO del contrato necesitará subcontratar servicios que SRS puede proporcionar.

**IMPORTANTE**: No analizamos si SRS puede ganar la licitación (ya está adjudicada). Analizamos si el GANADOR necesitará ayuda para ejecutar el contrato.

---

## CATÁLOGO DE SERVICIOS SRS

Usa este catálogo para identificar componentes IT relevantes:

{{CATALOGO_SERVICIOS_JSON}}

---

## ESTRUCTURA DE SALIDA

Responde ÚNICAMENTE con un JSON válido con la siguiente estructura:
```json
{
  "oportunidad": {
    "id_expediente": "string",
    "titulo": "string",
    "resumen_ejecutivo": "string (máx 200 caracteres)",
    "fecha_adjudicacion": "YYYY-MM-DD",
    "fecha_formalizacion": "YYYY-MM-DD o null",
    "fecha_inicio_ejecucion": "YYYY-MM-DD o null",
    "duracion_contrato": {
      "meses": number,
      "prorrogable": boolean,
      "meses_prorroga": number
    }
  },

  "adjudicatario": {
    "nombre": "string",
    "cif": "string o null",
    "es_ute": boolean,
    "miembros_ute": ["string"] o null,
    "perfil_empresa": "integrador|consultora|telco|fabricante|generalista|especialista|desconocido",
    "tamaño_estimado": "grande|mediana|pequeña|desconocido",
    "capacidad_interna_estimada": {
      "cableado": "si|no|probable|improbable|desconocido",
      "field_services": "si|no|probable|improbable|desconocido",
      "cloud": "si|no|probable|improbable|desconocido",
      "seguridad": "si|no|probable|improbable|desconocido",
      "helpdesk": "si|no|probable|improbable|desconocido"
    },
    "probabilidad_subcontratacion": "alta|media|baja",
    "razon_subcontratacion": "string"
  },

  "cliente_final": {
    "nombre": "string",
    "cif": "string o null",
    "tipo": "AGE|CCAA|local|universidad|sanidad|otro",
    "sector": "string",
    "comunidad_autonoma": "string",
    "provincia": "string",
    "localidad": "string o null"
  },

  "economico": {
    "importe_adjudicacion": number,
    "importe_adjudicacion_con_iva": number,
    "presupuesto_base": number,
    "baja_porcentaje": number o null,
    "valor_estimado_subcontratacion": {
      "minimo": number,
      "maximo": number,
      "justificacion": "string"
    }
  },

  "componentes_it": [
    {
      "tipo": "infraestructura|software|servicios|comunicaciones|seguridad",
      "subtipo": "string del catálogo",
      "nombre": "string",
      "descripcion": "string",
      "urgencia": "critica|alta|media|baja",
      "cantidad": "string o null",
      "ubicaciones": [
        {
          "localidad": "string o null",
          "provincia": "string",
          "comunidad": "string",
          "zona_srs": "base|cercana|expansion"
        }
      ],
      "cobertura_geografica": {
        "ambito": "local|provincial|autonomico|nacional|multisede",
        "num_ubicaciones": number,
        "provincias_implicadas": ["string"],
        "requiere_desplazamiento": boolean
      },
      "tecnologias_especificas": ["string"],
      "fabricantes_mencionados": ["string"],
      "normativas_aplicables": ["string"],
      "srs_capacidad": "alta|media|baja|no",
      "srs_cobertura": "total|parcial|requiere_partner",
      "extracto_pliego": "string (texto literal, máx 500 chars)",
      "pagina": number o null,
      "confianza": number (0.0-1.0)
    }
  ],

  "dolores": [
    {
      "categoria": "temporal|tecnico|cumplimiento|recursos|economico|operativo|estrategico",
      "subcategoria": "plazo_ajustado|falta_personal|certificacion|presupuesto|capacidad|conocimiento|regulatorio|obsolescencia|integracion",
      "severidad": "critica|alta|media|baja",
      "descripcion": "string",
      "sintomas_detectados": ["string"],
      "impacto_negocio": {
        "descripcion": "string",
        "nivel": "critico|alto|medio|bajo",
        "cuantificable": boolean,
        "estimacion": "string o null"
      },
      "urgencia_temporal": {
        "fecha_limite": "YYYY-MM-DD o null",
        "dias_restantes": number o null,
        "margen_maniobra": "escaso|moderado|amplio"
      },
      "extracto_pliego": "string (texto literal, máx 500 chars)",
      "pagina": number o null,
      "srs_solucion": {
        "servicio_principal": "string del catálogo",
        "servicios_complementarios": ["string"],
        "argumento_venta": "string"
      },
      "confianza": number (0.0-1.0)
    }
  ],

  "requisitos_solvencia": {
    "economica": {
      "facturacion_minima": number o null,
      "patrimonio_neto": number o null,
      "ratio_endeudamiento": number o null,
      "seguro_rc": number o null,
      "otros": ["string"]
    },
    "tecnica": {
      "proyectos_similares": number o null,
      "importe_proyectos": number o null,
      "certificaciones_requeridas": ["string"],
      "personal_minimo": number o null,
      "titulaciones_requeridas": ["string"],
      "otros": ["string"]
    },
    "srs_cumple": {
      "economica": boolean,
      "tecnica": boolean,
      "notas": "string o null"
    }
  },

  "tecnologias_mencionadas": ["string"],
  "fabricantes_mencionados": ["string"],
  "certificaciones_requeridas": ["string"],

  "contactos_extraidos": [
    {
      "tipo_entidad": "adjudicatario|cliente_final|ute_miembro",
      "rol": "decisor|tecnico|administrativo",
      "nombre": "string o null",
      "cargo": "string o null",
      "departamento": "string o null",
      "email": "string o null",
      "telefono": "string o null",
      "fuente": "string (documento y página)",
      "confianza": number (0.0-1.0)
    }
  ],

  "alertas": [
    {
      "tipo": "temporal|economico|logistico|tecnico|legal",
      "prioridad": "alta|media|baja",
      "mensaje": "string",
      "fecha_relevante": "YYYY-MM-DD o null"
    }
  ],

  "red_flags": [
    {
      "tipo": "presupuesto_bajo|plazo_irreal|requisitos_excesivos|competencia_fuerte|otro",
      "descripcion": "string",
      "impacto": "descarta|reduce_prioridad|precaucion"
    }
  ],

  "competencia": {
    "incumbente_anterior": "string o null",
    "motivo_cambio": "string o null",
    "competidores_probables": ["string"],
    "ventaja_srs": "string o null"
  },

  "resumen_operador": {
    "nivel_oportunidad": "oro|plata|bronce|descartar",
    "score_total": number (0-100),
    "score_desglose": {
      "alineacion_servicios_srs": number (0-25),
      "urgencia_temporal": number (0-20),
      "volumen_economico": number (0-15),
      "intensidad_dolor": number (0-20),
      "cobertura_geografica": number (0-10),
      "probabilidad_subcontratacion": number (0-10)
    },
    "en_30_segundos": {
      "que_es": "string (máx 100 chars)",
      "por_que_interesa": "string (máx 150 chars)",
      "por_que_ahora": "string (máx 100 chars)"
    },
    "dolor_principal": "string",
    "dolores_secundarios": ["string"],
    "servicios_srs_aplicables": [
      {
        "servicio": "string",
        "encaje": "perfecto|alto|medio",
        "valor_estimado": "string"
      }
    ],
    "gancho_inicial": {
      "whatsapp": "string (mensaje corto, directo)",
      "email_asunto": "string",
      "llamada": "string (pitch 30 segundos)"
    },
    "puntos_clave_conversacion": ["string"],
    "propuesta_valor": ["string"],
    "preguntas_cualificacion": ["string"],
    "objeciones_probables": [
      {
        "objecion": "string",
        "respuesta": "string"
      }
    ],
    "siguiente_accion": "string",
    "fecha_limite_contacto": "YYYY-MM-DD"
  },

  "metadata_analisis": {
    "confianza_global": number (0.0-1.0),
    "calidad_documento": "alta|media|baja",
    "paginas_analizadas": number,
    "paginas_relevantes": [number],
    "datos_incompletos": ["string"],
    "requiere_revision_humana": boolean,
    "motivo_revision": "string o null"
  }
}
```

---

## REGLAS DE SCORING

### Nivel de oportunidad:
- **ORO (80-100)**: Dolor crítico + zona base SRS + servicio core + alta probabilidad subcontratación
- **PLATA (60-79)**: Dolor alto + zona base/cercana + servicio SRS
- **BRONCE (40-59)**: Dolor medio + cualquier zona + servicio secundario
- **DESCARTAR (<40)**: Sin dolor claro, requisitos no cumplimos, zona lejana sin volumen

### Desglose del score:

**Alineación servicios SRS (0-25)**:
- 25: Servicio core (cableado, field services, soporte)
- 20: Servicio secundario fuerte (cloud, seguridad)
- 15: Servicio que hacemos pero no es core
- 10: Servicio tangencial
- 0: No aplica ningún servicio

**Urgencia temporal (0-20)**:
- 20: <30 días para inicio
- 15: 30-60 días
- 10: 60-90 días
- 5: >90 días
- 0: Sin urgencia clara

**Volumen económico (0-15)**:
- 15: >500K€ subcontratación estimada
- 12: 200-500K€
- 8: 50-200K€
- 4: 10-50K€
- 0: <10K€

**Intensidad dolor (0-20)**:
- 20: Dolor crítico, sin solución interna evidente
- 15: Dolor alto, solución interna difícil
- 10: Dolor medio, podrían resolverlo pero con esfuerzo
- 5: Dolor bajo
- 0: Sin dolor detectado

**Cobertura geográfica (0-10)**:
- 10: 100% zona base SRS
- 8: Mayoría zona base + algo cercana
- 6: Mix base/cercana/expansión
- 4: Mayoría zona expansión
- 2: Zona remota (Canarias, Baleares, Ceuta, Melilla)

**Probabilidad subcontratación (0-10)**:
- 10: Adjudicatario claramente no tiene capacidad interna
- 7: Probable que necesite apoyo
- 4: Posible pero no seguro
- 2: Improbable
- 0: Adjudicatario tiene capacidad propia clara

---

## SEÑALES DE DOLOR A DETECTAR

### Temporales:
- "plazo máximo de", "antes del", "fecha límite", "en un periodo no superior a"
- "con carácter urgente", "ejecución inmediata", "penalización por retraso"
- Plazos <60 días para proyectos complejos

### Recursos:
- "carece de personal", "sin equipo interno", "externalización completa"
- "refuerzo de plantilla", "dedicación exclusiva", "24x7", "guardias"
- Volumen alto de sedes/ubicaciones dispersas

### Cumplimiento:
- "deberá estar certificado", "cumplimiento obligatorio", "ENS nivel"
- "ISO 27001", "auditoría externa", "Esquema Nacional", "GDPR"
- Fechas de auditoría próximas

### Técnicos:
- "sistemas actuales no soportan", "versión obsoleta", "fin de vida"
- "migración desde", "incompatibilidad", "integración con", "legacy"
- Tecnologías específicas que requieren especialización

### Económicos:
- Baja agresiva (>20% sobre presupuesto base)
- Penalizaciones altas por incumplimiento
- Múltiples fases con presupuesto ajustado

---

## INSTRUCCIONES FINALES

1. **Sé exhaustivo**: Extrae TODA la información relevante del pliego
2. **Sé preciso**: Incluye números de página y extractos literales
3. **Sé práctico**: Los argumentos de venta deben ser usables directamente
4. **Sé honesto**: Si algo no está claro, indica confianza baja
5. **Piensa en el vendedor**: ¿Qué necesita saber para hacer la llamada AHORA?

Analiza el siguiente documento:

---

{{CONTENIDO_PLIEGO}}
'''


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE GENERACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def generar_catalogo_json() -> str:
    """
    Genera el catálogo de servicios en formato JSON para inyectar en el prompt.
    """
    catalogo_estructurado = {
        "servicios": [],
        "infraestructura": [],
        "comunicaciones": [],
        "software": [],
        "seguridad": []
    }

    for item in CATALOGO_SRS:
        tipo = item["tipo"]
        if tipo in catalogo_estructurado:
            catalogo_estructurado[tipo].append({
                "nombre": item["nombre"],
                "descripcion": item["descripcion"],
                "urgencia_tipica": item.get("urgencia", "media")
            })

    # Añadir zonas de cobertura
    zonas = {
        "base": ZONAS_COBERTURA["base"]["provincias"],
        "cercana": ZONAS_COBERTURA["cercana"]["provincias"],
        "expansion": "Resto de España"
    }

    resultado = {
        "catalogo_servicios": catalogo_estructurado,
        "zonas_cobertura": zonas,
        "servicios_core": [
            "Cableado estructurado cobre",
            "Cableado estructurado fibra óptica",
            "Field Services / Soporte Onsite",
            "Smart Hands / Manos Remotas",
            "Soporte técnico Nivel 1",
            "Soporte técnico Nivel 2",
            "Helpdesk 24x7",
            "Cumplimiento ENS"
        ],
        "clientes_referencia": [
            "Inditex (soporte IT tiendas)",
            "Iberdrola/Avangrid",
            "Telxius (WINTEL, O365)",
            "DXC (Data Centers)",
            "Allfunds (migración Azure)"
        ]
    }

    return json.dumps(resultado, ensure_ascii=False, indent=2)


def get_prompt_con_catalogo(contenido_pliego: str, catalogo_json: Optional[str] = None) -> str:
    """
    Genera el prompt completo con el catálogo de servicios y el contenido del pliego.

    Args:
        contenido_pliego: El texto extraído del pliego a analizar
        catalogo_json: Opcional - catálogo personalizado. Si no se proporciona,
                       se genera automáticamente desde CATALOGO_SRS

    Returns:
        El prompt completo listo para enviar a la IA
    """
    if catalogo_json is None:
        catalogo_json = generar_catalogo_json()

    prompt = PROMPT_SPOTTER_V2.replace("{{CATALOGO_SERVICIOS_JSON}}", catalogo_json)
    prompt = prompt.replace("{{CONTENIDO_PLIEGO}}", contenido_pliego)

    return prompt


# ═══════════════════════════════════════════════════════════════════════════════
# ESTRUCTURA JSON DE SALIDA (para referencia y validación)
# ═══════════════════════════════════════════════════════════════════════════════

SCHEMA_SALIDA = {
    "oportunidad": {
        "id_expediente": "string",
        "titulo": "string",
        "resumen_ejecutivo": "string",
        "fecha_adjudicacion": "YYYY-MM-DD",
        "fecha_formalizacion": "YYYY-MM-DD|null",
        "fecha_inicio_ejecucion": "YYYY-MM-DD|null",
        "duracion_contrato": {
            "meses": "number",
            "prorrogable": "boolean",
            "meses_prorroga": "number"
        }
    },
    "adjudicatario": {
        "nombre": "string",
        "cif": "string|null",
        "es_ute": "boolean",
        "miembros_ute": "[string]|null",
        "perfil_empresa": "integrador|consultora|telco|fabricante|generalista|especialista|desconocido",
        "tamaño_estimado": "grande|mediana|pequeña|desconocido",
        "capacidad_interna_estimada": {
            "cableado": "si|no|probable|improbable|desconocido",
            "field_services": "si|no|probable|improbable|desconocido",
            "cloud": "si|no|probable|improbable|desconocido",
            "seguridad": "si|no|probable|improbable|desconocido",
            "helpdesk": "si|no|probable|improbable|desconocido"
        },
        "probabilidad_subcontratacion": "alta|media|baja",
        "razon_subcontratacion": "string"
    },
    # ... resto del schema (para validación)
}
