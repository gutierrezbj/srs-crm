import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import {
    Target,
    Search,
    ExternalLink,
    ArrowUpDown,
    Building2,
    Euro,
    Calendar,
    Clock,
    CheckCircle2,
    Filter,
    X,
    UserPlus,
    TrendingUp,
    Play,
    RefreshCw,
    Loader2,
    Brain,
    AlertTriangle,
    Zap,
    Info,
    FileText,
    Mail,
    Phone,
    Shield,
    Server,
    Award,
    Lightbulb,
    ChevronRight,
    Eye,
    EyeOff,
    Sparkles,
    Ban,
    Users,
    Trophy
} from "lucide-react";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
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
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
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
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from "@/components/ui/dialog";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Score color coding based on requirements
const getScoreColor = (score) => {
    if (score > 80) return "bg-red-500/20 text-red-400 border-red-500/30";
    if (score > 60) return "bg-orange-500/20 text-orange-400 border-orange-500/30";
    if (score > 40) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    return "bg-green-500/20 text-green-400 border-green-500/30";
};

const getScoreBadgeClass = (score) => {
    if (score > 80) return "bg-gradient-to-r from-red-600 to-red-500 text-white shadow-red-500/30";
    if (score > 60) return "bg-gradient-to-r from-orange-600 to-orange-500 text-white shadow-orange-500/30";
    if (score > 40) return "bg-gradient-to-r from-yellow-600 to-yellow-500 text-white shadow-yellow-500/30";
    return "bg-gradient-to-r from-green-600 to-green-500 text-white shadow-green-500/30";
};

// Pain score color coding
const getPainScoreColor = (painScore) => {
    if (painScore >= 80) return "text-red-400 bg-red-500/20 border-red-500/30";
    if (painScore >= 60) return "text-orange-400 bg-orange-500/20 border-orange-500/30";
    if (painScore >= 40) return "text-yellow-400 bg-yellow-500/20 border-yellow-500/30";
    return "text-green-400 bg-green-500/20 border-green-500/30";
};

const getNivelUrgenciaLabel = (nivel) => {
    const labels = {
        critico: { text: "Crítico", icon: AlertTriangle, color: "text-red-400" },
        alto: { text: "Alto", icon: Zap, color: "text-orange-400" },
        medio: { text: "Medio", icon: Clock, color: "text-yellow-400" },
        bajo: { text: "Bajo", icon: CheckCircle2, color: "text-green-400" }
    };
    return labels[nivel] || labels.medio;
};

// Estado de revisión config
const getEstadoRevisionConfig = (estado) => {
    const config = {
        nueva: { label: "Nueva", icon: Sparkles, color: "bg-blue-500/20 text-blue-400 border-blue-500/30" },
        revisada: { label: "Revisada", icon: Eye, color: "bg-green-500/20 text-green-400 border-green-500/30" },
        descartada: { label: "Descartada", icon: Ban, color: "bg-slate-500/20 text-slate-400 border-slate-500/30" }
    };
    return config[estado] || config.nueva;
};

