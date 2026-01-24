"""Cliente para descargar feeds PLACSP."""
import httpx
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class FeedClient:
    """Cliente HTTP para feeds PLACSP."""
    
    def __init__(self, use_cert: bool = False):
        self.use_cert = use_cert
        self.cert_path = os.getenv("PLACSP_CERT_PATH", "./certs/client_cert.pem")
        self.key_path = os.getenv("PLACSP_KEY_PATH", "./certs/client_key_nopass.pem")
        self.timeout = 60.0
    
    async def fetch_feed(self, url: str) -> Optional[str]:
        """Descargar feed XML desde URL."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=True) as client:
                if self.use_cert and os.path.exists(self.cert_path):
                    client = httpx.AsyncClient(
                        timeout=self.timeout,
                        cert=(self.cert_path, self.key_path)
                    )
                
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except httpx.HTTPStatusError as e:
            print(f"Error HTTP {e.response.status_code}: {url}")
            return None
        except httpx.RequestError as e:
            print(f"Error de conexión: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None
    
    def fetch_feed_sync(self, url: str) -> Optional[str]:
        """Versión síncrona para testing."""
        try:
            with httpx.Client(timeout=self.timeout, verify=True) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"Error: {e}")
            return None
