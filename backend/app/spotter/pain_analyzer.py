#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║                    PAIN ANALYZER - SpotterSRS                      ║
║           Análisis profundo de pliegos con IA                      ║
╠═══════════════════════════════════════════════════════════════════╣
║  Descarga y analiza pliegos técnicos para:                         ║
║    - Calcular pain score (0-100)                                   ║
║    - Identificar señales de urgencia                               ║
║    - Detectar requisitos de subcontratación                        ║
║    - Extraer recursos humanos necesarios                           ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import aiohttp
import asyncio
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar importar las librerías de IA
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai no disponible")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic no disponible")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.warning("beautifulsoup4 no disponible")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    try:
        import PyPDF2
        PYPDF2_AVAILABLE = True
    except ImportError:
        PYPDF2_AVAILABLE = False
        logger.warning("Ninguna librería PDF disponible (pdfplumber o PyPDF2)")


class AIProvider(Enum):
    """Proveedores de IA disponibles"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    NONE = "none"


@dataclass
class PainSignal:
    """Señal de dolor/urgencia detectada"""
    tipo: str  # "urgencia", "complejidad", "recursos", "riesgo"
    descripcion: str
    peso: int  # 1-10
    extracto: Optional[str] = None  # Texto del pliego donde se detectó


@dataclass
class RecursoRequerido:
    """Recurso humano o técnico requerido"""
    perfil: str
    cantidad: int
    dedicacion: str  # "tiempo_completo", "parcial", "puntual"
    certificaciones: List[str] = field(default_factory=list)
    experiencia_minima: Optional[str] = None


@dataclass
class AnalisisPain:
    """Resultado del análisis de pain"""
    oportunidad_id: str
    pain_score: int  # 0-100
    nivel_urgencia: str  # "critico", "alto", "medio", "bajo"
    senales_dolor: List[PainSignal] = field(default_factory=list)
    recursos_requeridos: List[RecursoRequerido] = field(default_factory=list)
    resumen_ejecutivo: str = ""
    oportunidades_subcontratacion: List[str] = field(default_factory=list)
    riesgos_detectados: List[str] = field(default_factory=list)
    keywords_clave: List[str] = field(default_factory=list)
    fecha_analisis: str = field(default_factory=lambda: datetime.now().isoformat())
    proveedor_ia: str = "none"
    pliego_analizado: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convierte a diccionario para MongoDB"""
        result = asdict(self)
        # Convertir señales y recursos a diccionarios
        result["senales_dolor"] = [asdict(s) for s in self.senales_dolor]
        result["recursos_requeridos"] = [asdict(r) for r in self.recursos_requeridos]
        return result


class PainAnalyzer:
    """Analizador de pain en pliegos usando IA"""

    def __init__(self):
        self.provider = self._detect_provider()
        self._setup_provider()

    def _detect_provider(self) -> AIProvider:
        """Detecta qué proveedor de IA está disponible"""
        # Preferir Gemini por coste
        if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            return AIProvider.GEMINI
        elif ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            return AIProvider.CLAUDE
        return AIProvider.NONE

    def _setup_provider(self):
        """Configura el proveedor de IA"""
        if self.provider == AIProvider.GEMINI:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Usando Gemini Flash para análisis")
        elif self.provider == AIProvider.CLAUDE:
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            logger.info("Usando Claude para análisis")
        else:
            logger.warning("Sin proveedor de IA configurado - análisis básico")

    async def descargar_pliego(self, url: str) -> Optional[str]:
        """Descarga y extrae texto de un pliego (PDF o HTML)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status != 200:
                        logger.error(f"Error descargando pliego: {response.status}")
                        return None

                    content_type = response.headers.get("Content-Type", "")
                    content = await response.read()

                    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
                        return self._extraer_texto_pdf(content)
                    elif "html" in content_type.lower():
                        return self._extraer_texto_html(content)
                    else:
                        # Intentar como texto plano
                        return content.decode("utf-8", errors="ignore")

        except Exception as e:
            logger.error(f"Error descargando pliego {url}: {e}")
            return None

    def _extraer_texto_pdf(self, content: bytes) -> Optional[str]:
        """Extrae texto de un PDF"""
        import io

        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    texto = ""
                    for page in pdf.pages[:50]:  # Limitar a 50 páginas
                        texto += page.extract_text() or ""
                    return texto[:100000]  # Limitar a 100k caracteres
            except Exception as e:
                logger.error(f"Error con pdfplumber: {e}")

        if PYPDF2_AVAILABLE:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                texto = ""
                for page in reader.pages[:50]:
                    texto += page.extract_text() or ""
                return texto[:100000]
            except Exception as e:
                logger.error(f"Error con PyPDF2: {e}")

        return None

    def _extraer_texto_html(self, content: bytes) -> Optional[str]:
        """Extrae texto de HTML"""
        if not BS4_AVAILABLE:
            # Fallback básico
            text = content.decode("utf-8", errors="ignore")
            text = re.sub(r"<[^>]+>", " ", text)
            return text[:100000]

        try:
            soup = BeautifulSoup(content, "html.parser")
            # Eliminar scripts y estilos
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=" ", strip=True)[:100000]
        except Exception as e:
            logger.error(f"Error parseando HTML: {e}")
            return None

    def _generar_prompt_analisis(self, texto_pliego: str, objeto: str, cpv: str) -> str:
        """Genera el prompt para análisis de IA"""
        return f"""Analiza este pliego de contratación pública española y genera un JSON con el análisis de "pain" (dolor/urgencia del adjudicatario).

