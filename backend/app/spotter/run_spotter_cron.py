#!/usr/bin/env python3
"""
Wrapper para ejecutar SpotterSRS y enviar resultados al CRM
Diseñado para ejecución via cron
"""
import sys
import os
import json
import requests
from datetime import datetime

sys.path.insert(0, '/app')

from app.spotter.spotter_srs import (
    procesar_feed, 
    generar_json_crm,
    NivelDolor
)

CRM_API_URL = "http://172.17.0.1:8000/api/oportunidades/spotter-internal"
PLACSP_FEED_URL = "https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3.atom"

CERT_DIR = "/app/certs"
CLIENT_CERT = os.path.join(CERT_DIR, "client_cert.pem")
CLIENT_KEY = os.path.join(CERT_DIR, "client_key_nopass.pem")

LOG_DIR = "/app/logs"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"spotter_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def fetch_placsp_feed():
    log("Descargando feed Atom de PLACSP con certificado...")
    try:
        response = requests.get(
            PLACSP_FEED_URL,
            cert=(CLIENT_CERT, CLIENT_KEY),
            timeout=120
        )
        response.raise_for_status()
        log(f"Feed descargado: {len(response.text)} bytes")
        return response.text
    except Exception as e:
        log(f"ERROR descargando feed: {e}")
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
    log(f"Enviando {len(data['oportunidades'])} oportunidades al CRM...")
    try:
        response = requests.post(CRM_API_URL, json=data, headers={"Content-Type": "application/json"}, timeout=30)
        response.raise_for_status()
        result = response.json()
        log(f"Resultado: {result}")
        return result
    except Exception as e:
        log(f"ERROR enviando al CRM: {e}")
        return None

def main():
    log("=" * 60)
    log("SPOTTER SRS - Ejecucion Cron")
    log("=" * 60)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    xml_content = fetch_placsp_feed()
    if not xml_content:
        log("Abortando: no se pudo obtener el feed")
        sys.exit(1)
    
    log("Procesando feed (filtrando ADJ y RES)...")
    try:
        adjudicaciones = procesar_feed(xml_content)
        log(f"Detectadas {len(adjudicaciones)} oportunidades relevantes")
    except Exception as e:
        log(f"ERROR procesando feed: {e}")
        sys.exit(1)
    
    if not adjudicaciones:
        log("No se encontraron oportunidades relevantes")
        sys.exit(0)
    
    json_str = generar_json_crm(adjudicaciones)
    crm_data = transform_to_crm_format(json_str)
    result = send_to_crm(crm_data)
    
    if result:
        log(f"Importadas: {result.get('imported', 0)}, Duplicadas: {result.get('duplicates', 0)}")
    
    log("Ejecucion completada")
    log("=" * 60)

if __name__ == "__main__":
    main()
