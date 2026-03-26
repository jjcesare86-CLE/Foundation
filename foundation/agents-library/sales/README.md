# Sales Agents — Library Index

These are the 8-agent sales pipeline configs used by Automation Nation.

## Agent Pipeline Order
```
GREETING → DISCOVERY → SOLUTION_ARCHITECT → OBJECTION_HANDLER → CLOSER
                                                                     ↓
                                                         [YES] → ONBOARDING ORCHESTRATOR
                                                         [NO]  → NURTURE SEQUENCE
```

## Files
- `greeting-agent.json` — First contact, warm welcome + intent qualification
- `discovery-agent.json` — Pain point deep-dive, 5-7 questions
- `solution-architect-agent.json` — Maps pain to services, builds recommendation
- `objection-handler-agent.json` — Price, timing, trust, competitor objections
- `closer-agent.json` — Asks for sale, triggers onboarding on YES

## Pipeline-to-Integration Bridge (TODO)
When Closer Agent gets a YES, it must trigger:
1. Stripe Checkout → collect payment
2. GHL Sync → create contact + opportunity in pipeline
3. VAPI Deployment → spin up voice agent
4. Onboarding Orchestrator → launch 6-team onboarding
5. Welcome Email → send via Resend

See: `automation-nation` repo → `integrations/pipeline-bridge.py`
