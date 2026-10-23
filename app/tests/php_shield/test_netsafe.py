"""SSRF hardening tests: URL policy, IP policy, DNS pinning, redirects, transport caps."""
import http.server
import threading
import time

import pytest

from app.php_shield import netsafe
from app.php_shield.netsafe import FetchError, Response, Target, UnsafeURL, fetch, ip_is_blocked, validate_url

PUBLIC = "93.184.216.34"


# -- URL policy ---------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "ftp://example.com/", "file:///etc/passwd", "gopher://example.com/", "javascript:alert(1)",
    "http://user:pass@example.com/", "http://user@example.com/", "http://example.com@evil.com/",
    "http://example.com:8080/", "http://example.com:22/", "https://example.com:8443/", "http://example.com:0/",
    "http://localhost/", "http://LOCALHOST./", "http://foo/", "http://foo.local/", "http://foo.internal/",
    "http://metadata.google.internal/", "http://printer.lan/", "http://x.home.arpa/",
    "http://127.0.0.1/", "http://127.1/", "http://0.0.0.0/", "http://10.0.0.1/", "http://192.168.1.1/",
    "http://169.254.169.254/latest/meta-data/", "http://100.64.0.1/",
    "http://2130706433/", "http://0x7f000001/", "http://0177.0.0.1/", "http://017700000001/", "http://0x7f.0.0.1/",
    "http://[::1]/", "http://[::ffff:127.0.0.1]/", "http://[::ffff:169.254.169.254]/", "http://[fe80::1]/",
    "http://[fd00::1]/", "http://[2001:db8::1]/",
    "http://example.com\\@evil.com/", "http://exa mple.com/", "http://example.com/\x00", "http://example.com/\r\nX: y",
    "http://" + "a" * 64 + ".com/", "http://-bad.com/", "http://bad-.com/", "http://a..com/",
    "https://example.com/" + "a" * 2100,
])
def test_validate_url_rejects(url):
    with pytest.raises(UnsafeURL):
        validate_url(url)


@pytest.mark.parametrize("url,host,port", [
    ("https://example.com", "example.com", 443),
    ("http://example.com/a?b=1", "example.com", 80),
    ("https://EXAMPLE.com:443/x", "example.com", 443),
    ("http://sub.example.co.uk:80/", "sub.example.co.uk", 80),
    ("http://example.com./", "example.com", 80),
])
def test_validate_url_accepts(url, host, port):
    t = validate_url(url)
    assert (t.host, t.port) == (host, port)


def test_normalize_adds_https_and_blocks_scheme_tricks():
    assert netsafe.normalize_user_url("example.com") == "https://example.com"
    with pytest.raises(UnsafeURL):
        validate_url(netsafe.normalize_user_url("javascript:alert(1)"))
    with pytest.raises(UnsafeURL):
        netsafe.normalize_user_url("   ")


# -- IP policy ----------------------------------------------------------------

@pytest.mark.parametrize("ip", [
    "127.0.0.1", "127.255.255.254", "10.1.2.3", "172.16.0.1", "172.31.255.255", "192.168.0.1",
    "169.254.169.254", "169.254.0.1", "100.64.0.1", "100.127.255.255", "0.0.0.0", "224.0.0.1",
    "240.0.0.1", "255.255.255.255", "192.0.0.1", "198.18.0.1",
    "::1", "::", "fc00::1", "fd12:3456::1", "fe80::1", "ff02::1", "2001:db8::1",
    "::ffff:127.0.0.1", "::ffff:10.0.0.1", "::ffff:169.254.169.254", "::ffff:192.168.1.1",
    "64:ff9b::7f00:1", "2002:7f00:1::", "2002:a9fe:a9fe::", "2001:0:4136:e378:8000:63bf:3fff:fdd2",
])
def test_ip_is_blocked(ip):
    assert ip_is_blocked(ip)


@pytest.mark.parametrize("ip", ["8.8.8.8", "93.184.216.34", "1.1.1.1", "2606:4700:4700::1111", "::ffff:8.8.8.8"])
def test_public_ips_allowed(ip):
    assert not ip_is_blocked(ip)


def test_resolve_rejects_if_any_answer_is_private():
    with pytest.raises(UnsafeURL):
        netsafe.resolve_public("example.com", 80, lambda h, p: [PUBLIC, "10.0.0.5"])
    with pytest.raises(UnsafeURL):
        netsafe.resolve_public("example.com", 80, lambda h, p: ["::ffff:127.0.0.1"])
    with pytest.raises(UnsafeURL):
        netsafe.resolve_public("example.com", 80, lambda h, p: ["not-an-ip"])
    with pytest.raises(FetchError):
        netsafe.resolve_public("example.com", 80, lambda h, p: [])


def test_resolve_prefers_ipv4():
    assert netsafe.resolve_public("example.com", 80, lambda h, p: ["2606:4700:4700::1111", PUBLIC]) == PUBLIC


# -- fetch(): pinning, redirects ----------------------------------------------

def ok(body="hi", ctype="text/html", status=200, **headers):
    return Response(status=status, headers={"content-type": ctype, **{k.lower(): v for k, v in headers.items()}}, body=body)


