#!/usr/bin/env python3
"""
SpotterSRS-Licitaciones (Drones)
================================
Detector de licitaciones ABIERTAS en PLACSP relacionadas con servicios de drones.

A diferencia del SpotterSRS principal (que busca adjudicaciones para subcontratacion),
este modulo busca oportunidades de licitacion ANTES de adjudicar para que el partner
pueda pujar directamente.

Uso:
    python -m services.spotter_licitaciones_drones

Feed PLACSP:
    https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3.atom
"""

import os
import sys
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path

# Agregar el directorio backend al path para imports
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from services.spotter_licitaciones import LicitacionAnalyzer, LicitacionInput, get_analyzer


# ============================================================================
# CONFIGURACION
# ============================================================================

PLACSP_FEED_URL = "https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3.atom"

# Configuracion de certificados (produccion)
CERT_DIR = "/var/www/srs-crm/backend/certs"
CLIENT_CERT = os.path.join(CERT_DIR, "client_cert.pem")
CLIENT_KEY = os.path.join(CERT_DIR, "client_key_nopass.pem")

# Configuracion local (desarrollo)
LOCAL_CERT_DIR = BACKEND_DIR / "certs"
LOCAL_CLIENT_CERT = LOCAL_CERT_DIR / "client_cert.pem"
LOCAL_CLIENT_KEY = LOCAL_CERT_DIR / "client_key_nopass.pem"

# Logs
LOG_DIR = BACKEND_DIR / "logs"

# API del CRM
CRM_API_URL = os.environ.get("CRM_API_URL", "http://localhost:8000/api")

# Umbral minimo de score para guardar licitacion
SCORE_THRESHOLD = 30


# ============================================================================
# NAMESPACES XML (PLACSP)
# ============================================================================

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'cbc': 'urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2',
    'cfs': 'urn:dgpe:names:draft:codice:schema:xsd:ContractFolderStatus-2',
}


# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class LicitacionDrones:
    """Estructura de una licitacion de drones detectada"""
    expediente: str
    titulo: str
    descripcion: str
    cpv: str
    presupuesto: float
    organo_contratacion: str
    fecha_publicacion: str  # ISO format
    fecha_limite: Optional[str]  # ISO format
    dias_restantes: Optional[int]
    url_licitacion: str
    url_pliego: Optional[str]
    score: int
    relevante: bool
    cpv_matches: List[Dict[str, Any]]
    keywords_detectados: List[str]
    categoria_principal: Optional[str]
    estado: str = "nueva"
    fecha_deteccion: str = ""
    notas: str = ""

    def __post_init__(self):
        if not self.fecha_deteccion:
            self.fecha_deteccion = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def log(msg: str):
    """Log con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

    # Guardar en archivo de log
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = LOG_DIR / f"spotter_drones_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


def get_certificates():
    """Obtiene la ruta a los certificados (produccion o local)"""
    if os.path.exists(CLIENT_CERT) and os.path.exists(CLIENT_KEY):
        return (CLIENT_CERT, CLIENT_KEY)
    elif LOCAL_CLIENT_CERT.exists() and LOCAL_CLIENT_KEY.exists():
        return (str(LOCAL_CLIENT_CERT), str(LOCAL_CLIENT_KEY))
    else:
        return None


def calcular_dias_restantes(fecha_limite_str: Optional[str]) -> Optional[int]:
    """Calcula los dias restantes hasta la fecha limite"""
    if not fecha_limite_str:
        return None

    try:
        # Parsear fecha (puede venir en varios formatos)
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                fecha_limite = datetime.strptime(fecha_limite_str.replace("+00:00", "Z").replace("Z", ""), fmt.replace("Z", ""))
                break
            except ValueError:
                continue
        else:
            return None

        hoy = datetime.now()
        delta = fecha_limite - hoy
        return max(0, delta.days)
    except Exception:
        return None


# ============================================================================
# DESCARGA Y PARSEO DEL FEED
# ============================================================================

def descargar_feed_placsp() -> Optional[str]:
    """Descarga el feed ATOM de PLACSP con certificado FNMT"""
    log("Descargando feed ATOM de PLACSP...")

    certs = get_certificates()

    try:
        if certs:
            log(f"Usando certificados: {certs[0]}")
            response = requests.get(
                PLACSP_FEED_URL,
                cert=certs,
                timeout=120
            )
        else:
            log("ADVERTENCIA: Sin certificados, intentando sin autenticacion...")
            response = requests.get(PLACSP_FEED_URL, timeout=120)

        response.raise_for_status()
        log(f"Feed descargado: {len(response.text)} bytes")
        return response.text

    except requests.exceptions.SSLError as e:
        log(f"ERROR SSL: {e}")
        log("Verifica que los certificados FNMT esten correctamente configurados")
        return None
    except requests.exceptions.RequestException as e:
        log(f"ERROR descargando feed: {e}")
        return None


def parsear_entry_licitacion(entry: ET.Element) -> Optional[Dict[str, Any]]:
    """
    Parsea un entry del feed ATOM y extrae datos de la licitacion.
    Solo procesa licitaciones ABIERTAS (PUB, EV, etc.)
    """
    try:
        # Extraer titulo
        title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
        titulo = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

        # Extraer URL
        link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
        url = link_elem.get('href', '') if link_elem is not None else ""

        # Buscar ContractFolderStatus
        cfs = None
        for child in entry.iter():
            if 'ContractFolderStatus' in child.tag:
                cfs = child
                break

        if cfs is None:
            return None

        # Extraer estado - solo queremos licitaciones abiertas
        estado = ""
        for elem in cfs.iter():
            if 'ContractFolderStatusCode' in elem.tag:
                estado = elem.text or ""
                break

        # Estados de licitaciones ABIERTAS:
        # PUB = Publicada, EV = En evaluacion, ADM = Anuncio previo,
        # PEND = Pendiente de publicacion, PRE = Preanuncio
        estados_abiertos = ["PUB", "EV", "ADM", "PEND", "PRE", "PUBLICADA", "EVALUACION"]
        if estado.upper() not in estados_abiertos:
            return None

        # Extraer expediente
        expediente = ""
        for elem in cfs.iter():
            if 'ContractFolderID' in elem.tag:
                expediente = elem.text or ""
                break

        # Extraer CPV
        cpv = ""
        for elem in cfs.iter():
            if 'ItemClassificationCode' in elem.tag:
                cpv = elem.text or ""
                break

        # Extraer descripcion (del objeto del contrato)
        descripcion = titulo
        for elem in cfs.iter():
            if elem.tag.endswith('Name') and elem.text and len(elem.text) > len(descripcion):
                descripcion = elem.text.strip()
                break

        # Extraer presupuesto
        presupuesto = 0.0
        for elem in cfs.iter():
            if 'TotalAmount' in elem.tag or 'BudgetAmount' in elem.tag or 'TaxExclusiveAmount' in elem.tag:
                try:
                    presupuesto = float(elem.text)
                    break
                except (ValueError, TypeError):
                    pass

        # Extraer organo contratacion
        organo = ""
        for elem in cfs.iter():
            if 'LocatedContractingParty' in elem.tag or 'ContractingParty' in elem.tag:
                for sub in elem.iter():
                    if sub.tag.endswith('Name') and sub.text:
                        organo = sub.text.strip()
                        break
                break

        # Extraer fecha publicacion
        fecha_publicacion = ""
        for elem in cfs.iter():
            if 'IssueDate' in elem.tag and elem.text:
                fecha_publicacion = elem.text
                break

        # Extraer fecha limite presentacion
        fecha_limite = None
        for elem in cfs.iter():
            if 'EndDate' in elem.tag and elem.text:
                fecha_limite = elem.text
                break
            if 'TenderSubmissionDeadlinePeriod' in elem.tag:
                for sub in elem.iter():
                    if 'EndDate' in sub.tag and sub.text:
                        fecha_limite = sub.text
                        break

        # Extraer URL del pliego
        url_pliego = None
        for elem in cfs.iter():
            if 'DocumentReference' in elem.tag:
                for sub in elem.iter():
                    if sub.tag.endswith('URI') and sub.text:
                        uri = sub.text
                        if 'pliego' in uri.lower() or 'ppt' in uri.lower() or 'pcap' in uri.lower():
                            url_pliego = uri
                            break
                        elif not url_pliego:  # Cualquier documento si no hay pliego especifico
                            url_pliego = uri

        return {
            "expediente": expediente,
            "titulo": titulo,
            "descripcion": descripcion,
            "cpv": cpv,
            "presupuesto": presupuesto,
            "organo_contratacion": organo,
            "fecha_publicacion": fecha_publicacion,
            "fecha_limite": fecha_limite,
            "url_licitacion": url,
            "url_pliego": url_pliego,
            "estado_placsp": estado
        }

    except Exception as e:
        log(f"Error parseando entry: {e}")
        return None


def procesar_feed(xml_content: str) -> List[Dict[str, Any]]:
    """Procesa el feed completo y extrae licitaciones abiertas"""
    licitaciones = []

    try:
        root = ET.fromstring(xml_content)
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

        log(f"Procesando {len(entries)} entries del feed...")

        for entry in entries:
            lic_data = parsear_entry_licitacion(entry)
            if lic_data:
                licitaciones.append(lic_data)

        log(f"Encontradas {len(licitaciones)} licitaciones abiertas")

    except ET.ParseError as e:
        log(f"Error parseando XML: {e}")

    return licitaciones


# ============================================================================
# ANALISIS Y SCORING
# ============================================================================

def analizar_licitaciones(licitaciones_raw: List[Dict[str, Any]]) -> List[LicitacionDrones]:
    """Analiza las licitaciones con el motor de scoring de drones"""
    analyzer = get_analyzer()
    resultados = []

    log(f"Analizando {len(licitaciones_raw)} licitaciones...")

    for lic_data in licitaciones_raw:
        # Crear input para el analizador
        lic_input = LicitacionInput(
            titulo=lic_data.get("titulo", ""),
            descripcion=lic_data.get("descripcion", ""),
            cpv=lic_data.get("cpv", ""),
            presupuesto=lic_data.get("presupuesto"),
            organo_contratacion=lic_data.get("organo_contratacion", "")
        )

        # Analizar
        resultado = analyzer.analizar(lic_input)

        # Calcular dias restantes
        dias_restantes = calcular_dias_restantes(lic_data.get("fecha_limite"))

        # Solo incluir si cumple el umbral o es CPV directo de drones
        es_cpv_drones = analyzer.es_cpv_drones_directo(lic_data.get("cpv", ""))

        if resultado.score >= SCORE_THRESHOLD or es_cpv_drones or resultado.relevante:
            licitacion = LicitacionDrones(
                expediente=lic_data.get("expediente", ""),
                titulo=lic_data.get("titulo", ""),
                descripcion=lic_data.get("descripcion", ""),
                cpv=lic_data.get("cpv", ""),
                presupuesto=lic_data.get("presupuesto", 0),
                organo_contratacion=lic_data.get("organo_contratacion", ""),
                fecha_publicacion=lic_data.get("fecha_publicacion", ""),
                fecha_limite=lic_data.get("fecha_limite"),
                dias_restantes=dias_restantes,
                url_licitacion=lic_data.get("url_licitacion", ""),
                url_pliego=lic_data.get("url_pliego"),
                score=resultado.score if not es_cpv_drones else max(resultado.score, 95),
                relevante=resultado.relevante or es_cpv_drones,
                cpv_matches=resultado.cpv_matches,
                keywords_detectados=resultado.keywords_detectados,
                categoria_principal=resultado.categoria_principal or ("Suministro de Equipos" if es_cpv_drones else None)
            )
            resultados.append(licitacion)

    # Ordenar por score descendente
    resultados.sort(key=lambda x: x.score, reverse=True)

    log(f"Detectadas {len(resultados)} licitaciones relevantes (score >= {SCORE_THRESHOLD})")
    return resultados


# ============================================================================
# GUARDADO EN MONGODB
# ============================================================================

def guardar_en_mongodb(licitaciones: List[LicitacionDrones]) -> Dict[str, int]:
    """Envia las licitaciones detectadas al CRM para guardado en MongoDB"""
    if not licitaciones:
        return {"imported": 0, "duplicates": 0, "errors": 0}

    log(f"Enviando {len(licitaciones)} licitaciones al CRM...")

    # Preparar datos para la API
    data = {
        "licitaciones": [lic.to_dict() for lic in licitaciones]
    }

    try:
        response = requests.post(
            f"{CRM_API_URL}/oportunidades/import-internal",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        log(f"Resultado: importadas={result.get('imported', 0)}, duplicadas={result.get('duplicates', 0)}")
        return result
    except requests.exceptions.RequestException as e:
        log(f"ERROR enviando al CRM: {e}")
        return {"imported": 0, "duplicates": 0, "errors": len(licitaciones)}


def guardar_local_json(licitaciones: List[LicitacionDrones], filepath: str = None):
    """Guarda las licitaciones en un archivo JSON local (backup/debug)"""
    if filepath is None:
        os.makedirs(LOG_DIR, exist_ok=True)
        filepath = LOG_DIR / f"licitaciones_drones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    data = {
        "fecha_ejecucion": datetime.now(timezone.utc).isoformat(),
        "total": len(licitaciones),
        "licitaciones": [lic.to_dict() for lic in licitaciones]
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log(f"Guardado backup local: {filepath}")
    return filepath


# ============================================================================
# REPORTE
# ============================================================================

def generar_reporte(licitaciones: List[LicitacionDrones]) -> str:
    """Genera un reporte de las licitaciones detectadas"""
    lines = [
        "",
        "=" * 70,
        "  SPOTTER SRS - LICITACIONES DRONES",
        "  Detectadas: " + datetime.now().strftime("%Y-%m-%d %H:%M"),
        "=" * 70,
        f"  Total licitaciones relevantes: {len(licitaciones)}",
        ""
    ]

    # Resumen por categoria
    categorias = {}
    for lic in licitaciones:
        cat = lic.categoria_principal or "Sin categoria"
        categorias[cat] = categorias.get(cat, 0) + 1

    lines.append("  DISTRIBUCION POR CATEGORIA:")
    for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"    - {cat}: {count}")

    # Resumen por score
    alta = len([l for l in licitaciones if l.score >= 80])
    media = len([l for l in licitaciones if 60 <= l.score < 80])
    baja = len([l for l in licitaciones if 30 <= l.score < 60])

    lines.append("")
    lines.append("  DISTRIBUCION POR SCORE:")
    lines.append(f"    - Alta (>=80): {alta}")
    lines.append(f"    - Media (60-79): {media}")
    lines.append(f"    - Baja (30-59): {baja}")

    # Valor total
    valor_total = sum(l.presupuesto for l in licitaciones)
    lines.append("")
    lines.append(f"  VALOR TOTAL: {valor_total:,.0f} EUR")

    # Top 10 por score
    lines.append("")
    lines.append("  TOP 10 POR SCORE:")
    lines.append("-" * 70)

    for i, lic in enumerate(licitaciones[:10], 1):
        score_color = "!!!" if lic.score >= 80 else "! " if lic.score >= 60 else "  "
        lines.append(f"  {score_color}[{i}] Score: {lic.score} | {lic.presupuesto:,.0f} EUR")
        lines.append(f"      {lic.titulo[:65]}...")
        lines.append(f"      Org: {lic.organo_contratacion[:50]}")
        if lic.dias_restantes is not None:
            lines.append(f"      Dias restantes: {lic.dias_restantes}")
        lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Funcion principal - ejecuta el spotter de licitaciones de drones"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     SPOTTER SRS - LICITACIONES DRONES                     ║
    ║     "Detectando oportunidades antes que nadie"            ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    log("=" * 60)
    log("SPOTTER SRS - LICITACIONES DRONES - Ejecucion")
    log("=" * 60)

    # 1. Descargar feed de PLACSP
    xml_content = descargar_feed_placsp()
    if not xml_content:
        log("ERROR: No se pudo obtener el feed de PLACSP")
        sys.exit(1)

    # 2. Parsear licitaciones abiertas
    licitaciones_raw = procesar_feed(xml_content)
    if not licitaciones_raw:
        log("No se encontraron licitaciones abiertas en el feed")
        sys.exit(0)

    # 3. Analizar con motor de scoring de drones
    licitaciones = analizar_licitaciones(licitaciones_raw)

    if not licitaciones:
        log("No se detectaron licitaciones relevantes para drones")
        sys.exit(0)

    # 4. Generar y mostrar reporte
    reporte = generar_reporte(licitaciones)
    print(reporte)

    # 5. Guardar backup local
    guardar_local_json(licitaciones)

    # 6. Intentar enviar al CRM
    resultado = guardar_en_mongodb(licitaciones)

    log("=" * 60)
    log("EJECUCION COMPLETADA")
    log(f"  - Licitaciones detectadas: {len(licitaciones)}")
    log(f"  - Importadas al CRM: {resultado.get('imported', 0)}")
    log(f"  - Duplicadas: {resultado.get('duplicates', 0)}")
    log("=" * 60)


if __name__ == "__main__":
    main()
