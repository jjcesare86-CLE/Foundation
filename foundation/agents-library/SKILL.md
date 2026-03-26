---
name: ai-agent-industry-library
description: >-
  Master library of industry-specific and role-specific AI sub-agents and skills
  for building comprehensive AI automation solutions. Use when a client selects
  an industry vertical and you need to design a full AI agent ecosystem that goes
  far beyond basic appointment setting — including voice agents, intake forms,
  diagnostic tools, interactive widgets, CRM automation, predictive analytics,
  and sticky features that make the service irreplaceable. Covers 25+ industries
  with deep, actionable blueprints for each. Use when designing AI agent packages,
  building Vapi voice agents, configuring Go High Level sub-accounts, or consulting
  with clients about what AI can do for their specific business.
metadata:
  author: automation-nation
  version: '1.0'
---

# AI Agent Industry Library — Master Blueprint

## Purpose

This skill provides deep, actionable blueprints for building AI agent ecosystems across 25+ industry verticals. Each blueprint goes far beyond basic appointment setting to include every AI-powered tool, widget, workflow, and integration that makes the service irreplaceable ("sticky") for the client.

## When to Use This Skill

- A client selects an industry and you need to design their full AI agent package
- You're building Vapi voice agents, GHL workflows, or chatbot systems for a specific niche
- You need to understand what advanced AI capabilities exist for a given industry
- You're creating proposals, demos, or sales materials for AI automation services
- You want to identify the highest-value, stickiest features for any vertical

## How This Skill Works

1. The user identifies an industry or role
2. Load the corresponding reference file from `references/` for that industry
3. Use the blueprint to design the complete agent ecosystem
4. Customize to the specific client's tech stack, size, and needs

## Master Industry Index

Each industry below has a detailed reference file. Load the relevant file when working on that vertical.

### Tier 1 — Highest Demand / Highest Value Industries

| # | Industry | Reference File | Stickiness Score |
|---|----------|---------------|-----------------|
| 1 | Real Estate | `references/01-real-estate.md` | ★★★★★ |
| 2 | Healthcare (Medical/Dental) | `references/02-healthcare.md` | ★★★★★ |
| 3 | Legal Services | `references/03-legal.md` | ★★★★★ |
| 4 | Home Services (HVAC/Plumbing/Electrical) | `references/04-home-services.md` | ★★★★★ |
| 5 | Insurance | `references/05-insurance.md` | ★★★★★ |
| 6 | Automotive (Dealerships & Repair) | `references/06-automotive.md` | ★★★★★ |
| 7 | Financial Services / Mortgage | `references/07-financial-mortgage.md` | ★★★★★ |

### Tier 2 — High Demand / Strong Retention

| # | Industry | Reference File | Stickiness Score |
|---|----------|---------------|-----------------|
| 8 | Restaurant & Food Service | `references/08-restaurant.md` | ★★★★☆ |
| 9 | Salon / Spa / Beauty | `references/09-salon-spa.md` | ★★★★☆ |
| 10 | Veterinary | `references/10-veterinary.md` | ★★★★☆ |
| 11 | Fitness / Gym / Personal Training | `references/11-fitness.md` | ★★★★☆ |
| 12 | Property Management | `references/12-property-management.md` | ★★★★☆ |
| 13 | Recruitment / Staffing | `references/13-recruitment.md` | ★★★★☆ |
| 14 | Construction / Contracting | `references/14-construction.md` | ★★★★☆ |

### Tier 3 — Growing Demand / Niche Opportunities

| # | Industry | Reference File | Stickiness Score |
|---|----------|---------------|-----------------|
| 15 | E-Commerce / Retail | `references/15-ecommerce.md` | ★★★★☆ |
| 16 | Coaching / Consulting | `references/16-coaching.md` | ★★★★☆ |
| 17 | Accounting / Bookkeeping | `references/17-accounting.md` | ★★★★☆ |
| 18 | Chiropractic / Wellness | `references/18-chiropractic.md` | ★★★☆☆ |
| 19 | Pest Control / Cleaning Services | `references/19-pest-control-cleaning.md` | ★★★☆☆ |
| 20 | Roofing / Solar | `references/20-roofing-solar.md` | ★★★☆☆ |
| 21 | Education / Tutoring | `references/21-education.md` | ★★★☆☆ |
| 22 | Logistics / Transportation | `references/22-logistics.md` | ★★★★☆ |
| 23 | SaaS / Tech Companies | `references/23-saas.md` | ★★★★☆ |
| 24 | Travel / Hospitality | `references/24-travel-hospitality.md` | ★★★☆☆ |
| 25 | Funeral Services | `references/25-funeral.md` | ★★★☆☆ |

---

## Universal Agent Architecture (Applies to ALL Industries)

Every industry package should include these foundational layers, customized for the vertical:

### Layer 1: Voice Agent System (Vapi / ElevenLabs / Retell)
- **Inbound Call Handler**: 24/7 answering, intent detection, call routing
- **Outbound Caller**: Follow-ups, reminders, reactivation campaigns, review requests
- **After-Hours Agent**: Emergency triage, voicemail-to-text, callback scheduling
- **Multi-language Support**: Auto-detect caller language, respond accordingly
- **Sentiment Detection**: Real-time tone analysis, escalation triggers for frustration/urgency
- **Call Recording + Transcription**: Compliance-ready logs, AI-generated call summaries
- **Warm Transfer Protocol**: Seamless handoff to human with full context briefing

