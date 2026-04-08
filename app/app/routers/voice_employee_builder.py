"""
Foundation API — Voice Employee Builder Router
==============================================
Premium feature: clients build custom AI employees by talking to an AI interviewer.

Flow:
  1. POST /employees/voice-builder/start
       → Creates a VAPI interviewer assistant for this session
       → Returns VAPI assistant_id + call config for the frontend SDK

  2. VAPI calls the client, interviews them about their desired employee
       → 8–12 smart questions about role, scope, tone, handoffs, edge cases

  3. POST /employees/voice-builder/webhook  (VAPI server URL)
       → Receives completed transcript from VAPI end-of-call webhook
       → Claude processes transcript → builds full system prompt
       → Saves to foundation.custom_employee_prompts
       → Returns completed employee profile

  4. GET  /employees/voice-builder/result/{session_id}
       → Frontend polls this to get the completed employee after the call

  5. POST /employees/voice-builder/deploy
       → Optionally deploys the custom employee as a live VAPI assistant
"""

import os
import json
import uuid
import httpx
import anthropic
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/employees/voice-builder", tags=["voice-employee-builder"])

VAPI_API_KEY     = os.environ.get("VAPI_API_KEY", "")
VAPI_BASE        = "https://api.vapi.ai"
ANTHROPIC_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
SUPABASE_URL     = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY     = os.environ.get("SUPABASE_SERVICE_KEY", "")
FOUNDATION_URL   = os.environ.get("FOUNDATION_API_URL", "https://foundation-api-9gpl.onrender.com")

# ─── In-memory session store (swap to Supabase for production scale) ──────────
# Stores: session_id → { status, transcript, employee_profile, error }
_sessions: dict = {}

# ─── Models ───────────────────────────────────────────────────────────────────

class VoiceBuilderStartRequest(BaseModel):
    client_id:       Optional[str] = None
    client_name:     Optional[str] = "there"
    business_name:   Optional[str] = ""
    webhook_base_url: str          # e.g. https://foundation-api-9gpl.onrender.com

class VoiceBuilderDeployRequest(BaseModel):
    session_id: str
    client_id:  Optional[str] = None

# ─── VAPI Interviewer System Prompt ───────────────────────────────────────────

def build_interviewer_prompt(client_name: str, business_name: str, session_id: str) -> str:
    return f"""You are the Automation Nation Custom Employee Architect — a warm, expert AI consultant
who helps business owners design their own bespoke AI employee.

You are speaking with {client_name}{f' from {business_name}' if business_name else ''}.

Your job is to conduct a focused, conversational interview to gather everything needed
to build them a world-class AI employee. This is a premium service — treat it that way.
Be curious, insightful, and occasionally offer suggestions based on what you hear.

SESSION ID: {session_id}
(Do not mention this to the client — it is for internal tracking only.)

─── INTERVIEW STRUCTURE ───────────────────────────────────────────────────────

Open warmly, then work through these areas naturally — do NOT read them as a checklist.
Flow like a real conversation. Ask follow-ups. Be genuinely interested.

1. ROLE & PURPOSE
   - What should this AI employee do? What's the core job?
   - What does success look like for this role?
   - Is this a new position or replacing something they currently do manually?

2. SCOPE & EXPERTISE
   - What specific tasks, topics, and outputs should it handle?
   - Are there industry-specific terms, processes, or knowledge it must know?
   - What are the most common requests it will receive?

3. BOUNDARIES
   - What should it absolutely NOT do or say?
   - When should it escalate to a human?
   - Are there sensitive topics it must handle carefully?

4. PERSONALITY & COMMUNICATION STYLE
   - How should it communicate? (Formal? Casual? Technical? Empathetic?)
   - Should it have a distinct personality or stay neutral?
   - Any tone or language preferences?

5. NAME & IDENTITY
   - Do they have a name in mind? (Offer to suggest one if not)
   - Should it feel like part of their team or like an outside service?

6. HANDOFF & INTEGRATION
   - Who or what does it hand off to when outside its scope?
   - Does it need to know about other team members or systems?

7. QUALITY STANDARD
   - What does "excellent work" look like for this role?
   - Any examples of outputs they love or hate?

8. BUSINESS CONTEXT (if not already covered)
   - What industry/niche is this for?
   - Who are their clients/customers?
   - What makes their business different?

─── CLOSING ───────────────────────────────────────────────────────────────────

Once you have enough information (usually after 8–12 exchanges), wrap up warmly:
"I have everything I need to build [name/your employee]. Our system will generate
their full profile and system prompt — you'll see it on screen in just a moment.
This is going to be a seriously impressive addition to your team."

Then say goodbye and end the call naturally.

─── RULES ─────────────────────────────────────────────────────────────────────
- Never rush. This is a premium experience.
- If an answer is vague, ask a smart follow-up.
- Offer concrete suggestions when the client seems unsure.
- Keep each response concise — this is a voice call, not an essay.
- Never mention Claude, Anthropic, or the underlying technology.
- If asked, you are "the Automation Nation Employee Architect."
"""

