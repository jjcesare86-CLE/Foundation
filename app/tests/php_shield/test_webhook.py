"""Stripe webhook: signature verification, idempotency, order/subscription state."""
import json
import time

from app.php_shield import orders
from tests.php_shield.conftest import make_lead, sign_webhook


def pending_order(svc, tier="standard", maintenance=False, domain="example.com"):
    return orders.create_order(svc, make_lead(svc, domain), tier, maintenance)


def completed_event(order, event_id="evt_1", sub=None, payment_status="paid", total=75000):
    return {"id": event_id, "type": "checkout.session.completed", "data": {"object": {
        "id": "cs_live_1", "client_reference_id": order["id"], "payment_status": payment_status, "customer": "cus_1",
        "subscription": sub, "amount_total": total, "customer_email": order["customer_email"],
        "metadata": {"order_id": order["id"]}}}}


def post(client, event, **kw):
    payload, headers = sign_webhook(event, **kw)
    return client.post("/php-shield/stripe/webhook", content=payload, headers=headers)


def test_unsigned_and_badly_signed_requests_are_rejected(client, svc):
    order = pending_order(svc)
    ev = completed_event(order)
    assert client.post("/php-shield/stripe/webhook", content=json.dumps(ev)).status_code == 400  # no signature
    assert post(client, ev, secret="whsec_wrong").status_code == 400
    assert post(client, ev, ts=int(time.time()) - 3600).status_code == 400  # replayed/stale timestamp
    payload, headers = sign_webhook(ev)
    assert client.post("/php-shield/stripe/webhook", content=payload + b" ", headers=headers).status_code == 400  # tampered body
    assert svc.store.select("orders")[0]["status"] == "pending_payment"
    assert not svc.store.select("webhook_events")


def test_checkout_completed_marks_paid_and_notifies_everyone(client, svc):
    order = pending_order(svc)
    r = post(client, completed_event(order))
    assert r.status_code == 200 and r.json()["result"] == "paid"
    o = svc.store.select("orders", id=order["id"])[0]
    assert o["status"] == "paid" and o["paid_at"] and o["stripe_customer_id"] == "cus_1" and o["amount_cents"] == 75000
    assert svc.store.select("order_events", order_id=order["id"])[-1]["to_status"] == "paid"
    to = {tuple(m["to"]): m["subject"] for m in svc.mailer.sent}
    assert ("owner@example.com",) in to and "New paid order" in to[("owner@example.com",)]
    cust = to[("cust@example.com",)]
    assert "Payment received" in cust
    body = [m for m in svc.mailer.sent if m["to"] == ["cust@example.com"]][0]["html"]
    assert f"/php-shield/order/{o['public_token']}" in body
    assert svc.store.select("leads", id=order["lead_id"])[0]["status"] == "converted"


def test_duplicate_event_is_idempotent(client, svc):
    order = pending_order(svc)
    ev = completed_event(order)
    assert post(client, ev).json().get("duplicate") is None
    emails = len(svc.mailer.sent)
    r = post(client, ev)
    assert r.status_code == 200 and r.json()["duplicate"] is True
    assert len(svc.mailer.sent) == emails and len(svc.store.select("order_events", order_id=order["id"])) == 1


def test_same_session_under_a_new_event_id_does_not_double_process(client, svc):
    order = pending_order(svc)
    post(client, completed_event(order, "evt_a"))
    emails = len(svc.mailer.sent)
    post(client, completed_event(order, "evt_b"))  # Stripe re-sent under a different event id
    assert len(svc.mailer.sent) == emails
    assert svc.store.select("orders", id=order["id"])[0]["status"] == "paid"


def test_unpaid_session_does_not_mark_paid(client, svc):
    order = pending_order(svc)
    post(client, completed_event(order, payment_status="unpaid"))
    assert svc.store.select("orders", id=order["id"])[0]["status"] == "pending_payment"


def test_subscription_flow_active_renew_cancel(client, svc):
    order = pending_order(svc, "basic", True)
    post(client, completed_event(order, "evt_1", sub="sub_9", total=39900))
    sub = svc.store.select("subscriptions", stripe_subscription_id="sub_9")[0]
    assert sub["status"] == "active" and sub["domain"] == "example.com" and sub["next_scan_at"]

    inv = {"id": "evt_2", "type": "invoice.paid", "data": {"object": {"subscription": "sub_9", "customer": "cus_1"}}}
    assert post(client, inv).json()["result"] == "subscription_renewed"
    assert svc.store.select("subscriptions", stripe_subscription_id="sub_9")[0]["last_invoice_paid_at"]
    assert len(svc.store.select("subscriptions")) == 1  # no duplicate row

    cancel = {"id": "evt_3", "type": "customer.subscription.deleted", "data": {"object": {"id": "sub_9"}}}
    assert post(client, cancel).json()["result"] == "canceled"
    assert svc.store.select("subscriptions", stripe_subscription_id="sub_9")[0]["status"] == "canceled"
    assert any("Maintenance canceled" in m["subject"] for m in svc.mailer.sent)
    assert post(client, {**cancel, "id": "evt_4"}).json()["result"] == "already_canceled"


def test_invoice_paid_arriving_before_checkout_completed_is_deferred_then_recovered(client, svc):
    order = pending_order(svc, "basic", True)
    inv = {"id": "evt_i", "type": "invoice.paid", "data": {"object": {
        "subscription": "sub_early", "customer": "cus_1", "subscription_details": {"metadata": {"order_id": order["id"]}}}}}
    assert post(client, inv).json()["result"] == "deferred"
    assert not svc.store.select("subscriptions")
    post(client, completed_event(order, "evt_c", sub="sub_early", total=39900))
    assert len(svc.store.select("subscriptions")) == 1


def test_paid_checkout_with_no_matching_order_alerts_owner(client, svc):
    ev = {"id": "evt_x", "type": "checkout.session.completed", "data": {"object": {
        "id": "cs_x", "client_reference_id": "no-such-order", "payment_status": "paid", "customer_email": "ghost@example.com"}}}
    assert post(client, ev).json()["result"] == "unmatched"
    assert any("PAID checkout with no matching order" in m["subject"] for m in svc.mailer.sent)


def test_failed_processing_releases_the_event_so_stripe_retries(client, svc):
    order = pending_order(svc)
    real = svc.store.update
    svc.store.update = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("db hiccup"))
    r = post(client, completed_event(order))
    assert r.status_code == 500
    assert not svc.store.select("webhook_events")  # not recorded -> the retry will be processed
    svc.store.update = real
    assert post(client, completed_event(order)).json()["result"] == "paid"


def test_unknown_event_types_are_acknowledged(client, svc):
    assert post(client, {"id": "evt_u", "type": "charge.refunded", "data": {"object": {}}}).json()["result"] == "ignored"


def test_webhook_secret_missing_fails_closed(client, svc, monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET")
    payload, headers = sign_webhook({"id": "e", "type": "x", "data": {"object": {}}})
    assert client.post("/php-shield/stripe/webhook", content=payload, headers=headers).status_code == 503
