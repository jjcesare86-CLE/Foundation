"""Intake, signed authorization, domain verification, the fulfillment GATE, delivery, maintenance."""
import hashlib
from datetime import timedelta

import pytest

from app.php_shield import maintenance, orders, verification
from app.php_shield.scanner import ScanResult
from app.php_shield.php_version_db import risk_report
from app.php_shield.store import StoreRejected, iso, utcnow
from tests.php_shield.conftest import INTAKE, make_lead, paid_order

SIGN = {"typed_name": "Pat Owner", "agree": True}
UA = {"user-agent": "pytest-browser/1.0", "x-forwarded-for": "198.51.100.23"}


def api(client, order, path, method="post", **kw):
    url = f"/php-shield/order/{order['public_token']}{path}"
    return getattr(client, method)(url, headers=UA, **kw)


def through_intake(client, svc, **kw):
    o = paid_order(svc, **kw)
    assert api(client, o, "/intake", json=INTAKE).status_code == 200
    return svc.store.select("orders", id=o["id"])[0]


def through_authorization(client, svc, **kw):
    o = through_intake(client, svc, **kw)
    assert api(client, o, "/authorize", json=SIGN).status_code == 200
    return svc.store.select("orders", id=o["id"])[0]


def verify_ok(svc, o):
    return verification.verify_order(svc, o, dns_check=lambda h, v: True, file_check=lambda d, t: False)


def verified_order(client, svc, **kw):
    o = through_authorization(client, svc, **kw)
    verify_ok(svc, o)
    return svc.store.select("orders", id=o["id"])[0]


# -- intake ---------------------------------------------------------------------

def test_intake_requires_payment_and_matching_domain(client, svc):
    lead = make_lead(svc)
    o = orders.create_order(svc, lead, "basic", False)  # still pending_payment
    assert api(client, o, "/intake", json=INTAKE).status_code == 409
    o = paid_order(svc, domain="other.com")
    assert api(client, o, "/intake", json=INTAKE).status_code == 400  # site_url is example.com, order is other.com


def test_intake_happy_path_never_stores_credentials(client, svc):
    o = through_intake(client, svc)
    assert o["status"] == "intake_complete"
    row = svc.store.select("intake", order_id=o["id"])[0]
    assert row["credentials_handoff_status"] == "link_pending"
    assert not any(k for k in row if "pass" in k or "secret" in k or "credential" in k.replace("credentials_handoff_status", ""))
    assert api(client, o, "/intake", json=INTAKE).status_code == 409  # second submit refused


def test_intake_validation(client, svc):
    o = paid_order(svc)
    assert api(client, o, "/intake", json={**INTAKE, "access_method": "telnet"}).status_code == 400
    assert api(client, o, "/intake", json={**INTAKE, "hosting_provider": " "}).status_code == 400
    assert api(client, o, "/intake", json={**INTAKE, "site_url": "http://127.0.0.1"}).status_code == 400


# -- authorization ----------------------------------------------------------------

def test_cannot_sign_before_intake(client, svc):
    o = paid_order(svc)
    assert api(client, o, "/authorize", json=SIGN).status_code == 409
    assert not svc.store.select("authorizations")


@pytest.mark.parametrize("body", [{"typed_name": "Pat", "agree": True}, {"typed_name": "", "agree": True},
                                  {"typed_name": "Pat Owner", "agree": False}])
def test_signature_requires_full_name_and_checkbox(client, svc, body):
    o = through_intake(client, svc)
    assert api(client, o, "/authorize", json=body).status_code == 400
    assert not svc.store.select("authorizations")


def test_signing_records_evidence_and_emails_pdf_to_customer_and_owner(client, svc):
    o = through_intake(client, svc)
    ag = api(client, o, "/agreement", method="get").json()
    assert ag["hash"] == hashlib.sha256(ag["text"].encode()).hexdigest()
    assert "example.com" in ag["text"] and "DRAFT" in ag["text"] and o["id"] in ag["text"]
    assert api(client, o, "/agreement", method="get").json() == ag  # deterministic: what is read == what is hashed

    r = api(client, o, "/authorize", json=SIGN)
    assert r.status_code == 200 and r.json()["signed_at"]
    a = svc.store.select("authorizations", order_id=o["id"])[0]
    assert a["typed_name"] == "Pat Owner" and a["domain"] == "example.com" and a["order_id"] == o["id"]
    assert a["agreement_hash"] == ag["hash"] and a["agreement_text"] == ag["text"]
    assert a["ip"] == "198.51.100.23" and a["user_agent"] == "pytest-browser/1.0"
    assert svc.store.select("orders", id=o["id"])[0]["status"] == "authorized"

    for to in ("cust@example.com", "owner@example.com"):
        msgs = [m for m in svc.mailer.sent if m["to"] == [to] and m["attachments"]]
        assert msgs, f"no PDF email to {to}"
        pdf = msgs[-1]["attachments"][0]
        assert pdf["filename"].endswith(".pdf") and pdf["content"].startswith(b"%PDF")


