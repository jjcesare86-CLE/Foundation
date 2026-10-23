"""
PHP Shield -- HTTP API.

  public router  /php-shield/...          scan, report, quote, checkout, customer order flow
                                          (customer endpoints are authorised by the unguessable
                                          order token in the URL; there are no accounts)
  webhook        POST /php-shield/stripe/webhook   (Stripe signature verified)
  admin router   /php-shield/admin/...    X-Admin-Key == PHP_SHIELD_ADMIN_API_KEY
"""
import logging
import re
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.php_shield import billing, config, netsafe, notify, orders, tiers, turnstile, verification
from app.php_shield import scanner as scanner_mod
from app.php_shield import services
from app.php_shield.ops import guarded_write
from app.php_shield.pdf import signed_agreement_pdf
from app.php_shield.ratelimit import client_ip, hash_ip

log = logging.getLogger("php_shield")
router = APIRouter(prefix="/php-shield", tags=["php-shield"])
admin_router = APIRouter(prefix="/php-shield/admin", tags=["php-shield-admin"])

CONSENT_TEXT = "I own or am authorized to scan this site."
_EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")


def svc():
    return services.get()


# -- models -------------------------------------------------------------------

class ScanIn(BaseModel):
    url: str = Field(max_length=2048)
    email: str = Field(max_length=254)
    consent: bool
    company_website: str = Field(default="", max_length=500)  # honeypot: real users leave it empty
    turnstile_token: Optional[str] = Field(default=None, max_length=4096)


class QuoteIn(BaseModel):
    report_token: str = Field(max_length=200)
    notes: Optional[str] = Field(default=None, max_length=2000)


class CheckoutIn(BaseModel):
    report_token: str = Field(max_length=200)
    tier: Optional[str] = Field(default=None, max_length=20)
    maintenance: bool = False


class IntakeIn(BaseModel):
    site_url: str = Field(max_length=2048)
    hosting_provider: str = Field(max_length=200)
    access_method: str = Field(max_length=20)
    access_method_other: Optional[str] = Field(default=None, max_length=200)
    has_staging_or_backup: str = Field(max_length=100)
    preferred_timing: str = Field(max_length=200)
    contact_name: str = Field(max_length=200)
    contact_email: str = Field(max_length=254)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=3000)


class AuthorizeIn(BaseModel):
    typed_name: str = Field(max_length=200)
    agree: bool


class RevokeIn(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=1000)


# -- helpers ------------------------------------------------------------------

def _lead_by_token(token: str) -> dict:
    rows = svc().store.select("leads", report_token=token) if token else []
    if not rows:
        raise HTTPException(404, "report not found")
    return rows[0]


def _order_view(order: dict) -> dict:
    s = svc()
    return {
        "status": order["status"], "domain": order["domain"], "tier": order.get("tier"),
        "maintenance": bool(order.get("maintenance")),
        "intake_complete": order["status"] not in ("pending_payment", "paid", "canceled"),
        "authorized": orders.valid_authorization(s, order) is not None,
        "verified": orders.domain_verified(s, order),
        "verification": orders.verification_instructions(s, order),
    }


def _limit(key: str, limit: int, window: int = 3600):
    svc().simple_limiter.check(key, limit, window)


# -- public: scan / report ------------------------------------------------------

