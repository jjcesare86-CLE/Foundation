"""
PHP Shield -- order lifecycle, fulfillment gate, intake, authorization, delivery.

Status flow (one step at a time; the DB trigger in 003_php_shield_guards.sql enforces the
same rules as a backstop):

  pending_payment -> paid -> intake_complete -> authorized -> verified -> in_progress -> delivered -> closed
                      (any pre-work status may also go to `canceled`)

THE GATE: an order cannot reach `authorized`, `verified` or `in_progress` unless a signed,
unrevoked authorization exists for THAT order AND THAT domain; `verified`/`in_progress` also
need verified domain ownership; `in_progress` also needs payment. Customers move an order
forward through intake -> authorize -> verify; only the admin can start/deliver/close it.
"""
import logging
import secrets
from typing import Optional

from app.php_shield import agreement, netsafe, notify, tiers
from app.php_shield.ops import guarded_write
from app.php_shield.pdf import signed_agreement_pdf
from app.php_shield.store import StoreConflict, StoreRejected, iso

log = logging.getLogger("php_shield")

FLOW = ["pending_payment", "paid", "intake_complete", "authorized", "verified", "in_progress", "delivered", "closed"]
CANCELABLE = {"pending_payment", "paid", "intake_complete", "authorized", "verified"}
ADMIN_ONLY = {"in_progress", "delivered", "closed", "canceled"}
ACCESS_METHODS = {"sftp", "ssh", "cpanel", "wp_admin", "other"}


class OrderError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class GateError(OrderError):
    def __init__(self, message: str):
        super().__init__(message, 409)


def new_token() -> str:
    return secrets.token_urlsafe(32)


# -- lookups ------------------------------------------------------------------

def get_order(svc, order_id: str) -> dict:
    rows = svc.store.select("orders", id=order_id)
    if not rows:
        raise OrderError("order not found", 404)
    return rows[0]


def get_order_by_token(svc, token: str) -> dict:
    rows = svc.store.select("orders", public_token=token) if token else []
    if not rows:
        raise OrderError("order not found", 404)
    return rows[0]


def _one(svc, table: str, order_id: str) -> Optional[dict]:
    rows = svc.store.select(table, order_id=order_id)
    return rows[0] if rows else None


def valid_authorization(svc, order: dict) -> Optional[dict]:
    """The signed authorization for this order AND this order's domain, unless revoked."""
    auth = _one(svc, "authorizations", order["id"])
    if not auth or auth["domain"] != order["domain"]:
        return None
    if _one(svc, "authorization_revocations", order["id"]):
        return None
    return auth


def domain_verified(svc, order: dict) -> bool:
    v = _one(svc, "domain_verifications", order["id"])
    return bool(v and v.get("verified_at") and v["domain"] == order["domain"])


# -- creation -----------------------------------------------------------------

def create_order(svc, lead: dict, tier: Optional[str], maintenance: bool) -> dict:
    if tier is not None and tier not in tiers.TIER_ORDER:
        raise OrderError("unknown tier")
    if tier is None and not maintenance:
        raise OrderError("choose a fix tier, maintenance, or both")
    amount = (tiers.tier_price_cents(tier) if tier else 0) + (tiers.maintenance_plan()["price_cents"] if maintenance else 0)
    checklist = {i["key"]: {"done": False} for i in tiers.checklist_template()}
    payload = {
        "public_token": new_token(), "lead_id": lead["id"], "domain": lead["domain"],
        "customer_email": lead["contact_email"], "tier": tier, "maintenance": bool(maintenance),
        "amount_cents": amount, "status": "pending_payment", "checklist": checklist,
    }
    order = guarded_write(svc, "order", payload, lambda: svc.store.insert("orders", payload), {"lead": lead["id"]})
    ver = {"order_id": order["id"], "domain": order["domain"], "token": secrets.token_hex(16)}
    guarded_write(svc, "domain_verification", ver, lambda: svc.store.insert("domain_verifications", ver), {"order": order["id"]})
    return order


def verification_instructions(svc, order: dict) -> dict:
    v = _one(svc, "domain_verifications", order["id"])
    token = v["token"] if v else ""
    return {
        "token": token,
        "txt_host": f"_phpshield-verify.{order['domain']}",
        "txt_value": f"phpshield-verify={token}",
        "file_path": "/.well-known/phpshield-verify.txt",
        "file_content": token,
    }


# -- the single transition point ----------------------------------------------

def _check_gate(svc, order: dict, to: str) -> None:
    if to in ("authorized", "verified", "in_progress") and not valid_authorization(svc, order):
        raise GateError(f"cannot move to '{to}': no valid signed authorization exists for domain {order['domain']} on this order")
    if to in ("verified", "in_progress") and not domain_verified(svc, order):
        raise GateError(f"cannot move to '{to}': domain ownership of {order['domain']} has not been verified")
    if to == "in_progress" and not order.get("paid_at"):
        raise GateError("cannot start work before payment")
    if to == "intake_complete" and not _one(svc, "intake", order["id"]):
        raise GateError("cannot complete intake: no intake form on file")


