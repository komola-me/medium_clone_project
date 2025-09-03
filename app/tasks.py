import smtplib
from datetime import datetime, timedelta, UTC
from email.mime.text import MIMEText
from celery import Celery

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, EMAIL_USERNAME, EMAIL_FROM, EMAIL_PASSWORD, SMTP_PORT, SMTP_SERVER

celery = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

@celery.task
def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email {to_email}: {e}")