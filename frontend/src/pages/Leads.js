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
  AlertCircle,
  X,
  Trash2,
  UserPlus,
  ArrowRight,
  CheckSquare,
  Square
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import LeadModal from "@/components/LeadModal";
import ImportModal from "@/components/ImportModal";

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
  const [importModalOpen, setImportModalOpen] = useState(false);
  
  // Selection state
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [bulkStageDialogOpen, setBulkStageDialogOpen] = useState(false);
  const [bulkOwnerDialogOpen, setBulkOwnerDialogOpen] = useState(false);
  const [bulkStage, setBulkStage] = useState("");
  const [bulkOwner, setBulkOwner] = useState("");
  const [users, setUsers] = useState([]);

  const fetchLeads = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (stageFilter && stageFilter !== "all") params.append("etapa", stageFilter);
      if (sectorFilter && sectorFilter !== "all") params.append("sector", sectorFilter);

      const response = await axios.get(`${API}/leads?${params.toString()}`, { withCredentials: true });
      setLeads(response.data);
      // Clear selection when leads change
      setSelectedIds(new Set());
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

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`, { withCredentials: true });
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  useEffect(() => {
    fetchLeads();
    fetchSectors();
    fetchUsers();
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

  // Selection handlers
  const toggleSelect = (leadId) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(leadId)) {
        newSet.delete(leadId);
      } else {
        newSet.add(leadId);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === leads.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(leads.map((l) => l.lead_id)));
    }
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
  };

  // Bulk actions
  const handleBulkDelete = async () => {
    try {
      await axios.post(
        `${API}/leads/bulk-delete`,
        { lead_ids: Array.from(selectedIds) },
        { withCredentials: true }
      );
      toast.success(`${selectedIds.size} leads eliminados`);
      setDeleteDialogOpen(false);
      fetchLeads();
    } catch (error) {
      toast.error("Error al eliminar leads");
    }
  };

  const handleBulkStageChange = async () => {
    if (!bulkStage) return;
    
    try {
      await axios.post(
        `${API}/leads/bulk-update`,
        { lead_ids: Array.from(selectedIds), etapa: bulkStage },
        { withCredentials: true }
      );
      toast.success(`${selectedIds.size} leads actualizados`);
      setBulkStageDialogOpen(false);
      setBulkStage("");
      fetchLeads();
    } catch (error) {
      toast.error("Error al actualizar leads");
    }
  };

  const handleBulkOwnerChange = async () => {
    try {
      await axios.post(
        `${API}/leads/bulk-update`,
        { lead_ids: Array.from(selectedIds), propietario: bulkOwner || null },
        { withCredentials: true }
      );
      toast.success(`${selectedIds.size} leads actualizados`);
      setBulkOwnerDialogOpen(false);
      setBulkOwner("");
      fetchLeads();
    } catch (error) {
      toast.error("Error al actualizar leads");
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
  const hasSelection = selectedIds.size > 0;
  const allSelected = leads.length > 0 && selectedIds.size === leads.length;

  return (
    <div data-testid="leads-page" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold theme-text">Leads</h1>
          <p className="theme-text-secondary text-sm">{leads.length} contactos en total</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setImportModalOpen(true)}
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

      {/* Selection Action Bar */}
      {hasSelection && (
        <Card 
          className="p-3 bg-cyan-500/10 border-cyan-500/30 animate-fadeIn"
          data-testid="selection-bar"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckSquare className="w-5 h-5 text-cyan-400" />
              <span className="text-cyan-300 font-medium">
                {selectedIds.size} lead{selectedIds.size > 1 ? "s" : ""} seleccionado{selectedIds.size > 1 ? "s" : ""}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearSelection}
                className="text-cyan-400 hover:text-cyan-300"
              >
                <X className="w-4 h-4 mr-1" />
                Deseleccionar
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setBulkStageDialogOpen(true)}
                className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20"
              >
                <ArrowRight className="w-4 h-4 mr-1" />
                Cambiar etapa
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setBulkOwnerDialogOpen(true)}
                className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20"
              >
                <UserPlus className="w-4 h-4 mr-1" />
                Asignar propietario
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setDeleteDialogOpen(true)}
                className="border-red-500/30 text-red-400 hover:bg-red-500/20"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Eliminar
              </Button>
            </div>
          </div>
        </Card>
      )}

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
          <p className="theme-text-secondary mb-4">
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
        <div className="space-y-2">
          {/* Select all header */}
          <div className="flex items-center gap-3 px-4 py-2">
            <Checkbox
              checked={allSelected}
              onCheckedChange={toggleSelectAll}
              className="border-slate-600 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500"
              data-testid="select-all-checkbox"
            />
            <span className="text-sm theme-text-secondary">
              {allSelected ? "Deseleccionar todos" : "Seleccionar todos"}
            </span>
          </div>

          {/* Lead cards */}
          <div className="grid gap-3">
            {leads.map((lead) => (
              <Card
                key={lead.lead_id}
                className={`theme-bg-secondary p-4 hover:shadow-lg transition-all group ${
                  selectedIds.has(lead.lead_id) ? "ring-2 ring-cyan-500/50" : ""
                }`}
                style={{ border: '1px solid var(--theme-border)' }}
                data-testid={`lead-card-${lead.lead_id}`}
              >
                <div className="flex items-start gap-4">
                  {/* Checkbox */}
                  <div 
                    className="pt-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleSelect(lead.lead_id);
                    }}
                  >
                    <Checkbox
                      checked={selectedIds.has(lead.lead_id)}
                      onCheckedChange={() => toggleSelect(lead.lead_id)}
                      className="border-slate-600 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500"
                    />
                  </div>

                  {/* Lead content */}
                  <div 
                    className="flex-1 min-w-0 cursor-pointer"
                    onClick={() => openModal(lead)}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold theme-text truncate">{lead.empresa}</h3>
                      <Badge 
                        className={`${stageConfig[lead.etapa]?.className || "stage-nuevo"} text-xs`}
                      >
                        {stageConfig[lead.etapa]?.label || lead.etapa}
                      </Badge>
                      {lead.dias_sin_actividad > 7 && lead.etapa !== "ganado" && lead.etapa !== "perdido" && (
                        <Badge variant="outline" className="border-amber-500 text-amber-500 text-xs">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          {lead.dias_sin_actividad}d sin actividad
                        </Badge>
                      )}
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-2 text-sm">
                      <div className="flex items-center gap-2 theme-text-secondary">
                        <User className="w-4 h-4" />
                        <span className="truncate">{lead.contacto}</span>
                      </div>
                      <div className="flex items-center gap-2 theme-text-secondary">
                        <Mail className="w-4 h-4" />
                        <span className="truncate">{lead.email}</span>
                      </div>
                      {lead.telefono && (
                        <div className="flex items-center gap-2 theme-text-secondary">
                          <Phone className="w-4 h-4" />
                          <span>{lead.telefono}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2 font-medium" style={{ color: 'var(--theme-currency)' }}>
                        <Euro className="w-4 h-4" />
                        <span>{formatCurrency(lead.valor_estimado)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 transition-opacity theme-text-secondary"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="theme-bg-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                      <DropdownMenuItem 
                        onClick={(e) => {
                          e.stopPropagation();
                          openModal(lead);
                        }}
                        className="theme-text-secondary focus:theme-text"
                      >
                        Editar
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(lead.lead_id);
                        }}
                        className="text-red-500 focus:text-red-600 focus:bg-red-500/10"
                      >
                        Eliminar
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Lead Modal */}
      <LeadModal
        open={modalOpen}
        onClose={closeModal}
        lead={selectedLead}
      />

      {/* Import Modal */}
      <ImportModal
        open={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        onSuccess={fetchLeads}
      />

      {/* Bulk Delete Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-900 border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">¿Eliminar {selectedIds.size} leads?</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Esta acción no se puede deshacer. Los leads seleccionados y su historial de actividades serán eliminados permanentemente.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-white/10 text-slate-300 hover:bg-slate-800">
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleBulkDelete}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Eliminar {selectedIds.size} leads
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Bulk Stage Change Dialog */}
      <AlertDialog open={bulkStageDialogOpen} onOpenChange={setBulkStageDialogOpen}>
        <AlertDialogContent className="bg-slate-900 border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Cambiar etapa de {selectedIds.size} leads</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Selecciona la nueva etapa para los leads seleccionados.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="py-4">
            <Select value={bulkStage} onValueChange={setBulkStage}>
              <SelectTrigger className="bg-slate-950 border-slate-800">
                <SelectValue placeholder="Seleccionar etapa" />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-800">
                {Object.entries(stageConfig).map(([key, config]) => (
                  <SelectItem key={key} value={key}>{config.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-white/10 text-slate-300 hover:bg-slate-800">
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleBulkStageChange}
              disabled={!bulkStage}
              className="btn-gradient"
            >
              Aplicar cambio
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Bulk Owner Change Dialog */}
      <AlertDialog open={bulkOwnerDialogOpen} onOpenChange={setBulkOwnerDialogOpen}>
        <AlertDialogContent className="bg-slate-900 border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Asignar propietario a {selectedIds.size} leads</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Selecciona el propietario para los leads seleccionados.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="py-4">
            <Select value={bulkOwner} onValueChange={setBulkOwner}>
              <SelectTrigger className="bg-slate-950 border-slate-800">
                <SelectValue placeholder="Seleccionar propietario" />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-800">
                <SelectItem value="">Sin asignar</SelectItem>
                {users.map((u) => (
                  <SelectItem key={u.user_id} value={u.user_id}>{u.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-white/10 text-slate-300 hover:bg-slate-800">
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleBulkOwnerChange}
              className="btn-gradient"
            >
              Aplicar cambio
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
