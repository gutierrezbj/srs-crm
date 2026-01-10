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
  GripVertical
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import LeadModal from "@/components/LeadModal";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const stages = [
  { id: "nuevo", label: "Nuevo", icon: Users, color: "border-slate-500", headerBg: "bg-slate-500/10" },
  { id: "contactado", label: "Contactado", icon: Phone, color: "border-blue-500", headerBg: "bg-blue-500/10" },
  { id: "calificado", label: "Calificado", icon: CheckCircle2, color: "border-cyan-500", headerBg: "bg-cyan-500/10" },
  { id: "propuesta", label: "Propuesta", icon: FileText, color: "border-purple-500", headerBg: "bg-purple-500/10" },
  { id: "negociacion", label: "Negociación", icon: Handshake, color: "border-amber-500", headerBg: "bg-amber-500/10" },
  { id: "ganado", label: "Ganado", icon: Trophy, color: "border-emerald-500", headerBg: "bg-emerald-500/10" },
  { id: "perdido", label: "Perdido", icon: XCircle, color: "border-red-500", headerBg: "bg-red-500/10" },
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

    if (!destination) return;
    if (destination.droppableId === source.droppableId && destination.index === source.index) return;

    const newStage = destination.droppableId;
    const leadId = draggableId;

    // Optimistic update
    setLeads((prev) =>
      prev.map((lead) =>
        lead.lead_id === leadId ? { ...lead, etapa: newStage } : lead
      )
    );

    try {
      await axios.patch(
        `${API}/leads/${leadId}/stage?etapa=${newStage}`,
        {},
        { withCredentials: true }
      );
      toast.success(`Lead movido a ${stages.find(s => s.id === newStage)?.label}`);
    } catch (error) {
      // Revert on error
      fetchLeads();
      toast.error("Error al actualizar etapa");
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
        <div className="text-cyan-400 animate-pulse">Cargando pipeline...</div>
      </div>
    );
  }

  return (
    <div data-testid="pipeline-page" className="h-full">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Pipeline</h1>
        <p className="text-slate-400 text-sm">Arrastra los leads entre etapas</p>
      </div>

      {/* Kanban Board */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4 kanban-column">
          {stages.map((stage) => {
            const stageLeads = getLeadsByStage(stage.id);
            const stageTotal = getStageTotal(stage.id);
            const Icon = stage.icon;

            return (
              <div
                key={stage.id}
                className="flex-shrink-0 w-72"
                data-testid={`pipeline-column-${stage.id}`}
              >
                {/* Column Header */}
                <div className={`rounded-t-xl p-4 ${stage.headerBg} border-t-2 ${stage.color}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4 text-white" />
                      <span className="font-semibold text-white text-sm">{stage.label}</span>
                    </div>
                    <Badge variant="secondary" className="bg-white/10 text-white">
                      {stageLeads.length}
                    </Badge>
                  </div>
                  {stage.id !== "perdido" && (
                    <div className="text-xs text-slate-300">
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
                      className={`bg-slate-900/30 border border-white/5 border-t-0 rounded-b-xl p-2 min-h-[400px] transition-colors ${
                        snapshot.isDraggingOver ? "bg-cyan-400/5 border-cyan-400/20" : ""
                      }`}
                    >
                      {stageLeads.length === 0 ? (
                        <div className="text-center py-8 text-slate-600 text-sm">
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
                                <Card className={`bg-slate-800 border-white/5 p-3 cursor-pointer hover:border-cyan-400/30 transition-all group ${
                                  snapshot.isDragging ? "shadow-xl shadow-cyan-400/10 ring-2 ring-cyan-400/30" : ""
                                }`}>
                                  <div className="flex items-start gap-2">
                                    <div
                                      {...provided.dragHandleProps}
                                      className="mt-1 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                      <GripVertical className="w-4 h-4" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-center justify-between mb-1">
                                        <h4 className="font-medium text-white text-sm truncate">
                                          {lead.empresa}
                                        </h4>
                                        {lead.dias_sin_actividad > 7 && stage.id !== "ganado" && stage.id !== "perdido" && (
                                          <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                                        )}
                                      </div>
                                      <p className="text-xs text-slate-400 truncate mb-2">
                                        {lead.contacto}
                                      </p>
                                      <div className="flex items-center justify-between">
                                        <span className="text-xs font-medium text-cyan-400">
                                          {formatCurrency(lead.valor_estimado)}
                                        </span>
                                        {lead.dias_sin_actividad > 0 && (
                                          <span className={`text-xs ${
                                            lead.dias_sin_actividad > 7 ? "text-amber-400" : "text-slate-500"
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
