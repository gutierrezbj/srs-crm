#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║             SpotterSRS-Licitaciones                               ║
║     Análisis de Licitaciones ABIERTAS para Servicios de Drones   ║
╚═══════════════════════════════════════════════════════════════════╝

Servicio para analizar licitaciones de PLACSP y detectar oportunidades
relacionadas con servicios de drones usando:
- CPV matching (nivel 1 directo y nivel 2 indirecto)
- Búsqueda de keywords en título y descripción
- Cálculo de scoring basado en pesos configurados
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class LicitacionInput(BaseModel):
    """Datos de entrada de una licitación para analizar"""
    expediente: str
    objeto: str  # Título/objeto del contrato
    cpv: str  # Código CPV principal
    descripcion: Optional[str] = None  # Descripción adicional o PPT
    presupuesto: Optional[float] = None
    plazo_presentacion: Optional[datetime] = None
    organo_contratacion: Optional[str] = None
    url: Optional[str] = None


class CPVMatch(BaseModel):
    """Resultado de matching de CPV"""
    nivel: int  # 1 = directo, 2 = indirecto, 0 = sin match
    categoria: Optional[str] = None
    nombre_categoria: Optional[str] = None
    nombre_cpv: Optional[str] = None
    puntos: int = 0


class ScoringDetails(BaseModel):
    """Detalles del cálculo de scoring"""
    puntos_cpv: int = 0
    puntos_keywords_titulo: int = 0
    puntos_keywords_descripcion: int = 0
    puntos_presupuesto: int = 0
    puntos_plazo: int = 0
    bonus_keywords_multiples: int = 0
    total: int = 0


class LicitacionAnalysisResult(BaseModel):
    """Resultado del análisis de una licitación"""
    expediente: str
    es_relevante: bool
    score: int = Field(ge=0, le=100)
    cpv_match: CPVMatch
    keywords_encontradas: List[str] = []
    keywords_en_titulo: List[str] = []
    keywords_en_descripcion: List[str] = []
    categoria_principal: Optional[str] = None
    detalles_scoring: ScoringDetails
    recomendacion: str = ""


# ============================================================================
# ANALIZADOR DE LICITACIONES
# ============================================================================

