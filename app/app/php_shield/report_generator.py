"""
PHP Shield -- dark-themed HTML audit report.
"""
from html import escape
from typing import Optional

from app.php_shield.scanner import ScanResult

BADGE_COLORS = {
    "critical": "#ef4444",
    "high": "#f59e0b",
    "low": "#22c55e",
    "unknown": "#94a3b8",
}


def render_report(result: ScanResult, site_name: Optional[str] = None) -> str:
    name = escape(site_name or result.url)
    risk = result.risk or {}
    level = risk.get("risk_level", "unknown")
    color = BADGE_COLORS.get(level, BADGE_COLORS["unknown"])

    if result.error:
        headline = f"We couldn't complete the scan: {escape(result.error)}"
    elif not result.php_detected:
        headline = "No PHP signals were publicly detected on this site."
    elif not result.version:
        headline = "PHP appears to be in use, but the version isn't publicly disclosed."
    else:
        headline = escape(risk.get("headline", ""))

    version_line = f"PHP {escape(result.version)}" if result.version else "Version not detected"
    evidence = "".join(f"<li>{escape(e)}</li>" for e in result.evidence) or "<li>No public signals found.</li>"
    cves = "".join(f"<li>{escape(c)}</li>" for c in risk.get("cves", []))
    cve_block = (
        f"<h2>Example vulnerabilities in this branch</h2><ul>{cves}</ul>"
        "<p class='muted'>Illustrative examples, not an exhaustive list.</p>"
    ) if cves else ""

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PHP Shield Report - {name}</title>
<style>
  body {{ margin:0; background:#0b1020; color:#e2e8f0; font:16px/1.6 system-ui,sans-serif; }}
  .wrap {{ max-width:760px; margin:0 auto; padding:32px 16px; }}
  h1 {{ margin:0 0 4px; font-size:28px; }} h2 {{ margin-top:32px; font-size:20px; }}
  .muted {{ color:#94a3b8; font-size:14px; }}
  .card {{ background:#131a30; border:1px solid #243052; border-radius:12px; padding:20px; margin-top:20px; }}
  .badge {{ display:inline-block; padding:4px 14px; border-radius:999px; font-weight:700;
            text-transform:uppercase; letter-spacing:.05em; background:{color}22; color:{color}; border:1px solid {color}; }}
  ul {{ padding-left:20px; }}
  .tiers {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; }}
  .tier {{ background:#0f1630; border:1px solid #243052; border-radius:10px; padding:16px; }}
  .price {{ font-size:24px; font-weight:700; color:#fff; }}
  .cta {{ display:inline-block; margin-top:12px; padding:10px 18px; border-radius:8px; background:{color}; color:#0b1020; font-weight:700; text-decoration:none; }}
</style></head><body><div class="wrap">
  <p class="muted">PHP Shield audit</p>
  <h1>{name}</h1>
  <div class="card">
    <span class="badge">{escape(level)} risk</span>
    <p style="font-size:20px;margin:12px 0 4px">{version_line}</p>
    <p>{headline}</p>
    <p class="muted">Detection confidence: {escape(result.confidence)}</p>
  </div>
  <h2>What we saw</h2><ul>{evidence}</ul>
  {cve_block}
  <h2>Fix it</h2>
  <div class="tiers">
    <div class="tier"><div class="price">$300 - $1,500</div><strong>One-time fix</strong>
      <p class="muted">PHP upgrade and compatibility fixes, scoped to your site's size and plugins.</p></div>
    <div class="tier"><div class="price">$99/mo</div><strong>Maintenance</strong>
      <p class="muted">Ongoing updates, monitoring and security patching so you never fall behind again.</p></div>
  </div>
  <a class="cta" href="https://automaitionnation.com">Get my site fixed</a>
  <p class="muted" style="margin-top:32px">This report is based only on publicly visible signals from ordinary page requests. No login or exploitation was attempted.</p>
</div></body></html>"""


def _risk_cell(scan: dict) -> str:
    risk = (scan or {}).get("risk") or {}
    level = risk.get("risk_level", "unknown")
    color = BADGE_COLORS.get(level, BADGE_COLORS["unknown"])
    version = (scan or {}).get("version") or "not detected"
    return (f'<td style="padding:10px;border:1px solid #ddd"><b style="color:{color};text-transform:uppercase">'
            f'{escape(level)}</b><br>PHP {escape(str(version))}</td>')


def render_comparison(before: dict, after: dict, domain: str) -> str:
    """Email-safe before/after table (light theme: renders in any mail client)."""
    return (
        f'<p><b>{escape(domain)}</b></p>'
        '<table style="border-collapse:collapse;width:100%"><tr>'
        '<th style="padding:10px;border:1px solid #ddd;text-align:left">Before</th>'
        '<th style="padding:10px;border:1px solid #ddd;text-align:left">After</th></tr>'
        f'<tr>{_risk_cell(before)}{_risk_cell(after)}</tr></table>'
        f'<p style="color:#555;font-size:13px">{escape(((after or {}).get("risk") or {}).get("headline", ""))}</p>'
    )
