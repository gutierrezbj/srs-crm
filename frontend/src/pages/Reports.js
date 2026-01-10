import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts";
import { 
  BarChart3, 
  PieChart as PieChartIcon, 
  Download,
  Calendar,
  TrendingUp,
  Users,
  Target,
  Zap,
  AlertTriangle
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { useTheme } from "@/context/ThemeContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Colors for charts
const COLORS_DARK = ['#22d3ee', '#3b82f6', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#ec4899'];
const COLORS_LIGHT = ['#0891b2', '#2563eb', '#7c3aed', '#d97706', '#059669', '#dc2626', '#db2777'];

const STAGE_COLORS = {
  nuevo: '#64748b',
  contactado: '#3b82f6',
  calificado: '#06b6d4',
  propuesta: '#8b5cf6',
  negociacion: '#f59e0b',
  ganado: '#10b981',
  perdido: '#ef4444',
};

const STAGE_LABELS = {
  nuevo: 'Nuevo',
  contactado: 'Contactado',
  calificado: 'Calificado',
  propuesta: 'Propuesta',
  negociacion: 'Negociación',
  ganado: 'Ganado',
  perdido: 'Perdido',
};

export default function Reports({ user }) {
  const { theme } = useTheme();
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState("month");
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");

  const COLORS = theme === 'dark' ? COLORS_DARK : COLORS_LIGHT;

  // Calculate date range
  const { fechaInicio, fechaFin } = useMemo(() => {
    const now = new Date();
    let start, end;

    switch (dateRange) {
      case "month":
        start = new Date(now.getFullYear(), now.getMonth(), 1);
        end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        break;
      case "quarter":
        const quarter = Math.floor(now.getMonth() / 3);
        start = new Date(now.getFullYear(), quarter * 3, 1);
        end = new Date(now.getFullYear(), quarter * 3 + 3, 0);
        break;
      case "year":
        start = new Date(now.getFullYear(), 0, 1);
        end = new Date(now.getFullYear(), 11, 31);
        break;
      case "custom":
        start = customStart ? new Date(customStart) : new Date(now.getFullYear(), 0, 1);
        end = customEnd ? new Date(customEnd) : now;
        break;
      default:
        start = new Date(now.getFullYear(), now.getMonth(), 1);
        end = now;
    }

    return {
      fechaInicio: start.toISOString().split("T")[0],
      fechaFin: end.toISOString().split("T")[0],
    };
  }, [dateRange, customStart, customEnd]);

  useEffect(() => {
    fetchReports();
  }, [fechaInicio, fechaFin]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API}/reports?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`,
        { withCredentials: true }
      );
      setReports(response.data);
    } catch (error) {
      toast.error("Error al cargar reportes");
      console.error("Error fetching reports:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (reportType) => {
    try {
      const response = await axios.get(
        `${API}/reports/export/${reportType}?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`,
        { withCredentials: true, responseType: "blob" }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `reporte_${reportType}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Reporte exportado");
    } catch (error) {
      toast.error("Error al exportar reporte");
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
    }).format(value);
  };

  // Transform data for charts
  const pipelineData = useMemo(() => {
    if (!reports?.pipeline_por_etapa) return [];
    return Object.entries(reports.pipeline_por_etapa).map(([stage, data]) => ({
      name: STAGE_LABELS[stage] || stage,
      cantidad: data.cantidad,
      valor: data.valor,
      fill: STAGE_COLORS[stage] || '#64748b',
    }));
  }, [reports]);

  const fuentesData = useMemo(() => {
    if (!reports?.leads_por_fuente) return [];
    return Object.entries(reports.leads_por_fuente)
      .map(([name, value], idx) => ({
        name,
        value,
        fill: COLORS[idx % COLORS.length],
      }))
      .sort((a, b) => b.value - a.value);
  }, [reports, COLORS]);

  const sectoresData = useMemo(() => {
    if (!reports?.leads_por_sector) return [];
    return Object.entries(reports.leads_por_sector)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [reports]);

  const serviciosData = useMemo(() => {
    if (!reports?.servicios_demandados) return [];
    return Object.entries(reports.servicios_demandados)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [reports]);

  const propietariosData = useMemo(() => {
    if (!reports?.leads_por_propietario) return [];
    return Object.entries(reports.leads_por_propietario)
      .map(([name, data]) => ({
        name,
        cantidad: data.cantidad,
        valor: data.valor,
      }))
      .sort((a, b) => b.valor - a.valor);
  }, [reports]);

  const perdidasData = useMemo(() => {
    if (!reports?.motivos_perdida) return [];
    return Object.entries(reports.motivos_perdida)
      .map(([name, value], idx) => ({
        name,
        value,
        fill: COLORS[idx % COLORS.length],
      }))
      .sort((a, b) => b.value - a.value);
  }, [reports, COLORS]);

  const textColor = theme === 'dark' ? '#94a3b8' : '#475569';
  const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

  if (loading && !reports) {
    return (
      <div className="flex items-center justify-center h-64">
        <div style={{ color: 'var(--theme-accent)' }} className="animate-pulse">Cargando reportes...</div>
      </div>
    );
  }

  return (
    <div data-testid="reports-page" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold theme-text flex items-center gap-2">
            <BarChart3 className="w-6 h-6" style={{ color: 'var(--theme-accent)' }} />
            Reportes
          </h1>
          <p className="theme-text-secondary text-sm">
            {reports?.total_leads || 0} leads en el período seleccionado
          </p>
        </div>

        {/* Date Filter */}
        <div className="flex flex-wrap items-end gap-3">
          <div className="space-y-1">
            <Label className="text-xs theme-text-secondary">Período</Label>
            <Select value={dateRange} onValueChange={setDateRange}>
              <SelectTrigger className="w-[160px] theme-bg-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="theme-bg-secondary" style={{ borderColor: 'var(--theme-border)' }}>
                <SelectItem value="month">Este mes</SelectItem>
                <SelectItem value="quarter">Este trimestre</SelectItem>
                <SelectItem value="year">Este año</SelectItem>
                <SelectItem value="custom">Personalizado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {dateRange === "custom" && (
            <>
              <div className="space-y-1">
                <Label className="text-xs theme-text-secondary">Desde</Label>
                <Input
                  type="date"
                  value={customStart}
                  onChange={(e) => setCustomStart(e.target.value)}
                  className="w-[140px] theme-bg-secondary"
                  style={{ borderColor: 'var(--theme-border)' }}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs theme-text-secondary">Hasta</Label>
                <Input
                  type="date"
                  value={customEnd}
                  onChange={(e) => setCustomEnd(e.target.value)}
                  className="w-[140px] theme-bg-secondary"
                  style={{ borderColor: 'var(--theme-border)' }}
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Pipeline por Etapa */}
        <Card className="theme-bg-secondary lg:col-span-2" style={{ border: '1px solid var(--theme-border)' }}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold theme-text flex items-center gap-2">
              <TrendingUp className="w-5 h-5" style={{ color: 'var(--theme-accent)' }} />
              Pipeline por Etapa
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport("pipeline")}
              className="theme-text-secondary"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pipelineData} layout="vertical" margin={{ left: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                  <XAxis type="number" tick={{ fill: textColor, fontSize: 12 }} />
                  <YAxis dataKey="name" type="category" tick={{ fill: textColor, fontSize: 12 }} width={75} />
                  <Tooltip
                    formatter={(value, name) => [
                      name === 'valor' ? formatCurrency(value) : value,
                      name === 'valor' ? 'Valor' : 'Cantidad'
                    ]}
                    contentStyle={{
                      backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
                      border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0'}`,
                      borderRadius: '8px',
                      color: theme === 'dark' ? '#e2e8f0' : '#0f172a'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="cantidad" name="Cantidad" radius={[0, 4, 4, 0]}>
                    {pipelineData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            {/* Data table */}
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b" style={{ borderColor: 'var(--theme-border)' }}>
                    <th className="text-left py-2 theme-text-secondary font-medium">Etapa</th>
                    <th className="text-right py-2 theme-text-secondary font-medium">Cantidad</th>
                    <th className="text-right py-2 theme-text-secondary font-medium">Valor EUR</th>
                  </tr>
                </thead>
                <tbody>
                  {pipelineData.map((item) => (
                    <tr key={item.name} className="border-b" style={{ borderColor: 'var(--theme-border)' }}>
                      <td className="py-2 theme-text">{item.name}</td>
                      <td className="text-right py-2 theme-text">{item.cantidad}</td>
                      <td className="text-right py-2" style={{ color: 'var(--theme-currency)' }}>{formatCurrency(item.valor)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* 2. Leads por Fuente */}
        <Card className="theme-bg-secondary" style={{ border: '1px solid var(--theme-border)' }}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold theme-text flex items-center gap-2">
              <Zap className="w-5 h-5" style={{ color: 'var(--theme-accent)' }} />
              Leads por Fuente
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport("fuentes")}
              className="theme-text-secondary"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            {fuentesData.length > 0 ? (
              <>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={fuentesData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={2}
                        dataKey="value"
                        label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                        labelLine={{ stroke: textColor }}
                      >
                        {fuentesData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
                          border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0'}`,
                          borderRadius: '8px',
                          color: theme === 'dark' ? '#e2e8f0' : '#0f172a'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-2 space-y-1">
                  {fuentesData.slice(0, 5).map((item) => (
                    <div key={item.name} className="flex justify-between text-sm">
                      <span className="theme-text-secondary">{item.name}</span>
                      <span className="theme-text font-medium">{item.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-[250px] flex items-center justify-center theme-text-muted">
                Sin datos
              </div>
            )}
          </CardContent>
        </Card>

        {/* 3. Leads por Sector */}
        <Card className="theme-bg-secondary" style={{ border: '1px solid var(--theme-border)' }}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold theme-text flex items-center gap-2">
              <Target className="w-5 h-5" style={{ color: 'var(--theme-accent)' }} />
              Leads por Sector
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport("sectores")}
              className="theme-text-secondary"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            {sectoresData.length > 0 ? (
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={sectoresData.slice(0, 8)} margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fill: textColor, fontSize: 10 }} 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis tick={{ fill: textColor, fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
                        border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0'}`,
                        borderRadius: '8px',
                        color: theme === 'dark' ? '#e2e8f0' : '#0f172a'
                      }}
                    />
                    <Bar dataKey="value" name="Leads" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[300px] flex items-center justify-center theme-text-muted">
                Sin datos
              </div>
            )}
          </CardContent>
        </Card>

        {/* 4. Servicios más demandados */}
        <Card className="theme-bg-secondary" style={{ border: '1px solid var(--theme-border)' }}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold theme-text flex items-center gap-2">
              <Zap className="w-5 h-5" style={{ color: 'var(--theme-accent)' }} />
              Servicios Demandados
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport("servicios")}
              className="theme-text-secondary"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            {serviciosData.length > 0 ? (
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={serviciosData.slice(0, 8)} layout="vertical" margin={{ left: 120 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis type="number" tick={{ fill: textColor, fontSize: 12 }} />
                    <YAxis 
                      dataKey="name" 
                      type="category" 
                      tick={{ fill: textColor, fontSize: 11 }} 
                      width={115}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
                        border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0'}`,
                        borderRadius: '8px',
                        color: theme === 'dark' ? '#e2e8f0' : '#0f172a'
                      }}
                    />
                    <Bar dataKey="value" name="Leads" fill={COLORS[1]} radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[300px] flex items-center justify-center theme-text-muted">
                Sin datos
              </div>
            )}
          </CardContent>
        </Card>

        {/* 5. Leads por Propietario */}
        <Card className="theme-bg-secondary" style={{ border: '1px solid var(--theme-border)' }}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold theme-text flex items-center gap-2">
              <Users className="w-5 h-5" style={{ color: 'var(--theme-accent)' }} />
              Leads por Propietario
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport("propietarios")}
              className="theme-text-secondary"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            {propietariosData.length > 0 ? (
              <>
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={propietariosData} margin={{ left: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                      <XAxis dataKey="name" tick={{ fill: textColor, fontSize: 12 }} />
                      <YAxis tick={{ fill: textColor, fontSize: 12 }} />
                      <Tooltip
                        formatter={(value, name) => [
                          name === 'valor' ? formatCurrency(value) : value,
                          name === 'valor' ? 'Valor' : 'Cantidad'
                        ]}
                        contentStyle={{
                          backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
                          border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0'}`,
                          borderRadius: '8px',
                          color: theme === 'dark' ? '#e2e8f0' : '#0f172a'
                        }}
                      />
                      <Legend />
                      <Bar dataKey="cantidad" name="Cantidad" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 space-y-2">
                  {propietariosData.map((item) => (
                    <div key={item.name} className="flex justify-between items-center text-sm p-2 rounded theme-bg-tertiary">
                      <span className="theme-text font-medium">{item.name}</span>
                      <div className="text-right">
                        <span className="theme-text-secondary mr-4">{item.cantidad} leads</span>
                        <span style={{ color: 'var(--theme-currency)' }}>{formatCurrency(item.valor)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-[250px] flex items-center justify-center theme-text-muted">
                Sin datos
              </div>
            )}
          </CardContent>
        </Card>

        {/* 6. Motivos de Pérdida */}
        <Card className="theme-bg-secondary" style={{ border: '1px solid var(--theme-border)' }}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold theme-text flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Motivos de Pérdida
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport("perdidas")}
              className="theme-text-secondary"
              style={{ borderColor: 'var(--theme-border)' }}
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </Button>
          </CardHeader>
          <CardContent>
            {perdidasData.length > 0 ? (
              <>
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={perdidasData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {perdidasData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
                          border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : '#e2e8f0'}`,
                          borderRadius: '8px',
                          color: theme === 'dark' ? '#e2e8f0' : '#0f172a'
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-2 space-y-1">
                  {perdidasData.map((item, idx) => (
                    <div key={item.name} className="flex justify-between items-center text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.fill }}></div>
                        <span className="theme-text-secondary">{item.name}</span>
                      </div>
                      <span className="theme-text font-medium">{item.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-[250px] flex items-center justify-center theme-text-muted">
                Sin leads perdidos
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
