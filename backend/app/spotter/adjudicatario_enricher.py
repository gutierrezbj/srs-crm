"""
Módulo para enriquecer datos de adjudicatarios.

Fuentes de datos:
1. PLACSP (página de detalle) - Datos básicos del contrato
2. Infocif.es - Datos de empresa por NIF (scraping)
3. Einforma.com - Datos adicionales (fallback)

Los datos de PLACSP no incluyen contacto del adjudicatario,
solo del órgano contratante. Por eso usamos fuentes externas.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class DatosAdjudicatario:
    """Datos enriquecidos del adjudicatario y del contrato"""
    # Datos básicos (ya disponibles en CRM)
    nombre: str
    nif: str

    # Datos de contacto enriquecidos
    nombre_comercial: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    provincia: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None

    # Datos de la empresa (de Infocif/Einforma)
    forma_juridica: Optional[str] = None  # S.L., S.A., etc.
    fecha_constitucion: Optional[str] = None
    capital_social: Optional[float] = None
    cnae: Optional[str] = None
    actividad: Optional[str] = None
    empleados: Optional[int] = None
    facturacion: Optional[float] = None

    # Datos del contrato (de PLACSP)
    organo_contratacion: Optional[str] = None
    expediente: Optional[str] = None
    objeto: Optional[str] = None
    estado: Optional[str] = None
    resultado: Optional[str] = None
    importe_adjudicacion: Optional[str] = None
    valor_estimado: Optional[str] = None
    presupuesto_base: Optional[str] = None
    lugar_ejecucion: Optional[str] = None
    cpv: Optional[str] = None
    tipo_contrato: Optional[str] = None
    procedimiento: Optional[str] = None
    financiacion_ue: Optional[str] = None
    num_licitadores: Optional[str] = None
    documentos: Optional[list] = None  # Lista de {titulo, url}

    # Metadata
    fuente: str = "manual"  # placsp, infocif, einforma, manual
    fecha_enriquecimiento: Optional[str] = None
    confianza: str = "baja"  # alta, media, baja

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdjudicatarioEnricher:
    """
    Enriquece datos de adjudicatarios desde múltiples fuentes.
    """

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def __init__(self):
        self.timeout = 30.0

    async def enriquecer(
        self,
        nombre: str,
        nif: str,
        url_licitacion: Optional[str] = None
    ) -> DatosAdjudicatario:
        """
        Enriquece datos del adjudicatario desde múltiples fuentes.

        Args:
            nombre: Nombre del adjudicatario (del XML PLACSP)
            nif: NIF del adjudicatario
            url_licitacion: URL de la página de detalle en PLACSP (opcional)

        Returns:
            DatosAdjudicatario con la información disponible
        """
        logger.info(f"Enriqueciendo adjudicatario: {nombre} ({nif})")

        datos = DatosAdjudicatario(
            nombre=nombre,
            nif=nif,
            fecha_enriquecimiento=datetime.now().isoformat()
        )

        # 1. PRIMERO: Extraer datos de PLACSP (fuente oficial y más completa)
        if url_licitacion:
            datos_placsp = await self._scrape_placsp(url_licitacion)
            if datos_placsp:
                datos = self._merge_datos(datos, datos_placsp, "placsp")
                logger.info(f"Datos obtenidos de PLACSP: {list(datos_placsp.keys())}")

        # 2. Complementar con Infocif si faltan datos de contacto
        if not datos.telefono or not datos.email:
            datos_infocif = await self._scrape_infocif(nif)
            if datos_infocif:
                datos = self._merge_datos(datos, datos_infocif, "infocif")
                logger.info(f"Datos complementados desde Infocif para {nif}")

        # 3. Último recurso: Einforma
        if not datos.telefono and not datos.email:
            datos_einforma = await self._scrape_einforma(nif)
            if datos_einforma:
                datos = self._merge_datos(datos, datos_einforma, "einforma")
                logger.info(f"Datos obtenidos de Einforma para {nif}")

        # Calcular confianza
        datos.confianza = self._calcular_confianza(datos)

        return datos

    async def _scrape_infocif(self, nif: str) -> Optional[Dict[str, Any]]:
        """
        Extrae datos de empresa desde Infocif.es
        URL: https://www.infocif.es/ficha-empresa/{nif}
        """
        try:
            url = f"https://www.infocif.es/ficha-empresa/{nif.upper()}"

            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    logger.warning(f"Infocif retornó {response.status_code} para {nif}")
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')

                datos = {}

                # Nombre comercial
                nombre_elem = soup.select_one('h1.company-name, h1[itemprop="name"]')
                if nombre_elem:
                    datos['nombre_comercial'] = nombre_elem.get_text(strip=True)

                # Dirección
                direccion_elem = soup.select_one('[itemprop="streetAddress"], .address, .direccion')
                if direccion_elem:
                    datos['direccion'] = direccion_elem.get_text(strip=True)

                # Localidad
                localidad_elem = soup.select_one('[itemprop="addressLocality"]')
                if localidad_elem:
                    datos['localidad'] = localidad_elem.get_text(strip=True)

                # Provincia
                provincia_elem = soup.select_one('[itemprop="addressRegion"]')
                if provincia_elem:
                    datos['provincia'] = provincia_elem.get_text(strip=True)

                # Código postal
                cp_elem = soup.select_one('[itemprop="postalCode"]')
                if cp_elem:
                    datos['codigo_postal'] = cp_elem.get_text(strip=True)

                # Teléfono
                tel_elem = soup.select_one('[itemprop="telephone"], .telefono, a[href^="tel:"]')
                if tel_elem:
                    telefono = tel_elem.get_text(strip=True)
                    # Limpiar formato
                    telefono = re.sub(r'[^\d+]', '', telefono)
                    if len(telefono) >= 9:
                        datos['telefono'] = telefono

                # Email (buscar patrón en toda la página)
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)
                # Filtrar emails genéricos
                emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'infocif', 'cookie'])]
                if emails:
                    datos['email'] = emails[0]

                # Web
                web_elem = soup.select_one('[itemprop="url"], a.website, .web a')
                if web_elem and web_elem.get('href'):
                    web = web_elem.get('href')
                    if 'infocif' not in web:
                        datos['web'] = web

                # CNAE / Actividad
                cnae_elem = soup.select_one('.cnae, .actividad')
                if cnae_elem:
                    texto = cnae_elem.get_text(strip=True)
                    # Extraer código CNAE si existe
                    cnae_match = re.search(r'(\d{4})', texto)
                    if cnae_match:
                        datos['cnae'] = cnae_match.group(1)
                    datos['actividad'] = texto

                # Forma jurídica
                for texto in soup.stripped_strings:
                    if any(fj in texto.upper() for fj in ['S.L.', 'S.A.', 'S.L.U.', 'S.A.U.', 'SOCIEDAD LIMITADA', 'SOCIEDAD ANÓNIMA']):
                        datos['forma_juridica'] = texto.strip()[:50]
                        break

                # Empleados
                empleados_elem = soup.select_one('.empleados, .employees')
                if empleados_elem:
                    texto = empleados_elem.get_text()
                    nums = re.findall(r'\d+', texto)
                    if nums:
                        datos['empleados'] = int(nums[0])

                return datos if datos else None

        except Exception as e:
            logger.error(f"Error scraping Infocif para {nif}: {e}")
            return None

    async def _scrape_einforma(self, nif: str) -> Optional[Dict[str, Any]]:
        """
        Extrae datos de empresa desde Einforma.com (fallback)
        """
        try:
            # Einforma usa búsqueda, no URL directa por NIF
            url = f"https://www.einforma.com/servlet/app/portal/ENTP/prod/ETIQUETA_EMPRESA_498/nif/{nif.upper()}"

            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')

                datos = {}

                # Buscar datos en la estructura de Einforma
                # La estructura varía, usamos búsqueda genérica

                # Teléfono
                for elem in soup.find_all(string=re.compile(r'Tel[ée]fono', re.I)):
                    parent = elem.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling()
                        if next_elem:
                            tel = re.sub(r'[^\d+]', '', next_elem.get_text())
                            if len(tel) >= 9:
                                datos['telefono'] = tel
                                break

                # Email
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)
                emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'einforma', 'cookie'])]
                if emails:
                    datos['email'] = emails[0]

                return datos if datos else None

        except Exception as e:
            logger.error(f"Error scraping Einforma para {nif}: {e}")
            return None

    async def _scrape_placsp(self, url_licitacion: str) -> Optional[Dict[str, Any]]:
        """
        Extrae datos completos de la página de detalle de PLACSP.

        La página tiene estructura de tabla con filas:
        - Órgano de contratación
        - Expediente
        - Objeto del contrato
        - Estado de la Licitación
        - Adjudicatario
        - Importe de Adjudicación
        - Lugar de ejecución
        - Código CPV
        - Y más...
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    url_licitacion,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    logger.warning(f"PLACSP retornó {response.status_code}")
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')
                datos = {}

                # Mapeo de labels de PLACSP a campos
                mapeo_campos = {
                    'adjudicatario': 'nombre_comercial',
                    'contratista': 'nombre_comercial',
                    'órgano de contratación': 'organo_contratacion',
                    'organo de contratacion': 'organo_contratacion',
                    'expediente': 'expediente',
                    'objeto del contrato': 'objeto',
                    'estado de la licitación': 'estado',
                    'estado de la licitacion': 'estado',
                    'importe de adjudicación': 'importe_adjudicacion',
                    'importe de adjudicacion': 'importe_adjudicacion',
                    'valor estimado del contrato': 'valor_estimado',
                    'presupuesto base de licitación sin impuestos': 'presupuesto_base',
                    'presupuesto base de licitacion sin impuestos': 'presupuesto_base',
                    'lugar de ejecución': 'lugar_ejecucion',
                    'lugar de ejecucion': 'lugar_ejecucion',
                    'código cpv': 'cpv',
                    'codigo cpv': 'cpv',
                    'tipo de contrato': 'tipo_contrato',
                    'procedimiento de contratación': 'procedimiento',
                    'procedimiento de contratacion': 'procedimiento',
                    'financiación ue': 'financiacion_ue',
                    'financiacion ue': 'financiacion_ue',
                    'resultado': 'resultado',
                    'nº de licitadores presentados': 'num_licitadores',
                    'n° de licitadores presentados': 'num_licitadores',
                }

                # Buscar en todas las filas de tabla
                for row in soup.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        if not value:
                            continue

                        # Buscar coincidencia en el mapeo
                        for key_label, campo in mapeo_campos.items():
                            if key_label in label:
                                datos[campo] = value
                                break

                # También buscar en divs con estructura label/valor
                # PLACSP a veces usa divs en lugar de tablas
                for div in soup.find_all('div', class_=re.compile(r'campo|field|row', re.I)):
                    label_elem = div.find(class_=re.compile(r'label|titulo|etiqueta', re.I))
                    value_elem = div.find(class_=re.compile(r'value|valor|dato', re.I))

                    if label_elem and value_elem:
                        label = label_elem.get_text(strip=True).lower()
                        value = value_elem.get_text(strip=True)

                        for key_label, campo in mapeo_campos.items():
                            if key_label in label:
                                if campo not in datos:
                                    datos[campo] = value
                                break

                # Extraer enlaces a documentos (pliegos, adjudicación, etc.)
                documentos = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    texto = link.get_text(strip=True).lower()

                    # Buscar enlaces a documentos PDF
                    if '.pdf' in href.lower() or any(doc in texto for doc in ['pliego', 'adjudicación', 'adjudicacion', 'formalización', 'formalizacion', 'anuncio']):
                        doc_info = {
                            'titulo': link.get_text(strip=True),
                            'url': href if href.startswith('http') else f"https://contrataciondelestado.es{href}"
                        }
                        documentos.append(doc_info)

                if documentos:
                    datos['documentos'] = documentos[:10]  # Limitar a 10 documentos

                # Buscar emails en toda la página
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)
                emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'contratacion', 'hacienda', 'cookie', 'noreply'])]
                if emails:
                    datos['email_contacto'] = emails[0]

                # Buscar teléfonos
                tel_pattern = r'(?:\+34|0034)?[\s.-]?[6789]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}'
                telefonos = re.findall(tel_pattern, response.text)
                if telefonos:
                    # Limpiar y tomar el primero
                    tel = re.sub(r'[^\d+]', '', telefonos[0])
                    if len(tel) >= 9:
                        datos['telefono_contacto'] = tel

                logger.info(f"PLACSP extrajo {len(datos)} campos")
                return datos if datos else None

        except Exception as e:
            logger.error(f"Error scraping PLACSP: {e}")
            return None

        except Exception as e:
            logger.error(f"Error scraping PLACSP: {e}")
            return None

    def _merge_datos(
        self,
        base: DatosAdjudicatario,
        nuevos: Dict[str, Any],
        fuente: str
    ) -> DatosAdjudicatario:
        """Mezcla datos nuevos sin sobrescribir existentes"""
        for key, value in nuevos.items():
            if value and hasattr(base, key):
                current = getattr(base, key)
                if not current:
                    setattr(base, key, value)

        # Actualizar fuente si hay datos nuevos
        if nuevos:
            if base.fuente == "manual":
                base.fuente = fuente
            elif fuente not in base.fuente:
                base.fuente = f"{base.fuente},{fuente}"

        return base

    def _calcular_confianza(self, datos: DatosAdjudicatario) -> str:
        """Calcula nivel de confianza basado en datos disponibles"""
        puntos = 0

        if datos.nombre: puntos += 1
        if datos.nif: puntos += 1
        if datos.direccion: puntos += 2
        if datos.telefono: puntos += 3
        if datos.email: puntos += 3
        if datos.web: puntos += 1
        if datos.actividad: puntos += 1

        if puntos >= 8:
            return "alta"
        elif puntos >= 4:
            return "media"
        return "baja"


# Singleton
_enricher: Optional[AdjudicatarioEnricher] = None


def get_enricher() -> AdjudicatarioEnricher:
    global _enricher
    if _enricher is None:
        _enricher = AdjudicatarioEnricher()
    return _enricher


async def enriquecer_adjudicatario(
    nombre: str,
    nif: str,
    url_licitacion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Función principal para enriquecer datos de adjudicatario.

    Returns:
        Dict con todos los datos disponibles del adjudicatario
    """
    enricher = get_enricher()
    datos = await enricher.enriquecer(nombre, nif, url_licitacion)
    return datos.to_dict()


# Test
if __name__ == "__main__":
    async def test():
        # Test con un NIF real de empresa española
        resultado = await enriquecer_adjudicatario(
            nombre="TELEFONICA SOLUCIONES DE INFORMATICA Y COMUNICACIONES DE ESPAÑA S.A.U.",
            nif="A78053147"
        )
        print("Resultado:")
        for key, value in resultado.items():
            if value:
                print(f"  {key}: {value}")

    asyncio.run(test())
