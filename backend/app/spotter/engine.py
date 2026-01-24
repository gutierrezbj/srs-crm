"""Motor principal SpotterEngine."""
import yaml
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone

from .feed_client import FeedClient
from .parsers.atom_parser import AtomParser
from .analyzers.cpv_analyzer import CPVAnalyzer
from .analyzers.keyword_analyzer import KeywordAnalyzer
from .analyzers.scoring import ScoringEngine

from app.services.oportunidades import (
    get_oportunidad_by_expediente,
    create_oportunidad,
    update_oportunidad
)

class SpotterEngine:
    """Motor unificado de detección de oportunidades."""
    
    def __init__(self, sector: str, tipo: str = "licitacion"):
        self.sector = sector
        self.tipo = tipo
        self.config = self._load_config(sector)
        
        self.feed_client = FeedClient()
        self.parser = AtomParser(tipo_filtro=tipo)
        self.cpv_analyzer = CPVAnalyzer(self.config)
        self.keyword_analyzer = KeywordAnalyzer(self.config)
        self.scoring_engine = ScoringEngine(self.config)
    
    def _load_config(self, sector: str) -> dict:
        """Cargar configuración YAML del sector."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "config", "sectors", f"{sector}.yaml"
        )
        
        if not os.path.exists(config_path):
            raise ValueError(f"Configuración no encontrada: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def ejecutar(self, limit: int = None) -> Dict:
        """Ejecutar detección completa."""
        result = {
            "sector": self.sector,
            "tipo": self.tipo,
            "ejecutado_at": datetime.now(timezone.utc).isoformat(),
            "total_procesadas": 0,
            "nuevas": 0,
            "actualizadas": 0,
            "descartadas": 0,
            "errores": 0,
            "por_nivel": {"oro": 0, "plata": 0, "bronce": 0, "descarte": 0}
        }
        
        feeds = self.config.get("feeds", {})
        feed_url = feeds.get(self.tipo)
        
        if not feed_url:
            print(f"No hay feed configurado para {self.sector}/{self.tipo}")
            return result
        
        print(f"Descargando feed: {feed_url}")
        xml_content = await self.feed_client.fetch_feed(feed_url)
        
        if not xml_content:
            print("Error descargando feed")
            result["errores"] = 1
            return result
        
        entries = self.parser.parse(xml_content)
        print(f"Entries parseadas: {len(entries)}")
        
        if limit:
            entries = entries[:limit]
        
        for entry in entries:
            try:
                procesado = self._procesar_entry(entry)
                result["total_procesadas"] += 1
                
                if procesado:
                    nivel = procesado.get("scoring", {}).get("nivel", "descarte")
                    result["por_nivel"][nivel] = result["por_nivel"].get(nivel, 0) + 1
                    
                    if procesado.get("es_nueva"):
                        result["nuevas"] += 1
                    else:
                        result["actualizadas"] += 1
                else:
                    result["descartadas"] += 1
                    
            except Exception as e:
                print(f"Error procesando {entry.get('expediente')}: {e}")
                result["errores"] += 1
        
        return result
    
    def _procesar_entry(self, entry: dict) -> Optional[Dict]:
        """Procesar una entry individual."""
        expediente = entry.get("expediente")
        if not expediente:
            return None
        
        texto_analisis = " ".join(filter(None, [
            entry.get("titulo", ""),
            entry.get("descripcion", ""),
            entry.get("cpv_descripcion", "")
        ]))
        
        cpv_result = self.cpv_analyzer.analyze(entry.get("cpv"))
        keyword_result = self.keyword_analyzer.analyze(texto_analisis)
        
        if cpv_result["score"] < 30 and keyword_result["score"] < 30:
            return None
        
        dias_restantes = None
        fechas = entry.get("fechas", {})
        fecha_limite = fechas.get("limite")
        if fecha_limite:
            if isinstance(fecha_limite, str):
                fecha_limite = datetime.fromisoformat(fecha_limite.replace("Z", "+00:00"))
            delta = fecha_limite - datetime.now(timezone.utc)
            dias_restantes = max(0, delta.days)
        
        scoring = self.scoring_engine.calculate(
            cpv_score=cpv_result["score"],
            keyword_score=keyword_result["score"],
            importe=entry.get("importe"),
            dias_restantes=dias_restantes
        )
        
        if scoring["total"] < 40:
            return None
        
        oportunidad_data = {
            "expediente": expediente,
            "tipo": self.tipo,
            "sector": self.sector,
            "estado_placsp": entry.get("estado_placsp"),
            "titulo": entry.get("titulo"),
            "descripcion": entry.get("descripcion"),
            "cpv": entry.get("cpv"),
            "cpv_descripcion": entry.get("cpv_descripcion"),
            "importe": entry.get("importe"),
            "organo_contratacion": entry.get("organo_contratacion"),
            "url_licitacion": entry.get("url_licitacion"),
            "url_pliego": entry.get("url_pliego"),
            "fechas": fechas,
            "dias_restantes": dias_restantes,
            "adjudicatario": entry.get("adjudicatario"),
            "scoring": scoring,
            "analisis": {
                "cpv_matches": cpv_result.get("matches", []),
                "keywords": keyword_result.get("matches", []),
                "categoria": cpv_result.get("categoria_principal")
            },
            "estado": "nueva"
        }
        
        existing = get_oportunidad_by_expediente(expediente)
        
        if existing:
            update_data = {
                "scoring": scoring,
                "analisis": oportunidad_data["analisis"],
                "dias_restantes": dias_restantes,
                "estado_placsp": entry.get("estado_placsp")
            }
            result = update_oportunidad(expediente, update_data, "spotter")
            result["es_nueva"] = False
        else:
            result = create_oportunidad(oportunidad_data)
            result["es_nueva"] = True
        
        return result


class ConfigLoader:
    """Utilidad para cargar configuraciones."""
    
    @staticmethod
    def get_active_sectors() -> List[dict]:
        """Obtener todos los sectores activos."""
        config_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "config", "sectors"
        )
        
        sectors = []
        for filename in os.listdir(config_dir):
            if filename.endswith(".yaml"):
                filepath = os.path.join(config_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config.get("activo", True):
                        sectors.append(config)
        
        return sectors
    
    @staticmethod
    def get_sector_config(sector: str) -> Optional[dict]:
        """Obtener configuración de un sector específico."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "config", "sectors", f"{sector}.yaml"
        )
        
        if not os.path.exists(config_path):
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
