"""Motor de scoring normalizado."""
from typing import Dict, Optional
from datetime import datetime, timezone

class ScoringEngine:
    """Calcula score normalizado 0-100."""
    
    def __init__(self, config: dict):
        self.config = config
        scoring_config = config.get("scoring", {})
        
        self.pesos = scoring_config.get("pesos", {
            "cpv": 0.35,
            "keywords": 0.35,
            "importe": 0.15,
            "urgencia": 0.15
        })
        
        self.umbrales = scoring_config.get("umbrales", {
            "oro": 85,
            "plata": 70,
            "bronce": 50
        })
        
        self.importe_optimo = scoring_config.get("importe_optimo", 200000)
    
    def calculate(
        self,
        cpv_score: int,
        keyword_score: int,
        importe: Optional[float],
        dias_restantes: Optional[int]
    ) -> Dict:
        """Calcular score total."""
        importe_score = self._calculate_importe_score(importe)
        urgencia_score = self._calculate_urgencia_score(dias_restantes)
        
        desglose = {
            "cpv": cpv_score,
            "keywords": keyword_score,
            "importe": importe_score,
            "urgencia": urgencia_score
        }
        
        total = int(
            cpv_score * self.pesos.get("cpv", 0.35) +
            keyword_score * self.pesos.get("keywords", 0.35) +
            importe_score * self.pesos.get("importe", 0.15) +
            urgencia_score * self.pesos.get("urgencia", 0.15)
        )
        
        nivel = self._determine_nivel(total)
        
        return {
            "total": min(100, total),
            "nivel": nivel,
            "desglose": desglose
        }
    
    def _calculate_importe_score(self, importe: Optional[float]) -> int:
        """Calcular score basado en importe."""
        if importe is None or importe <= 0:
            return 30
        
        ratio = importe / self.importe_optimo
        
        if ratio < 0.1:
            return 20
        elif ratio < 0.5:
            return 40 + int(ratio * 60)
        elif ratio <= 2:
            return 80 + int((1 - abs(1 - ratio)) * 20)
        elif ratio <= 5:
            return 70
        else:
            return 50
    
    def _calculate_urgencia_score(self, dias_restantes: Optional[int]) -> int:
        """Calcular score basado en urgencia."""
        if dias_restantes is None:
            return 50
        
        if dias_restantes <= 0:
            return 10
        elif dias_restantes <= 3:
            return 100
        elif dias_restantes <= 7:
            return 90
        elif dias_restantes <= 14:
            return 75
        elif dias_restantes <= 30:
            return 60
        else:
            return 40
    
    def _determine_nivel(self, total: int) -> str:
        """Determinar nivel según umbrales."""
        if total >= self.umbrales.get("oro", 85):
            return "oro"
        elif total >= self.umbrales.get("plata", 70):
            return "plata"
        elif total >= self.umbrales.get("bronce", 50):
            return "bronce"
        else:
            return "descarte"