def test_dns_rebinding_is_defeated_by_pinning():
    """Resolver answers public the first time and internal afterwards (classic rebinding).
    fetch() must resolve once per hop and connect to that first answer."""
    calls = []

    def rebinding_resolver(host, port):
        calls.append(host)
        return [PUBLIC] if len(calls) == 1 else ["127.0.0.1"]

    seen = []

    def transport(ip, target, headers, deadline, max_bytes):
        seen.append((ip, headers["Host"]))
        return ok()

    fetch("https://example.com/", resolver=rebinding_resolver, transport=transport)
    assert calls == ["example.com"]  # resolved exactly once
    assert seen == [(PUBLIC, "example.com")]  # connected to the pinned IP, Host kept


def test_rebinding_on_second_hop_is_caught_by_revalidation():
    answers = {"a.example.com": [PUBLIC], "b.example.com": ["10.0.0.9"]}
    hops = iter([ok(status=302, location="http://b.example.com/")])

    with pytest.raises(UnsafeURL):
        fetch("http://a.example.com/", resolver=lambda h, p: answers[h],
              transport=lambda *a, **k: next(hops))


@pytest.mark.parametrize("location", [
    "http://169.254.169.254/latest/meta-data/", "http://127.0.0.1/admin", "http://localhost/",
    "http://[::1]/", "http://2130706433/", "http://example.com:8080/", "file:///etc/passwd",
    "ftp://example.com/", "http://user:pw@example.com/", "gopher://example.com/",
    "//169.254.169.254/", "http://metadata.google.internal/computeMetadata/v1/",
])
def test_redirect_to_internal_is_blocked(location):
    def transport(*a, **k):
        return ok(status=302, location=location)

    with pytest.raises(UnsafeURL):
        fetch("https://example.com/", resolver=lambda h, p: [PUBLIC], transport=transport)


def test_redirects_capped_at_three():
    n = {"c": 0}

    def transport(*a, **k):
        n["c"] += 1
        return ok(status=302, location=f"https://example.com/{n['c']}")

    with pytest.raises(FetchError, match="redirects"):
        fetch("https://example.com/", resolver=lambda h, p: [PUBLIC], transport=transport)
    assert n["c"] == netsafe.MAX_REDIRECTS + 1


def test_three_redirects_then_ok_succeeds_and_relative_location_resolves():
    seq = iter([ok(status=301, location="/a"), ok(status=302, location="b"),
                ok(status=307, location="https://example.com/c"), ok(body="done")])
    urls = []

    def transport(ip, target, *a, **k):
        urls.append(target.path)
        return next(seq)

    r = fetch("https://example.com/", resolver=lambda h, p: [PUBLIC], transport=transport)
    assert r.body == "done" and urls == ["/", "/a", "/b", "/c"]


def test_non_text_content_type_body_is_dropped_but_headers_kept():
    t = lambda *a, **k: ok(body="\x00\x01BINARY", ctype="application/octet-stream", **{"X-Powered-By": "PHP/7.4.1"})
    r = fetch("https://example.com/", resolver=lambda h, p: [PUBLIC], transport=t)
    assert r.body == "" and r.headers["x-powered-by"] == "PHP/7.4.1"


def test_blocked_target_never_reaches_transport():
    def transport(*a, **k):
        raise AssertionError("transport must not be called")

    for bad in ("http://127.0.0.1/", "http://169.254.169.254/", "http://2130706433/", "http://[::1]/"):
        with pytest.raises(UnsafeURL):
            fetch(bad, resolver=lambda h, p: [PUBLIC], transport=transport)


def test_host_resolving_to_metadata_ip_is_blocked():
    with pytest.raises(UnsafeURL):
        fetch("http://innocent.example.com/", resolver=lambda h, p: ["169.254.169.254"],
              transport=lambda *a, **k: ok())


# -- real transport against a local server (policy bypassed by calling it directly) --

class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/big":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            try:
                for _ in range(2000):
                    self.wfile.write(b"x" * 4096)
            except OSError:
                pass
        elif self.path == "/slow":
            time.sleep(3)
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Powered-By", "PHP/5.6.40")
            self.send_header("Set-Cookie", "PHPSESSID=abc; path=/")
            self.end_headers()
            self.wfile.write("héllo".encode())


@pytest.fixture(scope="module")
def local_server():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield srv.server_address[1]
    srv.shutdown()


def _call(port, path, max_bytes=netsafe.MAX_BODY_BYTES):
    return netsafe.default_transport("127.0.0.1", Target("http", "example.com", port, path),
                                     {"Host": "example.com"}, time.monotonic() + 10, max_bytes)


def test_transport_reads_headers_cookies_and_charset(local_server):
    r = _call(local_server, "/")
    assert r.status == 200 and r.body == "héllo"
    assert r.headers["x-powered-by"] == "PHP/5.6.40"
    assert r.set_cookies and r.set_cookies[0].startswith("PHPSESSID")


def test_transport_caps_response_size(local_server):
    r = _call(local_server, "/big", max_bytes=10_000)
    assert r.truncated and len(r.body) <= 10_000


def test_transport_read_timeout(local_server, monkeypatch):
    monkeypatch.setattr(netsafe, "READ_TIMEOUT", 0.5)
    with pytest.raises(FetchError):
        _call(local_server, "/slow")
