#!/usr/bin/env python3
"""
Motor de analisis de licitaciones para deteccion de oportunidades de drones.
Utiliza el mapeo CPV de config/cpv_drone_mapping.json para scoring.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


# Cargar configuracion de CPV
CONFIG_PATH = Path(__file__).parent.parent / "config" / "cpv_drone_mapping.json"


def load_cpv_config() -> Dict[str, Any]:
    """Carga la configuracion de CPV desde el archivo JSON"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Advertencia: No se encontro {CONFIG_PATH}, usando config vacia")
        return {"categorias": {}, "keywords_genericas_drones": {}, "scoring": {}}


@dataclass
class LicitacionInput:
    """Datos de entrada para analizar una licitacion"""
    titulo: str
    descripcion: Optional[str] = None
    cpv: Optional[str] = None
    presupuesto: Optional[float] = None
    organo_contratacion: Optional[str] = None


@dataclass
class LicitacionAnalysisResult:
    """Resultado del analisis de una licitacion"""
    score: int  # 0-100
    relevante: bool
    cpv_matches: List[Dict[str, Any]] = field(default_factory=list)
    keywords_detectados: List[str] = field(default_factory=list)
    categoria_principal: Optional[str] = None
    recomendacion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "relevante": self.relevante,
            "cpv_matches": self.cpv_matches,
            "keywords_detectados": self.keywords_detectados,
            "categoria_principal": self.categoria_principal,
            "recomendacion": self.recomendacion
        }


