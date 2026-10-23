"""
PHP Shield -- SSRF-safe URL validation and fetching.

Every outbound request PHP Shield makes to a user-supplied URL goes through
`fetch()`. Defences, in order:

1. URL policy: http/https only, ports 80/443 only, no credentials, bounded
   length, no control characters, a real DNS hostname (IP literals in any
   notation, `localhost`, single-label and internal-suffix names are refused).
2. DNS is resolved server-side and EVERY answer must be a public address
   (IPv4 + IPv6, IPv4-mapped IPv6 unwrapped, CGNAT/metadata/reserved blocked).
3. The connection is made to the resolved IP itself (pinned), with the
   original hostname used only for Host/SNI -- the resolver is never consulted
   a second time, so DNS rebinding cannot swap in an internal address.
4. Redirects are followed manually (max 3); each hop repeats steps 1-3.
5. Response size, time, and body content-type are capped.
"""
import ipaddress
import re
import socket
import time
from dataclasses import dataclass, field
from typing import Callable, Optional
from urllib.parse import urljoin, urlsplit

MAX_URL_LENGTH = 2048
ALLOWED_PORTS = (80, 443)
MAX_REDIRECTS = 3
MAX_BODY_BYTES = 512 * 1024
CONNECT_TIMEOUT = 4.0
READ_TIMEOUT = 6.0
TOTAL_DEADLINE = 12.0
USER_AGENT = "PHPShield-Scanner/1.0 (consent-based, passive; +https://automaitionnation.com)"
TEXT_TYPES = ("text/", "application/xhtml+xml", "application/xml", "application/json")

BLOCKED_SUFFIXES = (
    ".localhost", ".local", ".localdomain", ".internal", ".intranet", ".lan",
    ".home", ".corp", ".private", ".home.arpa", ".onion", ".test", ".invalid", ".example",
)

_BLOCKED_NETS = [ipaddress.ip_network(n) for n in (
    # IPv4
    "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8", "169.254.0.0/16",
    "172.16.0.0/12", "192.0.0.0/24", "192.0.2.0/24", "192.88.99.0/24", "192.168.0.0/16",
    "198.18.0.0/15", "198.51.100.0/24", "203.0.113.0/24", "224.0.0.0/4", "240.0.0.0/4",
    "255.255.255.255/32",
    # IPv6
    "::/128", "::1/128", "64:ff9b::/96", "64:ff9b:1::/48", "100::/64", "2001::/32",
    "2001:db8::/32", "2002::/16", "fc00::/7", "fe80::/10", "ff00::/8",
)]

_LABEL_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")
_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")
_BAD_CHARS_RE = re.compile(r"[\x00-\x20\x7f\\]")
_REDIRECT_CODES = {301, 302, 303, 307, 308}


class UnsafeURL(ValueError):
    """The URL (or a redirect/DNS answer it led to) is not allowed."""


class FetchError(RuntimeError):
    """Transport-level failure (timeout, TLS, too many redirects...)."""


@dataclass(frozen=True)
class Target:
    scheme: str
    host: str
    port: int
    path: str  # path + query, always starts with "/"

    @property
    def url(self) -> str:
        default = 443 if self.scheme == "https" else 80
        netloc = self.host if self.port == default else f"{self.host}:{self.port}"
        return f"{self.scheme}://{netloc}{self.path}"


@dataclass
class Response:
    status: int
    headers: dict  # lower-cased name -> last value
    set_cookies: list = field(default_factory=list)
    body: str = ""
    url: str = ""
    truncated: bool = False
    tls_verified: Optional[bool] = None
    pinned_ip: str = ""


# ── IP policy ────────────────────────────────────────────────────────────

def ip_is_blocked(value) -> bool:
    ip = ipaddress.ip_address(value) if not isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)) else value
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            return ip_is_blocked(ip.ipv4_mapped)
        if ip.sixtofour is not None and ip_is_blocked(ip.sixtofour):
            return True
        if ip.teredo is not None:
            return True
    if not ip.is_global:
        return True
    return any(ip in net for net in _BLOCKED_NETS if net.version == ip.version)


