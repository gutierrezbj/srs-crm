# Modelos de Datos

## Colecciones MongoDB

### users
Usuarios del sistema.

```javascript
{
  _id: ObjectId,
  user_id: String,         // Google ID
  email: String,           // Unique
  name: String,
  picture: String,         // URL avatar
  role: String,            // "admin" | "user"
  created_at: DateTime,
  last_login: DateTime
}
```

**Indices:**
```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ user_id: 1 })
```

---

### user_sessions
Sesiones activas.

```javascript
{
  _id: ObjectId,
  session_id: String,      // UUID
  user_id: String,
  email: String,
  created_at: DateTime,
  expires_at: DateTime     // 24h desde creacion
}
```

**Indices:**
```javascript
db.user_sessions.createIndex({ session_id: 1 }, { unique: true })
db.user_sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 })
```

---

### leads
Leads CRM.

```javascript
{
  _id: ObjectId,

  // Datos de contacto
  empresa: String,         // Nombre empresa
  contacto: String,        // Nombre persona
  email: String,
  telefono: String,        // Opcional
  cargo: String,           // Opcional

  // Clasificacion
  sector: String,          // Enum: sectores
  servicios: [String],     // Servicios de interes
  fuente: String,          // Enum: fuentes
  urgencia: String,        // Enum: urgencias

  // Comercial
  etapa: String,           // Enum: etapas pipeline
  valor_estimado: Number,  // Euros
  propietario: String,     // user_id asignado
  proximo_seguimiento: DateTime,

  // Notas
  notas: String,

  // Enriquecimiento Apollo
  apollo_data: {
    linkedin: String,
    telefono_directo: String,
    empresa_info: {
      sector: String,
      empleados: Number,
      revenue: String,
      website: String
    }
  },

  // Vinculo con oportunidad PLACSP
  oportunidad_origen: String,  // oportunidad_id

  // Metadata
  created_at: DateTime,
  updated_at: DateTime,
  created_by: String       // user_id
}
```

**Enums:**
```javascript
etapas = ["nuevo", "contactado", "calificado",
          "propuesta", "negociacion", "ganado", "perdido"]

sectores = ["IT/Soporte", "Fotovoltaica", "Drones",
            "Sanidad", "Retail", "Industria", "Otro"]

fuentes = ["Apollo", "Web", "LinkedIn", "Licitacion",
           "Referido", "Evento", "Otro"]

urgencias = ["Inmediata", "Corto plazo", "Medio plazo", "Largo plazo"]
```

**Indices:**
```javascript
db.leads.createIndex({ email: 1 })
db.leads.createIndex({ etapa: 1 })
db.leads.createIndex({ propietario: 1 })
db.leads.createIndex({ created_at: -1 })
db.leads.createIndex({ "$**": "text" })  // Full-text search
```

---

### activities
Historial de actividades por lead.

```javascript
{
  _id: ObjectId,
  lead_id: ObjectId,
  tipo: String,            // Enum: tipos_actividad
  descripcion: String,
  resultado: String,
  fecha: DateTime,
  created_by: String,      // user_id
  created_at: DateTime
}
```

**Enums:**
```javascript
tipos_actividad = ["llamada", "email", "reunion",
                   "demo", "propuesta", "nota"]
```

**Indices:**
```javascript
db.activities.createIndex({ lead_id: 1, fecha: -1 })
```

---

### oportunidades_placsp
Oportunidades de licitaciones publicas.

```javascript
{
  _id: ObjectId,

  // Identificacion PLACSP
  oportunidad_id: String,  // ID expediente (unique)
  expediente: String,      // Numero expediente
  titulo: String,
  objeto: String,          // Descripcion completa
  url_licitacion: String,
  url_pliego_tecnico: String,
  url_pliego_administrativo: String,

  // Fechas
  fecha_publicacion: DateTime,
  fecha_adjudicacion: DateTime,
  dias_restantes: Number,  // Hasta fin contrato

  // Cliente (organismo contratante)
  cliente_nombre: String,
  cliente_sector: String,
  cliente_tipo: String,    // AGE, CCAA, Local, etc.
  cliente_ccaa: String,
  cliente_provincia: String,

  // Adjudicatario (empresa ganadora)
  adjudicatario_nombre: String,
  adjudicatario_nif: String,
  adjudicatario_nombre_comercial: String,
  importe_adjudicacion: Number,
  importe_con_iva: Number,

  // Clasificacion SpotterSRS
  cpv: String,
  tipo_srs: String,        // Enum: TipoOportunidad
  keywords: [String],
  score: Number,           // 0-100
  indicadores_dolor: [String],

  // Datos extraidos HTML adjudicacion
  datos_adjudicatario: {
    nombre: String,
    nif: String,
    es_pyme: Boolean,
    pais_origen: String,
    direccion: {
      calle: String,
      cp: String,
      localidad: String
    },
    contacto: {
      telefono: String,
      email: String
    },
    importes: {
      sin_impuestos: Number,
      con_impuestos: Number
    },
    motivacion: {
      razon: String,
      fecha_acuerdo: String
    },
    ofertas: {
      recibidas: Number,
      pymes: Number,
      precio_bajo: Number,
      precio_alto: Number
    }
  },

  // Analisis rapido
  analisis_rapido: {
    pain_score: Number,
    nivel_urgencia: String,
    componentes_detectados: [String],
    probabilidad_subcontratacion: String,
    tecnologias: [String],
    zonas_cobertura: [String],
    timestamp: DateTime
  },

  // Analisis completo (ver AnalisisComercial)
  analisis_comercial: Object,

  // Empresas competidoras (del Acta)
  empresas_competidoras: [String],
  tiene_componente_it: Boolean,

  // Estado comercial
  estado_revision: String, // Enum: estados_revision
  asignado_a: String,      // user_id
  asignado_nombre: String,
  fecha_asignacion: DateTime,

  // Vinculo con lead creado
  lead_creado: String,     // lead_id

  // Metadata
  created_at: DateTime,
  updated_at: DateTime
}
```