def test_client_cannot_inject_agreement_text(client, svc):
    o = through_intake(client, svc)
    api(client, o, "/authorize", json={**SIGN, "agreement_text": "I owe nothing", "hash": "0" * 64})
    assert "I owe nothing" not in svc.store.select("authorizations")[0]["agreement_text"]


def test_authorizations_are_immutable(client, svc):
    o = through_authorization(client, svc)
    with pytest.raises(StoreRejected):
        svc.store.update("authorizations", {"typed_name": "Someone Else"}, order_id=o["id"])
    with pytest.raises(StoreRejected):
        svc.store.delete("authorizations", order_id=o["id"])
    assert svc.store.select("authorizations", order_id=o["id"])[0]["typed_name"] == "Pat Owner"


def test_cannot_sign_twice(client, svc):
    o = through_authorization(client, svc)
    assert api(client, o, "/authorize", json=SIGN).status_code == 409
    assert len(svc.store.select("authorizations")) == 1


# -- verification -------------------------------------------------------------------

def test_verify_requires_authorization_first(client, svc):
    o = through_intake(client, svc)
    assert api(client, o, "/verify").status_code == 409


def test_verify_by_dns_file_and_failure(client, svc):
    o = through_authorization(client, svc)
    ins = orders.verification_instructions(svc, o)
    assert ins["txt_host"] == "_phpshield-verify.example.com" and ins["txt_value"] == f"phpshield-verify={ins['token']}"

    res = verification.verify_order(svc, o, dns_check=lambda h, v: False, file_check=lambda d, t: False)
    assert res["verified"] is False and svc.store.select("orders", id=o["id"])[0]["status"] == "authorized"

    seen = {}
    res = verification.verify_order(svc, o, dns_check=lambda h, v: seen.update(h=h, v=v) or False,
                                    file_check=lambda d, t: d == "example.com" and t == ins["token"])
    assert res == {"verified": True, "method": "file", "detail": "Ownership verified via file."}
    assert seen == {"h": ins["txt_host"], "v": ins["txt_value"]}
    assert svc.store.select("orders", id=o["id"])[0]["status"] == "verified"
    assert svc.store.select("domain_verifications", order_id=o["id"])[0]["method"] == "file"


def test_file_check_requires_exact_token(svc):
    from app.php_shield import netsafe

    def fetcher(body, status=200):
        return lambda url: netsafe.Response(status=status, headers={}, body=body)

    assert verification.check_file("example.com", "tok123", fetcher("tok123\n"))
    assert verification.check_file("example.com", "tok123", fetcher("phpshield-verify=tok123"))
    assert not verification.check_file("example.com", "tok123", fetcher("<html>tok123</html>"))
    assert not verification.check_file("example.com", "tok123", fetcher("tok123", status=404))

    def raising(url):
        raise netsafe.UnsafeURL("blocked")

    assert not verification.check_file("example.com", "tok123", raising)


# -- THE GATE ---------------------------------------------------------------------

def test_gate_blocks_in_progress_without_authorization_via_api(client, svc):
    o = through_intake(client, svc)  # paid + intake, NOT signed
    r = client.post(f"/php-shield/admin/orders/{o['id']}/advance", json={"to": "in_progress"}, headers={"X-Admin-Key": "admin-test-key"})
    assert r.status_code == 409
    assert svc.store.select("orders", id=o["id"])[0]["status"] == "intake_complete"


@pytest.mark.parametrize("target", ["authorized", "verified", "in_progress"])
def test_gate_blocks_every_late_status_without_valid_authorization(client, svc, target):
    o = through_intake(client, svc)
    # force the status forward the way a bug or bad actor would, bypassing the sequence
    svc.store.update("orders", {"status": {"authorized": "intake_complete", "verified": "authorized", "in_progress": "verified"}[target]}, id=o["id"])
    with pytest.raises(orders.GateError):
        orders.transition(svc, o["id"], target, "admin")


