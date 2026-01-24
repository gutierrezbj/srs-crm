from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from typing import List
import httpx
import os
from dotenv import load_dotenv

from .models import (
    UserCreate, UserUpdate, UserResponse, UserMeResponse,
    TokenResponse, MessageResponse
)
from .service import (
    get_user_by_email, get_all_users, create_user, update_user, delete_user,
    create_access_token, upsert_google_user, get_user_permissions
)
from .dependencies import get_current_user, require_admin

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])
users_router = APIRouter(prefix="/api/users", tags=["users"])

# Google OAuth Config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://crm.systemrapidsolutions.com:3001/api/auth/callback")

# === AUTH ENDPOINTS ===

@router.get("/login")
async def login():
    """Redirigir a Google OAuth."""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=select_account"
    )
    return RedirectResponse(url=google_auth_url)

@router.get("/callback")
async def callback(code: str, request: Request):
    """Callback de Google OAuth."""
    # Intercambiar code por tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI
            }
        )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al obtener token de Google")
    
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    
    # Obtener info del usuario de Google
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    
    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al obtener datos de Google")
    
    google_data = user_response.json()
    
    # Verificar si usuario existe y está activo
    user = upsert_google_user(google_data)
    
    if not user:
        # Usuario no existe en DB - acceso denegado
        frontend_url = os.getenv("FRONTEND_URL", "https://crm.systemrapidsolutions.com:3001")
        return RedirectResponse(url=f"{frontend_url}/login?error=no_autorizado")
    
    if not user.get("activo", False):
        frontend_url = os.getenv("FRONTEND_URL", "https://crm.systemrapidsolutions.com:3001")
        return RedirectResponse(url=f"{frontend_url}/login?error=cuenta_desactivada")
    
    # Crear JWT
    jwt_token = create_access_token({
        "user_id": user["user_id"],
        "email": user["email"],
        "rol": user.get("rol", "viewer")
    })
    
    # Redirigir al frontend con token
    frontend_url = os.getenv("FRONTEND_URL", "https://crm.systemrapidsolutions.com:3001")
    return RedirectResponse(url=f"{frontend_url}/auth/success?token={jwt_token}")

@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Obtener datos del usuario actual."""
    permisos = get_user_permissions(current_user)
    return UserMeResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        nombre=current_user.get("nombre") or current_user.get("name", ""),
        picture=current_user.get("picture"),
        rol=current_user.get("rol", "viewer"),
        activo=current_user.get("activo", True),
        sectores=current_user.get("sectores", ["all"]),
        creado_at=current_user.get("creado_at"),
        ultimo_login=current_user.get("ultimo_login"),
        permisos=permisos
    )

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """Cerrar sesión (client-side debe eliminar el token)."""
    return MessageResponse(message="Sesión cerrada correctamente")

# === USERS ENDPOINTS (Admin only) ===

@users_router.get("", response_model=List[UserResponse])
async def list_users(current_user: dict = Depends(require_admin)):
    """Listar todos los usuarios."""
    users = get_all_users()
    return [
        UserResponse(
            user_id=u["user_id"],
            email=u["email"],
            nombre=u.get("nombre") or u.get("name", ""),
            picture=u.get("picture"),
            rol=u.get("rol", "viewer"),
            activo=u.get("activo", True),
            sectores=u.get("sectores", ["all"]),
            creado_at=u.get("creado_at"),
            ultimo_login=u.get("ultimo_login")
        )
        for u in users
    ]

@users_router.post("", response_model=UserResponse)
async def create_new_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_admin)
):
    """Crear nuevo usuario."""
    # Verificar que no exista
    existing = get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email"
        )
    
    user = create_user(
        email=user_data.email,
        nombre=user_data.nombre,
        rol=user_data.rol.value,
        sectores=user_data.sectores,
        creado_por=current_user["user_id"]
    )
    
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        nombre=user["nombre"],
        picture=user.get("picture"),
        rol=user["rol"],
        activo=user["activo"],
        sectores=user["sectores"],
        creado_at=user.get("creado_at"),
        ultimo_login=user.get("ultimo_login")
    )

@users_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(require_admin)):
    """Obtener usuario por ID."""
    from .service import get_user_by_id
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        nombre=user.get("nombre") or user.get("name", ""),
        picture=user.get("picture"),
        rol=user.get("rol", "viewer"),
        activo=user.get("activo", True),
        sectores=user.get("sectores", ["all"]),
        creado_at=user.get("creado_at"),
        ultimo_login=user.get("ultimo_login")
    )

@users_router.put("/{user_id}", response_model=UserResponse)
async def update_existing_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(require_admin)
):
    """Actualizar usuario."""
    update_dict = user_data.model_dump(exclude_unset=True)
    if "rol" in update_dict and update_dict["rol"]:
        update_dict["rol"] = update_dict["rol"].value
    
    user = update_user(user_id, update_dict, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        nombre=user.get("nombre") or user.get("name", ""),
        picture=user.get("picture"),
        rol=user.get("rol", "viewer"),
        activo=user.get("activo", True),
        sectores=user.get("sectores", ["all"]),
        creado_at=user.get("creado_at"),
        ultimo_login=user.get("ultimo_login")
    )

@users_router.delete("/{user_id}", response_model=MessageResponse)
async def delete_existing_user(
    user_id: str,
    current_user: dict = Depends(require_admin)
):
    """Eliminar usuario."""
    # No permitir auto-eliminación
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminarte a ti mismo"
        )
    
    success = delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return MessageResponse(message="Usuario eliminado correctamente")

@users_router.patch("/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: str,
    current_user: dict = Depends(require_admin)
):
    """Activar/desactivar usuario."""
    from .service import get_user_by_id
    
    # No permitir auto-desactivación
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivarte a ti mismo"
        )
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    new_status = not user.get("activo", True)
    updated = update_user(user_id, {"activo": new_status}, current_user["user_id"])
    
    return UserResponse(
        user_id=updated["user_id"],
        email=updated["email"],
        nombre=updated.get("nombre") or updated.get("name", ""),
        picture=updated.get("picture"),
        rol=updated.get("rol", "viewer"),
        activo=updated.get("activo", True),
        sectores=updated.get("sectores", ["all"]),
        creado_at=updated.get("creado_at"),
        ultimo_login=updated.get("ultimo_login")
    )