**Enums:**
```javascript
TipoOportunidad = [
  "Infraestructura / CPD",
  "Cloud / Virtualizacion",
  "Ciberseguridad",
  "Comunicaciones Unificadas",
  "Healthcare IT (RIS/PACS)",
  "Fotovoltaica / Energia",
  "Drones / Cartografia",
  "Soporte Internacional",
  "IT Generico",
  "No Relevante"
]

estados_revision = ["sin_revisar", "en_revision",
                    "descartada", "contactado"]
```

**Indices:**
```javascript
db.oportunidades_placsp.createIndex({ oportunidad_id: 1 }, { unique: true })
db.oportunidades_placsp.createIndex({ fecha_adjudicacion: -1 })
db.oportunidades_placsp.createIndex({ tipo_srs: 1 })
db.oportunidades_placsp.createIndex({ score: -1 })
db.oportunidades_placsp.createIndex({ estado_revision: 1 })
db.oportunidades_placsp.createIndex({ asignado_a: 1 })
```

---

## Modelos Pydantic (Analisis)

### AnalisisComercial
Estructura raiz del analisis completo con IA.

```python
class AnalisisComercial(BaseModel):
    # Datos basicos
    oportunidad: Oportunidad
    adjudicatario: Adjudicatario
    cliente_final: ClienteFinal
    economico: DatosEconomicos

    # Analisis detallado
    componentes_it: List[ComponenteIT]
    dolores: List[Dolor]
    requisitos_solvencia: RequisitosSolvencia
    contactos_extraidos: List[ContactoExtraido]

    # Alertas y riesgos
    alertas: List[Alerta]
    red_flags: List[RedFlag]
    competencia: Competencia

    # Resumen para comercial
    resumen_operador: ResumenOperador

    # Metadata
    metadata_analisis: MetadataAnalisisIA
```

### ResumenOperador
Lo mas importante para el comercial.

```python
class ResumenOperador(BaseModel):
    nivel_oportunidad: str        # "A", "B", "C", "D"
    score_total: int              # 0-100
    score_desglose: ScoreDesglose

    dolor_principal: Dolor
    en_30_segundos: En30Segundos

    servicios_aplicables: List[ServicioSRSAplicable]
    gancho_inicial: GanchoInicial
    objeciones: List[ObjecionRespuesta]

    siguiente_accion: str
    fecha_limite_contacto: Optional[datetime]
```

### ScoreDesglose
Desglose del scoring.

```python
class ScoreDesglose(BaseModel):
    alineacion_servicios: int     # 0-25
    urgencia_temporal: int        # 0-20
    volumen_economico: int        # 0-15
    dolor_detectado: int          # 0-20
    cobertura_geografica: int     # 0-10
    probabilidad_subcontratacion: int  # 0-10
```

### ComponenteIT
Componente IT detectado en el pliego.

```python
class ComponenteIT(BaseModel):
    tipo: str           # infraestructura|software|servicios|comunicaciones|seguridad
    nombre: str
    descripcion: str
    urgencia: str       # critico|alto|medio|bajo
    cobertura_srs: str  # total|parcial|ninguna
    confianza: float    # 0.0-1.0
    ubicacion: Optional[UbicacionComponente]
```

### Dolor
Pain point detectado.

```python
class Dolor(BaseModel):
    categoria: str      # temporal|tecnico|cumplimiento|recursos|economico|operativo|estrategico
    subcategoria: str
    descripcion: str
    severidad: str      # critico|alto|medio|bajo
    impacto: ImpactoNegocio
    urgencia: Optional[UrgenciaTemporal]
    solucion_srs: SRSSolucion
```

### GanchoInicial
Mensajes de apertura comercial.

```python
class GanchoInicial(BaseModel):
    whatsapp: str       # Mensaje corto informal
    email: str          # Asunto + cuerpo
    llamada: str        # Script telefónico
```

### Alerta
Alerta detectada en el analisis.

```python
class Alerta(BaseModel):
    tipo: str           # temporal|economico|logistico|tecnico|legal
    mensaje: str
    prioridad: str      # alta|media|baja
```

---

## Relaciones entre Colecciones

```
users
  │
  ├── 1:N → leads (propietario)
  ├── 1:N → activities (created_by)
  └── 1:N → oportunidades_placsp (asignado_a)

leads
  │
  ├── 1:N → activities (lead_id)
  └── N:1 → oportunidades_placsp (oportunidad_origen)

oportunidades_placsp
  │
  └── 1:1 → leads (lead_creado)
```

---

## Migraciones

### Añadir campo nuevo
```python
# En server.py o script separado
await db.oportunidades_placsp.update_many(
    {"nuevo_campo": {"$exists": False}},
    {"$set": {"nuevo_campo": valor_default}}
)
```

### Crear indice
```python
await db.oportunidades_placsp.create_index([("nuevo_campo", 1)])
```

---

## Validacion Pydantic

Ejemplo de modelo con validacion:

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LeadCreate(BaseModel):
    empresa: str = Field(..., min_length=2, max_length=200)
    contacto: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, pattern=r'^\+?[0-9\s\-]+$')
    sector: str
    valor_estimado: Optional[float] = Field(None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "empresa": "Empresa S.L.",
                "contacto": "Juan Perez",
                "email": "juan@empresa.com",
                "sector": "IT/Soporte"
            }
        }
```
