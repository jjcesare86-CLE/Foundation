"""
PHP Shield -- persistence layer.

`SupabaseStore` talks to PHP Shield's OWN Supabase project (PHP_SHIELD_SUPABASE_URL
+ PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY). `MemoryStore` is used by the test suite
and for local dev; it deliberately mimics the database rules the app depends on
(unique keys, immutable tables) so tests exercise the same failure modes.
"""
import copy
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional


class StoreError(RuntimeError):
    """Any persistence failure."""


class StoreConflict(StoreError):
    """Unique-key violation."""


class StoreRejected(StoreError):
    """A DB trigger/constraint refused the write (e.g. immutable table, fulfillment gate)."""


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: Optional[datetime] = None) -> str:
    return (dt or utcnow()).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class MemoryStore:
    IMMUTABLE = {"authorizations", "authorization_revocations"}
    UNIQUE = {
        "authorizations": ("order_id",),
        "authorization_revocations": ("order_id",),
        "domain_verifications": ("order_id",),
        "intake": ("order_id",),
        "orders": ("public_token",),
        "leads": ("report_token",),
        "webhook_events": ("event_id",),
        "subscriptions": ("stripe_subscription_id",),
    }

    def __init__(self):
        self.tables: dict[str, list[dict]] = {}
        self._lock = threading.RLock()

    def _rows(self, table):
        return self.tables.setdefault(table, [])

    def _check_unique(self, table, row):
        for cols in [self.UNIQUE.get(table, ())]:
            for col in cols:
                if row.get(col) is None:
                    continue
                if any(r.get(col) == row[col] for r in self._rows(table)):
                    raise StoreConflict(f"duplicate {table}.{col}")

    def insert(self, table: str, row: dict) -> dict:
        with self._lock:
            row = {"id": str(uuid.uuid4()), "created_at": iso(), **copy.deepcopy(row)}
            self._check_unique(table, row)
            self._rows(table).append(row)
            return copy.deepcopy(row)

    def insert_if_new(self, table: str, row: dict, key: str) -> bool:
        with self._lock:
            if any(r.get(key) == row.get(key) for r in self._rows(table)):
                return False
            self.insert(table, row)
            return True

    def select(self, table: str, **eq) -> list[dict]:
        with self._lock:
            return [copy.deepcopy(r) for r in self._rows(table) if all(r.get(k) == v for k, v in eq.items())]

    def select_since(self, table: str, since_iso: str, **eq) -> list[dict]:
        since = parse_iso(since_iso)
        return [r for r in self.select(table, **eq) if parse_iso(r["created_at"]) >= since]

    def update(self, table: str, patch: dict, **eq) -> list[dict]:
        if table in self.IMMUTABLE:
            raise StoreRejected(f"{table} is append-only")
        with self._lock:
            out = []
            for r in self._rows(table):
                if all(r.get(k) == v for k, v in eq.items()):
                    r.update(copy.deepcopy(patch))
                    r["updated_at"] = iso()
                    out.append(copy.deepcopy(r))
            return out

    def delete(self, table: str, **eq) -> int:
        if table in self.IMMUTABLE:
            raise StoreRejected(f"{table} is append-only")
        with self._lock:
            rows = self._rows(table)
            keep = [r for r in rows if not all(r.get(k) == v for k, v in eq.items())]
            n = len(rows) - len(keep)
            self.tables[table] = keep
            return n


class SupabaseStore:
    def __init__(self, url: str, key: str):
        from supabase import create_client

        self.client = create_client(url, key)

    @staticmethod
    def _wrap(exc: Exception) -> StoreError:
        code = str(getattr(exc, "code", "") or "")
        msg = str(getattr(exc, "message", "") or exc)
        if code == "23505":
            return StoreConflict(msg)
        if code in ("P0001", "23514", "23502"):
            return StoreRejected(msg)
        return StoreError(msg)

    def _q(self, fn):
        try:
            return fn()
        except StoreError:
            raise
        except Exception as e:  # postgrest APIError, httpx errors, ...
            raise self._wrap(e) from e

    def insert(self, table: str, row: dict) -> dict:
        data = self._q(lambda: self.client.table(table).insert(row).execute().data)
        return data[0] if data else row

    def insert_if_new(self, table: str, row: dict, key: str) -> bool:
        data = self._q(lambda: self.client.table(table).upsert(row, on_conflict=key, ignore_duplicates=True).execute().data)
        return bool(data)

    def select(self, table: str, **eq) -> list[dict]:
        def run():
            q = self.client.table(table).select("*")
            for k, v in eq.items():
                q = q.eq(k, v)
            return q.execute().data

        return self._q(run)

    def select_since(self, table: str, since_iso: str, **eq) -> list[dict]:
        def run():
            q = self.client.table(table).select("*").gte("created_at", since_iso)
            for k, v in eq.items():
                q = q.eq(k, v)
            return q.execute().data

        return self._q(run)

    def update(self, table: str, patch: dict, **eq) -> list[dict]:
        def run():
            q = self.client.table(table).update(patch)
            for k, v in eq.items():
                q = q.eq(k, v)
            return q.execute().data

        return self._q(run)

    def delete(self, table: str, **eq) -> int:
        def run():
            q = self.client.table(table).delete()
            for k, v in eq.items():
                q = q.eq(k, v)
            return len(q.execute().data or [])

        return self._q(run)
