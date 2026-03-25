# Onboarding Agents — Library Index

## The 6 Onboarding Teams

Each team has a dedicated agent that fires when triggered by the Orchestrator.

```
ONBOARDING ORCHESTRATOR
├── Team 1: Phone & Voice Setup Agent
│   └── Tasks: VAPI config, ElevenLabs voice, call flows, business hours, test calls
│
├── Team 2: Google Ecosystem Agent
│   └── Tasks: Google Business Profile, Google Analytics, Search Console, GMB posts
│
├── Team 3: Communications Agent
│   └── Tasks: Email templates (Resend), SMS flows (Twilio), GHL pipeline setup
│
├── Team 4: Social Media Agent
│   └── Tasks: Profile copy, 30-day calendar, template posts, scheduling setup
│
├── Team 5: Business Operations Agent
│   └── Tasks: SOPs, legal docs, intake forms, internal automations
│
└── Team 6: Content Production Agent
    └── Tasks: Blog posts, ad copy, website copy, brand story, video scripts
```

## Trigger Format
Each agent is triggered by the Orchestrator with this payload:
```json
{
  "client_id": "CLT-XXXXXXXX",
  "tier": "professional",
  "team": "voice-setup",
  "client_profile": { ... },
  "brand_profile": { ... },
  "tasks": ["task_1", "task_2", ...]
}
```

## Files
- `orchestrator-agent.json`
- `voice-setup-agent.json`
- `google-ecosystem-agent.json`
- `communications-agent.json`
- `social-media-agent.json`
- `business-ops-agent.json`
- `content-production-agent.json`