CONTEXTO:
- Objeto del contrato: {objeto}
- Código CPV: {cpv}
- Somos SRS (System Rapid Solutions), empresa de servicios IT que ofrece subcontratación a empresas que ganan licitaciones.

TEXTO DEL PLIEGO (extracto):
{texto_pliego[:30000]}

GENERA UN JSON con esta estructura exacta:
{{
    "pain_score": <número 0-100, donde 100 = máxima urgencia/complejidad>,
    "nivel_urgencia": "<critico|alto|medio|bajo>",
    "resumen_ejecutivo": "<resumen de 2-3 frases del proyecto y por qué necesitan subcontratación>",
    "senales_dolor": [
        {{
            "tipo": "<urgencia|complejidad|recursos|riesgo>",
            "descripcion": "<descripción de la señal>",
            "peso": <1-10>,
            "extracto": "<texto literal del pliego que evidencia esto>"
        }}
    ],
    "recursos_requeridos": [
        {{
            "perfil": "<nombre del perfil técnico>",
            "cantidad": <número>,
            "dedicacion": "<tiempo_completo|parcial|puntual>",
            "certificaciones": ["<cert1>", "<cert2>"],
            "experiencia_minima": "<X años en Y>"
        }}
    ],
    "oportunidades_subcontratacion": [
        "<área donde SRS puede aportar valor>"
    ],
    "riesgos_detectados": [
        "<riesgo para el adjudicatario>"
    ],
    "keywords_clave": ["<keyword1>", "<keyword2>"]
}}

CRITERIOS PARA PAIN SCORE:
- +20: Plazo de ejecución < 3 meses
- +15: Requiere certificaciones específicas (ENS, ISO27001, fabricantes)
- +15: Menciona penalizaciones por incumplimiento
- +10: Multisede o dispersión geográfica
- +10: Tecnologías específicas complejas
- +10: Horarios especiales (24x7, festivos)
- +10: Volumen alto de recursos humanos
- +5: Urgencia explícita en el texto

