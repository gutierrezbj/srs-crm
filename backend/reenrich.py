import asyncio
import sys
sys.path.insert(0, '/app')
from motor.motor_asyncio import AsyncIOMotorClient
from app.spotter.adjudicatario_enricher import AdjudicatarioEnricher

MONGODB_URL = "mongodb+srv://gutierrezbj_db_user:37UgH2dBTCATHtoO@srs-crm.6heswnw.mongodb.net/?appName=srs-crm"
OP_ID = "69794ac36e679c4fe424a05e"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["srs_crm"]
    
    from bson import ObjectId
    op = await db.oportunidades_placsp.find_one({"_id": ObjectId(OP_ID)})
    
    if not op:
        print("Oportunidad no encontrada")
        return
    
    print(f"Re-enriching: {op.get('expediente')}")
    print(f"URL adjudicacion: {op.get('url_adjudicacion', 'N/A')}")
    
    # Clear existing competitors to force re-extract
    await db.oportunidades_placsp.update_one(
        {"_id": ObjectId(OP_ID)},
        {"$set": {"empresas_competidoras": []}}
    )
    print("Cleared existing competitors")
    
    # Re-enrich
    enricher = AdjudicatarioEnricher(db)
    result = await enricher.enrich_oportunidad(op)
    
    if result:
        print("SUCCESS - New competitors:")
        for c in result.get("empresas_competidoras", []):
            print(f"  - {c.get('nombre', 'SIN')} | NIF: {c.get('nif', 'N/A')}")
    else:
        print("Enrichment returned None")
    
    client.close()

asyncio.run(main())
