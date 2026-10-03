"""Email delivery over SMTP (Gmail: smtp.gmail.com, port 465, an app password). Secrets come from Settings, never from code."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from morning_brief.config import Settings


def build_message(settings: Settings, subject: str, markdown: str, html: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_user
    message["To"] = settings.mail_to
    message.set_content(markdown)
    message.add_alternative(html, subtype="html")
    return message


def send_email(settings: Settings, subject: str, markdown: str, html: str, *, smtp_factory=smtplib.SMTP_SSL) -> str:
    if not settings.email_configured:
        raise RuntimeError("email is not configured (SMTP_HOST, SMTP_USER, SMTP_PASSWORD, MAIL_TO)")
    message = build_message(settings, subject, markdown, html)
    with smtp_factory(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)
    return f"sent to {settings.mail_to}"
