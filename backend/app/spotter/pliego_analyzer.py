#!/usr/bin/env python3
"""
Pliego Analyzer - Análisis EXHAUSTIVO de pliegos de licitaciones
Descarga PDFs/HTML y analiza con IA buscando IT oculto
Genera resumen orientado al OPERADOR COMERCIAL para preparar correos con el dolor

NO TIENE RESTRICCIONES DE TIEMPO - La calidad del análisis es prioritaria
"""

import os
import re
import json
import asyncio
import tempfile
import hashlib
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from io import BytesIO
import logging

import httpx
import pdfplumber
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detectar proveedores IA
ANTHROPIC_AVAILABLE = False
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    logger.warning("anthropic no disponible")

OPENAI_AVAILABLE = False
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    pass

GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai no disponible")
    pass


@dataclass
class ITComponente:
    """Componente IT detectado en el pliego"""
    tipo: str  # infraestructura, software, servicios, comunicaciones, seguridad
    nombre: str
    descripcion: str
    urgencia: str  # critica, alta, media, baja
    extracto_pliego: str  # Fragmento literal del pliego
    pagina: Optional[int] = None


@dataclass
class DolorDetectado:
    """Dolor/necesidad específica del cliente"""
    categoria: str  # operativo, tecnico, cumplimiento, recursos, economico
    descripcion: str
    impacto: str  # como afecta al cliente
    extracto_pliego: str
    argumento_venta: str  # Como SRS puede resolver esto


@dataclass
class ResumenOperador:
    """Resumen orientado al OPERADOR para preparar el contacto comercial"""
    # Contexto rápido
    tiene_it: bool
    nivel_oportunidad: str  # oro, plata, bronce, descartar
    tiempo_lectura: str  # "2 min", "5 min"

    # El dolor principal
    dolor_principal: str  # 1 frase que resume el dolor
    dolores_secundarios: List[str]  # Otros dolores detectados

    # IT detectado
    componentes_it: List[ITComponente]
    tecnologias_mencionadas: List[str]  # AWS, VMware, Cisco, etc.
    certificaciones_requeridas: List[str]  # ENS, ISO27001, etc.

    # Para el correo/llamada
    gancho_inicial: str  # Primera frase para el correo/llamada
    puntos_dolor_email: List[str]  # Bullets para el email
    preguntas_cualificacion: List[str]  # Preguntas para la llamada

    # Alertas
    alertas: List[str]  # Cosas importantes a tener en cuenta
    competidores_potenciales: List[str]  # Si se mencionan incumbentes

    # Metadata
    paginas_analizadas: int
    palabras_analizadas: int
    confianza_analisis: str  # alta, media, baja


@dataclass
class AnalisisPliego:
    """Resultado completo del análisis de pliego"""
    oportunidad_id: str

    # Para el CRM
    tiene_it: bool
    pain_score: int  # 0-100
    nivel_urgencia: str  # critico, alto, medio, bajo

    # Análisis detallado
    dolores: List[DolorDetectado]
    componentes_it: List[ITComponente]

    # Para el operador
    resumen_operador: ResumenOperador

    # Datos de contacto extraídos del pliego
    email_contacto: Optional[str] = None  # Email de contacto encontrado
    telefono_contacto: Optional[str] = None  # Teléfono de contacto encontrado
    resumen_it: Optional[str] = None  # Breve resumen del componente IT

    # Metadata
    url_pliego: str = ""
    tipo_documento: str = ""  # pdf, html
    fecha_analisis: str = ""
    proveedor_ia: str = ""
    tiempo_analisis_segundos: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        result = asdict(self)
        return result


