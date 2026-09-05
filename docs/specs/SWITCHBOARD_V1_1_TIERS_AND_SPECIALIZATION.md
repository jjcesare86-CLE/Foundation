# SWITCHBOARD v1.1 — TWO-TIER ACCESS + INDUSTRY SPECIALIZATION ENGINE
**Replaces Section 1 (Locked Decisions) and adds the specialization layer to SWITCHBOARD_BUILD.md**
Drop into docs/specs/

---

## 1. THE TWO TIERS (clarified)

### Tier A — John's Properties (always full, always on)
AN, VoiceMIO, Blast Video, MRLIN, LUTS, Delivered Fireworks.
- Switchboard enabled by default, all 34 agents unlocked, no upsell gates, no per-agent billing.
- These are your showrooms — clients and prospects who visit see the full team working.
- Flag in `sb_settings`: `is_internal_property BOOLEAN DEFAULT FALSE` — internal
  properties skip entitlement checks entirely.

### Tier B — Client Properties (add-on, niche-specialized)
Exterior Rescue, Broker Broker, SAS, every future client.
- **Switchboard itself is a paid add-on** (recommend $99–199/mo for the platform, or
  bundled into Professional+ plans — Switchboard is your stickiest retention tool).
- Buddy list shows agents **specialized for their niche** — not the raw Foundation
  roster. A roofing company sees "Nathan · your roofing social media manager" not
  "Nathan · Social Media Manager (generic)." More on this in Section 2.
- Locked agents appear as upsells within the directory (same lock/pricing flow as
  before), but the visible roster is pre-filtered to agents relevant to their
  industry so it doesn't feel like noise.
- Clients can pin/unpin from their filtered list; they can browse the full directory
  to discover agents outside their niche if they want ("Show all employees").

### How it works in the bootstrap call
```
GET /switchboard/bootstrap
→ is_internal_property? → return full roster, all unlocked, no filtering
→ client property? → resolve client.industry → load industry_playbooks for that
  industry → return roster filtered to agents with playbooks for that industry
  (+ universal agents that work for everyone) → apply entitlement mask (locked/unlocked)
```

---

## 2. INDUSTRY SPECIALIZATION ENGINE — "The Lens System"

### 2.1 The problem with creating hundreds of agents
If you build "Nathan-Roofing" and "Nathan-Restaurant" and "Nathan-Cannabis" as
separate agents, you get:
- 34 agents × 50 industries = 1,700 roster rows to maintain
- Every Nathan upgrade (new social platform, new playbook rule) must be applied
  1,700 times
- New industries require building 34 new agents from scratch
- Quality degrades because attention is spread thin

### 2.2 The solution: one agent + swappable industry playbooks
An industry playbook is a structured knowledge pack that snaps onto a base agent
at prompt-compose time. Nathan is always Nathan (social media skills, platform
rules, brand-voice engine). But when he's working for a roofing company, the
playbook injects:
- Industry-specific content themes ("before/after photos convert 3x")
- Terminology ("soffit," "flashing," "ice dam" — never "roof stuff")
- Compliance rules ("no guaranteed timelines on insurance claims")
- Seasonal calendar ("storm season = content goldmine, but never ambulance-chase")
- Competitor/market context ("HomeAdvisor and Angi own paid; win on local organic")
- KPIs that matter for the niche ("Google reviews > Instagram followers for roofers")

The agent sees: [base system prompt] + [brand voice profile] + [operational params]
+ **[industry playbook for this agent × this industry]** + [thread history].

