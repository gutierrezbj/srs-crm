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
    Loader2
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

export default function Oportunidades({ user }) {
    const [oportunidades, setOportunidades] = useState([]);
    const [loading, setLoading] = useState(true);
    const [tipoSrsFilter, setTipoSrsFilter] = useState("all");
    const [tiposSrs, setTiposSrs] = useState([]);
    const [convertDialogOpen, setConvertDialogOpen] = useState(false);
    const [selectedOportunidad, setSelectedOportunidad] = useState(null);
    const [converting, setConverting] = useState(false);
    const [executingSpotter, setExecutingSpotter] = useState(false);
    const [reclassifying, setReclassifying] = useState(false);

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
    };

    const hasFilters = tipoSrsFilter !== "all";

    // Stats
    const totalOportunidades = oportunidades.length;
    const pendientes = oportunidades.filter(o => !o.convertido_lead).length;
    const convertidas = oportunidades.filter(o => o.convertido_lead).length;
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
                        onClick={handleReclassify}
                        disabled={reclassifying || executingSpotter}
                        variant="outline"
                        className="theme-text-secondary hover:theme-text"
                        style={{ borderColor: 'var(--theme-border)' }}
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
                        disabled={executingSpotter || reclassifying}
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
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
                        <Filter className="w-4 h-4 theme-text-muted" />
                        <span className="theme-text-secondary text-sm">Filtrar por:</span>
                    </div>
                    <div className="flex gap-2 flex-wrap">
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
                                    <TableHead className="theme-text-secondary font-semibold">
                                        <div className="flex items-center gap-1">
                                            Score
                                            <ArrowUpDown className="w-3 h-3" />
                                        </div>
                                    </TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Adjudicatario</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Importe</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Tipo SRS</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Días Restantes</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold">Estado</TableHead>
                                    <TableHead className="theme-text-secondary font-semibold text-right">Acciones</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {oportunidades.map((oportunidad) => (
                                    <TableRow
                                        key={oportunidad.oportunidad_id}
                                        className="border-b hover:bg-white/5 transition-colors"
                                        style={{ borderColor: 'var(--theme-border)' }}
                                        data-testid={`oportunidad-row-${oportunidad.oportunidad_id}`}
                                    >
                                        <TableCell>
                                            <Badge
                                                className={`${getScoreBadgeClass(oportunidad.score)} shadow-lg font-bold px-3 py-1`}
                                            >
                                                {oportunidad.score}
                                            </Badge>
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
        </div>
    );
}
