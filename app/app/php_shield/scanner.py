"""
PHP Shield -- passive PHP fingerprinting.

Reads ONLY public signals from three ordinary GET requests (X-Powered-By,
Server, PHPSESSID cookie, body text). No authentication, no exploitation, no
payloads. All traffic goes through netsafe.fetch (SSRF-safe, IP-pinned).
Consent-based: callers must have recorded the visitor's "I own or am
authorized to scan this site" confirmation before invoking scan().
"""
import re
from dataclasses import asdict, dataclass, field
from typing import Callable, Optional

from app.php_shield import netsafe
from app.php_shield.php_version_db import risk_report
from app.php_shield.store import iso

PROBE_PATHS = ["/", "/wp-login.php", "/readme.html"]

_PHP_VERSION_RE = re.compile(r"PHP/(\d+\.\d+(?:\.\d+)?)", re.I)
_WP_GENERATOR_RE = re.compile(r"WordPress (\d+\.\d+(?:\.\d+)?)", re.I)


@dataclass
class ScanResult:
    url: str
    domain: str = ""
    php_detected: bool = False
    version: Optional[str] = None
    confidence: str = "none"  # none | low | medium | high
    evidence: list = field(default_factory=list)
    risk: Optional[dict] = None
    error: Optional[str] = None
    wordpress: bool = False
    scanned_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _bump(result: ScanResult, level: str):
    order = ["none", "low", "medium", "high"]
    if order.index(level) > order.index(result.confidence):
        result.confidence = level


def scan(url: str, *, fetcher: Callable = netsafe.fetch) -> ScanResult:
    """Never raises for bad/blocked/unreachable targets: failures land in .error."""
    result = ScanResult(url=url or "", scanned_at=iso())
    try:
        base = netsafe.validate_url(netsafe.normalize_user_url(url))
    except netsafe.UnsafeURL as e:
        result.error = str(e)
        return result

    origin = f"{base.scheme}://{base.host}"
    result.url = origin
    result.domain = netsafe.registrable_host(base.host)
    reached = False

    for path in PROBE_PATHS:
        try:
            resp = fetcher(origin + path)
        except netsafe.UnsafeURL as e:
            result.error = f"blocked: {e}"
            return result
        except netsafe.FetchError as e:
            if not reached:
                result.error = f"could not reach site: {e}"
                return result
            continue
        reached = True
        if resp.tls_verified is False and path == "/":
            result.evidence.append("TLS certificate did not validate (expired, self-signed or mismatched)")

        powered = resp.headers.get("x-powered-by", "")
        m = _PHP_VERSION_RE.search(powered)
        if m:
            result.php_detected = True
            result.version = result.version or m.group(1)
            _bump(result, "high")
            result.evidence.append(f"{path}: X-Powered-By: {powered}")
        elif "php" in powered.lower():
            result.php_detected = True
            _bump(result, "medium")
            result.evidence.append(f"{path}: X-Powered-By: {powered} (no version)")

        server = resp.headers.get("server", "")
        m = _PHP_VERSION_RE.search(server)
        if m:
            result.php_detected = True
            result.version = result.version or m.group(1)
            _bump(result, "high")
            result.evidence.append(f"{path}: Server: {server}")

        if any(c.startswith("PHPSESSID") for c in resp.set_cookies):
            result.php_detected = True
            _bump(result, "medium")
            result.evidence.append(f"{path}: PHPSESSID cookie present")

        body = resp.body if resp.status == 200 else ""
        if path == "/wp-login.php" and "wp-submit" in body:
            result.php_detected = result.wordpress = True
            _bump(result, "medium")
            result.evidence.append("/wp-login.php: WordPress login page (runs on PHP)")
        if path == "/readme.html":
            m = _WP_GENERATOR_RE.search(body)
            if m:
                result.php_detected = result.wordpress = True
                _bump(result, "low")
                result.evidence.append(f"/readme.html: WordPress {m.group(1)} readme (PHP version not disclosed)")
        m = _PHP_VERSION_RE.search(body)
        if m and not result.version:
            result.php_detected = True
            result.version = m.group(1)
            _bump(result, "low")
            result.evidence.append(f"{path}: PHP/{m.group(1)} mentioned in page body")

    if result.version:
        result.risk = risk_report(result.version)
    return result
