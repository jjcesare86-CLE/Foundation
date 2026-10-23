"""Rate limit + Turnstile tests."""
from types import SimpleNamespace

import pytest

from app.php_shield import turnstile
from app.php_shield.ratelimit import Busy, RateLimited, RateLimiter, SimpleLimiter, client_ip, hash_ip
from app.php_shield.store import MemoryStore, StoreError


def limiter(**kw):
    return RateLimiter(MemoryStore(), **kw)


def test_per_ip_limit_is_5_per_hour_with_retry_after():
    rl = limiter()
    for i in range(5):
        rl.check_and_record("1.2.3.4", f"site{i}.com")
    with pytest.raises(RateLimited) as e:
        rl.check_and_record("1.2.3.4", "another.com")
    assert e.value.scope == "ip" and 3500 < e.value.retry_after <= 3600
    rl.check_and_record("5.6.7.8", "another.com")  # a different IP is unaffected


def test_per_domain_limit_is_3_per_day_across_ips():
    rl = limiter()
    for i in range(3):
        rl.check_and_record(f"9.9.9.{i}", "target.com")
    with pytest.raises(RateLimited) as e:
        rl.check_and_record("9.9.9.99", "target.com")
    assert e.value.scope == "domain" and e.value.retry_after > 80000
    rl.check_and_record("9.9.9.99", "other.com")


def test_global_daily_cap():
    rl = limiter(global_per_day=4, ip_per_hour=100, domain_per_day=100)
    for i in range(4):
        rl.check_and_record(f"1.1.1.{i}", f"s{i}.com")
    with pytest.raises(RateLimited) as e:
        rl.check_and_record("2.2.2.2", "new.com")
    assert e.value.scope == "global"


def test_failed_scans_still_count():
    rl = limiter()
    for _ in range(3):
        rl.check_and_record("1.2.3.4", "x.com")  # recorded up-front regardless of outcome
    with pytest.raises(RateLimited):
        rl.check_and_record("1.2.3.4", "x.com")


def test_window_expiry_releases_the_limit():
    store = MemoryStore()
    rl = RateLimiter(store, ip_per_hour=1)
    rl.check_and_record("1.2.3.4", "a.com")
    store.tables["scan_events"][0]["created_at"] = "2020-01-01T00:00:00+00:00"
    rl.check_and_record("1.2.3.4", "b.com")


def test_concurrency_cap():
    rl = limiter(max_concurrent=2)
    with rl.slot():
        with rl.slot():
            with pytest.raises(Busy):
                with rl.slot():
                    pass
    with rl.slot():  # released
        pass


def test_limits_do_not_fail_open_when_store_is_down():
    class Down(MemoryStore):
        def select_since(self, *a, **k):
            raise StoreError("db down")

        def insert(self, *a, **k):
            raise StoreError("db down")

    rl = RateLimiter(Down(), ip_per_hour=2)
    rl.check_and_record("1.2.3.4", "a.com")
    rl.check_and_record("1.2.3.4", "b.com")
    with pytest.raises(RateLimited):
        rl.check_and_record("1.2.3.4", "c.com")


def test_simple_limiter():
    sl = SimpleLimiter()
    for _ in range(3):
        sl.check("checkout:1.1.1.1", 3)
    with pytest.raises(RateLimited) as e:
        sl.check("checkout:1.1.1.1", 3)
    assert e.value.retry_after > 0
    sl.check("checkout:2.2.2.2", 3)


def test_client_ip_uses_rightmost_forwarded_entry_not_spoofable_leftmost():
    req = SimpleNamespace(headers={"x-forwarded-for": "6.6.6.6, 203.0.113.7"}, client=SimpleNamespace(host="10.0.0.1"))
    assert client_ip(req) == "203.0.113.7"
    assert client_ip(SimpleNamespace(headers={}, client=SimpleNamespace(host="10.0.0.1"))) == "10.0.0.1"


def test_ip_hash_is_stable_and_not_the_raw_ip():
    assert hash_ip("1.2.3.4") == hash_ip("1.2.3.4") != hash_ip("1.2.3.5")
    assert "1.2.3.4" not in hash_ip("1.2.3.4")


# -- Turnstile ----------------------------------------------------------------

class FakeResp:
    def __init__(self, ok):
        self.ok = ok

    def json(self):
        return {"success": self.ok}


def test_turnstile_skipped_when_secret_unset(monkeypatch):
    monkeypatch.delenv("TURNSTILE_SECRET", raising=False)
    assert not turnstile.enabled() and turnstile.verify(None)


def test_turnstile_enforced_when_secret_set(monkeypatch):
    monkeypatch.setenv("TURNSTILE_SECRET", "s")
    assert turnstile.enabled()
    assert not turnstile.verify(None)
    assert turnstile.verify("tok", post=lambda *a, **k: FakeResp(True))
    assert not turnstile.verify("tok", post=lambda *a, **k: FakeResp(False))

    def boom(*a, **k):
        raise RuntimeError("cloudflare down")

    assert not turnstile.verify("tok", post=boom)  # fails closed
