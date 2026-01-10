from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Response, Request, Depends
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import csv
import io
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="System Rapid Solutions CRM")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============== MODELS ==============

# Lead stages
LEAD_STAGES = ["nuevo", "contactado", "calificado", "propuesta", "negociacion", "ganado", "perdido"]

# Dropdown options
SECTORES = [
    "IT / Soporte técnico",
    "Fotovoltaica / Energía",
    "Drones / Inspección",
    "Telecomunicaciones",
    "Retail",
    "Banca / Finanzas",
    "Industria / Manufactura",
    "Logística",
    "Otro"
]

SERVICIOS = [
    "Soporte IT Remoto",
    "Soporte IT Presencial",
    "Smart Hands / Remote Hands",
    "Managed Services (MSP)",
    "Inspección con Drones",
    "Termografía",
    "Topografía / Fotogrametría",
    "Cableado Estructurado",
    "Consultoría ENS",
    "Formación / Cursos",
    "Otro"
]

FUENTES = [
    "Apollo",
    "Web",
    "Referido",
    "Feria / Evento",
    "LinkedIn",
    "Licitación",
    "Otro"
]

URGENCIAS = [
    "Inmediata (< 1 mes)",
    "Corto plazo (1-3 meses)",
    "Medio plazo (3-6 meses)",
    "Largo plazo (6+ meses)",
    "Sin definir"
]

MOTIVOS_PERDIDA = [
    "Precio",
    "Timing",
    "Competencia",
    "No responde",
    "No califica",
    "Otro"
]

TIPOS_SEGUIMIENTO = [
    "Llamada",
    "Email",
    "Reunión",
    "Demo",
    "Propuesta",
    "Otro"
]

# Allowed users (initial, can be managed via admin panel)
ALLOWED_USERS = {
    "juancho@systemrapidsolutions.com": {"name": "JuanCho", "role": "admin"},
    "andros@systemrapidsolutions.com": {"name": "Andros", "role": "user"},
    "adriana@systemrapidsolutions.com": {"name": "Adriana", "role": "user"},
}

# Development mode - set to False for production
DEV_MODE = os.environ.get('DEV_MODE', 'true').lower() == 'true'

class UserBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role: str = "user"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

class LeadBase(BaseModel):
    empresa: str
    contacto: str
    email: EmailStr
    telefono: Optional[str] = None
    cargo: Optional[str] = None
    sector: Optional[str] = None
    valor_estimado: float = 0.0
    etapa: str = "nuevo"
    notas: Optional[str] = None
    # New fields
    propietario: Optional[str] = None  # user_id del propietario
    servicios: Optional[List[str]] = []  # Multiple services
    fuente: Optional[str] = None
    urgencia: Optional[str] = "Sin definir"
    motivo_perdida: Optional[str] = None
    proximo_seguimiento: Optional[str] = None  # ISO date
    tipo_seguimiento: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    empresa: Optional[str] = None
    contacto: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    cargo: Optional[str] = None
    sector: Optional[str] = None
    valor_estimado: Optional[float] = None
    etapa: Optional[str] = None
    notas: Optional[str] = None
    propietario: Optional[str] = None
    servicios: Optional[List[str]] = None
    fuente: Optional[str] = None
    urgencia: Optional[str] = None
    motivo_perdida: Optional[str] = None
    proximo_seguimiento: Optional[str] = None
    tipo_seguimiento: Optional[str] = None

class Lead(LeadBase):
    model_config = ConfigDict(extra="ignore")
    lead_id: str
    fecha_creacion: datetime
    fecha_ultimo_contacto: Optional[datetime] = None
    dias_sin_actividad: int = 0
    created_by: str
    propietario_nombre: Optional[str] = None

class ActivityBase(BaseModel):
    tipo: str  # nota, llamada, email, reunion
    descripcion: str

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    model_config = ConfigDict(extra="ignore")
    activity_id: str
    lead_id: str
    user_id: str
    user_name: str
    created_at: datetime

class EnrichRequest(BaseModel):
    email: str
    empresa: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    cargo: Optional[str] = None
    sector: Optional[str] = None

# ============== AUTH HELPERS ==============

