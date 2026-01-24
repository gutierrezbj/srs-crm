"""Analizador de keywords."""
import re
from typing import Dict, List, Set

class KeywordAnalyzer:
    """Analiza coincidencias de keywords en texto."""
    
    def __init__(self, config: dict):
        self.config = config
        self.keyword_sets = self._build_keyword_sets()
    
    def _build_keyword_sets(self) -> Dict[str, Dict]:
        """Construir sets de keywords por nivel."""
        result = {}
        
        keywords_config = self.config.get("keywords", {})
        for nivel, data in keywords_config.items():
            peso = data.get("peso", 50)
            palabras = set(p.lower() for p in data.get("palabras", []))
            result[nivel] = {"peso": peso, "palabras": palabras}
        
        return result
    
    def analyze(self, texto: str) -> Dict:
        """Analizar texto y retornar resultado."""
        if not texto:
            return {"score": 0, "matches": [], "por_nivel": {}}
        
        texto_lower = texto.lower()
        all_matches = []
        por_nivel = {}
        weighted_score = 0
        total_weight = 0
        
        for nivel, data in self.keyword_sets.items():
            peso = data["peso"]
            palabras = data["palabras"]
            nivel_matches = []
            
            for palabra in palabras:
                if len(palabra) <= 4:
                    pattern = r'\b' + re.escape(palabra) + r'\b'
                    if re.search(pattern, texto_lower):
                        nivel_matches.append(palabra)
                else:
                    if palabra in texto_lower:
                        nivel_matches.append(palabra)
            
            if nivel_matches:
                por_nivel[nivel] = nivel_matches
                all_matches.extend(nivel_matches)
                
                nivel_score = min(len(nivel_matches) * 20, 100)
                weighted_score += nivel_score * (peso / 100)
                total_weight += (peso / 100)
        
        final_score = 0
        if total_weight > 0:
            final_score = int(weighted_score / total_weight)
        elif all_matches:
            final_score = min(len(all_matches) * 15, 100)
        
        return {
            "score": min(100, final_score),
            "matches": list(set(all_matches)),
            "por_nivel": por_nivel
        }
