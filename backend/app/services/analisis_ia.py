"""Análisis IA de pliegos técnicos."""
import os
import httpx
from typing import Optional, Dict
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """Eres un experto en análisis de pliegos de contratación pública española.
Analiza el siguiente contenido y extrae:
1. Pain Score (0-100): Qué tan urgente/doloroso es el problema que quiere resolver el cliente
2. Resumen ejecutivo (2-3 frases)
3. Puntos de dolor del cliente (lista)
4. Requisitos técnicos clave (lista)
5. Recomendación estratégica para SRS

Responde en JSON con esta estructura:
{
  "pain_score": número,
  "resumen": "texto",
  "puntos_dolor": ["punto1", "punto2"],
  "requisitos_clave": ["req1", "req2"],
  "recomendacion": "texto"
}"""

async def analizar_con_openai(texto: str) -> Optional[Dict]:
    """Analizar texto con OpenAI GPT-4."""
    if not OPENAI_API_KEY:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Analiza este pliego:\n\n{texto[:8000]}"}
                    ],
                    "response_format": {"type": "json_object"}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                import json
                return json.loads(content)
    except Exception as e:
        print(f"Error OpenAI: {e}")
    
    return None

async def analizar_con_gemini(texto: str) -> Optional[Dict]:
    """Analizar texto con Google Gemini."""
    if not GEMINI_API_KEY:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{
                            "text": f"{SYSTEM_PROMPT}\n\nPliego a analizar:\n{texto[:8000]}"
                        }]
                    }],
                    "generationConfig": {
                        "responseMimeType": "application/json"
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                import json
                return json.loads(content)
    except Exception as e:
        print(f"Error Gemini: {e}")
    
    return None

async def analizar_pliego(texto: str, provider: str = "auto") -> Dict:
    """
    Analizar pliego con IA.
    
    Args:
        texto: Contenido del pliego
        provider: "openai", "gemini", o "auto" (intenta ambos)
    
    Returns:
        Resultado del análisis
    """
    resultado = None
    provider_usado = None
    
    if provider in ["openai", "auto"]:
        resultado = await analizar_con_openai(texto)
        if resultado:
            provider_usado = "openai"
    
    if not resultado and provider in ["gemini", "auto"]:
        resultado = await analizar_con_gemini(texto)
        if resultado:
            provider_usado = "gemini"
    
    if not resultado:
        return {
            "procesado": False,
            "error": "No se pudo procesar con ningún proveedor de IA"
        }
    
    return {
        "procesado": True,
        "procesado_at": datetime.now(timezone.utc),
        "provider": provider_usado,
        "pain_score": resultado.get("pain_score"),
        "resumen": resultado.get("resumen"),
        "puntos_dolor": resultado.get("puntos_dolor", []),
        "requisitos_clave": resultado.get("requisitos_clave", []),
        "recomendacion": resultado.get("recomendacion")
    }

async def extraer_texto_pliego(url: str) -> Optional[str]:
    """Descargar y extraer texto de un pliego (PDF/HTML)."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return None
            
            content_type = response.headers.get("content-type", "")
            
            if "pdf" in content_type:
                return None
            elif "html" in content_type or "text" in content_type:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                return soup.get_text(separator=" ", strip=True)
            
    except Exception as e:
        print(f"Error extrayendo pliego: {e}")
    
    return None
