"""
Runs the real migrations against a real PostgreSQL and checks the database-enforced guards.

Skipped unless PHP_SHIELD_TEST_PG_DSN is set, e.g.
    PHP_SHIELD_TEST_PG_DSN=postgresql://postgres@localhost:54329/postgres
(any scratch server will do; each test run creates and drops its own database).
auth.role() is stubbed the way Supabase defines it (reads the request JWT claim).
"""
import os
import pathlib
import uuid
from urllib.parse import urlparse
from datetime import datetime, timezone

import pytest

pg8000 = pytest.importorskip("pg8000.dbapi")
pg8000_native = pytest.importorskip("pg8000.native")
DSN = os.getenv("PHP_SHIELD_TEST_PG_DSN")
pytestmark = pytest.mark.skipif(not DSN, reason="PHP_SHIELD_TEST_PG_DSN not set")

MIGRATIONS = sorted((pathlib.Path(__file__).parents[3] / "supabase-php-shield" / "migrations").glob("*.sql"))

SUPABASE_STUB = """
create schema if not exists auth;
create or replace function auth.role() returns text language sql stable as
  $$ select coalesce(nullif(current_setting('request.jwt.claim.role', true), ''), 'anon') $$;
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then create role anon nologin; end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then create role service_role nologin; end if;
end $$;
"""
GRANTS = """
grant usage on schema public to anon, service_role;
grant all on all tables in schema public to anon, service_role;
"""


def _native(dsn):
    u = urlparse(dsn)
    return pg8000_native.Connection(u.username or "postgres", host=u.hostname, port=u.port or 5432,
                                    database=(u.path or "/postgres").lstrip("/"), password=u.password)


def _run_script(dsn, sql):
    c = _native(dsn)
    c.run(sql)  # simple-query protocol: multiple statements allowed
    c.close()


@pytest.fixture(scope="module")
def dbname():
    name = f"phpshield_test_{uuid.uuid4().hex[:8]}"
    base = DSN.rsplit("/", 1)[0]
    admin = _native(DSN)
    admin.run(f'create database "{name}"')
    _run_script(f"{base}/{name}", SUPABASE_STUB)
    for m in MIGRATIONS:
        _run_script(f"{base}/{name}", m.read_text(encoding="utf-8"))
    _run_script(f"{base}/{name}", GRANTS)
    yield f"{base}/{name}"
    admin.run(f'drop database "{name}" with (force)')
    admin.close()


@pytest.fixture
def cur(dbname):
    u = urlparse(dbname)
    conn = pg8000.connect(user=u.username or "postgres", host=u.hostname, port=u.port or 5432,
                          database=u.path.lstrip("/"), password=u.password)
    yield conn.cursor()
    conn.rollback()
    conn.close()


def fails(cur, sql, params=None, exc=Exception):
    """Statement must be rejected by the database; a savepoint keeps the test transaction usable."""
    cur.execute("savepoint guard")
    try:
        cur.execute(sql, params or ())
    except pg8000.DatabaseError as e:
        cur.execute("rollback to savepoint guard")
        return str(e)
    cur.execute("rollback to savepoint guard")
    raise AssertionError("statement was accepted but should have been rejected: " + sql[:80])


def new_order(cur, domain="example.com", tier="standard"):
    cur.execute("insert into orders (public_token, domain, customer_email, tier) values (%s,%s,'c@example.com',%s) returning id",
                (uuid.uuid4().hex, domain, tier))
    return cur.fetchone()[0]


def set_status(cur, oid, status, **extra):
    sets = ", ".join(["status=%s"] + [f"{k}=%s" for k in extra])
    cur.execute(f"update orders set {sets} where id=%s", (status, *extra.values(), oid))


def add_intake(cur, oid):
    cur.execute("insert into intake (order_id, site_url, hosting_provider, access_method, has_staging_or_backup, preferred_timing,"
                " contact_name, contact_email) values (%s,'https://example.com','h','sftp','backup','now','n','e@x.com')", (oid,))


def add_auth(cur, oid, domain="example.com"):
    cur.execute("insert into authorizations (order_id, domain, typed_name, agreement_version, agreement_hash, agreement_text, ip, user_agent)"
                " values (%s,%s,'Pat Owner','v1',%s,'text','1.2.3.4','ua')", (oid, domain, "a" * 64))


def add_verification(cur, oid, domain="example.com", verified=True):
    cur.execute("insert into domain_verifications (order_id, domain, token, verified_at) values (%s,%s,'tok', %s)",
                (oid, domain, datetime.now(timezone.utc) if verified else None))


