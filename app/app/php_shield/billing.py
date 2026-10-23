"""
PHP Shield -- Stripe Checkout and webhook handling.

Fixed tiers (no quote step): Basic $300 / Standard $750 / Complex $1,500 one-time, plus the
$99/mo Maintenance subscription as an add-on or standalone. Price IDs come from env
(STRIPE_PRICE_PHPSHIELD_*; created by scripts/create_stripe_products.py).

Webhooks (signature verified) handle checkout.session.completed, invoice.paid and
customer.subscription.deleted. Each Stripe event id is recorded in `webhook_events` first
(unique key), so a redelivered event is a no-op; if processing fails the record is removed
and a 500 is returned so Stripe retries.
"""
import logging
from datetime import timedelta
from typing import Optional

from app.php_shield import config, notify, orders, tiers
from app.php_shield.ops import guarded_write
from app.php_shield.store import iso, utcnow

log = logging.getLogger("php_shield")
RESCAN_INTERVAL_DAYS = 30


class BillingError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class StripeGateway:
    """Thin wrapper so tests can substitute session creation while still using the real
    signature-verification code path."""

    def create_session(self, **params) -> dict:
        import stripe

        stripe.api_key = config.env("STRIPE_SECRET_KEY")
        s = stripe.checkout.Session.create(**params)
        return {"id": s["id"], "url": s["url"]}

    def construct_event(self, payload: bytes, sig_header: str, secret: str):
        import stripe

        return stripe.Webhook.construct_event(payload, sig_header, secret)


def create_checkout(svc, lead: dict, tier: Optional[str], maintenance: bool) -> str:
    if tier is not None and tier not in tiers.TIER_ORDER:
        raise BillingError("unknown tier")
    prices = config.stripe_price_ids()
    lines = []
    if tier:
        if not prices.get(tier):
            raise BillingError("pricing is not configured yet", 503)
        lines.append({"price": prices[tier], "quantity": 1})
    if maintenance:
        if not prices["maintenance"]:
            raise BillingError("pricing is not configured yet", 503)
        lines.append({"price": prices["maintenance"], "quantity": 1})
    if not lines:
        raise BillingError("choose a fix tier, maintenance, or both")

    order = orders.create_order(svc, lead, tier, maintenance)
    meta = {"order_id": order["id"], "tier": tier or "", "maintenance": str(bool(maintenance)).lower()}
    params = {
        "mode": "subscription" if maintenance else "payment",
        "line_items": lines,
        "success_url": notify.order_url(order) + "?paid=1",
        "cancel_url": notify.report_url(lead) + "?canceled=1",
        "customer_email": lead["contact_email"],
        "client_reference_id": order["id"],
        "metadata": meta,
    }
    if maintenance:
        params["subscription_data"] = {"metadata": meta}
    else:
        params["payment_intent_data"] = {"metadata": meta}
    try:
        session = svc.stripe.create_session(**params)
    except Exception as e:  # noqa: BLE001
        log.exception("stripe session creation failed")
        svc.alerter.alert("stripe:create_session", "Stripe checkout creation failed", f"{type(e).__name__}: {e}")
        raise BillingError("could not start checkout, please try again shortly", 502) from e
    svc.store.update("orders", {"stripe_checkout_session_id": session["id"]}, id=order["id"])
    svc.store.update("leads", {"status": "checkout_started"}, id=lead["id"])
    return session["url"]


# -- webhooks -----------------------------------------------------------------

class WebhookError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _g(obj, *path, default=None):
    for p in path:
        if obj is None:
            return default
        try:
            obj = obj[p]
        except (KeyError, IndexError, TypeError):
            return default
    return obj if obj is not None else default


