import { useState } from "react";
import axios from "axios";
import {
    Plane,
    Search,
    Loader2,
    AlertCircle,
    CheckCircle2,
    TrendingUp,
    Target,
    FileText,
    Building2,
    Euro,
    Tag,
    Sparkles,
    Brain,
    Award,
    AlertTriangle,
    Info,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Alert,
    AlertDescription,
    AlertTitle,
} from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Score color utilities
const getScoreColor = (score) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    if (score >= 40) return "text-orange-400";
    return "text-red-400";
};

const getScoreBgGradient = (score) => {
    if (score >= 80) return "from-green-500/20 to-emerald-500/20";
    if (score >= 60) return "from-yellow-500/20 to-amber-500/20";
    if (score >= 40) return "from-orange-500/20 to-yellow-500/20";
    return "from-red-500/20 to-orange-500/20";
};

const getScoreBadgeClass = (score) => {
    if (score >= 80) return "bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg shadow-green-500/30";
    if (score >= 60) return "bg-gradient-to-r from-yellow-600 to-amber-600 text-white shadow-lg shadow-yellow-500/30";
    if (score >= 40) return "bg-gradient-to-r from-orange-600 to-yellow-600 text-white shadow-lg shadow-orange-500/30";
    return "bg-gradient-to-r from-red-600 to-orange-600 text-white shadow-lg shadow-red-500/30";
};

const getRelevanceBadge = (relevante) => {
    return relevante
        ? "bg-green-500/20 text-green-400 border-green-500/30"
        : "bg-gray-500/20 text-gray-400 border-gray-500/30";
};