@router.post("/scan")
def scan(body: ScanIn, request: Request):
    s = svc()
    if body.company_website.strip():
        raise HTTPException(400, "invalid request")  # honeypot tripped
    if not body.consent:
        raise HTTPException(400, "You must confirm you own or are authorized to scan this site.")
    email = body.email.strip()
    if not _EMAIL_RE.match(email):
        raise HTTPException(400, "Please enter a valid email address.")
    ip = client_ip(request)
    if not turnstile.verify(body.turnstile_token, ip):
        raise HTTPException(400, "Bot check failed. Please reload the page and try again.")

    try:
        target = netsafe.validate_url(netsafe.normalize_user_url(body.url))
    except netsafe.UnsafeURL as e:
        raise HTTPException(400, f"That URL can't be scanned: {e}") from None
    domain = netsafe.registrable_host(target.host)

    s.limiter.check_and_record(ip, domain)  # RateLimited -> 429 (handler in app factory)
    with s.limiter.slot():  # Busy -> 503
        result = scanner_mod.scan(target.url)
    if result.error:
        raise HTTPException(400, result.error)

    row = {
        "report_token": secrets.token_urlsafe(24), "url": result.url, "domain": domain, "contact_email": email,
        "consent_scan": True, "consent_text": CONSENT_TEXT, "ip_hash": hash_ip(ip),
        "user_agent": (request.headers.get("user-agent") or "")[:300], "php_version": result.version,
        "risk_level": (result.risk or {}).get("risk_level"), "confidence": result.confidence, "scan": result.to_dict(),
    }
    guarded_write(s, "lead", {**row, "scan": "(omitted)"}, lambda: s.store.insert("leads", row), {"domain": domain})
    return {"report_token": row["report_token"], "domain": domain, "php_detected": result.php_detected,
            "version": result.version, "confidence": result.confidence, "risk": result.risk}


@router.get("/tiers")
def get_tiers():
    return {"tiers": tiers.tier_catalog(), "maintenance": tiers.maintenance_plan()}


@router.get("/report/{report_token}")
def report(report_token: str):
    lead = _lead_by_token(report_token)
    scan_data = lead.get("scan") or {}
    return {
        "domain": lead["domain"], "scanned_at": scan_data.get("scanned_at") or lead["created_at"],
        "php_detected": scan_data.get("php_detected", False), "version": scan_data.get("version"),
        "confidence": scan_data.get("confidence", "none"), "evidence": scan_data.get("evidence", []),
        "risk": scan_data.get("risk"), "recommendation": tiers.recommend(scan_data),
        "tiers": tiers.tier_catalog(), "maintenance": tiers.maintenance_plan(),
    }


@router.post("/quote")
def quote(body: QuoteIn, request: Request):
    _limit(f"quote:{client_ip(request)}", 10)
    s = svc()
    lead = _lead_by_token(body.report_token)
    guarded_write(s, "quote_request", {"lead": lead["id"], "notes": body.notes},
                  lambda: s.store.update("leads", {"quote_requested": True, "status": "quote_requested", "quote_notes": body.notes},
                                         id=lead["id"]), {"lead": lead["id"]})
    notify.owner_quote_request(s, lead, body.notes)
    return {"ok": True}


@router.post("/checkout")
def checkout(body: CheckoutIn, request: Request):
    _limit(f"checkout:{client_ip(request)}", 10)
    lead = _lead_by_token(body.report_token)
    return {"checkout_url": billing.create_checkout(svc(), lead, body.tier, body.maintenance)}


# -- public: customer order flow (token = auth) -----------------------------------

@router.get("/order/{order_token}")
def get_order(order_token: str):
    return _order_view(orders.get_order_by_token(svc(), order_token))


@router.post("/order/{order_token}/intake")
def intake(order_token: str, body: IntakeIn, request: Request):
    _limit(f"intake:{client_ip(request)}", 30)
    s = svc()
    orders.submit_intake(s, orders.get_order_by_token(s, order_token), body.model_dump())
    return {"ok": True}


@router.get("/order/{order_token}/agreement")
def agreement_view(order_token: str):
    return orders.agreement_for(orders.get_order_by_token(svc(), order_token))


@router.post("/order/{order_token}/authorize")
def authorize(order_token: str, body: AuthorizeIn, request: Request):
    _limit(f"authorize:{client_ip(request)}", 20)
    s = svc()
    res = orders.sign_authorization(s, orders.get_order_by_token(s, order_token), typed_name=body.typed_name,
                                    agree=body.agree, ip=client_ip(request), user_agent=request.headers.get("user-agent", ""))
    return {"ok": True, "signed_at": res["authorization"]["signed_at"]}


@router.post("/order/{order_token}/verify")
def verify(order_token: str, request: Request):
    _limit(f"verify:{client_ip(request)}:{order_token[:8]}", 20)
    s = svc()
    return verification.verify_order(s, orders.get_order_by_token(s, order_token))


