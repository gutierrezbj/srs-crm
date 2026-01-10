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

# Allowed users
ALLOWED_USERS = {
    "juancho@systemrapidsolutions.com": {"name": "JuanCho", "role": "admin"},
    "andros@systemrapidsolutions.com": {"name": "Andros", "role": "user"},
    "adriana@systemrapidsolutions.com": {"name": "Adriana", "role": "user"},
}

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

class Lead(LeadBase):
    model_config = ConfigDict(extra="ignore")
    lead_id: str
    fecha_creacion: datetime
    fecha_ultimo_contacto: Optional[datetime] = None
    dias_sin_actividad: int = 0
    created_by: str

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
    
    # Create or update user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"email": email},
            {"$set": {
                "name": auth_data.get("name", allowed_user["name"]),
                "picture": auth_data.get("picture"),
                "role": allowed_user["role"]
            }}
        )
    else:
        new_user = {
            "user_id": user_id,
            "email": email,
            "name": auth_data.get("name", allowed_user["name"]),
            "picture": auth_data.get("picture"),
            "role": allowed_user["role"],
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
    search: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all leads with optional filters"""
    query = {}
    
    if etapa:
        query["etapa"] = etapa
    if sector:
        query["sector"] = sector
    if search:
        query["$or"] = [
            {"empresa": {"$regex": search, "$options": "i"}},
            {"contacto": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    leads = await db.leads.find(query, {"_id": 0}).sort("fecha_creacion", -1).to_list(1000)
    
    for lead in leads:
        if isinstance(lead.get("fecha_creacion"), str):
            lead["fecha_creacion"] = datetime.fromisoformat(lead["fecha_creacion"])
        if lead.get("fecha_ultimo_contacto") and isinstance(lead["fecha_ultimo_contacto"], str):
            lead["fecha_ultimo_contacto"] = datetime.fromisoformat(lead["fecha_ultimo_contacto"])
        lead["dias_sin_actividad"] = calculate_days_without_activity(lead.get("fecha_ultimo_contacto"))
    
    return leads

@api_router.get("/leads/stats")
async def get_leads_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get dashboard statistics"""
    leads = await db.leads.find({}, {"_id": 0}).to_list(1000)
    
    # Count by stage
    stages_count = {stage: 0 for stage in LEAD_STAGES}
    total_pipeline = 0.0
    leads_without_activity = 0
    
    for lead in leads:
        etapa = lead.get("etapa", "nuevo")
        stages_count[etapa] = stages_count.get(etapa, 0) + 1
        
        if etapa not in ["ganado", "perdido"]:
            total_pipeline += lead.get("valor_estimado", 0)
        
        dias = calculate_days_without_activity(lead.get("fecha_ultimo_contacto"))
        if dias > 7 and etapa not in ["ganado", "perdido"]:
            leads_without_activity += 1
    
    return {
        "stages_count": stages_count,
        "total_pipeline": total_pipeline,
        "leads_without_activity": leads_without_activity,
        "total_leads": len(leads)
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
    
    return Lead(**lead)

@api_router.post("/leads", response_model=Lead)
async def create_lead(lead: LeadCreate, current_user: UserResponse = Depends(get_current_user)):
    """Create new lead"""
    if lead.etapa not in LEAD_STAGES:
        raise HTTPException(status_code=400, detail=f"Etapa inválida. Usar: {LEAD_STAGES}")
    
    lead_id = f"lead_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    lead_doc = {
        "lead_id": lead_id,
        **lead.model_dump(),
        "fecha_creacion": now.isoformat(),
        "fecha_ultimo_contacto": now.isoformat(),
        "created_by": current_user.user_id
    }
    
    await db.leads.insert_one(lead_doc)
    
    lead_doc["dias_sin_actividad"] = 0
    lead_doc["fecha_creacion"] = now
    lead_doc["fecha_ultimo_contacto"] = now
    
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
    
    update_data = {k: v for k, v in lead_update.model_dump().items() if v is not None}
    
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

@api_router.post("/leads/import")
async def import_leads(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Import leads from CSV/Excel"""
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

# ============== ROOT ==============

@api_router.get("/")
async def root():
    return {"message": "System Rapid Solutions CRM API", "version": "1.0.0"}

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
