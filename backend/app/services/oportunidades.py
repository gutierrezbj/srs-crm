from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
import os
import math
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))
db = client.srs_crm
oportunidades_collection = db.oportunidades
users_collection = db.users

# === Índices (ejecutar una vez) ===
def create_indexes():
    """Crear índices para la colección oportunidades."""
    oportunidades_collection.create_index("expediente", unique=True)
    oportunidades_collection.create_index([("tipo", 1), ("sector", 1), ("scoring.total", -1)])
    oportunidades_collection.create_index([("tipo", 1), ("sector", 1), ("estado", 1)])
    oportunidades_collection.create_index([("propietario", 1), ("estado", 1)])
    oportunidades_collection.create_index("estado_placsp")
    oportunidades_collection.create_index("fechas.limite")
    oportunidades_collection.create_index("dias_restantes")

# === Helpers ===

def get_user_name(user_id: str) -> Optional[str]:
    """Obtener nombre de usuario por ID."""
    if not user_id:
        return None
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return user.get("nombre") or user.get("name")
    return None

def calculate_dias_restantes(fechas: dict, tipo: str) -> Optional[int]:
    """Calcular días restantes según tipo."""
    if not fechas:
        return None
    
    fecha_ref = None
    if tipo == "licitacion":
        fecha_ref = fechas.get("limite")
    else:
        fecha_ref = fechas.get("fin_contrato")
    
    if not fecha_ref:
        return None
    
    if isinstance(fecha_ref, str):
        fecha_ref = datetime.fromisoformat(fecha_ref.replace("Z", "+00:00"))
    
    delta = fecha_ref - datetime.now(timezone.utc)
    return max(0, delta.days)

def serialize_oportunidad(op: dict) -> dict:
    """Serializar oportunidad para respuesta."""
    if not op:
        return None
    
    op["_id"] = str(op["_id"]) if "_id" in op else None
    
    # Calcular días restantes
    op["dias_restantes"] = calculate_dias_restantes(op.get("fechas"), op.get("tipo"))
    
    # Añadir nombre del propietario
    op["propietario_nombre"] = get_user_name(op.get("propietario"))
    
    return op

# === CRUD Operations ===

