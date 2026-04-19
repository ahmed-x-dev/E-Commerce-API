# app/utils/email.py
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str):
    try:
        httpx.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": settings.brevo_api_key,
                "Content-Type": "application/json"
            },
            json={
                "sender": {
                    "name": "E-Commerce App",
                    "email": settings.mail_from
                },
                "to": [{"email": to}],
                "subject": subject,
                "htmlContent": f"<p>{body}</p>"
            }
        )
        logger.info(f"Email sent to {to} with subject '{subject}'")
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")