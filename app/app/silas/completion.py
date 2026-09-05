"""Job-completion hook: done -> Rahab review request + Joanna invoicing notify."""
from datetime import datetime, timezone

from app.database import supabase
from app.action_library.executor import create_action, execute_action


def complete_job(job_id: str) -> dict:
    job = supabase.schema("foundation").table("fs_jobs").select("*").eq("id", job_id).execute().data
    if not job:
        raise ValueError(f"job {job_id} not found")
    job = job[0]

    supabase.schema("foundation").table("fs_jobs").update({"status": "done"}).eq("id", job_id).execute()

    review_request = supabase.schema("foundation").table("rr_review_requests").insert({
        "client_id": job["client_id"],
        "customer_contact_id": job.get("customer_contact_id"),
        "job_ref": job_id,
    }).execute().data[0]

    # Informational notify, not an approval-gated action -- create it pre-approved
    # and execute immediately (no external side effect, just a durable record
    # Joanna's invoicing flow can query for "jobs completed, not yet invoiced").
    notify_action = create_action(
        action_type="invoicing_notify",
        draft={"message": f"Job {job_id} ({job.get('job_type')}) completed — ready to invoice."},
        payload={"job_id": job_id, "client_id": job["client_id"]},
        agent_id="silas-dispatch",
        client_id=job["client_id"],
        requested_by="silas-completion-hook",
        status="approved",
    )
    supabase.schema("foundation").table("agent_actions").update({
        "approved_by": "system", "approved_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", notify_action["id"]).execute()
    executed = execute_action(notify_action["id"])

    return {"job_id": job_id, "review_request_id": review_request["id"], "invoicing_notify_id": executed["id"]}
