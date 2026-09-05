# `voice_edit` — Foundation Layer Module

Voice-editable onboarding for any surface (brand portfolio, website,
voice agent prompt, social brand launcher, etc.). One module, mounted
under AN, VoiceMIO, Blast Video, and any future product.

## What it does

A customer can change anything we let them change by:
- **Speaking** — on a VAPI call, or via a mic button on a web form
- **Typing** — directly editing the form
- **Drag-dropping** — files (logos, photos, docs) auto-classify and attach to the right field

State is unified across the phone call and the web form via a
short-lived JWT handoff token, so the customer can start on a call,
get a follow-up email mid-conversation, click the link, and land on the
form with everything they've already said pre-filled and live.

## What's in here

| File | Purpose |
|---|---|
| `migrations/20260429_voice_edit_foundation.sql` | Supabase tables: `editable_surfaces`, `edit_sessions`, `edit_events` + RLS + Realtime publication |
| `config/editable_fields.yaml` | Whitelist of voice-editable fields per surface, with aliases, validators, post-hooks, and confirmation flags |
| `models.py` | Pydantic models for every request, response, and internal type |
| `intent_parser.py` | Sonnet 4.6 (cached system prompt) turns transcripts into JSON Patch ops; Haiku 4.5 prefilter classifies utterances |
| `edit_engine.py` | Validates → applies patches → writes audit events → fires post-hooks |
| `upload_classifier.py` | Heuristics + Haiku-vision fallback to auto-classify dropped files |
| `session_manager.py` | Cross-channel session continuity, JWT handoff tokens, channel attach/dedupe |
| `router.py` | FastAPI router — mount on the foundation API |

## Routing per the efficiency skill

| Task | Model | Rationale |
|---|---|---|
| Voice transcription on the call | Gemini 3.1 Flash Live (VAPI) | Already in place |
| Utterance prefilter (edit/undo/confirm/chitchat) | Haiku 4.5 | Cheap classification |
| Transcript → JSON Patch | Sonnet 4.6 (cached system) | Structured reasoning |
| Drop-file classification (ambiguous cases) | Haiku 4.5 vision | Fast + free for 80% via heuristics |

## Integration

### 1. Run the migration

```bash
# In your supabase repo
supabase migration new voice_edit_foundation
# then paste migrations/20260429_voice_edit_foundation.sql into the new file
supabase db push
```

Then create the storage bucket (control-plane action, not pure SQL):

```bash
supabase storage buckets create voice-edit-assets --public=false
```

### 2. Mount the router on `foundation-api`

```python
# foundation/main.py
from foundation.voice_edit.router import router as voice_edit_router
app.include_router(voice_edit_router, prefix="/voice-edit")
```

### 3. Env vars (Render)

```
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://rzsryxvlaezfvftqpvbx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
VOICE_EDIT_HANDOFF_SECRET=<generate with: openssl rand -hex 32>
VOICE_EDIT_PUBLIC_BASE_URL=https://app.automaitionnation.com
PIPELINE_API_KEY=<existing>

# Optional model overrides — defaults from the efficiency skill
MODEL_FAST=claude-haiku-4-5-20251001
MODEL_STANDARD=claude-sonnet-4-6
MODEL_COMPLEX=claude-opus-4-6
```

### 4. Pip dependencies

```
fastapi
pydantic>=2
anthropic
supabase
PyJWT
PyYAML
```

### 5. Wire VAPI into voice-edit

Add a tool to your VAPI agents:

```json
{
  "name": "voice_edit",
  "description": "Apply customer edits to their brand profile, website, voice agent, or social config by interpreting their spoken request.",
  "parameters": {
    "type": "object",
    "properties": {
      "transcript": {"type": "string"},
      "session_id": {"type": "string"}
    },
    "required": ["transcript", "session_id"]
  },
  "url": "https://foundation-api-9gpl.onrender.com/voice-edit/sessions/{session_id}/voice-edit",
  "method": "POST",
  "headers": { "X-API-Key": "{{PIPELINE_API_KEY}}" }
}
```

Add to the agent's system prompt:

> When the customer wants to change something about their business profile, website, voice agent, or social presence — call the `voice_edit` tool with the full utterance as `transcript`. Read back the value of `agent_should_say` verbatim. If it returns a `clarifying_question`, ask the customer that question and call the tool again with their answer.

### 6. Frontend handoff (call → email → web)

When the agent identifies a customer who wants to keep editing in the
browser, it calls:

```
POST /voice-edit/sessions
{
  "business_id": "...",
  "surface_id": "brand_portfolio",
  "channel": { "type": "voice", "vapi_call_id": "...", "attached_at": "..." }
}
```

Response includes `handoff_url`. Email that URL. When the customer
clicks, the landing page extracts `?t=<token>` and calls:

```
POST /voice-edit/sessions/resume
{ "token": "...", "channel": { "type":"web", "client_id":"<random>", "attached_at":"..." } }
```

Now both channels are attached to the same session row. Edits from
either side propagate via Supabase Realtime.

## Built-in safety / controls

- **Whitelist**: anything not in `editable_fields.yaml` cannot be voice-edited, even by an agent. Per-field.
- **Confirmation tier**: high-stakes fields (business name, phone, address, voice greeting) demand verbal confirmation before applying.
- **Audit trail**: every change is an `edit_event` with `inverse_patch`. Voice command "undo that" pops the latest.
- **RLS**: businesses can only see their own sessions and events.
- **Validators**: phone (E.164), email, postal address, business hours, color hex — all enforced server-side.
- **JWT handoff**: signed, short-lived (24h default), single-secret, revocable by expiring the session.

## Still to build (next turn)

Frontend pieces:
- `LiveEditPanel.tsx` — overlay component with mic button + drag-drop zone
- `useVoiceEdit.ts` — React hook that subscribes to Realtime updates and exposes `voiceEdit(transcript)` + `dropFile(file)` + `undo()`
- `useDragDrop.ts` — drag-drop hook with browser-side image dimensions/alpha detection (so we don't always upload before classifying)
- Email handoff landing page

Background workers:
- `validators.py` — implement the named validators referenced in the YAML
- `post_hooks/` — `generate_logo_variants`, `generate_social_avatars`, `reindex_voice_agent`, `rebuild_website_preview`

Optional polish:
- Anthropic Batch API for nightly re-validation passes
- Cost dashboard view on top of the existing `llm_usage` table
- Per-customer rate limiting on voice edits to prevent runaway agent loops
