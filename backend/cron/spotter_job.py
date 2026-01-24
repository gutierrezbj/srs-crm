"""Job para ejecutar SpotterEngine vía cron."""
import asyncio
import sys
import os
from datetime import datetime

# Añadir path del backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.spotter.engine import SpotterEngine, ConfigLoader

async def run_spotter_all():
    """Ejecutar spotter para todos los sectores activos."""
    print(f"\n{'='*60}")
    print(f"SpotterEngine - Ejecución: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    sectores = ConfigLoader.get_active_sectors()
    
    for sector_config in sectores:
        sector = sector_config.get("sector")
        tipos = sector_config.get("tipos", ["licitacion"])
        
        for tipo in tipos:
            print(f"\n--- Procesando: {sector} / {tipo} ---")
            try:
                engine = SpotterEngine(sector=sector, tipo=tipo)
                result = await engine.ejecutar()
                
                print(f"  Total procesadas: {result['total_procesadas']}")
                print(f"  Nuevas: {result['nuevas']}")
                print(f"  Actualizadas: {result['actualizadas']}")
                print(f"  Descartadas: {result['descartadas']}")
                print(f"  Por nivel: {result['por_nivel']}")
                
            except Exception as e:
                print(f"  ERROR: {e}")
    
    print(f"\n{'='*60}")
    print("Ejecución completada")
    print(f"{'='*60}\n")

async def run_spotter_sector(sector: str, tipo: str = "licitacion"):
    """Ejecutar spotter para un sector específico."""
    print(f"\n--- SpotterEngine: {sector} / {tipo} ---")
    
    try:
        engine = SpotterEngine(sector=sector, tipo=tipo)
        result = await engine.ejecutar()
        
        print(f"Resultado: {result}")
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sector = sys.argv[1]
        tipo = sys.argv[2] if len(sys.argv) > 2 else "licitacion"
        asyncio.run(run_spotter_sector(sector, tipo))
    else:
        asyncio.run(run_spotter_all())
