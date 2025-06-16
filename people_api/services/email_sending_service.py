"""Service to send e-mails to members using smtplib."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from people_api.settings import get_smtp_settings


class EmailSendingService:
    """Service to send e-mails to members using smtplib."""

    def send_email(self, to_email: str, subject: str, html_content: str, sender_email: str):
        """Sends an email with the provided HTML content and sender."""

        settings = get_smtp_settings()

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(sender_email, to_email, msg.as_string())

        logging.info("Email sent successfully from %s to %s", sender_email, to_email)
