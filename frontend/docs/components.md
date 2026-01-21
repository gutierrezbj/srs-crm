# Componentes Frontend

## Estructura de Componentes

```
src/components/
├── Layout.js              # Layout principal (sidebar + header)
├── LeadModal.js           # Modal crear/editar lead
├── ImportModal.js         # Modal importar desde Excel
└── ui/                    # Componentes shadcn/ui (50+)
    ├── accordion.jsx
    ├── alert.jsx
    ├── badge.jsx
    ├── button.jsx
    ├── card.jsx
    ├── dialog.jsx
    ├── dropdown-menu.jsx
    ├── input.jsx
    ├── select.jsx
    ├── table.jsx
    ├── tabs.jsx
    ├── toast.jsx
    └── ... (50+ componentes)
```

---

## Layout.js

### Proposito
Componente wrapper que proporciona la estructura basica de la aplicacion: sidebar de navegacion y header con usuario.

### Props
| Prop | Tipo | Descripcion |
|------|------|-------------|
| `children` | ReactNode | Contenido de la pagina |

### Estructura

```jsx
<div className="flex h-screen bg-background">
  {/* Sidebar */}
  <aside className="w-64 border-r">
    <Logo />
    <Navigation />
    <UserProfile />
  </aside>

  {/* Main content */}
  <main className="flex-1 overflow-auto">
    <Header />
    {children}
  </main>
</div>
```

### Navegacion

```jsx
const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: Users, label: "Leads", path: "/leads" },
  { icon: Kanban, label: "Pipeline", path: "/pipeline" },
  { icon: Target, label: "Oportunidades", path: "/oportunidades" },
  { icon: BarChart3, label: "Reportes", path: "/reports" },
  { icon: Settings, label: "Admin", path: "/admin", adminOnly: true }
];
```

---

## LeadModal.js

### Proposito
Modal para crear y editar leads del CRM. Incluye enriquecimiento Apollo.

### Props
| Prop | Tipo | Descripcion |
|------|------|-------------|
| `isOpen` | boolean | Controla visibilidad |
| `onClose` | function | Callback al cerrar |
| `lead` | object | Lead a editar (null para crear) |
| `onSave` | function | Callback al guardar |

### Campos del Formulario

```jsx
const fields = [
  // Datos de contacto
  { name: "empresa", label: "Empresa", required: true },
  { name: "contacto", label: "Nombre contacto", required: true },
  { name: "email", label: "Email", type: "email", required: true },
  { name: "telefono", label: "Telefono" },
  { name: "cargo", label: "Cargo" },

  // Clasificacion
  { name: "sector", label: "Sector", type: "select", options: sectores },
  { name: "servicios", label: "Servicios", type: "multiselect" },
  { name: "fuente", label: "Fuente", type: "select", options: fuentes },
  { name: "urgencia", label: "Urgencia", type: "select", options: urgencias },

  // Comercial
  { name: "valor_estimado", label: "Valor estimado", type: "number" },
  { name: "etapa", label: "Etapa", type: "select", options: etapas },
  { name: "propietario", label: "Propietario", type: "select" },
  { name: "proximo_seguimiento", label: "Proximo seguimiento", type: "date" },

  // Notas
  { name: "notas", label: "Notas", type: "textarea" }
];
```

### Enriquecimiento Apollo

```jsx
const handleEnrichApollo = async () => {
  setEnriching(true);
  try {
    const response = await fetch(`/api/apollo/enrich/person`, {
      method: "POST",
      body: JSON.stringify({ email: formData.email })
    });
    const data = await response.json();

    // Actualizar formulario con datos enriquecidos
    setFormData(prev => ({
      ...prev,
      telefono: data.telefono || prev.telefono,
      cargo: data.cargo || prev.cargo,
      apollo_data: data
    }));

    toast.success("Datos enriquecidos correctamente");
  } catch (error) {
    toast.error("Error al enriquecer datos");
  } finally {
    setEnriching(false);
  }
};
```

---

## ImportModal.js

### Proposito
Modal para importar leads desde archivos Excel.

### Props
| Prop | Tipo | Descripcion |
|------|------|-------------|
| `isOpen` | boolean | Controla visibilidad |
| `onClose` | function | Callback al cerrar |
| `onImport` | function | Callback tras importar |

### Flujo de Importacion

```
1. Seleccionar archivo Excel
         │
         ▼
2. Backend parsea y retorna preview
         │
         ▼
3. Usuario mapea columnas
         │
         ▼
4. Verificacion de duplicados
         │
         ▼
5. Importacion final
```

### Mapeo de Columnas

