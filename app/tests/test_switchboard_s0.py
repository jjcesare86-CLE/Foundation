"""
S0 tests (Addendum F): startup guard, workspace JWT, suspended workspaces, and
the dual-mode repository layer. Runs the SAME API scenarios in `foundation`
and `switchboard` mode against in-memory fakes of the two Supabase projects,
so it needs no credentials and never touches a live database.

What these tests do NOT prove (they need the live Switchboard project and its
env vars, see docs/state/BLOCKED_ON_JOHN.md): that the project's real signing
secret verifies the minted token, and that a Foundation key is rejected by the
Switchboard project. Cross-workspace RLS on the live database is covered by the
SQL gate in the switchboard repo (supabase/tests/rls_cross_workspace.sql).
"""
import sys
import types
import uuid

import jwt as pyjwt
import pytest

# Import without credentials: stand in for app.database only if it is not already
# importable with real env (the fixtures below re-point every module at fakes anyway).
if "app.database" not in sys.modules:
    _fake_db_mod = types.ModuleType("app.database")
    _fake_db_mod.supabase = None
    sys.modules["app.database"] = _fake_db_mod

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.switchboard import auth, repo, router as sb_router, switchboard_db  # noqa: E402

WS_A, WS_B = str(uuid.uuid4()), str(uuid.uuid4())
U_A, U_B = str(uuid.uuid4()), str(uuid.uuid4())

PK = {"sb_workspaces": ("id",), "sb_pins": ("client_id", "user_id", "agent_slug"),
      "sb_settings": ("client_id", "user_id"), "sb_memberships": ("workspace_id", "user_id")}


class _Res:
    def __init__(self, data): self.data = data


class _Query:
    def __init__(self, db, key):
        self.db, self.key, self.filters, self.op, self.payload = db, key, [], "select", None
        self._order, self._limit = None, None

    def select(self, *_a, **_k): return self
    def insert(self, row): self.op, self.payload = "insert", row; return self
    def upsert(self, row): self.op, self.payload = "upsert", row; return self
    def update(self, vals): self.op, self.payload = "update", vals; return self
    def delete(self): self.op = "delete"; return self
    def eq(self, col, val): self.filters.append(lambda r: str(r.get(col)) == str(val)); return self
    def is_(self, col, val): self.filters.append(lambda r: r.get(col) is None); return self
    def order(self, col, desc=False): self._order = (col, desc); return self
    def limit(self, n): self._limit = n; return self

    def execute(self):
        rows = self.db.tables.setdefault(self.key, [])
        name = self.key[1]
        if self.op == "insert":
            row = dict(self.payload)
            row.setdefault("id", str(uuid.uuid4())) if name in ("sb_threads", "sb_messages") else None
            row.setdefault("created_at", f"2026-10-22T00:00:{len(rows):02d}")
            if name == "sb_threads":
                row.setdefault("unread_count", 0)
            rows.append(row)
            return _Res([dict(row)])
        if self.op == "upsert":
            row, keys = dict(self.payload), PK.get(name, ("id",))
            for r in rows:
                if all(str(r.get(k)) == str(row.get(k)) for k in keys):
                    r.update(row); return _Res([dict(r)])
            rows.append(row); return _Res([dict(row)])
        hit = [r for r in rows if all(f(r) for f in self.filters)]
        if self.op == "update":
            for r in hit: r.update(self.payload)
            return _Res([dict(r) for r in hit])
        if self.op == "delete":
            for r in hit: rows.remove(r)
            return _Res([dict(r) for r in hit])
        out = [dict(r) for r in hit]
        if self._order:
            col, desc = self._order
            out.sort(key=lambda r: str(r.get(col)), reverse=desc)
        return _Res(out[: self._limit] if self._limit else out)


class FakeDB:
    def __init__(self, schema=None): self.tables, self._schema = {}, schema
    def schema(self, s): self._schema = s; return self
    def table(self, name):
        key = (self._schema or "public", name)
        self._schema = None if self._schema != "public" else self._schema
        return _Query(self, key)
    def rows(self, schema, name): return self.tables.get((schema, name), [])