### 2.3 Schema
```sql
-- The industry registry
CREATE TABLE industries (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,            -- roofing | restaurant | cannabis | fireworks | mortgage...
  display_name TEXT NOT NULL,
  category TEXT,                        -- home_services | food_bev | healthcare | professional...
  icon TEXT,
  sort_order INT DEFAULT 0
);

-- The playbook: one row per agent × industry combination
CREATE TABLE industry_playbooks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_slug TEXT NOT NULL,             -- nathan | rahab | zacchaeus | silas...
  industry_slug TEXT NOT NULL REFERENCES industries(slug),
  version INT DEFAULT 1,
  playbook JSONB NOT NULL,              -- structured: themes[], terminology{}, compliance[],
                                        --   seasonal_calendar[], kpis[], content_templates[],
                                        --   common_objections[], pricing_norms{}, tools[]
  role_override TEXT,                   -- "your roofing social media manager" (replaces generic role line)
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (agent_slug, industry_slug, version)
);

-- Which agents are universal (work for any industry without a playbook)
-- vs which require one. Stored as a flag on ai_employees:
-- ALTER TABLE ai_employees ADD COLUMN requires_industry_playbook BOOLEAN DEFAULT FALSE;
-- Universal agents (Solomon, Caleb, Miriam, Isaiah, Abigail, Leah, Eden, Hannah,
-- Delilah, Martha, Ezra, Peter, Elijah, Rebekah) → FALSE
-- Niche-benefiting agents (Nathan, Deborah, Esther, Anna, Gideon, Rahab, Silas,
-- Zacchaeus, Joanna, Obadiah, Bezalel, Priscilla, Amos, Tabitha) → TRUE
```

### 2.4 prompt_composer.py integration
```python
def compose_prompt(agent_slug: str, client_id: str, ...) -> str:
    base = load_system_prompt(agent_slug)
    brand = load_brand_voice(client_id)
    params = load_operational_params(agent_slug, client_id)
    
    # THE NEW PIECE
    client_industry = get_client_industry(client_id)
    playbook = load_industry_playbook(agent_slug, client_industry)
    
    if playbook:
        base = inject_playbook(base, playbook)
        # Replaces generic role line with niche version
        # Injects terminology, compliance, themes, seasonal calendar
        # Adds industry-specific examples to few-shot sections
    
    return compose(base, brand, params, playbook)
```

### 2.5 Generating the playbook library at scale
This is where the powerful model earns its keep. Use **Fable 5.1** (orchestrator_max
tier) to generate playbooks in batch, because each playbook requires:
- Deep industry knowledge (compliance, seasonality, terminology)
- Cross-referencing against the agent's base capabilities
- Quality that a business owner in that niche would trust on day one

