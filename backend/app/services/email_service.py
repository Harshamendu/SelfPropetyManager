import logging
from email.mime.text import MIMEText

import aiosmtplib

from app.config import settings

logger = logging.getLogger(__name__)


async def send_reminder_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email using aiosmtplib. Returns True on success, False on failure."""
    if not settings.smtp_user or not settings.smtp_from_email:
        logger.warning("SMTP not configured. Skipping email to %s", to_email)
        return False

    try:
        message = MIMEText(body, "plain", "utf-8")
        message["From"] = settings.smtp_from_email
        message["To"] = to_email
        message["Subject"] = subject

        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=settings.smtp_use_tls,
        )
        logger.info("Email sent successfully to %s", to_email)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False