def order_at(cur, upto):
    """Walk an order through the legitimate path as far as `upto`."""
    flow = ["paid", "intake_complete", "authorized", "verified", "in_progress"]
    oid = new_order(cur)
    for step in flow[: flow.index(upto) + 1]:
        if step == "paid":
            set_status(cur, oid, "paid", paid_at="2026-01-01")
        elif step == "intake_complete":
            add_intake(cur, oid); set_status(cur, oid, "intake_complete")
        elif step == "authorized":
            add_auth(cur, oid); set_status(cur, oid, "authorized")
        elif step == "verified":
            add_verification(cur, oid); set_status(cur, oid, "verified")
        elif step == "in_progress":
            set_status(cur, oid, "in_progress")
    return oid


# -- migrations -----------------------------------------------------------------

def test_migrations_are_idempotent(dbname):
    for _ in range(2):
        for m in MIGRATIONS:
            _run_script(dbname, m.read_text(encoding="utf-8"))


def test_every_table_has_rls_enabled(cur):
    cur.execute("select c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace "
                "where n.nspname='public' and c.relkind='r' and not c.relrowsecurity")
    assert list(cur.fetchall()) == []


def test_policy_naming_follows_service_role_all_convention(cur):
    cur.execute("select tablename, policyname from pg_policies where schemaname='public'")
    pol = {(t, p) for t, p in cur.fetchall()}
    for t in ("leads", "orders", "intake", "subscriptions", "webhook_events", "scan_events"):
        assert (t, f"service_role_all_{t}") in pol
    for t in ("authorizations", "authorization_revocations"):
        assert (t, f"service_role_select_{t}") in pol and (t, f"service_role_insert_{t}") in pol
        assert (t, f"service_role_all_{t}") not in pol  # no UPDATE/DELETE policy


# -- happy path -----------------------------------------------------------------

def test_legitimate_path_reaches_delivered_and_closed(cur):
    oid = order_at(cur, "in_progress")
    set_status(cur, oid, "delivered")
    set_status(cur, oid, "closed")
    cur.execute("select status, updated_at is not null from orders where id=%s", (oid,))
    assert tuple(cur.fetchone()) == ("closed", True)


# -- state machine ----------------------------------------------------------------

def test_orders_must_start_pending_payment(cur):
    assert "pending_payment" in fails(cur, "insert into orders (public_token, domain, customer_email, tier, status) "
                                           "values ('t','x.com','a@b.co','basic','paid')")


@pytest.mark.parametrize("frm,to", [("pending_payment", "intake_complete"), ("pending_payment", "in_progress"),
                                    ("paid", "authorized"), ("paid", "in_progress"), ("paid", "delivered")])
def test_cannot_skip_steps(cur, frm, to):
    oid = new_order(cur)
    if frm == "paid":
        set_status(cur, oid, "paid", paid_at="2026-01-01")
    assert "illegal order transition" in fails(cur, "update orders set status=%s where id=%s", (to, oid))


def test_cannot_go_backwards_or_leave_terminal_states(cur):
    oid = order_at(cur, "in_progress")
    assert "illegal" in fails(cur, "update orders set status='verified' where id=%s", (oid,))
    set_status(cur, oid, "delivered"); set_status(cur, oid, "closed")
    assert "illegal" in fails(cur, "update orders set status='in_progress' where id=%s", (oid,))


def test_intake_complete_requires_an_intake_row(cur):
    oid = new_order(cur)
    set_status(cur, oid, "paid", paid_at="2026-01-01")
    assert "intake" in fails(cur, "update orders set status='intake_complete' where id=%s", (oid,))


def test_order_domain_is_immutable(cur):
    oid = new_order(cur)
    assert "immutable" in fails(cur, "update orders set domain='other.com' where id=%s", (oid,))


# -- THE GATE (database backstop) ---------------------------------------------------

def test_gate_authorized_requires_signed_authorization(cur):
    oid = order_at(cur, "intake_complete")
    assert "valid signed authorization" in fails(cur, "update orders set status='authorized' where id=%s", (oid,))


def test_gate_verified_requires_verified_domain(cur):
    oid = order_at(cur, "authorized")
    add_verification(cur, oid, verified=False)
    assert "ownership" in fails(cur, "update orders set status='verified' where id=%s", (oid,))


def test_gate_in_progress_requires_everything(cur):
    oid = order_at(cur, "verified")
    cur.execute("update orders set paid_at=null where id=%s", (oid,))
    assert "before payment" in fails(cur, "update orders set status='in_progress' where id=%s", (oid,))


def test_gate_revoked_authorization_blocks_in_progress(cur):
    oid = order_at(cur, "verified")
    cur.execute("insert into authorization_revocations (order_id, reason) values (%s,'changed my mind')", (oid,))
    assert "valid signed authorization" in fails(cur, "update orders set status='in_progress' where id=%s", (oid,))


def test_gate_verification_for_another_domain_does_not_count(cur):
    oid = order_at(cur, "authorized")
    add_verification(cur, oid, domain="attacker-controlled.com")
    assert "ownership" in fails(cur, "update orders set status='verified' where id=%s", (oid,))


