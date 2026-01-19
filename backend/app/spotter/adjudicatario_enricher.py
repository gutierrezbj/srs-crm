"""
Módulo para enriquecer datos de adjudicatarios.

Fuentes de datos:
1. PLACSP (página de detalle) - Datos básicos del contrato
2. PLACSP XML de Adjudicación/Formalización - Datos detallados del adjudicatario
3. PLACSP PDF Acta de Resolución - Lista de licitadores/competidores
4. Infocif.es - Datos de empresa por NIF (scraping)
5. Einforma.com - Datos adicionales (fallback)

El XML de PLACSP (formato CODICE) contiene los datos más completos:
- Nombre completo del adjudicatario
- NIF/CIF
- Dirección fiscal
- Datos de contacto
- Importe exacto
- Fechas

El PDF del Acta de Resolución contiene:
- Lista de todas las empresas que licitaron
- NIF de cada empresa
- Puntuación obtenida
"""

import asyncio
import logging
import re
import tempfile
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
import pdfplumber

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

    # Empresas competidoras (otras que licitaron pero no ganaron)
    # Lista de {nif, nombre, puntuacion}
    empresas_competidoras: Optional[List[Dict[str, Any]]] = None

    # Metadata
    fuente: str = "manual"  # placsp, placsp_xml, placsp_html, infocif, einforma, manual
    fecha_enriquecimiento: Optional[str] = None
    confianza: str = "baja"  # alta, media, baja
    xml_adjudicacion_url: Optional[str] = None
    xml_formalizacion_url: Optional[str] = None
    html_adjudicacion_url: Optional[str] = None
    pdf_acta_resolucion_url: Optional[str] = None

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

        # 4. Extraer empresas competidoras del PDF del Acta de Resolución
        if datos.pdf_acta_resolucion_url:
            logger.info(f"Extrayendo competidores del PDF: {datos.pdf_acta_resolucion_url}")
            competidores = await self._extract_competidores_from_pdf(
                datos.pdf_acta_resolucion_url,
                nif
            )
            if competidores:
                datos.empresas_competidoras = competidores
                logger.info(f"Se encontraron {len(competidores)} empresas competidoras")

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

        PLACSP usa WebSphere Portal y puede tener diferentes estructuras:
        - Tablas tradicionales con <tr>/<td>
        - Divs con clases viewValue, boxPlegado, campoFichaTecnica
        - Estructura de formulario con labels y valores
        """
        try:
            logger.info(f"Scraping PLACSP: {url_licitacion}")

            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    url_licitacion,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    logger.warning(f"PLACSP retornó {response.status_code}")
                    return None

                logger.info(f"PLACSP respuesta OK, {len(response.text)} bytes")
                soup = BeautifulSoup(response.text, 'html.parser')
                datos = {}

                # Mapeo de labels de PLACSP a campos (normalizado sin tildes para comparación)
                mapeo_campos = {
                    'adjudicatario': 'nombre_comercial',
                    'contratista': 'nombre_comercial',
                    'organo de contratacion': 'organo_contratacion',
                    'órgano de contratación': 'organo_contratacion',
                    'expediente': 'expediente',
                    'objeto del contrato': 'objeto',
                    'objeto': 'objeto',
                    'estado de la licitacion': 'estado',
                    'estado de la licitación': 'estado',
                    'estado': 'estado',
                    'importe de adjudicacion': 'importe_adjudicacion',
                    'importe de adjudicación': 'importe_adjudicacion',
                    'importe adjudicacion': 'importe_adjudicacion',
                    'valor estimado del contrato': 'valor_estimado',
                    'valor estimado': 'valor_estimado',
                    'presupuesto base de licitacion sin impuestos': 'presupuesto_base',
                    'presupuesto base de licitación sin impuestos': 'presupuesto_base',
                    'presupuesto base': 'presupuesto_base',
                    'lugar de ejecucion': 'lugar_ejecucion',
                    'lugar de ejecución': 'lugar_ejecucion',
                    'codigo cpv': 'cpv',
                    'código cpv': 'cpv',
                    'cpv': 'cpv',
                    'tipo de contrato': 'tipo_contrato',
                    'procedimiento de contratacion': 'procedimiento',
                    'procedimiento de contratación': 'procedimiento',
                    'procedimiento': 'procedimiento',
                    'financiacion ue': 'financiacion_ue',
                    'financiación ue': 'financiacion_ue',
                    'resultado': 'resultado',
                    'nº de licitadores presentados': 'num_licitadores',
                    'n° de licitadores presentados': 'num_licitadores',
                    'numero de licitadores': 'num_licitadores',
                    'licitadores presentados': 'num_licitadores',
                }

                def normalizar_label(texto: str) -> str:
                    """Normaliza un label para comparación"""
                    return texto.lower().strip().replace(':', '').strip()

                # MÉTODO 1: Buscar en todas las filas de tabla (estructura tradicional)
                for row in soup.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = normalizar_label(cells[0].get_text(strip=True))
                        value = cells[1].get_text(strip=True)

                        if not value:
                            continue

                        # Buscar coincidencia en el mapeo
                        for key_label, campo in mapeo_campos.items():
                            if key_label in label or label in key_label:
                                if campo not in datos:
                                    datos[campo] = value
                                    logger.debug(f"Tabla: {campo} = {value[:50]}...")
                                break

                # MÉTODO 2: Buscar en divs con estructura label/valor (nueva estructura PLACSP)
                # Clases comunes: viewValue, campoFichaTecnica, boxPlegado, fieldValue
                for div in soup.find_all('div', class_=re.compile(r'campo|field|row|ficha|box', re.I)):
                    label_elem = div.find(class_=re.compile(r'label|titulo|etiqueta|viewLabel', re.I))
                    value_elem = div.find(class_=re.compile(r'value|valor|dato|viewValue', re.I))

                    if label_elem and value_elem:
                        label = normalizar_label(label_elem.get_text(strip=True))
                        value = value_elem.get_text(strip=True)

                        if not value:
                            continue

                        for key_label, campo in mapeo_campos.items():
                            if key_label in label or label in key_label:
                                if campo not in datos:
                                    datos[campo] = value
                                    logger.debug(f"Div: {campo} = {value[:50]}...")
                                break

                # MÉTODO 3: Buscar con selectores específicos de PLACSP
                # PLACSP usa clases como: cabeceraFichaTecnica, contenidoFichaTecnica
                for elem in soup.find_all(['span', 'div', 'p'], class_=re.compile(r'viewValue|fieldValue|valorCampo', re.I)):
                    # Buscar el label anterior (hermano o padre)
                    prev = elem.find_previous_sibling(class_=re.compile(r'viewLabel|fieldLabel|etiquetaCampo', re.I))
                    if not prev:
                        parent = elem.find_parent()
                        if parent:
                            prev = parent.find(class_=re.compile(r'viewLabel|fieldLabel|etiquetaCampo', re.I))

                    if prev:
                        label = normalizar_label(prev.get_text(strip=True))
                        value = elem.get_text(strip=True)

                        if not value:
                            continue

                        for key_label, campo in mapeo_campos.items():
                            if key_label in label or label in key_label:
                                if campo not in datos:
                                    datos[campo] = value
                                    logger.debug(f"ViewValue: {campo} = {value[:50]}...")
                                break

                # MÉTODO 4: Buscar patrones de texto directo (último recurso)
                # Útil cuando no hay estructura clara
                texto_pagina = soup.get_text()
                if not datos.get('expediente'):
                    exp_match = re.search(r'(?:Expediente|Nº Expediente)[:\s]*([A-Z0-9\-\/]+)', texto_pagina, re.I)
                    if exp_match:
                        datos['expediente'] = exp_match.group(1).strip()
                        logger.debug(f"Regex: expediente = {datos['expediente']}")

                if not datos.get('importe_adjudicacion'):
                    # Buscar importes con formato europeo (123.456,78 €)
                    imp_match = re.search(r'(?:Importe|Adjudicaci[oó]n)[:\s]*([\d.,]+)\s*(?:EUR|€)', texto_pagina, re.I)
                    if imp_match:
                        datos['importe_adjudicacion'] = f"{imp_match.group(1)} EUR"
                        logger.debug(f"Regex: importe = {datos['importe_adjudicacion']}")

                logger.info(f"PLACSP scraping básico: {len(datos)} campos encontrados - {list(datos.keys())}")

                # Extraer enlaces a documentos (pliegos, adjudicación, etc.)
                # Buscar en la sección "Anuncios y Documentos"
                documentos = []
                xml_adjudicacion = None
                xml_formalizacion = None
                html_adjudicacion = None
                pdf_acta_resolucion = None

                # Función auxiliar para identificar tipo de documento
                # PLACSP usa GetDocumentByIdServlet con parámetros cifrados
                # El tipo se detecta por: icono img alt/title, texto del enlace, o extensión en URL
                def identificar_tipo_documento(link_elem, href: str, texto: str) -> Optional[str]:
                    href_lower = href.lower()
                    texto_lower = texto.lower()

                    # Buscar icono dentro del enlace
                    img = link_elem.find('img') if link_elem else None
                    alt_text = (img.get('alt', '') + ' ' + img.get('title', '')).lower() if img else ''

                    # También buscar atributo title del enlace
                    title_attr = link_elem.get('title', '').lower() if link_elem else ''

                    # Combinar todas las fuentes de información
                    all_text = f"{texto_lower} {alt_text} {title_attr}"

                    # Detectar por extensión explícita en URL
                    if '.xml' in href_lower:
                        return 'xml'
                    elif '.pdf' in href_lower:
                        return 'pdf'
                    elif '.html' in href_lower or '.htm' in href_lower:
                        return 'html'

                    # Detectar por texto/alt/title (PLACSP usa iconos con alt="XML", "HTML", "PDF")
                    if 'xml' in all_text:
                        return 'xml'
                    elif 'pdf' in all_text:
                        return 'pdf'
                    elif 'html' in all_text or 'htm' in all_text:
                        return 'html'

                    # Para GetDocumentByIdServlet sin tipo claro, inferir por contexto
                    if 'GetDocumentByIdServlet' in href or 'FileSystem/servlet' in href:
                        # Si no hay indicación clara, asumir HTML (más común para adjudicaciones)
                        return 'html'

                    return None

                # MÉTODO PRINCIPAL: Buscar en filas de tabla (sección Anuncios y Documentos)
                logger.debug("Buscando documentos en tablas...")
                for row in soup.find_all('tr'):
                    row_text = row.get_text(strip=True).lower()

                    # Solo procesar filas que contengan tipos de documentos relevantes
                    es_adjudicacion = 'adjudicación' in row_text or 'adjudicacion' in row_text
                    es_formalizacion = 'formalización' in row_text or 'formalizacion' in row_text
                    es_acta = 'acta' in row_text and ('resolución' in row_text or 'resolucion' in row_text)
                    es_pliego = 'pliego' in row_text
                    es_anuncio = 'anuncio' in row_text

                    if not any([es_adjudicacion, es_formalizacion, es_acta, es_pliego, es_anuncio]):
                        continue

                    # Buscar TODOS los enlaces en esta fila
                    for link in row.find_all('a', href=True):
                        href = link.get('href', '')
                        link_text = link.get_text(strip=True)

                        # Construir URL completa
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            full_url = f"https://contrataciondelestado.es{href}"
                        else:
                            continue

                        # Identificar tipo de documento
                        tipo = identificar_tipo_documento(link, href, link_text)

                        if not tipo:
                            continue

                        logger.debug(f"Enlace encontrado: tipo={tipo}, fila={row_text[:50]}...")

                        # Clasificar según tipo de documento
                        doc_info = None
                        if es_adjudicacion:
                            if tipo == 'xml' and not xml_adjudicacion:
                                xml_adjudicacion = full_url
                                datos['xml_adjudicacion_url'] = full_url
                                logger.info(f"✓ XML adjudicación: {full_url[:80]}")
                            elif tipo == 'html' and not html_adjudicacion:
                                html_adjudicacion = full_url
                                datos['html_adjudicacion_url'] = full_url
                                logger.info(f"✓ HTML adjudicación: {full_url[:80]}")
                            elif tipo == 'pdf':
                                doc_info = {'titulo': 'Adjudicación PDF', 'url': full_url, 'tipo': tipo}
                            else:
                                doc_info = {'titulo': 'Adjudicación', 'url': full_url, 'tipo': tipo}
                        elif es_formalizacion:
                            if tipo == 'xml' and not xml_formalizacion:
                                xml_formalizacion = full_url
                                datos['xml_formalizacion_url'] = full_url
                                logger.info(f"✓ XML formalización: {full_url[:80]}")
                            doc_info = {'titulo': 'Formalización', 'url': full_url, 'tipo': tipo}
                        elif es_acta:
                            if tipo == 'pdf' and not pdf_acta_resolucion:
                                pdf_acta_resolucion = full_url
                                datos['pdf_acta_resolucion_url'] = full_url
                                logger.info(f"✓ PDF acta resolución: {full_url[:80]}")
                            doc_info = {'titulo': 'Acta de Resolución', 'url': full_url, 'tipo': tipo}
                        elif es_pliego:
                            doc_info = {'titulo': 'Pliego', 'url': full_url, 'tipo': tipo}
                        elif es_anuncio:
                            doc_info = {'titulo': 'Anuncio', 'url': full_url, 'tipo': tipo}

                        if doc_info:
                            documentos.append(doc_info)

                # MÉTODO SECUNDARIO: Buscar enlaces con iconos específicos en toda la página
                if not xml_adjudicacion and not html_adjudicacion:
                    logger.debug("Buscando documentos por iconos...")
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')

                        # Solo procesar enlaces a documentos
                        if 'GetDocumentByIdServlet' not in href and 'FileSystem' not in href:
                            continue

                        # Buscar contexto (fila padre)
                        parent = link.find_parent('tr')
                        if not parent:
                            continue

                        parent_text = parent.get_text(strip=True).lower()

                        # Construir URL completa
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            full_url = f"https://contrataciondelestado.es{href}"
                        else:
                            continue

                        # Identificar tipo
                        tipo = identificar_tipo_documento(link, href, link.get_text(strip=True))

                        if not tipo:
                            continue

                        # Clasificar
                        if ('adjudicación' in parent_text or 'adjudicacion' in parent_text):
                            if tipo == 'xml' and not xml_adjudicacion:
                                xml_adjudicacion = full_url
                                datos['xml_adjudicacion_url'] = full_url
                                logger.info(f"✓ XML adj (método 2): {full_url[:80]}")
                            elif tipo == 'html' and not html_adjudicacion:
                                html_adjudicacion = full_url
                                datos['html_adjudicacion_url'] = full_url
                                logger.info(f"✓ HTML adj (método 2): {full_url[:80]}")
                        elif ('formalización' in parent_text or 'formalizacion' in parent_text):
                            if tipo == 'xml' and not xml_formalizacion:
                                xml_formalizacion = full_url
                                datos['xml_formalizacion_url'] = full_url

                logger.info(f"Documentos encontrados: XML_adj={bool(xml_adjudicacion)}, HTML_adj={bool(html_adjudicacion)}, XML_form={bool(xml_formalizacion)}, PDF_acta={bool(pdf_acta_resolucion)}")

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

                # Si no encontramos HTML de adjudicación antes, buscar en documentos
                if not html_adjudicacion:
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

                # Buscar PDF del Acta de Resolución si no lo encontramos antes
                # (a veces está en una fila que dice "Documento de Acta de Resolución")
                if not pdf_acta_resolucion:
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        link_text = link.get_text(strip=True).lower()
                        parent = link.find_parent('tr')
                        parent_text = parent.get_text(strip=True).lower() if parent else ''

                        if '.pdf' in href.lower() and ('acta' in parent_text or 'resolución' in parent_text or 'resolucion' in parent_text):
                            pdf_acta_resolucion = href if href.startswith('http') else f"https://contrataciondelestado.es{href}"
                            datos['pdf_acta_resolucion_url'] = pdf_acta_resolucion
                            break

                # Resumen final
                campos_clave = ['nombre_comercial', 'expediente', 'objeto', 'importe_adjudicacion', 'direccion', 'telefono', 'email']
                campos_encontrados = [c for c in campos_clave if datos.get(c)]
                logger.info(f"PLACSP extrajo {len(datos)} campos en total. Clave: {campos_encontrados}")

                if not datos:
                    logger.warning(f"PLACSP: No se pudo extraer ningún dato de {url_licitacion}")

                return datos if datos else None

        except Exception as e:
            logger.error(f"Error scraping PLACSP: {e}", exc_info=True)
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

        El documento HTML de PLACSP usa estructura con:
        - <h5> para secciones/labels
        - <strong> para valores principales
        - Listas con guiones para datos adicionales
        - Formato: "Label: Valor" en muchas líneas

        Secciones típicas:
        - Entidad Adjudicadora (el cliente - datos de contacto importantes)
        - Adjudicatario (el ganador)
        - Importes de Adjudicación
        - Información sobre las ofertas
        """
        try:
            logger.info(f"Parseando HTML de adjudicación: {html_url[:80]}...")

            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    html_url,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    logger.warning(f"HTML adjudicación retornó {response.status_code}")
                    return None

                logger.info(f"HTML descargado: {len(response.text)} bytes")
                soup = BeautifulSoup(response.text, 'html.parser')
                datos = {}
                texto_completo = response.text.lower()
                texto_raw = response.text

                # === MÉTODO 1: Buscar <strong> después de <h5> (estructura típica PLACSP) ===
                for h5 in soup.find_all('h5'):
                    h5_text = h5.get_text(strip=True).lower()

                    # Buscar el siguiente <strong> que contenga el valor
                    next_strong = h5.find_next('strong')
                    if next_strong:
                        valor = next_strong.get_text(strip=True)

                        # Adjudicatario
                        if 'adjudicatario' in h5_text and 'entidad' not in h5_text:
                            if valor and len(valor) > 3:
                                datos['nombre_comercial'] = valor
                                logger.debug(f"H5: nombre_comercial = {valor}")

                        # Órgano/Entidad adjudicadora
                        elif 'entidad adjudicadora' in h5_text or 'órgano' in h5_text:
                            if valor and len(valor) > 3:
                                datos['organo_contratacion'] = valor
                                logger.debug(f"H5: organo_contratacion = {valor}")

                # === MÉTODO 2: Buscar patrones "Label: Valor" en el texto ===

                # NIF del adjudicatario (buscar cerca de "Adjudicatario" o solo el patrón)
                nif_patterns = [
                    r'NIF[:\s]*([A-Z]\d{8}|\d{8}[A-Z])',
                    r'CIF[:\s]*([A-Z]\d{8})',
                    r'\b([A-Z]\d{8})\b',  # Patrón NIF español
                ]
                for pattern in nif_patterns:
                    nif_match = re.search(pattern, texto_raw, re.I)
                    if nif_match:
                        datos['nif_verificado'] = nif_match.group(1).upper()
                        logger.debug(f"NIF encontrado: {datos['nif_verificado']}")
                        break

                # Es PYME
                if 'pyme' in texto_completo:
                    pyme_match = re.search(r'(?:es\s*)?pyme[:\s]*(sí|si|yes|true|no|false)?', texto_completo, re.I)
                    if pyme_match:
                        valor_pyme = pyme_match.group(1) if pyme_match.group(1) else ''
                        datos['es_pyme'] = valor_pyme.lower() in ['sí', 'si', 'yes', 'true', '']
                        logger.debug(f"Es PYME: {datos['es_pyme']}")

                # === DATOS DE CONTACTO DEL ADJUDICATARIO (teléfono y email) ===
                # La estructura típica de PLACSP usa:
                # - Sección "Adjudicatario" seguida de datos
                # - "→" como bullet points
                # - Labels como "Teléfono", "Correo Electrónico", "Dirección Física"

                # MÉTODO PRINCIPAL: Buscar en la sección entre "Adjudicatario" y la siguiente sección
                # (típicamente "Importes de Adjudicación" o "Entidad Adjudicadora")
                adj_section_match = re.search(
                    r'Adjudicatario.*?(?=Importes|Entidad\s*Adjudicadora|Motivación|Información|$)',
                    texto_raw, re.I | re.DOTALL
                )

                if adj_section_match:
                    adj_text = adj_section_match.group(0)
                    logger.debug(f"Sección Adjudicatario encontrada: {len(adj_text)} chars")

                    # Teléfono del adjudicatario (formato: +34 922276634 o 922276634)
                    tel_patterns = [
                        r'Tel[ée]fono[:\s→]*\+?34?\s*(\d{9}|\d{3}[\s.-]?\d{3}[\s.-]?\d{3})',
                        r'Tel[:\s→]*\+?34?\s*(\d{9})',
                        r'\+34\s*(\d{9})',
                    ]
                    for pattern in tel_patterns:
                        tel_match = re.search(pattern, adj_text, re.I)
                        if tel_match:
                            tel = re.sub(r'[^\d]', '', tel_match.group(1))
                            if len(tel) >= 9:
                                datos['telefono'] = tel
                                logger.info(f"✓ Teléfono adjudicatario: {tel}")
                                break

                    # Email del adjudicatario (formato: Correo Electrónico domaser@domasercanaria.com)
                    email_patterns = [
                        r'Correo\s*Electr[óo]nico[:\s→]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                        r'(?:Email|E-mail)[:\s→]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                        r'→\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                    ]
                    for pattern in email_patterns:
                        email_match = re.search(pattern, adj_text, re.I)
                        if email_match:
                            email = email_match.group(1)
                            if not any(x in email.lower() for x in ['noreply', 'no-reply', 'example', 'contratacion']):
                                datos['email'] = email
                                logger.info(f"✓ Email adjudicatario: {email}")
                                break

                    # Dirección Física del adjudicatario
                    # Formato típico: "Dirección Física → ACCESO AUTOPISTA, LA HIDALGA, Nº14, → (38550) ARAFO España"
                    dir_patterns = [
                        r'Direcci[óo]n\s*F[íi]sica[:\s→]*([^→\n]+(?:→[^→\n]+)*)',
                        r'Direcci[óo]n[:\s→]*([A-Z][^→\n]{10,80})',
                        r'→\s*((?:CALLE|AVENIDA|ACCESO|PLAZA|PASEO|C/)[^→\n]+)',
                    ]
                    for pattern in dir_patterns:
                        dir_match = re.search(pattern, adj_text, re.I)
                        if dir_match:
                            direccion = dir_match.group(1).strip()
                            # Limpiar múltiples → y espacios
                            direccion = re.sub(r'→\s*', ', ', direccion)
                            direccion = re.sub(r',\s*,', ',', direccion).strip(' ,')
                            if len(direccion) > 10:
                                datos['direccion'] = direccion
                                logger.info(f"✓ Dirección adjudicatario: {direccion[:60]}...")
                                break

                    # Código postal y localidad (formato: (38550) ARAFO)
                    cp_match = re.search(r'\((\d{5})\)\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)(?:\s*España)?(?:→|$|\n)', adj_text)
                    if cp_match:
                        datos['codigo_postal'] = cp_match.group(1)
                        datos['localidad'] = cp_match.group(2).strip()
                        logger.debug(f"CP: {datos['codigo_postal']}, Localidad: {datos['localidad']}")

                # Si no encontramos con el método principal, intentar patrones globales
                if not datos.get('telefono'):
                    # Buscar cualquier teléfono en la primera mitad del documento (antes de Entidad Adjudicadora)
                    primera_mitad = texto_raw[:len(texto_raw)//2]
                    tel_match = re.search(r'Tel[ée]fono[:\s→]*\+?34?\s*(\d{9})', primera_mitad, re.I)
                    if tel_match:
                        datos['telefono'] = tel_match.group(1)
                        logger.info(f"✓ Teléfono (global): {datos['telefono']}")

                if not datos.get('email'):
                    # Buscar primer email en la primera mitad
                    primera_mitad = texto_raw[:len(texto_raw)//2]
                    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', primera_mitad)
                    for email in emails:
                        if not any(x in email.lower() for x in ['noreply', 'no-reply', 'example', 'contratacion', 'hacienda']):
                            datos['email'] = email
                            logger.info(f"✓ Email (global): {email}")
                            break

                # === DATOS DEL ÓRGANO CONTRATANTE (EL CLIENTE - muy importante) ===

                # Dirección del órgano (buscar después de "Dirección" cerca de "Entidad")
                direccion_patterns = [
                    r'Direcci[óo]n[:\s]*([^<\n]{10,100})',
                    r'Domicilio[:\s]*([^<\n]{10,100})',
                    r'(?:Avenida|Calle|Plaza|Paseo)\s+[^<\n,]{5,50},?\s*(?:N[úu]mero\s*)?\d+',
                ]
                for pattern in direccion_patterns:
                    dir_match = re.search(pattern, texto_raw, re.I)
                    if dir_match:
                        direccion = dir_match.group(1) if dir_match.lastindex else dir_match.group(0)
                        direccion = direccion.strip()
                        if len(direccion) > 10:
                            datos['organo_direccion'] = direccion
                            logger.debug(f"Dirección órgano: {direccion[:50]}...")
                            break

                # Código postal y localidad
                cp_patterns = [
                    r'(\d{5})[,\s]+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,30})',
                    r'\((\d{5})\)[,\s]*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,30})',
                ]
                for pattern in cp_patterns:
                    cp_match = re.search(pattern, texto_raw)
                    if cp_match:
                        datos['organo_cp'] = cp_match.group(1)
                        localidad = cp_match.group(2).strip()
                        # Limpiar "España" si aparece
                        localidad = re.sub(r'\s*España.*$', '', localidad, flags=re.I).strip()
                        if localidad:
                            datos['organo_localidad'] = localidad
                        logger.debug(f"CP: {datos.get('organo_cp')}, Localidad: {datos.get('organo_localidad')}")
                        break

                # Teléfono del órgano (IMPORTANTE para contacto)
                tel_patterns = [
                    r'Tel[ée]fono[:\s]*(\d{9})',
                    r'Tel[ée]fono[:\s]*(\d{3}[\s.-]?\d{3}[\s.-]?\d{3})',
                    r'Tel[:\s]*(\d{9})',
                ]
                for pattern in tel_patterns:
                    tel_match = re.search(pattern, texto_raw, re.I)
                    if tel_match:
                        tel = re.sub(r'[^\d]', '', tel_match.group(1))
                        if len(tel) >= 9:
                            datos['organo_telefono'] = tel
                            logger.debug(f"Teléfono órgano: {tel}")
                            break

                # Email del órgano (IMPORTANTE para contacto)
                email_pattern = r'(?:Correo|Email|E-mail)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                email_match = re.search(email_pattern, texto_raw, re.I)
                if email_match:
                    email = email_match.group(1)
                    # Filtrar emails genéricos
                    if not any(x in email.lower() for x in ['noreply', 'no-reply', 'example']):
                        datos['organo_email'] = email
                        logger.debug(f"Email órgano: {email}")

                # También buscar emails sueltos si no encontramos con patrón
                if not datos.get('organo_email'):
                    all_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texto_raw)
                    for email in all_emails:
                        if not any(x in email.lower() for x in ['noreply', 'no-reply', 'example', 'cookie']):
                            datos['organo_email'] = email
                            logger.debug(f"Email encontrado: {email}")
                            break

                # Web del órgano
                web_match = re.search(r'(?:Web|P[áa]gina)[:\s]*(https?://[^\s<>"]+|www\.[^\s<>"]+)', texto_raw, re.I)
                if web_match:
                    web = web_match.group(1)
                    if not web.startswith('http'):
                        web = 'http://' + web
                    datos['organo_web'] = web
                    logger.debug(f"Web órgano: {web}")

                # === DATOS DEL CONTRATO ===

                # Importe sin impuestos (ofertado)
                importe_patterns = [
                    r'(?:Importe|Valor).*?sin\s*impuestos[:\s]*([\d.,]+)\s*EUR',
                    r'sin\s*impuestos[:\s]*([\d.,]+)\s*EUR',
                    r'([\d.,]+)\s*EUR\s*\(?sin\s*impuestos',
                ]
                for pattern in importe_patterns:
                    importe_match = re.search(pattern, texto_raw, re.I)
                    if importe_match:
                        datos['importe_adjudicacion'] = f"{importe_match.group(1)} EUR"
                        logger.debug(f"Importe sin IVA: {datos['importe_adjudicacion']}")
                        break

                # Importe con impuestos
                importe_iva_patterns = [
                    r'(?:Importe|Valor).*?con\s*impuestos[:\s]*([\d.,]+)\s*EUR',
                    r'con\s*impuestos[:\s]*([\d.,]+)\s*EUR',
                    r'([\d.,]+)\s*EUR\s*\(?con\s*impuestos',
                ]
                for pattern in importe_iva_patterns:
                    importe_match = re.search(pattern, texto_raw, re.I)
                    if importe_match:
                        datos['importe_con_iva'] = f"{importe_match.group(1)} EUR"
                        logger.debug(f"Importe con IVA: {datos['importe_con_iva']}")
                        break

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

                # === INFORMACIÓN ADICIONAL ===

                # Plazo de ejecución
                plazo_patterns = [
                    r'Plazo\s*(?:de\s*)?[Ee]jecuci[óo]n[:\s]*(\d+)\s*(d[íi]as?|meses?|a[ñn]os?)',
                    r'(\d+)\s*(d[íi]as?|meses?)\s*(?:de\s*)?plazo',
                ]
                for pattern in plazo_patterns:
                    plazo_match = re.search(pattern, texto_raw, re.I)
                    if plazo_match:
                        datos['duracion_contrato'] = f"{plazo_match.group(1)} {plazo_match.group(2)}"
                        logger.debug(f"Plazo: {datos['duracion_contrato']}")
                        break

                # Fecha de acuerdo/adjudicación
                fecha_patterns = [
                    r'(?:Fecha|Acuerdo).*?adjudicaci[óo]n[:\s]*(\d{1,2}/\d{1,2}/\d{4})',
                    r'(\d{1,2}/\d{1,2}/\d{4}).*?(?:acuerdo|adjudicaci[óo]n)',
                    r'Fecha[:\s]*(\d{1,2}/\d{1,2}/\d{4})',
                ]
                for pattern in fecha_patterns:
                    fecha_match = re.search(pattern, texto_raw, re.I)
                    if fecha_match:
                        datos['fecha_adjudicacion'] = fecha_match.group(1)
                        logger.debug(f"Fecha adjudicación: {datos['fecha_adjudicacion']}")
                        break

                # Número de ofertas
                ofertas_patterns = [
                    r'(?:N[úu]mero|Ofertas)\s*(?:de\s*)?(?:ofertas|licitadores)[:\s]*(\d+)',
                    r'(\d+)\s*ofertas?\s*recibidas?',
                    r'recibidas?[:\s]*(\d+)',
                ]
                for pattern in ofertas_patterns:
                    ofertas_match = re.search(pattern, texto_raw, re.I)
                    if ofertas_match:
                        try:
                            datos['numero_ofertas'] = int(ofertas_match.group(1))
                            logger.debug(f"Número ofertas: {datos['numero_ofertas']}")
                        except:
                            pass
                        break

                # CPV
                cpv_match = re.search(r'(?:CPV|C[óo]digo)[:\s]*(\d{8})', texto_raw, re.I)
                if cpv_match:
                    datos['cpv'] = cpv_match.group(1)
                    logger.debug(f"CPV: {datos['cpv']}")

                # Lugar de ejecución
                lugar_patterns = [
                    r'(?:Lugar|Subentidad)\s*(?:de\s*)?(?:ejecuci[óo]n|Nacional)[:\s]*([A-ZÁÉÍÓÚÑa-záéíóúñ\s,]{5,50})',
                    r'ES\d{3}\s*-\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,30})',  # Código NUTS
                ]
                for pattern in lugar_patterns:
                    lugar_match = re.search(pattern, texto_raw, re.I)
                    if lugar_match:
                        datos['lugar_ejecucion'] = lugar_match.group(1).strip()
                        logger.debug(f"Lugar ejecución: {datos['lugar_ejecucion']}")
                        break

                # Financiación UE
                if 'fondos de la ue' in texto_completo or 'financiación con fondos' in texto_completo or 'financiacion' in texto_completo:
                    ue_patterns = [
                        r'(Plan\s*de\s*Recuperaci[óo]n[^.]{0,50})',
                        r'(Fondos?\s*(?:de\s*la\s*)?UE[^.]{0,30})',
                        r'(PRTR[^.]{0,30})',
                        r'(NextGeneration[^.]{0,30})',
                    ]
                    for pattern in ue_patterns:
                        ue_match = re.search(pattern, texto_raw, re.I)
                        if ue_match:
                            datos['financiacion_ue'] = 'Sí - Fondos UE'
                            datos['programa_financiacion'] = ue_match.group(1).strip()
                            logger.debug(f"Financiación UE: {datos['programa_financiacion']}")
                            break
                    if 'financiacion_ue' not in datos:
                        datos['financiacion_ue'] = 'Sí - Fondos UE'

                # Resumen final
                campos_encontrados = [k for k in datos.keys()]
                logger.info(f"HTML adjudicación parseado: {len(datos)} campos - {campos_encontrados}")
                return datos if datos else None

        except Exception as e:
            logger.error(f"Error parseando HTML de adjudicación: {e}", exc_info=True)
            return None

    async def _extract_competidores_from_pdf(self, pdf_url: str, nif_ganador: str) -> Optional[List[Dict[str, Any]]]:
        """
        Extrae la lista de empresas competidoras del PDF del Acta de Resolución.

        El PDF contiene una tabla con:
        - CIF/NIF de cada empresa
        - Nombre de la empresa
        - Puntuación obtenida

        Returns:
            Lista de competidores (excluyendo al ganador) con formato:
            [{nif: str, nombre: str, puntuacion: str}, ...]
        """
        try:
            async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
                response = await client.get(
                    pdf_url,
                    headers={"User-Agent": self.USER_AGENT},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    logger.warning(f"PDF Acta retornó {response.status_code}")
                    return None

                # Guardar PDF temporalmente
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name

                competidores = []
                nif_ganador_upper = nif_ganador.upper() if nif_ganador else ""

                try:
                    with pdfplumber.open(tmp_path) as pdf:
                        for page in pdf.pages:
                            # Intentar extraer tablas
                            tables = page.extract_tables()

                            for table in tables:
                                if not table:
                                    continue

                                # Buscar tabla con CIF/NIF
                                for row in table:
                                    if not row or len(row) < 2:
                                        continue

                                    # Buscar NIF en cualquier celda (formato A12345678 o 12345678A)
                                    nif_found = None
                                    nombre_found = None
                                    puntuacion_found = None

                                    for i, cell in enumerate(row):
                                        if not cell:
                                            continue

                                        cell_text = str(cell).strip()

                                        # Detectar NIF/CIF (letra + 8 dígitos o 8 dígitos + letra)
                                        nif_match = re.search(r'\b([A-Z]\d{8}|\d{8}[A-Z])\b', cell_text, re.I)
                                        if nif_match:
                                            nif_found = nif_match.group(1).upper()
                                            continue

                                        # Detectar puntuación (número seguido de "puntos" o formato decimal)
                                        punt_match = re.search(r'(\d+[,.]?\d*)\s*(?:puntos?)?$', cell_text, re.I)
                                        if punt_match and len(cell_text) < 20:
                                            puntuacion_found = punt_match.group(1).replace(',', '.')
                                            continue

                                        # Lo que queda y tiene más de 5 caracteres probablemente es el nombre
                                        if len(cell_text) > 5 and not nif_match:
                                            # Verificar que no sea header
                                            if cell_text.upper() not in ['CIF', 'NIF', 'NOMBRE', 'PUNTUACIÓN', 'PUNTUACION', 'EMPRESA']:
                                                nombre_found = cell_text

                                    # Si encontramos NIF y nombre, añadir (excluyendo al ganador)
                                    if nif_found and nombre_found:
                                        if nif_found != nif_ganador_upper:
                                            competidor = {
                                                'nif': nif_found,
                                                'nombre': nombre_found,
                                                'puntuacion': puntuacion_found
                                            }
                                            # Evitar duplicados
                                            if not any(c['nif'] == nif_found for c in competidores):
                                                competidores.append(competidor)
                                                logger.info(f"Competidor encontrado: {nombre_found} ({nif_found})")

                            # Si no encontramos tablas, intentar con el texto
                            if not competidores:
                                text = page.extract_text()
                                if text:
                                    # Buscar patrones de NIF seguidos de nombre
                                    # Patrón: NIF en una línea, seguido de nombre
                                    lines = text.split('\n')
                                    for i, line in enumerate(lines):
                                        nif_match = re.search(r'\b([A-Z]\d{8}|\d{8}[A-Z])\b', line, re.I)
                                        if nif_match:
                                            nif = nif_match.group(1).upper()
                                            if nif == nif_ganador_upper:
                                                continue

                                            # Buscar nombre en la misma línea o la siguiente
                                            nombre = None
                                            # Texto después del NIF en la misma línea
                                            after_nif = line[nif_match.end():].strip()
                                            if after_nif and len(after_nif) > 5:
                                                # Quitar puntuación si está al final
                                                nombre = re.sub(r'\s+\d+[,.]?\d*\s*(?:puntos?)?\s*$', '', after_nif, flags=re.I).strip()
                                            elif i + 1 < len(lines):
                                                next_line = lines[i + 1].strip()
                                                if next_line and len(next_line) > 5 and not re.match(r'^[A-Z]\d{8}', next_line, re.I):
                                                    nombre = re.sub(r'\s+\d+[,.]?\d*\s*(?:puntos?)?\s*$', '', next_line, flags=re.I).strip()

                                            if nombre and not any(c['nif'] == nif for c in competidores):
                                                # Buscar puntuación
                                                punt_match = re.search(r'(\d+[,.]?\d*)\s*(?:puntos?)?', line)
                                                puntuacion = punt_match.group(1).replace(',', '.') if punt_match else None

                                                competidores.append({
                                                    'nif': nif,
                                                    'nombre': nombre,
                                                    'puntuacion': puntuacion
                                                })

                finally:
                    # Limpiar archivo temporal
                    import os
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass

                # Ordenar por puntuación si existe
                if competidores:
                    competidores.sort(
                        key=lambda x: float(x['puntuacion']) if x.get('puntuacion') else 0,
                        reverse=True
                    )
                    logger.info(f"Total competidores extraídos del PDF: {len(competidores)}")

                return competidores if competidores else None

        except Exception as e:
            logger.error(f"Error extrayendo competidores del PDF: {e}")
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
