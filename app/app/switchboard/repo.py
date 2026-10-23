"""
The one data-access seam for Switchboard tables (Addendum F.9.3).

Every /switchboard/* read or write of an sb_* table goes through table().
SWITCHBOARD_DB_MODE picks the backend:
  foundation  (default) -> foundation.<table> in the Foundation project
  switchboard           -> public.<table> in the dedicated Switchboard project
Table and column names are identical in both. Foundation-owned tables
(ai_employees, client_profiles, client_agent_entitlements) are NOT routed
here; they always use app.database.supabase.

Workspace mirror (F.4.1): in `switchboard` mode a row in sb_workspaces must
exist before any child row. sync_workspace() upserts it from Foundation's
client_profiles and applies suspension; ensure_workspace() is the cached
per-request form.
"""
import time
from datetime import datetime, timezone

from app.database import supabase
from app.switchboard import switchboard_db

_SYNC_TTL_SECONDS = 60
_last_sync: dict[str, tuple[float, str]] = {}

# client_profiles.status values (live: active, onboarding) -> sb_workspaces.status
_BLOCKED = {"suspended": "suspended", "paused": "suspended", "closed": "closed", "cancelled": "closed", "churned": "closed"}


def table(name: str):
    if switchboard_db.db_mode() == "switchboard":
        return switchboard_db.client().table(name)
    return supabase.schema("foundation").table(name)


def foundation_workspace(workspace_id: str) -> dict | None:
    rows = (
        supabase.schema("foundation").table("client_profiles")
        .select("id,business_name,status").eq("id", workspace_id).execute().data
    )
    return rows[0] if rows else None


def workspace_status(workspace_id: str) -> str:
    """'active' | 'suspended' | 'closed' | 'unknown' from Foundation, the source of truth."""
    row = foundation_workspace(workspace_id)
    if not row:
        return "unknown"
    return _BLOCKED.get((row.get("status") or "").lower(), "active")


def sync_workspace(workspace_id: str) -> str:
    """Upsert the sb_workspaces mirror in the Switchboard project; return its status.
    Always targets the Switchboard project, whatever SWITCHBOARD_DB_MODE says."""
    row = foundation_workspace(workspace_id)
    if not row:
        return "unknown"
    status = _BLOCKED.get((row.get("status") or "").lower(), "active")
    switchboard_db.client().table("sb_workspaces").upsert({
        "id": workspace_id, "name": row.get("business_name") or workspace_id,
        "status": status, "synced_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
    _last_sync[workspace_id] = (time.monotonic(), status)
    return status


def ensure_workspace(workspace_id: str) -> str:
    """Per-request guard. foundation mode: just read Foundation's status.
    switchboard mode: also keep the mirror fresh (cached 60s). Returns the status."""
    if switchboard_db.db_mode() != "switchboard":
        return workspace_status(workspace_id)
    hit = _last_sync.get(workspace_id)
    if hit and time.monotonic() - hit[0] < _SYNC_TTL_SECONDS:
        return hit[1]
    return sync_workspace(workspace_id)
