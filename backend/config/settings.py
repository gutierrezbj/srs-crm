from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # MongoDB
    mongo_url: str
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    
    # PLACSP
    placsp_cert_path: str = "./certs/client_cert.pem"
    placsp_key_path: str = "./certs/client_key_nopass.pem"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
