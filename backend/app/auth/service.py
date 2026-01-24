from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# Config
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# MongoDB
client = MongoClient(os.getenv("MONGO_URL"))
db = client.srs_crm
users_collection = db.users

def create_access_token(data: dict) -> str:
    """Crear JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verificar y decodificar JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_by_email(email: str) -> Optional[dict]:
    """Buscar usuario por email."""
    return users_collection.find_one({"email": email})

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Buscar usuario por user_id."""
    return users_collection.find_one({"user_id": user_id})

def get_all_users() -> list:
    """Obtener todos los usuarios."""
    users = list(users_collection.find())
    for user in users:
        user["_id"] = str(user["_id"])
    return users

def create_user(email: str, nombre: str, rol: str = "operador", sectores: list = None, creado_por: str = "system") -> dict:
    """Crear nuevo usuario."""
    import uuid
    
    if sectores is None:
        sectores = ["all"]
    
    user_data = {
        "user_id": f"user_{uuid.uuid4().hex[:12]}",
        "email": email,
        "nombre": nombre,
        "name": nombre,  # Compatibilidad
        "picture": None,
        "rol": rol,
        "activo": True,
        "sectores": sectores,
        "creado_at": datetime.now(timezone.utc),
        "creado_por": creado_por,
        "ultimo_login": None
    }
    
    result = users_collection.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data

def update_user(user_id: str, update_data: dict, actualizado_por: str = None) -> Optional[dict]:
    """Actualizar usuario."""
    update_data["actualizado_at"] = datetime.now(timezone.utc)
    if actualizado_por:
        update_data["actualizado_por"] = actualizado_por
    
    result = users_collection.find_one_and_update(
        {"user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    if result:
        result["_id"] = str(result["_id"])
    return result

def delete_user(user_id: str) -> bool:
    """Eliminar usuario."""
    result = users_collection.delete_one({"user_id": user_id})
    return result.deleted_count > 0

def update_last_login(user_id: str):
    """Actualizar último login."""
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"ultimo_login": datetime.now(timezone.utc)}}
    )

def upsert_google_user(google_data: dict) -> dict:
    """
    Crear o actualizar usuario desde Google OAuth.
    Solo actualiza picture y ultimo_login si ya existe.
    """
    email = google_data.get("email")
    existing = get_user_by_email(email)
    
    if existing:
        # Usuario existe - actualizar solo algunos campos
        update_data = {
            "picture": google_data.get("picture"),
            "ultimo_login": datetime.now(timezone.utc)
        }
        # Actualizar name si viene de Google y no tiene nombre
        if not existing.get("nombre") and google_data.get("name"):
            update_data["nombre"] = google_data.get("name")
            update_data["name"] = google_data.get("name")
        
        users_collection.update_one({"email": email}, {"$set": update_data})
        existing.update(update_data)
        existing["_id"] = str(existing["_id"])
        return existing
    else:
        # Usuario NO existe - retornar None (no crear automáticamente)
        return None

def get_user_permissions(user: dict) -> dict:
    """Calcular permisos basados en rol."""
    rol = user.get("rol", "viewer")
    sectores = user.get("sectores", [])
    
    return {
        "puede_gestionar_usuarios": rol == "admin",
        "puede_ejecutar_spotter": rol in ["admin", "operador"],
        "puede_editar": rol in ["admin", "operador"],
        "puede_asignar_otros": rol == "admin",
        "sectores_visibles": ["it", "drones", "energia"] if "all" in sectores else sectores
    }
