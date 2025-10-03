# src/services/email_service.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging as log
from src.core.config import settings

async def send_verification_email(email: str, username: str, token: str):
    """Envía email de verificación usando SendGrid"""
    try:
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=email,
        )
        
        message.template_id = settings.VERIFICATION_EMAIL_TEMPLATE_ID
        message.dynamic_template_data = {
            'username': username,
            'verify_url': verify_url,
            'company_name': 'inGeniia'
        }
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        log.info(f"Email enviado a {email}: status {response.status_code}")
        return True
    except Exception as e:
        log.error(f"Error enviando email: {e}")
        return False