@pytest.fixture
def env(monkeypatch):
    foundation, sbdb = FakeDB(), FakeDB()
    for mod in (repo, auth, sb_router):
        monkeypatch.setattr(mod, "supabase", foundation)
    monkeypatch.setattr(switchboard_db, "_client", sbdb)
    monkeypatch.setattr(switchboard_db, "client", lambda: sbdb)
    monkeypatch.setattr(switchboard_db, "is_configured", lambda: True)
    monkeypatch.setattr(auth, "SWITCHBOARD_JWT_SECRET", "api-secret-1")
    monkeypatch.setenv("SWITCHBOARD_SUPABASE_JWT_SECRET", "db-secret-2")
    monkeypatch.setenv("SWITCHBOARD_SUPABASE_URL", "https://gytuxzlrsgbueabywxhh.supabase.co")
    monkeypatch.setenv("SWITCHBOARD_SUPABASE_ANON_KEY", "sb-anon")
    repo._last_sync.clear()

    f = foundation.table  # seed Foundation-owned tables
    foundation.schema("foundation").table("ai_employees").insert({"id": "rahab", "is_active": True, "biblical_name": "Rahab"}).execute()
    foundation.schema("foundation").table("ai_employees").insert({"id": "solomon", "is_active": True, "biblical_name": "Solomon"}).execute()
    for ws, name in ((WS_A, "Alpha Co"), (WS_B, "Bravo Co")):
        foundation.schema("foundation").table("client_profiles").insert({"id": ws, "business_name": name, "status": "active"}).execute()

    monkeypatch.setattr(sb_router, "get_entitlement_mask", lambda ws: {"rahab": True, "solomon": False})
    monkeypatch.setattr(sb_router, "generate_reply", lambda agent, thread, history, text: f"echo:{text}")

    async def fake_verify(token, host="an"):
        return {"user_id": {"tokA": U_A, "tokB": U_B}[token], "email": None}
    monkeypatch.setattr(sb_router, "verify_host_token", fake_verify)

    app = FastAPI()
    app.include_router(sb_router.router)
    return types.SimpleNamespace(foundation=foundation, sbdb=sbdb, client=TestClient(app), monkeypatch=monkeypatch)


def _mode(env, mode):
    env.monkeypatch.setenv("SWITCHBOARD_DB_MODE", mode)
    store = env.sbdb if mode == "switchboard" else env.foundation
    schema = "public" if mode == "switchboard" else "foundation"
    for ws, u in ((WS_A, U_A), (WS_B, U_B)):
        if mode == "switchboard":
            repo.sync_workspace(ws)
        (env.sbdb if mode == "switchboard" else env.foundation).schema(schema).table("sb_memberships").insert(
            {"workspace_id": ws, "user_id": u, "role": "owner"}).execute()
    return store, schema


def _auth(env, tok):
    r = env.client.post("/switchboard/auth/exchange", json={"access_token": tok})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


MODES = ["foundation", "switchboard"]


@pytest.mark.parametrize("mode", MODES)
def test_conversation_flow_lands_in_the_selected_database(env, mode):
    store, schema = _mode(env, mode)
    other, other_schema = (env.foundation, "foundation") if mode == "switchboard" else (env.sbdb, "public")
    h = _auth(env, "tokA")

    assert env.client.get("/switchboard/bootstrap", headers=h).json()["workspace_id"] == WS_A
    r = env.client.post("/switchboard/threads/rahab/messages", json={"text": "hi"}, headers=h)
    assert r.status_code == 200 and r.json()["reply"]["body"] == "echo:hi"
    thread = env.client.get("/switchboard/threads/rahab", headers=h).json()
    assert [m["body"] for m in thread["messages"]] == ["hi", "echo:hi"]
    assert env.client.post("/switchboard/pins", json={"agent_slug": "rahab", "action": "add"}, headers=h).status_code == 200

    assert len(store.rows(schema, "sb_threads")) == 1 and len(store.rows(schema, "sb_messages")) == 2
    assert len(store.rows(schema, "sb_pins")) == 1
    # nothing leaked into the other database
    assert other.rows(other_schema, "sb_threads") == [] and other.rows(other_schema, "sb_messages") == []
    if mode == "switchboard":
        assert {r["id"] for r in env.sbdb.rows("public", "sb_workspaces")} >= {WS_A}


@pytest.mark.parametrize("mode", MODES)
def test_users_cannot_see_each_others_threads(env, mode):
    _mode(env, mode)
    ha, hb = _auth(env, "tokA"), _auth(env, "tokB")
    env.client.post("/switchboard/threads/rahab/messages", json={"text": "secret-A"}, headers=ha)
    msgs = env.client.get("/switchboard/threads/rahab", headers=hb).json()["messages"]
    assert msgs == []
    assert env.client.get("/switchboard/bootstrap", headers=hb).json()["workspace_id"] == WS_B


@pytest.mark.parametrize("mode", MODES)
def test_locked_agent_and_unknown_pin_rejected(env, mode):
    _mode(env, mode)
    h = _auth(env, "tokA")
    assert env.client.get("/switchboard/threads/solomon", headers=h).status_code == 403
    assert env.client.post("/switchboard/pins", json={"agent_slug": "nobody", "action": "add"}, headers=h).status_code == 404


@pytest.mark.parametrize("mode", MODES)
def test_suspended_workspace_gets_no_token_and_loses_access(env, mode):
    _mode(env, mode)
    h = _auth(env, "tokA")
    assert env.client.get("/switchboard/bootstrap", headers=h).status_code == 200
    env.foundation.schema("foundation").table("client_profiles").update({"status": "suspended"}).eq("id", WS_A).execute()
    repo._last_sync.clear()  # cache TTL elapsed
    assert env.client.get("/switchboard/bootstrap", headers=h).status_code == 403   # existing session stops
    assert env.client.post("/switchboard/auth/exchange", json={"access_token": "tokA"}).status_code == 403
    assert env.client.post("/switchboard/token", json={"access_token": "tokA"}).status_code == 403
    # the mirror in the Switchboard project is marked so RLS stops serving it too
    mirror = [r for r in env.sbdb.rows("public", "sb_workspaces") if r["id"] == WS_A]
    assert mirror and mirror[0]["status"] == "suspended"
    # workspace B is unaffected
    assert env.client.post("/switchboard/token", json={"access_token": "tokB"}).status_code == 200


