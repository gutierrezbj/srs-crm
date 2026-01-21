# Paginas Frontend

## Estructura de Rutas

```jsx
// App.js
<Routes>
  <Route path="/login" element={<Login />} />

  {/* Rutas protegidas */}
  <Route element={<ProtectedRoute />}>
    <Route path="/" element={<Dashboard />} />
    <Route path="/leads" element={<Leads />} />
    <Route path="/pipeline" element={<Pipeline />} />
    <Route path="/oportunidades" element={<Oportunidades />} />
    <Route path="/reports" element={<Reports />} />
    <Route path="/admin" element={<Admin />} />
  </Route>
</Routes>
```

---

## Login.js

### Proposito
Autenticacion con Google OAuth 2.0.

### Flujo
```
1. Usuario hace click en "Iniciar sesion con Google"
         │
         ▼
2. Google OAuth popup
         │
         ▼
3. Callback con credential (JWT)
         │
         ▼
4. POST /api/auth/session con credential
         │
         ▼
5. Backend verifica y crea sesion
         │
         ▼
6. Redireccion a Dashboard
```

### Implementacion

```jsx
import { GoogleLogin } from "@react-oauth/google";

function Login() {
  const navigate = useNavigate();

  const handleSuccess = async (credentialResponse) => {
    try {
      const response = await fetch("/api/auth/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          credential: credentialResponse.credential
        })
      });

      const data = await response.json();

      if (data.session_id) {
        localStorage.setItem("session_id", data.session_id);
        navigate("/");
      }
    } catch (error) {
      toast.error("Error al iniciar sesion");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-96">
        <CardHeader>
          <img src="/logo.svg" alt="SRS" className="h-12 mx-auto" />
          <CardTitle>SRS CRM</CardTitle>
        </CardHeader>
        <CardContent>
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={() => toast.error("Error de autenticacion")}
          />
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## Dashboard.js

### Proposito
Vista general con KPIs y metricas del pipeline.

### Secciones

```
┌─────────────────────────────────────────────────────────────────┐
│  KPI CARDS                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Total    │ │ Este mes │ │ Pipeline │ │Conversion│           │
│  │ Leads    │ │ Nuevos   │ │ Value    │ │ Rate     │           │
│  │   150    │ │   25     │ │  €500K   │ │  27%     │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
├─────────────────────────────────────────────────────────────────┤
│  GRAFICOS                                                       │
│  ┌─────────────────────────┐ ┌─────────────────────────┐       │
│  │ Leads por Etapa         │ │ Tendencia Mensual       │       │
│  │ [Bar Chart]             │ │ [Line Chart]            │       │
│  └─────────────────────────┘ └─────────────────────────┘       │
├─────────────────────────────────────────────────────────────────┤
│  TABLAS                                                         │
│  ┌─────────────────────────┐ ┌─────────────────────────┐       │
│  │ Por Sector              │ │ Por Fuente              │       │
│  │ IT/Soporte: 45          │ │ Licitacion: 60          │       │
│  │ Fotovoltaica: 30        │ │ Apollo: 40              │       │
│  │ ...                     │ │ ...                     │       │
│  └─────────────────────────┘ └─────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Fetch de Datos

```jsx
useEffect(() => {
  const fetchStats = async () => {
    const response = await fetch("/api/leads/stats", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await response.json();
    setStats(data);
  };
  fetchStats();
}, []);
```

---

## Leads.js

### Proposito
Gestion CRUD de leads del CRM.