class LicitacionAnalyzer:
    """
    Analizador de licitaciones para detectar oportunidades de servicios drone.
    Usa el archivo cpv_drone_mapping.json para CPVs, keywords y scoring.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el analizador cargando la configuración.
        
        Args:
            config_path: Ruta al archivo de configuración JSON.
                        Si no se especifica, busca en backend/config/
        """
        if config_path is None:
            # Buscar en la ruta por defecto
            base_path = Path(__file__).parent.parent
            config_path = base_path / "config" / "cpv_drone_mapping.json"
        
        self.config_path = Path(config_path)
        self._load_config()
        self._build_cpv_index()
        self._build_keyword_sets()
    
    def _load_config(self):
        """Carga la configuración desde el archivo JSON"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.scoring_weights = self.config.get("scoring_weights", {})
        self.nivel_1 = self.config.get("nivel_1_cpv_directos", {})
        self.nivel_2 = self.config.get("nivel_2_cpv_indirectos", {})
        self.keywords_universales = self.config.get("keywords_universales", {})
        self.exclusiones = self.config.get("exclusiones", {}).get("cpv_codes", [])
    
    def _build_cpv_index(self):
        """Construye un índice de CPVs para búsqueda rápida"""
        self.cpv_index: Dict[str, Dict[str, Any]] = {}
        
        # Indexar nivel 1 (directos)
        for cat_key, cat_data in self.nivel_1.get("categories", {}).items():
            for cpv_item in cat_data.get("cpv_codes", []):
                code = cpv_item["code"]
                self.cpv_index[code] = {
                    "nivel": 1,
                    "categoria": cat_key,
                    "nombre_categoria": cat_data.get("name", ""),
                    "nombre_cpv": cpv_item.get("name", ""),
                    "keywords": cat_data.get("keywords", [])
                }
        
        # Indexar nivel 2 (indirectos)
        for cat_key, cat_data in self.nivel_2.get("categories", {}).items():
            for cpv_item in cat_data.get("cpv_codes", []):
                code = cpv_item["code"]
                # Solo agregar si no está ya en nivel 1
                if code not in self.cpv_index:
                    self.cpv_index[code] = {
                        "nivel": 2,
                        "categoria": cat_key,
                        "nombre_categoria": cat_data.get("name", ""),
                        "nombre_cpv": cpv_item.get("name", ""),
                        "keywords": cat_data.get("keywords_ppt", []),
                        "probability": cat_data.get("probability", "media")
                    }
    
    def _build_keyword_sets(self):
        """Construye conjuntos de keywords para búsqueda"""
        self.all_keywords: set = set()
        self.keywords_by_category: Dict[str, List[str]] = {}
        
        # Keywords de nivel 1
        for cat_key, cat_data in self.nivel_1.get("categories", {}).items():
            keywords = cat_data.get("keywords", [])
            self.keywords_by_category[cat_key] = keywords
            self.all_keywords.update(kw.lower() for kw in keywords)
        
        # Keywords de nivel 2
        for cat_key, cat_data in self.nivel_2.get("categories", {}).items():
            keywords = cat_data.get("keywords_ppt", [])
            if cat_key not in self.keywords_by_category:
                self.keywords_by_category[cat_key] = []
            self.keywords_by_category[cat_key].extend(keywords)
            self.all_keywords.update(kw.lower() for kw in keywords)
        
        # Keywords universales
        for key in ["keywords_tecnicos", "keywords_regulatorios", "keywords_equipamiento"]:
            keywords = self.keywords_universales.get(key, [])
            self.all_keywords.update(kw.lower() for kw in keywords)
    
    def _match_cpv(self, cpv: str) -> CPVMatch:
        """
        Busca el CPV en el índice y retorna información de matching.
        También intenta match por prefijo de CPV.
        """
        # Normalizar CPV (quitar espacios)
        cpv = cpv.strip()
        
        # Verificar exclusiones
        if cpv in self.exclusiones:
            return CPVMatch(nivel=0, puntos=0)
        
        # Match exacto
        if cpv in self.cpv_index:
            info = self.cpv_index[cpv]
            nivel = info["nivel"]
            puntos = self.scoring_weights.get("cpv_nivel_1", 40) if nivel == 1 else self.scoring_weights.get("cpv_nivel_2", 20)
            return CPVMatch(
                nivel=nivel,
                categoria=info["categoria"],
                nombre_categoria=info["nombre_categoria"],
                nombre_cpv=info["nombre_cpv"],
                puntos=puntos
            )
        
        # Intentar match por prefijo (primeros 5 dígitos)
        # Formato CPV: XXXXXXXX-X (8 dígitos + dígito de control)
        cpv_prefix = cpv[:5] if len(cpv) >= 5 else cpv
        
        for code, info in self.cpv_index.items():
            if code.startswith(cpv_prefix):
                nivel = info["nivel"]
                # Dar menos puntos por match parcial
                base_puntos = self.scoring_weights.get("cpv_nivel_1", 40) if nivel == 1 else self.scoring_weights.get("cpv_nivel_2", 20)
                puntos = int(base_puntos * 0.7)  # 70% por match parcial
                return CPVMatch(
                    nivel=nivel,
                    categoria=info["categoria"],
                    nombre_categoria=info["nombre_categoria"],
                    nombre_cpv=f"(Parcial) {info['nombre_cpv']}",
                    puntos=puntos
                )
        
        return CPVMatch(nivel=0, puntos=0)
    
    def _buscar_keywords(self, texto: str) -> List[str]:
        """
        Busca keywords relevantes en un texto.
        Retorna lista de keywords encontradas.
        """
        if not texto:
            return []
        
        texto_lower = texto.lower()
        encontradas = []
        
        for keyword in self.all_keywords:
            # Usar regex para word boundary matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, texto_lower, re.IGNORECASE):
                encontradas.append(keyword)
        
        return list(set(encontradas))
    
    def _calcular_puntos_presupuesto(self, presupuesto: Optional[float]) -> int:
        """Calcula puntos bonus por presupuesto"""
        if presupuesto is None:
            return 0
        
        rangos = self.scoring_weights.get("presupuesto", {})
        
        if presupuesto < 10000:
            return rangos.get("menos_10k", 5)
        elif presupuesto < 50000:
            return rangos.get("10k_50k", 15)
        elif presupuesto < 100000:
            return rangos.get("50k_100k", 25)
        elif presupuesto < 500000:
            return rangos.get("100k_500k", 35)
        else:
            return rangos.get("mas_500k", 40)
    
    def _calcular_puntos_plazo(self, plazo: Optional[datetime]) -> int:
        """Calcula ajuste de puntos por plazo de presentación"""
        if plazo is None:
            return 0
        
        # Calcular días hasta el plazo
        ahora = datetime.now(timezone.utc)
        if plazo.tzinfo is None:
            plazo = plazo.replace(tzinfo=timezone.utc)
        
        dias = (plazo - ahora).days
        
        rangos = self.scoring_weights.get("plazo_presentacion", {})
        
        if dias < 7:
            return rangos.get("menos_7_dias", -10)
        elif dias <= 15:
            return rangos.get("7_15_dias", 5)
        elif dias <= 30:
            return rangos.get("15_30_dias", 10)
        else:
            return rangos.get("mas_30_dias", 0)
    
    def _calcular_bonus_keywords(self, num_keywords: int) -> int:
        """Calcula bonus por múltiples keywords encontradas"""
        bonus_config = self.scoring_weights.get("bonus_keywords_multiples", {})
        
        if num_keywords >= 4:
            return bonus_config.get("4_o_mas_keywords", 15)
        elif num_keywords >= 3:
            return bonus_config.get("3_keywords", 10)
        elif num_keywords >= 2:
            return bonus_config.get("2_keywords", 5)
        return 0
    
    def _generar_recomendacion(self, score: int, cpv_match: CPVMatch, keywords: List[str]) -> str:
        """Genera texto de recomendación basado en el análisis"""
        if score >= 80:
            return "🔥 ALTA PRIORIDAD - Revisar inmediatamente, alta probabilidad de match"
        elif score >= 60:
            return "⭐ PRIORIDAD MEDIA - Revisar PPT para confirmar requisitos de drone"
        elif score >= 40:
            return "📋 REVISAR - Posible oportunidad, verificar detalles técnicos"
        elif score >= 20:
            return "🔎 BAJA PRIORIDAD - Match parcial, revisar si hay tiempo"
        else:
            return "❌ NO RELEVANTE - No cumple criterios mínimos"
    
    def analizar(self, licitacion: LicitacionInput) -> LicitacionAnalysisResult:
        """
        Analiza una licitación y calcula su relevancia para servicios drone.
        
        Args:
            licitacion: Datos de la licitación a analizar
            
        Returns:
            LicitacionAnalysisResult con el análisis completo
        """
        # 1. Match de CPV
        cpv_match = self._match_cpv(licitacion.cpv)
        
        # 2. Búsqueda de keywords
        keywords_titulo = self._buscar_keywords(licitacion.objeto)
        keywords_descripcion = self._buscar_keywords(licitacion.descripcion or "")
        todas_keywords = list(set(keywords_titulo + keywords_descripcion))
        
        # 3. Calcular scoring
        scoring = ScoringDetails()
        
        # Puntos por CPV
        scoring.puntos_cpv = cpv_match.puntos
        
        # Puntos por keywords en título (peso alto)
        if keywords_titulo:
            scoring.puntos_keywords_titulo = min(
                len(keywords_titulo) * self.scoring_weights.get("keyword_titulo", 15),
                30  # Cap máximo
            )
        
        # Puntos por keywords en descripción
        if keywords_descripcion:
            scoring.puntos_keywords_descripcion = min(
                len(keywords_descripcion) * self.scoring_weights.get("keyword_ppt", 25) // 3,
                25  # Cap máximo
            )
        
        # Puntos por presupuesto
        scoring.puntos_presupuesto = self._calcular_puntos_presupuesto(licitacion.presupuesto)
        
        # Ajuste por plazo
        scoring.puntos_plazo = self._calcular_puntos_plazo(licitacion.plazo_presentacion)
        
        # Bonus por múltiples keywords
        scoring.bonus_keywords_multiples = self._calcular_bonus_keywords(len(todas_keywords))
        
        # Total (máximo 100)
        scoring.total = min(100, max(0,
            scoring.puntos_cpv +
            scoring.puntos_keywords_titulo +
            scoring.puntos_keywords_descripcion +
            scoring.puntos_presupuesto +
            scoring.puntos_plazo +
            scoring.bonus_keywords_multiples
        ))
        
        # 4. Determinar relevancia (umbral: 20 puntos)
        es_relevante = scoring.total >= 20
        
        # 5. Generar recomendación
        recomendacion = self._generar_recomendacion(scoring.total, cpv_match, todas_keywords)
        
        return LicitacionAnalysisResult(
            expediente=licitacion.expediente,
            es_relevante=es_relevante,
            score=scoring.total,
            cpv_match=cpv_match,
            keywords_encontradas=todas_keywords,
            keywords_en_titulo=keywords_titulo,
            keywords_en_descripcion=keywords_descripcion,
            categoria_principal=cpv_match.nombre_categoria,
            detalles_scoring=scoring,
            recomendacion=recomendacion
        )
    
    def analizar_batch(self, licitaciones: List[LicitacionInput]) -> List[LicitacionAnalysisResult]:
        """
        Analiza múltiples licitaciones y retorna resultados ordenados por score.
        
        Args:
            licitaciones: Lista de licitaciones a analizar
            
        Returns:
            Lista de resultados ordenados por score (mayor primero)
        """
        resultados = [self.analizar(lic) for lic in licitaciones]
        
        # Ordenar por score descendente
        resultados.sort(key=lambda x: x.score, reverse=True)
        
        return resultados
    
    def get_estadisticas(self, resultados: List[LicitacionAnalysisResult]) -> Dict[str, Any]:
        """
        Genera estadísticas de un batch de análisis.
        
        Args:
            resultados: Lista de resultados de análisis
            
        Returns:
            Diccionario con estadísticas
        """
        if not resultados:
            return {"total": 0}
        
        relevantes = [r for r in resultados if r.es_relevante]
        
        return {
            "total": len(resultados),
            "relevantes": len(relevantes),
            "no_relevantes": len(resultados) - len(relevantes),
            "score_promedio": sum(r.score for r in resultados) / len(resultados),
            "score_max": max(r.score for r in resultados),
            "alta_prioridad": len([r for r in resultados if r.score >= 80]),
            "media_prioridad": len([r for r in resultados if 60 <= r.score < 80]),
            "baja_prioridad": len([r for r in resultados if 20 <= r.score < 60]),
            "categorias": list(set(r.categoria_principal for r in relevantes if r.categoria_principal))
        }