def test_workspace_token_claims_and_secret_separation(env):
    _mode(env, "switchboard")
    r = env.client.post("/switchboard/token", json={"access_token": "tokA"})
    assert r.status_code == 200
    body = r.json()
    claims = pyjwt.decode(body["token"], "db-secret-2", algorithms=["HS256"], audience="authenticated")
    assert claims["role"] == "authenticated" and claims["sb_role"] == "owner"
    assert claims["workspace_id"] == WS_A and claims["user_id"] == U_A and claims["exp"] - claims["iat"] == 3600
    with pytest.raises(pyjwt.InvalidTokenError):   # not verifiable with the API's own secret
        pyjwt.decode(body["token"], "api-secret-1", algorithms=["HS256"], audience="authenticated")
    # and the API token is rejected as a workspace JWT / vice versa
    api_tok = _auth(env, "tokA")["Authorization"].split()[1]
    with pytest.raises(pyjwt.InvalidTokenError):
        pyjwt.decode(api_tok, "db-secret-2", algorithms=["HS256"])
    bad = env.client.get("/switchboard/bootstrap", headers={"Authorization": f"Bearer {body['token']}"})
    assert bad.status_code == 401   # workspace JWT does not authenticate the Foundation API
    assert body["anon_key"] == "sb-anon" and "service" not in str(body).lower()


def test_token_endpoint_503_when_unconfigured(env, monkeypatch):
    monkeypatch.delenv("SWITCHBOARD_SUPABASE_ANON_KEY")
    assert env.client.post("/switchboard/token", json={"access_token": "tokA"}).status_code == 503


# ---- startup guard -------------------------------------------------------------------
GOOD = {
    "SUPABASE_URL": "https://rhtwtoinmiekttvunlzs.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "f-svc",
    "SUPABASE_ANON_KEY": "f-anon", "SWITCHBOARD_JWT_SECRET": "api-secret-1",
    "SWITCHBOARD_SUPABASE_URL": "https://gytuxzlrsgbueabywxhh.supabase.co",
    "SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY": "s-svc", "SWITCHBOARD_SUPABASE_ANON_KEY": "s-anon",
    "SWITCHBOARD_SUPABASE_JWT_SECRET": "db-secret-2", "SWITCHBOARD_PROJECT_REF": "gytuxzlrsgbueabywxhh",
}
ALL = set(GOOD) | {"SWITCHBOARD_DB_MODE", "SUPABASE_JWT_SECRET"}


def _set(monkeypatch, **over):
    for k in ALL: monkeypatch.delenv(k, raising=False)
    for k, v in {**GOOD, **over}.items():
        if v is None: monkeypatch.delenv(k, raising=False)
        else: monkeypatch.setenv(k, v)


def test_guard_accepts_valid_config_in_both_modes(monkeypatch):
    _set(monkeypatch); switchboard_db.validate_config()
    _set(monkeypatch, SWITCHBOARD_DB_MODE="switchboard"); switchboard_db.validate_config()


def test_guard_allows_unset_switchboard_vars_in_foundation_mode(monkeypatch):
    for k in ALL: monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("SUPABASE_URL", GOOD["SUPABASE_URL"])
    switchboard_db.validate_config()   # a deploy without the new vars must still boot


@pytest.mark.parametrize("over,why", [
    ({"SWITCHBOARD_SUPABASE_URL": GOOD["SUPABASE_URL"]}, "identical URLs"),
    ({"SWITCHBOARD_SUPABASE_URL": GOOD["SUPABASE_URL"].upper() + "/"}, "identical URLs, case/slash-insensitive"),
    ({"SWITCHBOARD_SUPABASE_URL": "https://rzsryxvlaezfvftqpvbx.supabase.co", "SWITCHBOARD_PROJECT_REF": None}, "AN project"),
    ({"SWITCHBOARD_SUPABASE_URL": "https://rhtwtoinmiekttvunlzs.supabase.co/", "SUPABASE_URL": "https://other.supabase.co", "SWITCHBOARD_PROJECT_REF": None}, "Foundation ref"),
    ({"SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY": "f-svc"}, "same service key"),
    ({"SWITCHBOARD_SUPABASE_ANON_KEY": "f-anon"}, "same anon key"),
    ({"SWITCHBOARD_SUPABASE_JWT_SECRET": "api-secret-1"}, "JWT secret reuse"),
    ({"SWITCHBOARD_PROJECT_REF": "someotherref"}, "ref mismatch"),
    ({"SWITCHBOARD_DB_MODE": "switchboard", "SWITCHBOARD_SUPABASE_JWT_SECRET": None}, "switchboard mode missing secret"),
    ({"SWITCHBOARD_DB_MODE": "bogus"}, "invalid mode"),
])
def test_guard_refuses_to_boot(monkeypatch, over, why):
    _set(monkeypatch, **over)
    with pytest.raises(switchboard_db.SwitchboardConfigError):
        switchboard_db.validate_config()
