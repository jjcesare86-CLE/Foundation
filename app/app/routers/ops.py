"""Foundation API — Ops Audit Router. Admin-only (gated via require_api_key in main.py)."""
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from app.ops.ops_audit import run_full_audit

router = APIRouter(prefix="/ops", tags=["ops"])

_STATUS_COLOR = {"green": "#1D9E75", "amber": "#D4A017", "red": "#C0392B"}


@router.get("/agent-health")
def agent_health(run_l5: bool = Query(True, description="Set false to skip the (billable) smoke call layer")):
    board = run_full_audit(run_l5=run_l5)
    counts = {"green": 0, "amber": 0, "red": 0}
    for row in board:
        counts[row["status"]] += 1
    return {"summary": counts, "total": len(board), "agents": board}


@router.get("/agent-health/dashboard", response_class=HTMLResponse)
def agent_health_dashboard(run_l5: bool = Query(False, description="Default false: the grid page shouldn't silently rack up smoke-call cost on every page load")):
    board = run_full_audit(run_l5=run_l5)
    rows_html = ""
    for row in board:
        color = _STATUS_COLOR[row["status"]]
        cells = "".join(
            f'<td title="{row["layers"][layer]["reason"]}" style="text-align:center">'
            f'{"✓" if row["layers"][layer]["pass"] else ("—" if row["layers"][layer]["pass"] is None else "✗")}</td>'
            for layer in ("L1", "L2", "L3", "L4", "L5")
        )
        rows_html += (
            f'<tr><td style="border-left:4px solid {color};padding-left:8px">'
            f'{row["biblical_name"] or row["agent_id"]}</td>{cells}</tr>'
        )
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Foundation — Agent Ops Health</title>
<style>
body {{ font-family: -apple-system, sans-serif; padding: 24px; background: #0A1628; color: #E8ECF1; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: 6px 10px; border-bottom: 1px solid #223; }}
th {{ text-align: left; color: #9AA5B1; font-weight: 600; }}
</style></head><body>
<h2>Agent Ops Health ({len(board)} agents{" — L5 skipped" if not run_l5 else ""})</h2>
<table><tr><th>Agent</th><th>L1</th><th>L2</th><th>L3</th><th>L4</th><th>L5</th></tr>
{rows_html}
</table>
</body></html>"""
    return HTMLResponse(html)
