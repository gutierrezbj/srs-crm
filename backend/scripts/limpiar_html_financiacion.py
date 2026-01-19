#!/usr/bin/env python3
"""
Script para limpiar HTML residual del campo programa_financiacion
en los datos existentes de la base de datos.

Ejecutar desde el directorio backend:
    python scripts/limpiar_html_financiacion.py
"""

import asyncio
import os
import re
import sys
from pathlib import Path

# Añadir el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Cargar variables de entorno
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')


def limpiar_html(texto: str) -> str:
    """Elimina tags HTML y normaliza espacios"""
    if not texto:
        return texto
    # Eliminar tags HTML
    limpio = re.sub(r'<[^>]+>', '', texto)
    # Normalizar espacios
    limpio = re.sub(r'\s+', ' ', limpio).strip()
    return limpio


async def main():
    # Conectar a MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')

    if not mongo_url or not db_name:
        print("❌ Error: MONGO_URL o DB_NAME no configurados en .env")
        sys.exit(1)

    print(f"🔌 Conectando a MongoDB...")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # Buscar documentos con programa_financiacion que contenga HTML
    filtro = {
        "datos_adjudicatario.programa_financiacion": {"$regex": "<.*>", "$options": "i"}
    }

    cursor = db.oportunidades_placsp.find(filtro)
    documentos = await cursor.to_list(length=None)

    print(f"📊 Encontrados {len(documentos)} documentos con HTML en programa_financiacion")

    if not documentos:
        print("✅ No hay documentos que limpiar")
        return

    # Limpiar cada documento
    actualizados = 0
    for doc in documentos:
        oportunidad_id = doc.get('oportunidad_id', doc.get('_id'))
        datos_adj = doc.get('datos_adjudicatario', {})
        programa_original = datos_adj.get('programa_financiacion', '')

        print(f"\n📄 Oportunidad: {oportunidad_id}")
        print(f"   Original: {programa_original[:100]}...")

        # Limpiar
        programa_limpio = limpiar_html(programa_original)
        print(f"   Limpio:   {programa_limpio[:100]}...")

        # Actualizar en BD
        resultado = await db.oportunidades_placsp.update_one(
            {"_id": doc['_id']},
            {"$set": {"datos_adjudicatario.programa_financiacion": programa_limpio}}
        )

        if resultado.modified_count > 0:
            actualizados += 1
            print(f"   ✅ Actualizado")
        else:
            print(f"   ⚠️ Sin cambios")

    print(f"\n{'='*50}")
    print(f"✅ Limpieza completada: {actualizados}/{len(documentos)} documentos actualizados")

    # Cerrar conexión
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
