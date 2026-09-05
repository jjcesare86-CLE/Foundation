"""Every cron calls this at the end of its run so ops_audit's L4 check has
something real to read. Never raises -- a heartbeat failure shouldn't crash
the job it's reporting on."""
import logging
from datetime import datetime, timezone

from app.database import supabase

logger = logging.getLogger(__name__)


def heartbeat(agent_slug: str, job_name: str, status: str, detail: str = "") -> None:
    try:
        supabase.schema("foundation").table("agent_jobs").update({
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "last_status": status,
            "last_detail": detail[:500] if detail else None,
        }).eq("agent_slug", agent_slug).eq("job_name", job_name).execute()
    except Exception as e:
        logger.error(f"heartbeat failed for {agent_slug}/{job_name}: {e}")
