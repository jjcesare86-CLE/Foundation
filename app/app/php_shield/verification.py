"""
PHP Shield -- domain ownership verification (required before any fix work).

Two ways to prove control of the domain:
  DNS TXT : _phpshield-verify.<domain>  =  phpshield-verify=<token>
  File    : https://<domain>/.well-known/phpshield-verify.txt  containing <token>
The token is random, per order, and shown only on that order's page.
"""
import logging
from typing import Callable, Optional

from app.php_shield import netsafe, orders
from app.php_shield.store import iso

log = logging.getLogger("php_shield")
FILE_PATH = "/.well-known/phpshield-verify.txt"


def check_dns(host: str, expected: str) -> bool:
    import dns.exception
    import dns.resolver

    try:
        answers = dns.resolver.resolve(host, "TXT", lifetime=5.0)
    except (dns.exception.DNSException, OSError):
        return False
    for rdata in answers:
        value = b"".join(rdata.strings).decode("utf-8", "replace").strip().strip('"')
        if value == expected:
            return True
    return False


def check_file(domain: str, token: str, fetcher: Callable = netsafe.fetch) -> bool:
    for scheme in ("https", "http"):
        try:
            resp = fetcher(f"{scheme}://{domain}{FILE_PATH}")
        except (netsafe.UnsafeURL, netsafe.FetchError):
            continue
        body = (resp.body or "").strip()
        if resp.status == 200 and body in (token, f"phpshield-verify={token}"):
            return True
    return False


def verify_order(svc, order: dict, *, dns_check: Optional[Callable] = None, file_check: Optional[Callable] = None) -> dict:
    dns_check, file_check = dns_check or check_dns, file_check or check_file
    if order["status"] in ("verified", "in_progress", "delivered", "closed"):
        return {"verified": True, "method": None, "detail": "already verified"}
    if order["status"] != "authorized":
        raise orders.OrderError("sign the authorization before verifying ownership", 409)
    if not orders.valid_authorization(svc, order):
        raise orders.GateError("no valid signed authorization on this order")

    ins = orders.verification_instructions(svc, order)
    method = "dns" if dns_check(ins["txt_host"], ins["txt_value"]) else "file" if file_check(order["domain"], ins["token"]) else None
    patch = {"last_checked_at": iso(), "last_detail": "verified via " + method if method else "token not found yet"}
    if not method:
        svc.store.update("domain_verifications", patch, order_id=order["id"])
        return {"verified": False, "method": None,
                "detail": "We couldn't find the DNS record or the file yet. DNS changes can take a few minutes - try again shortly."}
    svc.store.update("domain_verifications", {**patch, "method": method, "verified_at": iso()}, order_id=order["id"])
    orders.transition(svc, order["id"], "verified", "customer", note=f"ownership verified via {method}")
    return {"verified": True, "method": method, "detail": f"Ownership verified via {method}."}