### Funcionalidades
- Listado con paginacion
- Busqueda full-text
- Filtros por etapa, sector, propietario
- Acciones: editar, eliminar, cambiar etapa
- Exportacion CSV
- Importacion Excel

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER                                                         │
│  ┌────────────────┐  ┌─────────────────────────────────────────│
│  │ Buscar...      │  │ [Filtros] [Exportar] [Importar] [Nuevo] │
│  └────────────────┘  └─────────────────────────────────────────│
├─────────────────────────────────────────────────────────────────┤
│  TABLA DE LEADS                                                 │
│  ┌─────┬──────────┬───────────┬────────┬────────┬─────────────┐│
│  │ □   │ Empresa  │ Contacto  │ Etapa  │ Valor  │ Acciones    ││
│  ├─────┼──────────┼───────────┼────────┼────────┼─────────────┤│
│  │ □   │ Acme SL  │ Juan P.   │ Nuevo  │ €25K   │ ⋮           ││
│  │ □   │ Tech Co  │ Maria G.  │ Prop.  │ €50K   │ ⋮           ││
│  │ ...                                                         ││
│  └─────┴──────────┴───────────┴────────┴────────┴─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  PAGINACION                                                     │
│  « 1 2 3 ... 10 »                          Mostrando 1-20 de 150│
└─────────────────────────────────────────────────────────────────┘
```

### Estado

```jsx
const [leads, setLeads] = useState([]);
const [total, setTotal] = useState(0);
const [page, setPage] = useState(1);
const [search, setSearch] = useState("");
const [filters, setFilters] = useState({
  etapa: "",
  sector: "",
  propietario: ""
});
const [selectedLeads, setSelectedLeads] = useState([]);
const [isModalOpen, setIsModalOpen] = useState(false);
const [editingLead, setEditingLead] = useState(null);
```

---

## Pipeline.js

### Proposito
Vista Kanban del pipeline comercial.

### Columnas (Etapas)

```jsx
const etapas = [
  { key: "nuevo", label: "Nuevo", color: "bg-blue-100" },
  { key: "contactado", label: "Contactado", color: "bg-yellow-100" },
  { key: "calificado", label: "Calificado", color: "bg-purple-100" },
  { key: "propuesta", label: "Propuesta", color: "bg-orange-100" },
  { key: "negociacion", label: "Negociacion", color: "bg-pink-100" },
  { key: "ganado", label: "Ganado", color: "bg-green-100" },
  { key: "perdido", label: "Perdido", color: "bg-red-100" }
];
```

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  KANBAN BOARD                                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ Nuevo   │ │Contacta-│ │Califica-│ │Propuesta│ │Negocia- │  │
│  │   (5)   │ │ do (8)  │ │ do (3)  │ │  (4)    │ │cion (2) │  │
│  ├─────────┤ ├─────────┤ ├─────────┤ ├─────────┤ ├─────────┤  │
│  │┌───────┐│ │┌───────┐│ │┌───────┐│ │┌───────┐│ │┌───────┐│  │
│  ││ Acme  ││ ││ Tech  ││ ││ Corp  ││ ││ Mega  ││ ││ Giant ││  │
│  ││ €25K  ││ ││ €50K  ││ ││ €30K  ││ ││ €100K ││ ││ €75K  ││  │
│  │└───────┘│ │└───────┘│ │└───────┘│ │└───────┘│ │└───────┘│  │
│  │┌───────┐│ │┌───────┐│ │         │ │         │ │         │  │
│  ││ Beta  ││ ││ Alpha ││ │         │ │         │ │         │  │
│  ││ €15K  ││ ││ €20K  ││ │         │ │         │ │         │  │
│  │└───────┘│ │└───────┘│ │         │ │         │ │         │  │
│  │  ...    │ │  ...    │ │         │ │         │ │         │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Drag & Drop

```jsx
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