**Generation pipeline:**
1. Define the industry list (start with your existing verticals + the prospect
   engine's target niches — see Section 3).
2. For each industry × each niche-benefiting agent (14 agents):
   - Fable 5.1 prompt: "You are building a structured industry playbook for
     {agent_name} ({agent_role}) serving a {industry} business. Generate the
     playbook JSON with: themes (5–8 content/strategy themes specific to this
     industry), terminology (20+ must-know terms with plain-English definitions),
     compliance (industry-specific rules this agent must never violate),
     seasonal_calendar (12-month rhythm), kpis (the 3–5 metrics that actually
     matter in this niche), content_templates (3 ready-to-adapt templates),
     common_objections (what clients in this industry will push back on),
     pricing_norms (typical price ranges so the agent isn't naive about money).
     Be specific, not generic. A {industry} business owner reading this should
     think 'this agent knows my world.'"
   - Human review pass: you or a domain-expert contractor spot-checks each
     vertical's first batch (especially compliance). After the first 5 verticals
     are validated, the pattern is solid enough to trust Fable on the rest with
     spot-checks only.
3. Insert into industry_playbooks via a seed migration.
4. **Ongoing:** when a new industry is requested (client signs up, selects
   "Pool Service" and no playbooks exist), trigger a Fable generation job →
   playbooks created → admin review queue → activate. Client sees "Your team
   is getting trained on pool service — ready in 24h" (honest, and it builds
   anticipation).

### 2.6 Agent relevance per industry
Not every agent makes sense for every industry. The playbook table naturally
handles this: if no playbook exists for Obadiah (property manager) × restaurant,
Obadiah doesn't appear in a restaurant client's filtered buddy list. The
universal agents (C-suite, legal, admin, HR, Eden) always appear.

This means the buddy list self-curates per niche:
- **Roofing company** sees: Solomon, Caleb (universal) + Nathan, Deborah, Anna,
  Esther, Rahab, Silas, Zacchaeus, Amos, Elijah, Priscilla (all with roofing
  playbooks). They do NOT see Obadiah or Tabitha (irrelevant).
- **Nonprofit** sees: Solomon, Caleb + Tabitha (donor relations!), Nathan, Deborah,
  Esther, Zacchaeus, Priscilla, Elijah. They do NOT see Silas (no field crews).
- **Cannabis dispensary** sees: the canna.ai agent roster mapped to Foundation
  names + Amos (compliance — Metrc!), Zacchaeus (280E tax rules!), Rahab.

---

## 3. LAUNCH VERTICALS (industry playbooks to generate first)

Priority based on: (a) you already serve or have specced them, (b) the prospect
engine targets them, (c) revenue density.

### Wave 1 — Dogfood + existing clients (generate immediately)
| Industry slug | Why | Playbook agents (14 niche + universals) |
|---|---|---|
| fireworks | LUTS + Delivered = live pilots | All 14 — you know this cold |
| home_services_roofing | Exterior Rescue + StormReach | Nathan, Deborah, Anna, Esther, Rahab, Silas, Zacchaeus, Amos, Elijah, Priscilla |
| home_services_general | Exterior Rescue (gutter, power wash) | Same as roofing minus storm-specific |
| real_estate | Broker Broker Realty | Nathan, Deborah, Anna, Esther, Rahab, Obadiah, Zacchaeus, Elijah |
| mortgage | Broker Broker Mortgage | Deborah, Esther, Zacchaeus, Amos (NMLS), Elijah |
| baking_ecommerce | Bakerellas | Nathan, Deborah, Anna, Esther, Rahab, Bezalel, Zacchaeus, Elijah |
| ballistic_armor | SAS Industries | Nathan, Deborah, Gideon, Amos (ATF/ITAR), Elijah |

### Wave 2 — Prospect engine targets (generate week 2)
| Industry slug | Notes |
|---|---|
| hvac | Silas is built for this |
| plumbing | Field service + emergency dispatch |
| landscaping | Seasonal calendar is content goldmine |
| pest_control | Recurring revenue model, Silas routes |
| dental | High-ticket, review-dependent (Rahab shines) |
| medspa | Before/after content, compliance-heavy (Amos) |
| auto_dealership | Valor Arms proved the cinematic site model |
| restaurant | Rahab reviews + Nathan food content |
| fitness_gym | Retention-focused (Esther nurture sequences) |
| legal_firm | Amos (bar compliance) + Deborah (thought leadership) |

### Wave 3 — Expand to 50 (generate month 2, Fable batch API at 50% discount)
cannabis, accounting, insurance, chiropractic, veterinary, salon_barbershop,
photography, wedding_planning, funeral_home, property_management, trucking,
electrical, painting, pool_service, cleaning_service, tutoring, daycare,
pet_grooming, florist, car_wash, towing, moving, self_storage, martial_arts,
yoga_studio, church_nonprofit, construction, solar, garage_door, appliance_repair,
tattoo_studio, event_planning, catering, personal_training

**At 50 industries × 14 niche agents = 700 playbooks.** Each is a JSON document
generated by Fable 5.1 in batch. At Batch API pricing ($5/$25 per MTok, 50%
discount) and ~2K tokens per playbook output: ~1.4M output tokens = ~$35 total.
The entire 700-playbook library costs less than lunch.

### Wave ∞ — On-demand generation
New client selects an industry not in the library → Fable generates playbooks →
admin review queue → activate within 24h. The library grows organically and
every new vertical is instantly available to every future client in that niche.

---

## 4. THE PRODUCT STORY (how this sells)

### For AN/AssistMIO sales:
"Tell me your industry. We already have a team trained in it."
→ Client says "I run a dental practice."
→ Show the buddy list: Nathan knows dental content, Rahab knows dental reviews
  matter more than any other channel, Esther knows recall-reminder sequences,
  Zacchaeus knows dental-specific deductions, Amos tracks DEA license renewals.
→ "These aren't generic bots. They already know your world."

### Pricing (Tier B clients):
- **Switchboard platform fee:** $149/mo (includes 5 agent seats — the filtered
  recommended roster for their niche). Additional agents à la carte per the
  existing pricing engine.
- **OR** bundled into Professional ($499/mo, 10 agents) / Enterprise ($1,499/mo,
  unlimited) plans — Switchboard included, no separate fee.
- Internal properties (Tier A): $0, always full.

### The library as a moat:
Every playbook you generate makes the next client in that niche faster to
onboard. Competitors selling generic chatbots can't match "Nathan already knows
roofing" without building the same structured knowledge layer. And your library
grows with every client — first-mover compounding.

---

## 5. UPDATED DOCK BOOTSTRAP FLOW
```
GET /switchboard/bootstrap?tenant_key=pk_...
│
├─ Resolve client_id + user_id from JWT
├─ is_internal_property?
│  ├─ YES → return full roster (34), all unlocked, no industry filter
│  └─ NO  → resolve client.industry_slug
│          ├─ Load industry_playbooks WHERE industry = client.industry
│          │  → agent list = universal agents + agents WITH playbooks for this industry
│          ├─ Apply entitlement mask (plan tier → which of those are unlocked)
│          ├─ Locked agents in the filtered list = niche-relevant upsells
│          ├─ "Show all employees" directory = full 34 (most locked, some irrelevant
│          │   but browsable — discovery moment)
│          └─ Return: filtered roster + entitlements + pins + unreads + presence
│
└─ Each agent's display: name, role_override (from playbook, e.g. "your roofing
   social media manager"), avatar, presence, lock state
```

---

## 6. CLAUDE CODE PROMPT — SPECIALIZATION ENGINE
```
Foundation repo, branch industry-specialization. Same GLOBAL RULES. Read
docs/specs/SWITCHBOARD_V1_1_TIERS_AND_SPECIALIZATION.md.
1. Migrations: industries table, industry_playbooks table,
   requires_industry_playbook column on ai_employees (backfill per Section 2.3
   — 14 niche agents TRUE, 20 universal agents FALSE), is_internal_property
   on sb_settings, industry_slug on clients table if not present.
2. prompt_composer.py: playbook injection per Section 2.4 — playbook block
   renders between brand_voice and operational_params; role_override replaces
   the generic role line in the agent header.
3. Switchboard bootstrap: implement the two-tier flow per Section 5 — internal
   properties get full unfiltered roster; client properties get industry-
   filtered + entitlement-masked + "Show all" directory.
4. Playbook generation pipeline: admin endpoint POST /admin/generate-playbooks
   { industry_slug, agent_slugs[] } → Fable 5.1 batch call (MODEL_ORCH_MAX)
   with the structured prompt from Section 2.5 → insert rows →
   status=pending_review. Admin review endpoint to activate.
5. On-demand trigger: when a new client's industry has no playbooks, auto-
   queue generation + set client.onboarding_status='team_training' with a
   message: "Your team is getting trained on {industry} — ready within 24h."
6. Seed Wave 1 (7 industries from Section 3): run the generation pipeline
   for all 7 × their listed agents. Human-review the fireworks + roofing
   sets (John knows these cold); spot-check the rest.
VERIFY: bootstrap for an internal property returns 34 unlocked; bootstrap
for a roofing client returns ~12 filtered agents with roofing role_overrides;
bootstrap for a niche with no playbooks returns universals only + training
message; Nathan's composed prompt for a roofing client contains roofing
terminology and themes; same Nathan for a restaurant client contains
restaurant terminology.
Finish with docs/specs/SPECIALIZATION_ENGINE_COMPLETION.md including the
playbook count and any industries that need human review.
```
