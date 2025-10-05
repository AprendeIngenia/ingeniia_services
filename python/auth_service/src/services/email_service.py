# src/services/email_service.py
import httpx
from src.core.config import settings

SENDGRID_API = "https://api.sendgrid.com/v3/mail/send"

async def send_verification_email(to_email: str, username: str, verification_url: str, verification_token: str):
    payload = {
      "from": {
        "email": settings.FROM_EMAIL.split('<')[-1].strip('> '),
        "name": (settings.FROM_EMAIL.split('<')[0].strip() if '<' in settings.FROM_EMAIL else "Ingeniia")
      },
      "personalizations": [{
        "to": [{"email": to_email}],
        "dynamic_template_data": {
          "username": username,
          "verification_url": verification_url,
          "verification_token": verification_token
        }
      }],
      "template_id": settings.VERIFICATION_EMAIL_TEMPLATE_ID
    }
    headers = {"Authorization": f"Bearer {settings.SENDGRID_API_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=8) as client:
      r = await client.post(SENDGRID_API, json=payload, headers=headers)
      if r.status_code >= 300:
        raise RuntimeError(f"SendGrid error {r.status_code}: {r.text}")