def test_gate_requires_verified_ownership_even_with_signature(client, svc):
    o = through_authorization(client, svc)
    svc.store.update("orders", {"status": "verified"}, id=o["id"])  # claim verified without proof
    with pytest.raises(orders.GateError, match="verified"):
        orders.start_work(svc, o["id"], "admin")


def test_gate_authorization_must_match_the_orders_domain(client, svc):
    o = through_intake(client, svc)
    svc.store.insert("authorizations", {"order_id": o["id"], "domain": "evil-other-site.com", "typed_name": "Pat Owner",
                                        "agreement_version": "v", "agreement_hash": "a" * 64, "agreement_text": "t",
                                        "signed_at": iso(), "ip": "1.1.1.1", "user_agent": "x"})
    assert orders.valid_authorization(svc, o) is None
    with pytest.raises(orders.GateError):
        orders.transition(svc, o["id"], "authorized", "customer")


def test_gate_authorization_for_a_different_order_does_not_count(client, svc):
    a = through_authorization(client, svc, domain="example.com")
    b = through_intake(client, svc, domain="example.com")  # same domain, different order
    assert orders.valid_authorization(svc, b) is None
    assert orders.valid_authorization(svc, a) is not None


def test_revoked_authorization_blocks_work(client, svc):
    o = verified_order(client, svc)
    assert api(client, o, "/revoke", json={"reason": "changed my mind"}).status_code == 200
    assert any("REVOKED" in m["subject"] for m in svc.mailer.sent)
    with pytest.raises(orders.GateError):
        orders.start_work(svc, o["id"], "admin")


def test_in_progress_requires_payment(client, svc):
    o = verified_order(client, svc)
    svc.store.update("orders", {"paid_at": None}, id=o["id"])
    with pytest.raises(orders.GateError, match="payment"):
        orders.start_work(svc, o["id"], "admin")


def test_customers_cannot_start_work_and_sequence_cannot_be_skipped(client, svc):
    o = through_intake(client, svc)
    with pytest.raises(orders.OrderError):
        orders.transition(svc, o["id"], "verified", "customer")  # skipping authorized
    r = client.post(f"/php-shield/admin/orders/{o['id']}/advance", json={"to": "verified"}, headers={"X-Admin-Key": "admin-test-key"})
    assert r.status_code == 400  # admin endpoint only allows start/close/cancel


# -- delivery -----------------------------------------------------------------------

def rescan(version):
    return lambda url: ScanResult(url=url, domain="example.com", php_detected=True, version=version, confidence="high",
                                  risk=risk_report(version), scanned_at=iso())


def test_full_happy_path_to_delivered_and_closed(client, svc):
    o = verified_order(client, svc)
    started = client.post(f"/php-shield/admin/orders/{o['id']}/advance", json={"to": "in_progress"}, headers={"X-Admin-Key": "admin-test-key"})
    assert started.status_code == 200 and started.json()["status"] == "in_progress"

    with pytest.raises(orders.OrderError, match="checklist incomplete"):
        orders.deliver(svc, o["id"], "admin", scanner=rescan("8.3.1"))
    for item in svc.store.select("orders", id=o["id"])[0]["checklist"]:
        client.post(f"/php-shield/admin/orders/{o['id']}/checklist", json={"key": item, "done": True}, headers={"X-Admin-Key": "admin-test-key"})
    done = orders.deliver(svc, o["id"], "admin", scanner=rescan("8.3.1"))
    assert done["status"] == "delivered" and done["delivered_at"]
    after = svc.store.select("scan_reports", order_id=o["id"], kind="after")[0]
    assert after["version"] == "8.3.1"
    mail = [m for m in svc.mailer.sent if "delivered" in m["subject"].lower()][0]
    assert mail["to"] == ["cust@example.com"] and "7.4.33" in mail["html"] and "8.3.1" in mail["html"]  # before AND after

    assert client.post(f"/php-shield/admin/orders/{o['id']}/advance", json={"to": "closed"}, headers={"X-Admin-Key": "admin-test-key"}).json()["status"] == "closed"
    # every step was recorded and customer-notified
    events = [e["to_status"] for e in svc.store.select("order_events", order_id=o["id"])]
    assert events == ["paid", "intake_complete", "authorized", "verified", "in_progress", "delivered", "closed"]
    subjects = " | ".join(m["subject"] for m in svc.mailer.sent if m["to"] == ["cust@example.com"])
    for phrase in ("Payment received", "Intake received", "Authorization signed", "Ownership verified", "started work", "delivered", "complete"):
        assert phrase in subjects


