"""
Foundation API — PHP Shield Router.

`router` is PUBLIC (free scan + report, called from the marketing site's
scan box). `admin_router` (lead lookup) is gated behind require_api_key in
main.py -- same split as connections.py.

The public scan makes outbound requests to a caller-supplied URL, so private
and loopback addresses are refused to keep it from being used to probe our
own network.
"""
import ipaddress
import socket
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.database import supabase
from app.php_shield import scanner
from app.php_shield.report_generator import render_report

router = APIRouter(prefix="/php-shield", tags=["php-shield"])
admin_router = APIRouter(prefix="/php-shield", tags=["php-shield"])


class ScanRequest(BaseModel):
    url: str


class ReportRequest(BaseModel):
    url: str
    site_name: Optional[str] = None
    contact_email: Optional[str] = None


def _assert_public_host(url: str) -> None:
    host = urlparse(url if "://" in url else "https://" + url).hostname
    if not host:
        raise HTTPException(400, "invalid url")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise HTTPException(400, "could not resolve host")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise HTTPException(400, "url must point to a public host")


@router.post("/scan")
def scan(body: ScanRequest):
    _assert_public_host(body.url)
    return scanner.scan(body.url).to_dict()


@router.post("/report", response_class=HTMLResponse)
def report(body: ReportRequest):
    _assert_public_host(body.url)
    result = scanner.scan(body.url)

    if body.contact_email:
        risk = result.risk or {}
        try:
            supabase.schema("foundation").table("php_shield_leads").insert({
                "url": result.url,
                "site_name": body.site_name,
                "contact_email": body.contact_email,
                "php_version": result.version,
                "risk_level": risk.get("risk_level"),
                "confidence": result.confidence,
            }).execute()
        except Exception:
            # A lead-capture failure must not cost the visitor their report.
            pass

    return render_report(result, body.site_name)


@admin_router.get("/leads/{lead_id}")
def get_lead(lead_id: str):
    rows = supabase.schema("foundation").table("php_shield_leads").select("*").eq("id", lead_id).execute().data
    if not rows:
        raise HTTPException(404, f"lead {lead_id} not found")
    return rows[0]