def get_oportunidades(
    tipo: Optional[str] = None,
    sector: Optional[str] = None,
    estado: Optional[str] = None,
    propietario: Optional[str] = None,
    score_min: Optional[int] = None,
    nivel: Optional[str] = None,
    dias_max: Optional[int] = None,
    categoria: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = "scoring.total",
    order: str = "desc",
    page: int = 1,
    limit: int = 50,
    current_user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Obtener oportunidades con filtros y paginación."""
    
    # Construir query
    query = {}
    
    if tipo:
        query["tipo"] = tipo
    if sector and sector != "all":
        query["sector"] = sector
    if estado and estado != "all":
        query["estado"] = estado
    if propietario:
        if propietario == "me" and current_user_id:
            query["propietario"] = current_user_id
        elif propietario == "null":
            query["propietario"] = None
        elif propietario != "all":
            query["propietario"] = propietario
    if score_min:
        query["scoring.total"] = {"$gte": score_min}
    if nivel and nivel != "all":
        query["scoring.nivel"] = nivel
    if dias_max:
        query["dias_restantes"] = {"$lte": dias_max}
    if categoria and categoria != "all":
        query["analisis.categoria"] = categoria
    if q:
        query["$or"] = [
            {"titulo": {"$regex": q, "$options": "i"}},
            {"descripcion": {"$regex": q, "$options": "i"}},
            {"organo_contratacion": {"$regex": q, "$options": "i"}}
        ]
    
    # Contar total
    total = oportunidades_collection.count_documents(query)
    
    # Ordenar
    sort_direction = DESCENDING if order == "desc" else 1
    
    # Paginar
    skip = (page - 1) * limit
    
    # Ejecutar query
    cursor = oportunidades_collection.find(query).sort(sort, sort_direction).skip(skip).limit(limit)
    
    items = [serialize_oportunidad(op) for op in cursor]
    
    return {
        "total": total,
        "page": page,
        "pages": math.ceil(total / limit) if limit > 0 else 1,
        "items": items
    }

def get_oportunidad_by_expediente(expediente: str) -> Optional[dict]:
    """Obtener oportunidad por expediente."""
    op = oportunidades_collection.find_one({"expediente": expediente})
    return serialize_oportunidad(op)

def create_oportunidad(data: dict) -> dict:
    """Crear nueva oportunidad."""
    data["creado_at"] = datetime.now(timezone.utc)
    data["actualizado_at"] = datetime.now(timezone.utc)
    data["estado"] = data.get("estado", "nueva")
    data["historial"] = []
    
    # Calcular días restantes
    data["dias_restantes"] = calculate_dias_restantes(data.get("fechas"), data.get("tipo"))
    
    result = oportunidades_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return serialize_oportunidad(data)

def update_oportunidad(expediente: str, update_data: dict, usuario: str = None) -> Optional[dict]:
    """Actualizar oportunidad."""
    # Obtener actual para historial
    current = oportunidades_collection.find_one({"expediente": expediente})
    if not current:
        return None
    
    # Preparar historial
    historial_entries = []
    for key, new_value in update_data.items():
        if key in current and current[key] != new_value:
            historial_entries.append({
                "campo": key,
                "valor_anterior": current[key],
                "valor_nuevo": new_value,
                "usuario": usuario,
                "fecha": datetime.now(timezone.utc)
            })
    
    # Actualizar
    update_data["actualizado_at"] = datetime.now(timezone.utc)
    if usuario:
        update_data["actualizado_por"] = usuario
    
    update_ops = {"$set": update_data}
    if historial_entries:
        update_ops["$push"] = {"historial": {"$each": historial_entries}}
    
    result = oportunidades_collection.find_one_and_update(
        {"expediente": expediente},
        update_ops,
        return_document=True
    )
    
    return serialize_oportunidad(result)

def update_estado(expediente: str, nuevo_estado: str, usuario: str = None) -> Optional[dict]:
    """Cambiar estado de oportunidad."""
    return update_oportunidad(expediente, {"estado": nuevo_estado}, usuario)

def update_propietario(expediente: str, propietario: Optional[str], usuario: str = None) -> Optional[dict]:
    """Asignar propietario a oportunidad."""
    return update_oportunidad(expediente, {"propietario": propietario}, usuario)

def delete_oportunidad(expediente: str) -> bool:
    """Eliminar oportunidad."""
    result = oportunidades_collection.delete_one({"expediente": expediente})
    return result.deleted_count > 0

# === Stats ===

def get_stats(tipo: Optional[str] = None, sector: Optional[str] = None) -> dict:
    """Obtener estadísticas de oportunidades."""
    query = {}
    if tipo:
        query["tipo"] = tipo
    if sector and sector != "all":
        query["sector"] = sector
    
    # Total
    total = oportunidades_collection.count_documents(query)
    
    # Por estado
    pipeline_estado = [
        {"$match": query},
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}}
    ]
    por_estado = {r["_id"]: r["count"] for r in oportunidades_collection.aggregate(pipeline_estado)}
    
    # Por nivel
    pipeline_nivel = [
        {"$match": query},
        {"$group": {"_id": "$scoring.nivel", "count": {"$sum": 1}}}
    ]
    por_nivel = {r["_id"]: r["count"] for r in oportunidades_collection.aggregate(pipeline_nivel) if r["_id"]}
    
    # Por categoría
    pipeline_categoria = [
        {"$match": query},
        {"$group": {"_id": "$analisis.categoria", "count": {"$sum": 1}}}
    ]
    por_categoria = {r["_id"]: r["count"] for r in oportunidades_collection.aggregate(pipeline_categoria) if r["_id"]}
    
    # Score promedio
    pipeline_score = [
        {"$match": query},
        {"$group": {"_id": None, "avg": {"$avg": "$scoring.total"}}}
    ]
    score_result = list(oportunidades_collection.aggregate(pipeline_score))
    score_promedio = score_result[0]["avg"] if score_result and score_result[0]["avg"] else 0
    
    # Importe total
    pipeline_importe = [
        {"$match": query},
        {"$group": {"_id": None, "total": {"$sum": "$importe"}}}
    ]
    importe_result = list(oportunidades_collection.aggregate(pipeline_importe))
    importe_total = importe_result[0]["total"] if importe_result and importe_result[0]["total"] else 0
    
    # Urgentes (días restantes <= 7)
    urgentes_query = {**query, "dias_restantes": {"$lte": 7, "$gt": 0}}
    urgentes = oportunidades_collection.count_documents(urgentes_query)
    
    return {
        "total": total,
        "por_estado": por_estado,
        "por_nivel": por_nivel,
        "por_categoria": por_categoria,
        "score_promedio": round(score_promedio, 1),
        "importe_total": importe_total,
        "urgentes": urgentes
    }

# === Bulk Operations ===

def bulk_update_estado(expedientes: List[str], estado: str, usuario: str = None) -> int:
    """Actualizar estado de múltiples oportunidades."""
    result = oportunidades_collection.update_many(
        {"expediente": {"$in": expedientes}},
        {
            "$set": {
                "estado": estado,
                "actualizado_at": datetime.now(timezone.utc),
                "actualizado_por": usuario
            }
        }
    )
    return result.modified_count

def bulk_update_propietario(expedientes: List[str], propietario: str, usuario: str = None) -> int:
    """Asignar propietario a múltiples oportunidades."""
    result = oportunidades_collection.update_many(
        {"expediente": {"$in": expedientes}},
        {
            "$set": {
                "propietario": propietario,
                "actualizado_at": datetime.now(timezone.utc),
                "actualizado_por": usuario
            }
        }
    )
    return result.modified_count

# Crear índices al importar
try:
    create_indexes()
except Exception as e:
    print(f"Warning: Could not create indexes: {e}")
