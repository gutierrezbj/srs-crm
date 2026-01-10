import { useState, useEffect } from "react";
import axios from "axios";
import { 
  Users, 
  Phone, 
  CheckCircle2, 
  FileText, 
  Handshake, 
  Trophy, 
  XCircle,
  AlertTriangle,
  TrendingUp,
  Euro,
  Activity
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const stageConfig = {
  nuevo: { label: "Nuevos", icon: Users, color: "text-slate-400", bg: "bg-slate-400/10" },
  contactado: { label: "Contactados", icon: Phone, color: "text-blue-400", bg: "bg-blue-400/10" },
  calificado: { label: "Calificados", icon: CheckCircle2, color: "text-cyan-400", bg: "bg-cyan-400/10" },
  propuesta: { label: "Propuesta", icon: FileText, color: "text-purple-400", bg: "bg-purple-400/10" },
  negociacion: { label: "Negociación", icon: Handshake, color: "text-amber-400", bg: "bg-amber-400/10" },
  ganado: { label: "Ganados", icon: Trophy, color: "text-emerald-400", bg: "bg-emerald-400/10" },
  perdido: { label: "Perdidos", icon: XCircle, color: "text-red-400", bg: "bg-red-400/10" },
};

export default function Dashboard({ user }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/leads/stats`, { withCredentials: true });
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    } finally {
      setLoading(false);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-cyan-400 animate-pulse">Cargando dashboard...</div>
      </div>
    );
  }

  return (
    <div data-testid="dashboard-page" className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold theme-text mb-2">
          Hola, {user?.name?.split(" ")[0] || "Usuario"}
        </h1>
        <p className="theme-text-secondary">Resumen de tu pipeline de ventas</p>
      </div>

      {/* Main KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Pipeline Value */}
        <Card className="bg-gradient-to-br from-cyan-400/10 to-blue-600/10 border-cyan-400/20 hover:border-cyan-400/40 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium theme-text-secondary flex items-center gap-2">
              <Euro className="w-4 h-4" />
              Valor del Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold gradient-text" data-testid="pipeline-value">
              {formatCurrency(stats?.total_pipeline || 0)}
            </div>
            <p className="text-xs theme-text-muted mt-1">En oportunidades activas</p>
          </CardContent>
        </Card>

        {/* Total Leads */}
        <Card className="theme-bg-secondary border theme-border hover:border-cyan-400/20 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium theme-text-secondary flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Total Leads
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold theme-text" data-testid="total-leads">
              {stats?.total_leads || 0}
            </div>
            <p className="text-xs theme-text-muted mt-1">En el sistema</p>
          </CardContent>
        </Card>

        {/* Won Deals */}
        <Card className="theme-bg-secondary border theme-border hover:border-emerald-400/20 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium theme-text-secondary flex items-center gap-2">
              <Trophy className="w-4 h-4 text-emerald-400" />
              Ganados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-emerald-400" data-testid="won-deals">
              {stats?.stages_count?.ganado || 0}
            </div>
            <p className="text-xs theme-text-muted mt-1">Deals cerrados</p>
          </CardContent>
        </Card>

        {/* Leads without activity */}
        <Card className={`theme-bg-secondary border theme-border hover:border-amber-400/20 transition-colors ${
          stats?.leads_without_activity > 0 ? "border-amber-400/30" : ""
        }`}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium theme-text-secondary flex items-center gap-2">
              <AlertTriangle className={`w-4 h-4 ${stats?.leads_without_activity > 0 ? "text-amber-400" : ""}`} />
              Sin Actividad
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${stats?.leads_without_activity > 0 ? "text-amber-400" : "theme-text"}`} data-testid="inactive-leads">
              {stats?.leads_without_activity || 0}
            </div>
            <p className="text-xs theme-text-muted mt-1">Más de 7 días</p>
          </CardContent>
        </Card>
      </div>

      {/* Pipeline by Stage */}
      <div>
        <h2 className="text-xl font-semibold theme-text mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          Pipeline por Etapa
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
          {Object.entries(stageConfig).map(([key, config]) => {
            const Icon = config.icon;
            const count = stats?.stages_count?.[key] || 0;
            
            return (
              <Card 
                key={key} 
                className={`theme-bg-secondary border theme-border hover:border-cyan-400/20 transition-all hover:-translate-y-1`}
                data-testid={`stage-${key}`}
              >
                <CardContent className="p-4 text-center">
                  <div className={`w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center mx-auto mb-3`}>
                    <Icon className={`w-5 h-5 ${config.color}`} />
                  </div>
                  <div className="text-2xl font-bold theme-text mb-1">{count}</div>
                  <p className="text-xs theme-text-muted">{config.label}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Quick Info Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity Placeholder */}
        <Card className="theme-bg-secondary border theme-border">
          <CardHeader>
            <CardTitle className="text-lg font-semibold theme-text">Actividad Reciente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 theme-text-muted">
              <Activity className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>Las actividades recientes aparecerán aquí</p>
              <p className="text-xs mt-1">Añade notas y actividades a tus leads</p>
            </div>
          </CardContent>
        </Card>

        {/* Calendar Placeholder */}
        <Card className="theme-bg-secondary border theme-border">
          <CardHeader>
            <CardTitle className="text-lg font-semibold theme-text">Próximos Seguimientos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 theme-text-muted">
              <svg className="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p>Integración con Calendar</p>
              <p className="text-xs mt-1">Disponible en Fase 2</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
