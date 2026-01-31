"""Cliente para descargar feeds PLACSP."""
import httpx
from typing import Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class FeedClient:
    """Cliente HTTP para feeds PLACSP con soporte de certificados SSL."""
    
    def __init__(self, use_cert: bool = True):
        """
        Inicializar cliente de feed.
        
        Args:
            use_cert: Si True, usa certificados SSL para autenticación
        
        Raises:
            FileNotFoundError: Si use_cert=True y los certificados no existen
        """
        self.use_cert = use_cert
        
        # Usar variable de entorno CERT_DIR con fallbacks inteligentes
        cert_dir = os.getenv("CERT_DIR")
        if not cert_dir:
            # Intentar detectar el directorio de certificados
            possible_paths = [
                "/app/certs",  # Docker
                "/opt/apps/srs-crm/backend/certs",  # VPS new path
                "/var/www/srs-crm/backend/certs",  # VPS old path
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    cert_dir = path
                    logger.info(f"Auto-detected certificate directory: {cert_dir}")
                    break
            
            if not cert_dir:
                cert_dir = "/app/certs"  # Default para Docker
        
        self.cert_path = os.path.join(cert_dir, "client_cert.pem")
        self.key_path = os.path.join(cert_dir, "client_key_nopass.pem")
        self.timeout = 60.0
        
        # Validar existencia de certificados si se requieren
        if self.use_cert:
            if not os.path.exists(self.cert_path):
                raise FileNotFoundError(
                    f"Certificate not found: {self.cert_path}\n"
                    f"Please ensure certificates are mounted/available at this location.\n"
                    f"Set CERT_DIR environment variable to override."
                )
            if not os.path.exists(self.key_path):
                raise FileNotFoundError(
                    f"Private key not found: {self.key_path}\n"
                    f"Please ensure certificates are mounted/available at this location.\n"
                    f"Set CERT_DIR environment variable to override."
                )
            logger.info(f"✅ SSL certificates validated: {cert_dir}")
    
    async def fetch_feed(self, url: str) -> Optional[str]:
        """
        Descargar feed XML desde URL de forma asíncrona.
        
        Args:
            url: URL del feed PLACSP
            
        Returns:
            Contenido XML del feed o None si hay error
        """
        cert = None
        if self.use_cert:
            cert = (self.cert_path, self.key_path)
            
        try:
            # ✅ FIX: Cliente configurado correctamente desde el constructor
            async with httpx.AsyncClient(
                timeout=self.timeout,
                verify=True,
                cert=cert
            ) as client:
                logger.info(f"Downloading feed from: {url}")
                logger.debug(f"Using certificates: {self.use_cert}")
                
                response = await client.get(url)
                response.raise_for_status()
                
                logger.info(f"✅ Feed downloaded successfully: {len(response.text)} bytes")
                return response.text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error {e.response.status_code}: {url}")
            logger.error(f"Response body (first 500 chars): {e.response.text[:500]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Connection error: {e}")
            logger.error(f"Certificate paths - cert: {self.cert_path}, key: {self.key_path}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading feed: {e}")
            return None
    
    def fetch_feed_sync(self, url: str) -> Optional[str]:
        """
        Versión síncrona para testing y scripts.
        
        Args:
            url: URL del feed PLACSP
            
        Returns:
            Contenido XML del feed o None si hay error
        """
        cert = None
        if self.use_cert:
            cert = (self.cert_path, self.key_path)
            
        try:
            # ✅ Cliente síncrono configurado correctamente
            with httpx.Client(
                timeout=self.timeout,
                verify=True,
                cert=cert
            ) as client:
                logger.info(f"Downloading feed (sync) from: {url}")
                
                response = client.get(url)
                response.raise_for_status()
                
                logger.info(f"✅ Feed downloaded successfully: {len(response.text)} bytes")
                return response.text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error {e.response.status_code}: {url}")
            logger.error(f"Response body (first 500 chars): {e.response.text[:500]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Connection error: {e}")
            logger.error(f"Certificate paths - cert: {self.cert_path}, key: {self.key_path}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