def transition(svc, order_id: str, to: str, actor: str, note: Optional[str] = None,
               patch: Optional[dict] = None, attachments: Optional[list] = None, notify_customer: bool = True) -> dict:
    order = get_order(svc, order_id)
    cur = order["status"]
    if to == "canceled":
        if cur not in CANCELABLE:
            raise OrderError(f"cannot cancel an order that is {cur}", 409)
    else:
        if cur not in FLOW or to not in FLOW or FLOW.index(to) != FLOW.index(cur) + 1:
            raise OrderError(f"illegal transition {cur} -> {to}", 409)
    _check_gate(svc, order, to)

    full_patch = {"status": to, **(patch or {})}
    if to == "delivered":
        full_patch["delivered_at"] = iso()
    if to == "closed":
        full_patch["closed_at"] = iso()
    try:
        rows = svc.store.update("orders", full_patch, id=order_id, status=cur)  # status in WHERE = optimistic lock
    except StoreRejected as e:  # DB backstop fired
        raise GateError(str(e)) from e
    if not rows:
        raise OrderError("order changed concurrently; retry", 409)
    updated = rows[0]
    ev = {"order_id": order_id, "from_status": cur, "to_status": to, "actor": actor, "note": note}
    guarded_write(svc, "order_event", ev, lambda: svc.store.insert("order_events", ev), {"order": order_id})
    if notify_customer:
        notify.customer_status(svc, updated, to, attachments=attachments)
    return updated


# -- customer actions -----------------------------------------------------------

def mark_paid(svc, order: dict, *, customer_id: Optional[str], subscription_id: Optional[str],
              session_id: str, amount_total: Optional[int]) -> Optional[dict]:
    """Idempotent: only the first call on a pending_payment order changes anything."""
    if order["status"] != "pending_payment":
        return None
    patch = {"paid_at": iso(), "stripe_customer_id": customer_id, "stripe_subscription_id": subscription_id,
             "stripe_checkout_session_id": session_id}
    if amount_total is not None:
        patch["amount_cents"] = amount_total
    updated = transition(svc, order["id"], "paid", "stripe", patch=patch)
    notify.owner_new_order(svc, updated)
    return updated


def _same_site(a: str, b: str) -> bool:
    try:
        return netsafe.registrable_host(a) == netsafe.registrable_host(b)
    except Exception:  # noqa: BLE001
        return False


def submit_intake(svc, order: dict, data: dict) -> dict:
    if order["status"] != "paid":
        raise OrderError("intake is only available right after payment" if order["status"] == "pending_payment"
                         else f"intake already completed (order is {order['status']})", 409)
    site_url = (data.get("site_url") or "").strip()
    try:
        netsafe.validate_url(netsafe.normalize_user_url(site_url))
    except netsafe.UnsafeURL as e:
        raise OrderError(f"invalid site url: {e}") from e
    if not _same_site(site_url, order["domain"]):
        raise OrderError(f"site url must be on the purchased domain ({order['domain']})")
    method = data.get("access_method")
    if method not in ACCESS_METHODS:
        raise OrderError("invalid access method")
    for f in ("hosting_provider", "has_staging_or_backup", "preferred_timing", "contact_name", "contact_email"):
        if not (data.get(f) or "").strip():
            raise OrderError(f"{f} is required")
    row = {
        "order_id": order["id"], "site_url": site_url, "hosting_provider": data["hosting_provider"].strip(),
        "access_method": method, "access_method_other": (data.get("access_method_other") or "").strip() or None,
        "has_staging_or_backup": data["has_staging_or_backup"].strip(), "preferred_timing": data["preferred_timing"].strip(),
        "contact_name": data["contact_name"].strip(), "contact_email": data["contact_email"].strip(),
        "contact_phone": (data.get("contact_phone") or "").strip() or None,
        "notes": (data.get("notes") or "").strip() or None,
        "credentials_handoff_status": "link_pending",  # we email a one-time secure link later; never a form field
    }
    if _one(svc, "intake", order["id"]):
        raise OrderError("intake already submitted", 409)
    try:
        guarded_write(svc, "intake", row, lambda: svc.store.insert("intake", row), {"order": order["id"]})
    except Exception as e:  # noqa: BLE001
        if isinstance(e.__cause__, StoreConflict):
            raise OrderError("intake already submitted", 409) from e
        raise
    return transition(svc, order["id"], "intake_complete", "customer")


def scope_text(order: dict) -> str:
    parts = [tiers.tier_name(order["tier"])] if order.get("tier") else []
    if order.get("maintenance"):
        parts.append("Maintenance Plan (monthly rescans)")
    return " + ".join(parts)


def agreement_for(order: dict) -> dict:
    text = agreement.render(domain=order["domain"], order_id=order["id"], scope=scope_text(order))
    return {"version": agreement.AGREEMENT_VERSION, "text": text, "hash": agreement.sha256_hex(text)}


