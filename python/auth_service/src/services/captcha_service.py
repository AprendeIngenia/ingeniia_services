# src/services/captcha_service.py
import httpx
import logging as log
from src.core.config import settings

async def verify_recaptcha(token: str, remote_ip: str | None = None) -> bool:
    """Valida reCAPTCHA v3 (score) y v2 Invisible (success)."""
    if settings.ENVIRONMENT == "development":
        log.info("reCAPTCHA bypass en desarrollo")
        return True

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                settings.RECAPTCHA_VERIFY_URL,
                data={"secret": settings.RECAPTCHA_SECRET_KEY, "response": token, "remoteip": remote_ip},
            )
            data = resp.json()
    except Exception as e:
        log.error(f"Error verificando reCAPTCHA: {e}")
        return False

    if not data.get("success"):
        log.warning(f"reCAPTCHA failed: {data.get('error-codes')}")
        return False

    # v3 trae score; v2 Invisible no
    if "score" in data:
        score = float(data.get("score", 0))
        if score < float(settings.RECAPTCHA_MIN_SCORE):
            log.warning(f"reCAPTCHA score too low: {score}")
            return False

    return True