def test_owner_notified_of_paid_order_and_signature(client, svc):
    through_authorization(client, svc)
    owner = [m["subject"] for m in svc.mailer.sent if m["to"] == ["owner@example.com"]]
    assert any("New paid order" in s for s in owner) and any("Authorization signed" in s for s in owner)


def test_order_view_exposes_flags_and_verification_instructions(client, svc):
    o = through_authorization(client, svc)
    v = api(client, o, "", method="get").json()
    assert v["status"] == "authorized" and v["authorized"] and v["intake_complete"] and not v["verified"]
    assert v["verification"]["file_path"] == "/.well-known/phpshield-verify.txt"
    assert client.get("/php-shield/order/unknown-token").status_code == 404


# -- admin auth ---------------------------------------------------------------------

def test_admin_requires_key(client, svc, monkeypatch):
    assert client.get("/php-shield/admin/orders").status_code == 403
    assert client.get("/php-shield/admin/orders", headers={"X-Admin-Key": "wrong"}).status_code == 403
    assert client.get("/php-shield/admin/orders", headers={"X-Admin-Key": "admin-test-key"}).status_code == 200
    monkeypatch.delenv("PHP_SHIELD_ADMIN_API_KEY")
    assert client.get("/php-shield/admin/orders", headers={"X-Admin-Key": "anything"}).status_code == 503  # fails closed


# -- maintenance --------------------------------------------------------------------

def maintenance_sub(client, svc, due=True):
    o = verified_order(client, svc, tier="basic", maintenance=True)
    svc.store.insert("subscriptions", {"order_id": o["id"], "stripe_subscription_id": "sub_m", "domain": o["domain"],
                                       "customer_email": o["customer_email"], "status": "active",
                                       "next_scan_at": iso(utcnow() - timedelta(days=1) if due else utcnow() + timedelta(days=10))})
    return o


def test_monthly_rescan_emails_customer_and_alerts_owner_on_new_critical(client, svc):
    maintenance_sub(client, svc)
    svc.mailer.sent.clear()
    summary = maintenance.run_monthly(svc, scanner=rescan("7.4.33"))
    assert summary["scanned"] == 1 and summary["critical_alerts"] == 0  # previous scan was already critical
    assert any("monthly report" in m["subject"] for m in svc.mailer.sent if m["to"] == ["cust@example.com"])
    nxt = svc.store.select("subscriptions")[0]["next_scan_at"]
    assert nxt > iso(utcnow() + timedelta(days=29))
    assert maintenance.run_monthly(svc, scanner=rescan("7.4.33"))["due"] == 0  # not re-run until due again

    svc.store.update("subscriptions", {"next_scan_at": iso(utcnow() - timedelta(hours=1))})
    svc.store.update("scan_reports", {"risk_level": "low"}, kind="monthly")
    prior = svc.store.select("scan_reports", kind="monthly")[0]
    prior["result"]["risk"] = risk_report("8.4.1")
    svc.store.tables["scan_reports"][0]["result"] = prior["result"]
    s2 = maintenance.run_monthly(svc, scanner=rescan("7.4.33"))
    assert s2["critical_alerts"] == 1
    assert any("NEW CRITICAL" in m["subject"] and m["to"] == ["owner@example.com"] for m in svc.mailer.sent)


def test_maintenance_skips_not_due_canceled_and_unauthorized(client, svc):
    maintenance_sub(client, svc, due=False)
    assert maintenance.run_monthly(svc, scanner=rescan("7.4.33"))["due"] == 0

    svc.store.update("subscriptions", {"next_scan_at": iso(utcnow() - timedelta(days=1)), "status": "canceled"})
    assert maintenance.run_monthly(svc, scanner=rescan("7.4.33"))["due"] == 0

    svc.store.update("subscriptions", {"status": "active"})
    svc.store.insert("authorization_revocations", {"order_id": svc.store.select("subscriptions")[0]["order_id"]})
    calls = []
    s = maintenance.run_monthly(svc, scanner=lambda u: calls.append(u) or rescan("7.4.33")(u))
    assert s["skipped_no_consent"] == 1 and s["scanned"] == 0 and not calls  # no consent -> never scanned


def test_one_failing_subscription_does_not_stop_the_batch(client, svc):
    maintenance_sub(client, svc)
    svc.store.insert("subscriptions", {"order_id": "missing", "stripe_subscription_id": "sub_bad", "domain": "x.com",
                                       "customer_email": "x@x.com", "status": "active", "next_scan_at": iso(utcnow() - timedelta(days=2))})
    s = maintenance.run_monthly(svc, scanner=rescan("7.4.33"))
    assert s["errors"] == 1 and s["scanned"] == 1