class PliegoAnalyzer:
    """
    Analizador EXHAUSTIVO de pliegos.
    Descarga el documento, extrae texto, analiza con IA.
    SIN restricciones de tiempo - prioriza calidad.
    """

    # User agent para descargas
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # Tecnologías IT a detectar
    TECNOLOGIAS_IT = [
        # Cloud
        "aws", "azure", "google cloud", "gcp", "oracle cloud", "ibm cloud",
        # Virtualización
        "vmware", "hyper-v", "proxmox", "nutanix", "citrix",
        # Redes
        "cisco", "juniper", "fortinet", "palo alto", "aruba", "hp networking",
        # Almacenamiento
        "netapp", "dell emc", "hpe", "pure storage", "synology",
        # Backup
        "veeam", "veritas", "commvault", "acronis", "nakivo",
        # Seguridad
        "crowdstrike", "sentinel one", "kaspersky", "trend micro", "sophos",
        # Monitorización
        "nagios", "zabbix", "prometheus", "grafana", "datadog", "splunk",
        # ITSM
        "servicenow", "jira", "freshservice", "zendesk", "remedy",
        # Microsoft
        "microsoft 365", "office 365", "active directory", "exchange", "sharepoint",
        # Linux
        "linux", "ubuntu", "redhat", "centos", "debian",
        # Bases de datos
        "oracle", "sql server", "postgresql", "mysql", "mongodb",
    ]

    # Keywords de dolor
    KEYWORDS_DOLOR = {
        "urgencia": ["urgente", "inmediato", "crítico", "prioritario", "plazo perentorio"],
        "24x7": ["24x7", "24/7", "7x24", "disponibilidad continua", "sin interrupción"],
        "penalizaciones": ["penalización", "penalizacion", "sla", "nivel de servicio", "incumplimiento"],
        "complejidad": ["heterogéneo", "legacy", "obsoleto", "migración", "integración compleja"],
        "certificaciones": ["ens", "iso 27001", "iso27001", "rgpd", "lopd", "certificación"],
        "recursos": ["escasez", "falta de personal", "dificultad para contratar"],
        "multisede": ["multisede", "nacional", "delegaciones", "sedes distribuidas"],
    }

    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_model = None

        # Configurar Gemini (PRIORIDAD - gemini-2.0-flash)
        if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            logger.info("PliegoAnalyzer: Gemini 2.0 Flash configurado (PRINCIPAL)")

        # Configurar OpenAI como primer fallback
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("PliegoAnalyzer: OpenAI configurado como fallback #1")

        # Configurar Anthropic Claude como último fallback (deshabilitado por defecto)
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            logger.info("PliegoAnalyzer: Anthropic Claude configurado como fallback #2 (último)")

        if not self.gemini_model and not self.openai_client and not self.anthropic_client:
            logger.warning("PliegoAnalyzer: Ningún proveedor IA disponible - solo análisis básico")

    async def descargar_documento(self, url: str) -> Tuple[Optional[bytes], str]:
        """Descarga documento de PLACSP o URL directa"""
        try:
            async with httpx.AsyncClient(
                timeout=120.0,  # 2 minutos para descargas grandes
                follow_redirects=True,
                headers={"User-Agent": self.USER_AGENT}
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "").lower()

                if "pdf" in content_type or url.lower().endswith(".pdf"):
                    return response.content, "pdf"
                elif "html" in content_type or "text" in content_type:
                    return response.content, "html"
                else:
                    # Intentar detectar por magic bytes
                    if response.content[:4] == b'%PDF':
                        return response.content, "pdf"
                    return response.content, "html"

        except Exception as e:
            logger.error(f"Error descargando {url}: {e}")
            return None, "error"

    async def extraer_url_pliego_tecnico(self, url_licitacion: str) -> Optional[str]:
        """
        Extrae la URL del pliego técnico desde la página de detalle de PLACSP.
        Busca en la sección de documentos el enlace al pliego de prescripciones técnicas.
        """
        try:
            async with httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
                headers={"User-Agent": self.USER_AGENT}
            ) as client:
                response = await client.get(url_licitacion)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                # Buscar enlaces a documentos
                # Patrones comunes: "Pliego Prescripciones Técnicas", "PPT", "Pliego Técnico"
                patrones_pliego_tecnico = [
                    "pliego prescripciones técnicas",
                    "pliego de prescripciones técnicas",
                    "prescripciones técnicas",
                    "pliego técnico",
                    "ppt",
                    "condiciones técnicas",
                    "especificaciones técnicas",
                ]

                # Buscar en todos los enlaces
                for link in soup.find_all('a', href=True):
                    texto_link = link.get_text(strip=True).lower()
                    href = link.get('href', '')

                    # Verificar si el texto del enlace contiene palabras clave del pliego técnico
                    for patron in patrones_pliego_tecnico:
                        if patron in texto_link:
                            # Construir URL completa si es relativa
                            if href.startswith('/'):
                                href = f"https://contrataciondelestado.es{href}"
                            elif not href.startswith('http'):
                                continue

                            # Preferir PDFs sobre HTML
                            if '.pdf' in href.lower() or 'GetDocumentsById' in href:
                                logger.info(f"Encontrado pliego técnico: {href}")
                                return href

                # Segunda pasada: buscar por estructura de tabla de documentos
                for row in soup.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    row_text = ' '.join([c.get_text(strip=True).lower() for c in cells])

                    if any(p in row_text for p in patrones_pliego_tecnico):
                        # Buscar enlace PDF en esta fila
                        for link in row.find_all('a', href=True):
                            href = link.get('href', '')
                            if '.pdf' in href.lower() or 'GetDocumentsById' in href:
                                if href.startswith('/'):
                                    href = f"https://contrataciondelestado.es{href}"
                                logger.info(f"Encontrado pliego técnico en tabla: {href}")
                                return href

                logger.warning(f"No se encontró pliego técnico en {url_licitacion}")
                return None

        except Exception as e:
            logger.error(f"Error extrayendo URL pliego técnico: {e}")
            return None

    def extraer_texto_pdf(self, pdf_bytes: bytes) -> Tuple[str, int]:
        """Extrae texto de PDF usando pdfplumber"""
        texto_completo = []
        paginas = 0

        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                paginas = len(pdf.pages)
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo.append(texto)
        except Exception as e:
            logger.error(f"Error extrayendo texto PDF: {e}")

        return "\n\n".join(texto_completo), paginas

    def extraer_texto_html(self, html_bytes: bytes) -> str:
        """Extrae texto de HTML"""
        try:
            soup = BeautifulSoup(html_bytes, "html.parser")

            # Eliminar scripts y estilos
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # Extraer texto
            texto = soup.get_text(separator="\n", strip=True)

            # Limpiar líneas vacías excesivas
            lineas = [l.strip() for l in texto.split("\n") if l.strip()]
            return "\n".join(lineas)

        except Exception as e:
            logger.error(f"Error extrayendo texto HTML: {e}")
            return ""

    def _detectar_tecnologias(self, texto: str) -> List[str]:
        """Detecta tecnologías IT mencionadas"""
        texto_lower = texto.lower()
        encontradas = []

        for tech in self.TECNOLOGIAS_IT:
            if tech.lower() in texto_lower:
                # Capitalizar correctamente
                encontradas.append(tech.title() if len(tech) > 3 else tech.upper())

        return list(set(encontradas))

    def _detectar_certificaciones(self, texto: str) -> List[str]:
        """Detecta certificaciones requeridas"""
        certs = []
        texto_lower = texto.lower()

        patrones = {
            "ENS": r"\bens\b|esquema nacional de seguridad",
            "ISO 27001": r"iso\s*27001|iso-27001",
            "ISO 20000": r"iso\s*20000|iso-20000",
            "ISO 9001": r"iso\s*9001|iso-9001",
            "RGPD": r"\brgpd\b|reglamento general de protección",
            "LOPD": r"\blopd\b|ley orgánica de protección",
            "SOC 2": r"soc\s*2|soc-2",
            "PCI DSS": r"pci[\s-]*dss",
        }

        for cert, patron in patrones.items():
            if re.search(patron, texto_lower):
                certs.append(cert)

        return certs

    def _generar_prompt_analisis(self, texto: str, objeto: str, importe: float) -> str:
        """Genera prompt para análisis exhaustivo con IA"""
        from app.spotter.catalogo_srs import SERVICIOS_RESUMEN_PROMPT

        # Limitar texto a ~50k caracteres para no exceder contexto
        texto_truncado = texto[:50000] if len(texto) > 50000 else texto

        return f"""Eres un analista experto en licitaciones públicas de IT/Infraestructura para SRS (System Rapid Solutions), empresa especializada en servicios de soporte IT, cableado estructurado e infraestructura.

{SERVICIOS_RESUMEN_PROMPT}

CONTEXTO DE LA LICITACIÓN:
- Objeto: {objeto}
- Importe: {importe:,.0f}€

TEXTO DEL PLIEGO (extracto):
---
{texto_truncado}
---

ANALIZA EL PLIEGO buscando ESPECÍFICAMENTE servicios del catálogo SRS y responde en JSON con esta estructura EXACTA:

{{
  "tiene_it": true/false,  // ¿Tiene componentes IT/Infraestructura?
  "pain_score": 0-100,  // Puntuación de dolor/urgencia
  "nivel_urgencia": "critico|alto|medio|bajo",

  "dolor_principal": "Frase corta describiendo el PRINCIPAL dolor/necesidad del cliente",

  "dolores": [
    {{
      "categoria": "operativo|tecnico|cumplimiento|recursos|economico",
      "descripcion": "Descripción del dolor",
      "impacto": "Cómo afecta al cliente",
      "extracto_pliego": "Fragmento literal del pliego que evidencia esto",
      "argumento_venta": "Cómo SRS puede resolver esto"
    }}
  ],

  "componentes_it": [
    {{
      "tipo": "servicios|infraestructura|comunicaciones|software|seguridad",
      "nombre": "Nombre EXACTO del servicio del catálogo SRS (ej: 'Soporte técnico Nivel 1', 'Cableado estructurado cobre')",
      "descripcion": "Descripción específica de lo que pide el pliego",
      "urgencia": "critica|alta|media|baja",
      "extracto_pliego": "Fragmento LITERAL del pliego que evidencia esta necesidad"
    }}
  ],

  "gancho_inicial": "Primera frase IMPACTANTE para un correo/llamada que capte atención",

  "puntos_dolor_email": [
    "Punto 1 para incluir en email",
    "Punto 2...",
    "Punto 3..."
  ],

  "preguntas_cualificacion": [
    "¿Pregunta 1 para la llamada?",
    "¿Pregunta 2?"
  ],

  "alertas": [
    "Cosas importantes a tener en cuenta"
  ],

  "competidores_potenciales": ["Si se mencionan empresas incumbentes"],

  "nivel_oportunidad": "oro|plata|bronce|descartar",  // Basado en fit con SRS

  "confianza_analisis": "alta|media|baja",

  "email_contacto": "email@ejemplo.es o null si no se encuentra",
  "telefono_contacto": "+34 XXX XXX XXX o null si no se encuentra",
  "resumen_it": "Breve resumen (2-3 frases) del componente IT del contrato para el operador comercial"
}}

CRITERIOS PARA pain_score:
- +25: Servicio 24x7 / SLAs estrictos
- +20: CPD / Infraestructura crítica
- +15: Certificaciones obligatorias (ENS, ISO)
- +15: Urgencia explícita / Plazos cortos
- +10: Multisede / Complejidad técnica
- +10: Penalizaciones por incumplimiento

CRITERIOS PARA nivel_oportunidad:
- ORO: IT es el núcleo del contrato, alto importe, alta urgencia
- PLATA: IT relevante, buen importe, oportunidad clara
- BRONCE: IT secundario pero presente, vale la pena explorar
- DESCARTAR: No hay IT o no encaja con SRS

IMPORTANTE:
- USA NOMBRES DEL CATÁLOGO SRS para los componentes_it (ej: "Soporte técnico Nivel 1", no "soporte técnico")
- Busca IT OCULTO en contratos que parecen de otra cosa (obras, suministros, etc.)
- Busca especialmente: cableado, puntos de red, fibra, racks, switches, CPD, servidores, backup, monitorización
- Extrae fragmentos LITERALES del pliego como evidencia
- El gancho_inicial debe ser ESPECÍFICO al dolor detectado, no genérico
- Las preguntas de cualificación deben ayudar a entender si es oportunidad real
- Busca emails y teléfonos de contacto en el pliego (del órgano contratante o responsable técnico)
- El resumen_it debe ser conciso pero informativo para un comercial que va a llamar
- Si detectas servicios de soporte/helpdesk, indica los niveles (N1, N2, N3) y horarios (24x7, 8x5)
- Si detectas cableado, especifica tipo (cobre Cat6/Cat6A, fibra monomodo/multimodo)

RESPONDE SOLO JSON, sin explicaciones adicionales."""

    async def _analizar_con_anthropic(self, texto: str, objeto: str, importe: float) -> Optional[Dict]:
        """Análisis con Anthropic Claude (fallback #2 - último recurso)"""
        if not self.anthropic_client:
            logger.warning("Anthropic client no disponible")
            return None

        try:
            prompt = self._generar_prompt_analisis(texto, objeto, importe)
            logger.info("Enviando solicitud a Anthropic Claude...")

            # Timeout de 90 segundos para la llamada a Claude
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=90.0
            )

            text = response.content[0].text
            logger.info(f"Respuesta recibida de Claude ({len(text)} caracteres)")

            # Extraer JSON
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())

            logger.warning("No se pudo extraer JSON de la respuesta de Claude")
            return None

        except asyncio.TimeoutError:
            logger.error("Timeout de 90s en análisis Claude")
            return None
        except Exception as e:
            logger.error(f"Error en análisis Claude: {e}")
            return None

    async def _analizar_con_openai(self, texto: str, objeto: str, importe: float) -> Optional[Dict]:
        """Análisis con OpenAI GPT-4o (fallback #1)"""
        if not self.openai_client:
            logger.warning("OpenAI client no disponible - saltando análisis IA")
            return None

        try:
            prompt = self._generar_prompt_analisis(texto, objeto, importe)
            logger.info("Enviando solicitud a OpenAI GPT-4o...")

            # Timeout de 90 segundos para la llamada a OpenAI
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-4o",  # Modelo más potente para análisis profundo
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.3,
                ),
                timeout=90.0  # 90 segundos máximo
            )

            text = response.choices[0].message.content
            logger.info(f"Respuesta recibida de OpenAI ({len(text)} caracteres)")

            # Extraer JSON
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())

            logger.warning("No se pudo extraer JSON de la respuesta de OpenAI")
            return None

        except asyncio.TimeoutError:
            logger.error("Timeout de 90s en análisis OpenAI - intentando Gemini")
            return None
        except Exception as e:
            logger.error(f"Error en análisis OpenAI: {e}")
            return None

    async def _analizar_con_gemini(self, texto: str, objeto: str, importe: float) -> Optional[Dict]:
        """Análisis con Gemini 2.0 Flash (PRINCIPAL - rápido y económico)"""
        if not self.gemini_model:
            logger.warning("Gemini no disponible")
            return None

        try:
            prompt = self._generar_prompt_analisis(texto, objeto, importe)
            logger.info("Enviando solicitud a Gemini...")

            # Timeout de 90 segundos
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.gemini_model.generate_content,
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=4000,
                    )
                ),
                timeout=90.0
            )

            text = response.text
            logger.info(f"Respuesta recibida de Gemini ({len(text)} caracteres)")

            # Extraer JSON
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())

            logger.warning("No se pudo extraer JSON de la respuesta de Gemini")
            return None

        except asyncio.TimeoutError:
            logger.error("Timeout de 90s en análisis Gemini")
            return None
        except Exception as e:
            logger.error(f"Error en análisis Gemini: {e}")
            return None

    def _analisis_basico(self, texto: str, objeto: str, importe: float) -> Dict:
        """Análisis básico sin IA (fallback)"""
        texto_lower = texto.lower()

        # Detectar si tiene IT
        keywords_it = ["informátic", "software", "hardware", "sistemas", "red", "comunicaciones",
                       "soporte técnico", "helpdesk", "cpd", "servidor", "cloud", "nube"]
        tiene_it = any(kw in texto_lower for kw in keywords_it)

        # Calcular pain_score básico
        pain_score = 30 if tiene_it else 10

        for categoria, keywords in self.KEYWORDS_DOLOR.items():
            for kw in keywords:
                if kw.lower() in texto_lower:
                    pain_score += 10

        pain_score = min(100, pain_score)

        # Detectar tecnologías y certificaciones
        tecnologias = self._detectar_tecnologias(texto)
        certificaciones = self._detectar_certificaciones(texto)

        if certificaciones:
            pain_score += 10

        # Nivel urgencia
        if pain_score >= 75:
            nivel = "critico"
        elif pain_score >= 55:
            nivel = "alto"
        elif pain_score >= 35:
            nivel = "medio"
        else:
            nivel = "bajo"

        return {
            "tiene_it": tiene_it,
            "pain_score": pain_score,
            "nivel_urgencia": nivel,
            "dolor_principal": f"Necesidad de servicios IT detectada en: {objeto[:100]}",
            "dolores": [],
            "componentes_it": [],
            "gancho_inicial": f"He visto su licitación de {objeto[:50]}... y creo que podemos ayudarles.",
            "puntos_dolor_email": [
                "Detectada necesidad de servicios IT",
                f"Importe: {importe:,.0f}€" if importe else "Importe por determinar"
            ],
            "preguntas_cualificacion": [
                "¿Cuál es el principal reto que buscan resolver con este contrato?",
                "¿Tienen actualmente un proveedor para estos servicios?"
            ],
            "alertas": ["Análisis básico - se recomienda revisión manual del pliego"],
            "competidores_potenciales": [],
            "nivel_oportunidad": "bronce" if tiene_it else "descartar",
            "confianza_analisis": "baja",
            "tecnologias_detectadas": tecnologias,
            "certificaciones_detectadas": certificaciones,
        }

    async def analizar_pliego(
        self,
        oportunidad_id: str,
        url_pliego: str,
        objeto: str = "",
        importe: float = 0,
    ) -> AnalisisPliego:
        """
        Análisis EXHAUSTIVO de un pliego.
        Descarga, extrae texto, analiza con IA.
        SIN restricciones de tiempo.
        """
        inicio = datetime.now()

        logger.info(f"Iniciando análisis exhaustivo de pliego: {oportunidad_id}")
        logger.info(f"URL inicial: {url_pliego}")

        # 0. Si la URL es la página de detalle de PLACSP (no un PDF directo),
        #    intentar extraer la URL del pliego técnico real
        url_final = url_pliego
        if 'detalle_licitacion' in url_pliego or 'deeplink' in url_pliego:
            logger.info("URL es página de detalle PLACSP, buscando pliego técnico...")
            url_pliego_tecnico = await self.extraer_url_pliego_tecnico(url_pliego)
            if url_pliego_tecnico:
                logger.info(f"Pliego técnico encontrado: {url_pliego_tecnico}")
                url_final = url_pliego_tecnico
            else:
                logger.warning("No se encontró pliego técnico, usando página de detalle")

        # 1. Descargar documento
        logger.info(f"Descargando documento desde: {url_final}")
        contenido, tipo_doc = await self.descargar_documento(url_final)

        if not contenido:
            return AnalisisPliego(
                oportunidad_id=oportunidad_id,
                tiene_it=False,
                pain_score=0,
                nivel_urgencia="bajo",
                dolores=[],
                componentes_it=[],
                resumen_operador=ResumenOperador(
                    tiene_it=False,
                    nivel_oportunidad="descartar",
                    tiempo_lectura="N/A",
                    dolor_principal="No se pudo descargar el pliego",
                    dolores_secundarios=[],
                    componentes_it=[],
                    tecnologias_mencionadas=[],
                    certificaciones_requeridas=[],
                    gancho_inicial="",
                    puntos_dolor_email=[],
                    preguntas_cualificacion=[],
                    alertas=["ERROR: No se pudo descargar el documento"],
                    competidores_potenciales=[],
                    paginas_analizadas=0,
                    palabras_analizadas=0,
                    confianza_analisis="baja"
                ),
                url_pliego=url_final,
                tipo_documento="error",
                fecha_analisis=datetime.now().isoformat(),
                proveedor_ia="ninguno",
                tiempo_analisis_segundos=0,
                error="No se pudo descargar el documento"
            )

        # 2. Extraer texto
        logger.info(f"Extrayendo texto de {tipo_doc}...")
        if tipo_doc == "pdf":
            texto, paginas = self.extraer_texto_pdf(contenido)
        else:
            texto = self.extraer_texto_html(contenido)
            paginas = 1

        palabras = len(texto.split())
        logger.info(f"Extraídas {palabras} palabras de {paginas} páginas")

        if not texto or len(texto) < 100:
            return AnalisisPliego(
                oportunidad_id=oportunidad_id,
                tiene_it=False,
                pain_score=0,
                nivel_urgencia="bajo",
                dolores=[],
                componentes_it=[],
                resumen_operador=ResumenOperador(
                    tiene_it=False,
                    nivel_oportunidad="descartar",
                    tiempo_lectura="N/A",
                    dolor_principal="No se pudo extraer texto del documento",
                    dolores_secundarios=[],
                    componentes_it=[],
                    tecnologias_mencionadas=[],
                    certificaciones_requeridas=[],
                    gancho_inicial="",
                    puntos_dolor_email=[],
                    preguntas_cualificacion=[],
                    alertas=["ERROR: Documento sin texto extraíble (posible imagen/escaneo)"],
                    competidores_potenciales=[],
                    paginas_analizadas=paginas,
                    palabras_analizadas=0,
                    confianza_analisis="baja"
                ),
                url_pliego=url_final,
                tipo_documento=tipo_doc,
                fecha_analisis=datetime.now().isoformat(),
                proveedor_ia="ninguno",
                tiempo_analisis_segundos=0,
                error="No se pudo extraer texto del documento"
            )

        # 3. Analizar con IA (Gemini primero, luego OpenAI, luego Anthropic)
        logger.info("Analizando con IA (esto puede tardar 30-60 segundos)...")
        resultado_ia = None
        proveedor = "basico"

        # Intentar Gemini primero (PRINCIPAL - rápido y económico)
        if self.gemini_model:
            resultado_ia = await self._analizar_con_gemini(texto, objeto, importe)
            if resultado_ia:
                proveedor = "gemini"

        # Fallback a OpenAI si Gemini falla
        if not resultado_ia and self.openai_client:
            logger.info("Gemini falló, intentando con OpenAI...")
            resultado_ia = await self._analizar_con_openai(texto, objeto, importe)
            if resultado_ia:
                proveedor = "openai"

        # Fallback a Anthropic Claude si OpenAI también falla
        if not resultado_ia and self.anthropic_client:
            logger.info("OpenAI falló, intentando con Anthropic Claude...")
            resultado_ia = await self._analizar_con_anthropic(texto, objeto, importe)
            if resultado_ia:
                proveedor = "anthropic"

        # Último recurso: análisis básico
        if not resultado_ia:
            logger.warning("Fallback a análisis básico (sin IA)")
            resultado_ia = self._analisis_basico(texto, objeto, importe)

        # 4. Detectar tecnologías y certificaciones (adicional)
        tecnologias = self._detectar_tecnologias(texto)
        certificaciones = self._detectar_certificaciones(texto)

        # Merge con lo detectado por IA
        if "tecnologias_detectadas" in resultado_ia:
            tecnologias = list(set(tecnologias + resultado_ia.get("tecnologias_detectadas", [])))
        if "certificaciones_detectadas" in resultado_ia:
            certificaciones = list(set(certificaciones + resultado_ia.get("certificaciones_detectadas", [])))

        # 5. Construir respuesta
        tiempo_total = (datetime.now() - inicio).total_seconds()
        logger.info(f"Análisis completado en {tiempo_total:.1f} segundos")

        # Construir dolores
        dolores = []
        for d in resultado_ia.get("dolores", []):
            dolores.append(DolorDetectado(
                categoria=d.get("categoria", "tecnico"),
                descripcion=d.get("descripcion", ""),
                impacto=d.get("impacto", ""),
                extracto_pliego=d.get("extracto_pliego", ""),
                argumento_venta=d.get("argumento_venta", "")
            ))

        # Construir componentes IT
        componentes = []
        for c in resultado_ia.get("componentes_it", []):
            componentes.append(ITComponente(
                tipo=c.get("tipo", "servicios"),
                nombre=c.get("nombre", ""),
                descripcion=c.get("descripcion", ""),
                urgencia=c.get("urgencia", "media"),
                extracto_pliego=c.get("extracto_pliego", ""),
                pagina=c.get("pagina")
            ))

        # Construir resumen operador
        resumen = ResumenOperador(
            tiene_it=resultado_ia.get("tiene_it", False),
            nivel_oportunidad=resultado_ia.get("nivel_oportunidad", "bronce"),
            tiempo_lectura=f"{max(1, paginas // 10)} min" if paginas > 10 else "2 min",
            dolor_principal=resultado_ia.get("dolor_principal", ""),
            dolores_secundarios=[d.descripcion for d in dolores[1:4]],  # Top 3 adicionales
            componentes_it=componentes,
            tecnologias_mencionadas=tecnologias,
            certificaciones_requeridas=certificaciones,
            gancho_inicial=resultado_ia.get("gancho_inicial", ""),
            puntos_dolor_email=resultado_ia.get("puntos_dolor_email", []),
            preguntas_cualificacion=resultado_ia.get("preguntas_cualificacion", []),
            alertas=resultado_ia.get("alertas", []),
            competidores_potenciales=resultado_ia.get("competidores_potenciales", []),
            paginas_analizadas=paginas,
            palabras_analizadas=palabras,
            confianza_analisis=resultado_ia.get("confianza_analisis", "media")
        )

        return AnalisisPliego(
            oportunidad_id=oportunidad_id,
            tiene_it=resultado_ia.get("tiene_it", False),
            pain_score=resultado_ia.get("pain_score", 30),
            nivel_urgencia=resultado_ia.get("nivel_urgencia", "medio"),
            dolores=dolores,
            componentes_it=componentes,
            resumen_operador=resumen,
            email_contacto=resultado_ia.get("email_contacto"),
            telefono_contacto=resultado_ia.get("telefono_contacto"),
            resumen_it=resultado_ia.get("resumen_it"),
            url_pliego=url_final,
            tipo_documento=tipo_doc,
            fecha_analisis=datetime.now().isoformat(),
            proveedor_ia=proveedor,
            tiempo_analisis_segundos=tiempo_total
        )


# Singleton
_pliego_analyzer: Optional[PliegoAnalyzer] = None


def get_pliego_analyzer() -> PliegoAnalyzer:
    global _pliego_analyzer
    if _pliego_analyzer is None:
        _pliego_analyzer = PliegoAnalyzer()
    return _pliego_analyzer


async def analizar_pliego_completo(
    oportunidad_id: str,
    url_pliego: str,
    objeto: str = "",
    importe: float = 0,
) -> Dict:
    """Función principal para análisis exhaustivo de pliego"""
    analyzer = get_pliego_analyzer()
    resultado = await analyzer.analizar_pliego(
        oportunidad_id=oportunidad_id,
        url_pliego=url_pliego,
        objeto=objeto,
        importe=importe
    )
    return resultado.to_dict()


if __name__ == "__main__":
    async def test():
        # Test con un pliego real
        resultado = await analizar_pliego_completo(
            oportunidad_id="TEST-001",
            url_pliego="https://contrataciondelestado.es/wps/poc?uri=deeplink:detalle_licitacion&idEvl=EJEMPLO",
            objeto="Servicio de soporte informático",
            importe=500000
        )
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    asyncio.run(test())