def test_authorization_only_when_order_is_intake_complete_and_domain_matches(cur):
    oid = new_order(cur)
    assert "intake_complete" in fails(cur, "insert into authorizations (order_id, domain, typed_name, agreement_version, agreement_hash,"
                                           " agreement_text, ip, user_agent) values (%s,'example.com','Pat Owner','v',%s,'t','1.1.1.1','u')", (oid, "b" * 64))
    set_status(cur, oid, "paid", paid_at="2026-01-01"); add_intake(cur, oid); set_status(cur, oid, "intake_complete")
    assert "does not match" in fails(cur, "insert into authorizations (order_id, domain, typed_name, agreement_version, agreement_hash,"
                                          " agreement_text, ip, user_agent) values (%s,'different.com','Pat Owner','v',%s,'t','1.1.1.1','u')", (oid, "b" * 64))


def test_authorization_row_constraints(cur):
    oid = order_at(cur, "intake_complete")
    assert fails(cur, "insert into authorizations (order_id, domain, typed_name, agreement_version, agreement_hash, agreement_text, ip, user_agent)"
                      " values (%s,'example.com','Pat Owner','v','not-a-sha256','t','1.1.1.1','u')", (oid,))
    assert fails(cur, "insert into authorizations (order_id, domain, typed_name, agreement_version, agreement_hash, agreement_text, ip, user_agent)"
                      " values (%s,'example.com','  ','v',%s,'t','1.1.1.1','u')", (oid, "c" * 64))


# -- immutability ---------------------------------------------------------------------

def test_authorizations_are_append_only_even_for_superuser(cur):
    oid = order_at(cur, "authorized")
    assert "append-only" in fails(cur, "update authorizations set typed_name='Mallory Evil' where order_id=%s", (oid,))
    assert "append-only" in fails(cur, "delete from authorizations where order_id=%s", (oid,))
    assert "append-only" in fails(cur, "truncate authorizations")
    cur.execute("select typed_name from authorizations where order_id=%s", (oid,))
    assert cur.fetchone()[0] == "Pat Owner"


def test_revocations_are_append_only(cur):
    oid = order_at(cur, "authorized")
    cur.execute("insert into authorization_revocations (order_id) values (%s)", (oid,))
    assert "append-only" in fails(cur, "delete from authorization_revocations where order_id=%s", (oid,))
    assert "append-only" in fails(cur, "update authorization_revocations set reason='x' where order_id=%s", (oid,))


def test_one_authorization_per_order(cur):
    oid = order_at(cur, "authorized")
    assert fails(cur, "insert into authorizations (order_id, domain, typed_name, agreement_version, agreement_hash, agreement_text, ip, user_agent)"
                      " values (%s,'example.com','Pat Owner','v',%s,'t','1.1.1.1','u')", (oid, "d" * 64))


# -- RLS --------------------------------------------------------------------------------

def _as(cur, role, claim):
    cur.execute(f"set local role {role}")
    cur.execute("select set_config('request.jwt.claim.role', %s, true)", (claim,))


def test_anon_role_sees_and_writes_nothing(cur):
    cur.execute("insert into leads (report_token, url, domain, contact_email, consent_scan, consent_text) "
                "values ('t','https://a.com','a.com','e@x.com',true,'c')")
    _as(cur, "anon", "anon")
    cur.execute("select count(*) from leads")
    assert cur.fetchone()[0] == 0
    assert "row-level security" in fails(cur, "insert into leads (report_token, url, domain, contact_email, consent_scan, consent_text) "
                                              "values ('t2','https://b.com','b.com','e@x.com',true,'c')")


def test_service_role_can_use_tables_but_cannot_update_authorizations(cur):
    oid = order_at(cur, "authorized")
    _as(cur, "service_role", "service_role")
    cur.execute("select count(*) from authorizations where order_id=%s", (oid,))
    assert cur.fetchone()[0] == 1
    cur.execute("select count(*) from orders")
    assert cur.fetchone()[0] >= 1
    # no UPDATE/DELETE policy: RLS hides the row from the write, so nothing is changed (and the trigger backstops superusers)
    cur.execute("update authorizations set typed_name='Mallory Evil' where order_id=%s", (oid,))
    assert cur.rowcount == 0


def test_lead_requires_consent(cur):
    assert fails(cur, "insert into leads (report_token, url, domain, contact_email, consent_scan, consent_text) "
                      "values ('t','https://a.com','a.com','e@x.com',false,'c')")


def test_order_needs_a_tier_or_maintenance(cur):
    assert fails(cur, "insert into orders (public_token, domain, customer_email, tier, maintenance) values ('t','a.com','e@x.com',null,false)")
    cur.execute("insert into orders (public_token, domain, customer_email, tier, maintenance) values ('t2','a.com','e@x.com',null,true)")
