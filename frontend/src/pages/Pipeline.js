import { useState, useEffect } from "react";
import axios from "axios";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { 
  Users, 
  Phone, 
  CheckCircle2, 
  FileText, 
  Handshake, 
  Trophy, 
  XCircle,
  Euro,
  AlertCircle,
  GripVertical,
  UserCircle
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import LeadModal from "@/components/LeadModal";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const stages = [
  { id: "nuevo", label: "Nuevo", icon: Users, borderColor: "#64748b", headerClass: "kanban-header-nuevo" },
  { id: "contactado", label: "Contactado", icon: Phone, borderColor: "#2563eb", headerClass: "kanban-header-contactado" },
  { id: "calificado", label: "Calificado", icon: CheckCircle2, borderColor: "#0891b2", headerClass: "kanban-header-calificado" },
  { id: "propuesta", label: "Propuesta", icon: FileText, borderColor: "#7c3aed", headerClass: "kanban-header-propuesta" },
  { id: "negociacion", label: "Negociación", icon: Handshake, borderColor: "#d97706", headerClass: "kanban-header-negociacion" },
  { id: "ganado", label: "Ganado", icon: Trophy, borderColor: "#059669", headerClass: "kanban-header-ganado" },
  { id: "perdido", label: "Perdido", icon: XCircle, borderColor: "#dc2626", headerClass: "kanban-header-perdido" },
];

export default function Pipeline({ user }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API}/leads`, { withCredentials: true });
      setLeads(response.data);
    } catch (error) {
      toast.error("Error al cargar leads");
      console.error("Error fetching leads:", error);
    } finally {
      setLoading(false);
    }
  };

  const getLeadsByStage = (stageId) => {
    return leads.filter((lead) => lead.etapa === stageId);
  };

  const handleDragEnd = async (result) => {
    const { destination, source, draggableId } = result;

    // No destination or same position
    if (!destination) return;
    if (destination.droppableId === source.droppableId && destination.index === source.index) return;

    const newStage = destination.droppableId;
    const leadId = draggableId;

    // Find the lead being moved
    const movedLead = leads.find((l) => l.lead_id === leadId);
    if (!movedLead) return;

    // Optimistic update
    setLeads((prevLeads) =>
      prevLeads.map((lead) =>
        lead.lead_id === leadId ? { ...lead, etapa: newStage } : lead
      )
    );

    try {
      await axios.patch(
        `${API}/leads/${leadId}/stage?etapa=${newStage}`,
        {},
        { withCredentials: true }
      );
      
      const stageLabel = stages.find(s => s.id === newStage)?.label || newStage;
      toast.success(`${movedLead.empresa} → ${stageLabel}`);
    } catch (error) {
      // Revert on error
      setLeads((prevLeads) =>
        prevLeads.map((lead) =>
          lead.lead_id === leadId ? { ...lead, etapa: source.droppableId } : lead
        )
      );
      toast.error("Error al actualizar etapa");
      console.error("Error updating stage:", error);
    }
  };

  const openModal = (lead) => {
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

  const getStageTotal = (stageId) => {
    return getLeadsByStage(stageId).reduce((sum, lead) => sum + (lead.valor_estimado || 0), 0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div style={{ color: 'var(--theme-accent)' }} className="animate-pulse">Cargando pipeline...</div>
      </div>
    );
  }

  return (
    <div data-testid="pipeline-page" className="h-full">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold theme-text">Pipeline</h1>
        <p className="theme-text-secondary text-sm">Arrastra los leads entre etapas</p>
      </div>

      {/* Kanban Board */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4" style={{ minHeight: "calc(100vh - 220px)" }}>
          {stages.map((stage) => {
            const stageLeads = getLeadsByStage(stage.id);
            const stageTotal = getStageTotal(stage.id);
            const Icon = stage.icon;

            return (
              <div
                key={stage.id}
                className="flex-shrink-0 w-72 flex flex-col"
                data-testid={`pipeline-column-${stage.id}`}
              >
                {/* Column Header */}
                <div 
                  className={`rounded-t-xl p-4 ${stage.headerClass}`}
                  style={{ borderTop: `4px solid ${stage.borderColor}` }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4 theme-text" />
                      <span className="font-semibold theme-text text-sm">{stage.label}</span>
                    </div>
                    <Badge variant="secondary" className="theme-bg-secondary theme-text" style={{ border: '1px solid var(--theme-border)' }}>
                      {stageLeads.length}
                    </Badge>
                  </div>
                  {stage.id !== "perdido" && (
                    <div className="text-xs" style={{ color: 'var(--theme-currency)' }}>
                      {formatCurrency(stageTotal)}
                    </div>
                  )}
                </div>

                {/* Droppable Area */}
                <Droppable droppableId={stage.id}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`flex-1 theme-bg-tertiary border theme-border border-t-0 rounded-b-xl p-2 transition-colors ${
                        snapshot.isDraggingOver ? "bg-cyan-400/5 border-cyan-400/20" : ""
                      }`}
                      style={{ minHeight: "200px" }}
                    >
                      {stageLeads.length === 0 ? (
                        <div className="text-center py-8 theme-text-muted text-sm">
                          Sin leads
                        </div>
                      ) : (
                        stageLeads.map((lead, index) => (
                          <Draggable
                            key={lead.lead_id}
                            draggableId={lead.lead_id}
                            index={index}
                          >
                            {(provided, snapshot) => (
                              <div
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                onClick={() => openModal(lead)}
                                className={`mb-2 ${snapshot.isDragging ? "opacity-90" : ""}`}
                                data-testid={`pipeline-card-${lead.lead_id}`}
                              >
                                <Card className={`theme-bg-secondary border theme-border p-3 cursor-pointer hover:border-cyan-400/30 transition-all group ${
                                  snapshot.isDragging ? "shadow-xl shadow-cyan-400/10 ring-2 ring-cyan-400/30" : ""
                                }`}>
                                  <div className="flex items-start gap-2">
                                    <div
                                      {...provided.dragHandleProps}
                                      className="mt-1 theme-text-muted opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing"
                                    >
                                      <GripVertical className="w-4 h-4" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-center justify-between mb-1">
                                        <h4 className="font-medium theme-text text-sm truncate">
                                          {lead.empresa}
                                        </h4>
                                        {lead.dias_sin_actividad > 7 && stage.id !== "ganado" && stage.id !== "perdido" && (
                                          <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                                        )}
                                      </div>
                                      <p className="text-xs theme-text-secondary truncate mb-2">
                                        {lead.contacto}
                                      </p>
                                      
                                      {/* Propietario */}
                                      {lead.propietario_nombre && (
                                        <div className="flex items-center gap-1 mb-2">
                                          <UserCircle className="w-3 h-3 text-cyan-400" />
                                          <span className="text-xs text-cyan-400">{lead.propietario_nombre}</span>
                                        </div>
                                      )}
                                      
                                      <div className="flex items-center justify-between">
                                        <span className="text-xs font-medium text-cyan-400">
                                          {formatCurrency(lead.valor_estimado)}
                                        </span>
                                        {lead.dias_sin_actividad > 0 && (
                                          <span className={`text-xs ${
                                            lead.dias_sin_actividad > 7 ? "text-amber-400" : "theme-text-muted"
                                          }`}>
                                            {lead.dias_sin_actividad}d
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                </Card>
                              </div>
                            )}
                          </Draggable>
                        ))
                      )}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            );
          })}
        </div>
      </DragDropContext>

      {/* Lead Modal */}
      <LeadModal
        open={modalOpen}
        onClose={closeModal}
        lead={selectedLead}
      />
    </div>
  );
}