```jsx
const [mapping, setMapping] = useState({});
const [previewData, setPreviewData] = useState([]);
const [excelColumns, setExcelColumns] = useState([]);

const targetFields = [
  { key: "empresa", label: "Empresa", required: true },
  { key: "contacto", label: "Contacto", required: true },
  { key: "email", label: "Email", required: true },
  { key: "telefono", label: "Telefono" },
  { key: "cargo", label: "Cargo" },
  { key: "sector", label: "Sector" },
  { key: "valor_estimado", label: "Valor estimado" },
  { key: "notas", label: "Notas" }
];

// Render mapeo
{excelColumns.map(col => (
  <div key={col}>
    <span>{col}</span>
    <Select
      value={mapping[col]}
      onChange={val => setMapping({...mapping, [col]: val})}
    >
      <option value="">Ignorar</option>
      {targetFields.map(f => (
        <option key={f.key} value={f.key}>{f.label}</option>
      ))}
    </Select>
  </div>
))}
```

---

## Componentes shadcn/ui

### Instalacion

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
# etc.
```

### Componentes Mas Usados

#### Button
```jsx
import { Button } from "@/components/ui/button";

<Button variant="default">Guardar</Button>
<Button variant="outline">Cancelar</Button>
<Button variant="destructive">Eliminar</Button>
<Button variant="ghost" size="icon"><X /></Button>
```

#### Card
```jsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

<Card>
  <CardHeader>
    <CardTitle>Titulo</CardTitle>
  </CardHeader>
  <CardContent>
    Contenido
  </CardContent>
</Card>
```

#### Dialog (Modal)
```jsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from "@/components/ui/dialog";

<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Titulo del modal</DialogTitle>
    </DialogHeader>
    {/* Contenido */}
    <DialogFooter>
      <Button>Guardar</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

#### Table
```jsx
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell
} from "@/components/ui/table";

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Empresa</TableHead>
      <TableHead>Email</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {leads.map(lead => (
      <TableRow key={lead.id}>
        <TableCell>{lead.empresa}</TableCell>
        <TableCell>{lead.email}</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

#### DropdownMenu
```jsx
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem
} from "@/components/ui/dropdown-menu";

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="ghost" size="icon">
      <MoreVertical />
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem onClick={handleEdit}>
      <Edit className="mr-2 h-4 w-4" />
      Editar
    </DropdownMenuItem>
    <DropdownMenuItem onClick={handleDelete} className="text-red-600">
      <Trash className="mr-2 h-4 w-4" />
      Eliminar
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

#### Select
```jsx
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from "@/components/ui/select";

<Select value={sector} onValueChange={setSector}>
  <SelectTrigger>
    <SelectValue placeholder="Seleccionar sector" />
  </SelectTrigger>
  <SelectContent>
    {sectores.map(s => (
      <SelectItem key={s} value={s}>{s}</SelectItem>
    ))}
  </SelectContent>
</Select>
```

#### Tabs
```jsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

<Tabs defaultValue="general">
  <TabsList>
    <TabsTrigger value="general">General</TabsTrigger>
    <TabsTrigger value="actividades">Actividades</TabsTrigger>
  </TabsList>
  <TabsContent value="general">
    Contenido general
  </TabsContent>
  <TabsContent value="actividades">
    Historial de actividades
  </TabsContent>
</Tabs>
```

#### Badge
```jsx
import { Badge } from "@/components/ui/badge";

<Badge>Nuevo</Badge>
<Badge variant="secondary">En progreso</Badge>
<Badge variant="destructive">Urgente</Badge>
<Badge variant="outline">Info</Badge>
```

#### Toast (Notificaciones)
```jsx
import { useToast } from "@/hooks/use-toast";

const { toast } = useToast();

// Usar
toast({
  title: "Lead guardado",
  description: "El lead se ha guardado correctamente"
});

// Con variantes
toast({
  variant: "destructive",
  title: "Error",
  description: "No se pudo guardar"
});
```

---

## Iconos (Lucide React)

```jsx
import {
  LayoutDashboard,
  Users,
  Kanban,
  Target,
  BarChart3,
  Settings,
  Search,
  Plus,
  Edit,
  Trash,
  MoreVertical,
  X,
  Check,
  ChevronDown,
  ExternalLink,
  Mail,
  Phone,
  Building,
  Calendar,
  Clock,
  AlertCircle,
  Info,
  UserCircle
} from "lucide-react";

// Uso
<Search className="h-4 w-4" />
<Plus className="h-5 w-5 mr-2" />
```

---

## Estilos con Tailwind

### Clases Comunes

```jsx
// Layout
"flex items-center justify-between"
"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
"space-y-4"

// Texto
"text-sm text-muted-foreground"
"font-semibold"
"truncate"

// Colores
"bg-primary text-primary-foreground"
"bg-secondary"
"bg-destructive text-destructive-foreground"

// Bordes
"border rounded-lg"
"border-b"

// Hover/Focus
"hover:bg-accent"
"focus:ring-2 focus:ring-ring"

// Responsive
"hidden md:flex"
"w-full lg:w-auto"
```

### Variables CSS (Tema)

```css
/* En globals.css */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96.1%;
  --muted: 210 40% 96.1%;
  --accent: 210 40% 96.1%;
  --destructive: 0 84.2% 60.2%;
  --border: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... */
}
```