# ─── Claude Employee Builder ──────────────────────────────────────────────────

def build_employee_from_transcript(transcript: str) -> dict:
    """
    Takes the raw call transcript and uses Claude to extract structured
    employee data + generate a full deployable system prompt.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    extraction_prompt = f"""You are processing a transcript from an AI employee design interview.
Extract the key information and build a complete AI employee profile.

TRANSCRIPT:
{transcript}

Return a JSON object with exactly these fields:
{{
  "name": "Employee name (uppercase, 4-6 chars if possible, e.g. ARIA, REX, NOVA)",
  "role": "Job title / role name",
  "department": "Best matching department: Marketing, Sales, Operations, Tech & Automation, Content & Media, Legal & Finance, Client Success, or Custom",
  "style": "Communication style in 3-4 words",
  "helps": "Comma-separated list of specific tasks and outputs this employee handles",
  "outside_scope": "What they don't do and who to redirect to",
  "business_context": "Industry, niche, client type, and brand voice notes",
  "quality_standard": "What excellent output looks like for this role",
  "handoff_rules": "Specific escalation and handoff logic",
  "personality_notes": "Tone, personality traits, communication preferences",
  "suggested_color": "A hex color that matches this department/role vibe",
  "suggested_bg": "A lighter version of that color with low opacity (rgba format)",
  "system_prompt": "A complete, deployable AI system prompt for this employee. Include: identity, expertise areas, hard scope rules with exact redirect language, information-gathering protocol (must ask clarifying questions before producing output), quality standards, and opening greeting. Make it exceptional — this is a premium custom build."
}}

Return ONLY the JSON. No markdown, no preamble."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": extraction_prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)

# ─── Supabase save helper ─────────────────────────────────────────────────────

async def save_custom_employee(client_id: Optional[str], session_id: str, profile: dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    async with httpx.AsyncClient() as c:
        resp = await c.post(
            f"{SUPABASE_URL}/rest/v1/foundation.custom_employee_prompts",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json={
                "client_id":        client_id,
                "session_id":       session_id,
                "employee_name":    profile.get("name"),
                "role":             profile.get("role"),
                "department":       profile.get("department"),
                "style":            profile.get("style"),
                "helps":            profile.get("helps"),
                "outside_scope":    profile.get("outside_scope"),
                "business_context": profile.get("business_context"),
                "system_prompt":    profile.get("system_prompt"),
                "full_profile":     json.dumps(profile),
                "created_at":       datetime.utcnow().isoformat(),
            },
        )
    return resp.json()

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@router.post("/start")
async def start_voice_builder(req: VoiceBuilderStartRequest):
    """
    Creates a VAPI interviewer assistant and returns the config
    needed for the frontend to start the call via VAPI Web SDK.
    """
    if not VAPI_API_KEY:
        raise HTTPException(status_code=500, detail="VAPI_API_KEY not configured")

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"status": "pending", "transcript": None, "employee": None, "error": None}

    webhook_url = f"{req.webhook_base_url}/employees/voice-builder/webhook"
    system_prompt = build_interviewer_prompt(req.client_name, req.business_name, session_id)

    # Create VAPI assistant
    async with httpx.AsyncClient() as c:
        resp = await c.post(
            f"{VAPI_BASE}/assistant",
            headers={"Authorization": f"Bearer {VAPI_API_KEY}", "Content-Type": "application/json"},
            json={
                "name": f"Employee Architect — {session_id[:8]}",
                "model": {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-20250514",
                    "messages": [{"role": "system", "content": system_prompt}],
                    "temperature": 0.7,
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "ErXwobaYiN019PkySvjV",  # Antoni — warm, professional male
                },
                "firstMessage": f"Hey {req.client_name}! I'm the Automation Nation Employee Architect. I'm here to help you design a completely custom AI employee built specifically for your business. This is going to be really exciting — I just have a few questions to get started. First, tell me — what kind of role do you have in mind?",
                "endCallMessage": "Perfect — I have everything I need. Your custom AI employee profile is being built right now. Check the screen in just a moment to see your new team member. Talk soon!",
                "serverUrl": webhook_url,
                "serverUrlSecret": session_id,
                "recordingEnabled": True,
                "endCallFunctionEnabled": True,
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "en-US",
                },
                "maxDurationSeconds": 900,  # 15 min max
                "backgroundSound": "off",
                "backchannelingEnabled": True,
            },
            timeout=30,
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"VAPI error: {resp.text}")

    vapi_data = resp.json()
    assistant_id = vapi_data.get("id")

    _sessions[session_id]["assistant_id"] = assistant_id
    _sessions[session_id]["status"] = "ready"

    return {
        "session_id":   session_id,
        "assistant_id": assistant_id,
        "status":       "ready",
        "message":      "Voice builder ready. Use assistant_id with VAPI Web SDK to start the call.",
    }