const handleDragEnd = async (result) => {
  const { destination, source, draggableId } = result;

  if (!destination) return;
  if (destination.droppableId === source.droppableId) return;

  // Actualizar estado local
  const newLeads = [...leads];
  const leadIndex = newLeads.findIndex(l => l.id === draggableId);
  newLeads[leadIndex].etapa = destination.droppableId;
  setLeads(newLeads);

  // Actualizar en backend
  await fetch(`/api/leads/${draggableId}/stage`, {
    method: "PATCH",
    body: JSON.stringify({ etapa: destination.droppableId })
  });
};
```

---

## Oportunidades.jsx

### Proposito
Gestor de oportunidades PLACSP adjudicadas. Pagina mas compleja del sistema.

### Funcionalidades
- Listado con 30+ columnas
- Filtros avanzados (tipo, score, estado, asignado)
- Analisis rapido y completo
- Conversion a lead
- Asignacion a usuarios

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  FILTROS                                                        │
│  [Tipo SRS ▼] [Score min ▼] [Estado ▼] [Asignado ▼] [Buscar...] │
├─────────────────────────────────────────────────────────────────┤
│  TABLA DE OPORTUNIDADES                                         │
│  ┌────┬────────────┬──────────┬────────┬───────┬──────┬───────┐│
│  │Asig│ Empresa    │ Cliente  │ Tipo   │ Score │Estado│Acciones│
│  ├────┼────────────┼──────────┼────────┼───────┼──────┼───────┤│
│  │ JG │ NTT Data   │ Min.Def. │ Infra  │  85   │ ⬤   │ ▶ ⋮   ││
│  │ -- │ Accenture  │ Sanidad  │ Health │  72   │ ⬤   │ ▶ ⋮   ││
│  │ ...                                                          │
│  └────┴────────────┴──────────┴────────┴───────┴──────┴───────┘│
├─────────────────────────────────────────────────────────────────┤
│  DETALLE EXPANDIDO (al hacer click en fila)                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Objeto: Contrato de mantenimiento de infraestructura...     ││
│  │ Email: spain.proposals@nttdata.com                          ││
│  │ Importe: €1.500.000                                         ││
│  │ Componentes: [Cableado] [Soporte IT] [Backup]               ││
│  │ [Analisis Rapido] [Analisis Completo] [Convertir a Lead]    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Analisis Rapido

```jsx
const handleAnalisisRapido = async (oportunidadId) => {
  setAnalizando(oportunidadId);
  try {
    const response = await fetch("/api/oportunidades/analisis-rapido", {
      method: "POST",
      body: JSON.stringify({
        oportunidad_id: oportunidadId,
        url_licitacion: oportunidad.url_licitacion
      })
    });
    const resultado = await response.json();

    // Actualizar oportunidad local con resultado
    setOportunidades(prev => prev.map(o =>
      o.oportunidad_id === oportunidadId
        ? { ...o, analisis_rapido: resultado }
        : o
    ));

    toast.success("Analisis completado");
  } catch (error) {
    toast.error("Error en analisis");
  } finally {
    setAnalizando(null);
  }
};
```

### Asignacion de Usuario

```jsx
const handleAsignar = async (oportunidadId, usuario) => {
  await fetch(`/api/oportunidades/${oportunidadId}/asignar`, {
    method: "PATCH",
    body: JSON.stringify({
      user_id: usuario?.email || null,
      nombre: usuario?.name || null
    })
  });

  // Actualizar estado local
  setOportunidades(prev => prev.map(o =>
    o.oportunidad_id === oportunidadId
      ? {
          ...o,
          asignado_a: usuario?.email,
          asignado_nombre: usuario?.name
        }
      : o
  ));
};
```

### Abreviaciones de Tipo

```jsx
const abreviarTipoSrs = (tipo) => {
  const abreviaturas = {
    "Fotovoltaica / Energia": "FV",
    "Infraestructura / CPD": "Infra",
    "Cloud / Virtualizacion": "Cloud",
    "Ciberseguridad": "Ciber",
    "Comunicaciones Unificadas": "UC",
    "Healthcare IT (RIS/PACS)": "Health",
    "Drones / Cartografia": "Drones",
    "IT Generico": "IT",
    "Soporte Internacional": "Intl"
  };
  return abreviaturas[tipo] || tipo;
};
```

---

## Reports.js

### Proposito
Reportes y exportacion de datos.

### Tipos de Reportes
- Conversion por periodo
- Pipeline value trending
- Performance por usuario
- Leads por fuente/sector

---

## Admin.js

### Proposito
Panel de administracion (solo rol admin).

### Funcionalidades
- Gestion de usuarios (CRUD)
- Asignacion de roles
- Log de actividad del sistema
- Configuracion general

### Acceso Restringido

```jsx
function Admin() {
  const { user } = useAuth();

  if (user?.role !== "admin") {
    return <Navigate to="/" />;
  }

  return (
    <Layout>
      {/* Contenido admin */}
    </Layout>
  );
}
```