export default function AnalizarDrones({ user }) {
    const [formData, setFormData] = useState({
        titulo: "",
        descripcion: "",
        cpv: "",
        presupuesto: "",
        organo_contratacion: "",
    });

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.titulo.trim()) {
            toast.error("El título es obligatorio");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const payload = {
                titulo: formData.titulo,
                ...(formData.descripcion && { descripcion: formData.descripcion }),
                ...(formData.cpv && { cpv: formData.cpv }),
                ...(formData.presupuesto && { presupuesto: parseFloat(formData.presupuesto) }),
                ...(formData.organo_contratacion && { organo_contratacion: formData.organo_contratacion }),
            };

            const response = await axios.post(
                `${API}/licitaciones/analizar`,
                payload,
                { withCredentials: true }
            );

            setResult(response.data);
            toast.success("Análisis completado exitosamente");
        } catch (err) {
            console.error("Error al analizar licitación:", err);
            const errorMessage = err.response?.data?.detail || "Error al analizar la licitación";
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setFormData({
            titulo: "",
            descripcion: "",
            cpv: "",
            presupuesto: "",
            organo_contratacion: "",
        });
        setResult(null);
        setError(null);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30">
                        <Plane className="w-6 h-6 text-cyan-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold theme-text">
                            Análisis de Licitaciones - Drones
                        </h1>
                        <p className="theme-text-muted text-sm">
                            Evalúa la relevancia de licitaciones para servicios con drones
                        </p>
                    </div>
                </div>
            </div>

            {/* Main content grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Form */}
                <Card className="theme-bg-secondary border" style={{ borderColor: 'var(--theme-border)' }}>
                    <div className="p-6 border-b" style={{ borderColor: 'var(--theme-border)' }}>
                        <div className="flex items-center gap-2">
                            <FileText className="w-5 h-5 text-cyan-400" />
                            <h2 className="text-lg font-semibold theme-text">
                                Datos de la Licitación
                            </h2>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="p-6 space-y-4">
                        {/* Título */}
                        <div className="space-y-2">
                            <Label htmlFor="titulo" className="theme-text flex items-center gap-1">
                                Título <span className="text-red-400">*</span>
                            </Label>
                            <Input
                                id="titulo"
                                name="titulo"
                                value={formData.titulo}
                                onChange={handleChange}
                                placeholder="Ej: Servicio de inspección con drones"
                                className="theme-bg-tertiary theme-text border"
                                style={{ borderColor: 'var(--theme-border)' }}
                                required
                            />
                        </div>

                        {/* Descripción */}
                        <div className="space-y-2">
                            <Label htmlFor="descripcion" className="theme-text">
                                Descripción
                            </Label>
                            <Textarea
                                id="descripcion"
                                name="descripcion"
                                value={formData.descripcion}
                                onChange={handleChange}
                                placeholder="Descripción detallada del servicio..."
                                className="theme-bg-tertiary theme-text border min-h-[100px]"
                                style={{ borderColor: 'var(--theme-border)' }}
                                rows={4}
                            />
                        </div>

                        {/* CPV */}
                        <div className="space-y-2">
                            <Label htmlFor="cpv" className="theme-text flex items-center gap-1">
                                <Tag className="w-4 h-4" />
                                Código CPV
                            </Label>
                            <Input
                                id="cpv"
                                name="cpv"
                                value={formData.cpv}
                                onChange={handleChange}
                                placeholder="Ej: 71355000-1"
                                className="theme-bg-tertiary theme-text border"
                                style={{ borderColor: 'var(--theme-border)' }}
                            />
                        </div>

                        {/* Presupuesto */}
                        <div className="space-y-2">
                            <Label htmlFor="presupuesto" className="theme-text flex items-center gap-1">
                                <Euro className="w-4 h-4" />
                                Presupuesto
                            </Label>
                            <Input
                                id="presupuesto"
                                name="presupuesto"
                                type="number"
                                step="0.01"
                                value={formData.presupuesto}
                                onChange={handleChange}
                                placeholder="Ej: 50000.00"
                                className="theme-bg-tertiary theme-text border"
                                style={{ borderColor: 'var(--theme-border)' }}
                            />
                        </div>

                        {/* Órgano de Contratación */}
                        <div className="space-y-2">
                            <Label htmlFor="organo_contratacion" className="theme-text flex items-center gap-1">
                                <Building2 className="w-4 h-4" />
                                Órgano de Contratación
                            </Label>
                            <Input
                                id="organo_contratacion"
                                name="organo_contratacion"
                                value={formData.organo_contratacion}
                                onChange={handleChange}
                                placeholder="Ej: Ayuntamiento de Madrid"
                                className="theme-bg-tertiary theme-text border"
                                style={{ borderColor: 'var(--theme-border)' }}
                            />
                        </div>

                        {/* Action buttons */}
                        <div className="flex gap-3 pt-4">
                            <Button
                                type="submit"
                                disabled={loading}
                                className="flex-1 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Analizando...
                                    </>
                                ) : (
                                    <>
                                        <Brain className="w-4 h-4 mr-2" />
                                        Analizar
                                    </>
                                )}
                            </Button>

                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleReset}
                                disabled={loading}
                                className="theme-border theme-text-secondary hover:theme-text"
                            >
                                Limpiar
                            </Button>
                        </div>
                    </form>
                </Card>

                {/* Results Panel */}
                <div className="space-y-4">
                    {error && (
                        <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertTitle>Error</AlertTitle>
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    {result && (
                        <>
                            {/* Score Card */}
                            <Card className={`theme-bg-secondary border-2 bg-gradient-to-br ${getScoreBgGradient(result.score)}`}
                                  style={{ borderColor: 'var(--theme-border)' }}>
                                <div className="p-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center gap-2">
                                            <Sparkles className="w-5 h-5 text-cyan-400" />
                                            <h3 className="text-lg font-semibold theme-text">
                                                Resultado del Análisis
                                            </h3>
                                        </div>
                                        <Badge className={getRelevanceBadge(result.relevante)}>
                                            {result.relevante ? (
                                                <>
                                                    <CheckCircle2 className="w-3 h-3 mr-1" />
                                                    Relevante
                                                </>
                                            ) : (
                                                <>
                                                    <AlertCircle className="w-3 h-3 mr-1" />
                                                    No Relevante
                                                </>
                                            )}
                                        </Badge>
                                    </div>

                                    {/* Score Display */}
                                    <div className="flex flex-col items-center justify-center py-6 space-y-4">
                                        <div className="relative">
                                            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-slate-800 to-slate-900 border-4 border-cyan-500/30 flex items-center justify-center">
                                                <div className="text-center">
                                                    <div className={`text-4xl font-bold ${getScoreColor(result.score)}`}>
                                                        {result.score}
                                                    </div>
                                                    <div className="text-xs theme-text-muted">de 100</div>
                                                </div>
                                            </div>
                                        </div>

                                        <Progress
                                            value={result.score}
                                            className="w-full h-2"
                                        />

                                        <Badge className={`${getScoreBadgeClass(result.score)} text-sm px-4 py-1`}>
                                            <Award className="w-4 h-4 mr-1" />
                                            Score: {result.score}
                                        </Badge>
                                    </div>
                                </div>
                            </Card>

                            {/* Category Card */}
                            {result.categoria_principal && (
                                <Card className="theme-bg-secondary border" style={{ borderColor: 'var(--theme-border)' }}>
                                    <div className="p-4">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Target className="w-4 h-4 text-cyan-400" />
                                            <span className="text-sm font-medium theme-text">
                                                Categoría Principal
                                            </span>
                                        </div>
                                        <Badge variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/30">
                                            {result.categoria_principal}
                                        </Badge>
                                    </div>
                                </Card>
                            )}

                            {/* CPV Matches */}
                            {result.cpv_matches && result.cpv_matches.length > 0 && (
                                <Card className="theme-bg-secondary border" style={{ borderColor: 'var(--theme-border)' }}>
                                    <div className="p-4">
                                        <div className="flex items-center gap-2 mb-3">
                                            <Tag className="w-4 h-4 text-cyan-400" />
                                            <span className="text-sm font-medium theme-text">
                                                Códigos CPV Detectados
                                            </span>
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {result.cpv_matches.map((cpv, index) => (
                                                <Badge
                                                    key={index}
                                                    variant="outline"
                                                    className="bg-blue-500/10 text-blue-400 border-blue-500/30"
                                                >
                                                    {cpv}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                </Card>
                            )}

                            {/* Keywords */}
                            {result.keywords_detectados && result.keywords_detectados.length > 0 && (
                                <Card className="theme-bg-secondary border" style={{ borderColor: 'var(--theme-border)' }}>
                                    <div className="p-4">
                                        <div className="flex items-center gap-2 mb-3">
                                            <Search className="w-4 h-4 text-cyan-400" />
                                            <span className="text-sm font-medium theme-text">
                                                Palabras Clave Detectadas
                                            </span>
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {result.keywords_detectados.map((keyword, index) => (
                                                <Badge
                                                    key={index}
                                                    variant="outline"
                                                    className="bg-purple-500/10 text-purple-400 border-purple-500/30"
                                                >
                                                    {keyword}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                </Card>
                            )}

                            {/* Recommendation */}
                            {result.recomendacion && (
                                <Alert className={result.relevante ? "border-green-500/30 bg-green-500/10" : "border-gray-500/30 bg-gray-500/10"}>
                                    <Info className={`h-4 w-4 ${result.relevante ? "text-green-400" : "text-gray-400"}`} />
                                    <AlertTitle className={result.relevante ? "text-green-400" : "text-gray-400"}>
                                        Recomendación
                                    </AlertTitle>
                                    <AlertDescription className="theme-text-secondary">
                                        {result.recomendacion}
                                    </AlertDescription>
                                </Alert>
                            )}
                        </>
                    )}

                    {!result && !error && !loading && (
                        <Card className="theme-bg-secondary border" style={{ borderColor: 'var(--theme-border)' }}>
                            <div className="p-12 text-center">
                                <div className="flex justify-center mb-4">
                                    <div className="p-4 rounded-full bg-cyan-500/10 border border-cyan-500/30">
                                        <Brain className="w-8 h-8 text-cyan-400" />
                                    </div>
                                </div>
                                <h3 className="text-lg font-medium theme-text mb-2">
                                    Sin resultados
                                </h3>
                                <p className="theme-text-muted text-sm">
                                    Completa el formulario y haz clic en "Analizar" para ver los resultados
                                </p>
                            </div>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
