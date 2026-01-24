"""Parser para feeds Atom de PLACSP."""
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime
import re

# Namespaces PLACSP
NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'cbc-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-1',
    'cac-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-1',
    'cac': 'urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2'
}

class AtomParser:
    """Parser de feeds Atom PLACSP."""
    
    def __init__(self, tipo_filtro: str = None):
        self.tipo_filtro = tipo_filtro
    
    def parse(self, xml_content: str) -> List[Dict]:
        """Parsear feed Atom y extraer entries."""
        if not xml_content:
            return []
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"Error parseando XML: {e}")
            return []
        
        entries = root.findall('atom:entry', NAMESPACES)
        results = []
        
        for entry in entries:
            parsed = self._parse_entry(entry)
            if parsed:
                if self.tipo_filtro:
                    if self.tipo_filtro == "adjudicacion" and parsed.get("estado_placsp") in ["ADJ", "RES"]:
                        results.append(parsed)
                    elif self.tipo_filtro == "licitacion" and parsed.get("estado_placsp") in ["PUB", "EV", "PRE"]:
                        results.append(parsed)
                else:
                    results.append(parsed)
        
        return results
    
    def _parse_entry(self, entry: ET.Element) -> Optional[Dict]:
        """Parsear una entry del feed."""
        try:
            id_elem = entry.find('atom:id', NAMESPACES)
            if id_elem is None or not id_elem.text:
                return None
            
            expediente = self._extract_expediente(id_elem.text)
            
            title = entry.find('atom:title', NAMESPACES)
            titulo = title.text.strip() if title is not None and title.text else "Sin título"
            
            summary = entry.find('atom:summary', NAMESPACES)
            descripcion = summary.text.strip() if summary is not None and summary.text else None
            
            url_licitacion = None
            url_pliego = None
            for link in entry.findall('atom:link', NAMESPACES):
                rel = link.get('rel', '')
                href = link.get('href', '')
                if rel == 'alternate':
                    url_licitacion = href
                elif 'pliego' in rel.lower() or 'documento' in rel.lower():
                    url_pliego = href
            
            updated = entry.find('atom:updated', NAMESPACES)
            fecha_actualizacion = self._parse_date(updated.text) if updated is not None and updated.text else None
            
            contract_folder = entry.find('.//cac-place-ext:ContractFolderStatus', NAMESPACES)
            
            cpv = None
            cpv_descripcion = None
            importe = None
            organo = None
            estado_placsp = None
            fecha_limite = None
            
            if contract_folder is not None:
                cpv_elem = contract_folder.find('.//cbc:ItemClassificationCode', NAMESPACES)
                if cpv_elem is not None and cpv_elem.text:
                    cpv = cpv_elem.text.strip()
                
                cpv_desc = contract_folder.find('.//cbc:Description', NAMESPACES)
                if cpv_desc is not None and cpv_desc.text:
                    cpv_descripcion = cpv_desc.text.strip()
                
                amount = contract_folder.find('.//cbc:TotalAmount', NAMESPACES)
                if amount is not None and amount.text:
                    try:
                        importe = float(amount.text.replace(',', '.'))
                    except ValueError:
                        pass
                
                party_name = contract_folder.find('.//cac:Party/cac:PartyName/cbc:Name', NAMESPACES)
                if party_name is not None and party_name.text:
                    organo = party_name.text.strip()
                
                status = contract_folder.find('.//cbc-place-ext:ContractFolderStatusCode', NAMESPACES)
                if status is not None and status.text:
                    estado_placsp = status.text.strip()
                
                end_date = contract_folder.find('.//cac:TenderSubmissionDeadlinePeriod/cbc:EndDate', NAMESPACES)
                if end_date is not None and end_date.text:
                    fecha_limite = self._parse_date(end_date.text)
            
            adjudicatario = None
            award = entry.find('.//cac:TenderResult', NAMESPACES)
            if award is not None:
                winner_name = award.find('.//cac:WinningParty/cac:PartyName/cbc:Name', NAMESPACES)
                winner_nif = award.find('.//cac:WinningParty/cac:PartyIdentification/cbc:ID', NAMESPACES)
                
                if winner_name is not None and winner_name.text:
                    adjudicatario = {
                        "nombre": winner_name.text.strip(),
                        "nif": winner_nif.text.strip() if winner_nif is not None and winner_nif.text else None
                    }
            
            return {
                "expediente": expediente,
                "titulo": titulo,
                "descripcion": descripcion,
                "cpv": cpv,
                "cpv_descripcion": cpv_descripcion,
                "importe": importe,
                "organo_contratacion": organo,
                "estado_placsp": estado_placsp,
                "url_licitacion": url_licitacion,
                "url_pliego": url_pliego,
                "fechas": {
                    "limite": fecha_limite,
                    "actualizacion": fecha_actualizacion,
                    "deteccion": datetime.utcnow()
                },
                "adjudicatario": adjudicatario
            }
            
        except Exception as e:
            print(f"Error parseando entry: {e}")
            return None
    
    def _extract_expediente(self, id_text: str) -> str:
        """Extraer número de expediente del ID."""
        match = re.search(r'idDoc=([^&]+)', id_text)
        if match:
            return match.group(1)
        return id_text.split('/')[-1] if '/' in id_text else id_text
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parsear fecha en varios formatos."""
        if not date_str:
            return None
        
        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