class LicitacionAnalyzer:
    """
    Analizador de licitaciones para detectar oportunidades de drones.
    Calcula un score de relevancia basado en CPV y keywords.
    """

    def __init__(self):
        self.config = load_cpv_config()
        self.categorias = self.config.get("categorias", {})
        self.keywords_genericas = self.config.get("keywords_genericas_drones", {})
        self.scoring_config = self.config.get("scoring", {
            "cpv_directo_drones": 100,
            "cpv_categoria_primaria": 80,
            "cpv_categoria_secundaria": 60,
            "keyword_alta_prioridad": 50,
            "keyword_media_prioridad": 30,
            "keyword_contexto": 10,
            "multiplicador_presupuesto_alto": 1.2,
            "umbral_presupuesto_alto": 50000
        })

        # Construir indice de CPV para busqueda rapida
        self._build_cpv_index()

        # Compilar keywords para busqueda
        self._compile_keywords()

    def _build_cpv_index(self):
        """Construye un indice de CPV -> categoria para busqueda rapida"""
        self.cpv_index = {}

        for cat_key, cat_data in self.categorias.items():
            cpvs = cat_data.get("cpvs", {})
            peso_base = cat_data.get("peso_base", 50)
            nombre = cat_data.get("nombre", cat_key)

            for cpv_code, cpv_desc in cpvs.items():
                self.cpv_index[cpv_code] = {
                    "categoria": cat_key,
                    "categoria_nombre": nombre,
                    "descripcion": cpv_desc,
                    "peso_base": peso_base
                }

    def _compile_keywords(self):
        """Compila las keywords en listas para busqueda"""
        self.keywords_alta = []
        self.keywords_media = []
        self.keywords_contexto = []
        self.keywords_por_categoria = {}

        # Keywords genericas
        for kw in self.keywords_genericas.get("alta_prioridad", []):
            self.keywords_alta.append(kw.lower())

        for kw in self.keywords_genericas.get("media_prioridad", []):
            self.keywords_media.append(kw.lower())

        for kw in self.keywords_genericas.get("contexto_adicional", []):
            self.keywords_contexto.append(kw.lower())

        # Keywords por categoria
        for cat_key, cat_data in self.categorias.items():
            self.keywords_por_categoria[cat_key] = [
                kw.lower() for kw in cat_data.get("keywords", [])
            ]

    def _match_cpv(self, cpv: str) -> List[Dict[str, Any]]:
        """Busca coincidencias de CPV en el indice"""
        if not cpv:
            return []

        matches = []
        cpv_clean = cpv.replace("-", "").replace(" ", "")[:8]

        # Busqueda exacta
        if cpv_clean in self.cpv_index:
            match = self.cpv_index[cpv_clean].copy()
            match["cpv"] = cpv_clean
            match["tipo_match"] = "exacto"
            matches.append(match)
            return matches

        # Busqueda por prefijo (grupos de CPV)
        for length in [5, 4, 3, 2]:
            prefix = cpv_clean[:length]
            for cpv_code, data in self.cpv_index.items():
                if cpv_code.startswith(prefix) and data not in [m for m in matches]:
                    match = data.copy()
                    match["cpv"] = cpv_code
                    match["tipo_match"] = f"prefijo_{length}"
                    matches.append(match)
                    break
            if matches:
                break

        return matches

    def _find_keywords(self, texto: str) -> Dict[str, List[str]]:
        """Busca keywords en el texto"""
        if not texto:
            return {"alta": [], "media": [], "contexto": [], "categoria": []}

        texto_lower = texto.lower()
        found = {
            "alta": [],
            "media": [],
            "contexto": [],
            "categoria": []
        }

        # Keywords genericas
        for kw in self.keywords_alta:
            if kw in texto_lower:
                found["alta"].append(kw)

        for kw in self.keywords_media:
            if kw in texto_lower:
                found["media"].append(kw)

        for kw in self.keywords_contexto:
            if kw in texto_lower:
                found["contexto"].append(kw)

        # Keywords por categoria
        for cat_key, keywords in self.keywords_por_categoria.items():
            for kw in keywords:
                if kw in texto_lower and kw not in found["categoria"]:
                    found["categoria"].append(kw)

        return found

    def _calcular_score(
        self,
        cpv_matches: List[Dict[str, Any]],
        keywords_found: Dict[str, List[str]],
        presupuesto: Optional[float]
    ) -> int:
        """Calcula el score de relevancia (0-100)"""
        score = 0

        # Score por CPV
        if cpv_matches:
            best_match = max(cpv_matches, key=lambda x: x.get("peso_base", 0))
            if best_match.get("tipo_match") == "exacto":
                score += self.scoring_config.get("cpv_categoria_primaria", 80)
            else:
                score += self.scoring_config.get("cpv_categoria_secundaria", 60)

        # Score por keywords
        n_alta = len(keywords_found.get("alta", []))
        n_media = len(keywords_found.get("media", []))
        n_contexto = len(keywords_found.get("contexto", []))
        n_categoria = len(keywords_found.get("categoria", []))

        # Keywords de alta prioridad dan mas puntos
        score += min(n_alta * 15, 45)  # Max 45 puntos por keywords de alta
        score += min(n_media * 8, 24)   # Max 24 puntos por keywords de media
        score += min(n_contexto * 3, 9) # Max 9 puntos por contexto
        score += min(n_categoria * 5, 15) # Max 15 puntos por categoria

        # Bonus por presupuesto alto
        umbral = self.scoring_config.get("umbral_presupuesto_alto", 50000)
        if presupuesto and presupuesto > umbral:
            multiplicador = self.scoring_config.get("multiplicador_presupuesto_alto", 1.2)
            score = int(score * multiplicador)

        # Limitar a 100
        return min(100, score)

    def _determinar_categoria_principal(
        self,
        cpv_matches: List[Dict[str, Any]],
        keywords_found: Dict[str, List[str]]
    ) -> Optional[str]:
        """Determina la categoria principal de la licitacion"""
        # Prioridad a CPV si hay match
        if cpv_matches:
            best = max(cpv_matches, key=lambda x: x.get("peso_base", 0))
            return best.get("categoria_nombre")

        # Si hay keywords de categoria, buscar la mas frecuente
        if keywords_found.get("categoria"):
            # Contar en que categoria aparecen mas
            cat_counts = {}
            for kw in keywords_found["categoria"]:
                for cat_key, keywords in self.keywords_por_categoria.items():
                    if kw in keywords:
                        cat_name = self.categorias.get(cat_key, {}).get("nombre", cat_key)
                        cat_counts[cat_name] = cat_counts.get(cat_name, 0) + 1

            if cat_counts:
                return max(cat_counts, key=cat_counts.get)

        # Keywords genericas de drones
        if keywords_found.get("alta"):
            return "Servicios con Drones"

        return None

    def _generar_recomendacion(self, score: int, categoria: Optional[str]) -> str:
        """Genera una recomendacion basada en el score"""
        if score >= 80:
            return f"Muy relevante para servicios de drones{' - ' + categoria if categoria else ''}. Revisar urgente."
        elif score >= 60:
            return f"Relevante{' para ' + categoria if categoria else ''}. Revisar el pliego tecnico."
        elif score >= 40:
            return f"Potencialmente relevante. Verificar alcance en pliego."
        elif score >= 20:
            return "Baja relevancia. Solo revisar si hay capacidad."
        else:
            return "No relevante para servicios de drones."

    def analizar(self, licitacion: LicitacionInput) -> LicitacionAnalysisResult:
        """
        Analiza una licitacion y retorna el resultado con score de relevancia.

        Args:
            licitacion: Datos de la licitacion a analizar

        Returns:
            LicitacionAnalysisResult con score, relevancia y detalles
        """
        # Combinar titulo y descripcion para analisis
        texto_completo = licitacion.titulo or ""
        if licitacion.descripcion:
            texto_completo += " " + licitacion.descripcion
        if licitacion.organo_contratacion:
            texto_completo += " " + licitacion.organo_contratacion

        # Buscar coincidencias de CPV
        cpv_matches = self._match_cpv(licitacion.cpv)

        # Buscar keywords
        keywords_found = self._find_keywords(texto_completo)

        # Calcular score
        score = self._calcular_score(
            cpv_matches,
            keywords_found,
            licitacion.presupuesto
        )

        # Determinar categoria principal
        categoria = self._determinar_categoria_principal(cpv_matches, keywords_found)

        # Aplanar keywords encontrados
        all_keywords = (
            keywords_found.get("alta", []) +
            keywords_found.get("media", []) +
            keywords_found.get("contexto", []) +
            keywords_found.get("categoria", [])
        )
        all_keywords = list(set(all_keywords))  # Eliminar duplicados

        # Generar recomendacion
        recomendacion = self._generar_recomendacion(score, categoria)

        # Determinar si es relevante (umbral: 30)
        relevante = score >= 30 or len(cpv_matches) > 0

        return LicitacionAnalysisResult(
            score=score,
            relevante=relevante,
            cpv_matches=cpv_matches,
            keywords_detectados=all_keywords,
            categoria_principal=categoria,
            recomendacion=recomendacion
        )

    def analizar_batch(self, licitaciones: List[LicitacionInput]) -> List[LicitacionAnalysisResult]:
        """
        Analiza un lote de licitaciones.

        Args:
            licitaciones: Lista de licitaciones a analizar

        Returns:
            Lista de resultados de analisis
        """
        return [self.analizar(lic) for lic in licitaciones]

    def es_cpv_drones_directo(self, cpv: str) -> bool:
        """
        Verifica si un CPV es directamente relacionado con drones.
        CPV 34711200 = Aeronaves no tripuladas
        """
        if not cpv:
            return False
        cpv_clean = cpv.replace("-", "").replace(" ", "")[:8]
        return cpv_clean.startswith("34711200")


# Instancia global del analizador
_analyzer_instance = None


def get_analyzer() -> LicitacionAnalyzer:
    """Retorna la instancia singleton del analizador"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = LicitacionAnalyzer()
    return _analyzer_instance


# Para pruebas directas
if __name__ == "__main__":
    analyzer = LicitacionAnalyzer()

    # Ejemplo de licitacion
    test_lic = LicitacionInput(
        titulo="Servicio de inspeccion con drones de lineas electricas de alta tension",
        descripcion="Inspeccion termografica y visual de torres de alta tension mediante RPAS",
        cpv="71631400",
        presupuesto=75000,
        organo_contratacion="Iberdrola Distribucion"
    )

    resultado = analyzer.analizar(test_lic)
    print(f"Score: {resultado.score}")
    print(f"Relevante: {resultado.relevante}")
    print(f"Categoria: {resultado.categoria_principal}")
    print(f"Keywords: {resultado.keywords_detectados}")
    print(f"CPV Matches: {resultado.cpv_matches}")
    print(f"Recomendacion: {resultado.recomendacion}")