@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Receives VAPI end-of-call webhook.
    Extracts transcript, builds employee with Claude, saves to Supabase.
    """
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ok"}

    msg_type = payload.get("message", {}).get("type", "")

    # We only care about end-of-call-report
    if msg_type != "end-of-call-report":
        return {"status": "ok", "ignored": True}

    call      = payload.get("message", {}).get("call", {})
    artifact  = payload.get("message", {}).get("artifact", {})
    transcript = artifact.get("transcript", "")
    session_id = call.get("assistantOverrides", {}).get("serverUrlSecret") or \
                 payload.get("message", {}).get("serverUrlSecret", "")

    if not session_id or session_id not in _sessions:
        # Try to find session by assistant_id
        assistant_id = call.get("assistantId", "")
        for sid, data in _sessions.items():
            if data.get("assistant_id") == assistant_id:
                session_id = sid
                break

    if not session_id or session_id not in _sessions:
        return {"status": "ok", "warning": "Session not found"}

    _sessions[session_id]["status"] = "processing"
    _sessions[session_id]["transcript"] = transcript

    try:
        employee_profile = build_employee_from_transcript(transcript)
        _sessions[session_id]["employee"] = employee_profile
        _sessions[session_id]["status"] = "complete"

        # Save to Supabase
        client_id = _sessions[session_id].get("client_id")
        await save_custom_employee(client_id, session_id, employee_profile)

    except Exception as e:
        _sessions[session_id]["status"] = "error"
        _sessions[session_id]["error"] = str(e)

    return {"status": "ok"}


@router.get("/result/{session_id}")
async def get_result(session_id: str):
    """
    Frontend polls this after the call ends to get the completed employee profile.
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[session_id]
    return {
        "session_id": session_id,
        "status":     session["status"],
        "employee":   session.get("employee"),
        "error":      session.get("error"),
    }


@router.post("/deploy")
async def deploy_custom_employee(req: VoiceBuilderDeployRequest):
    """
    Optionally deploys the custom employee as a live VAPI assistant
    so it can be called / embedded immediately.
    """
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[req.session_id]
    if session["status"] != "complete" or not session.get("employee"):
        raise HTTPException(status_code=400, detail="Employee profile not yet complete")

    emp = session["employee"]

    if not VAPI_API_KEY:
        raise HTTPException(status_code=500, detail="VAPI_API_KEY not configured")

    async with httpx.AsyncClient() as c:
        resp = await c.post(
            f"{VAPI_BASE}/assistant",
            headers={"Authorization": f"Bearer {VAPI_API_KEY}", "Content-Type": "application/json"},
            json={
                "name": f"{emp.get('name')} — {emp.get('role')}",
                "model": {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-20250514",
                    "messages": [{"role": "system", "content": emp.get("system_prompt", "")}],
                    "temperature": 0.6,
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "ErXwobaYiN019PkySvjV",
                },
                "firstMessage": f"Hi! I'm {emp.get('name')}, your {emp.get('role')}. How can I help you today?",
                "endCallFunctionEnabled": True,
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "en-US",
                },
            },
            timeout=30,
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"VAPI deploy error: {resp.text}")

    vapi_data = resp.json()

    return {
        "status":       "deployed",
        "vapi_assistant_id": vapi_data.get("id"),
        "employee_name": emp.get("name"),
        "employee_role": emp.get("role"),
        "message":      f"{emp.get('name')} is now live as a VAPI assistant.",
    }