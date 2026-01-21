#!/usr/bin/env python3
"""
Tests para SpotterSRS-Licitaciones
Verifica el funcionamiento del analizador de licitaciones
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.spotter_licitaciones import (
    LicitacionAnalyzer,
    LicitacionInput,
    LicitacionAnalysisResult
)


class TestSpotterLicitaciones:
    """Tests para el analizador de licitaciones"""
    
    def __init__(self):
        self.analyzer = LicitacionAnalyzer()
        self.tests_run = 0
        self.tests_passed = 0
    
    def log_test(self, name: str, passed: bool, details: str = ""):
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
    
    def test_cpv_nivel_1_match(self):
        """Test CPV nivel 1 (directo) - fotogrametría"""
        licitacion = LicitacionInput(
            expediente="TEST-001",
            objeto="Servicio de fotogrametría",
            cpv="71355100-2"  # Servicios de fotogrametría
        )
        
        result = self.analyzer.analizar(licitacion)
        
        passed = (
            result.cpv_match.nivel == 1 and
            result.cpv_match.puntos >= 40 and
            result.es_relevante
        )
        
        self.log_test(
            "CPV nivel 1 match (fotogrametría)",
            passed,
            f"nivel={result.cpv_match.nivel}, puntos={result.cpv_match.puntos}"
        )
    
    def test_cpv_nivel_2_match(self):
        """Test CPV nivel 2 (indirecto) - construcción"""
        licitacion = LicitacionInput(
            expediente="TEST-002",
            objeto="Trabajos de construcción",
            cpv="45000000-7"  # Construcción
        )
        
        result = self.analyzer.analizar(licitacion)
        
        passed = result.cpv_match.nivel == 2 and result.cpv_match.puntos >= 20
        
        self.log_test(
            "CPV nivel 2 match (construcción)",
            passed,
            f"nivel={result.cpv_match.nivel}, puntos={result.cpv_match.puntos}"
        )
    
    def test_keywords_en_titulo(self):
        """Test detección de keywords en título"""
        licitacion = LicitacionInput(
            expediente="TEST-003",
            objeto="Servicio de topografía con drones para levantamiento cartográfico",
            cpv="99999999-9"  # CPV sin match
        )
        
        result = self.analyzer.analizar(licitacion)
        
        # Debería encontrar: drones, topografía, levantamiento, cartografía
        keywords_esperadas = ["dron", "topográfico", "levantamiento", "cartografía"]
        keywords_encontradas = [k.lower() for k in result.keywords_en_titulo]
        
        # Al menos 1 keyword encontrada
        passed = len(result.keywords_en_titulo) >= 1
        
        self.log_test(
            "Keywords en título",
            passed,
            f"encontradas={result.keywords_en_titulo}"
        )
    
    def test_keywords_universales_drone(self):
        """Test keywords universales relacionadas con drones"""
        licitacion = LicitacionInput(
            expediente="TEST-004",
            objeto="Servicio de inspección con UAV y cámara térmica",
            cpv="99999999-9"
        )
        
        result = self.analyzer.analizar(licitacion)
        
        # Debería encontrar: UAV, cámara térmica
        passed = len(result.keywords_encontradas) >= 1
        
        self.log_test(
            "Keywords universales (UAV, térmica)",
            passed,
            f"encontradas={result.keywords_encontradas}"
        )
    
    def test_scoring_completo(self):
        """Test scoring con todos los factores"""
        plazo = datetime.now(timezone.utc) + timedelta(days=20)
        
        licitacion = LicitacionInput(
            expediente="TEST-005",
            objeto="Servicio de fotogrametría y ortofoto con drones para cartografía municipal",
            cpv="71355100-2",  # Fotogrametría (nivel 1)
            descripcion="Se requiere levantamiento topográfico con UAV multiespectral",
            presupuesto=75000,  # 50k-100k = +25
            plazo_presentacion=plazo  # 15-30 días = +10
        )
        
        result = self.analyzer.analizar(licitacion)
        
        # Score esperado alto (>70)
        passed = result.score >= 70 and result.es_relevante
        
        self.log_test(
            "Scoring completo (alta relevancia)",
            passed,
            f"score={result.score}, detalles={result.detalles_scoring}"
        )
    
    def test_licitacion_no_relevante(self):
        """Test licitación sin relevancia para drones"""
        licitacion = LicitacionInput(
            expediente="TEST-006",
            objeto="Suministro de material de oficina",
            cpv="30190000-7"  # Material de oficina
        )
        
        result = self.analyzer.analizar(licitacion)
        
        passed = not result.es_relevante and result.score < 20
        
        self.log_test(
            "Licitación no relevante",
            passed,
            f"es_relevante={result.es_relevante}, score={result.score}"
        )
    
    def test_batch_analysis(self):
        """Test análisis batch"""
        licitaciones = [
            LicitacionInput(
                expediente="BATCH-001",
                objeto="Servicio de fotogrametría con drones",
                cpv="71355100-2",
                presupuesto=50000
            ),
            LicitacionInput(
                expediente="BATCH-002",
                objeto="Inspección de líneas eléctricas",
                cpv="45231400-9",
                presupuesto=100000
            ),
            LicitacionInput(
                expediente="BATCH-003",
                objeto="Suministro de papel",
                cpv="30190000-7"
            )
        ]
        
        resultados = self.analyzer.analizar_batch(licitaciones)
        estadisticas = self.analyzer.get_estadisticas(resultados)
        
        # Verificar orden (mayor score primero)
        orden_correcto = all(
            resultados[i].score >= resultados[i+1].score 
            for i in range(len(resultados)-1)
        )
        
        passed = (
            len(resultados) == 3 and
            orden_correcto and
            estadisticas["total"] == 3
        )
        
        self.log_test(
            "Análisis batch",
            passed,
            f"total={len(resultados)}, orden_ok={orden_correcto}, stats={estadisticas}"
        )
    
    def test_recomendacion_generada(self):
        """Test que se genera recomendación correcta"""
        licitacion = LicitacionInput(
            expediente="TEST-007",
            objeto="Servicio de topografía aérea con drones y LiDAR para cartografía",
            cpv="71355100-2",
            presupuesto=200000
        )
        
        result = self.analyzer.analizar(licitacion)
        
        passed = len(result.recomendacion) > 0 and "🔥" in result.recomendacion
        
        self.log_test(
            "Recomendación alta prioridad",
            passed,
            f"recomendacion={result.recomendacion}"
        )
    
    def run_all(self):
        """Ejecuta todos los tests"""
        print("=" * 60)
        print("🚀 SpotterSRS-Licitaciones Tests")
        print("=" * 60)
        
        self.test_cpv_nivel_1_match()
        self.test_cpv_nivel_2_match()
        self.test_keywords_en_titulo()
        self.test_keywords_universales_drone()
        self.test_scoring_completo()
        self.test_licitacion_no_relevante()
        self.test_batch_analysis()
        self.test_recomendacion_generada()
        
        print("=" * 60)
        print(f"📊 Tests: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed")
            return 1


def main():
    tester = TestSpotterLicitaciones()
    return tester.run_all()


if __name__ == "__main__":
    sys.exit(main())