export default function Oportunidades({ user }) {
    const [oportunidades, setOportunidades] = useState([]);
    const [loading, setLoading] = useState(true);
    const [tipoSrsFilter, setTipoSrsFilter] = useState("all");
    const [estadoRevisionFilter, setEstadoRevisionFilter] = useState("all");
    const [tiposSrs, setTiposSrs] = useState([]);
    const [convertDialogOpen, setConvertDialogOpen] = useState(false);
    const [selectedOportunidad, setSelectedOportunidad] = useState(null);
    const [converting, setConverting] = useState(false);
    const [executingSpotter, setExecutingSpotter] = useState(false);
    const [reclassifying, setReclassifying] = useState(false);
    const [analyzingPain, setAnalyzingPain] = useState({});
    const [analyzingBatch, setAnalyzingBatch] = useState(false);
    const [resumenOperadorOpen, setResumenOperadorOpen] = useState(false);
    const [resumenOperador, setResumenOperador] = useState(null);
    const [loadingResumen, setLoadingResumen] = useState(false);
    const [enrichingAdjudicatario, setEnrichingAdjudicatario] = useState(false);
    const [analyzingPliego, setAnalyzingPliego] = useState({});
    const [analyzingRapido, setAnalyzingRapido] = useState({});
    const [analisisPliego, setAnalisisPliego] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");

    const fetchOportunidades = useCallback(async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (tipoSrsFilter && tipoSrsFilter !== "all") {
                params.append("tipo_srs", tipoSrsFilter);
            }

            const response = await axios.get(`${API}/oportunidades?${params.toString()}`, {
                withCredentials: true
            });
            setOportunidades(response.data);
        } catch (error) {
            toast.error("Error al cargar oportunidades");
            console.error("Error fetching oportunidades:", error);
        } finally {
            setLoading(false);
        }
    }, [tipoSrsFilter]);

    const fetchTiposSrs = async () => {
        try {
            const response = await axios.get(`${API}/oportunidades/tipos-srs`, {
                withCredentials: true
            });
            setTiposSrs(response.data);
        } catch (error) {
            console.error("Error fetching tipos SRS:", error);
        }
    };

    useEffect(() => {
        fetchOportunidades();
        fetchTiposSrs();
    }, [fetchOportunidades]);

    const handleConvertToLead = async () => {
        if (!selectedOportunidad) return;

        setConverting(true);
        try {
            await axios.post(
                `${API}/oportunidades/${selectedOportunidad.oportunidad_id}/convertir-lead`,
                {},
                { withCredentials: true }
            );
            toast.success("Oportunidad convertida a lead correctamente");
            setConvertDialogOpen(false);
            setSelectedOportunidad(null);
            fetchOportunidades();
        } catch (error) {
            if (error.response?.status === 400) {
                toast.error("Esta oportunidad ya fue convertida a lead");
            } else {
                toast.error("Error al convertir a lead");
            }
        } finally {
            setConverting(false);
        }
    };

    const openConvertDialog = (oportunidad) => {
        setSelectedOportunidad(oportunidad);
        setConvertDialogOpen(true);
    };

    const handleExecuteSpotter = async () => {
        setExecutingSpotter(true);
        try {
            const response = await axios.post(
                `${API}/oportunidades/ejecutar-spotter`,
                {},
                { withCredentials: true }
            );

            if (response.data.success) {
                toast.success("SpotterSRS ejecutado correctamente");
                // Recargar oportunidades para ver las nuevas
                fetchOportunidades();
            } else {
                toast.error(response.data.message || "Error al ejecutar SpotterSRS");
            }
        } catch (error) {
            toast.error(error.response?.data?.detail || "Error al ejecutar SpotterSRS");
            console.error("Error executing SpotterSRS:", error);
        } finally {
            setExecutingSpotter(false);
        }
    };

    const handleReclassify = async () => {
        setReclassifying(true);
        try {
            const response = await axios.post(
                `${API}/oportunidades/reclasificar`,
                {},
                { withCredentials: true }
            );

            if (response.data.success) {
                toast.success(
                    `Reclasificación completada: ${response.data.cambios} cambios de ${response.data.total} oportunidades`
                );
                // Recargar oportunidades para ver los cambios
                fetchOportunidades();
                // Recargar tipos SRS por si hay nuevos
                fetchTiposSrs();
            } else {
                toast.error(response.data.message || "Error en reclasificación");
            }
        } catch (error) {
            toast.error(error.response?.data?.detail || "Error al reclasificar");
            console.error("Error reclassifying:", error);
        } finally {
            setReclassifying(false);
        }
    };

    const handleAnalyzePain = async (oportunidadId) => {
        setAnalyzingPain(prev => ({ ...prev, [oportunidadId]: true }));
        try {
            const response = await axios.post(
                `${API}/oportunidades/${oportunidadId}/analizar-pain`,
                {},
                { withCredentials: true }
            );

            if (response.data.success) {
                toast.success(`Análisis completado: Pain Score ${response.data.pain_analysis.pain_score}`);
                fetchOportunidades();
            } else {
                toast.error("Error en análisis de pain");
            }
        } catch (error) {
            toast.error(error.response?.data?.detail || "Error al analizar pain");
            console.error("Error analyzing pain:", error);
        } finally {
            setAnalyzingPain(prev => ({ ...prev, [oportunidadId]: false }));
        }
    };

    const handleAnalyzePainBatch = async () => {
        setAnalyzingBatch(true);
        try {
            const response = await axios.post(
                `${API}/oportunidades/analizar-pain-batch`,
                {},
                { withCredentials: true }
            );

            if (response.data.success) {
                toast.success(
                    `Análisis completado: ${response.data.analizadas} oportunidades. Pendientes: ${response.data.pendientes}`
                );
                fetchOportunidades();
            } else {
                toast.error(response.data.message || "Error en análisis batch");
            }
        } catch (error) {
            toast.error(error.response?.data?.detail || "Error al analizar batch");
            console.error("Error analyzing batch:", error);
        } finally {
            setAnalyzingBatch(false);
        }
    };

    const handleAnalyzePliego = async (oportunidadId) => {
        console.log("[DEBUG] handleAnalyzePliego called with:", oportunidadId);

        if (!oportunidadId) {
            console.error("[ERROR] oportunidadId is undefined/null");
            toast.error("Error: ID de oportunidad no válido");
            return;
        }

        setAnalyzingPliego(prev => ({ ...prev, [oportunidadId]: true }));
        toast.info("Analizando pliego... Esto puede tardar 30-60 segundos", { duration: 5000 });

        // Buscar la oportunidad para obtener datos del organismo
        const oportunidad = oportunidades.find(o => o.oportunidad_id === oportunidadId);
        console.log("[DEBUG] Found oportunidad:", oportunidad ? "yes" : "no");

        try {
            console.log("[DEBUG] Calling API:", `${API}/oportunidades/${oportunidadId}/analizar-pliego`);
            const response = await axios.post(
                `${API}/oportunidades/${oportunidadId}/analizar-pliego`,
                {},
                { withCredentials: true, timeout: 330000 } // 5.5 min timeout para PDFs grandes
            );
            console.log("[DEBUG] API response:", response.status);

            if (response.data.success) {
                const analisis = response.data.analisis;
                const nivelOp = analisis.resumen_operador?.nivel_oportunidad || "bronce";
                const tieneIt = analisis.tiene_it ? "Sí" : "No";

                toast.success(
                    `Análisis completado en ${response.data.tiempo_analisis.toFixed(1)}s. IT: ${tieneIt}, Nivel: ${nivelOp.toUpperCase()}`,
                    { duration: 5000 }
                );

                // Mostrar resumen del operador automáticamente
                setResumenOperador({
                    ...analisis.resumen_operador,
                    oportunidad_id: oportunidadId,
                    ref_code: oportunidad?.ref_code,
                    organismo: oportunidad?.adjudicatario || oportunidad?.organo_contratacion || "Organismo",
                    objeto: oportunidad?.objeto || "",
                    importe: oportunidad?.importe || analisis.importe,
                    // Datos del adjudicatario para contacto
                    adjudicatario: oportunidad?.adjudicatario,
                    nif: oportunidad?.nif,
                    organo_contratacion: oportunidad?.organo_contratacion,
                    email_contacto: analisis.email_contacto,
                    telefono_contacto: analisis.telefono_contacto,
                    resumen_it: analisis.resumen_it,
                    tiene_it: analisis.tiene_it,
                    // Datos enriquecidos (si ya existen)
                    datos_adjudicatario: oportunidad?.datos_adjudicatario,
                    // Incluir análisis completo para mostrar componentes IT y pain score
                    analisis_pliego: analisis
                });
                setResumenOperadorOpen(true);

                // Desactivar spinner ANTES de refrescar para evitar race condition
                setAnalyzingPliego(prev => ({ ...prev, [oportunidadId]: false }));

                // Refrescar lista en background (sin bloquear)
                fetchOportunidades();
            } else {
                toast.error("Error en análisis de pliego");
                setAnalyzingPliego(prev => ({ ...prev, [oportunidadId]: false }));
            }
        } catch (error) {
            console.error("[DEBUG] Error full:", error);
            console.error("[DEBUG] Error response:", error.response);
            console.error("[DEBUG] Error code:", error.code);
            console.error("[DEBUG] Error message:", error.message);

            if (error.code === 'ECONNABORTED') {
                toast.error("Timeout: El análisis tardó demasiado. Inténtalo de nuevo.");
            } else {
                toast.error(error.response?.data?.detail || "Error al analizar pliego");
            }
            console.error("Error analyzing pliego:", error);
            setAnalyzingPliego(prev => ({ ...prev, [oportunidadId]: false }));
        }
    };

    // Análisis rápido Level 1 (~5 segundos) - solo extracción sin IA
    const handleAnalisisRapido = async (oportunidadId) => {
        if (!oportunidadId) {
            toast.error("Error: ID de oportunidad no válido");
            return;
        }

        setAnalyzingRapido(prev => ({ ...prev, [oportunidadId]: true }));
        toast.info("Análisis rápido en progreso...", { duration: 3000 });

        const oportunidad = oportunidades.find(o => o.oportunidad_id === oportunidadId);

        try {
            const response = await axios.post(
                `${API}/oportunidades/${oportunidadId}/analisis-rapido`,
                {},
                { withCredentials: true, timeout: 30000 }
            );

            if (response.data) {
                const { tiene_componente_it, num_competidores, empresas_competidoras } = response.data;

                // Mostrar resultado
                toast.success(
                    `Análisis rápido completado. IT: ${tiene_componente_it ? "Sí" : "No"}, Competidores: ${num_competidores}`,
                    { duration: 4000 }
                );

                // Si hay competidores, mostrar resumen con ellos
                if (empresas_competidoras && empresas_competidoras.length > 0) {
                    setResumenOperador({
                        oportunidad_id: oportunidadId,
                        ref_code: oportunidad?.ref_code,
                        organismo: oportunidad?.adjudicatario || oportunidad?.organo_contratacion || "Organismo",
                        objeto: oportunidad?.objeto || "",
                        importe: oportunidad?.importe,
                        adjudicatario: oportunidad?.adjudicatario,
                        nif: oportunidad?.nif,
                        organo_contratacion: oportunidad?.organo_contratacion,
                        tiene_it: tiene_componente_it,
                        nivel_analisis: "rapido",
                        empresas_competidoras: empresas_competidoras,
                        datos_adjudicatario: response.data.datos_adjudicatario,
                        datos_organo: response.data.datos_organo,
                        url_pliego_tecnico: response.data.url_pliego_tecnico,
                    });
                    setResumenOperadorOpen(true);
                }

                // Refrescar lista en background
                fetchOportunidades();
            }
        } catch (error) {
            toast.error(error.response?.data?.detail || "Error en análisis rápido");
            console.error("Error en análisis rápido:", error);
        } finally {
            setAnalyzingRapido(prev => ({ ...prev, [oportunidadId]: false }));
        }
    };

    const handleUpdateEstadoRevision = async (oportunidadId, nuevoEstado) => {
        try {
            await axios.patch(
                `${API}/oportunidades/${oportunidadId}/estado-revision`,
                { estado: nuevoEstado },
                { withCredentials: true }
            );
            // Actualizar localmente sin refetch completo
            setOportunidades(prev => prev.map(op =>
                op.oportunidad_id === oportunidadId
                    ? { ...op, estado_revision: nuevoEstado }
                    : op
            ));
            if (nuevoEstado === "descartada") {
                toast.success("Oportunidad marcada como descartada");
            }
        } catch (error) {
            console.error("Error updating estado revision:", error);
        }
    };

    const handleViewResumenOperador = async (oportunidad) => {
        // Auto-marcar como revisada si era nueva
        if (!oportunidad.estado_revision || oportunidad.estado_revision === "nueva") {
            handleUpdateEstadoRevision(oportunidad.oportunidad_id, "revisada");
        }

        // Si ya tiene análisis de pliego, mostrar el resumen
        if (oportunidad.analisis_pliego) {
            setResumenOperador({
                ...oportunidad.analisis_pliego.resumen_operador,
                oportunidad_id: oportunidad.oportunidad_id,
                ref_code: oportunidad.ref_code,
                organismo: oportunidad.adjudicatario || oportunidad.organo_contratacion || "Organismo",
                objeto: oportunidad.objeto,
                importe: oportunidad.importe,
                // Datos del adjudicatario para contacto
                adjudicatario: oportunidad.adjudicatario,
                nif: oportunidad.nif,
                organo_contratacion: oportunidad.organo_contratacion,
                email_contacto: oportunidad.analisis_pliego.email_contacto,
                telefono_contacto: oportunidad.analisis_pliego.telefono_contacto,
                resumen_it: oportunidad.analisis_pliego.resumen_it,
                tiene_it: oportunidad.analisis_pliego.tiene_it,
                // Datos enriquecidos del adjudicatario
                datos_adjudicatario: oportunidad.datos_adjudicatario
            });
            setResumenOperadorOpen(true);
            return;
        }

        // Si no tiene, intentar obtenerlo del endpoint
        setLoadingResumen(true);
        try {
            const response = await axios.get(
                `${API}/oportunidades/${oportunidad.oportunidad_id}/resumen-operador`,
                { withCredentials: true }
            );
            setResumenOperador(response.data);
            setResumenOperadorOpen(true);
        } catch (error) {
            if (error.response?.status === 400) {
                toast.info("Esta oportunidad no tiene análisis de pliego. Usa 'Analizar Pliego' primero.");
            } else {
                toast.error("Error al obtener resumen");
            }
        } finally {
            setLoadingResumen(false);
        }
    };

    const handleEnrichAdjudicatario = async (oportunidadId) => {
        // Verificar si tenemos NIF antes de hacer la llamada
        if (!resumenOperador.nif) {
            toast.warning("Esta oportunidad no tiene NIF del adjudicatario. No es posible enriquecer los datos.", { duration: 5000 });
            return;
        }

        setEnrichingAdjudicatario(true);
        toast.info("Buscando datos del adjudicatario... Esto puede tardar unos segundos.", { duration: 3000 });

        try {
            const response = await axios.post(
                `${API}/oportunidades/${oportunidadId}/enriquecer-adjudicatario`,
                {},
                { withCredentials: true, timeout: 90000 } // Aumentar timeout a 90s
            );

            if (response.data.success) {
                const datos = response.data.datos_adjudicatario;
                const confianza = datos.confianza || "baja";

                toast.success(
                    `Datos obtenidos (confianza: ${confianza}). Fuente: ${datos.fuente || "N/A"}`,
                    { duration: 4000 }
                );

                // Actualizar el resumenOperador con los nuevos datos
                setResumenOperador(prev => ({
                    ...prev,
                    datos_adjudicatario: datos,
                    telefono_contacto: datos.telefono || prev?.telefono_contacto,
                    email_contacto: datos.email || prev?.email_contacto
                }));

                // Refrescar oportunidades para que se guarden los datos
                fetchOportunidades();
            } else {
                toast.error("No se pudieron obtener datos adicionales");
            }
        } catch (error) {
            const errorMsg = error.response?.data?.detail || "Error al buscar datos del adjudicatario";
            if (errorMsg.includes("NIF")) {
                toast.warning("No hay NIF disponible para buscar datos del adjudicatario", { duration: 5000 });
            } else {
                toast.error(errorMsg);
            }
            console.error("Error enriching adjudicatario:", error);
        } finally {
            setEnrichingAdjudicatario(false);
        }
    };

    const handleCreateLeadFromCompetidor = async (empresa) => {
        try {
            // Crear un lead directamente desde la empresa competidora
            const leadData = {
                nombre_empresa: empresa.nombre,
                nif: empresa.nif,
                fuente: "Licitación",
                notas: `Empresa que participó en licitación (puntuación: ${empresa.puntuacion || 'N/A'} pts). Posible cliente potencial - no ganaron la adjudicación.`,
                stage: "nuevo"
            };

            const response = await axios.post(
                `${API}/leads`,
                leadData,
                { withCredentials: true }
            );

            if (response.data) {
                toast.success(`Lead creado: ${empresa.nombre}`, { duration: 3000 });
            }
        } catch (error) {
            if (error.response?.status === 400 && error.response?.data?.detail?.includes("ya existe")) {
                toast.info(`Ya existe un lead para ${empresa.nombre}`);
            } else {
                toast.error(error.response?.data?.detail || "Error al crear lead");
            }
            console.error("Error creating lead from competidor:", error);
        }
    };

    const getNivelOportunidadBadge = (nivel) => {
        const config = {
            oro: { color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30", icon: Award },
            plata: { color: "bg-slate-400/20 text-slate-300 border-slate-400/30", icon: Award },
            bronce: { color: "bg-orange-700/20 text-orange-400 border-orange-700/30", icon: Award },
            descartar: { color: "bg-red-500/20 text-red-400 border-red-500/30", icon: X }
        };
        return config[nivel] || config.bronce;
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat("es-ES", {
            style: "currency",
            currency: "EUR",
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    };

    const formatDate = (dateString) => {
        if (!dateString) return "-";
        const date = new Date(dateString);
        return date.toLocaleDateString("es-ES", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });
    };

    const clearFilters = () => {
        setTipoSrsFilter("all");
        setEstadoRevisionFilter("all");
        setSearchQuery("");
    };

    const hasFilters = tipoSrsFilter !== "all" || estadoRevisionFilter !== "all" || searchQuery !== "";

    // Filtrar oportunidades por estado de revisión y búsqueda (cliente-side)
    const filteredOportunidades = oportunidades.filter(o => {
        // Filtro por estado
        if (estadoRevisionFilter !== "all") {
            const estado = o.estado_revision || "nueva";
            if (estado !== estadoRevisionFilter) return false;
        }

        // Filtro por búsqueda (ref_code, adjudicatario, objeto, NIF)
        if (searchQuery) {
            const query = searchQuery.toLowerCase().trim();
            const refCode = (o.ref_code || "").toLowerCase();
            const adjudicatario = (o.adjudicatario || "").toLowerCase();
            const objeto = (o.objeto || "").toLowerCase();
            const nif = (o.nif || "").toLowerCase();

            // Buscar coincidencia en cualquiera de los campos
            if (!refCode.includes(query) &&
                !adjudicatario.includes(query) &&
                !objeto.includes(query) &&
                !nif.includes(query)) {
                return false;
            }
        }

        return true;
    });

    // Stats (sobre datos filtrados)
    const totalOportunidades = filteredOportunidades.length;
    const pendientes = filteredOportunidades.filter(o => !o.convertido_lead).length;
    const convertidas = filteredOportunidades.filter(o => o.convertido_lead).length;
    const nuevas = oportunidades.filter(o => !o.estado_revision || o.estado_revision === "nueva").length;
    const avgScore = oportunidades.length > 0
        ? Math.round(oportunidades.reduce((sum, o) => sum + o.score, 0) / oportunidades.length)
        : 0;

    return (
        <div data-testid="oportunidades-page" className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold theme-text flex items-center gap-2">
                        <Target className="w-7 h-7 text-cyan-400" />
                        Oportunidades PLACSP
                    </h1>
                    <p className="theme-text-secondary text-sm">
                        Oportunidades detectadas por SpotterSRS
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        onClick={handleAnalyzePainBatch}
                        disabled={analyzingBatch || reclassifying || executingSpotter}
                        variant="outline"
                        className="bg-purple-500/20 text-purple-300 border-purple-500/50 hover:bg-purple-500/30 hover:text-purple-200"
                        title="Analizar pain de oportunidades pendientes con IA"
                    >
                        {analyzingBatch ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Analizando...
                            </>
                        ) : (
                            <>
                                <Brain className="w-4 h-4 mr-2" />
                                Analizar Pain (IA)
                            </>
                        )}
                    </Button>
                    <Button
                        onClick={handleReclassify}
                        disabled={reclassifying || executingSpotter || analyzingBatch}
                        variant="outline"
                        className="bg-amber-500/20 text-amber-300 border-amber-500/50 hover:bg-amber-500/30 hover:text-amber-200"
                        title="Reclasificar oportunidades existentes con el algoritmo actualizado"
                    >
                        {reclassifying ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Reclasificando...
                            </>
                        ) : (
                            <>
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Reclasificar
                            </>
                        )}
                    </Button>
                    <Button
                        onClick={handleExecuteSpotter}
                        disabled={executingSpotter || reclassifying || analyzingBatch}
                        className="btn-gradient"
                        title="Ejecutar SpotterSRS para buscar nuevas oportunidades en PLACSP"
                    >
                        {executingSpotter ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Ejecutando...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4 mr-2" />
                                Ejecutar SpotterSRS
                            </>
                        )}
                    </Button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <Card
                    className={`theme-bg-secondary p-4 cursor-pointer transition-all hover:ring-2 hover:ring-blue-500/50 ${estadoRevisionFilter === "nueva" ? "ring-2 ring-blue-500" : ""}`}
                    style={{ border: '1px solid var(--theme-border)' }}
                    onClick={() => setEstadoRevisionFilter(estadoRevisionFilter === "nueva" ? "all" : "nueva")}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/10">
                            <Sparkles className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                            <p className="theme-text-muted text-xs">Nuevas</p>
                            <p className="theme-text font-bold text-xl">{nuevas}</p>
                        </div>
                    </div>
                </Card>
                <Card className="theme-bg-secondary p-4" style={{ border: '1px solid var(--theme-border)' }}>
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-cyan-500/10">
                            <Target className="w-5 h-5 text-cyan-400" />
                        </div>
                        <div>
                            <p className="theme-text-muted text-xs">Total</p>
                            <p className="theme-text font-bold text-xl">{totalOportunidades}</p>
                        </div>
                    </div>
                </Card>
                <Card className="theme-bg-secondary p-4" style={{ border: '1px solid var(--theme-border)' }}>
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-yellow-500/10">
                            <Clock className="w-5 h-5 text-yellow-400" />
                        </div>
                        <div>
                            <p className="theme-text-muted text-xs">Pendientes</p>
                            <p className="theme-text font-bold text-xl">{pendientes}</p>
                        </div>
                    </div>
                </Card>
                <Card className="theme-bg-secondary p-4" style={{ border: '1px solid var(--theme-border)' }}>
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-green-500/10">
                            <CheckCircle2 className="w-5 h-5 text-green-400" />
                        </div>
                        <div>
                            <p className="theme-text-muted text-xs">Convertidas</p>
                            <p className="theme-text font-bold text-xl">{convertidas}</p>
                        </div>
                    </div>
                </Card>
                <Card className="theme-bg-secondary p-4" style={{ border: '1px solid var(--theme-border)' }}>
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-purple-500/10">
                            <TrendingUp className="w-5 h-5 text-purple-400" />
                        </div>
                        <div>
                            <p className="theme-text-muted text-xs">Score Medio</p>
                            <p className="theme-text font-bold text-xl">{avgScore}</p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Filters */}
            <Card className="theme-bg-secondary p-4" style={{ border: '1px solid var(--theme-border)' }}>
                <div className="flex flex-col sm:flex-row gap-4 items-center">
                    <div className="flex items-center gap-2 flex-1">
                        <div className="relative w-full max-w-xs">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 theme-text-muted" />
                            <Input
                                placeholder="Buscar por ref, empresa, NIF..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-9 theme-bg-tertiary w-full"
                                style={{ borderColor: 'var(--theme-border)' }}
                            />
                        </div>
                    </div>
                    <div className="flex gap-2 flex-wrap items-center">
                        <Filter className="w-4 h-4 theme-text-muted" />
                        <Select value={tipoSrsFilter} onValueChange={setTipoSrsFilter}>
                            <SelectTrigger
                                className="w-[200px] theme-bg-tertiary"
                                style={{ borderColor: 'var(--theme-border)' }}
                                data-testid="tipo-srs-filter"
                            >
                                <SelectValue placeholder="Tipo SRS" />
                            </SelectTrigger>
                            <SelectContent className="theme-bg-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                                <SelectItem value="all">Todos los tipos</SelectItem>
                                {tiposSrs.map((tipo) => (
                                    <SelectItem key={tipo} value={tipo}>{tipo}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Select value={estadoRevisionFilter} onValueChange={setEstadoRevisionFilter}>
                            <SelectTrigger
                                className="w-[180px] theme-bg-tertiary"
                                style={{ borderColor: 'var(--theme-border)' }}
                            >
                                <SelectValue placeholder="Estado revisión" />
                            </SelectTrigger>
                            <SelectContent className="theme-bg-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                                <SelectItem value="all">Todos los estados</SelectItem>
                                <SelectItem value="nueva">
                                    <span className="flex items-center gap-2">
                                        <Sparkles className="w-3 h-3 text-blue-400" />
                                        Nuevas
                                    </span>
                                </SelectItem>
                                <SelectItem value="revisada">
                                    <span className="flex items-center gap-2">
                                        <Eye className="w-3 h-3 text-green-400" />
                                        Revisadas
                                    </span>
                                </SelectItem>
                                <SelectItem value="descartada">
                                    <span className="flex items-center gap-2">
                                        <Ban className="w-3 h-3 text-slate-400" />
                                        Descartadas
                                    </span>
                                </SelectItem>
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

            {/* Opportunities Table */}
            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div style={{ color: 'var(--theme-accent)' }} className="animate-pulse">
                        Cargando oportunidades...
                    </div>
                </div>
            ) : oportunidades.length === 0 ? (
                <Card className="theme-bg-secondary p-12 text-center" style={{ border: '1px solid var(--theme-border)' }}>
                    <Target className="w-12 h-12 mx-auto mb-4 theme-text-muted" />
                    <h3 className="text-lg font-medium theme-text mb-2">No hay oportunidades</h3>
                    <p className="theme-text-secondary mb-4">
                        {hasFilters
                            ? "No se encontraron oportunidades con los filtros aplicados"
                            : "Importa oportunidades desde SpotterSRS para empezar"}
                    </p>
                </Card>
            ) : (
                <Card className="theme-bg-secondary overflow-hidden" style={{ border: '1px solid var(--theme-border)' }}>
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow className="border-b" style={{ borderColor: 'var(--theme-border)' }}>
                                    <TableHead className="theme-text-secondary font-semibold w-12">Ref</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">
                                        <div className="flex items-center gap-1">
                                            Score
                                            <ArrowUpDown className="w-3 h-3" />
                                        </div>
                                    </TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">
                                        <div className="flex items-center gap-1">
                                            <Brain className="w-3 h-3" />
                                            Pain
                                        </div>
                                    </TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Adjudicatario</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Importe</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Tipo SRS</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Días Restantes</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Revisión</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Lead</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold text-right">Acciones</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredOportunidades.map((oportunidad) => (
                                    <TableRow
                                        key={oportunidad.oportunidad_id}
                                        className={`border-b hover:bg-white/5 transition-colors ${
                                            oportunidad.estado_revision === "descartada" ? "opacity-50" : ""
                                        }`}
                                        style={{ borderColor: 'var(--theme-border)' }}
                                        data-testid={`oportunidad-row-${oportunidad.oportunidad_id}`}
                                    >
                                        <TableCell className="font-mono text-sm theme-text-secondary">
                                            {oportunidad.ref_code || "-"}
                                        </TableCell>
                                        <TableCell>
                                            <Badge
                                                className={`${getScoreBadgeClass(oportunidad.score)} shadow-lg font-bold px-3 py-1`}
                                            >
                                                {oportunidad.score}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            <TooltipProvider>
                                                {oportunidad.pain_score !== undefined ? (
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <div className="flex flex-col items-start gap-0.5">
                                                                <Badge
                                                                    className={`${getPainScoreColor(oportunidad.pain_score)} font-bold px-2.5 py-1 text-sm shadow-lg`}
                                                                >
                                                                    <Brain className="w-3 h-3 mr-1" />
                                                                    {oportunidad.pain_score}
                                                                </Badge>
                                                                <span className={`text-[10px] font-medium ${
                                                                    oportunidad.nivel_urgencia === "critico" ? "text-red-400" :
                                                                    oportunidad.nivel_urgencia === "alto" ? "text-orange-400" :
                                                                    oportunidad.nivel_urgencia === "medio" ? "text-yellow-400" :
                                                                    "text-green-400"
                                                                }`}>
                                                                    {getNivelUrgenciaLabel(oportunidad.nivel_urgencia).text}
                                                                </span>
                                                            </div>
                                                        </TooltipTrigger>
                                                        <TooltipContent side="right" className="max-w-xs bg-slate-900 border-slate-700">
                                                            <div className="space-y-2">
                                                                <p className="font-semibold text-white">
                                                                    Pain Score: {oportunidad.pain_score}
                                                                </p>
                                                                <p className="text-xs text-slate-300">
                                                                    Nivel: {getNivelUrgenciaLabel(oportunidad.nivel_urgencia).text}
                                                                </p>
                                                                {oportunidad.pain_analysis?.resumen_ejecutivo && (
                                                                    <p className="text-xs text-slate-400">
                                                                        {oportunidad.pain_analysis.resumen_ejecutivo.substring(0, 150)}...
                                                                    </p>
                                                                )}
                                                            </div>
                                                        </TooltipContent>
                                                    </Tooltip>
                                                ) : (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => handleAnalyzePain(oportunidad.oportunidad_id)}
                                                        disabled={analyzingPain[oportunidad.oportunidad_id]}
                                                        className="text-slate-400 border-slate-600 hover:text-purple-400 hover:border-purple-500/50 hover:bg-purple-500/10"
                                                        title="Analizar con IA"
                                                    >
                                                        {analyzingPain[oportunidad.oportunidad_id] ? (
                                                            <Loader2 className="w-4 h-4 animate-spin" />
                                                        ) : (
                                                            <>
                                                                <Brain className="w-4 h-4 mr-1" />
                                                                <span className="text-xs">Analizar</span>
                                                            </>
                                                        )}
                                                    </Button>
                                                )}
                                            </TooltipProvider>
                                        </TableCell>
                                        <TableCell>
                                            <div className="max-w-[250px]">
                                                <p className="theme-text font-medium truncate" title={oportunidad.adjudicatario}>
                                                    {oportunidad.adjudicatario}
                                                </p>
                                                <p className="theme-text-muted text-xs truncate" title={oportunidad.objeto}>
                                                    {oportunidad.objeto.substring(0, 50)}...
                                                </p>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <span className="font-semibold" style={{ color: 'var(--theme-currency)' }}>
                                                {formatCurrency(oportunidad.importe)}
                                            </span>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="outline" className="theme-text-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                                                {oportunidad.tipo_srs}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            {oportunidad.dias_restantes !== null ? (
                                                <div className="flex items-center gap-1">
                                                    <Clock className="w-4 h-4 theme-text-muted" />
                                                    <span className={`font-medium ${oportunidad.dias_restantes < 30 ? 'text-red-400' :
                                                            oportunidad.dias_restantes < 90 ? 'text-yellow-400' :
                                                                'text-green-400'
                                                        }`}>
                                                        {oportunidad.dias_restantes} días
                                                    </span>
                                                </div>
                                            ) : (
                                                <span className="theme-text-muted">-</span>
                                            )}
                                        </TableCell>
                                        {/* Estado de Revisión */}
                                        <TableCell>
                                            <TooltipProvider>
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <Badge
                                                            className={`${getEstadoRevisionConfig(oportunidad.estado_revision || "nueva").color} cursor-pointer`}
                                                            onClick={() => {
                                                                const estados = ["nueva", "revisada", "descartada"];
                                                                const currentIdx = estados.indexOf(oportunidad.estado_revision || "nueva");
                                                                const nextEstado = estados[(currentIdx + 1) % estados.length];
                                                                handleUpdateEstadoRevision(oportunidad.oportunidad_id, nextEstado);
                                                            }}
                                                        >
                                                            {(() => {
                                                                const config = getEstadoRevisionConfig(oportunidad.estado_revision || "nueva");
                                                                const Icon = config.icon;
                                                                return (
                                                                    <>
                                                                        <Icon className="w-3 h-3 mr-1" />
                                                                        {config.label}
                                                                    </>
                                                                );
                                                            })()}
                                                        </Badge>
                                                    </TooltipTrigger>
                                                    <TooltipContent>
                                                        Click para cambiar estado
                                                    </TooltipContent>
                                                </Tooltip>
                                            </TooltipProvider>
                                        </TableCell>
                                        {/* Estado Lead */}
                                        <TableCell>
                                            {oportunidad.convertido_lead ? (
                                                <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                                    <CheckCircle2 className="w-3 h-3 mr-1" />
                                                    Convertido
                                                </Badge>
                                            ) : (
                                                <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                                                    Pendiente
                                                </Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                {/* Botón Análisis Rápido (Level 1) */}
                                                <TooltipProvider>
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <Button
                                                                size="sm"
                                                                variant="outline"
                                                                onClick={() => handleAnalisisRapido(oportunidad.oportunidad_id)}
                                                                disabled={analyzingRapido[oportunidad.oportunidad_id]}
                                                                className={`${oportunidad.empresas_competidoras?.length > 0 ? 'text-amber-400 border-amber-500/30' : 'text-slate-400 border-slate-500/30'} hover:bg-amber-500/10`}
                                                            >
                                                                {analyzingRapido[oportunidad.oportunidad_id] ? (
                                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                                ) : (
                                                                    <Search className="w-4 h-4" />
                                                                )}
                                                            </Button>
                                                        </TooltipTrigger>
                                                        <TooltipContent>
                                                            {oportunidad.empresas_competidoras?.length > 0
                                                                ? `Análisis rápido (${oportunidad.empresas_competidoras.length} competidores)`
                                                                : "Análisis rápido (~5s) - Extrae competidores"}
                                                        </TooltipContent>
                                                    </Tooltip>
                                                </TooltipProvider>

                                                {/* Botón Analizar Pliego (Level 2) */}
                                                <TooltipProvider>
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <Button
                                                                size="sm"
                                                                variant="outline"
                                                                onClick={() => handleAnalyzePliego(oportunidad.oportunidad_id)}
                                                                disabled={analyzingPliego[oportunidad.oportunidad_id]}
                                                                className={`${oportunidad.analisis_pliego ? 'text-green-400 border-green-500/30' : 'text-cyan-400 border-cyan-500/30'} hover:bg-cyan-500/10`}
                                                            >
                                                                {analyzingPliego[oportunidad.oportunidad_id] ? (
                                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                                ) : (
                                                                    <FileText className="w-4 h-4" />
                                                                )}
                                                            </Button>
                                                        </TooltipTrigger>
                                                        <TooltipContent>
                                                            {oportunidad.analisis_pliego
                                                                ? "Re-analizar pliego (ya analizado)"
                                                                : "Analizar pliego completo con IA (~30-60s)"}
                                                        </TooltipContent>
                                                    </Tooltip>
                                                </TooltipProvider>

                                                {/* Botón Ver Resumen Operador */}
                                                {oportunidad.analisis_pliego && (
                                                    <TooltipProvider>
                                                        <Tooltip>
                                                            <TooltipTrigger asChild>
                                                                <Button
                                                                    size="sm"
                                                                    variant="outline"
                                                                    onClick={() => handleViewResumenOperador(oportunidad)}
                                                                    className="text-purple-400 border-purple-500/30 hover:bg-purple-500/10"
                                                                >
                                                                    <Lightbulb className="w-4 h-4" />
                                                                </Button>
                                                            </TooltipTrigger>
                                                            <TooltipContent>
                                                                Ver resumen para el operador
                                                            </TooltipContent>
                                                        </Tooltip>
                                                    </TooltipProvider>
                                                )}

                                                {!oportunidad.convertido_lead && (
                                                    <Button
                                                        size="sm"
                                                        onClick={() => openConvertDialog(oportunidad)}
                                                        className="btn-gradient"
                                                        data-testid={`convert-btn-${oportunidad.oportunidad_id}`}
                                                    >
                                                        <UserPlus className="w-4 h-4 mr-1" />
                                                        Convertir a Lead
                                                    </Button>
                                                )}
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => window.open(oportunidad.url_licitacion, '_blank')}
                                                    className="theme-text-secondary hover:theme-text"
                                                    style={{ borderColor: 'var(--theme-border)' }}
                                                >
                                                    <ExternalLink className="w-4 h-4" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </Card>
            )}

            {/* Convert to Lead Dialog */}
            <AlertDialog open={convertDialogOpen} onOpenChange={setConvertDialogOpen}>
                <AlertDialogContent className="bg-slate-900 border-white/10">
                    <AlertDialogHeader>
                        <AlertDialogTitle className="text-white">
                            Convertir a Lead
                        </AlertDialogTitle>
                        <AlertDialogDescription className="text-slate-400">
                            {selectedOportunidad && (
                                <>
                                    ¿Deseas convertir esta oportunidad en un lead?
                                    <div className="mt-4 p-4 rounded-lg bg-slate-800 space-y-2">
                                        <p className="text-white font-medium">{selectedOportunidad.adjudicatario}</p>
                                        <p className="text-sm">{formatCurrency(selectedOportunidad.importe)}</p>
                                        <p className="text-sm">Score: {selectedOportunidad.score}</p>
                                    </div>
                                </>
                            )}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel className="border-white/10 text-slate-300 hover:bg-slate-800">
                            Cancelar
                        </AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleConvertToLead}
                            disabled={converting}
                            className="btn-gradient"
                        >
                            {converting ? "Convirtiendo..." : "Convertir a Lead"}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            {/* Resumen Operador Dialog */}
            <Dialog open={resumenOperadorOpen} onOpenChange={setResumenOperadorOpen}>
                <DialogContent className="bg-slate-900 border-white/10 max-w-xl sm:max-w-2xl md:max-w-3xl w-[95vw] max-h-[90vh] overflow-y-auto overflow-x-hidden p-4 sm:p-6">
                    <DialogHeader>
                        <DialogTitle className="text-white flex items-center gap-2">
                            <Lightbulb className="w-5 h-5 text-yellow-400" />
                            Resumen para el Operador
                            {resumenOperador?.ref_code && (
                                <Badge variant="outline" className="ml-2 font-mono text-xs bg-slate-700/50 text-slate-300 border-slate-600">
                                    #{resumenOperador.ref_code}
                                </Badge>
                            )}
                        </DialogTitle>
                        <DialogDescription className="text-slate-400">
                            Información clave para preparar el contacto comercial
                        </DialogDescription>
                    </DialogHeader>

                    {resumenOperador && (
                        <div className="space-y-6 mt-4">
                            {/* Header con nivel de oportunidad */}
                            <div className="p-4 rounded-lg bg-slate-800/50 overflow-hidden">
                                <div className="flex items-center gap-2 mb-2 flex-wrap">
                                    <Badge className={getNivelOportunidadBadge(resumenOperador.nivel_oportunidad).color}>
                                        {resumenOperador.nivel_oportunidad?.toUpperCase()}
                                    </Badge>
                                    {resumenOperador.tiene_it && (
                                        <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                                            <Server className="w-3 h-3 mr-1" />
                                            Contiene IT
                                        </Badge>
                                    )}
                                </div>
                                <p className="text-white font-semibold text-lg break-words">{resumenOperador.organismo || resumenOperador.empresa || "Organismo"}</p>
                                <p className="text-slate-400 text-sm break-words mt-1">{resumenOperador.objeto}</p>
                                {resumenOperador.importe > 0 && (
                                    <p className="text-cyan-400 font-medium mt-2">{formatCurrency(resumenOperador.importe)}</p>
                                )}
                            </div>

                            {/* Datos del Adjudicatario para Contacto */}
                            <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20 overflow-hidden">
                                <div className="flex flex-col gap-2 mb-3">
                                    <h3 className="text-blue-400 font-semibold flex items-center gap-2">
                                        <Building2 className="w-4 h-4" />
                                        Datos del Adjudicatario
                                    </h3>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="text-blue-400 border-blue-500/30 hover:bg-blue-500/20 w-full"
                                        onClick={() => handleEnrichAdjudicatario(resumenOperador.oportunidad_id)}
                                        disabled={enrichingAdjudicatario || !resumenOperador.oportunidad_id}
                                    >
                                        {enrichingAdjudicatario ? (
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        ) : (
                                            <Search className="w-4 h-4 mr-2" />
                                        )}
                                        {resumenOperador.datos_adjudicatario?.telefono ? "Actualizar datos" : "Buscar datos"}
                                    </Button>
                                </div>
                                <div className="space-y-3">
                                    <div>
                                        <p className="text-slate-400 text-xs mb-1">Empresa</p>
                                        <p className="text-white font-medium">
                                            {(() => {
                                                const nombreComercial = resumenOperador.datos_adjudicatario?.nombre_comercial;
                                                // Ignorar valores placeholder inválidos
                                                const esValido = nombreComercial &&
                                                    !nombreComercial.toLowerCase().includes('the bid') &&
                                                    !nombreComercial.toLowerCase().includes('file number') &&
                                                    nombreComercial.length > 2;
                                                return esValido ? nombreComercial : (resumenOperador.adjudicatario || resumenOperador.organismo || "-");
                                            })()}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-slate-400 text-xs mb-1">NIF</p>
                                        <p className="text-white font-medium">{resumenOperador.nif || "-"}</p>
                                    </div>
                                    {/* Botones de acción rápida cuando hay datos de contacto */}
                                    {(resumenOperador.datos_adjudicatario?.email || resumenOperador.email_contacto ||
                                      resumenOperador.datos_adjudicatario?.telefono || resumenOperador.telefono_contacto) && (
                                        <div className="flex gap-2 py-2">
                                            {(resumenOperador.datos_adjudicatario?.telefono || resumenOperador.telefono_contacto) && (
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    className="flex-1 text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/20"
                                                    asChild
                                                >
                                                    <a href={`tel:${resumenOperador.datos_adjudicatario?.telefono || resumenOperador.telefono_contacto}`}>
                                                        <Phone className="w-4 h-4 mr-2" />
                                                        Llamar
                                                    </a>
                                                </Button>
                                            )}
                                            {(resumenOperador.datos_adjudicatario?.email || resumenOperador.email_contacto) && (
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    className="flex-1 text-purple-400 border-purple-500/30 hover:bg-purple-500/20"
                                                    asChild
                                                >
                                                    <a href={`mailto:${resumenOperador.datos_adjudicatario?.email || resumenOperador.email_contacto}`}>
                                                        <Mail className="w-4 h-4 mr-2" />
                                                        Email
                                                    </a>
                                                </Button>
                                            )}
                                        </div>
                                    )}
                                    {(resumenOperador.datos_adjudicatario?.email || resumenOperador.email_contacto) && (
                                        <div>
                                            <p className="text-slate-400 text-xs mb-1">Email</p>
                                            <a
                                                href={`mailto:${resumenOperador.datos_adjudicatario?.email || resumenOperador.email_contacto}`}
                                                className="text-blue-400 hover:underline flex items-center gap-1"
                                            >
                                                <Mail className="w-3 h-3" />
                                                {resumenOperador.datos_adjudicatario?.email || resumenOperador.email_contacto}
                                            </a>
                                        </div>
                                    )}
                                    {(resumenOperador.datos_adjudicatario?.telefono || resumenOperador.telefono_contacto) && (
                                        <div>
                                            <p className="text-slate-400 text-xs mb-1">Teléfono</p>
                                            <a
                                                href={`tel:${resumenOperador.datos_adjudicatario?.telefono || resumenOperador.telefono_contacto}`}
                                                className="text-blue-400 hover:underline flex items-center gap-1"
                                            >
                                                <Phone className="w-3 h-3" />
                                                {resumenOperador.datos_adjudicatario?.telefono || resumenOperador.telefono_contacto}
                                            </a>
                                        </div>
                                    )}
                                    {/* Mensaje cuando no hay datos de contacto */}
                                    {!resumenOperador.datos_adjudicatario?.email && !resumenOperador.email_contacto &&
                                     !resumenOperador.datos_adjudicatario?.telefono && !resumenOperador.telefono_contacto && (
                                        <p className="text-slate-500 text-xs italic py-2">
                                            Haz clic en "Buscar datos" para obtener contacto
                                        </p>
                                    )}
                                    {resumenOperador.datos_adjudicatario?.web && (
                                        <div>
                                            <p className="text-slate-400 text-xs mb-1">Web</p>
                                            <a
                                                href={resumenOperador.datos_adjudicatario.web.startsWith('http') ? resumenOperador.datos_adjudicatario.web : `https://${resumenOperador.datos_adjudicatario.web}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-blue-400 hover:underline flex items-center gap-1"
                                            >
                                                <ExternalLink className="w-3 h-3" />
                                                {resumenOperador.datos_adjudicatario.web}
                                            </a>
                                        </div>
                                    )}
                                    {resumenOperador.datos_adjudicatario?.direccion && (
                                        <div className="col-span-2">
                                            <p className="text-slate-400 text-xs mb-1">Dirección</p>
                                            <p className="text-slate-300 text-sm">
                                                {resumenOperador.datos_adjudicatario.direccion}
                                                {resumenOperador.datos_adjudicatario.localidad && `, ${resumenOperador.datos_adjudicatario.localidad}`}
                                                {resumenOperador.datos_adjudicatario.provincia && ` (${resumenOperador.datos_adjudicatario.provincia})`}
                                            </p>
                                        </div>
                                    )}
                                </div>
                                {resumenOperador.datos_adjudicatario?.actividad && (
                                    <div className="mt-3 pt-3 border-t border-blue-500/20">
                                        <p className="text-slate-400 text-xs mb-1">Actividad</p>
                                        <p className="text-slate-300 text-sm">{resumenOperador.datos_adjudicatario.actividad}</p>
                                    </div>
                                )}
                                {resumenOperador.datos_adjudicatario?.lugar_ejecucion && (
                                    <div className="mt-3 pt-3 border-t border-blue-500/20">
                                        <p className="text-slate-400 text-xs mb-1">Lugar de Ejecución</p>
                                        <p className="text-slate-300 text-sm">{resumenOperador.datos_adjudicatario.lugar_ejecucion}</p>
                                    </div>
                                )}
                                {resumenOperador.datos_adjudicatario?.es_pyme !== undefined && (
                                    <div className="mt-2">
                                        <Badge className={resumenOperador.datos_adjudicatario.es_pyme ? "bg-green-500/20 text-green-400" : "bg-slate-500/20 text-slate-400"}>
                                            {resumenOperador.datos_adjudicatario.es_pyme ? "PYME" : "Gran Empresa"}
                                        </Badge>
                                    </div>
                                )}
                                {resumenOperador.datos_adjudicatario?.fuente && (
                                    <div className="mt-2 flex justify-end">
                                        <span className="text-xs text-slate-500">
                                            Fuente: {resumenOperador.datos_adjudicatario.fuente} | Confianza: {resumenOperador.datos_adjudicatario.confianza}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* Datos del Órgano Contratante (EL CLIENTE) */}
                            {(resumenOperador.organo_contratacion || resumenOperador.datos_adjudicatario?.organo_contratacion) && (
                                <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20 overflow-hidden">
                                    <h3 className="text-green-400 font-semibold flex items-center gap-2 mb-3">
                                        <Target className="w-4 h-4" />
                                        Órgano Contratante (Cliente)
                                    </h3>
                                    <div className="space-y-3">
                                        <div>
                                            <p className="text-slate-400 text-xs mb-1">Entidad</p>
                                            <p className="text-white font-medium break-words">
                                                {resumenOperador.datos_adjudicatario?.organo_contratacion || resumenOperador.organo_contratacion}
                                            </p>
                                        </div>
                                        {/* Botones de acción rápida para órgano contratante */}
                                        {(resumenOperador.datos_adjudicatario?.organo_email || resumenOperador.datos_adjudicatario?.organo_telefono) && (
                                            <div className="flex gap-2 py-2">
                                                {resumenOperador.datos_adjudicatario?.organo_telefono && (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="flex-1 text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/20"
                                                        asChild
                                                    >
                                                        <a href={`tel:${resumenOperador.datos_adjudicatario.organo_telefono}`}>
                                                            <Phone className="w-4 h-4 mr-2" />
                                                            Llamar
                                                        </a>
                                                    </Button>
                                                )}
                                                {resumenOperador.datos_adjudicatario?.organo_email && (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="flex-1 text-purple-400 border-purple-500/30 hover:bg-purple-500/20"
                                                        asChild
                                                    >
                                                        <a href={`mailto:${resumenOperador.datos_adjudicatario.organo_email}`}>
                                                            <Mail className="w-4 h-4 mr-2" />
                                                            Email
                                                        </a>
                                                    </Button>
                                                )}
                                            </div>
                                        )}
                                        {resumenOperador.datos_adjudicatario?.organo_email && (
                                            <div>
                                                <p className="text-slate-400 text-xs mb-1">Email</p>
                                                <a
                                                    href={`mailto:${resumenOperador.datos_adjudicatario.organo_email}`}
                                                    className="text-green-400 hover:underline flex items-center gap-1 break-all"
                                                >
                                                    <Mail className="w-3 h-3 flex-shrink-0" />
                                                    {resumenOperador.datos_adjudicatario.organo_email}
                                                </a>
                                            </div>
                                        )}
                                        {resumenOperador.datos_adjudicatario?.organo_telefono && (
                                            <div>
                                                <p className="text-slate-400 text-xs mb-1">Teléfono</p>
                                                <a
                                                    href={`tel:${resumenOperador.datos_adjudicatario.organo_telefono}`}
                                                    className="text-green-400 hover:underline flex items-center gap-1"
                                                >
                                                    <Phone className="w-3 h-3 flex-shrink-0" />
                                                    {resumenOperador.datos_adjudicatario.organo_telefono}
                                                </a>
                                            </div>
                                        )}
                                        {resumenOperador.datos_adjudicatario?.organo_web && (
                                            <div>
                                                <p className="text-slate-400 text-xs mb-1">Web</p>
                                                <a
                                                    href={resumenOperador.datos_adjudicatario.organo_web.startsWith('http') ? resumenOperador.datos_adjudicatario.organo_web : `https://${resumenOperador.datos_adjudicatario.organo_web}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-green-400 hover:underline flex items-center gap-1 break-all"
                                                >
                                                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                                                    {resumenOperador.datos_adjudicatario.organo_web}
                                                </a>
                                            </div>
                                        )}
                                    </div>
                                    {resumenOperador.datos_adjudicatario?.financiacion_ue && (
                                        <div className="mt-3 pt-3 border-t border-green-500/20">
                                            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                                                <Euro className="w-3 h-3 mr-1" />
                                                {resumenOperador.datos_adjudicatario.financiacion_ue}
                                            </Badge>
                                            {resumenOperador.datos_adjudicatario.programa_financiacion && (
                                                <p className="text-slate-400 text-xs mt-1">{resumenOperador.datos_adjudicatario.programa_financiacion}</p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Datos del Contrato */}
                            {(resumenOperador.datos_adjudicatario?.importe_adjudicacion || resumenOperador.datos_adjudicatario?.fecha_adjudicacion) && (
                                <div className="p-4 rounded-lg bg-slate-800/50 overflow-hidden">
                                    <h3 className="text-slate-300 font-semibold flex items-center gap-2 mb-3">
                                        <FileText className="w-4 h-4" />
                                        Datos del Contrato
                                    </h3>
                                    <div className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                                        {resumenOperador.datos_adjudicatario?.importe_adjudicacion && (
                                            <div>
                                                <p className="text-slate-400 text-xs mb-1">Importe</p>
                                                <p className="text-cyan-400 font-medium">{resumenOperador.datos_adjudicatario.importe_adjudicacion}</p>
                                            </div>
                                        )}
                                        {resumenOperador.datos_adjudicatario?.fecha_adjudicacion && (
                                            <div>
                                                <p className="text-slate-400 text-xs mb-1">Fecha</p>
                                                <p className="text-slate-300">{resumenOperador.datos_adjudicatario.fecha_adjudicacion}</p>
                                            </div>
                                        )}
                                        {resumenOperador.datos_adjudicatario?.duracion_contrato && (
                                            <div>
                                                <p className="text-slate-400 text-xs mb-1">Duración</p>
                                                <p className="text-slate-300">{resumenOperador.datos_adjudicatario.duracion_contrato}</p>
                                            </div>
                                        )}
                                        {resumenOperador.datos_adjudicatario?.numero_ofertas && (
                                            <div>
                                                <p className="text-slate-400 text-xs mb-1">Ofertas</p>
                                                <p className="text-slate-300">{resumenOperador.datos_adjudicatario.numero_ofertas}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Botón Analizar Pliego - SIEMPRE visible */}
                            <div className="p-4 rounded-lg bg-slate-800/50">
                                <h3 className="text-slate-300 font-semibold flex items-center gap-2">
                                    <Brain className="w-4 h-4 text-green-400" />
                                    Análisis de Pliego con IA
                                </h3>
                                <p className="text-slate-500 text-xs mt-1 mb-3">
                                    Detecta oportunidades IT y servicios donde SRS puede ayudar
                                </p>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-green-400 border-green-500/30 hover:bg-green-500/20 w-full"
                                    onClick={() => handleAnalyzePliego(resumenOperador.oportunidad_id)}
                                    disabled={analyzingPliego[resumenOperador.oportunidad_id] || !resumenOperador.oportunidad_id}
                                >
                                    {analyzingPliego[resumenOperador.oportunidad_id] ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            Analizando...
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="w-4 h-4 mr-2" />
                                            Analizar Pliego
                                        </>
                                    )}
                                </Button>
                            </div>

                            {/* Documentos Disponibles (si existen) */}
                            {(resumenOperador.datos_adjudicatario?.documentos?.length > 0 ||
                              resumenOperador.pliegos?.url_pliego_tecnico ||
                              resumenOperador.datos_adjudicatario?.url_pliego_tecnico ||
                              (analisisPliego || resumenOperador.analisis_pliego)?.metadata?.url_pliego) && (
                                <div className="p-4 rounded-lg bg-slate-800/50">
                                    <h3 className="text-slate-300 font-semibold flex items-center gap-2 mb-3">
                                        <FileText className="w-4 h-4" />
                                        Documentos Disponibles
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {/* Pliego Técnico Analizado (destacado) */}
                                        {(resumenOperador.pliegos?.url_pliego_tecnico ||
                                          resumenOperador.datos_adjudicatario?.url_pliego_tecnico ||
                                          (analisisPliego || resumenOperador.analisis_pliego)?.metadata?.url_pliego) && (
                                            <a
                                                href={resumenOperador.pliegos?.url_pliego_tecnico ||
                                                      resumenOperador.datos_adjudicatario?.url_pliego_tecnico ||
                                                      (analisisPliego || resumenOperador.analisis_pliego)?.metadata?.url_pliego}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs px-2 py-1 bg-emerald-700 text-emerald-100 rounded hover:bg-emerald-600 flex items-center gap-1 font-medium"
                                            >
                                                <FileText className="w-3 h-3" />
                                                Pliego Técnico (PDF)
                                            </a>
                                        )}
                                        {/* Otros documentos */}
                                        {resumenOperador.datos_adjudicatario?.documentos?.slice(0, 8).map((doc, idx) => (
                                            <a
                                                key={idx}
                                                href={doc.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs px-2 py-1 bg-slate-700 text-slate-300 rounded hover:bg-slate-600 flex items-center gap-1"
                                            >
                                                <FileText className="w-3 h-3" />
                                                {doc.titulo} ({doc.tipo?.toUpperCase() || "DOC"})
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Resultado del Análisis de Pliego */}
                            {(analisisPliego || resumenOperador.analisis_pliego) && (
                                <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                                    <h3 className="text-green-400 font-semibold flex items-center gap-2 mb-3">
                                        <Brain className="w-4 h-4" />
                                        Oportunidades para SRS
                                        <Badge className="bg-green-500/20 text-green-300 text-xs ml-2">
                                            Pain Score: {(analisisPliego || resumenOperador.analisis_pliego)?.pain_score || 0}/100
                                        </Badge>
                                    </h3>

                                    {/* Componentes IT detectados */}
                                    {((analisisPliego || resumenOperador.analisis_pliego)?.componentes_it?.length > 0 ||
                                      (analisisPliego || resumenOperador.analisis_pliego)?.resumen_operador?.componentes_it?.length > 0) && (
                                        <div className="mb-4">
                                            <p className="text-slate-400 text-xs mb-2">Servicios IT donde SRS puede ayudar:</p>
                                            <div className="space-y-2">
                                                {((analisisPliego || resumenOperador.analisis_pliego)?.componentes_it ||
                                                  (analisisPliego || resumenOperador.analisis_pliego)?.resumen_operador?.componentes_it || []).slice(0, 5).map((comp, idx) => (
                                                    <div key={idx} className="p-2 bg-slate-800/50 rounded">
                                                        <div className="flex items-center gap-2">
                                                            <Badge className={`text-xs ${
                                                                comp.urgencia === 'critica' ? 'bg-red-500/20 text-red-300' :
                                                                comp.urgencia === 'alta' ? 'bg-orange-500/20 text-orange-300' :
                                                                'bg-slate-500/20 text-slate-300'
                                                            }`}>
                                                                {comp.tipo}
                                                            </Badge>
                                                            <span className="text-white text-sm font-medium">{comp.nombre}</span>
                                                        </div>
                                                        {comp.descripcion && (
                                                            <p className="text-slate-400 text-xs mt-1">{comp.descripcion}</p>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Tecnologías mencionadas */}
                                    {((analisisPliego || resumenOperador.analisis_pliego)?.resumen_operador?.tecnologias_mencionadas?.length > 0) && (
                                        <div className="mb-3">
                                            <p className="text-slate-400 text-xs mb-1">Tecnologías detectadas:</p>
                                            <div className="flex flex-wrap gap-1">
                                                {(analisisPliego || resumenOperador.analisis_pliego).resumen_operador.tecnologias_mencionadas.map((tech, idx) => (
                                                    <Badge key={idx} variant="outline" className="text-green-300 border-green-500/30 text-xs">
                                                        {tech}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Alertas importantes */}
                                    {((analisisPliego || resumenOperador.analisis_pliego)?.resumen_operador?.alertas?.length > 0) && (
                                        <div className="mt-3 p-2 bg-yellow-500/10 rounded border border-yellow-500/20">
                                            <p className="text-yellow-400 text-xs font-medium mb-1">Alertas:</p>
                                            {(analisisPliego || resumenOperador.analisis_pliego).resumen_operador.alertas.slice(0, 3).map((alerta, idx) => (
                                                <p key={idx} className="text-yellow-200 text-xs">• {alerta}</p>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Empresas Competidoras (otras que licitaron) */}
                            {resumenOperador.datos_adjudicatario?.empresas_competidoras?.length > 0 && (
                                <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20">
                                    <h3 className="text-amber-400 font-semibold flex items-center gap-2 mb-3">
                                        <Users className="w-4 h-4" />
                                        Otras Empresas que Licitaron
                                        <Badge className="bg-amber-500/20 text-amber-300 text-xs ml-2">
                                            {resumenOperador.datos_adjudicatario.empresas_competidoras.length} empresas
                                        </Badge>
                                    </h3>
                                    <p className="text-slate-400 text-xs mb-3">
                                        Estas empresas participaron en la licitación pero no ganaron. Son posibles clientes potenciales.
                                    </p>
                                    <div className="space-y-2">
                                        {resumenOperador.datos_adjudicatario.empresas_competidoras.map((empresa, idx) => (
                                            <div
                                                key={idx}
                                                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors"
                                            >
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-amber-400 font-bold text-sm">#{idx + 2}</span>
                                                        <p className="text-white font-medium truncate" title={empresa.nombre}>
                                                            {empresa.nombre}
                                                        </p>
                                                    </div>
                                                    <div className="flex items-center gap-3 mt-1">
                                                        <span className="text-slate-400 text-xs">
                                                            NIF: {empresa.nif}
                                                        </span>
                                                        {empresa.puntuacion && (
                                                            <span className="text-slate-400 text-xs flex items-center gap-1">
                                                                <Trophy className="w-3 h-3 text-amber-400" />
                                                                {empresa.puntuacion} pts
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                <TooltipProvider>
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <Button
                                                                size="sm"
                                                                variant="outline"
                                                                className="text-amber-400 border-amber-500/30 hover:bg-amber-500/20 h-8"
                                                                onClick={() => {
                                                                    // Crear lead desde competidor
                                                                    handleCreateLeadFromCompetidor(empresa);
                                                                }}
                                                            >
                                                                <UserPlus className="w-3 h-3 mr-1" />
                                                                Lead
                                                            </Button>
                                                        </TooltipTrigger>
                                                        <TooltipContent>
                                                            Crear lead desde esta empresa
                                                        </TooltipContent>
                                                    </Tooltip>
                                                </TooltipProvider>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Tecnologías */}
                            {resumenOperador.tecnologias_mencionadas?.length > 0 && (
                                <div className="p-4 rounded-lg bg-slate-800">
                                    <h3 className="text-green-400 font-semibold flex items-center gap-2 mb-2">
                                        <Server className="w-4 h-4" />
                                        Tecnologías
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {resumenOperador.tecnologias_mencionadas.map((tech, idx) => (
                                            <Badge key={idx} variant="outline" className="text-green-300 border-green-500/30">
                                                {tech}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Certificaciones */}
                            {resumenOperador.certificaciones_requeridas?.length > 0 && (
                                <div className="p-4 rounded-lg bg-slate-800">
                                    <h3 className="text-orange-400 font-semibold flex items-center gap-2 mb-2">
                                        <Shield className="w-4 h-4" />
                                        Certificaciones Requeridas
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {resumenOperador.certificaciones_requeridas.map((cert, idx) => (
                                            <Badge key={idx} variant="outline" className="text-orange-300 border-orange-500/30">
                                                {cert}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            )}

{/* Alertas eliminadas - ya se muestran en Oportunidades para SRS */}

                            {/* Metadata */}
                            <div className="flex justify-between items-center text-xs text-slate-500 pt-4 border-t border-slate-700">
                                <span>
                                    Confianza: {resumenOperador.confianza_analisis || "N/A"}
                                </span>
                                <span>
                                    {resumenOperador.paginas_analizadas} páginas • {resumenOperador.palabras_analizadas?.toLocaleString()} palabras
                                </span>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}