# ── URL policy ───────────────────────────────────────────────────────────

def normalize_user_url(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        raise UnsafeURL("url required")
    if not _SCHEME_RE.match(raw):
        raw = "https://" + raw
    return raw


def _validate_host(host: str) -> str:
    host = host.lower().rstrip(".")
    if not host:
        raise UnsafeURL("missing hostname")
    if host.startswith("[") or ":" in host:
        raise UnsafeURL("IP literals are not allowed")
    try:
        ipaddress.ip_address(host)
        raise UnsafeURL("IP literals are not allowed")
    except ValueError:
        pass
    # Decimal / hex / octal IPv4 spellings (2130706433, 0x7f000001, 0177.0.0.1)
    # never contain a letter outside a hex prefix and have an all-numeric last label.
    last = host.rsplit(".", 1)[-1]
    if re.fullmatch(r"(0x[0-9a-f]+|[0-9]+)", last):
        raise UnsafeURL("numeric hostnames are not allowed")
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        raise UnsafeURL("invalid hostname")
    if "." not in host or host == "localhost" or host.endswith(BLOCKED_SUFFIXES):
        raise UnsafeURL("internal hostnames are not allowed")
    if len(host) > 253 or not all(_LABEL_RE.match(label) for label in host.split(".")):
        raise UnsafeURL("invalid hostname")
    return host


def validate_url(url: str) -> Target:
    if not isinstance(url, str) or len(url) > MAX_URL_LENGTH:
        raise UnsafeURL("url too long")
    if _BAD_CHARS_RE.search(url.strip()):
        raise UnsafeURL("url contains illegal characters")
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        raise UnsafeURL("only http and https are allowed")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise UnsafeURL("credentials in url are not allowed")
    try:
        port = parts.port
    except ValueError:
        raise UnsafeURL("invalid port")
    if port is None:  # NOT `port or default`: an explicit port 0 must be rejected, not defaulted
        port = 443 if parts.scheme == "https" else 80
    if port not in ALLOWED_PORTS:
        raise UnsafeURL("only ports 80 and 443 are allowed")
    host = _validate_host(parts.hostname or "")
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query
    return Target(parts.scheme, host, port, path)


def registrable_host(url_or_host: str) -> str:
    """Normalized host used for per-domain limits and ownership matching (www. stripped)."""
    host = url_or_host
    if "://" in host or "/" in host:
        host = urlsplit(normalize_user_url(host)).hostname or ""
    host = host.lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


# ── DNS ──────────────────────────────────────────────────────────────────

Resolver = Callable[[str, int], list]


def default_resolver(host: str, port: int) -> list:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise FetchError("could not resolve host")
    return [info[4][0] for info in infos]


def resolve_public(host: str, port: int, resolver: Optional[Resolver] = None) -> str:
    """Resolve once; every answer must be public; return the IP to pin."""
    answers = list((resolver or default_resolver)(host, port))
    if not answers:
        raise FetchError("could not resolve host")
    ips = []
    for a in answers:
        try:
            ip = ipaddress.ip_address(str(a).split("%")[0])
        except ValueError:
            raise UnsafeURL("host resolved to an invalid address")
        if ip_is_blocked(ip):
            raise UnsafeURL("host resolves to a non-public address")
        ips.append(ip)
    ips.sort(key=lambda i: i.version)  # prefer IPv4
    return str(ips[0])


# ── transport (replaceable in tests) ─────────────────────────────────────

Transport = Callable[..., Response]


def default_transport(ip: str, target: Target, headers: dict, deadline: float, max_bytes: int) -> Response:
    import certifi
    import urllib3

    timeout = urllib3.Timeout(connect=CONNECT_TIMEOUT, read=READ_TIMEOUT)
    tls_verified = None

    def _request(verify: bool):
        if target.scheme == "https":
            pool = urllib3.HTTPSConnectionPool(
                ip, port=target.port, timeout=timeout, retries=False, maxsize=1,
                cert_reqs="CERT_REQUIRED" if verify else "CERT_NONE",
                ca_certs=certifi.where() if verify else None,
                assert_hostname=target.host if verify else False,
                server_hostname=target.host,
            )
        else:
            pool = urllib3.HTTPConnectionPool(ip, port=target.port, timeout=timeout, retries=False, maxsize=1)
        resp = pool.urlopen("GET", target.path, headers=headers, redirect=False, retries=False,
                            preload_content=False, assert_same_host=False)
        return pool, resp

    try:
        try:
            pool, resp = _request(verify=True)
            tls_verified = True if target.scheme == "https" else None
        except urllib3.exceptions.SSLError:
            # Neglected sites often have expired certs -- they are exactly who needs this
            # scan. The connection is already pinned to a validated public IP, so skipping
            # chain validation here cannot be used to reach anything internal.
            pool, resp = _request(verify=False)
            tls_verified = False
    except urllib3.exceptions.HTTPError as e:
        raise FetchError(f"request failed: {type(e).__name__}")
    except OSError as e:
        raise FetchError(f"request failed: {type(e).__name__}")

    chunks, size, truncated = [], 0, False
    try:
        for chunk in resp.stream(8192):
            size += len(chunk)
            if size > max_bytes:
                chunks.append(chunk[: max_bytes - (size - len(chunk))])
                truncated = True
                break
            chunks.append(chunk)
            if time.monotonic() > deadline:
                truncated = True
                break
    except urllib3.exceptions.HTTPError:
        truncated = True
    finally:
        resp.release_conn()
        resp.close()
        pool.close()

    hdrs = {k.lower(): v for k, v in resp.headers.items()}
    cookies = resp.headers.getlist("Set-Cookie") if hasattr(resp.headers, "getlist") else []
    charset = "utf-8"
    m = re.search(r"charset=([\w\-]+)", hdrs.get("content-type", ""), re.I)
    if m:
        charset = m.group(1)
    raw = b"".join(chunks)
    try:
        body = raw.decode(charset, errors="replace")
    except LookupError:
        body = raw.decode("utf-8", errors="replace")
    return Response(status=resp.status, headers=hdrs, set_cookies=cookies, body=body,
                    truncated=truncated, tls_verified=tls_verified, pinned_ip=ip)


def _is_text(content_type: str) -> bool:
    ct = (content_type or "").split(";")[0].strip().lower()
    return ct == "" or ct.startswith(TEXT_TYPES)


# ── the one public entry point ───────────────────────────────────────────

def fetch(
    url: str,
    *,
    resolver: Optional[Resolver] = None,
    transport: Optional[Transport] = None,
    max_bytes: int = MAX_BODY_BYTES,
    extra_headers: Optional[dict] = None,
) -> Response:
    transport = transport or default_transport
    deadline = time.monotonic() + TOTAL_DEADLINE
    current = normalize_user_url(url)
    for hop in range(MAX_REDIRECTS + 1):
        target = validate_url(current)
        ip = resolve_public(target.host, target.port, resolver)
        default_port = 443 if target.scheme == "https" else 80
        headers = {
            "Host": target.host if target.port == default_port else f"{target.host}:{target.port}",
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.5",
            "Accept-Encoding": "identity",
            "Connection": "close",
            **(extra_headers or {}),
        }
        resp = transport(ip, target, headers, deadline, max_bytes)
        resp.url = target.url
        if not _is_text(resp.headers.get("content-type", "")):
            resp.body = ""  # unexpected content type: keep headers/cookies, drop the body
        if resp.status in _REDIRECT_CODES and resp.headers.get("location"):
            if hop == MAX_REDIRECTS:
                raise FetchError("too many redirects")
            current = urljoin(target.url, resp.headers["location"])
            continue
        return resp
    raise FetchError("too many redirects")