Responde SOLO con el JSON, sin explicaciones adicionales."""

    async def _analizar_con_gemini(self, texto_pliego: str, objeto: str, cpv: str) -> Optional[Dict]:
        """Analiza usando Gemini"""
        try:
            prompt = self._generar_prompt_analisis(texto_pliego, objeto, cpv)
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                )
            )

            # Extraer JSON de la respuesta
            text = response.text
            # Buscar JSON en la respuesta
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return None

        except Exception as e:
            logger.error(f"Error con Gemini: {e}")
            return None

    async def _analizar_con_claude(self, texto_pliego: str, objeto: str, cpv: str) -> Optional[Dict]:
        """Analiza usando Claude"""
        try:
            prompt = self._generar_prompt_analisis(texto_pliego, objeto, cpv)
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-haiku-20240307",  # Usar Haiku por coste
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return None

        except Exception as e:
            logger.error(f"Error con Claude: {e}")
            return None

    def _analisis_basico(self, texto_pliego: str, objeto: str) -> Dict:
        """Análisis básico sin IA basado en keywords"""
        pain_score = 30  # Base
        senales = []
        texto_lower = texto_pliego.lower() if texto_pliego else objeto.lower()

        # Detectar urgencia
        urgencia_keywords = ["urgente", "inmediato", "improrrogable", "perentorio", "máxima prioridad"]
        for kw in urgencia_keywords:
            if kw in texto_lower:
                pain_score += 15
                senales.append({
                    "tipo": "urgencia",
                    "descripcion": f"Detectada palabra de urgencia: {kw}",
                    "peso": 8
                })
                break

        # Detectar penalizaciones
        if "penaliza" in texto_lower or "penalidad" in texto_lower:
            pain_score += 10
            senales.append({
                "tipo": "riesgo",
                "descripcion": "Menciona penalizaciones por incumplimiento",
                "peso": 7
            })

        # Detectar certificaciones
        certs = ["iso 27001", "ens", "itil", "pmp", "cisco", "microsoft", "vmware"]
        for cert in certs:
            if cert in texto_lower:
                pain_score += 5
                senales.append({
                    "tipo": "complejidad",
                    "descripcion": f"Requiere certificación: {cert.upper()}",
                    "peso": 6
                })

        # Detectar 24x7
        if "24x7" in texto_lower or "24 horas" in texto_lower or "7x24" in texto_lower:
            pain_score += 10
            senales.append({
                "tipo": "recursos",
                "descripcion": "Requiere cobertura 24x7",
                "peso": 8
            })

        # Detectar multisede
        if "multisede" in texto_lower or "múltiples sedes" in texto_lower or "dispersión geográfica" in texto_lower:
            pain_score += 10
            senales.append({
                "tipo": "complejidad",
                "descripcion": "Proyecto multisede / dispersión geográfica",
                "peso": 7
            })

        nivel = "bajo"
        if pain_score >= 80:
            nivel = "critico"
        elif pain_score >= 60:
            nivel = "alto"
        elif pain_score >= 40:
            nivel = "medio"

        return {
            "pain_score": min(100, pain_score),
            "nivel_urgencia": nivel,
            "resumen_ejecutivo": f"Análisis básico del contrato: {objeto[:200]}",
            "senales_dolor": senales,
            "recursos_requeridos": [],
            "oportunidades_subcontratacion": [],
            "riesgos_detectados": [],
            "keywords_clave": []
        }

    async def analizar_oportunidad(
        self,
        oportunidad_id: str,
        objeto: str,
        cpv: str = "",
        url_pliego: Optional[str] = None
    ) -> AnalisisPain:
        """
        Analiza una oportunidad y calcula su pain score.

        Args:
            oportunidad_id: ID único de la oportunidad
            objeto: Descripción del objeto del contrato
            cpv: Código CPV
            url_pliego: URL del pliego técnico (opcional)

        Returns:
            AnalisisPain con el resultado del análisis
        """
        texto_pliego = None
        pliego_analizado = False

        # Intentar descargar pliego si hay URL
        if url_pliego:
            logger.info(f"Descargando pliego: {url_pliego}")
            texto_pliego = await self.descargar_pliego(url_pliego)
            if texto_pliego:
                pliego_analizado = True
                logger.info(f"Pliego descargado: {len(texto_pliego)} caracteres")

        # Si no hay pliego, usar el objeto como texto
        texto_para_analisis = texto_pliego or objeto

        # Analizar según proveedor disponible
        resultado = None
        proveedor_usado = "none"

        if self.provider == AIProvider.GEMINI and texto_para_analisis:
            resultado = await self._analizar_con_gemini(texto_para_analisis, objeto, cpv)
            proveedor_usado = "gemini"
        elif self.provider == AIProvider.CLAUDE and texto_para_analisis:
            resultado = await self._analizar_con_claude(texto_para_analisis, objeto, cpv)
            proveedor_usado = "claude"

        # Fallback a análisis básico
        if not resultado:
            resultado = self._analisis_basico(texto_para_analisis, objeto)
            proveedor_usado = "basico"

        # Construir respuesta
        try:
            senales = [
                PainSignal(
                    tipo=s.get("tipo", ""),
                    descripcion=s.get("descripcion", ""),
                    peso=s.get("peso", 5),
                    extracto=s.get("extracto")
                )
                for s in resultado.get("senales_dolor", [])
            ]

            recursos = [
                RecursoRequerido(
                    perfil=r.get("perfil", ""),
                    cantidad=r.get("cantidad", 1),
                    dedicacion=r.get("dedicacion", "tiempo_completo"),
                    certificaciones=r.get("certificaciones", []),
                    experiencia_minima=r.get("experiencia_minima")
                )
                for r in resultado.get("recursos_requeridos", [])
            ]

            return AnalisisPain(
                oportunidad_id=oportunidad_id,
                pain_score=resultado.get("pain_score", 30),
                nivel_urgencia=resultado.get("nivel_urgencia", "medio"),
                senales_dolor=senales,
                recursos_requeridos=recursos,
                resumen_ejecutivo=resultado.get("resumen_ejecutivo", ""),
                oportunidades_subcontratacion=resultado.get("oportunidades_subcontratacion", []),
                riesgos_detectados=resultado.get("riesgos_detectados", []),
                keywords_clave=resultado.get("keywords_clave", []),
                proveedor_ia=proveedor_usado,
                pliego_analizado=pliego_analizado
            )

        except Exception as e:
            logger.error(f"Error construyendo AnalisisPain: {e}")
            return AnalisisPain(
                oportunidad_id=oportunidad_id,
                pain_score=30,
                nivel_urgencia="medio",
                error=str(e)
            )


# Singleton para reutilizar
_analyzer_instance: Optional[PainAnalyzer] = None


def get_pain_analyzer() -> PainAnalyzer:
    """Obtiene instancia singleton del analizador"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = PainAnalyzer()
    return _analyzer_instance


async def analizar_pain_oportunidad(
    oportunidad_id: str,
    objeto: str,
    cpv: str = "",
    url_pliego: Optional[str] = None
) -> Dict:
    """
    Función de conveniencia para analizar una oportunidad.

    Returns:
        Diccionario con el análisis de pain listo para MongoDB
    """
    analyzer = get_pain_analyzer()
    resultado = await analyzer.analizar_oportunidad(
        oportunidad_id=oportunidad_id,
        objeto=objeto,
        cpv=cpv,
        url_pliego=url_pliego
    )
    return resultado.to_dict()


# Para testing
if __name__ == "__main__":
    async def test():
        resultado = await analizar_pain_oportunidad(
            oportunidad_id="TEST-001",
            objeto="Servicio de soporte técnico informático 24x7 con certificación ISO 27001 para multisede urgente",
            cpv="72000000"
        )
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    asyncio.run(test())
