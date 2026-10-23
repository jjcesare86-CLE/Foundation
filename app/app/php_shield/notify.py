"""
PHP Shield -- customer and owner emails.

Every send goes through `safe_send`: a failed email never breaks the business flow it
belongs to, but it is never silent either (logged, dead-lettered, owner alerted).
"""
import logging
from html import escape
from typing import Optional

from app.php_shield import config, tiers
from app.php_shield.ops import dead_letter

log = logging.getLogger("php_shield")


def order_url(order: dict) -> str:
    return f"{config.site_url()}/php-shield/order/{order['public_token']}"


def report_url(lead: dict) -> str:
    return f"{config.site_url()}/php-shield/report/{lead['report_token']}"


def _wrap(title: str, body: str) -> str:
    return (
        '<div style="font-family:system-ui,Arial,sans-serif;max-width:560px;margin:0 auto;color:#111;line-height:1.55">'
        f'<h2 style="margin:0 0 12px">{escape(title)}</h2>{body}'
        '<p style="color:#777;font-size:12px;margin-top:28px">PHP Shield &middot; a service of Automaition Nation</p></div>'
    )


def _btn(url: str, label: str) -> str:
    return (f'<p><a href="{escape(url)}" style="display:inline-block;background:#0A1628;color:#fff;padding:10px 18px;'
            f'border-radius:6px;text-decoration:none;font-weight:600">{escape(label)}</a></p>')


def safe_send(svc, to: str, subject: str, html: str, *, kind: str, attachments: Optional[list] = None) -> bool:
    try:
        svc.mailer.send(to, subject, html, attachments=attachments)
        return True
    except Exception as e:  # noqa: BLE001
        log.exception("email failed kind=%s to=%s", kind, to)
        dead_letter(f"email:{kind}", {"to": to, "subject": subject}, f"{type(e).__name__}: {e}", store=svc.store)
        svc.alerter.alert(f"email:{kind}", f"email '{kind}' failed", f"to={to}\nsubject={subject}\n{type(e).__name__}: {e}")
        return False


def to_owner(svc, subject: str, body_html: str, *, kind: str, attachments: Optional[list] = None) -> bool:
    owner = config.owner_email()
    if not owner:
        log.error("PHP_SHIELD_OWNER_EMAIL unset; owner notice '%s' not sent", subject)
        return False
    return safe_send(svc, owner, f"[PHP Shield] {subject}", _wrap(subject, body_html), kind=kind, attachments=attachments)


# -- owner notices --------------------------------------------------------------

def owner_new_order(svc, order: dict) -> None:
    to_owner(svc, f"New paid order: {order['domain']}",
             f"<p><b>{escape(order['customer_email'])}</b> paid for <b>{escape(tiers.tier_name(order.get('tier')))}</b>"
             f"{' + Maintenance' if order.get('maintenance') else ''} on <b>{escape(order['domain'])}</b>.</p>"
             f"<p>Order <code>{escape(order['id'])}</code>. Next step is theirs (intake).</p>", kind="owner_new_order")


def owner_authorization_signed(svc, order: dict, auth: dict, pdf: bytes) -> None:
    to_owner(svc, f"Authorization signed: {order['domain']}",
             f"<p><b>{escape(auth['typed_name'])}</b> signed the authorization for <b>{escape(order['domain'])}</b> "
             f"(order <code>{escape(order['id'])}</code>) at {escape(str(auth['signed_at']))}.</p>"
             "<p>Signed copy attached. Domain verification is still required before work starts.</p>",
             kind="owner_authorization", attachments=[{"filename": f"authorization-{order['id']}.pdf", "content": pdf}])


def owner_quote_request(svc, lead: dict, notes: Optional[str]) -> None:
    to_owner(svc, f"Custom quote requested: {lead['domain']}",
             f"<p><b>{escape(lead['contact_email'])}</b> asked for a custom quote on <b>{escape(lead['domain'])}</b> "
             f"(PHP {escape(str(lead.get('php_version') or 'unknown'))}).</p>"
             f"<p>Notes: {escape(notes or '(none)')}</p>", kind="owner_quote")


def owner_misc(svc, subject: str, body_html: str) -> None:
    to_owner(svc, subject, body_html, kind="owner_misc")


# -- customer messages ----------------------------------------------------------

_STATUS_COPY = {
    "paid": ("Payment received - next, tell us about your site",
             "Thanks for your order. The next step is a short intake form so we know how to reach your site."),
    "intake_complete": ("Intake received - next, sign the authorization",
                        "We have your site details. Please review and sign the authorization agreement."),
    "authorized": ("Authorization signed - next, verify ownership",
                   "Your signed agreement is attached for your records. Last step before we start: prove you control the domain."),
    "verified": ("Ownership verified - you're in the queue",
                 "Thank you. We'll email you a one-time secure link to hand over site access, then begin the work."),
    "in_progress": ("We've started work on your site",
                    "Your backup comes first. We'll email you when the work is delivered."),
    "closed": ("Your order is complete", "This order is now closed. Thank you for choosing PHP Shield."),
    "canceled": ("Your order was canceled", "If this wasn't expected, reply to this email."),
}


def customer_status(svc, order: dict, to_status: str, attachments: Optional[list] = None) -> None:
    if to_status not in _STATUS_COPY:
        return
    title, text = _STATUS_COPY[to_status]
    body = f"<p>{escape(text)}</p><p>Site: <b>{escape(order['domain'])}</b></p>" + _btn(order_url(order), "Open your order")
    safe_send(svc, order["customer_email"], f"PHP Shield: {title}", _wrap(title, body),
              kind=f"customer_{to_status}", attachments=attachments)


def customer_delivered(svc, order: dict, comparison_html: str) -> None:
    body = ("<p>Your site has been updated. Here is the before/after security rescan.</p>"
            + comparison_html + _btn(order_url(order), "View your order"))
    safe_send(svc, order["customer_email"], "PHP Shield: your fix is delivered",
              _wrap("Your fix is delivered", body), kind="customer_delivered")


def customer_report_ready(svc, lead: dict) -> None:
    safe_send(svc, lead["contact_email"], f"Your PHP Shield report for {lead['domain']}",
              _wrap("Your PHP Shield report is ready",
                    f"<p>Here is your scan report for <b>{escape(lead['domain'])}</b>.</p>" + _btn(report_url(lead), "View report")),
              kind="customer_report")
