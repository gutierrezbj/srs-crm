#!/usr/bin/env python3
"""
Wrapper para ejecutar SpotterSRS y enviar resultados al CRM
Diseñado para ejecución via cron

Mejoras v2.1:
- Validación de certificados al inicio
- Logging estructurado
- Soporte para variables de entorno
- Detección automática de rutas
"""
import sys
import os
import json
import requests
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging ANTES de cualquier import del proyecto
LOG_DIR = os.getenv("LOG_DIR", "/app/logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f"spotter_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, '/app')

from app.spotter.spotter_srs import (
    procesar_feed, 
    generar_json_crm,
    NivelDolor
)

# Configuración con soporte para variables de entorno
CRM_API_URL = os.getenv("CRM_API_URL", "http://172.17.0.1:8000/api/oportunidades/spotter-internal")
PLACSP_FEED_URL = os.getenv(
    "PLACSP_FEED_URL",
    "https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3.atom"
)

# Auto-detectar directorio de certificados
CERT_DIR = os.getenv("CERT_DIR")
if not CERT_DIR:
    # Intentar detectar automáticamente
    possible_paths = [
        "/app/certs",
        "/opt/apps/srs-crm/backend/certs",
        "/var/www/srs-crm/backend/certs"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            CERT_DIR = path
            logger.info(f"Auto-detected certificate directory: {CERT_DIR}")
            break
    
    if not CERT_DIR:
        CERT_DIR = "/app/certs"  # Default

CLIENT_CERT = os.path.join(CERT_DIR, "client_cert.pem")
CLIENT_KEY = os.path.join(CERT_DIR, "client_key_nopass.pem")

def validate_certificates():
    """Validar que los certificados existen antes de ejecutar."""
    logger.info("Validating SSL certificates...")
    logger.info(f"Certificate directory: {CERT_DIR}")
    logger.info(f"Certificate file: {CLIENT_CERT}")
    logger.info(f"Key file: {CLIENT_KEY}")
    
    if not os.path.exists(CERT_DIR):
        logger.error(f"❌ Certificate directory does not exist: {CERT_DIR}")
        logger.error("Please ensure certificates are mounted correctly in Docker.")
        return False
    
    if not os.path.exists(CLIENT_CERT):
        logger.error(f"❌ Certificate file not found: {CLIENT_CERT}")
        logger.error("Available files in cert directory:")
        try:
            for f in os.listdir(CERT_DIR):
                logger.error(f"  - {f}")
        except Exception as e:
            logger.error(f"  Could not list directory: {e}")
        return False
    
    if not os.path.exists(CLIENT_KEY):
        logger.error(f"❌ Private key file not found: {CLIENT_KEY}")
        return False
    
    # Verificar permisos de lectura
    if not os.access(CLIENT_CERT, os.R_OK):
        logger.error(f"❌ Cannot read certificate file: {CLIENT_CERT}")
        return False
    
    if not os.access(CLIENT_KEY, os.R_OK):
        logger.error(f"❌ Cannot read key file: {CLIENT_KEY}")
        return False
    
    logger.info("✅ SSL certificates validated successfully")
    return True

def fetch_placsp_feed():
    """Descargar feed PLACSP usando certificados SSL."""
    logger.info("Descargando feed Atom de PLACSP con certificado...")
    logger.info(f"URL: {PLACSP_FEED_URL}")
    logger.info(f"Using certificate: {CLIENT_CERT}")
    
    try:
        response = requests.get(
            PLACSP_FEED_URL,
            cert=(CLIENT_CERT, CLIENT_KEY),
            timeout=120,
            verify=True
        )
        response.raise_for_status()
        logger.info(f"✅ Feed descargado: {len(response.text)} bytes")
        
        # Verificar que el feed no esté vacío
        if len(response.text) < 100:
            logger.warning(f"⚠️ Feed seems too small: {len(response.text)} bytes")
            logger.warning(f"Response preview: {response.text[:200]}")
        
        return response.text
    except requests.exceptions.SSLError as e:
        logger.error(f"❌ SSL Error: {e}")
        logger.error("This usually means:")
        logger.error("  1. Certificate is invalid or expired")
        logger.error("  2. Certificate doesn't match the private key")
        logger.error("  3. Certificate is not authorized for this feed")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP Error {e.response.status_code}: {e}")
        logger.error(f"Response body: {e.response.text[:500]}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Connection Error: {e}")
        return None
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out after 120 seconds")
        return None
    except Exception as e:
        logger.error(f"❌ ERROR descargando feed: {e}")
        logger.exception("Full traceback:")
        return None

def transform_to_crm_format(json_str):
    data = json.loads(json_str)
    crm_oportunidades = []
    for op in data.get("oportunidades", []):
        tipo_raw = op["analisis"]["tipo_oportunidad"]
        tipo_srs = "IT / Soporte tecnico"
        if "Cableado" in tipo_raw:
            tipo_srs = "Telecomunicaciones"
        elif "Ciberseguridad" in tipo_raw or "ENS" in tipo_raw:
            tipo_srs = "Consultoria ENS"
        elif "Comunicaciones" in tipo_raw:
            tipo_srs = "Telecomunicaciones"
        elif "Dron" in tipo_raw:
            tipo_srs = "Drones / Inspeccion"
        
        indicadores = []
        nivel = op["analisis"]["nivel_dolor"]
        if nivel in ["CRITICO", "ALTO"]:
            indicadores.append(f"Urgencia: {nivel}")
        
        crm_op = {
            "expediente": op["contrato"]["expediente"],
            "adjudicatario": op["empresa"],
            "nif": op["nif"] or "",
            "importe": op["contrato"]["importe"],
            "objeto": op["contrato"]["objeto"],
            "cpv": op["contrato"]["cpv"] or "",
            "score": op["analisis"]["score"],
            "tipo_srs": tipo_srs,
            "keywords": op["analisis"]["keywords"],
            "indicadores_dolor": indicadores,
            "fecha_adjudicacion": op["contrato"]["fecha_adjudicacion"],
            "fecha_fin_contrato": None,
            "dias_restantes": op["analisis"]["dias_restantes"],
            "url_licitacion": op["documentacion"]["url_licitacion"],
            "url_pliego": op["documentacion"]["url_pliego_tecnico"],
            "organo_contratacion": op["contrato"]["organo"] or "",
            "es_pyme": op["es_pyme"],
            "convertido_lead": False,
            "fecha_deteccion": datetime.now().isoformat()
        }
        crm_oportunidades.append(crm_op)
    return {"oportunidades": crm_oportunidades}

def send_to_crm(data):
    """Enviar oportunidades al CRM vía API interna."""
    logger.info(f"Enviando {len(data['oportunidades'])} oportunidades al CRM...")
    logger.info(f"API URL: {CRM_API_URL}")
    
    try:
        response = requests.post(
            CRM_API_URL,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"✅ Resultado: {result}")
        return result
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP Error {e.response.status_code}: {e}")
        logger.error(f"Response: {e.response.text[:500]}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Cannot connect to CRM API at {CRM_API_URL}")
        logger.error(f"Error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ ERROR enviando al CRM: {e}")
        logger.exception("Full traceback:")
        return None

def main():
    """Función principal del SpotterSRS cron job."""
    logger.info("=" * 60)
    logger.info("   SPOTTER SRS - Ejecución Cron")
    logger.info("=" * 60)
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info(f"Certificate directory: {CERT_DIR}")
    logger.info(f"CRM API URL: {CRM_API_URL}")
    logger.info("=" * 60)
    
    # Validar certificados antes de continuar
    if not validate_certificates():
        logger.error("❌ Certificate validation failed. Aborting.")
        sys.exit(1)
    
    # Descargar feed
    xml_content = fetch_placsp_feed()
    if not xml_content:
        logger.error("❌ Abortando: no se pudo obtener el feed")
        sys.exit(1)
    
    # Procesar feed
    logger.info("Procesando feed (filtrando ADJ y RES)...")
    try:
        adjudicaciones = procesar_feed(xml_content)
        logger.info(f"✅ Detectadas {len(adjudicaciones)} oportunidades relevantes")
    except Exception as e:
        logger.error(f"❌ ERROR procesando feed: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
    
    if not adjudicaciones:
        logger.info("ℹ️  No se encontraron oportunidades relevantes en este ciclo")
        sys.exit(0)
    
    # Transformar y enviar al CRM
    try:
        json_str = generar_json_crm(adjudicaciones)
        crm_data = transform_to_crm_format(json_str)
        result = send_to_crm(crm_data)
        
        if result:
            logger.info(f"✅ Importadas: {result.get('imported', 0)}, Duplicadas: {result.get('duplicates', 0)}")
        else:
            logger.warning("⚠️ No se pudo enviar al CRM, pero el proceso continuó")
    except Exception as e:
        logger.error(f"❌ ERROR en transformación/envío: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
    
    logger.info("✅ Ejecución completada exitosamente")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