def handle_webhook(svc, payload: bytes, sig_header: Optional[str]) -> dict:
    secret = config.env("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise WebhookError("webhook secret not configured", 503)
    if not sig_header:
        raise WebhookError("missing signature")
    try:
        event = svc.stripe.construct_event(payload, sig_header, secret)
    except Exception as e:  # ValueError (bad payload) / SignatureVerificationError
        raise WebhookError(f"invalid webhook: {type(e).__name__}") from e

    event_id, etype = event["id"], event["type"]
    if not svc.store.insert_if_new("webhook_events", {"event_id": event_id, "type": etype}, "event_id"):
        return {"ok": True, "duplicate": True}
    try:
        result = _process(svc, etype, event["data"]["object"])
    except Exception:
        svc.store.delete("webhook_events", event_id=event_id)  # let Stripe retry
        log.exception("webhook processing failed event=%s type=%s", event_id, etype)
        svc.alerter.alert(f"webhook:{etype}", f"Stripe webhook {etype} failed", f"event {event_id}; Stripe will retry. See logs.")
        raise
    return {"ok": True, "result": result}


def _process(svc, etype: str, obj) -> str:
    if etype == "checkout.session.completed":
        return _checkout_completed(svc, obj)
    if etype == "invoice.paid":
        return _invoice_paid(svc, obj)
    if etype == "customer.subscription.deleted":
        return _subscription_deleted(svc, obj)
    return "ignored"


def _order_for_session(svc, session) -> Optional[dict]:
    oid = _g(session, "client_reference_id") or _g(session, "metadata", "order_id")
    rows = svc.store.select("orders", id=oid) if oid else []
    return rows[0] if rows else None


def _checkout_completed(svc, session) -> str:
    order = _order_for_session(svc, session)
    if not order:
        svc.alerter.alert("stripe:unmatched", "PAID checkout with no matching order",
                          f"session {_g(session, 'id')} email {_g(session, 'customer_email')}. Money was taken; find the customer.")
        return "unmatched"
    if _g(session, "payment_status") not in ("paid", "no_payment_required"):
        return "awaiting_payment"
    sub_id = _g(session, "subscription")
    orders.mark_paid(svc, order, customer_id=_g(session, "customer"), subscription_id=sub_id,
                     session_id=_g(session, "id"), amount_total=_g(session, "amount_total"))
    if sub_id:
        _activate_subscription(svc, order, sub_id, _g(session, "customer"))
    svc.store.update("leads", {"status": "converted"}, id=order["lead_id"]) if order.get("lead_id") else None
    return "paid"


def _activate_subscription(svc, order: dict, sub_id: str, customer_id: Optional[str]) -> None:
    row = {"order_id": order["id"], "stripe_subscription_id": sub_id, "stripe_customer_id": customer_id,
           "domain": order["domain"], "customer_email": order["customer_email"], "status": "active",
           "next_scan_at": iso(utcnow() + timedelta(days=RESCAN_INTERVAL_DAYS))}
    guarded_write(svc, "subscription", row, lambda: svc.store.insert_if_new("subscriptions", row, "stripe_subscription_id"),
                  {"order": order["id"]})


def _invoice_paid(svc, invoice) -> str:
    sub_id = _g(invoice, "subscription") or _g(invoice, "parent", "subscription_details", "subscription")
    if not sub_id:
        return "no_subscription"
    existing = svc.store.select("subscriptions", stripe_subscription_id=sub_id)
    if existing:
        svc.store.update("subscriptions", {"status": "active", "last_invoice_paid_at": iso()}, stripe_subscription_id=sub_id)
        return "subscription_renewed"
    order_id = (_g(invoice, "subscription_details", "metadata", "order_id")
                or _g(invoice, "parent", "subscription_details", "metadata", "order_id")
                or _g(invoice, "lines", "data", 0, "metadata", "order_id"))
    rows = svc.store.select("orders", id=order_id) if order_id else svc.store.select("orders", stripe_subscription_id=sub_id)
    if rows and rows[0]["status"] != "pending_payment":
        _activate_subscription(svc, rows[0], sub_id, _g(invoice, "customer"))
        svc.store.update("subscriptions", {"last_invoice_paid_at": iso()}, stripe_subscription_id=sub_id)
        return "subscription_created"
    return "deferred"  # arrived before checkout.session.completed; that handler creates the row


def _subscription_deleted(svc, sub) -> str:
    sub_id = _g(sub, "id")
    rows = svc.store.select("subscriptions", stripe_subscription_id=sub_id)
    if not rows:
        return "unknown_subscription"
    if rows[0]["status"] == "canceled":
        return "already_canceled"
    svc.store.update("subscriptions", {"status": "canceled", "canceled_at": iso()}, stripe_subscription_id=sub_id)
    notify.owner_misc(svc, f"Maintenance canceled: {rows[0]['domain']}",
                      f"<p>{rows[0]['customer_email']} canceled the Maintenance Plan for <b>{rows[0]['domain']}</b>. Rescans stopped.</p>")
    notify.safe_send(svc, rows[0]["customer_email"], "PHP Shield: Maintenance Plan canceled",
                     notify._wrap("Maintenance canceled",
                                  f"<p>Your Maintenance Plan for <b>{rows[0]['domain']}</b> has ended. Monthly rescans have stopped.</p>"),
                     kind="customer_maintenance_canceled")
    return "canceled"
