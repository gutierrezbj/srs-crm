import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://gutierrezbj_db_user:37UgH2dBTCATHtoO@srs-crm.6heswnw.mongodb.net/?appName=srs-crm"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["srs_crm"]
    
    op = await db.oportunidades_placsp.find_one({"empresas_competidoras.nif": "B30785992"})
    if op:
        print("ID:", op["_id"])
        print("Expediente:", op.get("expediente", "N/A"))
        print("Competidoras:")
        for c in op.get("empresas_competidoras", []):
            print("  -", c.get("nombre", "SIN"), "| NIF:", c.get("nif", "N/A"))
    else:
        print("No encontrada")
    client.close()

asyncio.run(main())
