"""
Módulo para enriquecer datos de adjudicatarios.

Fuentes de datos:
1. PLACSP (página de detalle) - Datos básicos del contrato
2. PLACSP XML de Adjudicación/Formalización - Datos detallados del adjudicatario
3. Infocif.es - Datos de empresa por NIF (scraping)
4. Einforma.com - Datos adicionales (fallback)

El XML de PLACSP (formato CODICE) contiene los datos más completos:
- Nombre completo del adjudicatario
- NIF/CIF
- Dirección fiscal
- Datos de contacto
- Importe exacto
- Fechas
"""

import asyncio
import logging
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

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

    # Datos del contrato (de PLACSP página)
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
    documentos: Optional[list] = None  # Lista de {titulo, url, tipo}

    # Datos detallados del XML de Adjudicación/Formalización
    fecha_adjudicacion: Optional[str] = None
    fecha_formalizacion: Optional[str] = None
    duracion_contrato: Optional[str] = None
    fecha_inicio_ejecucion: Optional[str] = None
    fecha_fin_ejecucion: Optional[str] = None
    es_pyme: Optional[bool] = None
    numero_ofertas: Optional[int] = None

    # Datos del órgano contratante (EL CLIENTE - muy importante para prospección)
    organo_nif: Optional[str] = None
    organo_direccion: Optional[str] = None
    organo_localidad: Optional[str] = None
    organo_cp: Optional[str] = None
    organo_email: Optional[str] = None
    organo_telefono: Optional[str] = None
    organo_web: Optional[str] = None

    # Datos adicionales del contrato
    importe_con_iva: Optional[str] = None
    programa_financiacion: Optional[str] = None
    nif_verificado: Optional[str] = None  # NIF confirmado del adjudicatario

    # Metadata
    fuente: str = "manual"  # placsp, placsp_xml, placsp_html, infocif, einforma, manual
    fecha_enriquecimiento: Optional[str] = None
    confianza: str = "baja"  # alta, media, baja
    xml_adjudicacion_url: Optional[str] = None
    xml_formalizacion_url: Optional[str] = None
    html_adjudicacion_url: Optional[str] = None

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
                # Buscar en la sección "Anuncios y Documentos"
                documentos = []
                xml_adjudicacion = None
                xml_formalizacion = None

                # Buscar todas las filas de la tabla de documentos
                for row in soup.find_all('tr'):
                    row_text = row.get_text(strip=True).lower()

                    # Buscar enlaces en esta fila
                    for link in row.find_all('a', href=True):
                        href = link.get('href', '')
                        link_text = link.get_text(strip=True).lower()

                        # Construir URL completa
                        full_url = href if href.startswith('http') else f"https://contrataciondelestado.es{href}"

                        # Identificar tipo de documento
                        tipo = None
                        if '.xml' in href.lower() or 'xml' in link_text:
                            tipo = 'xml'
                        elif '.pdf' in href.lower() or 'pdf' in link_text:
                            tipo = 'pdf'
                        elif '.html' in href.lower() or 'html' in link_text:
                            tipo = 'html'

                        # Determinar categoría del documento
                        if 'adjudicación' in row_text or 'adjudicacion' in row_text:
                            if tipo == 'xml' and not xml_adjudicacion:
                                xml_adjudicacion = full_url
                                datos['xml_adjudicacion_url'] = full_url
                            doc_info = {'titulo': 'Adjudicación', 'url': full_url, 'tipo': tipo}
                        elif 'formalización' in row_text or 'formalizacion' in row_text:
                            if tipo == 'xml' and not xml_formalizacion:
                                xml_formalizacion = full_url
                                datos['xml_formalizacion_url'] = full_url
                            doc_info = {'titulo': 'Formalización', 'url': full_url, 'tipo': tipo}
                        elif 'pliego' in row_text:
                            doc_info = {'titulo': 'Pliego', 'url': full_url, 'tipo': tipo}
                        elif 'anuncio' in row_text:
                            doc_info = {'titulo': 'Anuncio', 'url': full_url, 'tipo': tipo}
                        else:
                            continue

                        if tipo:  # Solo añadir si identificamos el tipo
                            documentos.append(doc_info)

                # También buscar enlaces sueltos por si la estructura es diferente
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    texto = link.get_text(strip=True).lower()
                    img = link.find('img')
                    alt_text = img.get('alt', '').lower() if img else ''

                    # Los iconos de XML/PDF tienen alt text descriptivo
                    if 'xml' in alt_text or 'xml' in texto:
                        full_url = href if href.startswith('http') else f"https://contrataciondelestado.es{href}"
                        parent_text = link.find_parent('tr')
                        if parent_text:
                            parent_text = parent_text.get_text(strip=True).lower()
                            if ('adjudicación' in parent_text or 'adjudicacion' in parent_text) and not xml_adjudicacion:
                                xml_adjudicacion = full_url
                                datos['xml_adjudicacion_url'] = full_url
                            elif ('formalización' in parent_text or 'formalizacion' in parent_text) and not xml_formalizacion:
                                xml_formalizacion = full_url
                                datos['xml_formalizacion_url'] = full_url

                if documentos:
                    # Eliminar duplicados manteniendo orden
                    seen = set()
                    unique_docs = []
                    for doc in documentos:
                        key = (doc['titulo'], doc['tipo'])
                        if key not in seen:
                            seen.add(key)
                            unique_docs.append(doc)
                    datos['documentos'] = unique_docs[:15]

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

                # Buscar HTML de adjudicación (más fácil de parsear que XML)
                html_adjudicacion = None
                for doc in datos.get('documentos', []):
                    if doc.get('titulo') == 'Adjudicación' and doc.get('tipo') == 'html':
                        html_adjudicacion = doc.get('url')
                        break

                # Parsear HTML de adjudicación (contiene todos los datos del adjudicatario)
                if html_adjudicacion:
                    logger.info(f"Descargando HTML de adjudicación: {html_adjudicacion}")
                    datos_html = await self._parse_html_adjudicacion(html_adjudicacion)
                    if datos_html:
                        datos.update(datos_html)
                        logger.info(f"HTML adjudicación aportó {len(datos_html)} campos")

                # Fallback a XML si no tenemos HTML o faltan datos
                elif xml_adjudicacion and not datos.get('direccion'):
                    logger.info(f"Descargando XML de adjudicación: {xml_adjudicacion}")
                    datos_xml = await self._parse_xml_adjudicacion(xml_adjudicacion)
                    if datos_xml:
                        datos.update(datos_xml)
                        logger.info(f"XML adjudicación aportó {len(datos_xml)} campos adicionales")

                # Si hay formalización y faltan datos, intentar también
                if xml_formalizacion and not datos.get('direccion'):
                    logger.info(f"Descargando XML de formalización: {xml_formalizacion}")
                    datos_xml = await self._parse_xml_adjudicacion(xml_formalizacion)
                    if datos_xml:
                        for k, v in datos_xml.items():
                            if k not in datos or not datos[k]:
                                datos[k] = v

                logger.info(f"PLACSP extrajo {len(datos)} campos en total")
                return datos if datos else None

        except Exception as e:
            logger.error(f"Error scraping PLACSP: {e}")
            return None

    async def _parse_xml_adjudicacion(self, xml_url: str) -> Optional[Dict[str, Any]]:
        """
        Parsea el XML de adjudicación/formalización de PLACSP.

        El XML sigue el formato CODICE (estándar europeo de contratación).
        Contiene datos detallados del adjudicatario y del contrato.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    xml_url,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    logger.warning(f"XML retornó {response.status_code}")
                    return None

                # Parsear XML
                try:
                    root = ET.fromstring(response.content)
                except ET.ParseError as e:
                    logger.error(f"Error parseando XML: {e}")
                    return None

                datos = {}

                # Buscar WinningParty (datos del adjudicatario)
                for elem in root.iter():
                    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

                    # Datos del adjudicatario (WinningParty)
                    if tag == 'WinningParty':
                        for sub in elem.iter():
                            subtag = sub.tag.split('}')[-1] if '}' in sub.tag else sub.tag

                            if subtag == 'Name' and sub.text:
                                datos['nombre_comercial'] = sub.text.strip()
                            elif subtag == 'ID' and sub.text:
                                # NIF/CIF
                                if len(sub.text.strip()) == 9:
                                    datos['nif_verificado'] = sub.text.strip()
                            elif subtag == 'StreetName' and sub.text:
                                datos['direccion'] = sub.text.strip()
                            elif subtag == 'CityName' and sub.text:
                                datos['localidad'] = sub.text.strip()
                            elif subtag == 'PostalZone' and sub.text:
                                datos['codigo_postal'] = sub.text.strip()
                            elif subtag == 'CountrySubentity' and sub.text:
                                datos['provincia'] = sub.text.strip()
                            elif subtag == 'Telephone' and sub.text:
                                tel = re.sub(r'[^\d+]', '', sub.text)
                                if len(tel) >= 9:
                                    datos['telefono'] = tel
                            elif subtag == 'ElectronicMail' and sub.text:
                                datos['email'] = sub.text.strip()
                            elif subtag == 'WebsiteURI' and sub.text:
                                datos['web'] = sub.text.strip()
                            elif subtag == 'SMEAwardedIndicator' and sub.text:
                                datos['es_pyme'] = sub.text.lower() == 'true'

                    # Datos del órgano contratante (LocatedContractingParty)
                    elif tag == 'LocatedContractingParty' or tag == 'ContractingParty':
                        for sub in elem.iter():
                            subtag = sub.tag.split('}')[-1] if '}' in sub.tag else sub.tag

                            if subtag == 'Name' and sub.text and 'organo_contratacion' not in datos:
                                datos['organo_contratacion'] = sub.text.strip()
                            elif subtag == 'ID' and sub.text and len(sub.text.strip()) == 9:
                                datos['organo_nif'] = sub.text.strip()
                            elif subtag == 'StreetName' and sub.text:
                                datos['organo_direccion'] = sub.text.strip()
                            elif subtag == 'CityName' and sub.text:
                                datos['organo_localidad'] = sub.text.strip()
                            elif subtag == 'PostalZone' and sub.text:
                                datos['organo_cp'] = sub.text.strip()
                            elif subtag == 'Telephone' and sub.text:
                                tel = re.sub(r'[^\d+]', '', sub.text)
                                if len(tel) >= 9:
                                    datos['organo_telefono'] = tel
                            elif subtag == 'ElectronicMail' and sub.text:
                                datos['organo_email'] = sub.text.strip()
                            elif subtag == 'WebsiteURI' and sub.text:
                                datos['organo_web'] = sub.text.strip()

                    # Importe
                    elif tag in ['TotalAmount', 'TaxExclusiveAmount', 'PayableAmount']:
                        if elem.text:
                            try:
                                datos['importe_adjudicacion'] = f"{float(elem.text):,.2f} €"
                            except:
                                pass

                    # Fechas
                    elif tag == 'AwardDate' and elem.text:
                        datos['fecha_adjudicacion'] = elem.text
                    elif tag == 'ContractFolderID' and elem.text:
                        datos['expediente'] = elem.text
                    elif tag == 'IssueDate' and elem.text:
                        if 'fecha_formalizacion' not in datos:
                            datos['fecha_formalizacion'] = elem.text

                    # Duración
                    elif tag == 'DurationMeasure' and elem.text:
                        try:
                            duracion = int(float(elem.text))
                            unit = elem.get('unitCode', 'DAY')
                            if unit == 'MON':
                                datos['duracion_contrato'] = f"{duracion} meses"
                            elif unit == 'ANN':
                                datos['duracion_contrato'] = f"{duracion} años"
                            else:
                                datos['duracion_contrato'] = f"{duracion} días"
                        except:
                            pass

                    # Número de ofertas
                    elif tag == 'ReceivedTenderQuantity' and elem.text:
                        try:
                            datos['numero_ofertas'] = int(elem.text)
                        except:
                            pass

                    # CPV
                    elif tag == 'ItemClassificationCode' and elem.text:
                        if 'cpv' not in datos:
                            datos['cpv'] = elem.text

                    # Objeto del contrato
                    elif tag == 'Name' and 'objeto' not in datos:
                        parent = elem
                        # Solo si es hijo de ProcurementProject
                        if elem.text and len(elem.text) > 50:
                            datos['objeto'] = elem.text.strip()

                logger.info(f"XML parseado: {list(datos.keys())}")
                return datos if datos else None

        except Exception as e:
            logger.error(f"Error parseando XML de adjudicación: {e}")
            return None

    async def _parse_html_adjudicacion(self, html_url: str) -> Optional[Dict[str, Any]]:
        """
        Parsea el HTML de adjudicación de PLACSP.

        El documento HTML tiene secciones claramente definidas:
        - Entidad Adjudicadora (el cliente)
        - Adjudicatario (el ganador)
        - Importes de Adjudicación
        - Información sobre las ofertas
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    html_url,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    logger.warning(f"HTML adjudicación retornó {response.status_code}")
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')
                datos = {}
                texto_completo = response.text.lower()

                # Función auxiliar para extraer valor después de un label
                def extraer_valor(label_text: str) -> Optional[str]:
                    """Busca un label y extrae el valor que le sigue"""
                    for elem in soup.find_all(string=re.compile(label_text, re.I)):
                        parent = elem.find_parent()
                        if parent:
                            # Buscar el siguiente elemento con texto
                            next_elem = parent.find_next_sibling()
                            if next_elem:
                                valor = next_elem.get_text(strip=True)
                                if valor and valor != '-':
                                    return valor
                            # O buscar en el mismo elemento después del label
                            full_text = parent.get_text(strip=True)
                            if ':' in full_text:
                                parts = full_text.split(':', 1)
                                if len(parts) > 1 and parts[1].strip():
                                    return parts[1].strip()
                    return None

                # === DATOS DEL ADJUDICATARIO ===

                # Buscar sección "Adjudicatario"
                for header in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b']):
                    header_text = header.get_text(strip=True).lower()
                    if 'adjudicatario' in header_text and 'entidad' not in header_text:
                        # Encontramos la sección del adjudicatario
                        parent_section = header.find_parent(['div', 'section', 'td'])
                        if parent_section:
                            section_text = parent_section.get_text()

                            # Nombre de empresa (primera línea después de "Adjudicatario")
                            lines = [l.strip() for l in section_text.split('\n') if l.strip()]
                            for i, line in enumerate(lines):
                                if 'adjudicatario' in line.lower() and i + 1 < len(lines):
                                    nombre = lines[i + 1]
                                    if nombre and len(nombre) > 3 and 'nif' not in nombre.lower():
                                        datos['nombre_comercial'] = nombre
                                    break

                # NIF del adjudicatario
                nif_match = re.search(r'NIF[:\s]*([A-Z]\d{8}|\d{8}[A-Z])', response.text, re.I)
                if nif_match:
                    datos['nif_verificado'] = nif_match.group(1).upper()

                # Es PYME
                if 'pyme' in texto_completo:
                    pyme_match = re.search(r'pyme[:\s]*(sí|si|yes|true)', texto_completo, re.I)
                    datos['es_pyme'] = bool(pyme_match)

                # Dirección Física del adjudicatario
                direccion_match = re.search(
                    r'Direcci[óo]n\s*F[íi]sica[:\s]*([^<\n]+)',
                    response.text, re.I
                )
                if direccion_match:
                    direccion_text = direccion_match.group(1).strip()
                    # Puede tener múltiples líneas
                    datos['direccion'] = direccion_text

                # Buscar dirección con patrón de CP
                cp_match = re.search(r'\((\d{5})\)\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+)', response.text)
                if cp_match:
                    datos['codigo_postal'] = cp_match.group(1)
                    datos['localidad'] = cp_match.group(2).strip().split(' España')[0].strip()

                # Teléfono del adjudicatario
                tel_section = re.search(
                    r'(?:Adjudicatario|Contacto).*?Tel[ée]fono[:\s]*(\+?\d[\d\s.-]{8,})',
                    response.text, re.I | re.DOTALL
                )
                if tel_section:
                    tel = re.sub(r'[^\d+]', '', tel_section.group(1))
                    if len(tel) >= 9:
                        datos['telefono'] = tel

                # Email del adjudicatario
                email_section = re.search(
                    r'(?:Adjudicatario|Contacto).*?(?:Correo|Email|E-mail)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                    response.text, re.I | re.DOTALL
                )
                if email_section:
                    datos['email'] = email_section.group(1)

                # === DATOS DEL CONTRATO ===

                # Importe sin impuestos
                importe_match = re.search(
                    r'Importe\s*(?:total\s*)?(?:ofertado\s*)?\(?sin\s*impuestos\)?[:\s]*([\d.,]+)\s*EUR',
                    response.text, re.I
                )
                if importe_match:
                    datos['importe_adjudicacion'] = f"{importe_match.group(1)} EUR"

                # Importe con impuestos
                importe_iva_match = re.search(
                    r'Importe\s*(?:total\s*)?(?:ofertado\s*)?\(?con\s*impuestos\)?[:\s]*([\d.,]+)\s*EUR',
                    response.text, re.I
                )
                if importe_iva_match:
                    datos['importe_con_iva'] = f"{importe_iva_match.group(1)} EUR"

                # Plazo de ejecución
                plazo_match = re.search(r'Plazo\s*de\s*Ejecuci[óo]n[:\s]*(\d+)\s*(D[íi]as?|Meses?|A[ñn]os?)', response.text, re.I)
                if plazo_match:
                    datos['duracion_contrato'] = f"{plazo_match.group(1)} {plazo_match.group(2)}"

                # Fecha de acuerdo/adjudicación
                fecha_match = re.search(r'Fecha\s*de\s*(?:Acuerdo|Adjudicaci[óo]n)[:\s]*(\d{2}/\d{2}/\d{4})', response.text, re.I)
                if fecha_match:
                    datos['fecha_adjudicacion'] = fecha_match.group(1)

                # Número de ofertas
                ofertas_match = re.search(r'Ofertas\s*recibidas[:\s]*(\d+)', response.text, re.I)
                if ofertas_match:
                    datos['numero_ofertas'] = int(ofertas_match.group(1))

                # === DATOS DEL ÓRGANO CONTRATANTE (EL CLIENTE) ===

                # Buscar sección "Entidad Adjudicadora"
                for header in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b']):
                    header_text = header.get_text(strip=True).lower()
                    if 'entidad adjudicadora' in header_text:
                        parent_section = header.find_parent(['div', 'section', 'td'])
                        if parent_section:
                            section_text = parent_section.get_text()
                            lines = [l.strip() for l in section_text.split('\n') if l.strip()]
                            for i, line in enumerate(lines):
                                if 'entidad adjudicadora' in line.lower() and i + 1 < len(lines):
                                    nombre_org = lines[i + 1]
                                    if nombre_org and len(nombre_org) > 5:
                                        datos['organo_contratacion'] = nombre_org
                                    break

                # Teléfono del órgano
                org_tel_match = re.search(
                    r'Entidad\s*Adjudicadora.*?Tel[ée]fono[:\s]*(\d[\d\s]{6,})',
                    response.text, re.I | re.DOTALL
                )
                if org_tel_match:
                    tel = re.sub(r'[^\d]', '', org_tel_match.group(1))
                    if len(tel) >= 9:
                        datos['organo_telefono'] = tel

                # Email del órgano
                org_email_match = re.search(
                    r'Entidad\s*Adjudicadora.*?(?:Correo|Email)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                    response.text, re.I | re.DOTALL
                )
                if org_email_match:
                    datos['organo_email'] = org_email_match.group(1)

                # === INFORMACIÓN ADICIONAL ===

                # CPV
                cpv_match = re.search(r'(\d{8})\s*-\s*[A-Za-záéíóúñ\s]+(?:eléctrica|solar|instalación)', response.text)
                if cpv_match:
                    if 'cpv' not in datos:
                        datos['cpv'] = cpv_match.group(1)

                # Lugar de ejecución
                lugar_match = re.search(r'Subentidad\s*Nacional[:\s]*([A-Za-záéíóúñ\s]+)', response.text, re.I)
                if lugar_match:
                    datos['lugar_ejecucion'] = lugar_match.group(1).strip()

                # Financiación UE
                if 'fondos de la ue' in texto_completo or 'financiación con fondos' in texto_completo:
                    datos['financiacion_ue'] = 'Sí - Fondos UE'
                    # Buscar programa específico
                    programa_match = re.search(r'Plan\s*de\s*Recuperaci[óo]n[^.]*', response.text, re.I)
                    if programa_match:
                        datos['programa_financiacion'] = programa_match.group(0).strip()

                logger.info(f"HTML adjudicación parseado: {list(datos.keys())}")
                return datos if datos else None

        except Exception as e:
            logger.error(f"Error parseando HTML de adjudicación: {e}")
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
