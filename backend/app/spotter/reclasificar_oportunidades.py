#!/usr/bin/env python3
"""
Script de reclasificación de oportunidades existentes en MongoDB.

Usa el algoritmo actualizado de SpotterSRS para reclasificar todas las
oportunidades en la colección oportunidades_placsp.

Uso:
    python reclasificar_oportunidades.py [--dry-run]

    --dry-run: Muestra los cambios sin aplicarlos a la base de datos
"""

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Añadir el directorio padre al path para importar spotter_srs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spotter_srs import (
    calcular_dolor,
    extraer_keywords,
    TipoOportunidad,
)


# Cargar variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

MONGO_URL = os.environ.get('MONGO_URL', '')
DB_NAME = os.environ.get('DB_NAME', 'srs_crm')


async def reclasificar_oportunidades(dry_run: bool = False):
    """
    Reclasifica todas las oportunidades existentes usando el algoritmo actualizado.

    Args:
        dry_run: Si es True, solo muestra los cambios sin aplicarlos.
    """
    if not MONGO_URL:
        print("❌ Error: MONGO_URL no está configurada en .env")
        return

    print(f"""
╔════════════════════════════════════════════════════════════════════╗
║          RECLASIFICACIÓN DE OPORTUNIDADES PLACSP                  ║
║          Usando algoritmo SpotterSRS actualizado                  ║
╚════════════════════════════════════════════════════════════════════╝

Modo: {'🔍 DRY RUN (sin cambios)' if dry_run else '✏️  APLICANDO CAMBIOS'}
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

    # Conectar a MongoDB
    print("📡 Conectando a MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    try:
        # Obtener todas las oportunidades
        oportunidades = await db.oportunidades.find(
            {},
            {"_id": 0}
        ).to_list(10000)

        print(f"📊 Encontradas {len(oportunidades)} oportunidades para analizar\n")

        if not oportunidades:
            print("⚠️  No hay oportunidades en la base de datos")
            return

        # Contadores
        cambios = []
        sin_cambios = 0
        errores = 0

        # Procesar cada oportunidad
        for opp in oportunidades:
            try:
                oportunidad_id = opp.get('oportunidad_id', 'N/A')
                objeto = opp.get('objeto', '')
                cpv = opp.get('cpv', '')
                tipo_actual = opp.get('tipo_srs', '')
                fecha_adj = opp.get('fecha_adjudicacion', '')

                # Calcular días restantes si hay fecha de fin
                dias_restantes = opp.get('dias_restantes')

                # Extraer keywords con el algoritmo actualizado
                keywords = extraer_keywords(objeto)

                # Convertir fecha a string si es datetime
                if isinstance(fecha_adj, datetime):
                    fecha_adj_str = fecha_adj.strftime('%Y-%m-%d')
                else:
                    fecha_adj_str = str(fecha_adj)[:10] if fecha_adj else ''

                # Calcular nuevo dolor/clasificación
                dolor = calcular_dolor(
                    objeto=objeto,
                    fecha_adjudicacion=fecha_adj_str,
                    duracion_dias=dias_restantes,
                    cpv=cpv,
                    keywords=keywords
                )

                nuevo_tipo = dolor.tipo_oportunidad.value
                nuevas_keywords = list(keywords.keys())
                nuevos_indicadores = dolor.indicadores_urgencia
                nuevo_score = dolor.score_dolor

                # Comparar con el tipo actual
                if tipo_actual != nuevo_tipo:
                    cambio = {
                        'oportunidad_id': oportunidad_id,
                        'expediente': opp.get('expediente', 'N/A'),
                        'objeto': objeto[:80] + '...' if len(objeto) > 80 else objeto,
                        'tipo_anterior': tipo_actual,
                        'tipo_nuevo': nuevo_tipo,
                        'keywords': nuevas_keywords[:5],
                        'score_anterior': opp.get('score', 0),
                        'score_nuevo': nuevo_score,
                    }
                    cambios.append(cambio)

                    # Aplicar cambio si no es dry run
                    if not dry_run:
                        await db.oportunidades.update_one(
                            {"oportunidad_id": oportunidad_id},
                            {"$set": {
                                "tipo_srs": nuevo_tipo,
                                "keywords": nuevas_keywords,
                                "indicadores_dolor": nuevos_indicadores,
                                "score": nuevo_score,
                            }}
                        )
                else:
                    sin_cambios += 1

            except Exception as e:
                errores += 1
                print(f"❌ Error procesando {opp.get('oportunidad_id', 'N/A')}: {e}")

        # Mostrar resultados
        print("=" * 70)
        print("📋 RESUMEN DE RECLASIFICACIÓN")
        print("=" * 70)
        print(f"   Total oportunidades: {len(oportunidades)}")
        print(f"   ✅ Sin cambios: {sin_cambios}")
        print(f"   🔄 Con cambios: {len(cambios)}")
        print(f"   ❌ Errores: {errores}")
        print()

        if cambios:
            print("=" * 70)
            print("🔄 DETALLE DE CAMBIOS" + (" (NO APLICADOS - DRY RUN)" if dry_run else " (APLICADOS)"))
            print("=" * 70)

            for i, c in enumerate(cambios, 1):
                print(f"""
┌─ [{i}] {c['expediente']} ─────────────────────────────────
│ Objeto: {c['objeto']}
│
│ Tipo anterior: {c['tipo_anterior']}
│ Tipo nuevo:    {c['tipo_nuevo']}
│
│ Score: {c['score_anterior']} → {c['score_nuevo']}
│ Keywords: {', '.join(c['keywords']) if c['keywords'] else 'ninguna'}
└────────────────────────────────────────────────────────────""")

            print()

        # Resumen por tipo
        if cambios:
            print("=" * 70)
            print("📊 CAMBIOS POR TIPO")
            print("=" * 70)

            # Contar cambios por tipo nuevo
            por_tipo = {}
            for c in cambios:
                tipo = c['tipo_nuevo']
                if tipo not in por_tipo:
                    por_tipo[tipo] = 0
                por_tipo[tipo] += 1

            for tipo, count in sorted(por_tipo.items(), key=lambda x: x[1], reverse=True):
                print(f"   {tipo}: {count}")
            print()

        if dry_run and cambios:
            print("=" * 70)
            print("💡 Para aplicar los cambios, ejecuta sin --dry-run:")
            print("   python reclasificar_oportunidades.py")
            print("=" * 70)
        elif not dry_run and cambios:
            print("=" * 70)
            print("✅ Cambios aplicados correctamente")
            print("=" * 70)

    finally:
        client.close()
        print("\n📡 Conexión cerrada")


def main():
    """Punto de entrada principal."""
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return

    asyncio.run(reclasificar_oportunidades(dry_run=dry_run))


if __name__ == "__main__":
    main()
