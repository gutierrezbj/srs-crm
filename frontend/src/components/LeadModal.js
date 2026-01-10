import { useState, useEffect } from "react";
import axios from "axios";
import { 
  Building2, 
  User, 
  Mail, 
  Phone, 
  Briefcase, 
  Tag, 
  Euro, 
  FileText,
  Plus,
  Clock,
  MessageSquare,
  PhoneCall,
  Calendar,
  UserCircle,
  Zap,
  Target,
  AlertTriangle,
  CalendarClock
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const stages = [
  { value: "nuevo", label: "Nuevo" },
  { value: "contactado", label: "Contactado" },
  { value: "calificado", label: "Calificado" },
  { value: "propuesta", label: "Propuesta" },
  { value: "negociacion", label: "Negociación" },
  { value: "ganado", label: "Ganado" },
  { value: "perdido", label: "Perdido" },
];

const activityTypes = [
  { value: "nota", label: "Nota", icon: MessageSquare },
  { value: "llamada", label: "Llamada", icon: PhoneCall },
  { value: "email", label: "Email", icon: Mail },
  { value: "reunion", label: "Reunión", icon: Calendar },
];

const initialFormState = {
  empresa: "",
  contacto: "",
  email: "",
  telefono: "",
  cargo: "",
  sector: "",
  valor_estimado: 0,
  etapa: "nuevo",
  notas: "",
  propietario: "",
  servicios: [],
  fuente: "",
  urgencia: "Sin definir",
  motivo_perdida: "",
  proximo_seguimiento: "",
  tipo_seguimiento: "",
};

export default function LeadModal({ open, onClose, lead }) {
  const [formData, setFormData] = useState(initialFormState);
  const [activities, setActivities] = useState([]);
  const [newActivity, setNewActivity] = useState({ tipo: "nota", descripcion: "" });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("info");
  const [options, setOptions] = useState({});
  const [users, setUsers] = useState([]);

  const isEditing = !!lead;

  useEffect(() => {
    fetchOptions();
    fetchUsers();
  }, []);

  useEffect(() => {
    if (lead) {
      setFormData({
        empresa: lead.empresa || "",
        contacto: lead.contacto || "",
        email: lead.email || "",
        telefono: lead.telefono || "",
        cargo: lead.cargo || "",
        sector: lead.sector || "",
        valor_estimado: lead.valor_estimado || 0,
        etapa: lead.etapa || "nuevo",
        notas: lead.notas || "",
        propietario: lead.propietario || "",
        servicios: lead.servicios || [],
        fuente: lead.fuente || "",
        urgencia: lead.urgencia || "Sin definir",
        motivo_perdida: lead.motivo_perdida || "",
        proximo_seguimiento: lead.proximo_seguimiento ? lead.proximo_seguimiento.split("T")[0] : "",
        tipo_seguimiento: lead.tipo_seguimiento || "",
      });
      fetchActivities(lead.lead_id);
    } else {
      setFormData(initialFormState);
      setActivities([]);
    }
    setActiveTab("info");
  }, [lead, open]);

  const fetchOptions = async () => {
    try {
      const response = await axios.get(`${API}/options`, { withCredentials: true });
      setOptions(response.data);
    } catch (error) {
      console.error("Error fetching options:", error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`, { withCredentials: true });
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const fetchActivities = async (leadId) => {
    try {
      const response = await axios.get(`${API}/leads/${leadId}/activities`, { withCredentials: true });
      setActivities(response.data);
    } catch (error) {
      console.error("Error fetching activities:", error);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleServiceToggle = (service) => {
    setFormData((prev) => {
      const current = prev.servicios || [];
      if (current.includes(service)) {
        return { ...prev, servicios: current.filter((s) => s !== service) };
      } else {
        return { ...prev, servicios: [...current, service] };
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const dataToSend = {
        ...formData,
        proximo_seguimiento: formData.proximo_seguimiento ? new Date(formData.proximo_seguimiento).toISOString() : null,
      };

      if (isEditing) {
        await axios.put(`${API}/leads/${lead.lead_id}`, dataToSend, { withCredentials: true });
        toast.success("Lead actualizado");
      } else {
        await axios.post(`${API}/leads`, dataToSend, { withCredentials: true });
        toast.success("Lead creado");
      }
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al guardar lead");
    } finally {
      setLoading(false);
    }
  };

  const handleAddActivity = async () => {
    if (!newActivity.descripcion.trim()) {
      toast.error("Añade una descripción");
      return;
    }

    try {
      await axios.post(
        `${API}/leads/${lead.lead_id}/activities`,
        newActivity,
        { withCredentials: true }
      );
      toast.success("Actividad añadida");
      setNewActivity({ tipo: "nota", descripcion: "" });
      fetchActivities(lead.lead_id);
    } catch (error) {
      toast.error("Error al añadir actividad");
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("es-ES", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getActivityIcon = (tipo) => {
    const activity = activityTypes.find((a) => a.value === tipo);
    const Icon = activity?.icon || MessageSquare;
    return <Icon className="w-4 h-4" />;
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-slate-900 border-white/10 max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-cyan-400" />
            {isEditing ? "Editar Lead" : "Nuevo Lead"}
          </DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-slate-800 border-white/5">
            <TabsTrigger value="info" className="data-[state=active]:bg-slate-700">
              Información
            </TabsTrigger>
            <TabsTrigger value="details" className="data-[state=active]:bg-slate-700">
              Detalles
            </TabsTrigger>
            {isEditing && (
              <TabsTrigger value="activity" className="data-[state=active]:bg-slate-700">
                Actividad
              </TabsTrigger>
            )}
          </TabsList>

          {/* Info Tab - Basic fields */}
          <TabsContent value="info" className="mt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Building2 className="w-4 h-4" />
                    Empresa *
                  </Label>
                  <Input
                    value={formData.empresa}
                    onChange={(e) => handleChange("empresa", e.target.value)}
                    required
                    data-testid="lead-empresa"
                    className="bg-slate-950 border-slate-800 focus:border-cyan-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Contacto *
                  </Label>
                  <Input
                    value={formData.contacto}
                    onChange={(e) => handleChange("contacto", e.target.value)}
                    required
                    data-testid="lead-contacto"
                    className="bg-slate-950 border-slate-800 focus:border-cyan-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    Email *
                  </Label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange("email", e.target.value)}
                    required
                    data-testid="lead-email"
                    className="bg-slate-950 border-slate-800 focus:border-cyan-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    Teléfono
                  </Label>
                  <Input
                    value={formData.telefono}
                    onChange={(e) => handleChange("telefono", e.target.value)}
                    data-testid="lead-telefono"
                    className="bg-slate-950 border-slate-800 focus:border-cyan-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Briefcase className="w-4 h-4" />
                    Cargo
                  </Label>
                  <Input
                    value={formData.cargo}
                    onChange={(e) => handleChange("cargo", e.target.value)}
                    data-testid="lead-cargo"
                    className="bg-slate-950 border-slate-800 focus:border-cyan-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <UserCircle className="w-4 h-4" />
                    Propietario
                  </Label>
                  <Select
                    value={formData.propietario}
                    onValueChange={(value) => handleChange("propietario", value)}
                  >
                    <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="lead-propietario">
                      <SelectValue placeholder="Seleccionar..." />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      <SelectItem value="">Sin asignar</SelectItem>
                      {users.map((user) => (
                        <SelectItem key={user.user_id} value={user.user_id}>
                          {user.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Euro className="w-4 h-4" />
                    Valor Estimado (EUR)
                  </Label>
                  <Input
                    type="number"
                    min="0"
                    step="100"
                    value={formData.valor_estimado}
                    onChange={(e) => handleChange("valor_estimado", parseFloat(e.target.value) || 0)}
                    data-testid="lead-valor"
                    className="bg-slate-950 border-slate-800 focus:border-cyan-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Etapa</Label>
                  <Select
                    value={formData.etapa}
                    onValueChange={(value) => handleChange("etapa", value)}
                  >
                    <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="lead-etapa">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      {stages.map((stage) => (
                        <SelectItem key={stage.value} value={stage.value}>
                          {stage.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Notas
                </Label>
                <Textarea
                  value={formData.notas}
                  onChange={(e) => handleChange("notas", e.target.value)}
                  placeholder="Información adicional..."
                  data-testid="lead-notas"
                  className="bg-slate-950 border-slate-800 focus:border-cyan-400 min-h-[80px]"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  className="border-white/10 text-slate-300 hover:bg-slate-800"
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  data-testid="lead-submit"
                  className="btn-gradient"
                >
                  {loading ? "Guardando..." : isEditing ? "Guardar Cambios" : "Crear Lead"}
                </Button>
              </div>
            </form>
          </TabsContent>

          {/* Details Tab - New fields */}
          <TabsContent value="details" className="mt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Tag className="w-4 h-4" />
                    Sector
                  </Label>
                  <Select
                    value={formData.sector}
                    onValueChange={(value) => handleChange("sector", value)}
                  >
                    <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="lead-sector">
                      <SelectValue placeholder="Seleccionar..." />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      {options.sectores?.map((sector) => (
                        <SelectItem key={sector} value={sector}>
                          {sector}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    Fuente del Lead
                  </Label>
                  <Select
                    value={formData.fuente}
                    onValueChange={(value) => handleChange("fuente", value)}
                  >
                    <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="lead-fuente">
                      <SelectValue placeholder="Seleccionar..." />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      {options.fuentes?.map((fuente) => (
                        <SelectItem key={fuente} value={fuente}>
                          {fuente}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Urgencia
                  </Label>
                  <Select
                    value={formData.urgencia}
                    onValueChange={(value) => handleChange("urgencia", value)}
                  >
                    <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="lead-urgencia">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      {options.urgencias?.map((urg) => (
                        <SelectItem key={urg} value={urg}>
                          {urg}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                {formData.etapa === "perdido" && (
                  <div className="space-y-2">
                    <Label className="text-slate-300 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                      Motivo de Pérdida
                    </Label>
                    <Select
                      value={formData.motivo_perdida}
                      onValueChange={(value) => handleChange("motivo_perdida", value)}
                    >
                      <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="lead-motivo-perdida">
                        <SelectValue placeholder="Seleccionar..." />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-800">
                        {options.motivos_perdida?.map((motivo) => (
                          <SelectItem key={motivo} value={motivo}>
                            {motivo}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>

              {/* Próximo Seguimiento */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300 flex items-center gap-2">
                    <CalendarClock className="w-4 h-4" />
                    Próximo Seguimiento
                  </Label>
                  <Input
                    type="date"
                    value={formData.proximo_seguimiento}
                    onChange={(e) => handleChange("proximo_seguimiento", e.target.value)}
                    data-testid="lead-proximo-seguimiento"
                    className="bg-slate-950 border-slate-800 focus:border-cyan-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Tipo de Acción</Label>
                  <Select
                    value={formData.tipo_seguimiento}
                    onValueChange={(value) => handleChange("tipo_seguimiento", value)}
                  >
                    <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="lead-tipo-seguimiento">
                      <SelectValue placeholder="Seleccionar..." />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      {options.tipos_seguimiento?.map((tipo) => (
                        <SelectItem key={tipo} value={tipo}>
                          {tipo}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Servicios de Interés */}
              <div className="space-y-3">
                <Label className="text-slate-300 flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Servicios de Interés
                </Label>
                <div className="grid grid-cols-2 gap-2 p-3 bg-slate-950 rounded-lg border border-slate-800">
                  {options.servicios?.map((servicio) => (
                    <label
                      key={servicio}
                      className="flex items-center gap-2 cursor-pointer hover:bg-slate-900 p-2 rounded"
                    >
                      <Checkbox
                        checked={formData.servicios?.includes(servicio)}
                        onCheckedChange={() => handleServiceToggle(servicio)}
                        className="border-slate-600 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500"
                      />
                      <span className="text-sm text-slate-300">{servicio}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  className="border-white/10 text-slate-300 hover:bg-slate-800"
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  data-testid="lead-submit-details"
                  className="btn-gradient"
                >
                  {loading ? "Guardando..." : "Guardar Cambios"}
                </Button>
              </div>
            </form>
          </TabsContent>

          {/* Activity Tab */}
          {isEditing && (
            <TabsContent value="activity" className="mt-4 space-y-4">
              {/* Add Activity */}
              <div className="bg-slate-800/50 rounded-lg p-4 space-y-3">
                <Label className="text-slate-300">Añadir Actividad</Label>
                <div className="flex gap-2">
                  <Select
                    value={newActivity.tipo}
                    onValueChange={(value) => setNewActivity((prev) => ({ ...prev, tipo: value }))}
                  >
                    <SelectTrigger className="w-32 bg-slate-950 border-slate-800">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      {activityTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Descripción..."
                    value={newActivity.descripcion}
                    onChange={(e) => setNewActivity((prev) => ({ ...prev, descripcion: e.target.value }))}
                    className="flex-1 bg-slate-950 border-slate-800"
                    data-testid="activity-input"
                  />
                  <Button
                    type="button"
                    onClick={handleAddActivity}
                    data-testid="add-activity-btn"
                    className="btn-gradient"
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Activity Timeline */}
              <div className="space-y-3">
                <Label className="text-slate-300 flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Historial
                </Label>
                {activities.length === 0 ? (
                  <div className="text-center py-8 text-slate-500">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>Sin actividades registradas</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {activities.map((activity) => (
                      <div
                        key={activity.activity_id}
                        className="flex gap-3 p-3 bg-slate-800/30 rounded-lg"
                        data-testid={`activity-${activity.activity_id}`}
                      >
                        <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-cyan-400">
                          {getActivityIcon(activity.tipo)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-white text-sm">
                              {activity.user_name}
                            </span>
                            <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                              {activityTypes.find((t) => t.value === activity.tipo)?.label || activity.tipo}
                            </Badge>
                          </div>
                          <p className="text-sm text-slate-300">{activity.descripcion}</p>
                          <p className="text-xs text-slate-500 mt-1">
                            {formatDate(activity.created_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </TabsContent>
          )}
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
