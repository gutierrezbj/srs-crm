import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { 
  Plus, 
  Search, 
  Upload, 
  Download, 
  MoreVertical,
  Building2,
  Mail,
  Phone,
  User,
  Euro,
  Calendar,
  AlertCircle,
  Filter,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import LeadModal from "@/components/LeadModal";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const stageConfig = {
  nuevo: { label: "Nuevo", className: "stage-nuevo" },
  contactado: { label: "Contactado", className: "stage-contactado" },
  calificado: { label: "Calificado", className: "stage-calificado" },
  propuesta: { label: "Propuesta", className: "stage-propuesta" },
  negociacion: { label: "Negociación", className: "stage-negociacion" },
  ganado: { label: "Ganado", className: "stage-ganado" },
  perdido: { label: "Perdido", className: "stage-perdido" },
};

export default function Leads({ user }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [stageFilter, setStageFilter] = useState("all");
  const [sectorFilter, setSectorFilter] = useState("all");
  const [sectors, setSectors] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);

  const fetchLeads = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (stageFilter && stageFilter !== "all") params.append("etapa", stageFilter);
      if (sectorFilter && sectorFilter !== "all") params.append("sector", sectorFilter);

      const response = await axios.get(`${API}/leads?${params.toString()}`, { withCredentials: true });
      setLeads(response.data);
    } catch (error) {
      toast.error("Error al cargar leads");
      console.error("Error fetching leads:", error);
    } finally {
      setLoading(false);
    }
  }, [search, stageFilter, sectorFilter]);

  const fetchSectors = async () => {
    try {
      const response = await axios.get(`${API}/sectors`, { withCredentials: true });
      setSectors(response.data);
    } catch (error) {
      console.error("Error fetching sectors:", error);
    }
  };

  useEffect(() => {
    fetchLeads();
    fetchSectors();
  }, [fetchLeads]);

  const handleExport = async () => {
    try {
      const response = await axios.get(`${API}/leads/export`, {
        withCredentials: true,
        responseType: "blob",
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "leads_export.csv");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Leads exportados correctamente");
    } catch (error) {
      toast.error("Error al exportar leads");
    }
  };

  const handleImport = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API}/leads/import`, formData, {
        withCredentials: true,
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success(`${response.data.imported} leads importados`);
      if (response.data.errors?.length > 0) {
        toast.warning(`${response.data.errors.length} errores encontrados`);
      }
      fetchLeads();
    } catch (error) {
      toast.error("Error al importar leads");
    }
    
    event.target.value = "";
  };

  const handleDelete = async (leadId) => {
    if (!window.confirm("¿Eliminar este lead?")) return;
    
    try {
      await axios.delete(`${API}/leads/${leadId}`, { withCredentials: true });
      toast.success("Lead eliminado");
      fetchLeads();
    } catch (error) {
      toast.error("Error al eliminar lead");
    }
  };

  const openModal = (lead = null) => {
    setSelectedLead(lead);
    setModalOpen(true);
  };

  const closeModal = () => {
    setSelectedLead(null);
    setModalOpen(false);
    fetchLeads();
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const clearFilters = () => {
    setSearch("");
    setStageFilter("all");
    setSectorFilter("all");
  };

  const hasFilters = search || stageFilter !== "all" || sectorFilter !== "all";

  return (
    <div data-testid="leads-page" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold theme-text">Leads</h1>
          <p className="theme-text-secondary text-sm">{leads.length} contactos en total</p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="file"
            id="import-file"
            accept=".csv,.xlsx,.xls"
            onChange={handleImport}
            className="hidden"
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => document.getElementById("import-file")?.click()}
            data-testid="import-btn"
            className="theme-text-secondary hover:theme-text"
            style={{ borderColor: 'var(--theme-border)' }}
          >
            <Upload className="w-4 h-4 mr-2" />
            Importar
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
            data-testid="export-btn"
            className="theme-text-secondary hover:theme-text"
            style={{ borderColor: 'var(--theme-border)' }}
          >
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
          <Button
            onClick={() => openModal()}
            data-testid="new-lead-btn"
            className="btn-gradient"
          >
            <Plus className="w-4 h-4 mr-2" />
            Nuevo Lead
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="theme-bg-secondary p-4" style={{ border: '1px solid var(--theme-border)' }}>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 theme-text-muted" />
            <Input
              placeholder="Buscar por empresa, contacto o email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              data-testid="search-input"
              className="pl-10 theme-bg-tertiary"
              style={{ borderColor: 'var(--theme-border)' }}
            />
          </div>
          <div className="flex gap-2">
            <Select value={stageFilter} onValueChange={setStageFilter}>
              <SelectTrigger 
                className="w-[150px] theme-bg-tertiary"
                style={{ borderColor: 'var(--theme-border)' }}
                data-testid="stage-filter"
              >
                <SelectValue placeholder="Etapa" />
              </SelectTrigger>
              <SelectContent className="theme-bg-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                <SelectItem value="all">Todas las etapas</SelectItem>
                {Object.entries(stageConfig).map(([key, config]) => (
                  <SelectItem key={key} value={key}>{config.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={sectorFilter} onValueChange={setSectorFilter}>
              <SelectTrigger 
                className="w-[150px] theme-bg-tertiary"
                style={{ borderColor: 'var(--theme-border)' }}
                data-testid="sector-filter"
              >
                <SelectValue placeholder="Sector" />
              </SelectTrigger>
              <SelectContent className="theme-bg-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                <SelectItem value="all">Todos los sectores</SelectItem>
                {sectors.map((sector) => (
                  <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {hasFilters && (
              <Button
                variant="ghost"
                size="icon"
                onClick={clearFilters}
                className="theme-text-secondary hover:theme-text"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Leads List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div style={{ color: 'var(--theme-accent)' }} className="animate-pulse">Cargando leads...</div>
        </div>
      ) : leads.length === 0 ? (
        <Card className="theme-bg-secondary p-12 text-center" style={{ border: '1px solid var(--theme-border)' }}>
          <Building2 className="w-12 h-12 mx-auto mb-4 theme-text-muted" />
          <h3 className="text-lg font-medium theme-text mb-2">No hay leads</h3>
          <p className="text-slate-400 mb-4">
            {hasFilters ? "No se encontraron leads con los filtros aplicados" : "Comienza añadiendo tu primer lead"}
          </p>
          {!hasFilters && (
            <Button onClick={() => openModal()} className="btn-gradient">
              <Plus className="w-4 h-4 mr-2" />
              Añadir Lead
            </Button>
          )}
        </Card>
      ) : (
        <div className="grid gap-4">
          {leads.map((lead) => (
            <Card
              key={lead.lead_id}
              className="bg-slate-900/50 border-white/5 p-4 hover:border-cyan-400/20 transition-colors cursor-pointer group"
              onClick={() => openModal(lead)}
              data-testid={`lead-card-${lead.lead_id}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-white truncate">{lead.empresa}</h3>
                    <Badge 
                      className={`${stageConfig[lead.etapa]?.color || "bg-slate-500"} text-white text-xs`}
                    >
                      {stageConfig[lead.etapa]?.label || lead.etapa}
                    </Badge>
                    {lead.dias_sin_actividad > 7 && lead.etapa !== "ganado" && lead.etapa !== "perdido" && (
                      <Badge variant="outline" className="border-amber-400/50 text-amber-400 text-xs">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        {lead.dias_sin_actividad}d sin actividad
                      </Badge>
                    )}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-2 text-sm">
                    <div className="flex items-center gap-2 text-slate-400">
                      <User className="w-4 h-4" />
                      <span className="truncate">{lead.contacto}</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-400">
                      <Mail className="w-4 h-4" />
                      <span className="truncate">{lead.email}</span>
                    </div>
                    {lead.telefono && (
                      <div className="flex items-center gap-2 text-slate-400">
                        <Phone className="w-4 h-4" />
                        <span>{lead.telefono}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-cyan-400 font-medium">
                      <Euro className="w-4 h-4" />
                      <span>{formatCurrency(lead.valor_estimado)}</span>
                    </div>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-slate-900 border-slate-800">
                    <DropdownMenuItem 
                      onClick={(e) => {
                        e.stopPropagation();
                        openModal(lead);
                      }}
                      className="text-slate-300 focus:text-white focus:bg-slate-800"
                    >
                      Editar
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(lead.lead_id);
                      }}
                      className="text-red-400 focus:text-red-300 focus:bg-red-400/10"
                    >
                      Eliminar
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Lead Modal */}
      <LeadModal
        open={modalOpen}
        onClose={closeModal}
        lead={selectedLead}
      />
    </div>
  );
}