def sign_authorization(svc, order: dict, *, typed_name: str, agree: bool, ip: str, user_agent: str) -> dict:
    if not agree:
        raise OrderError("you must tick the confirmation box to sign")
    typed_name = " ".join((typed_name or "").split())
    if len(typed_name) < 3 or " " not in typed_name:
        raise OrderError("type your full name (first and last) to sign")
    if order["status"] != "intake_complete":
        raise OrderError("the authorization can only be signed after intake" if order["status"] in ("pending_payment", "paid")
                         else "this order is already authorized", 409)
    if _one(svc, "authorizations", order["id"]):
        raise OrderError("this order is already signed", 409)
    ag = agreement_for(order)  # always rendered server-side; the client never supplies text
    row = {
        "order_id": order["id"], "domain": order["domain"], "typed_name": typed_name,
        "agreement_version": ag["version"], "agreement_hash": ag["hash"], "agreement_text": ag["text"],
        "signed_at": iso(), "ip": ip, "user_agent": (user_agent or "unknown")[:500],
    }
    try:
        auth = guarded_write(svc, "authorization", row, lambda: svc.store.insert("authorizations", row), {"order": order["id"]})
    except Exception as e:  # noqa: BLE001
        if isinstance(e.__cause__, StoreConflict):
            raise OrderError("this order is already signed", 409) from e
        raise
    pdf = signed_agreement_pdf(auth, order)
    attach = [{"filename": f"authorization-{order['id']}.pdf", "content": pdf}]
    updated = transition(svc, order["id"], "authorized", "customer", note=f"signed by {typed_name}", attachments=attach)
    notify.owner_authorization_signed(svc, updated, auth, pdf)
    return {"order": updated, "authorization": auth}


def revoke_authorization(svc, order: dict, *, reason: str, ip: str, user_agent: str) -> None:
    if not _one(svc, "authorizations", order["id"]):
        raise OrderError("no signed authorization to revoke", 409)
    if _one(svc, "authorization_revocations", order["id"]):
        return
    row = {"order_id": order["id"], "reason": (reason or "")[:1000], "ip": ip, "user_agent": (user_agent or "")[:500]}
    guarded_write(svc, "authorization_revocation", row, lambda: svc.store.insert("authorization_revocations", row), {"order": order["id"]})
    notify.owner_misc(svc, f"Authorization REVOKED: {order['domain']}",
                      f"<p>The customer revoked authorization for <b>{order['domain']}</b> (order {order['id']}). "
                      "Stop all work and access. Reason: " + (reason or "(none given)") + "</p>")


# -- admin actions ------------------------------------------------------------

def tick_checklist(svc, order_id: str, key: str, done: bool, actor: str) -> dict:
    order = get_order(svc, order_id)
    cl = dict(order.get("checklist") or {})
    if key not in cl:
        raise OrderError(f"unknown checklist item '{key}'")
    cl[key] = {"done": bool(done), "at": iso() if done else None, "by": actor if done else None}
    return svc.store.update("orders", {"checklist": cl}, id=order_id)[0]


def checklist_complete(order: dict) -> bool:
    cl = order.get("checklist") or {}
    return bool(cl) and all(v.get("done") for v in cl.values())


def start_work(svc, order_id: str, actor: str) -> dict:
    return transition(svc, order_id, "in_progress", actor)


def deliver(svc, order_id: str, actor: str, *, scanner=None) -> dict:
    """in_progress -> delivered. Requires a complete checklist, runs the post-fix rescan
    (allowed: this order is authorized and ownership-verified) and emails before/after."""
    from app.php_shield import report_generator, scanner as scanner_mod

    order = get_order(svc, order_id)
    if order["status"] != "in_progress":
        raise OrderError(f"order is {order['status']}, not in_progress", 409)
    if not checklist_complete(order):
        open_items = [k for k, v in (order.get("checklist") or {}).items() if not v.get("done")]
        raise OrderError("delivery checklist incomplete: " + ", ".join(open_items), 409)
    if not valid_authorization(svc, order) or not domain_verified(svc, order):
        raise GateError("authorization or domain verification no longer valid")

    after = (scanner or scanner_mod.scan)(f"https://{order['domain']}").to_dict()
    before = (svc.store.select("scan_reports", order_id=order_id, kind="before") or [None])[0]
    if before is None and order.get("lead_id"):
        lead = (svc.store.select("leads", id=order["lead_id"]) or [None])[0]
        before = {"result": (lead or {}).get("scan") or {}}
    rep = {"order_id": order_id, "domain": order["domain"], "kind": "after", "version": after.get("version"),
           "risk_level": (after.get("risk") or {}).get("risk_level"), "result": after}
    guarded_write(svc, "scan_report", rep, lambda: svc.store.insert("scan_reports", rep), {"order": order_id})
    updated = transition(svc, order_id, "delivered", actor, notify_customer=False)
    notify.customer_delivered(svc, updated, report_generator.render_comparison(before["result"], after, order["domain"]))
    return updated
