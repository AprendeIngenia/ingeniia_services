# src/services/captcha_service.py
import httpx
import logging as log
from src.core.config import settings


async def verify_recaptcha(token: str, remote_ip: str = None) -> bool:
    """Verifica token de reCAPTCHA con Google"""
    
    if settings.ENVIRONMENT == "development":
        log.info("Saltando verificación de reCAPTCHA en modo de desarrollo.")
        return True
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.RECAPTCHA_VERIFY_URL,
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token,
                    "remoteip": remote_ip
                }
            )
            result = response.json()
            
            if not result.get("success"):
                log.warning(f"reCAPTCHA failed: {result.get('error-codes')}")
                return False
            
            # Para reCAPTCHA v3, verificar score
            score = result.get("score", 0)
            if score < settings.RECAPTCHA_MIN_SCORE:
                log.warning(f"reCAPTCHA score too low: {score}")
                return False
            
            return True
    except Exception as e:
        log.error(f"Error verificando reCAPTCHA: {e}")
        return False