@router.post("/order/{order_token}/revoke")
def revoke(order_token: str, body: RevokeIn, request: Request):
    _limit(f"revoke:{client_ip(request)}", 10)
    s = svc()
    orders.revoke_authorization(s, orders.get_order_by_token(s, order_token), reason=body.reason or "",
                                ip=client_ip(request), user_agent=request.headers.get("user-agent", ""))
    return {"ok": True}


# -- Stripe webhook -------------------------------------------------------------

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(default=None, alias="Stripe-Signature")):
    payload = await request.body()
    from starlette.concurrency import run_in_threadpool

    try:
        return await run_in_threadpool(billing.handle_webhook, svc(), payload, stripe_signature)
    except billing.WebhookError as e:
        raise HTTPException(e.status_code, str(e)) from e


# -- admin ----------------------------------------------------------------------

def require_admin(x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key")):
    expected = config.env("PHP_SHIELD_ADMIN_API_KEY")
    if not expected:
        raise HTTPException(503, "admin key not configured")  # fail closed
    if not x_admin_key or not secrets.compare_digest(x_admin_key.encode(), expected.encode()):
        raise HTTPException(403, "invalid admin key")


class AdvanceIn(BaseModel):
    to: str = Field(max_length=30)
    note: Optional[str] = Field(default=None, max_length=1000)


class ChecklistIn(BaseModel):
    key: str = Field(max_length=100)
    done: bool


def _order_summary(o: dict) -> dict:
    return {k: o.get(k) for k in ("id", "status", "domain", "customer_email", "tier", "maintenance", "amount_cents",
                                   "paid_at", "created_at", "delivered_at")}


@admin_router.get("/orders", dependencies=[Depends(require_admin)])
def admin_orders(status: Optional[str] = None):
    rows = svc().store.select("orders", **({"status": status} if status else {}))
    return {"orders": [_order_summary(o) for o in sorted(rows, key=lambda r: r["created_at"], reverse=True)]}


@admin_router.get("/orders/{order_id}", dependencies=[Depends(require_admin)])
def admin_order(order_id: str):
    s = svc()
    o = orders.get_order(s, order_id)
    auth = (s.store.select("authorizations", order_id=order_id) or [None])[0]
    return {
        "order": o, "intake": (s.store.select("intake", order_id=order_id) or [None])[0],
        "authorization": {k: auth[k] for k in ("typed_name", "signed_at", "ip", "agreement_version", "agreement_hash")} if auth else None,
        "revoked": bool(s.store.select("authorization_revocations", order_id=order_id)),
        "verification": (s.store.select("domain_verifications", order_id=order_id) or [None])[0],
        "events": sorted(s.store.select("order_events", order_id=order_id), key=lambda r: r["created_at"]),
        "checklist_template": tiers.checklist_template(),
    }


@admin_router.post("/orders/{order_id}/advance", dependencies=[Depends(require_admin)])
def admin_advance(order_id: str, body: AdvanceIn):
    if body.to not in orders.ADMIN_ONLY:
        raise HTTPException(400, f"admin may only set: {', '.join(sorted(orders.ADMIN_ONLY))} "
                                 "(customers advance intake/authorization/verification themselves)")
    if body.to == "delivered":
        raise HTTPException(400, "use POST /deliver (runs the rescan and checks the checklist)")
    return _order_summary(orders.transition(svc(), order_id, body.to, "admin", note=body.note))


@admin_router.post("/orders/{order_id}/checklist", dependencies=[Depends(require_admin)])
def admin_checklist(order_id: str, body: ChecklistIn):
    return orders.tick_checklist(svc(), order_id, body.key, body.done, "admin")["checklist"]


@admin_router.post("/orders/{order_id}/deliver", dependencies=[Depends(require_admin)])
def admin_deliver(order_id: str):
    return _order_summary(orders.deliver(svc(), order_id, "admin"))


@admin_router.get("/orders/{order_id}/authorization.pdf", dependencies=[Depends(require_admin)])
def admin_pdf(order_id: str):
    s = svc()
    o = orders.get_order(s, order_id)
    auth = (s.store.select("authorizations", order_id=order_id) or [None])[0]
    if not auth:
        raise HTTPException(404, "not signed")
    return Response(signed_agreement_pdf(auth, o), media_type="application/pdf")


@admin_router.get("/leads", dependencies=[Depends(require_admin)])
def admin_leads():
    rows = svc().store.select("leads")
    return {"leads": [{k: r.get(k) for k in ("id", "domain", "contact_email", "php_version", "risk_level", "status",
                                              "quote_requested", "quote_notes", "created_at")} for r in sorted(rows, key=lambda r: r["created_at"], reverse=True)]}


_ADMIN_HTML = """<!doctype html><meta charset=utf-8><meta name=robots content=noindex>
<title>PHP Shield admin</title>
<style>body{font:14px system-ui;margin:24px;background:#0b1020;color:#e2e8f0}input,button,select{font:inherit;padding:6px 10px;border-radius:6px;border:1px solid #334}
button{background:#1e3a5f;color:#fff;cursor:pointer}table{border-collapse:collapse;width:100%;margin-top:16px}td,th{border-bottom:1px solid #243052;padding:8px;text-align:left}
.pill{padding:2px 8px;border-radius:99px;background:#243052}</style>
<h2>PHP Shield - orders</h2>
<p><input id=key type=password placeholder="Admin key" size=34> <button onclick="save()">Load</button> <span id=msg></span></p>
<table id=t><thead><tr><th>Domain<th>Customer<th>Order<th>Status<th>Created<th>Actions</tr></thead><tbody></tbody></table>
<script>
const api=(p,o={})=>fetch('/php-shield/admin'+p,{...o,headers:{'X-Admin-Key':sessionStorage.k||'','Content-Type':'application/json'}}).then(async r=>{const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.detail||r.status);return j});
const say=m=>document.getElementById('msg').textContent=m;
function save(){sessionStorage.k=document.getElementById('key').value;load()}
function cell(tr,text){const td=document.createElement('td');td.textContent=text??'';tr.appendChild(td);return td}
function btn(td,label,fn){const b=document.createElement('button');b.textContent=label;b.style.marginRight='6px';b.onclick=async()=>{try{say('...');await fn();say('done');load()}catch(e){say(e.message)}};td.appendChild(b)}
async function load(){try{const {orders}=await api('/orders');const tb=document.querySelector('#t tbody');tb.textContent='';
for(const o of orders){const tr=document.createElement('tr');cell(tr,o.domain);cell(tr,o.customer_email);cell(tr,(o.tier||'maintenance')+(o.maintenance&&o.tier?' +maint':''));
const s=cell(tr,'');const p=document.createElement('span');p.className='pill';p.textContent=o.status;s.appendChild(p);cell(tr,(o.created_at||'').slice(0,10));const a=cell(tr,'');
if(o.status==='verified')btn(a,'Start work',()=>api('/orders/'+o.id+'/advance',{method:'POST',body:JSON.stringify({to:'in_progress'})}));
if(o.status==='in_progress')btn(a,'Deliver (rescan)',()=>api('/orders/'+o.id+'/deliver',{method:'POST'}));
if(o.status==='delivered')btn(a,'Close',()=>api('/orders/'+o.id+'/advance',{method:'POST',body:JSON.stringify({to:'closed'})}));
btn(a,'Checklist',async()=>{const d=await api('/orders/'+o.id);const open=Object.entries(d.order.checklist).filter(([k,v])=>!v.done).map(([k])=>k);
if(!open.length){say('checklist complete');return}const k=prompt('Mark done ('+open.join(', ')+'):',open[0]);if(k)await api('/orders/'+o.id+'/checklist',{method:'POST',body:JSON.stringify({key:k,done:true})})});
tb.appendChild(tr)}say(orders.length+' orders')}catch(e){say(e.message)}}
if(sessionStorage.k)load();
</script>"""


@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_page():
    """Static shell only -- every data call needs the admin key."""
    return HTMLResponse(_ADMIN_HTML, headers={"Cache-Control": "no-store", "X-Robots-Tag": "noindex"})
