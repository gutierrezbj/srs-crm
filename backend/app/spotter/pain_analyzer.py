#!/usr/bin/env python3
"""
Pain Analyzer - SpotterSRS
Análisis rápido de oportunidades con IA (sin PDFs para velocidad)
Fallback: OpenAI -> Gemini -> Claude -> Básico
"""

import os
import re
import json
import asyncio
from typing import Optional, Dict, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detectar proveedores disponibles
OPENAI_AVAILABLE = False
GEMINI_AVAILABLE = False
ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("openai no disponible")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai no disponible")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    logger.warning("anthropic no disponible")


class AIProvider(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    BASICO = "basico"


@dataclass
class PainSignal:
    tipo: str
    descripcion: str
    peso: int
    extracto: Optional[str] = None


@dataclass
class RecursoRequerido:
    perfil: str
    cantidad: int
    dedicacion: str
    certificaciones: List[str] = field(default_factory=list)
    experiencia_minima: Optional[str] = None


@dataclass
class AnalisisPain:
    oportunidad_id: str
    pain_score: int
    nivel_urgencia: str
    senales_dolor: List[PainSignal] = field(default_factory=list)
    recursos_requeridos: List[RecursoRequerido] = field(default_factory=list)
    resumen_ejecutivo: str = ""
    oportunidades_subcontratacion: List[str] = field(default_factory=list)
    riesgos_detectados: List[str] = field(default_factory=list)
    keywords_clave: List[str] = field(default_factory=list)
    fecha_analisis: str = field(default_factory=lambda: datetime.now().isoformat())
    proveedor_ia: str = "basico"
    pliego_analizado: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["senales_dolor"] = [asdict(s) for s in self.senales_dolor]
        result["recursos_requeridos"] = [asdict(r) for r in self.recursos_requeridos]
        return result


class PainAnalyzer:
    """Analizador de pain con multi-IA y fallback"""

    # CPVs de alto valor para SRS (IT/Infraestructura)
    CPV_ALTO_VALOR = {
        "72": 25,  # Servicios IT
        "48": 20,  # Software
        "32": 20,  # Telecomunicaciones
        "50": 15,  # Mantenimiento
        "79": 10,  # Servicios empresariales
    }

    # Keywords que indican alta complejidad/oportunidad
    KEYWORDS_ALTO_PAIN = {
        "24x7": 15, "24/7": 15, "7x24": 15,
        "certificación": 10, "certificacion": 10,
        "ens": 12, "iso 27001": 12, "iso27001": 12,
        "cpd": 15, "centro de datos": 15, "datacenter": 15,
        "infraestructura": 12, "sistemas": 8,
        "soporte": 10, "helpdesk": 12, "service desk": 12,
        "penalización": 10, "penalizacion": 10, "sla": 12,
        "urgente": 15, "inmediato": 12,
        "multisede": 12, "nacional": 10,
        "técnico": 8, "tecnico": 8,
        "microinformática": 10, "microinformatica": 10,
        "redes": 10, "comunicaciones": 10,
        "ciberseguridad": 15, "seguridad": 8,
        "cloud": 10, "nube": 10,
        "virtualización": 10, "virtualizacion": 10,
    }

    def __init__(self):
        self.providers = self._init_providers()
        logger.info(f"Proveedores IA disponibles: {[p.value for p in self.providers]}")

    def _init_providers(self) -> List[AIProvider]:
        """Inicializa proveedores en orden de preferencia"""
        providers = []

        # OpenAI primero (más rápido)
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            providers.append(AIProvider.OPENAI)
            logger.info("OpenAI configurado")

        # Gemini segundo
        if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            providers.append(AIProvider.GEMINI)
            logger.info("Gemini configurado")

        # Claude tercero
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            providers.append(AIProvider.CLAUDE)
            logger.info("Claude configurado")

        # Siempre tener básico como fallback
        providers.append(AIProvider.BASICO)
        return providers

    def _generar_prompt(self, objeto: str, cpv: str, importe: float = 0) -> str:
        """Prompt corto y directo para respuesta rápida"""
        return f"""Analiza esta licitación y devuelve JSON con pain_score (0-100).

LICITACIÓN:
- Objeto: {objeto[:800]}
- CPV: {cpv}
- Importe: {importe:,.0f}€

CRITERIOS PAIN SCORE:
+20: CPD/Infraestructura/Sistemas críticos
+15: 24x7/Urgente/Penalizaciones SLA
+12: ENS/ISO27001/Certificaciones
+10: Multisede/Nacional/Soporte IT
+8: Telecomunicaciones/Redes

RESPONDE SOLO JSON:
{{"pain_score":N,"nivel_urgencia":"critico|alto|medio|bajo","resumen_ejecutivo":"1 frase","senales_dolor":[{{"tipo":"urgencia|complejidad|recursos","descripcion":"breve","peso":1-10}}],"keywords_clave":["kw1","kw2"]}}"""

    async def _analizar_openai(self, objeto: str, cpv: str, importe: float) -> Optional[Dict]:
        """Análisis con OpenAI GPT-3.5-turbo (muy rápido)"""
        try:
            prompt = self._generar_prompt(objeto, cpv, importe)

            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3,
                    timeout=15
                ),
                timeout=20
            )

            text = response.choices[0].message.content
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return None

        except asyncio.TimeoutError:
            logger.error("Timeout OpenAI (20s)")
            return None
        except Exception as e:
            logger.error(f"Error OpenAI: {e}")
            return None

    async def _analizar_gemini(self, objeto: str, cpv: str, importe: float) -> Optional[Dict]:
        """Análisis con Gemini Flash"""
        try:
            prompt = self._generar_prompt(objeto, cpv, importe)

            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.gemini_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=500,
                    )
                ),
                timeout=30
            )

            text = response.text
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return None

        except asyncio.TimeoutError:
            logger.error("Timeout Gemini (30s)")
            return None
        except Exception as e:
            logger.error(f"Error Gemini: {e}")
            return None

    async def _analizar_claude(self, objeto: str, cpv: str, importe: float) -> Optional[Dict]:
        """Análisis con Claude Haiku"""
        try:
            prompt = self._generar_prompt(objeto, cpv, importe)

            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.claude_client.messages.create,
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=30
            )

            text = response.content[0].text
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return None

        except asyncio.TimeoutError:
            logger.error("Timeout Claude (30s)")
            return None
        except Exception as e:
            logger.error(f"Error Claude: {e}")
            return None

    def _analisis_basico(self, objeto: str, cpv: str, importe: float = 0) -> Dict:
        """Análisis rápido basado en keywords (sin IA)"""
        pain_score = 25  # Base
        senales = []
        keywords_encontradas = []
        texto = objeto.lower()

        # Scoring por CPV
        cpv_prefix = cpv[:2] if cpv else ""
        if cpv_prefix in self.CPV_ALTO_VALOR:
            bonus = self.CPV_ALTO_VALOR[cpv_prefix]
            pain_score += bonus
            senales.append({
                "tipo": "complejidad",
                "descripcion": f"CPV {cpv_prefix}* indica servicios IT/Infraestructura",
                "peso": 7
            })

        # Scoring por keywords
        for kw, puntos in self.KEYWORDS_ALTO_PAIN.items():
            if kw in texto:
                pain_score += puntos
                keywords_encontradas.append(kw)
                if len(senales) < 5:  # Limitar señales
                    senales.append({
                        "tipo": "complejidad" if puntos >= 12 else "recursos",
                        "descripcion": f"Detectado: {kw}",
                        "peso": min(10, puntos)
                    })

        # Bonus por importe alto (>500k)
        if importe > 500000:
            pain_score += 10
            senales.append({
                "tipo": "recursos",
                "descripcion": f"Contrato de alto valor ({importe:,.0f}€)",
                "peso": 8
            })

        # Normalizar score
        pain_score = min(100, max(0, pain_score))

        # Determinar nivel
        if pain_score >= 75:
            nivel = "critico"
        elif pain_score >= 55:
            nivel = "alto"
        elif pain_score >= 35:
            nivel = "medio"
        else:
            nivel = "bajo"

        return {
            "pain_score": pain_score,
            "nivel_urgencia": nivel,
            "resumen_ejecutivo": f"Análisis de: {objeto[:150]}...",
            "senales_dolor": senales,
            "recursos_requeridos": [],
            "oportunidades_subcontratacion": [],
            "riesgos_detectados": [],
            "keywords_clave": keywords_encontradas[:10]
        }

    async def analizar_oportunidad(
        self,
        oportunidad_id: str,
        objeto: str,
        cpv: str = "",
        importe: float = 0,
        url_pliego: Optional[str] = None  # Ignorado para velocidad
    ) -> AnalisisPain:
        """
        Analiza oportunidad con fallback multi-IA.
        NO descarga PDFs para garantizar respuesta <5s.
        """
        resultado = None
        proveedor_usado = "basico"

        # Intentar cada proveedor en orden
        for provider in self.providers:
            if provider == AIProvider.OPENAI:
                logger.info(f"Intentando OpenAI para {oportunidad_id}")
                resultado = await self._analizar_openai(objeto, cpv, importe)
                if resultado:
                    proveedor_usado = "openai"
                    break

            elif provider == AIProvider.GEMINI:
                logger.info(f"Intentando Gemini para {oportunidad_id}")
                resultado = await self._analizar_gemini(objeto, cpv, importe)
                if resultado:
                    proveedor_usado = "gemini"
                    break

            elif provider == AIProvider.CLAUDE:
                logger.info(f"Intentando Claude para {oportunidad_id}")
                resultado = await self._analizar_claude(objeto, cpv, importe)
                if resultado:
                    proveedor_usado = "claude"
                    break

            elif provider == AIProvider.BASICO:
                logger.info(f"Usando análisis básico para {oportunidad_id}")
                resultado = self._analisis_basico(objeto, cpv, importe)
                proveedor_usado = "basico"

        # Construir respuesta
        if not resultado:
            resultado = self._analisis_basico(objeto, cpv, importe)
            proveedor_usado = "basico"

        try:
            senales = [
                PainSignal(
                    tipo=s.get("tipo", "complejidad"),
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
                pliego_analizado=False
            )

        except Exception as e:
            logger.error(f"Error construyendo resultado: {e}")
            return AnalisisPain(
                oportunidad_id=oportunidad_id,
                pain_score=30,
                nivel_urgencia="medio",
                proveedor_ia="error",
                error=str(e)
            )


# Singleton
_analyzer_instance: Optional[PainAnalyzer] = None


def get_pain_analyzer() -> PainAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = PainAnalyzer()
    return _analyzer_instance


async def analizar_pain_oportunidad(
    oportunidad_id: str,
    objeto: str,
    cpv: str = "",
    importe: float = 0,
    url_pliego: Optional[str] = None
) -> Dict:
    """Función principal para analizar una oportunidad"""
    analyzer = get_pain_analyzer()
    resultado = await analyzer.analizar_oportunidad(
        oportunidad_id=oportunidad_id,
        objeto=objeto,
        cpv=cpv,
        importe=importe,
        url_pliego=url_pliego
    )
    return resultado.to_dict()


if __name__ == "__main__":
    async def test():
        resultado = await analizar_pain_oportunidad(
            oportunidad_id="TEST-001",
            objeto="Servicio de soporte técnico informático 24x7 con certificación ISO 27001 para CPD multisede nacional urgente",
            cpv="72000000",
            importe=850000
        )
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    asyncio.run(test())
