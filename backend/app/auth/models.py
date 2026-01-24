from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RolEnum(str, Enum):
    admin = "admin"
    operador = "operador"
    viewer = "viewer"

# === Request Models ===

class UserCreate(BaseModel):
    email: EmailStr
    nombre: str
    rol: RolEnum = RolEnum.operador
    sectores: List[str] = ["all"]

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[RolEnum] = None
    sectores: Optional[List[str]] = None
    activo: Optional[bool] = None

class TokenData(BaseModel):
    user_id: str
    email: str

# === Response Models ===

class UserResponse(BaseModel):
    user_id: str
    email: str
    nombre: str
    picture: Optional[str] = None
    rol: str
    activo: bool
    sectores: List[str]
    creado_at: Optional[datetime] = None
    ultimo_login: Optional[datetime] = None

class UserMeResponse(UserResponse):
    permisos: dict

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
