import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import {
  Plane,
  ExternalLink,
  Filter,
  RefreshCw,
  Eye,
  Trash2,
  Star,
  Clock,
  Euro,
  Building2,
  Tag,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Bookmark
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Estados posibles
const ESTADOS = [
  { value: "nueva", label: "Nueva", icon: AlertCircle, color: "bg-blue-500" },
  { value: "vista", label: "Vista", icon: Eye, color: "bg-gray-500" },
  { value: "en_seguimiento", label: "En Seguimiento", icon: Bookmark, color: "bg-yellow-500" },
  { value: "descartada", label: "Descartada", icon: XCircle, color: "bg-red-500" },
];

// Funcion para color de score
const getScoreColor = (score) => {
  if (score >= 80) return "bg-red-500 text-white";
  if (score >= 60) return "bg-orange-500 text-white";
  if (score >= 40) return "bg-yellow-500 text-black";
  return "bg-gray-400 text-white";
};

// Funcion para color de dias restantes
const getDiasColor = (dias) => {
  if (dias === null || dias === undefined) return "text-gray-400";
  if (dias <= 7) return "text-red-500 font-bold";
  if (dias <= 15) return "text-orange-500 font-semibold";
  if (dias <= 30) return "text-yellow-600";
  return "text-green-600";
};

export default function LicitacionesDrones({ user }) {
  const [licitaciones, setLicitaciones] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedLicitacion, setSelectedLicitacion] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Filtros
  const [scoreMin, setScoreMin] = useState("");
  const [diasRestantes, setDiasRestantes] = useState("");
  const [categoriaFilter, setCategoriaFilter] = useState("");
  const [estadoFilter, setEstadoFilter] = useState("");

  // Cargar licitaciones
  const fetchLicitaciones = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (scoreMin && scoreMin !== "all") params.append("score_min", scoreMin);
      if (diasRestantes && diasRestantes !== "all") params.append("dias_restantes", diasRestantes);
      if (categoriaFilter && categoriaFilter !== "all") params.append("categoria", categoriaFilter);
      if (estadoFilter && estadoFilter !== "all") params.append("estado", estadoFilter);

      const [licRes, statsRes] = await Promise.all([
        axios.get(`${API}/licitaciones-drones?${params.toString()}`),
        axios.get(`${API}/licitaciones-drones/stats`)
      ]);

      setLicitaciones(licRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error("Error cargando licitaciones:", error);
      toast.error("Error cargando licitaciones");
    } finally {
      setLoading(false);
    }
  }, [scoreMin, diasRestantes, categoriaFilter, estadoFilter]);

  useEffect(() => {
    fetchLicitaciones();
  }, [fetchLicitaciones]);

  // Cambiar estado de licitacion
  const cambiarEstado = async (licitacionId, nuevoEstado) => {
    try {
      await axios.patch(`${API}/licitaciones-drones/${licitacionId}/estado`, {
        estado: nuevoEstado
      });
      toast.success(`Estado actualizado a ${nuevoEstado}`);
      fetchLicitaciones();
    } catch (error) {
      console.error("Error actualizando estado:", error);
      toast.error("Error actualizando estado");
    }
  };

  // Abrir detalle
  const openDetalle = (licitacion) => {
    setSelectedLicitacion(licitacion);
    setDialogOpen(true);
    // Marcar como vista si es nueva
    if (licitacion.estado === "nueva") {
      cambiarEstado(licitacion.licitacion_id, "vista");
    }
  };

  // Formatear presupuesto
  const formatPresupuesto = (valor) => {
    if (!valor) return "-";
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
      maximumFractionDigits: 0
    }).format(valor);
  };

  // Categorias unicas para filtro
  const categorias = [...new Set(licitaciones.map(l => l.categoria_principal).filter(Boolean))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold theme-text flex items-center gap-2">
            <Plane className="w-7 h-7 text-cyan-400" />
            Licitaciones Drones
          </h1>
          <p className="text-sm theme-text-muted mt-1">
            Oportunidades de licitacion detectadas para servicios de drones
          </p>
        </div>
        <Button
          onClick={fetchLicitaciones}
          variant="outline"
          className="border-cyan-400/30 hover:bg-cyan-400/10"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Actualizar
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="theme-bg-secondary rounded-lg p-4 border" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex items-center justify-between">
              <span className="text-sm theme-text-muted">Total</span>
              <Tag className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-2xl font-bold theme-text">{stats.total}</p>
          </div>
          <div className="theme-bg-secondary rounded-lg p-4 border" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex items-center justify-between">
              <span className="text-sm theme-text-muted">Urgentes</span>
              <Clock className="w-4 h-4 text-red-400" />
            </div>
            <p className="text-2xl font-bold text-red-400">{stats.urgentes}</p>
          </div>
          <div className="theme-bg-secondary rounded-lg p-4 border" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex items-center justify-between">
              <span className="text-sm theme-text-muted">Alta Prioridad</span>
              <Star className="w-4 h-4 text-orange-400" />
            </div>
            <p className="text-2xl font-bold text-orange-400">{stats.por_score?.alta || 0}</p>
          </div>
          <div className="theme-bg-secondary rounded-lg p-4 border" style={{ borderColor: 'var(--theme-border)' }}>
            <div className="flex items-center justify-between">
              <span className="text-sm theme-text-muted">Valor Total</span>
              <Euro className="w-4 h-4 text-green-400" />
            </div>
            <p className="text-xl font-bold text-green-400">
              {formatPresupuesto(stats.valor_total)}
            </p>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="theme-bg-secondary rounded-lg p-4 border" style={{ borderColor: 'var(--theme-border)' }}>
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 theme-text-muted" />
          <span className="text-sm font-medium theme-text">Filtros</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="text-xs theme-text-muted mb-1 block">Score minimo</label>
            <Select value={scoreMin} onValueChange={setScoreMin}>
              <SelectTrigger className="w-full theme-bg border-slate-600">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="80">80+ (Alta)</SelectItem>
                <SelectItem value="60">60+ (Media)</SelectItem>
                <SelectItem value="40">40+ (Baja)</SelectItem>
                <SelectItem value="30">30+</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs theme-text-muted mb-1 block">Dias restantes</label>
            <Select value={diasRestantes} onValueChange={setDiasRestantes}>
              <SelectTrigger className="w-full theme-bg border-slate-600">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="7">7 dias o menos</SelectItem>
                <SelectItem value="15">15 dias o menos</SelectItem>
                <SelectItem value="30">30 dias o menos</SelectItem>
                <SelectItem value="60">60 dias o menos</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs theme-text-muted mb-1 block">Categoria</label>
            <Select value={categoriaFilter} onValueChange={setCategoriaFilter}>
              <SelectTrigger className="w-full theme-bg border-slate-600">
                <SelectValue placeholder="Todas" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                {categorias.map(cat => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs theme-text-muted mb-1 block">Estado</label>
            <Select value={estadoFilter} onValueChange={setEstadoFilter}>
              <SelectTrigger className="w-full theme-bg border-slate-600">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                {ESTADOS.map(e => (
                  <SelectItem key={e.value} value={e.value}>{e.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Tabla de licitaciones */}
      <div className="theme-bg-secondary rounded-lg border overflow-hidden" style={{ borderColor: 'var(--theme-border)' }}>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
          </div>
        ) : licitaciones.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Plane className="w-12 h-12 text-gray-500 mb-4" />
            <p className="theme-text-muted">No se encontraron licitaciones</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-b" style={{ borderColor: 'var(--theme-border)' }}>
                  <TableHead className="w-16">Score</TableHead>
                  <TableHead>Titulo</TableHead>
                  <TableHead className="w-32">Presupuesto</TableHead>
                  <TableHead className="w-24">Dias</TableHead>
                  <TableHead className="w-40">Categoria</TableHead>
                  <TableHead className="w-28">Estado</TableHead>
                  <TableHead className="w-24">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {licitaciones.map((lic) => {
                  const estadoInfo = ESTADOS.find(e => e.value === lic.estado) || ESTADOS[0];
                  const EstadoIcon = estadoInfo.icon;

                  return (
                    <TableRow
                      key={lic.licitacion_id}
                      className="border-b hover:bg-cyan-400/5 cursor-pointer"
                      style={{ borderColor: 'var(--theme-border)' }}
                      onClick={() => openDetalle(lic)}
                    >
                      <TableCell>
                        <span className={`inline-flex items-center justify-center w-10 h-10 rounded-lg font-bold ${getScoreColor(lic.score)}`}>
                          {lic.score}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-md">
                          <p className="font-medium theme-text truncate" title={lic.titulo}>
                            {lic.titulo}
                          </p>
                          <p className="text-xs theme-text-muted truncate">
                            {lic.organo_contratacion}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell className="font-medium text-green-400">
                        {formatPresupuesto(lic.presupuesto)}
                      </TableCell>
                      <TableCell>
                        <span className={getDiasColor(lic.dias_restantes)}>
                          {lic.dias_restantes !== null && lic.dias_restantes !== undefined
                            ? `${lic.dias_restantes} dias`
                            : "-"
                          }
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs">
                          {lic.categoria_principal || "Sin categoria"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={lic.estado}
                          onValueChange={(value) => {
                            cambiarEstado(lic.licitacion_id, value);
                          }}
                        >
                          <SelectTrigger
                            className="w-full h-8 text-xs"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <div className="flex items-center gap-1">
                              <EstadoIcon className="w-3 h-3" />
                              <span>{estadoInfo.label}</span>
                            </div>
                          </SelectTrigger>
                          <SelectContent>
                            {ESTADOS.map(e => (
                              <SelectItem key={e.value} value={e.value}>
                                <div className="flex items-center gap-2">
                                  <e.icon className="w-3 h-3" />
                                  {e.label}
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={(e) => {
                              e.stopPropagation();
                              window.open(lic.url_licitacion, "_blank");
                            }}
                            title="Ver en PLACSP"
                          >
                            <ExternalLink className="w-4 h-4 text-cyan-400" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {/* Dialog de detalle */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl theme-bg-secondary overflow-hidden border" style={{ borderColor: 'var(--theme-border)' }}>
          {selectedLicitacion && (
            <>
              <DialogHeader>
                <DialogTitle className="theme-text flex items-center gap-2">
                  <span className={`inline-flex items-center justify-center w-8 h-8 rounded-lg font-bold text-sm ${getScoreColor(selectedLicitacion.score)}`}>
                    {selectedLicitacion.score}
                  </span>
                  <span className="truncate">{selectedLicitacion.titulo}</span>
                </DialogTitle>
                <DialogDescription className="theme-text-muted">
                  Expediente: {selectedLicitacion.expediente}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 mt-4">
                {/* Info principal */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs theme-text-muted">Presupuesto</label>
                    <p className="font-bold text-lg text-green-400">
                      {formatPresupuesto(selectedLicitacion.presupuesto)}
                    </p>
                  </div>
                  <div>
                    <label className="text-xs theme-text-muted">Dias Restantes</label>
                    <p className={`font-bold text-lg ${getDiasColor(selectedLicitacion.dias_restantes)}`}>
                      {selectedLicitacion.dias_restantes !== null
                        ? `${selectedLicitacion.dias_restantes} dias`
                        : "Sin fecha limite"
                      }
                    </p>
                  </div>
                </div>

                {/* Organo contratacion */}
                <div>
                  <label className="text-xs theme-text-muted flex items-center gap-1">
                    <Building2 className="w-3 h-3" />
                    Organo de Contratacion
                  </label>
                  <p className="theme-text">{selectedLicitacion.organo_contratacion}</p>
                </div>

                {/* Descripcion */}
                <div>
                  <label className="text-xs theme-text-muted">Descripcion</label>
                  <p className="theme-text text-sm">{selectedLicitacion.descripcion}</p>
                </div>

                {/* Categoria y CPV */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs theme-text-muted">Categoria</label>
                    <Badge variant="outline" className="mt-1">
                      {selectedLicitacion.categoria_principal || "Sin categoria"}
                    </Badge>
                  </div>
                  <div>
                    <label className="text-xs theme-text-muted">CPV</label>
                    <p className="theme-text font-mono text-sm">{selectedLicitacion.cpv || "-"}</p>
                  </div>
                </div>

                {/* Keywords */}
                {selectedLicitacion.keywords_detectados?.length > 0 && (
                  <div>
                    <label className="text-xs theme-text-muted">Keywords Detectados</label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedLicitacion.keywords_detectados.map((kw, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          {kw}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Fechas */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs theme-text-muted">Fecha Publicacion</label>
                    <p className="theme-text text-sm">{selectedLicitacion.fecha_publicacion || "-"}</p>
                  </div>
                  <div>
                    <label className="text-xs theme-text-muted">Fecha Limite</label>
                    <p className="theme-text text-sm">{selectedLicitacion.fecha_limite || "-"}</p>
                  </div>
                </div>

                {/* Botones de accion */}
                <div className="flex gap-2 pt-4 border-t" style={{ borderColor: 'var(--theme-border)' }}>
                  <Button
                    onClick={() => window.open(selectedLicitacion.url_licitacion, "_blank")}
                    className="flex-1 bg-cyan-500 hover:bg-cyan-600"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Ver en PLACSP
                  </Button>
                  {selectedLicitacion.url_pliego && (
                    <Button
                      variant="outline"
                      onClick={() => window.open(selectedLicitacion.url_pliego, "_blank")}
                      className="border-cyan-400/30 hover:bg-cyan-400/10"
                    >
                      Ver Pliego
                    </Button>
                  )}
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
