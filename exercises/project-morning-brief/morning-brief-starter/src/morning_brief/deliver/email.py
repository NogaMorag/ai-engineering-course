"""Email delivery over SMTP (Gmail: smtp.gmail.com, port 465, an app password). Secrets come from Settings, never from code."""
from __future__ import annotations
import smtplib
from email.message import EmailMessage
from morning_brief.config import Settings

def build_message(settings: Settings, subject: str, markdown: str, html: str) -> EmailMessage:
    raise NotImplementedError

def send_email(settings: Settings, subject: str, markdown: str, html: str, *, smtp_factory=smtplib.SMTP_SSL) -> str:
    raise NotImplementedError