### Layer 2: Chat / Web Agent System
- **Website Chat Widget**: Embedded on client site, handles inquiries 24/7
- **SMS/Text Agent**: Two-way conversational texting for scheduling, follow-ups
- **Social Media DM Agent**: Instagram, Facebook Messenger, WhatsApp auto-responses
- **Email Agent**: Reads inbound emails, drafts responses, routes to appropriate team member
- **Live Chat Escalation**: Smart handoff to human when AI confidence drops below threshold

### Layer 3: CRM & Pipeline Automation (Go High Level / HubSpot)
- **Lead Capture & Scoring**: Auto-score leads based on intent signals, demographics, behavior
- **Pipeline Stage Automation**: Auto-move contacts through sales stages based on actions
- **AI Decision Maker**: Plain-English routing logic (GHL's native AI decision node)
- **Automated Nurture Sequences**: Drip campaigns personalized by AI based on lead profile
- **Win-Back Campaigns**: AI identifies dormant leads/clients, triggers re-engagement
- **Review Generation**: Post-service automated review requests with smart timing

### Layer 4: Booking & Calendar System
- **AI-Powered Scheduling**: Books appointments into team calendars based on availability, expertise, and priority
- **No-Show Prevention**: Confirmation + reminder sequences (SMS, email, voice call)
- **Smart Rescheduling**: AI offers alternative times when cancellations happen
- **Emergency Priority Routing**: Urgent requests bypass normal queue
- **Resource Allocation**: Match bookings to specific staff/rooms/equipment

### Layer 5: Analytics & Intelligence Dashboard
- **Call Analytics**: Volume, duration, conversion rates, peak times
- **Lead Source Attribution**: Which channels produce the highest-quality leads
- **Revenue Attribution**: Track which AI interactions led to closed deals
- **Churn Prediction**: AI flags at-risk clients based on engagement patterns
- **Staff Performance**: Compare AI-handled vs human-handled metrics

### Layer 6: Compliance & Security
- **HIPAA Module** (healthcare): Encrypted data, BAA agreements, audit trails
- **PCI Compliance** (payments): Secure payment processing protocols
- **TCPA Compliance** (calling): Opt-in/out management, calling time restrictions
- **GDPR/CCPA Module**: Data privacy, consent management, right-to-delete
- **Call Recording Consent**: Auto-announce recording per state laws

---

## Sticky Feature Categories (What Makes Clients Never Leave)

These are the advanced features — beyond appointment setting — that create deep dependency:

### Category A: Industry-Specific Intake & Diagnostic Tools
- Smart forms that adapt questions based on previous answers
- AI pre-diagnosis/triage before human consultation
- Photo/video upload analysis (pets, property damage, vehicles, skin conditions)
- Insurance verification automation
- Cost estimation engines

### Category B: Interactive Widgets & Client-Facing Tools
- Virtual staging / room design (real estate)
- Treatment cost calculators (dental, medical)
- Vehicle diagnostic lookup (automotive)
- Meal planning generators (fitness, nutrition)
- Project estimators (construction, roofing)
- Loan qualification calculators (mortgage)
- Insurance quote generators

### Category C: Operational Automation
- Intelligent dispatch and routing (home services, logistics)
- Inventory management with auto-reorder (restaurants, salons, retail)
- Staff scheduling optimization
- Route optimization for field teams
- Automated document generation (contracts, invoices, proposals)

### Category D: Revenue Amplification
- AI-powered upsell/cross-sell recommendations
- Dynamic pricing suggestions based on demand
- Abandoned cart / dropped lead recovery
- Referral program automation
- Loyalty program management

### Category E: Knowledge & Training
- AI-powered employee training modules
- Client education content delivery
- FAQ knowledge bases that learn from interactions
- Compliance training tracking

---

## How to Use This Library for Client Consultations

### Step 1: Industry Discovery
Ask: "What industry is your business in?"
→ Load the corresponding reference file

### Step 2: Current Pain Point Assessment
Ask: "What are the top 3 things that take up the most time in your business?"
→ Map to specific sub-agents in the blueprint

### Step 3: Tech Stack Audit
Ask: "What software do you currently use?" (CRM, POS, scheduling, etc.)
→ Design integrations around existing tools

### Step 4: Package Design
Use the industry blueprint to design a tiered package:
- **Starter**: Voice agent + booking + basic CRM (Quick win, low barrier)
- **Professional**: + Intake forms + pipeline automation + analytics
- **Enterprise**: + Interactive widgets + diagnostics + operational automation + custom integrations

### Step 5: Stickiness Strategy
Identify the 2-3 features from Categories A-E above that will make this client dependent on your system. These are the features that are painful to replicate or migrate away from.

---

## Implementation Priority Framework

When building for a new industry client, deploy in this order:

1. **Week 1**: Voice agent (inbound) + booking system + basic CRM setup
2. **Week 2**: Chat widget + SMS agent + lead capture forms
3. **Week 3**: Industry-specific intake forms + pipeline automation
4. **Week 4**: Analytics dashboard + review generation + nurture sequences
5. **Month 2**: Interactive widgets + diagnostic tools + operational automation
6. **Month 3**: Advanced integrations + custom features + revenue amplification tools

---

## Reference Files

Each industry reference file in `references/` contains:
- Complete list of sub-agents with detailed descriptions
- Industry-specific intake form designs
- Interactive widget specifications
- Integration requirements (which APIs, platforms, data sources)
- Sticky feature breakdown with implementation notes
- Employee role mapping (which roles get which agents)
- Competitive advantages (what others in the space are doing)
- Revenue model suggestions (how to price the package)
- Real-world examples and case studies