async def get_current_user(request: Request) -> UserResponse:
    """Get current user from session token cookie or Authorization header"""
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    session = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=401, detail="Sesión inválida")
    
    expires_at = session["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Sesión expirada")
    
    user = await db.users.find_one(
        {"user_id": session["user_id"]},
        {"_id": 0}
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return UserResponse(**user)

# ============== AUTH ROUTES ==============

@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id from Emergent Auth for session data"""
    session_id = request.headers.get("X-Session-ID")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID requerido")
    
    # Exchange session_id with Emergent Auth
    async with httpx.AsyncClient() as client:
        auth_response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        
        if auth_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Sesión inválida de Emergent Auth")
        
        auth_data = auth_response.json()
    
    email = auth_data.get("email", "").lower()
    
    # In DEV_MODE, allow any email. In production, restrict to @systemrapidsolutions.com
    if not DEV_MODE:
        # Check domain restriction
        if not email.endswith("@systemrapidsolutions.com"):
            raise HTTPException(
                status_code=403, 
                detail="Solo cuentas @systemrapidsolutions.com permitidas"
            )
        
        # Check if user is in allowed list (case insensitive)
        allowed_user = ALLOWED_USERS.get(email)
        if not allowed_user:
            raise HTTPException(
                status_code=403,
                detail="Usuario no autorizado. Contacte al administrador."
            )
        user_role = allowed_user["role"]
        user_name = auth_data.get("name", allowed_user["name"])
    else:
        # DEV_MODE: Allow any Google account as admin for testing
        user_role = "admin"
        user_name = auth_data.get("name", email.split("@")[0])
    
    # Create or update user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"email": email},
            {"$set": {
                "name": user_name,
                "picture": auth_data.get("picture"),
                "role": user_role
            }}
        )
    else:
        new_user = {
            "user_id": user_id,
            "email": email,
            "name": user_name,
            "picture": auth_data.get("picture"),
            "role": user_role,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(new_user)
    
    # Create session
    session_token = auth_data.get("session_token", f"session_{uuid.uuid4().hex}")
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return UserResponse(**user)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user and clear session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Sesión cerrada"}

# ============== LEADS ROUTES ==============

def calculate_days_without_activity(fecha_ultimo_contacto: Optional[datetime]) -> int:
    """Calculate days since last activity"""
    if not fecha_ultimo_contacto:
        return 999
    
    if isinstance(fecha_ultimo_contacto, str):
        fecha_ultimo_contacto = datetime.fromisoformat(fecha_ultimo_contacto)
    
    if fecha_ultimo_contacto.tzinfo is None:
        fecha_ultimo_contacto = fecha_ultimo_contacto.replace(tzinfo=timezone.utc)
    
    delta = datetime.now(timezone.utc) - fecha_ultimo_contacto
    return delta.days

@api_router.get("/leads", response_model=List[Lead])
async def get_leads(
    etapa: Optional[str] = None,
    sector: Optional[str] = None,
    propietario: Optional[str] = None,
    search: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all leads with optional filters"""
    query = {}
    
    if etapa:
        query["etapa"] = etapa
    if sector:
        query["sector"] = sector
    if propietario:
        query["propietario"] = propietario
    if search:
        query["$or"] = [
            {"empresa": {"$regex": search, "$options": "i"}},
            {"contacto": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    leads = await db.leads.find(query, {"_id": 0}).sort("fecha_creacion", -1).to_list(1000)
    
    # Get all users for propietario_nombre lookup
    users = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1}).to_list(100)
    users_map = {u["user_id"]: u["name"] for u in users}
    
    for lead in leads:
        if isinstance(lead.get("fecha_creacion"), str):
            lead["fecha_creacion"] = datetime.fromisoformat(lead["fecha_creacion"])
        if lead.get("fecha_ultimo_contacto") and isinstance(lead["fecha_ultimo_contacto"], str):
            lead["fecha_ultimo_contacto"] = datetime.fromisoformat(lead["fecha_ultimo_contacto"])
        lead["dias_sin_actividad"] = calculate_days_without_activity(lead.get("fecha_ultimo_contacto"))
        # Add propietario name
        if lead.get("propietario"):
            lead["propietario_nombre"] = users_map.get(lead["propietario"], "")
        else:
            lead["propietario_nombre"] = None
        # Ensure servicios is a list
        if not lead.get("servicios"):
            lead["servicios"] = []
    
    return leads

@api_router.get("/leads/stats")
async def get_leads_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get dashboard statistics"""
    leads = await db.leads.find({}, {"_id": 0}).to_list(1000)
    today = datetime.now(timezone.utc).date()
    
    # Count by stage
    stages_count = {stage: 0 for stage in LEAD_STAGES}
    total_pipeline = 0.0
    leads_without_activity = 0
    seguimientos_hoy = []
    
    for lead in leads:
        etapa = lead.get("etapa", "nuevo")
        stages_count[etapa] = stages_count.get(etapa, 0) + 1
        
        if etapa not in ["ganado", "perdido"]:
            total_pipeline += lead.get("valor_estimado", 0)
        
        dias = calculate_days_without_activity(lead.get("fecha_ultimo_contacto"))
        if dias > 7 and etapa not in ["ganado", "perdido"]:
            leads_without_activity += 1
        
        # Check for seguimientos today
        proximo = lead.get("proximo_seguimiento")
        if proximo:
            try:
                fecha_seg = datetime.fromisoformat(proximo.replace("Z", "+00:00")).date() if isinstance(proximo, str) else proximo.date()
                if fecha_seg == today:
                    seguimientos_hoy.append({
                        "lead_id": lead.get("lead_id"),
                        "empresa": lead.get("empresa"),
                        "contacto": lead.get("contacto"),
                        "tipo_seguimiento": lead.get("tipo_seguimiento", "Llamada"),
                        "proximo_seguimiento": proximo
                    })
            except:
                pass
    
    return {
        "stages_count": stages_count,
        "total_pipeline": total_pipeline,
        "leads_without_activity": leads_without_activity,
        "total_leads": len(leads),
        "seguimientos_hoy": seguimientos_hoy
    }

@api_router.get("/leads/export")
async def export_leads(current_user: UserResponse = Depends(get_current_user)):
    """Export leads to CSV"""
    leads = await db.leads.find({}, {"_id": 0}).to_list(1000)
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "empresa", "contacto", "email", "telefono", "cargo", 
        "sector", "valor_estimado", "etapa", "notas"
    ])
    writer.writeheader()
    
    for lead in leads:
        writer.writerow({
            "empresa": lead.get("empresa", ""),
            "contacto": lead.get("contacto", ""),
            "email": lead.get("email", ""),
            "telefono": lead.get("telefono", ""),
            "cargo": lead.get("cargo", ""),
            "sector": lead.get("sector", ""),
            "valor_estimado": lead.get("valor_estimado", 0),
            "etapa": lead.get("etapa", "nuevo"),
            "notas": lead.get("notas", "")
        })
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )

@api_router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get single lead by ID"""
    lead = await db.leads.find_one({"lead_id": lead_id}, {"_id": 0})
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    if isinstance(lead.get("fecha_creacion"), str):
        lead["fecha_creacion"] = datetime.fromisoformat(lead["fecha_creacion"])
    if lead.get("fecha_ultimo_contacto") and isinstance(lead["fecha_ultimo_contacto"], str):
        lead["fecha_ultimo_contacto"] = datetime.fromisoformat(lead["fecha_ultimo_contacto"])
    lead["dias_sin_actividad"] = calculate_days_without_activity(lead.get("fecha_ultimo_contacto"))
    
    # Get propietario name
    if lead.get("propietario"):
        owner = await db.users.find_one({"user_id": lead["propietario"]}, {"_id": 0, "name": 1})
        lead["propietario_nombre"] = owner["name"] if owner else None
    else:
        lead["propietario_nombre"] = None
    
    if not lead.get("servicios"):
        lead["servicios"] = []
    
    return Lead(**lead)

@api_router.post("/leads", response_model=Lead)
async def create_lead(lead: LeadCreate, current_user: UserResponse = Depends(get_current_user)):
    """Create new lead"""
    if lead.etapa not in LEAD_STAGES:
        raise HTTPException(status_code=400, detail=f"Etapa inválida. Usar: {LEAD_STAGES}")
    
    lead_id = f"lead_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    lead_dict = lead.model_dump()
    # Ensure servicios is a list
    if not lead_dict.get("servicios"):
        lead_dict["servicios"] = []
    
    lead_doc = {
        "lead_id": lead_id,
        **lead_dict,
        "fecha_creacion": now.isoformat(),
        "fecha_ultimo_contacto": now.isoformat(),
        "created_by": current_user.user_id
    }
    
    await db.leads.insert_one(lead_doc)
    
    lead_doc["dias_sin_actividad"] = 0
    lead_doc["fecha_creacion"] = now
    lead_doc["fecha_ultimo_contacto"] = now
    
    # Get propietario name
    if lead_doc.get("propietario"):
        owner = await db.users.find_one({"user_id": lead_doc["propietario"]}, {"_id": 0, "name": 1})
        lead_doc["propietario_nombre"] = owner["name"] if owner else None
    else:
        lead_doc["propietario_nombre"] = None
    
    return Lead(**lead_doc)

@api_router.put("/leads/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: str, 
    lead_update: LeadUpdate, 
    current_user: UserResponse = Depends(get_current_user)
):
    """Update lead"""
    existing = await db.leads.find_one({"lead_id": lead_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    update_data = {}
    for k, v in lead_update.model_dump().items():
        if v is not None:
            update_data[k] = v
        elif k == "servicios" and lead_update.servicios is not None:
            update_data[k] = lead_update.servicios  # Allow empty list
    
    if "etapa" in update_data and update_data["etapa"] not in LEAD_STAGES:
        raise HTTPException(status_code=400, detail=f"Etapa inválida. Usar: {LEAD_STAGES}")
    
    if update_data:
        await db.leads.update_one({"lead_id": lead_id}, {"$set": update_data})
    
    updated = await db.leads.find_one({"lead_id": lead_id}, {"_id": 0})
    
    if isinstance(updated.get("fecha_creacion"), str):
        updated["fecha_creacion"] = datetime.fromisoformat(updated["fecha_creacion"])
    if updated.get("fecha_ultimo_contacto") and isinstance(updated["fecha_ultimo_contacto"], str):
        updated["fecha_ultimo_contacto"] = datetime.fromisoformat(updated["fecha_ultimo_contacto"])
    updated["dias_sin_actividad"] = calculate_days_without_activity(updated.get("fecha_ultimo_contacto"))
    
    # Get propietario name
    if updated.get("propietario"):
        owner = await db.users.find_one({"user_id": updated["propietario"]}, {"_id": 0, "name": 1})
        updated["propietario_nombre"] = owner["name"] if owner else None
    else:
        updated["propietario_nombre"] = None
    
    if not updated.get("servicios"):
        updated["servicios"] = []
    
    return Lead(**updated)

@api_router.patch("/leads/{lead_id}/stage")
async def update_lead_stage(
    lead_id: str,
    etapa: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update lead stage (for Kanban drag & drop)"""
    if etapa not in LEAD_STAGES:
        raise HTTPException(status_code=400, detail=f"Etapa inválida. Usar: {LEAD_STAGES}")
    
    result = await db.leads.update_one(
        {"lead_id": lead_id},
        {"$set": {"etapa": etapa}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    return {"message": "Etapa actualizada", "lead_id": lead_id, "etapa": etapa}

@api_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Delete lead"""
    result = await db.leads.delete_one({"lead_id": lead_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    # Delete related activities
    await db.activities.delete_many({"lead_id": lead_id})
    
    return {"message": "Lead eliminado"}

# ============== ACTIVITIES ROUTES ==============

@api_router.get("/leads/{lead_id}/activities", response_model=List[Activity])
async def get_lead_activities(lead_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get activities for a lead"""
    activities = await db.activities.find(
        {"lead_id": lead_id}, 
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    for act in activities:
        if isinstance(act.get("created_at"), str):
            act["created_at"] = datetime.fromisoformat(act["created_at"])
    
    return activities

@api_router.post("/leads/{lead_id}/activities", response_model=Activity)
async def create_activity(
    lead_id: str, 
    activity: ActivityCreate, 
    current_user: UserResponse = Depends(get_current_user)
):
    """Create activity for a lead"""
    lead = await db.leads.find_one({"lead_id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    now = datetime.now(timezone.utc)
    activity_id = f"act_{uuid.uuid4().hex[:12]}"
    
    activity_doc = {
        "activity_id": activity_id,
        "lead_id": lead_id,
        "user_id": current_user.user_id,
        "user_name": current_user.name,
        **activity.model_dump(),
        "created_at": now.isoformat()
    }
    
    await db.activities.insert_one(activity_doc)
    
    # Update lead's last contact date
    await db.leads.update_one(
        {"lead_id": lead_id},
        {"$set": {"fecha_ultimo_contacto": now.isoformat()}}
    )
    
    activity_doc["created_at"] = now
    return Activity(**activity_doc)

# ============== IMPORT/EXPORT ROUTES ==============

@api_router.post("/leads/parse")
async def parse_file(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Parse CSV/Excel file and return headers and preview rows"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo requerido")
    
    content = await file.read()
    headers = []
    rows = []
    
    try:
        if file.filename.endswith('.csv'):
            decoded = content.decode('utf-8')
            reader = csv.reader(io.StringIO(decoded))
            all_rows = list(reader)
            if all_rows:
                headers = all_rows[0]
                rows = all_rows[1:]
        elif file.filename.endswith(('.xlsx', '.xls')):
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(content))
            ws = wb.active
            all_rows = list(ws.iter_rows(values_only=True))
            if all_rows:
                headers = [str(cell) if cell is not None else "" for cell in all_rows[0]]
                rows = [[str(cell) if cell is not None else "" for cell in row] for row in all_rows[1:]]
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use CSV o Excel.")
        
        # Return first 3 rows as preview
        preview = rows[:3] if len(rows) >= 3 else rows
        
        return {
            "headers": headers,
            "rows": rows,
            "preview": preview,
            "total_rows": len(rows)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando archivo: {str(e)}")


class DuplicateCheckRequest(BaseModel):
    leads: List[dict]


@api_router.post("/leads/check-duplicates")
async def check_duplicates(
    data: DuplicateCheckRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Check for duplicate leads by email or company name"""
    duplicates = []
    
    # Get all existing leads
    existing_leads = await db.leads.find({}, {"_id": 0}).to_list(10000)
    existing_emails = {lead.get("email", "").lower(): lead for lead in existing_leads}
    existing_companies = {}
    for lead in existing_leads:
        empresa = lead.get("empresa", "").lower().strip()
        if empresa:
            if empresa not in existing_companies:
                existing_companies[empresa] = []
            existing_companies[empresa].append(lead)
    
    for idx, new_lead in enumerate(data.leads):
        email = str(new_lead.get("email", "")).lower().strip()
        empresa = str(new_lead.get("empresa", "")).lower().strip()
        
        # Check exact email match
        if email and email in existing_emails:
            duplicates.append({
                "rowIndex": idx,
                "type": "exact",
                "newLead": new_lead,
                "existingLead": existing_emails[email]
            })
        # Check company name match (different email)
        elif empresa and empresa in existing_companies:
            # Only mark as possible duplicate if different email
            for existing in existing_companies[empresa]:
                if existing.get("email", "").lower() != email:
                    duplicates.append({
                        "rowIndex": idx,
                        "type": "possible",
                        "newLead": new_lead,
                        "existingLead": existing
                    })
                    break
    
    return {"duplicates": duplicates}


class ImportMappedRequest(BaseModel):
    leads: List[dict]
    mapping: dict


@api_router.post("/leads/import-mapped")
async def import_mapped_leads(
    data: ImportMappedRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Import leads with custom column mapping and duplicate handling"""
    imported = 0
    updated = 0
    skipped = 0
    errors = []
    
    for idx, lead_data in enumerate(data.leads):
        try:
            action = lead_data.pop("_action", "import")
            existing_id = lead_data.pop("_existingId", None)
            
            if action == "skip":
                skipped += 1
                continue
            
            # Clean and validate data
            lead_doc = {
                "empresa": str(lead_data.get("empresa", "")).strip() or "Sin empresa",
                "contacto": str(lead_data.get("contacto", "")).strip() or "Sin contacto",
                "email": str(lead_data.get("email", "")).strip().lower(),
                "telefono": str(lead_data.get("telefono", "")).strip() if lead_data.get("telefono") else None,
                "cargo": str(lead_data.get("cargo", "")).strip() if lead_data.get("cargo") else None,
                "sector": str(lead_data.get("sector", "")).strip() if lead_data.get("sector") else None,
                "fuente": str(lead_data.get("fuente", "")).strip() if lead_data.get("fuente") else None,
                "notas": str(lead_data.get("notas", "")).strip() if lead_data.get("notas") else None,
            }
            
            # Handle numeric value
            try:
                valor = lead_data.get("valor_estimado", "0")
                # Remove currency symbols and commas
                if isinstance(valor, str):
                    valor = valor.replace("€", "").replace("$", "").replace(",", ".").strip()
                lead_doc["valor_estimado"] = float(valor) if valor else 0.0
            except:
                lead_doc["valor_estimado"] = 0.0
            
            # Handle etapa
            etapa = str(lead_data.get("etapa", "nuevo")).strip().lower()
            lead_doc["etapa"] = etapa if etapa in LEAD_STAGES else "nuevo"
            
            if action == "update" and existing_id:
                # Update existing lead
                await db.leads.update_one(
                    {"lead_id": existing_id},
                    {"$set": lead_doc}
                )
                updated += 1
            else:
                # Create new lead
                lead_id = f"lead_{uuid.uuid4().hex[:12]}"
                now = datetime.now(timezone.utc)
                lead_doc.update({
                    "lead_id": lead_id,
                    "fecha_creacion": now.isoformat(),
                    "fecha_ultimo_contacto": now.isoformat(),
                    "created_by": current_user.user_id,
                    "servicios": [],
                    "urgencia": "Sin definir",
                })
                await db.leads.insert_one(lead_doc)
                imported += 1
                
        except Exception as e:
            errors.append(f"Fila {idx + 2}: {str(e)}")
    
    return {
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:10] if errors else []
    }


@api_router.post("/leads/import")
async def import_leads(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Import leads from CSV/Excel (legacy endpoint)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo requerido")
    
    content = await file.read()
    imported = 0
    errors = []
    
    try:
        if file.filename.endswith('.csv'):
            decoded = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            rows = list(reader)
        elif file.filename.endswith(('.xlsx', '.xls')):
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(content))
            ws = wb.active
            headers = [cell.value for cell in ws[1]]
            rows = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                rows.append(dict(zip(headers, row)))
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use CSV o Excel.")
        
        for idx, row in enumerate(rows):
            try:
                lead_id = f"lead_{uuid.uuid4().hex[:12]}"
                now = datetime.now(timezone.utc)
                
                lead_doc = {
                    "lead_id": lead_id,
                    "empresa": str(row.get("empresa", "")).strip() or "Sin empresa",
                    "contacto": str(row.get("contacto", "")).strip() or "Sin contacto",
                    "email": str(row.get("email", "")).strip().lower() or f"sin_email_{idx}@temp.com",
                    "telefono": str(row.get("telefono", "")).strip() if row.get("telefono") else None,
                    "cargo": str(row.get("cargo", "")).strip() if row.get("cargo") else None,
                    "sector": str(row.get("sector", "")).strip() if row.get("sector") else None,
                    "valor_estimado": float(row.get("valor_estimado", 0) or 0),
                    "etapa": str(row.get("etapa", "nuevo")).strip().lower() or "nuevo",
                    "notas": str(row.get("notas", "")).strip() if row.get("notas") else None,
                    "fecha_creacion": now.isoformat(),
                    "fecha_ultimo_contacto": now.isoformat(),
                    "created_by": current_user.user_id
                }
                
                if lead_doc["etapa"] not in LEAD_STAGES:
                    lead_doc["etapa"] = "nuevo"
                
                await db.leads.insert_one(lead_doc)
                imported += 1
            except Exception as e:
                errors.append(f"Fila {idx + 2}: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando archivo: {str(e)}")
    
    return {
        "message": f"{imported} leads importados",
        "imported": imported,
        "errors": errors[:10] if errors else []
    }

# ============== BULK OPERATIONS ==============

class BulkUpdateRequest(BaseModel):
    lead_ids: List[str]
    etapa: Optional[str] = None
    propietario: Optional[str] = None


@api_router.post("/leads/bulk-update")
async def bulk_update_leads(
    data: BulkUpdateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Bulk update leads stage or owner"""
    update_fields = {}
    
    if data.etapa:
        if data.etapa not in LEAD_STAGES:
            raise HTTPException(status_code=400, detail=f"Etapa inválida")
        update_fields["etapa"] = data.etapa
    
    if data.propietario is not None:
        update_fields["propietario"] = data.propietario if data.propietario else None
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    result = await db.leads.update_many(
        {"lead_id": {"$in": data.lead_ids}},
        {"$set": update_fields}
    )
    
    return {"updated": result.modified_count}


class BulkDeleteRequest(BaseModel):
    lead_ids: List[str]


@api_router.post("/leads/bulk-delete")
async def bulk_delete_leads(
    data: BulkDeleteRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Bulk delete leads"""
    result = await db.leads.delete_many({"lead_id": {"$in": data.lead_ids}})
    
    # Also delete related activities
    await db.activities.delete_many({"lead_id": {"$in": data.lead_ids}})
    
    return {"deleted": result.deleted_count}


@api_router.delete("/leads/delete-all")
async def delete_all_leads(
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete all leads (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar todos los leads")
    
    result = await db.leads.delete_many({})
    await db.activities.delete_many({})
    
    return {"deleted": result.deleted_count}


# ============== ENRICH API (for Apollo.io) ==============

@api_router.post("/leads/enrich")
async def enrich_lead(data: EnrichRequest):
    """
    API endpoint for external enrichment services like Apollo.io
    Receives email and updates the lead with additional data
    """
    lead = await db.leads.find_one({"email": data.email.lower()}, {"_id": 0})
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado con ese email")
    
    update_data = {}
    if data.empresa:
        update_data["empresa"] = data.empresa
    if data.contacto:
        update_data["contacto"] = data.contacto
    if data.telefono:
        update_data["telefono"] = data.telefono
    if data.cargo:
        update_data["cargo"] = data.cargo
    if data.sector:
        update_data["sector"] = data.sector
    
    if update_data:
        await db.leads.update_one(
            {"email": data.email.lower()},
            {"$set": update_data}
        )
    
    return {"message": "Lead enriquecido", "email": data.email, "updated_fields": list(update_data.keys())}

# ============== SECTORS ==============

@api_router.get("/sectors")
async def get_sectors(current_user: UserResponse = Depends(get_current_user)):
    """Get all unique sectors from leads"""
    sectors = await db.leads.distinct("sector")
    return [s for s in sectors if s]

# ============== OPTIONS (Dropdowns) ==============

@api_router.get("/options")
async def get_options(current_user: UserResponse = Depends(get_current_user)):
    """Get all dropdown options"""
    return {
        "sectores": SECTORES,
        "servicios": SERVICIOS,
        "fuentes": FUENTES,
        "urgencias": URGENCIAS,
        "motivos_perdida": MOTIVOS_PERDIDA,
        "tipos_seguimiento": TIPOS_SEGUIMIENTO,
        "etapas": LEAD_STAGES
    }

# ============== REPORTS ==============

@api_router.get("/reports")
async def get_reports(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all reports data with optional date filter"""
    
    # Build date filter
    query = {}
    if fecha_inicio and fecha_fin:
        query["fecha_creacion"] = {
            "$gte": fecha_inicio,
            "$lte": fecha_fin + "T23:59:59"
        }
    
    leads = await db.leads.find(query, {"_id": 0}).to_list(10000)
    users = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1}).to_list(100)
    users_map = {u["user_id"]: u["name"] for u in users}
    
    # 1. Pipeline por etapa
    pipeline_por_etapa = {}
    for stage in LEAD_STAGES:
        stage_leads = [l for l in leads if l.get("etapa") == stage]
        pipeline_por_etapa[stage] = {
            "cantidad": len(stage_leads),
            "valor": sum(l.get("valor_estimado", 0) for l in stage_leads)
        }
    
    # 2. Leads por fuente
    leads_por_fuente = {}
    for lead in leads:
        fuente = lead.get("fuente") or "Sin definir"
        leads_por_fuente[fuente] = leads_por_fuente.get(fuente, 0) + 1
    
    # 3. Leads por sector
    leads_por_sector = {}
    for lead in leads:
        sector = lead.get("sector") or "Sin definir"
        leads_por_sector[sector] = leads_por_sector.get(sector, 0) + 1
    
    # 4. Servicios más demandados
    servicios_demandados = {}
    for lead in leads:
        servicios = lead.get("servicios") or []
        for servicio in servicios:
            servicios_demandados[servicio] = servicios_demandados.get(servicio, 0) + 1
    
    # 5. Leads por propietario
    leads_por_propietario = {}
    for lead in leads:
        prop_id = lead.get("propietario")
        prop_name = users_map.get(prop_id, "Sin asignar") if prop_id else "Sin asignar"
        if prop_name not in leads_por_propietario:
            leads_por_propietario[prop_name] = {"cantidad": 0, "valor": 0}
        leads_por_propietario[prop_name]["cantidad"] += 1
        leads_por_propietario[prop_name]["valor"] += lead.get("valor_estimado", 0)
    
    # 6. Motivos de pérdida
    motivos_perdida = {}
    for lead in leads:
        if lead.get("etapa") == "perdido":
            motivo = lead.get("motivo_perdida") or "Sin especificar"
            motivos_perdida[motivo] = motivos_perdida.get(motivo, 0) + 1
    
    return {
        "pipeline_por_etapa": pipeline_por_etapa,
        "leads_por_fuente": leads_por_fuente,
        "leads_por_sector": leads_por_sector,
        "servicios_demandados": servicios_demandados,
        "leads_por_propietario": leads_por_propietario,
        "motivos_perdida": motivos_perdida,
        "total_leads": len(leads)
    }

@api_router.get("/reports/export/{report_type}")
async def export_report(
    report_type: str,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Export report data to CSV"""
    
    # Build date filter
    query = {}
    if fecha_inicio and fecha_fin:
        query["fecha_creacion"] = {
            "$gte": fecha_inicio,
            "$lte": fecha_fin + "T23:59:59"
        }
    
    leads = await db.leads.find(query, {"_id": 0}).to_list(10000)
    users = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1}).to_list(100)
    users_map = {u["user_id"]: u["name"] for u in users}
    
    output = io.StringIO()
    
    if report_type == "pipeline":
        writer = csv.writer(output)
        writer.writerow(["Etapa", "Cantidad", "Valor EUR"])
        for stage in LEAD_STAGES:
            stage_leads = [l for l in leads if l.get("etapa") == stage]
            cantidad = len(stage_leads)
            valor = sum(l.get("valor_estimado", 0) for l in stage_leads)
            writer.writerow([stage.capitalize(), cantidad, valor])
    
    elif report_type == "fuentes":
        writer = csv.writer(output)
        writer.writerow(["Fuente", "Cantidad"])
        fuentes = {}
        for lead in leads:
            fuente = lead.get("fuente") or "Sin definir"
            fuentes[fuente] = fuentes.get(fuente, 0) + 1
        for fuente, cantidad in sorted(fuentes.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([fuente, cantidad])
    
    elif report_type == "sectores":
        writer = csv.writer(output)
        writer.writerow(["Sector", "Cantidad"])
        sectores = {}
        for lead in leads:
            sector = lead.get("sector") or "Sin definir"
            sectores[sector] = sectores.get(sector, 0) + 1
        for sector, cantidad in sorted(sectores.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([sector, cantidad])
    
    elif report_type == "servicios":
        writer = csv.writer(output)
        writer.writerow(["Servicio", "Leads Interesados"])
        servicios = {}
        for lead in leads:
            for servicio in (lead.get("servicios") or []):
                servicios[servicio] = servicios.get(servicio, 0) + 1
        for servicio, cantidad in sorted(servicios.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([servicio, cantidad])
    
    elif report_type == "propietarios":
        writer = csv.writer(output)
        writer.writerow(["Propietario", "Cantidad Leads", "Valor EUR"])
        propietarios = {}
        for lead in leads:
            prop_id = lead.get("propietario")
            prop_name = users_map.get(prop_id, "Sin asignar") if prop_id else "Sin asignar"
            if prop_name not in propietarios:
                propietarios[prop_name] = {"cantidad": 0, "valor": 0}
            propietarios[prop_name]["cantidad"] += 1
            propietarios[prop_name]["valor"] += lead.get("valor_estimado", 0)
        for prop, data in sorted(propietarios.items(), key=lambda x: x[1]["valor"], reverse=True):
            writer.writerow([prop, data["cantidad"], data["valor"]])
    
    elif report_type == "perdidas":
        writer = csv.writer(output)
        writer.writerow(["Motivo", "Cantidad"])
        motivos = {}
        for lead in leads:
            if lead.get("etapa") == "perdido":
                motivo = lead.get("motivo_perdida") or "Sin especificar"
                motivos[motivo] = motivos.get(motivo, 0) + 1
        for motivo, cantidad in sorted(motivos.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([motivo, cantidad])
    
    else:
        raise HTTPException(status_code=400, detail="Tipo de reporte no válido")
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reporte_{report_type}.csv"}
    )

# ============== USERS (Admin Panel) ==============

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: UserResponse = Depends(get_current_user)):
    """Get all users (for propietario dropdown and admin panel)"""
    users = await db.users.find({}, {"_id": 0}).to_list(100)
    return users

@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: UserResponse = Depends(get_current_user)):
    """Create new user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear usuarios")
    
    # Check if email already exists
    existing = await db.users.find_one({"email": user.email.lower()}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    new_user = {
        "user_id": user_id,
        "email": user.email.lower(),
        "name": user.name,
        "picture": None,
        "role": user.role,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(new_user)
    return UserResponse(**new_user)

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, current_user: UserResponse = Depends(get_current_user)):
    """Update user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden editar usuarios")
    
    existing = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    
    if update_data:
        await db.users.update_one({"user_id": user_id}, {"$set": update_data})
    
    updated = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return UserResponse(**updated)

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Delete user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar usuarios")
    
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    
    result = await db.users.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Also delete user sessions
    await db.user_sessions.delete_many({"user_id": user_id})
    
    return {"message": "Usuario eliminado"}

# ============== ROOT ==============

@api_router.get("/")
async def root():
    return {"message": "System Rapid Solutions CRM API", "version": "1.1.0"}

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
