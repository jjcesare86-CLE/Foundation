"""
PHP Shield -- email via Resend (the provider already used across Automaition Nation).

`Mailer` posts to the Resend REST API. `OutboxMailer` records messages instead of
sending them (tests, and local dev when RESEND_API_KEY is unset).
"""
import base64
import logging
from typing import Optional

import requests

from app.php_shield import config

log = logging.getLogger("php_shield")
RESEND_URL = "https://api.resend.com/emails"


class MailError(RuntimeError):
    pass


class Mailer:
    def __init__(self, api_key: str, from_email: Optional[str] = None, post=requests.post):
        self.api_key, self.from_email, self._post = api_key, from_email or config.from_email(), post

    def send(self, to, subject: str, html: str, attachments: Optional[list] = None, reply_to: Optional[str] = None) -> None:
        payload = {"from": self.from_email, "to": [to] if isinstance(to, str) else list(to), "subject": subject, "html": html}
        if reply_to:
            payload["reply_to"] = reply_to
        if attachments:
            payload["attachments"] = [
                {"filename": a["filename"], "content": base64.b64encode(a["content"]).decode()} for a in attachments
            ]
        resp = self._post(RESEND_URL, json=payload, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=15)
        if resp.status_code >= 300:
            raise MailError(f"Resend {resp.status_code}: {resp.text[:200]}")


class OutboxMailer:
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, to, subject: str, html: str, attachments: Optional[list] = None, reply_to: Optional[str] = None) -> None:
        self.sent.append({"to": [to] if isinstance(to, str) else list(to), "subject": subject, "html": html,
                          "attachments": attachments or []})
        log.info("[outbox] to=%s subject=%s", to, subject)


def build_mailer():
    key = config.env("RESEND_API_KEY")
    return Mailer(key) if key else OutboxMailer()
