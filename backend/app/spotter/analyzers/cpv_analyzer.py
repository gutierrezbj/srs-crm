"""Analizador de códigos CPV."""
from typing import Dict, List, Optional, Tuple

class CPVAnalyzer:
    """Analiza coincidencias de CPV contra configuración de sector."""
    
    def __init__(self, config: dict):
        self.config = config
        self.cpv_map = self._build_cpv_map()
        self.cpv_directo = config.get("cpv_directo")
    
    def _build_cpv_map(self) -> Dict[str, Tuple[str, int]]:
        """Construir mapa CPV -> (categoría, peso)."""
        cpv_map = {}
        
        cpvs_config = self.config.get("cpvs", {})
        for categoria, data in cpvs_config.items():
            peso_base = data.get("peso_base", 50)
            for cpv_item in data.get("codigos", []):
                codigo = cpv_item.get("codigo", "")
                cpv_map[codigo] = (categoria, peso_base)
        
        return cpv_map
    
    def analyze(self, cpv: str) -> Dict:
        """Analizar CPV y retornar resultado."""
        if not cpv:
            return {"score": 0, "matches": [], "categoria_principal": None}
        
        cpv_clean = cpv.strip()
        matches = []
        best_score = 0
        categoria_principal = None
        
        if self.cpv_directo:
            cpv_directo_codigo = self.cpv_directo.get("codigo", "")
            if cpv_clean.startswith(cpv_directo_codigo[:8]):
                best_score = self.cpv_directo.get("peso", 100)
                matches.append({
                    "cpv": cpv_clean,
                    "categoria": "cpv_directo",
                    "descripcion": self.cpv_directo.get("descripcion", ""),
                    "tipo_match": "directo"
                })
                categoria_principal = "cpv_directo"
        
        for cpv_config, (categoria, peso) in self.cpv_map.items():
            if cpv_clean.startswith(cpv_config[:min(len(cpv_config), 8)]):
                if peso > best_score:
                    best_score = peso
                    categoria_principal = categoria
                
                matches.append({
                    "cpv": cpv_clean,
                    "categoria": categoria,
                    "tipo_match": "prefijo"
                })
                break
            
            elif cpv_config[:4] == cpv_clean[:4]:
                partial_score = peso * 0.5
                if partial_score > best_score:
                    best_score = int(partial_score)
                    categoria_principal = categoria
                
                matches.append({
                    "cpv": cpv_clean,
                    "categoria": categoria,
                    "tipo_match": "parcial"
                })
        
        return {
            "score": min(100, best_score),
            "matches": matches,
            "categoria_principal": categoria_principal
        }
