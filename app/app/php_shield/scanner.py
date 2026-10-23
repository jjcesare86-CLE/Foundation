"""
PHP Shield -- passive PHP fingerprinting.

Reads ONLY public signals from three ordinary GET requests (X-Powered-By,
Server, PHPSESSID cookie, body text). No authentication, no exploitation,
no payloads. Only scan sites you own or have permission to assess.
"""
import re
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlparse

import requests

from app.php_shield.php_version_db import risk_report

PROBE_PATHS = ["/", "/wp-login.php", "/readme.html"]
TIMEOUT_SECONDS = 8
USER_AGENT = "PHPShield-Scanner/1.0 (passive; +https://automaitionnation.com)"

_PHP_VERSION_RE = re.compile(r"PHP/(\d+\.\d+(?:\.\d+)?)", re.I)
_WP_GENERATOR_RE = re.compile(r"WordPress (\d+\.\d+(?:\.\d+)?)", re.I)


@dataclass
class ScanResult:
    url: str
    php_detected: bool = False
    version: Optional[str] = None
    confidence: str = "none"  # none | low | medium | high
    evidence: list[str] = field(default_factory=list)
    risk: Optional[dict] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def _normalize(url: str) -> str:
    url = (url or "").strip()
    if not url:
        raise ValueError("url required")
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("url must be http(s)")
    return f"{parsed.scheme}://{parsed.netloc}"


def scan(url: str) -> ScanResult:
    try:
        base = _normalize(url)
    except ValueError as e:
        return ScanResult(url=url or "", error=str(e))

    result = ScanResult(url=base)
    reached = False

    for path in PROBE_PATHS:
        try:
            resp = requests.get(
                base + path, timeout=TIMEOUT_SECONDS, allow_redirects=True,
                headers={"User-Agent": USER_AGENT},
            )
        except requests.RequestException as e:
            if path == "/" and not reached:
                result.error = f"could not reach site: {type(e).__name__}"
                return result
            continue
        reached = True

        powered = resp.headers.get("X-Powered-By", "")
        m = _PHP_VERSION_RE.search(powered)
        if m:
            result.php_detected = True
            result.version = result.version or m.group(1)
            result.confidence = "high"
            result.evidence.append(f"{path}: X-Powered-By: {powered}")
        elif "php" in powered.lower():
            result.php_detected = True
            result.confidence = result.confidence if result.confidence == "high" else "medium"
            result.evidence.append(f"{path}: X-Powered-By: {powered} (no version)")

        server = resp.headers.get("Server", "")
        m = _PHP_VERSION_RE.search(server)
        if m:
            result.php_detected = True
            result.version = result.version or m.group(1)
            result.confidence = "high"
            result.evidence.append(f"{path}: Server: {server}")

        if "PHPSESSID" in resp.cookies or "PHPSESSID" in resp.headers.get("Set-Cookie", ""):
            if not result.php_detected:
                result.confidence = "medium"
            result.php_detected = True
            result.evidence.append(f"{path}: PHPSESSID cookie present")

        body = resp.text[:200_000] if resp.status_code == 200 else ""
        if path == "/wp-login.php" and resp.status_code == 200 and "wp-submit" in body:
            result.php_detected = True
            if result.confidence in ("none", "low"):
                result.confidence = "medium"
            result.evidence.append("/wp-login.php: WordPress login page (runs on PHP)")
        if path == "/readme.html" and resp.status_code == 200:
            m = _WP_GENERATOR_RE.search(body)
            if m:
                result.php_detected = True
                if result.confidence == "none":
                    result.confidence = "low"
                result.evidence.append(f"/readme.html: WordPress {m.group(1)} readme (PHP version not disclosed)")
        m = _PHP_VERSION_RE.search(body)
        if m and not result.version:
            result.php_detected = True
            result.version = m.group(1)
            result.confidence = "low" if result.confidence == "none" else result.confidence
            result.evidence.append(f"{path}: PHP/{m.group(1)} mentioned in page body")

    if result.version:
        result.risk = risk_report(result.version)
    return result
