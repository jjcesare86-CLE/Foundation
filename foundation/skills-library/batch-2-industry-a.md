# Batch 2: Industry-Specific Skills Group A (041-080)

**40 Deployable AI Skill/Sub-Agent Definitions**
**Industries Covered**: Real Estate | Healthcare/Dental | Legal | Home Services | Insurance | Automotive | Restaurant

---

## Table of Contents

| # | Skill Name | Industry | Category | Value/Month |
|---|-----------|----------|----------|-------------|
| 041 | AI Virtual Staging Engine | Real Estate | Widget/Tool | $800–$2,500 |
| 042 | AI Inspection Report Analyzer | Real Estate | Analytics/Workflow | $500–$1,200 |
| 043 | AI Comparative Market Analysis Generator | Real Estate | Analytics/Content | $1,000–$3,000 |
| 044 | AI Listing Description Writer | Real Estate | Content Engine | $300–$800 |
| 045 | AI Neighborhood Intelligence Agent | Real Estate | Analytics/Widget | $600–$1,500 |
| 046 | AI Seller Net Sheet Calculator | Real Estate | Widget/Analytics | $400–$1,000 |
| 047 | AI Open House Follow-Up Agent | Real Estate | Voice/Chat/Automation | $400–$1,000 |
| 048 | AI Patient Symptom Triage Bot | Healthcare | Chat/Voice/Intake | $1,200–$3,500 |
| 049 | AI Insurance Verification Agent | Healthcare | Workflow/Operations | $1,500–$4,000 |
| 050 | AI Treatment Cost Estimator Widget | Healthcare | Widget/Tool | $600–$1,800 |
| 051 | AI Patient Recall Agent | Healthcare | Workflow/Voice | $800–$2,500 |
| 052 | AI Post-Procedure Follow-Up Agent | Healthcare | Workflow/Chat/Voice | $600–$1,500 |
| 053 | AI Dental Treatment Plan Presenter | Healthcare | Widget/Analytics | $1,000–$3,000 |
| 054 | AI Mental Health Screening Intake | Healthcare | Intake/Diagnostic | $800–$2,500 |
| 055 | AI Chronic Disease Management Agent | Healthcare | Chat/Workflow | $1,500–$4,500 |
| 056 | AI Case Qualification Bot | Legal | Intake/Diagnostic | $1,500–$5,000 |
| 057 | AI Contract Review Agent | Legal | Analytics/Diagnostic | $1,500–$6,000 |
| 058 | AI Personal Injury Case Calculator | Legal | Widget/Analytics | $800–$2,500 |
| 059 | AI Estate Planning Questionnaire | Legal | Intake/Workflow | $600–$2,000 |
| 060 | AI Court Deadline Tracker | Legal | Operations/Workflow | $1,000–$3,500 |
| 061 | AI Demand Letter Generator | Legal | Content/Workflow | $600–$2,000 |
| 062 | AI Emergency Dispatch Triage Agent | Home Services | Voice Agent | $1,000–$3,500 |
| 063 | AI Job Estimator Widget | Home Services | Widget/Tool | $400–$1,200 |
| 064 | AI Smart Dispatch & Route Optimizer | Home Services | Operations/Workflow | $1,500–$5,000 |
| 065 | AI Seasonal Maintenance Campaign Agent | Home Services | Workflow/Chat | $500–$1,500 |
| 066 | AI Weather-Triggered Campaign Agent | Home Services | Workflow/Operations | $500–$1,500 |
| 067 | AI Energy Audit Calculator Widget | Home Services | Widget/Analytics | $400–$1,200 |
| 068 | AI Quote Generation Voice Agent | Insurance | Voice Agent | $1,500–$5,000 |
| 069 | AI Claims Intake Bot (FNOL) | Insurance | Chat/Voice/Intake | $1,200–$4,000 |
| 070 | AI Underwriting Assistant | Insurance | Analytics/Workflow | $2,000–$7,000 |
| 071 | AI Policy Comparison Widget | Insurance | Widget/Tool | $500–$1,500 |
| 072 | AI Catastrophe Response Agent | Insurance | Workflow/Voice | $2,500–$8,000 |
| 073 | AI Life Insurance Needs Calculator | Insurance | Widget/Analytics | $400–$1,200 |
| 074 | AI Vehicle Diagnostic Pre-Assessment | Automotive | Chat/Voice/Intake | $600–$1,800 |
| 075 | AI Digital Vehicle Inspection Reporter | Automotive | Content/Workflow | $1,000–$3,500 |
| 076 | AI Trade-In Value Estimator Widget | Automotive | Widget/Tool | $600–$2,000 |
| 077 | AI Recall & TSB Monitor | Automotive | Workflow/Operations | $500–$1,500 |
| 078 | AI Phone Ordering Agent | Restaurant | Voice Agent | $1,500–$5,000 |
| 079 | AI Reservation & Waitlist Manager | Restaurant | Chat/Voice/Workflow | $800–$2,500 |
| 080 | AI Inventory Forecasting Agent | Restaurant | Analytics/Operations | $1,000–$4,000 |

---

# REAL ESTATE (041-047)

---

## SKILL-041: AI Virtual Staging Engine

**Category**: Widget/Tool
**Applies To**: Residential Real Estate — agents, brokers, listing specialists, property investors
**Deployment Platform**: Custom (AI image API integration) + GHL or standalone web widget
**Complexity**: High
**Monthly Value to Client**: $800 - $2,500

### What It Does
Transforms photos of vacant or poorly furnished rooms into professionally staged images across multiple interior design styles (modern, farmhouse, luxury, minimalist, coastal, mid-century, etc.) using generative AI. The engine allows listing agents to present any property at its best possible visual state without physical staging costs of $2,000–$8,000 per listing. Staged photos are delivered within minutes directly from the agent's branded portal.

### Core Capabilities
- Upload empty or cluttered room photos and receive AI-staged alternatives in 2-5 minutes
- Select from 8+ interior design style presets with one-click switching
- Batch process multiple rooms in a single job (full house staging in under 15 minutes)
- Remove unwanted objects (old furniture, clutter) and replace with styled furnishings
- Generate 3–5 style variants per room for A/B testing in listings
- Watermark and brand output images with agent/brokerage logo
- Export in MLS-ready dimensions (JPEG/PNG, 1200×800 minimum)
- Track staging jobs per listing with before/after comparison view

### Data Inputs Required
- Raw room photos (JPEG/PNG, minimum 800px wide)
- Room type designation (living room, bedroom, kitchen, bathroom, etc.)
- Desired design style selection
- Optional: brand color palette for watermarking
- Optional: furniture exclusion/inclusion preferences

### Integration Points
- Google Drive / Dropbox for photo storage and delivery
- MLS platforms (via manual export or API where available)
- GHL opportunity/contact records to tie staging jobs to listings
- Canva or Photoshop plugins for further editing post-staging
- Listing management tools (Homesnap, ShowingTime, Buyside)

### Sample Prompt/Persona
> "You are a professional real estate staging coordinator. When a user uploads room photos, confirm the room type, ask which staging style they prefer from the available presets, then submit the job and return staged versions. Present all results with a before/after comparison. Offer to run additional style variants or batch the next room. Always remind users that output images are AI-generated and should be labeled 'virtually staged' per NAR disclosure guidelines."

### Customization Variables
- Available design style presets per brokerage brand standards
- Watermark logo and color scheme per agent/team
- Default MLS export resolution per market
- Disclosure language per state (NAR compliance)
- Number of style variants included in base vs. premium tier
- Client-facing portal white-label branding

### Stickiness Factor
Agents who use this tool build it into their listing workflow standard operating procedure — it becomes the first step after signing a listing agreement. The per-listing output creates a growing archive tied to the brokerage's GHL instance, making migration painful. Agents also train sellers to expect virtual staging as part of the service, creating external expectations that further lock in the workflow.

### Upsell Path
Pairs naturally with SKILL-044 (AI Listing Description Writer) to create a complete listing launch package. Can be bundled with a professional photography coordination workflow. High-volume agents (15+ listings/month) unlock volume pricing tiers, creating a natural upsell to a full listing operations package.

---

## SKILL-042: AI Inspection Report Analyzer

**Category**: Analytics / Workflow Automation
**Applies To**: Residential Real Estate — buyer's agents, listing agents, transaction coordinators
**Deployment Platform**: Claude (document analysis) + GHL automation + Custom webhook
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,200

### What It Does
Ingests raw home inspection reports (typically 40–80 pages of PDF) and produces a crisp, prioritized 1-page executive summary that categorizes findings by severity: Safety Hazards, Major Defects, Minor Defects, and Maintenance Items. This eliminates 2–3 hours of agent reading time per transaction and gives buyers a clear, anxiety-reducing picture of the property's condition within minutes of receiving the report.

### Core Capabilities
- Parse multi-page PDF inspection reports from any major inspection software (HouseCheck, HomeGauge, Spectora, iNACHI-format)
- Categorize all findings into: Safety Hazard / Major Defect / Minor Defect / Maintenance Item
- Estimate repair cost ranges per finding using regional labor/material benchmarks
- Generate total estimated repair cost range for negotiation leverage
- Flag items that affect insurability (mold, roof age, electrical panels, foundation)
- Highlight items that typically trigger lender flags (FHA/VA specific)
- Output a clean 1-page PDF summary in agent-branded format
- Auto-attach summary to GHL opportunity record and trigger buyer notification

### Data Inputs Required
- Inspection report PDF (any standard format)
- Property address (for regional cost benchmarking)
- Transaction type flag (FHA/VA/Conventional) for lender-specific flagging
- Optional: client's stated repair budget threshold for prioritization

### Integration Points
- GHL (attach summary to opportunity, trigger follow-up sequences)
- DocuSign / Dotloop (attach to transaction file)
- Email/SMS delivery to buyer and agent simultaneously
- Zapier webhook for connection to transaction management platforms (Skyslope, Dotloop, Brokermint)
- Regional cost databases (RSMeans, HomeAdvisor benchmarks)

### Sample Prompt/Persona
> "You are a licensed home inspector's expert assistant reviewing an uploaded inspection report. Extract ALL noted deficiencies. Categorize each as Safety Hazard, Major Defect, Minor Defect, or Maintenance Item using standard inspector definitions. For each item in the top two categories, provide a brief explanation of why it matters and an estimated repair cost range. Summarize the total estimated remediation cost. Flag any items that may affect insurability or trigger lender conditions. Output must be under 2 pages, written in plain English for a first-time homebuyer, using no jargon."

### Customization Variables
- Agent/brokerage branding on output PDF
- Regional labor cost multiplier (varies significantly by market)
- Lender type flags enabled/disabled (FHA, VA, USDA, conventional)
- Cost estimate source (HomeAdvisor national, RSMeans local, or agent-defined ranges)
- Summary length preference (1-page max vs. 2-page detailed)
- Automatic GHL trigger actions post-analysis

### Stickiness Factor
Transaction coordinators and agents build this into their standard contract-to-close checklist as step one after inspection receipt. Every transaction processed through the system adds to an audit trail of analyzed reports tied to the agent's GHL, creating historical data on property condition trends by neighborhood. Removing the tool would break a workflow that buyers and TCs have come to expect.

### Upsell Path
Naturally leads to an AI Repair Request Generator that drafts the formal repair addendum from the summary findings. Bundle with SKILL-043 (CMA Generator) for a complete offer-through-close analytics package. High-volume teams (20+ transactions/month) benefit from a team-level dashboard showing average repair costs by neighborhood.

---

## SKILL-043: AI Comparative Market Analysis Generator

**Category**: Analytics / Content Engine
**Applies To**: Residential Real Estate — listing agents, buyer's agents, appraisers
**Deployment Platform**: Custom (MLS data integration) + Claude + GHL
**Complexity**: High
**Monthly Value to Client**: $1,000 - $3,000

### What It Does
Connects to MLS data feeds (via RETS/RESO API or data aggregators like Bridge Interactive or Spark Platform) and automatically generates professional, client-ready Comparative Market Analysis reports within minutes. The agent inputs an address and parameters, the system pulls relevant comps, applies adjustments, and produces a branded PDF report with pricing recommendations — a task that previously took 45–90 minutes per report by hand.

### Core Capabilities
- Pull active, pending, and sold comps from MLS within configurable radius and timeframe
- Apply automated adjustments for square footage, beds/baths, garage, lot size, condition, and year built
- Calculate price-per-square-foot analysis with trend visualization
- Generate days-on-market analysis and absorption rate for the micro-market
- Produce recommended list price range with confidence interval
- Include neighborhood sold price trend chart (6-month and 12-month views)
- Generate client-ready branded PDF with agent headshot, bio, and contact info
- Deliver via GHL email sequence with personalized seller narrative

### Data Inputs Required
- Subject property address
- MLS board credentials (agent's active MLS login or data feed API key)
- Comp search parameters: radius (0.25–1 mile), timeframe (3–12 months), property type
- Agent branding assets (logo, headshot, brand colors, bio)
- Optional: known property condition, recent updates, unique features

### Integration Points
- MLS data feeds: RETS/RESO APIs, Bridge Interactive, Spark Platform, MLS Grid
- GHL CRM (auto-create opportunity, attach CMA, trigger seller nurture sequence)
- Cloud Cma, MoxiPresent (as fallback for branded output formatting)
- Google Maps API (for neighborhood map overlay in report)
- Email delivery platforms for branded CMA presentation

### Sample Prompt/Persona
> "You are an expert real estate pricing analyst. When given a subject property and comp data, analyze the market carefully. Prioritize closed sales within 0.5 miles in the last 6 months. Adjust for material differences — explain each adjustment clearly. Be honest about market uncertainty — provide a recommended range, not a single number. Your tone is confident but consultative; you are helping a homeowner make a major financial decision. The final report must read like it was prepared by a seasoned listing agent, not a computer."

### Customization Variables
- MLS board connection (unique per agent/brokerage)
- Default comp search parameters per local market norms
- Adjustment logic per market (e.g., garage premium varies widely by climate)
- Agent branding (logo, colors, headshot, bio, tagline)
- Report narrative tone (consultative vs. data-heavy)
- Delivery method (email, text link, printed PDF)

### Stickiness Factor
CMA generation is the #1 activity that converts seller leads to signed listing agreements. An agent who runs 3–5 CMAs per week and has this embedded in their workflow cannot practically remove it — it would require returning to manual 90-minute sessions. The MLS data connection, once established and tuned to a specific market, represents significant setup investment. Brokerages that deploy this across their agent roster create team-wide dependency.

### Upsell Path
Pair with SKILL-044 (Listing Description Writer) and SKILL-041 (Virtual Staging Engine) for a complete "listing ready in 24 hours" package. High-volume brokerages (50+ agents) benefit from a market analytics dashboard built on aggregated CMA data. Upsell to automated seller pricing alert system that re-runs CMAs monthly for pipeline nurture.

---

## SKILL-044: AI Listing Description Writer

**Category**: Content Engine
**Applies To**: Residential & Commercial Real Estate — listing agents, brokers, property managers
**Deployment Platform**: Claude + GHL + Custom intake form
**Complexity**: Low
**Monthly Value to Client**: $300 - $800

### What It Does
Transforms a structured property data intake form (beds, baths, square footage, features, upgrades, location highlights, seller's story) into compelling, MLS-compliant listing descriptions that convert browsers into showing requests. The system writes multiple variants (full MLS description, short social media caption, email marketing version, luxury narrative version) in under 60 seconds, matching the agent's brand voice and local market tone.

### Core Capabilities
- Generate full MLS description (up to 500 characters for portals with limits, or unlimited for broker sites)
- Produce Instagram/Facebook caption variants (150–250 characters)
- Write email marketing version (150–200 words, storytelling format)
- Create luxury narrative version for high-end properties ($1M+)
- Incorporate neighborhood highlights, walkability, school district naturally
- Flag overused clichés ("cozy," "must-see," "charming") and replace with specific language
- Ensure MLS compliance (no fair housing violations, no contact info in description)
- Output in multiple reading levels (standard buyer vs. sophisticated investor)

### Data Inputs Required
- Property address
- Beds, baths, square footage, lot size, year built, garage
- Key features list (finishes, appliances, upgrades, outdoor spaces)
- Neighborhood highlights (schools, proximity to amenities, transit)
- Unique selling points (seller's story, recent renovations, views)
- Agent's preferred tone/style (energetic, sophisticated, friendly, professional)
- Price point category (starter, mid-range, luxury, ultra-luxury)

### Integration Points
- GHL intake form → automatic description generation → attach to opportunity
- MLS input forms (copy-paste optimized output)
- Social media scheduling tools (Buffer, Hootsuite) for direct caption posting
- Email marketing platforms (Mailchimp, Constant Contact, GHL email)
- Canva integration for direct use in listing flyer templates

### Sample Prompt/Persona
> "You are a top-producing real estate copywriter who has written thousands of listing descriptions. You write with specificity — never vague adjectives, always concrete details. You open with the property's single most compelling hook. You write to the buyer's emotion first, then back it up with features. You are MLS-compliant: no phone numbers, no fair housing violations, no all-caps. You always produce three variants: MLS standard, social media short, and email marketing. Ask the agent to confirm the price tier so you can match the appropriate vocabulary register."

### Customization Variables
- Agent/team brand voice and style guide
- Character limits per MLS board (varies by market)
- Preferred vocabulary and phrases per brokerage brand standards
- Tone intensity level (subdued/professional vs. enthusiastic/marketing-forward)
- Fair housing compliance rules per state
- Auto-publish to GHL listing pipeline stage

### Stickiness Factor
Agents using this tool generate better descriptions than they ever wrote manually — and they know it. Once the brand voice is calibrated, the output feels authentically "theirs," making it nearly impossible to revert. The time savings (15–30 minutes per listing) compounds to multiple hours monthly for active agents. MLS output quality becomes a differentiator in listing presentations.

### Upsell Path
Bundle with SKILL-041 (Virtual Staging) and SKILL-043 (CMA Generator) as a "List Launch Trifecta." Upsell to social media content calendar automation that distributes listing content across Instagram, Facebook, and LinkedIn automatically. High-volume teams can unlock a listing content archive that repurposes past listings for market report content.

---

## SKILL-045: AI Neighborhood Intelligence Agent

**Category**: Analytics / Widget/Tool
**Applies To**: Residential Real Estate — buyer's agents, relocation specialists, investor advisors
**Deployment Platform**: Custom API aggregation + Claude + GHL + Embeddable widget
**Complexity**: High
**Monthly Value to Client**: $600 - $1,500

### What It Does
Delivers a comprehensive, hyperlocal neighborhood intelligence report for any US address in under 30 seconds, pulling from multiple live data sources: school ratings (GreatSchools), crime statistics (SpotCrime, CrimeGrade), Walk Score and Bike Score, commute time analysis to user-defined destinations, Points of Interest density, and flood/fire/environmental risk. Buyers get objective data to replace the subjective "is this a good neighborhood?" anxiety conversation.

### Core Capabilities
- Pull GreatSchools ratings for all assigned schools (elementary, middle, high) at any address
- Retrieve crime risk scores and incident category breakdown (property crime, violent crime, trends)
- Calculate Walk Score, Transit Score, and Bike Score
- Generate commute time analysis to up to 5 user-defined destinations (work, family, gym, etc.)
- Identify nearest grocery, pharmacy, hospital, restaurant, park within configurable radius
- Pull FEMA flood zone designation and fire risk rating
- Calculate noise pollution estimate (proximity to highways, airports, rail)
- Output branded neighborhood report as PDF and embeddable widget for listing pages

### Data Inputs Required
- Subject property address (street, city, state, ZIP)
- Up to 5 commute destination addresses
- Agent/brokerage branding assets
- Optional: buyer demographic profile (family with kids → weight schools heavily; young professional → weight walkability/transit)

### Integration Points
- GreatSchools API (school data)
- Walk Score API (walkability/transit/bikeability)
- SpotCrime or CrimeGrade API (crime data)
- Google Maps / Distance Matrix API (commute times)
- FEMA flood map API (flood zone data)
- GHL CRM (attach report to buyer contact record, trigger follow-up)
- IDX website plugins (embed neighborhood widget on listing detail pages)

### Sample Prompt/Persona
> "You are a relocation specialist and neighborhood data analyst. When given an address, compile a complete neighborhood profile using all available data sources. Present the report with a clear scoring summary at the top (A–F grades for schools, safety, walkability, and commute). Use plain language — avoid jargon. Be honest about trade-offs: if walkability is low but school ratings are excellent, say so directly. Tailor the emphasis to the buyer's stated priorities. Never editorialize about neighborhood character in ways that could imply fair housing bias — stick to data."

### Customization Variables
- Weighting algorithm per buyer profile (family vs. single vs. retiree)
- Commute destination presets (downtown office cores, major employment hubs)
- Data source selection (premium vs. free tier APIs)
- Report branding per agent/brokerage
- Output language (English/Spanish bilingual support)
- Embeddable widget style (light/dark, color scheme)

### Stickiness Factor
Buyer agents who include this report in every property tour packet create a standard of service that clients rave about and refer friends for. The commute analysis in particular is highly personalized — once a buyer's destinations are saved in GHL, the system auto-generates neighborhood reports for every showing, creating deep workflow integration. IDX websites that embed the widget see measurably higher engagement, creating a performance dependency that clients can see in analytics.

### Upsell Path
Natural companion to SKILL-043 (CMA Generator) for a complete property intelligence package. Upsell to an automated monthly "Neighborhood Update" report sent to past clients to maintain database engagement. High-value upsell: a custom relocation portal for HR departments or corporate relocation firms that embeds neighborhood intelligence for employees moving to a new city.

---

## SKILL-046: AI Seller Net Sheet Calculator

**Category**: Widget/Tool / Analytics
**Applies To**: Residential Real Estate — listing agents, sellers, transaction coordinators
**Deployment Platform**: GHL + Custom calculation widget + Claude narrative layer
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,000

### What It Does
Calculates a seller's estimated net proceeds from a home sale in real time, accounting for agent commissions, buyer concessions, title and escrow fees, transfer taxes, prorated property taxes, HOA transfer fees, outstanding mortgage payoff, and estimated repair credits. Replaces the error-prone Excel spreadsheet most agents use and delivers a professional, branded "Seller Net Sheet" PDF on demand — a critical document used in listing presentations to set accurate financial expectations.

### Core Capabilities
- Calculate net proceeds with full closing cost itemization
- Support multiple scenario modeling: full price, 3% below ask, offer with buyer concessions side-by-side
- Include state/county-specific transfer tax rates (database of all 50 states + major counties)
- Calculate prorated property tax credit/debit based on closing date
- Factor in HOA transfer fee and any outstanding HOA assessments
- Apply estimated repair credit scenarios (seller pays $X vs. price reduction)
- Include estimated mortgage payoff (user-inputs current balance + daily interest rate)
- Generate branded PDF Net Sheet with agent contact info and disclaimer language

### Data Inputs Required
- Sale price (or asking price for estimate)
- Property location (state/county for tax rates)
- Listing agent commission rate
- Buyer agent commission rate (or buyer concession % if MLS compensation decoupled)
- Estimated closing date (for proration calculations)
- Current mortgage balance and approximate interest rate
- Known HOA fees and transfer costs
- Any pre-agreed seller credits or repair allowances

### Integration Points
- GHL CRM (auto-generate net sheet from opportunity record, attach to seller contact)
- DocuSign / Dotloop (attach to listing agreement package)
- Mortgage payoff estimator APIs (optional live connection vs. manual entry)
- State/county tax rate database (updated quarterly)
- Email/SMS delivery via GHL automation

### Sample Prompt/Persona
> "You are a real estate financial advisor helping a seller understand exactly what they will walk away with after closing. Be precise — show every line item. Use the seller's specific property location to apply the correct transfer taxes and proration rules. Always run three scenarios: full asking price, 3% below asking, and asking price with $10,000 buyer credit. Explain each major deduction in one plain-English sentence so the seller understands why it exists. End with a clear 'Your estimated check at closing' for each scenario."

### Customization Variables
- State/county transfer tax and recording fee schedule
- Default commission rate structure per brokerage
- Buyer agent compensation scenarios (pre/post NAR settlement options)
- Branding (logo, colors, agent name and license number)
- Disclaimer language per state licensing requirements
- Scenario presets (full price / at asking / with concessions)

### Stickiness Factor
Listing agents use this in every seller presentation — it becomes the financial anchor of the listing appointment. Sellers who receive it come to expect it, and agents who provide it close more listings. The state-specific tax logic (especially complex in multi-county markets) represents real setup investment. Once embedded in the listing presentation template, it is not replaced without disrupting a proven pitch flow.

### Upsell Path
Bundle with SKILL-043 (CMA Generator) as a complete "Listing Presentation Package." Upsell to a Buyer Net Sheet Calculator for buyer agents (analogous tool for cash-to-close estimates). Add a mortgage integration that pulls live payoff quotes directly from lender APIs for high-volume brokerages.

---

## SKILL-047: AI Open House Follow-Up Agent

**Category**: Voice Agent / Chat Agent / Workflow Automation
**Applies To**: Residential Real Estate — listing agents, buyer's agents, open house hosts
**Deployment Platform**: GHL + Vapi (optional voice) + Claude (personalization layer)
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,000

### What It Does
Automatically follows up with every open house visitor within 30 minutes of sign-in using personalized outreach via SMS, email, or voice call — referencing the specific property they visited, their stated timeline and buyer criteria (captured at sign-in), and offering relevant comparable properties from the agent's current listings. Converts open house foot traffic into active buyer conversations at 3–5x the rate of manual follow-up.

### Core Capabilities
- Trigger automated follow-up sequence immediately upon sign-in form submission
- Personalize outreach using visitor's name, visit time, stated buyer criteria from sign-in
- Reference the specific property they visited and its key features in every touchpoint
- Include 2–3 comparable properties from agent's active listings based on visitor criteria
- Schedule follow-up sequence: 30-min text → 2-hour email → 24-hour personal text → 3-day check-in
- Voice agent option: outbound call within 2 hours asking for feedback and offering to schedule a showing
- Score visitor engagement (opened email, clicked listing link, replied to text) and route hot leads to agent immediately
- Integrate with showing scheduling (ShowingTime, Calendly) for instant appointment booking

### Data Inputs Required
- Open house sign-in data: name, phone, email, current address/ZIP, timeline, pre-approval status, agent representation
- Property details of the open house (address, price, beds/baths, key features)
- Agent's current active listing inventory for comp suggestions
- Agent's calendar availability for showing scheduling
- GHL contact record (existing buyer or new lead)

### Integration Points
- GHL CRM (create/update contact, enroll in workflow, trigger sequences)
- Open house sign-in apps (Open Home Pro, Spacio, Curb Hero) via Zapier webhook
- ShowingTime / Calendly for showing scheduling links
- Vapi for outbound voice follow-up call option
- MLS IDX for dynamic listing recommendations
- SMS and email delivery via GHL

### Sample Prompt/Persona
> "You are a warm, knowledgeable buyer's concierge following up after someone visited an open house. You remember exactly which property they saw and what they told you about their search. You are helpful, not pushy. Lead with feedback — ask what they liked and didn't like about the property. Then, if they expressed interest in finding alternatives, offer two or three specific properties from the current inventory that match what they described. Your goal in every conversation is to book a showing or a buyer consultation call — but only after you've genuinely helped them first."

### Customization Variables
- Follow-up sequence timing (30 min, 2 hours, 24 hours — adjustable)
- Outreach channel preference (SMS-first vs. email-first vs. voice-first)
- Message tone per agent brand (casual vs. professional)
- Comp selection logic (price range, beds/baths, proximity to open house)
- Hot lead threshold (engagement score that triggers immediate agent notification)
- Voice agent script and persona per agent

### Stickiness Factor
Open house follow-up is a universal pain point — agents universally do it inconsistently or not at all. Once this system consistently converts 1–2 additional buyers per month from open houses, the ROI is undeniable and the agent is deeply reluctant to stop. The sign-in app webhook + GHL automation creates a seamless operational loop that would take significant effort to disassemble and rebuild.

### Upsell Path
Natural companion to SKILL-045 (Neighborhood Intelligence Agent) — send the neighborhood report for the visited property as part of the follow-up sequence. Upsell to a full Buyer Nurture Campaign package that continues follow-up for 90 days across multiple channels. High-volume listing agents upsell to an Open House Analytics Dashboard showing conversion rates by property, price range, and visitor source.

---

# HEALTHCARE / DENTAL (048-055)

---

## SKILL-048: AI Patient Symptom Triage Bot

**Category**: Chat Agent / Intake
**Applies To**: Healthcare — primary care clinics, urgent care, multi-specialty practices, telehealth platforms
**Deployment Platform**: GHL + Claude + Custom chat widget + Vapi (voice option)
**Complexity**: High
**Monthly Value to Client**: $1,200 - $3,500

### What It Does
Guides patients through a structured symptom assessment conversation, evaluates urgency on a 1–5 scale (1=routine, 5=call 911 immediately), and routes them to the appropriate care pathway: ER, urgent care, same-day appointment, next available appointment, or self-care instructions. Reduces front desk call volume by 30–50% for non-emergency triage inquiries while ensuring patients with serious symptoms receive immediate escalation.

### Core Capabilities
- Conduct structured symptom intake using validated triage logic (adapted from Manchester Triage System)
- Assess urgency on 1–5 scale with documented reasoning for each determination
- Route Level 4–5 patients to 911 call instruction or ER guidance immediately, bypassing queue
- Route Level 3 patients to same-day scheduling or on-call nurse callback
- Route Level 1–2 patients to self-care guidance plus next-available appointment scheduling
- Collect patient demographics, insurance, and chief complaint for pre-registration
- Log all triage interactions with timestamp and urgency score in EHR or GHL
- Send post-triage confirmation to patient (appointment details or care instructions via SMS/email)
- Escalation flag: if AI is uncertain, route immediately to live clinical staff

### Data Inputs Required
- Patient name, date of birth, contact information
- Chief complaint (free-text symptom description)
- Symptom duration, severity (1–10 self-report), associated symptoms
- Medical history flags (chronic conditions, current medications)
- Insurance information (for routing and eligibility pre-check)
- Practice schedule and available appointment slots (integration required)

### Integration Points
- EHR systems: Epic, Athenahealth, eClinicalWorks, DrChrono (via HL7/FHIR API)
- GHL CRM (patient contact record creation and follow-up sequences)
- Scheduling platforms: Kareo, Zocdoc, Acuity Scheduling
- Practice's nurse/on-call phone line for Level 3 escalation
- SMS/email delivery platforms for patient confirmations
- Telehealth platforms (Doxy.me, Zoom for Healthcare) for virtual urgent slots

### Sample Prompt/Persona
> "You are a clinical triage assistant for [Practice Name]. You help patients determine the right level of care for their symptoms. You are calm, warm, and efficient. You never diagnose — you assess urgency and route. Ask one question at a time. Start with the chief complaint, then assess severity, duration, and red-flag symptoms. If you detect any of the following red flags, immediately instruct the patient to call 911 or go to the nearest ER: chest pain with shortness of breath, signs of stroke (FAST acronym), severe allergic reaction, uncontrolled bleeding, altered consciousness. Document everything and never leave a patient without a clear next step."

### Customization Variables
- Practice type and specialty (affects triage logic significantly)
- Red flag symptom list per specialty
- Appointment slot availability feed per location
- Escalation pathway (on-call nurse number, telehealth slot, partner ER)
- EHR integration target and field mapping
- Triage urgency scale labels per practice preference
- Disclaimer and scope-of-practice language per state

### Stickiness Factor
Once live, this bot handles after-hours triage inquiries that previously went to voicemail and never converted. Practices that use it for 60+ days can demonstrate in analytics exactly how many patients were routed to appropriate care vs. lost. The EHR integration — especially FHIR-based connections to Epic or Athenahealth — represents months of setup and compliance work that no practice will redo for a competitor.

### Upsell Path
Natural companion to SKILL-049 (Insurance Verification Agent) to create a complete patient intake pipeline. Upsell to a full after-hours virtual care package combining triage + telehealth scheduling. Multi-location practices upsell to a unified triage dashboard with site-level routing logic.

---

## SKILL-049: AI Insurance Verification Agent

**Category**: Workflow Automation / Operations
**Applies To**: Healthcare — dental practices, medical clinics, specialty practices, behavioral health
**Deployment Platform**: Custom (insurance API integrations) + GHL + Zapier/Make
**Complexity**: High
**Monthly Value to Client**: $1,500 - $4,000

### What It Does
Automatically verifies patient insurance eligibility, active coverage status, in-network/out-of-network determination, deductible amounts, deductible amounts met, copay and coinsurance percentages, and remaining benefit maximums — all before the patient arrives for their appointment. Eliminates 2–4 hours of daily manual verification calls that burden front desk staff and prevents the revenue leakage caused by treating unverified patients.

### Core Capabilities
- Batch-verify all next-day appointments overnight (results ready at 7 AM)
- Check eligibility across 900+ US insurance payers via real-time EDI 270/271 transactions
- Extract and display: deductible (individual/family), deductible met, out-of-pocket max, copay, coinsurance, coverage percentages by procedure type
- Flag terminated coverage, expired coverage, or coordination of benefits requirements
- Identify secondary insurance and verify coordination of benefits order
- Generate patient financial responsibility estimate per appointment type
- Send patient pre-visit financial summary via text/email (optional)
- Update PMS/EHR with verified benefits data automatically

### Data Inputs Required
- Patient demographics: name, DOB, member ID, group number
- Insurance payer name and payer ID
- Appointment type / procedure code (for benefit-specific verification)
- Practice's NPI number(s)
- Appointment date and treating provider NPI
- Practice management system access for data write-back

### Integration Points
- Insurance clearinghouses: Availity, Change Healthcare (Optum), Waystar, Office Ally
- PMS/EHR systems: Dentrix, Eaglesoft, Open Dental (dental); Athenahealth, eClinicalWorks (medical)
- GHL CRM (update patient financial record, trigger pre-visit communication)
- Patient portal for financial estimate delivery
- Billing platforms: Kareo Billing, Biller and Med

### Sample Prompt/Persona
> "You are an expert insurance verification specialist. Your job is to pull complete benefits information for each patient appointment and translate it into clear, actionable financial information for the front desk team. For every appointment, answer: Is the patient active? Are we in-network? What does the patient owe at today's visit? Flag any coverage issues immediately. Present results in a clean daily verification report formatted for morning huddle review. If verification fails or returns incomplete data, escalate immediately for manual follow-up before the patient arrives."

### Customization Variables
- Clearinghouse connection (Availity, Change Healthcare, or other)
- PMS/EHR target and field mapping per system
- Verification run time (nightly batch vs. 72-hour advance vs. real-time at scheduling)
- Payer list configuration (which payers require portal vs. EDI vs. phone)
- Patient-facing financial summary template and delivery method
- Staff notification format for flagged/failed verifications

### Stickiness Factor
Manual insurance verification is the most universally despised front desk task in healthcare. Once automated, practices immediately recapture 10–15 staff-hours per week. The clearinghouse integrations and PMS data mappings represent weeks of technical setup and testing. Revenue cycle teams at multi-location groups build their entire pre-authorization workflow around this system, making it foundational infrastructure.

### Upsell Path
Pair with SKILL-050 (Treatment Cost Estimator) for a complete financial transparency stack. Upsell to automated prior authorization submission for high-frequency procedure types. Multi-location practices upsell to a revenue cycle analytics dashboard showing verification failure rates, coverage lapse trends, and collection improvement metrics.

---

## SKILL-050: AI Treatment Cost Estimator Widget

**Category**: Widget/Tool
**Applies To**: Healthcare — dental practices, elective surgery centers, specialty medical, vision, chiro
**Deployment Platform**: Custom embeddable widget + insurance benefits API + Claude
**Complexity**: Medium
**Monthly Value to Client**: $600 - $1,800

### What It Does
Embeds on a practice's website or patient portal and allows prospective or established patients to get a real-time estimate of their out-of-pocket cost for specific treatments BEFORE committing to an appointment. Patients input their insurance information (or it's pulled from their record), select the procedure type, and receive an itemized cost estimate. Dramatically reduces "how much will this cost me?" anxiety calls and increases case acceptance by presenting financial clarity upfront.

### Core Capabilities
- Display estimated patient responsibility based on live or stored insurance benefits data
- Support 50+ common procedure types per specialty (dental: crowns, implants, Invisalign; medical: colonoscopy, MRI, physical therapy)
- Break down estimate by: insurance pays, patient deductible applied, patient coinsurance, total patient responsibility
- Present financing options (CareCredit, Sunbit, in-house payment plan) with monthly payment calculation
- Collect patient contact information for follow-up appointment scheduling
- Update PMS/EHR with estimate provided and patient inquiry record
- Provide disclaimer language and "exact quote at exam" messaging for compliance
- Track estimate-to-appointment conversion rate in practice analytics dashboard

### Data Inputs Required
- Insurance carrier, plan name, member ID, group number (or pulled from patient record)
- Selected procedure type
- Practice fee schedule (UCR fees per CDT/CPT code)
- Insurance contracted rate (in-network fee schedule per payer)
- Current benefits data: deductible met, remaining maximum (from SKILL-049 or manual entry)
- Financing partner credentials (CareCredit, Sunbit APIs)

### Integration Points
- Practice website (embeddable JavaScript widget)
- Patient portal (Phreesia, Solutionreach, Weave)
- PMS: Dentrix, Eaglesoft, Open Dental (dental); Athenahealth, Kareo (medical)
- Financing platforms: CareCredit API, Sunbit API, in-house payment plan calculator
- GHL CRM (capture inquiry, trigger follow-up sequence)
- Scheduling platform for appointment booking after estimate review

### Sample Prompt/Persona
> "You are a patient financial advisor. Your job is to give patients an honest, clear picture of what their treatment will likely cost before they decide to schedule. Be transparent about what is estimated vs. guaranteed — always include the disclaimer that exact amounts are confirmed at the time of service. Lead with the bottom line (your estimated cost today: $X), then show the breakdown. Always present financing options alongside the full-pay amount. Never let cost be the reason a patient doesn't move forward — always offer the next step."

### Customization Variables
- Procedure menu per specialty and practice offerings
- Fee schedule upload per practice (UCR fees)
- In-network payer list and contracted rate schedule
- Financing partner selection and integration credentials
- Disclaimer language per state and specialty
- Widget color scheme, logo, and brand voice
- Conversion tracking pixel for practice website analytics

### Stickiness Factor
Practices that publish this widget see measurable increases in online appointment requests from high-intent patients who have already self-qualified financially. Case acceptance rates improve because financial ambiguity — the #1 reason patients delay treatment — is removed. The fee schedule + contracted rate configuration is deeply customized per practice and takes significant time to rebuild elsewhere.

### Upsell Path
Bundle with SKILL-049 (Insurance Verification) for a complete patient financial transparency system. Upsell to a Treatment Plan Financing Coordinator that automatically presents financing at case acceptance and handles application processing. High-value upsell for DSO groups: a multi-location cost estimator with centralized fee schedule management.

---

## SKILL-051: AI Patient Recall Agent

**Category**: Workflow Automation / Voice Agent
**Applies To**: Dental practices, primary care, specialty medical, eye care, chiro/PT
**Deployment Platform**: GHL + Vapi + PMS integration + Make/Zapier
**Complexity**: Medium
**Monthly Value to Client**: $800 - $2,500

### What It Does
Automatically identifies patients who are overdue for their next appointment (based on recommended recall intervals in the PMS), and executes a multi-channel outreach campaign via text, email, and AI voice call to re-activate them. For a busy dental practice, recall accounts for 70%+ of revenue — yet most practices lose 20–40% of their active patient base annually to "passive attrition" because follow-up is inconsistent. This agent runs continuously, never missing an overdue patient.

### Core Capabilities
- Pull overdue patient list daily from PMS based on last visit date + recommended recall interval
- Segment by recall type: 6-month cleaning, annual exam, hygiene reactivation, specialty recall
- Execute multi-channel sequence: SMS day 1 → email day 3 → AI voice call day 7 → final SMS day 14
- AI voice call (Vapi): personalized outbound call mentioning patient by name, last visit, specific recall need
- Allow patient to book directly via SMS link, email link, or voice conversation
- Auto-update PMS appointment status when booking is confirmed
- Track sequence performance: open rates, booking rates, response rates per channel
- Pause sequence automatically when patient books or requests removal

### Data Inputs Required
- PMS patient database with last visit date, recall date, contact preferences
- Recall interval rules per procedure type (6-month, 12-month, 3-month perio, etc.)
- Patient contact information (phone, email, text opt-in status)
- Provider schedule and available appointment slots
- Practice branding (name, phone, address for messages)
- HIPAA Business Associate Agreement (BAA) with all platforms used

### Integration Points
- PMS: Dentrix, Eaglesoft, Open Dental, Carestream, Curve Dental (dental); Athenahealth, Kareo (medical)
- GHL CRM (sequence management, tracking, reporting)
- Vapi (outbound AI voice calls with appointment booking capability)
- Scheduling platforms: Zocdoc, Acuity, NexHealth for direct booking links
- SMS/email delivery compliant with TCPA and HIPAA
- Unsubscribe management for compliance

### Sample Prompt/Persona
> "You are a caring patient care coordinator calling on behalf of [Practice Name]. You are warm, personal, and genuinely concerned about the patient's health — not just filling chairs. When you call, use the patient's first name, mention that it's been about [X months] since their last visit, and remind them that [recall type — e.g., their 6-month cleaning] is due. Never use high-pressure language. Make it easy: offer to book right now on the call or send a text link for them to book at their convenience. Always ask if there's anything that prevented them from coming in — and listen."

### Customization Variables
- Recall interval rules per procedure type and patient risk category
- Multi-channel sequence timing and channel order
- Voice agent script per recall type (cleaning vs. exam vs. specialty)
- PMS integration target and appointment type mapping
- Booking link destination (online scheduler URL)
- Compliance settings: TCPA call windows, opt-out management, HIPAA BAA status

### Stickiness Factor
For dental practices especially, recall revenue is existential. A practice with 1,500 active patients overdue at any given time represents $150,000+ in potential recall revenue. Once this system is running, practices measure its impact directly in their monthly production numbers. The PMS integration — particularly the bidirectional data sync with appointment status — takes weeks to configure and validate, creating strong switching inertia.

### Upsell Path
Bundle with SKILL-052 (Post-Procedure Follow-Up Agent) for a complete patient lifecycle communication system. Upsell to a full Patient Reactivation Campaign that targets patients who haven't visited in 18–36 months. Multi-location DSO groups upsell to a centralized recall analytics dashboard across all locations.

---

## SKILL-052: AI Post-Procedure Follow-Up Agent

**Category**: Workflow Automation / Chat Agent / Voice Agent
**Applies To**: Dental practices, surgical centers, specialty medical, urgent care
**Deployment Platform**: GHL + Vapi + Claude + Make/Zapier
**Complexity**: Medium
**Monthly Value to Client**: $600 - $1,500

### What It Does
Automatically contacts patients 24–48 hours after procedures to assess their recovery, monitor for complications or adverse reactions, and provide appropriate guidance. Flags patients reporting concerning symptoms for immediate clinical staff callback. For practices performing extractions, implants, surgeries, or invasive treatments, this agent fulfills post-operative monitoring obligations, improves patient satisfaction scores, and reduces after-hours emergency calls from anxious patients who simply need reassurance.

### Core Capabilities
- Trigger personalized follow-up at configurable intervals post-procedure (24h, 48h, 72h, 7 days)
- Ask condition-specific recovery questions (pain level, swelling, bleeding, medication compliance)
- Detect red-flag responses indicating potential complications and escalate to clinical staff immediately
- Provide reassurance and standard post-op care reminders for normal recovery reports
- Collect patient satisfaction rating (NPS/CSAT) and treatment experience feedback
- Offer to schedule follow-up appointment or post-op exam if needed
- Log all responses in PMS/EHR patient record with timestamp
- Generate daily exception report for clinical team: patients reporting elevated concern scores

### Data Inputs Required
- Procedure type and date (from PMS appointment record)
- Patient contact information and preferred contact method
- Procedure-specific post-op care protocol (provided by clinical staff)
- Red-flag symptom criteria per procedure type
- On-call clinician contact for escalation
- HIPAA BAA with all platforms in the workflow

### Integration Points
- PMS: Dentrix, Eaglesoft, Open Dental, Athenahealth (procedure completion trigger)
- GHL CRM (sequence management, response logging)
- Vapi (voice follow-up option for elderly patients or those without text access)
- Clinical team notification (SMS/pager/Slack alert for escalation cases)
- Review platform integration (Google, Healthgrades) for satisfied-patient review requests
- EHR documentation (write-back of follow-up note to patient chart)

### Sample Prompt/Persona
> "You are a caring post-procedure care coordinator from [Practice Name]. You're calling to check in on [Patient Name] following their [Procedure Type] on [Date]. Your tone is warm, unhurried, and clinically competent. Ask specifically about their pain level (1–10), swelling, any bleeding, and whether they have been able to take their medications as prescribed. If they report pain above 7/10, persistent bleeding, fever, or difficulty breathing, immediately advise them to call the practice emergency line and flag their record for urgent clinical callback. If recovery is normal, provide reassurance, remind them of their next steps, and ask if they'd like to share their experience."

### Customization Variables
- Follow-up timing intervals per procedure type
- Procedure-specific question scripts (extraction vs. implant vs. root canal vs. surgical)
- Red-flag threshold calibration per clinical team's standards
- Escalation routing (on-call line, clinical inbox, text alert)
- Review request timing and platform (Google, Healthgrades, Zocdoc)
- PMS documentation template for write-back notes

### Stickiness Factor
Post-procedure follow-up directly reduces malpractice risk by creating a documented record that the practice monitored patient recovery. Once clinical staff see the daily exception report and realize it surfaces complications earlier than before, they trust the system as a clinical safety net. HIPAA-compliant integrations into EHR documentation are particularly sticky because they become part of the legal medical record workflow.

### Upsell Path
Combine with SKILL-051 (Recall Agent) to create a complete patient lifecycle communication system. Upsell to a comprehensive patient experience management system including satisfaction surveys, review generation, and complaint resolution tracking. Practices with high surgical volume upsell to a clinical outcomes tracking module.

---

## SKILL-053: AI Dental Treatment Plan Presenter

**Category**: Widget/Tool / Analytics
**Applies To**: Dental practices — general dentistry, cosmetic, implants, orthodontics
**Deployment Platform**: Custom web app + Claude + GHL + Financing API integrations
**Complexity**: High
**Monthly Value to Client**: $1,000 - $3,000

### What It Does
Transforms clinical treatment plan data from the PMS into a patient-friendly visual presentation showing recommended treatments, their clinical rationale (with X-ray and photo references), total cost, insurance coverage breakdown, and multiple financing options — all in a clean, branded interface the patient can review chairside or at home before accepting. Increases case acceptance rates by 20–35% by removing the three barriers to acceptance: not understanding the need, not understanding the cost, and not knowing how to afford it.

### Core Capabilities
- Import treatment plan directly from PMS (CDT codes → plain-language descriptions)
- Pair each treatment item with clinical photos/X-rays from the imaging system
- Explain why each treatment is needed in plain language (not dental jargon)
- Show total treatment cost with priority phasing (Phase 1 urgent / Phase 2 important / Phase 3 elective)
- Display real-time insurance benefit application per treatment item (from SKILL-049 data)
- Present side-by-side financing options: full pay, CareCredit 12-month, Sunbit 24-month, in-house plan
- Allow patient to accept, defer, or ask questions about each item digitally
- Generate signed treatment acceptance form (electronically) and save to PMS
- Send take-home version via email/text link for spouse/partner consultation

### Data Inputs Required
- Treatment plan data from PMS (CDT codes, quantities, fees)
- Clinical photos and X-rays from imaging system
- Patient's insurance benefits data (from SKILL-049)
- Practice fee schedule and any phasing recommendations
- Financing partner credentials (CareCredit, Sunbit)
- Patient demographics and contact for take-home link delivery

### Integration Points
- PMS: Dentrix, Eaglesoft, Open Dental, Curve Dental (treatment plan import)
- Dental imaging: DEXIS, Carestream, Sirona (X-ray/photo import)
- Financing: CareCredit API, Sunbit API, in-house payment plan calculator
- GHL CRM (treatment plan status tracking, follow-up for pending accepted plans)
- Electronic signature: DocuSign or native signature capture
- Patient portal for take-home access

### Sample Prompt/Persona
> "You are a patient treatment educator. When presenting a treatment plan, lead with health outcomes — not dollars. Explain each recommended treatment in terms the patient can relate to: 'This tooth has decay that has reached the nerve, which is why you've been having sensitivity. Without treatment, the infection can spread.' Then address cost directly — patients respect transparency. Show the insurance portion clearly. Always present payment options as solutions, not sales — the goal is that no patient ever says no to needed care because of finances."

### Customization Variables
- Clinical language presets per specialty (general vs. cosmetic vs. implant vs. ortho)
- Phasing logic per clinical philosophy (aggressive vs. conservative treatment phasing)
- Financing partner selection and monthly payment calculation parameters
- Brand styling (practice logo, colors, font, imagery)
- Informed consent language per state and procedure type
- Take-home link expiration window (24h, 48h, 72h)

### Stickiness Factor
Treatment plan presentation is directly tied to practice revenue. DSOs that deploy this system across locations can measure case acceptance rate improvements precisely. Dentists who present plans this way in their evening follow-up communications rarely go back to manual email attachments because they can see which patients opened the plan, how long they spent on each item, and which financing option they selected — behavioral data that drives a fundamentally different conversation when the patient calls back.

### Upsell Path
Bundle with SKILL-050 (Cost Estimator Widget) and SKILL-049 (Insurance Verification) for a complete financial clarity suite. Upsell to a treatment plan follow-up sequence that automatically contacts patients with deferred treatment 30/60/90 days later. Enterprise upsell for DSO groups: a multi-location case acceptance analytics dashboard.

---

## SKILL-054: AI Mental Health Screening Intake

**Category**: Intake / Diagnostic
**Applies To**: Behavioral health practices, psychiatry, primary care, employee assistance programs
**Deployment Platform**: Claude + GHL + HIPAA-compliant form platform + Custom intake portal
**Complexity**: High
**Monthly Value to Client**: $800 - $2,500

### What It Does
Administers validated mental health screening tools (PHQ-9 for depression, GAD-7 for anxiety, PCL-5 for PTSD, AUDIT for alcohol use, MDQ for bipolar, CAGE for substance use) via a conversational interface or structured form before the patient's first appointment. AI scores results, flags clinical thresholds, generates a structured intake summary for the provider, and routes urgent presentations (active suicidal ideation, severe PHQ-9) to immediate crisis protocols. Saves providers 20–30 minutes of intake time per new patient.

### Core Capabilities
- Administer PHQ-9, GAD-7, PCL-5, AUDIT, CAGE, MDQ per provider-specified protocol
- Score all instruments automatically with clinical interpretation (mild/moderate/severe thresholds)
- Detect safety-critical responses (PHQ-9 Question 9, suicidal ideation) and trigger crisis protocol immediately
- Generate structured intake summary in provider-ready format (SOAP-compatible)
- Collect chief complaint, psychiatric history, medication history, family history, social history
- Allow patient to complete on their own device before arrival (text/email link)
- Integrate completed intake into EHR chart as structured data
- Generate provider pre-session briefing: key scores, risk flags, recommended clinical focus areas

### Data Inputs Required
- Patient name, DOB, contact information
- Insurance/payment information
- Referral source and presenting concern
- Screening instrument selection (per provider workflow)
- HIPAA authorization and consent (captured digitally)
- EHR chart destination for intake data

### Integration Points
- EHR: TherapyNotes, SimplePractice, Kareo Behavioral Health, Epic Behavioral (structured note import)
- Crisis escalation: National Suicide Prevention Lifeline integration, local crisis team contact
- GHL CRM (new patient record creation, intake completion status)
- Patient portal (Phreesia, Klara, or custom) for pre-visit completion
- Provider scheduling platform for intake-linked appointment confirmation
- Telehealth platform (if intake precedes virtual appointment)

### Sample Prompt/Persona
> "You are a compassionate new patient intake coordinator for [Practice Name]. Your role is to help new patients complete their intake screening before their first appointment. Administer each screening instrument conversationally — explain why you're asking each question in plain language. Never rush. If a patient discloses active thoughts of self-harm, immediately pause all other intake, provide the 988 Suicide and Crisis Lifeline number, and alert the clinical team immediately. Your tone is warm, non-judgmental, and professional. Always affirm that the patient made the right decision by seeking help."

### Customization Variables
- Screening instrument battery per provider specialty and clinical focus
- Crisis protocol: specific escalation steps, contact numbers, safe messaging guidelines compliance
- Intake form sections per practice (what clinical history is required)
- EHR field mapping per target system
- Provider pre-session briefing format preferences
- Consent and authorization language per state and payer requirements

### Stickiness Factor
Mental health practices that digitize intake reduce no-show rates (patients who complete intake are more committed), decrease session waste on basic history-taking, and build a structured clinical dataset from day one. The validated instrument scoring and EHR integration creates a clinical documentation workflow that providers rely on for treatment planning — removing it would disrupt clinical operations, not just administrative efficiency.

### Upsell Path
Pair with SKILL-055 (Chronic Disease Management Agent) for practices managing patients with co-occurring conditions. Upsell to a Measurement-Based Care Dashboard that tracks patient PHQ-9/GAD-7 scores over time to demonstrate treatment efficacy for insurance credentialing and value-based care contracts. Group/EAP practices upsell to a centralized outcomes reporting module.

---

## SKILL-055: AI Chronic Disease Management Agent

**Category**: Chat Agent / Workflow Automation
**Applies To**: Primary care, endocrinology, cardiology, nephrology, behavioral health
**Deployment Platform**: GHL + Claude + Vapi (check-in calls) + EHR integration
**Complexity**: High
**Monthly Value to Client**: $1,500 - $4,500

### What It Does
Conducts regular automated check-ins with patients managing chronic conditions (Type 1/2 diabetes, hypertension, CHF, COPD, CKD, depression) between scheduled appointments. Collects biometric readings (blood glucose, blood pressure, weight, peak flow), symptom reports, and medication adherence data, flags values outside clinical thresholds for immediate provider review, and feeds structured data into the EHR. Extends the clinical team's reach into the patient's daily life, reduces avoidable hospitalizations, and supports value-based care quality metrics.

### Core Capabilities
- Schedule condition-specific check-in cadence per care plan (daily, 3x/week, weekly, biweekly)
- Collect condition-specific data points: blood glucose (diabetes), BP and pulse (hypertension), weight (CHF), mood/sleep/medication (behavioral health)
- Apply clinical alert thresholds and flag out-of-range values for same-day provider review
- Provide real-time behavioral coaching: medication reminders, dietary nudges, activity prompts
- Conduct medication adherence check and capture barriers to adherence
- Summarize check-in data into structured clinical note for EHR documentation
- Generate weekly trend report for provider (glucose trends, BP patterns, weight trajectory)
- Identify patients with worsening trends before crisis and trigger care team outreach
- Support remote patient monitoring (RPM) billing codes (CPT 99457, 99458) with compliant documentation

### Data Inputs Required
- Patient chronic condition diagnoses and active care plan
- Biometric thresholds (clinical alert ranges per patient)
- Current medication list and dosing schedule
- Preferred contact time and method
- Wearable/device data feeds (if patient uses connected glucometer, BP cuff, scale)
- Provider alert preferences (what triggers immediate notification vs. weekly review)

### Integration Points
- EHR: Epic, Athenahealth, eClinicalWorks (structured data import and RPM documentation)
- Connected devices: iHealth, Withings, Omron (glucometers, BP cuffs, scales via Bluetooth/API)
- GHL CRM (patient engagement tracking, care gap identification)
- Vapi (voice check-in calls for elderly patients)
- Provider notification: secure messaging platforms (Klara, OhMD)
- Value-based care registries and quality measure reporting

### Sample Prompt/Persona
> "You are a dedicated care coordinator for patients with chronic health conditions. You check in regularly — not to interrogate, but to support. You are genuinely curious about how the patient is doing, not just collecting numbers. When a patient's reading is out of range, stay calm — acknowledge the number, ask if they know what might have caused it, provide a brief coaching response, and tell them clearly that you're sending this to their care team right now. When values are in range, celebrate wins. You remember their progress — 'Your blood pressure has been much better this week' builds trust and keeps patients engaged."

### Customization Variables
- Condition-specific check-in protocols per clinical guideline (ADA diabetes standards, JNC hypertension guidelines)
- Alert threshold configuration per patient (individualized by provider)
- Check-in frequency and timing per care plan
- Connected device integrations per patient's devices
- RPM billing documentation settings (CPT code compliance per payer)
- EHR field mapping and note template per target system
- Language/literacy level adaptation per patient population

### Stickiness Factor
Practices using this for RPM billing generate $150–$300 per patient per month in additional revenue with minimal incremental cost. Once the practice's billing team is running RPM claims through this workflow, it becomes a revenue stream — not just a tool. The EHR integration and compliant RPM documentation structure represent significant regulatory and technical investment. Value-based care contract performance metrics (measured quarterly) depend on this data, creating institutional-level dependency.

### Upsell Path
Bundle with SKILL-052 (Post-Procedure Follow-Up) and SKILL-054 (Mental Health Screening) for a complete patient engagement platform. Upsell to a Population Health Analytics module that identifies care gaps across the entire chronic disease panel. Enterprise upsell: an ACO or health system-level platform with multi-provider RPM management and value-based care performance dashboards.

---

# LEGAL (056-061)

---

## SKILL-056: AI Case Qualification Bot

**Category**: Intake / Diagnostic
**Applies To**: Personal injury, mass tort, workers' comp, immigration, criminal defense, family law
**Deployment Platform**: GHL + Claude + Vapi (voice intake option) + Custom intake form
**Complexity**: High
**Monthly Value to Client**: $1,500 - $5,000

### What It Does
Conducts a comprehensive, structured intake conversation with potential clients 24/7, scoring case viability against the firm's specific practice area criteria and intake parameters. The bot distinguishes between viable cases and non-qualifying inquiries within minutes, routes A/B/C-grade leads accordingly, and delivers a complete case intake summary to the attorney before they ever speak to the prospect. Eliminates the 60–90% of intake calls that don't convert into cases while ensuring no qualifying case falls through the cracks after hours.

### Core Capabilities
- Conduct complete intake conversation via chat, SMS, or AI voice call at any hour
- Score case viability on A/B/C scale per firm-defined qualification criteria per practice area
- Apply statute of limitations check (flag cases nearing or past deadline for immediate attorney review)
- Capture complete incident facts: date, location, parties involved, injuries/damages, insurance information
- Identify conflict of interest flags (opposing party against existing clients)
- Route A-grade cases: immediate attorney text alert + calendar booking for consultation
- Route B-grade cases: intake coordinator review queue + 30-minute follow-up sequence
- Route C-grade cases: professional declination message + referral to appropriate firm type
- Generate complete intake summary memo for reviewing attorney

### Data Inputs Required
- Firm's qualification criteria per practice area (provided by lead attorney)
- Conflict-of-interest check database (existing client list)
- Attorney availability calendar (for A-grade direct booking)
- State-specific statute of limitations rules per case type
- Intake form fields required by each practice area

### Integration Points
- GHL CRM (lead record creation, pipeline staging, sequence enrollment)
- Clio, MyCase, Filevine, Smokeball (case management — matter creation for qualified cases)
- Vapi (voice intake for callers who don't complete web form)
- Calendar (Calendly, Acuity) for instant consultation booking
- Conflict check database integration
- E-signature platforms for fee agreement delivery to A-grade leads

### Sample Prompt/Persona
> "You are a professional legal intake specialist for [Firm Name]. You are empathetic, organized, and thorough. Your job is to gather complete facts about a potential client's situation and evaluate whether our firm can help them. Never give legal advice — your role is to gather information and connect the right cases with our attorneys. When someone describes a traumatic event, acknowledge it first before moving to questions. Be efficient but never rushed — people calling a law firm are often in crisis. Every case that might qualify must receive our full attention. Cases that don't qualify must be declined with dignity and a helpful referral."

### Customization Variables
- Practice area qualification logic per firm
- Minimum damages threshold per practice area
- SOL warning trigger (cases within 30/60/90 days of deadline get immediate escalation)
- Geographic limitations (state licensing, multi-state practice)
- A/B/C routing logic and follow-up sequences per grade
- Conflict check scope
- Declination message language and referral network

### Stickiness Factor
Law firms that run this 24/7 capture leads from after-hours organic search and referral traffic that previously went to competitors. Once a firm sees intake data showing that 35% of their qualified leads come in outside business hours, removing the system becomes existential. The qualification logic — calibrated over months to match each attorney's case selection instincts — cannot be replicated by a generic intake form.

### Upsell Path
Bundle with SKILL-060 (Deadline Tracker) and SKILL-061 (Demand Letter Generator) for a complete case lifecycle intake-to-demand package. Upsell to a comprehensive lead analytics dashboard showing lead volume by source, qualification rates, and conversion to signed clients. High-volume PI firms upsell to a mass-tort campaign intake system.

---

## SKILL-057: AI Contract Review Agent

**Category**: Analytics / Diagnostic
**Applies To**: Business law, real estate law, employment law, commercial transactions, in-house legal teams
**Deployment Platform**: Claude (document analysis) + GHL + Custom secure upload portal
**Complexity**: High
**Monthly Value to Client**: $1,500 - $6,000

### What It Does
Analyzes uploaded contracts and legal agreements to identify risky clauses, missing standard provisions, non-market terms, ambiguous language, and jurisdiction-specific compliance issues. Delivers a structured risk report categorizing issues by severity (high/medium/low), with specific redline suggestions for each flagged clause. Enables small-to-mid-size firms to efficiently conduct preliminary contract review at scale — or allows in-house legal teams to triage a high volume of incoming contracts before escalating to outside counsel.

### Core Capabilities
- Analyze contracts up to 100+ pages across common types: NDAs, MSAs, employment agreements, commercial leases, asset purchase agreements, licensing agreements
- Flag high-risk clauses: unlimited liability, broad indemnification, non-compete overreach, unilateral amendment rights, one-sided IP assignment
- Identify missing standard provisions: limitation of liability, dispute resolution, governing law, IP ownership, termination for convenience
- Check governing law and jurisdiction against client's operating state for conflict flags
- Highlight non-standard payment terms, auto-renewal traps, and termination penalties
- Generate issue-specific redline language suggestions for negotiation
- Produce one-page risk summary for client (plain English + attorney review flags)
- Track contract review history in matter management system

### Data Inputs Required
- Contract document (PDF, DOCX, or plain text)
- Contract type designation (NDA, MSA, lease, employment, etc.)
- Client's role in the agreement
- Client's industry and jurisdiction
- Specific concerns flagged by client (optional)
- Firm's standard position/playbook per contract type (optional but improves output dramatically)

### Integration Points
- Secure document upload portal (SFTP or encrypted client portal)
- Clio, Filevine, MyCase (matter record attachment and billing trigger)
- Microsoft Word / Google Docs (redline output in tracked-changes format)
- GHL CRM (client communication and follow-up)
- E-signature platforms for reviewed/negotiated agreement execution
- Document management: NetDocuments, iManage, Worldox

### Sample Prompt/Persona
> "You are an experienced commercial contracts attorney conducting a preliminary contract review. You read with the client's interests at front of mind. Flag every provision that creates asymmetric risk, unusual obligations, or potential exposure. Be specific — quote the exact language and explain why it's a problem in plain English. Provide a negotiation-ready alternative for every high-risk clause you flag. Organize your output as: (1) Executive Summary with overall risk rating, (2) High Priority Issues, (3) Medium Priority Issues, (4) Low Priority Issues / Minor Notes, (5) Missing Provisions. Never give a clean bill of health — every contract has something worth discussing."

### Customization Variables
- Contract playbook per firm's standard negotiating positions per contract type
- Client industry-specific risk priorities
- Jurisdiction-specific law flags
- Risk tolerance calibration per firm
- Output format (attorney memo vs. client-facing plain English summary)
- Matter billing integration (time entry creation for review)

### Stickiness Factor
Law firms that build a proprietary contract playbook into this system create institutional knowledge that lives in the platform. The more contracts a firm reviews, the better the playbook gets, creating a compounding advantage. In-house legal teams that route all incoming contracts through this system build a searchable contract repository with indexed risk flags, creating an operational dependency that spans the entire business.

### Upsell Path
Bundle with SKILL-059 (Estate Planning Questionnaire) and SKILL-061 (Demand Letter Generator) for a full transactional practice automation package. Upsell to a Contract Negotiation Tracker. Enterprise upsell: an in-house legal operations platform with contract lifecycle management, clause library, and vendor contract risk analytics.

---

## SKILL-058: AI Personal Injury Case Calculator

**Category**: Widget/Tool / Analytics
**Applies To**: Personal injury law firms — auto accidents, slip-and-fall, medical malpractice, premises liability
**Deployment Platform**: Claude + GHL + Custom intake widget (embeddable on firm website)
**Complexity**: Medium
**Monthly Value to Client**: $800 - $2,500

### What It Does
Provides prospective personal injury clients with an estimated settlement value range based on their injury type, medical bills incurred, lost wages, future medical needs, pain and suffering multiplier, and jurisdiction-specific verdict data. Serves as both a lead qualification tool (serious injuries self-identify by high estimated value) and a trust-building mechanism. Embeds on the firm's website to convert organic search traffic into intake appointments.

### Core Capabilities
- Calculate economic damages: medical specials (current and estimated future), lost wages, lost earning capacity
- Apply jurisdiction-specific pain and suffering multiplier ranges (varies 1.5x–5x by state and injury type)
- Adjust for liability percentage (comparative negligence in applicable states)
- Cross-reference injury-specific settlement data from national verdict databases
- Generate estimated settlement range: conservative, likely, and optimistic scenarios
- Capture lead contact information and case facts for attorney follow-up
- Flag cases with estimated value above firm's minimum threshold for immediate priority routing
- Provide caveat-appropriate language ("this is an estimate for informational purposes only")

### Data Inputs Required
- Injury type (fracture, soft tissue, TBI, spinal, wrongful death, etc.)
- Total medical bills to date
- Estimated future medical costs
- Lost wages (weekly income × weeks missed)
- Future lost earning capacity (if applicable)
- Liability percentage estimate
- Jurisdiction (state governs multipliers, caps, and comparative negligence rules)
- Insurance policy limits

### Integration Points
- Firm website (embeddable JavaScript widget)
- GHL CRM (lead capture with case value estimate)
- Clio / Filevine (intake-to-matter pipeline for high-value cases)
- Jury verdict databases (API where available)
- Attorney calendar for immediate consultation booking
- Follow-up email sequence with "your case explained" content

### Sample Prompt/Persona
> "You are a personal injury case analyst. When a potential client provides their injury details and damages, calculate a realistic estimated settlement range using established legal methodology: economic damages + pain and suffering multiplier applied per jurisdiction norms. Always present three scenarios — conservative, likely, and optimistic. Be honest about factors that affect value up or down: liability percentage, the defendant's insurance limits, and injury severity documentation. Never over-promise. Always end with: 'These numbers give you a starting point — an attorney review of your actual medical records and accident documentation will sharpen this picture significantly.'"

### Customization Variables
- Jurisdiction configuration (state-specific multipliers, damage caps, comparative negligence rules)
- Injury type database and corresponding severity/value benchmarks
- Firm's minimum case value threshold for A-grade routing
- Pain and suffering multiplier range per injury category
- Website widget styling and branding
- Disclaimer language per state bar advertising rules

### Stickiness Factor
A firm that embeds this calculator on their website and begins generating qualified leads from it becomes dependent on the conversion data. After 6 months, the firm has empirical data on which injury types convert at the highest rates, which jurisdictions produce the highest-value leads, and what the average case value of their online intake funnel is.

### Upsell Path
Bundle with SKILL-056 (Case Qualification Bot) for a complete intake and case value pipeline. Upsell to a full settlement negotiation support tool that tracks medical record gathering, calculates updated demand amounts as bills come in, and drafts demand letter updates. High-volume PI firms upsell to a case portfolio analytics dashboard.

---

## SKILL-059: AI Estate Planning Questionnaire

**Category**: Intake / Workflow Automation
**Applies To**: Estate planning attorneys, elder law firms, trust and estate practices, financial advisory firms with legal partnerships
**Deployment Platform**: GHL + Claude + Custom intake form + Document automation
**Complexity**: Medium
**Monthly Value to Client**: $600 - $2,000

### What It Does
Replaces the antiquated paper or PDF intake form with an intelligent, conversational questionnaire that adapts based on client responses. Collects complete family structure, asset inventory, beneficiary designations, healthcare and financial power of attorney preferences, and special circumstances (minor children, blended families, business interests, special needs beneficiaries). Delivers a structured attorney brief before the first consultation, cutting meeting time in half.

### Core Capabilities
- Adaptive questionnaire logic: basic will path vs. revocable living trust path vs. advanced estate planning based on asset level and family complexity
- Collect complete family inventory: spouse, children, grandchildren, estranged relatives, prior marriages
- Capture full asset inventory with ownership structure: real property, financial accounts, retirement accounts, life insurance, business interests
- Document beneficiary designation goals and specific bequests
- Collect healthcare directive preferences (DNR, life support, organ donation)
- Gather financial power of attorney scope preferences
- Identify special circumstances: minor children (guardian nominations), special needs beneficiaries, charitable giving goals, family business succession
- Generate attorney pre-meeting brief: family map, asset summary, key planning goals, complexity tier
- Flag common estate planning traps identified in responses

### Data Inputs Required
- Client and spouse full legal names, DOBs, addresses
- Family structure (complete)
- Real property addresses and ownership
- Financial account types and approximate values
- Life insurance policies and current beneficiaries
- Business interests and ownership percentages
- Healthcare and end-of-life preferences
- Stated goals

### Integration Points
- GHL CRM (new client record, intake completion tracking)
- Clio, MyCase (matter creation with intake data)
- Document automation platforms: HotDocs, Lawyaw, Knackly (intake data → draft documents)
- Secure client portal for intake completion
- Attorney calendar for consultation scheduling post-intake
- E-signature for engagement letter and data authorization

### Sample Prompt/Persona
> "You are a thoughtful estate planning intake coordinator for [Firm Name]. Your job is to help clients think through and document their estate planning wishes before they meet with our attorney. Many clients find this process emotional or overwhelming — acknowledge that, and reassure them that there are no wrong answers here. Ask questions in plain English. When a client mentions minor children, probe for guardian nominations carefully — this is often the most important decision they will make today. When a client mentions a business, flag it clearly for the attorney: business succession planning changes everything."

### Customization Variables
- Questionnaire depth per planning tier
- Asset threshold triggers for advanced planning prompts
- State-specific questions (community property states)
- Document automation integration mapping
- Attorney briefing format preferences
- Engagement letter and fee schedule delivery at intake completion

### Stickiness Factor
Estate planning attorneys who use this system cut their average first-meeting time from 90 minutes to 45 minutes. Once document automation is connected (so that will and trust drafts are auto-populated from intake responses), removing this system means rebuilding the entire intake-to-drafting pipeline. Firms that process 20+ estate plans per month have this embedded as infrastructure, not a tool.

### Upsell Path
Bundle with SKILL-057 (Contract Review Agent) for a complete transactional law automation package. Upsell to a document automation system that generates complete draft wills, trusts, POAs, and directives from intake data. High-value upsell for elder law firms: an annual estate plan review system that proactively contacts past clients when life events should trigger a plan update.

---

## SKILL-060: AI Court Deadline Tracker

**Category**: Operations / Workflow Automation
**Applies To**: Litigation firms, criminal defense, family law, civil litigation, appellate practice
**Deployment Platform**: GHL + Make/Zapier + Clio/Filevine integration + Calendar automation
**Complexity**: High
**Monthly Value to Client**: $1,000 - $3,500

### What It Does
Maintains a centralized, automated deadline management system for all active litigation matters — tracking statute of limitations deadlines, court filing deadlines, discovery cutoffs, motion response windows, expert disclosure dates, deposition deadlines, and hearing dates. Sends multi-stage advance warnings (30 days, 14 days, 7 days, 48 hours) to responsible attorneys and staff, logs all deadline-related activity, and creates a daily "critical deadline" morning briefing. Missed deadlines are the #1 cause of legal malpractice claims; this is existential risk management.

### Core Capabilities
- Import matters and deadlines from case management system (Clio, Filevine, MyCase, Smokeball)
- Manually create deadline chains from court scheduling orders (upload order → AI extracts all dates)
- Apply jurisdiction-specific court rules for deadline calculation
- Calculate weekends/holidays correctly per jurisdiction's court calendar
- Send escalating advance warnings: 30-day, 14-day, 7-day, 48-hour, and day-of alerts
- Route alerts to responsible attorney, supervising partner, and paralegal simultaneously
- Generate daily morning briefing: all deadlines in the next 30 days across all active matters
- Log confirmation of acknowledgment for each alert
- Flag unclaimed/unacknowledged alerts for managing partner review
- Integrate with attorney calendars (Google Calendar, Outlook) for direct deadline blocking

### Data Inputs Required
- Active matter list from case management system
- Court scheduling orders (PDF upload for AI extraction)
- Jurisdiction per matter
- Responsible attorney and staff assignments per matter
- State/federal court calendars for holiday exclusions
- Attorney/staff notification preferences

### Integration Points
- Case management: Clio, Filevine, MyCase, Smokeball, Practice Panther (two-way sync)
- Court calendar data (PACER for federal courts, state court portals)
- Google Calendar / Microsoft Outlook (calendar event creation)
- GHL CRM (firm-level deadline dashboard)
- SMS/email delivery for multi-channel alerts
- Managing partner escalation system for unacknowledged deadlines

### Sample Prompt/Persona
> "You are a meticulous litigation docket manager and malpractice prevention specialist. Your single most important job is to make sure no deadline is ever missed. You are obsessive about accuracy — you verify every date calculation twice, accounting for weekends, federal and state holidays, and local court rules. When you extract dates from a scheduling order, list every single date you found and have the responsible attorney confirm each one. When a deadline is within 7 days and has not been acknowledged, you escalate immediately to the managing partner. You treat a missed deadline as a catastrophic failure. Because it is."

### Customization Variables
- Jurisdiction court rules database per firm's practice geography
- Alert timing configuration per deadline category
- Responsible party routing per matter role
- Case management system integration target
- Holiday calendar per jurisdiction
- Acknowledgment requirement settings per deadline category

### Stickiness Factor
Deadline management is existential for litigation firms — a missed statute of limitations is a malpractice claim. Once attorneys rely on this system's morning briefings and acknowledge its alerts as part of their daily workflow, it becomes the operational backbone of the litigation practice. Firms with active malpractice insurance often see underwriters ask about deadline management systems — having this documented creates insurance and risk management value that is institutionalized.

### Upsell Path
Bundle with SKILL-056 (Case Qualification Bot) for a complete intake-to-active case management package. Upsell to a full matter workflow automation system that chains deadline alerts to task assignments. Enterprise upsell for large litigation departments: a firm-wide docket analytics dashboard.

---

## SKILL-061: AI Demand Letter Generator

**Category**: Content Engine / Workflow Automation
**Applies To**: Personal injury, insurance defense, employment law, collections, landlord-tenant
**Deployment Platform**: Claude + GHL + Document automation + Clio/Filevine integration
**Complexity**: Medium
**Monthly Value to Client**: $600 - $2,000

### What It Does
Generates a professionally drafted demand letter from structured case facts and damage calculations — typically a 3–6 page document that serves as the formal opening of settlement negotiations. What typically takes an attorney or paralegal 1–2 hours to draft from scratch is produced in under 5 minutes, in the firm's established style and format, ready for attorney review. For high-volume PI practices handling 50–200 active cases, this is a multi-hour-per-week time recapture.

### Core Capabilities
- Generate complete demand letter from: incident facts, liability narrative, injury description, medical treatment timeline, medical bills, lost wages, pain and suffering, future medical needs
- Apply jurisdiction-specific formatting, citation style, and legal standard language
- Pull all damages figures directly from integrated case management data
- Include supporting exhibit list (medical records index, bills summary, wage loss documentation)
- Produce demand in firm's letterhead/template format
- Calculate total demand amount with itemized breakdown
- Flag missing documentation
- Generate multiple demand versions: initial demand, counter-offer response, final demand
- Log demand version history in case management system

### Data Inputs Required
- Incident facts: date, location, liability narrative, defendant information
- Injury description: diagnosis, treatment providers, treatment timeline
- Medical records and bills (uploaded documents or summarized data)
- Lost wages documentation
- Future medical needs estimate (if applicable)
- Pain and suffering narrative
- Defendant/insurance carrier information
- Policy limits information (if known)
- Firm letterhead template and style guide

### Integration Points
- Clio, Filevine, MyCase (pull case facts, damages data, document list from matter record)
- Document management: NetDocuments, iManage (save generated letter to matter file)
- Medical bill aggregation tools (SmartAdvocate, EsquireTech)
- Microsoft Word (output in .docx format for attorney review)
- GHL CRM (demand letter stage tracking in case pipeline)
- E-fax or certified mail delivery services for formal transmission

### Sample Prompt/Persona
> "You are a senior litigation attorney drafting a demand letter. Your writing is authoritative, precise, and strategic. You open with a clear statement of liability — don't bury the lede. Build your damages argument methodically: start with economic damages where you have hard numbers, then build to general damages with vivid but professionally appropriate narrative. Your demand amount is not your bottom line — structure it to leave negotiating room. Your tone is firm and professional, never threatening. Every claim must be supported — if you don't have documentation, flag it as a gap rather than stating unsupported facts."

### Customization Variables
- Practice area template variants (auto accident vs. slip-and-fall vs. medical malpractice vs. employment)
- Jurisdiction-specific legal standards and statutory citations
- Firm letterhead and formatting template
- Pain and suffering narrative style
- Demand multiplier logic (firm's typical demand-to-settlement ratio approach)
- Insurance carrier-specific style adjustments
- Attorney review workflow (track changes, approval gate before transmission)

### Stickiness Factor
PI firms that run 50+ active cases at any time generate demand letters continuously. Once the firm's standard demand template, damages calculation formula, and exhibit structure are built into this system, the generated output matches the firm's established style so closely that attorneys use it as a final-draft starting point. The case management data integration means damages figures pull directly from the matter record — any re-drafting from scratch wastes paralegal time that firms measure in dollars.

### Upsell Path
Bundle with SKILL-056 (Case Qualification Bot) and SKILL-058 (PI Case Calculator) for a complete personal injury practice automation suite. Upsell to a full settlement negotiation workflow tool. High-volume firms upsell to a case progression analytics dashboard.

---

# HOME SERVICES (062-067)

---

## SKILL-062: AI Emergency Dispatch Triage Agent

**Category**: Voice Agent / Chat Agent
**Applies To**: Plumbing, HVAC, electrical, restoration, locksmith, roofing — any home services company with emergency response
**Deployment Platform**: Vapi (voice-first) + GHL + Dispatch software integration
**Complexity**: High
**Monthly Value to Client**: $1,000 - $3,500

### What It Does
Answers all inbound calls 24/7 — including 2 AM emergency calls that would otherwise go to voicemail and convert to lost revenue. Conducts a rapid triage conversation to determine whether the situation is a true emergency or a standard service call. Dispatches on-call techs immediately for confirmed emergencies, books standard appointments for non-urgent calls, and eliminates the need for a live after-hours answering service that costs $500–$1,500/month and still misroutes calls.

### Core Capabilities
- Answer 100% of inbound calls 24/7 without voicemail
- Conduct situation-specific triage questions: "Is water actively flowing right now?" / "Do you smell gas?" / "Is there any sparking or burning smell?"
- Classify call as Emergency (immediate dispatch), Urgent (same-day), or Standard (scheduled)
- For gas/fire/life-safety situations: immediately direct caller to call 911 first, then stay on line
- Capture customer name, address, phone, and problem description
- Trigger on-call tech dispatch via SMS alert with full customer and job details
- Book standard appointments directly into scheduling software (ServiceTitan, Housecall Pro)
- Provide caller with ETA confirmation and tech name/photo (if available)
- Create job record in CRM/dispatch system automatically

### Data Inputs Required
- On-call tech schedule and rotation
- Emergency classification criteria per trade
- Service area ZIP codes for geographic routing
- Tech phone numbers and dispatch preferences
- Scheduling software access (ServiceTitan, Housecall Pro, Jobber)
- Customer database for returning customer recognition

### Integration Points
- Vapi (AI voice agent, 24/7 live call answering)
- ServiceTitan, Housecall Pro, Jobber, FieldEdge (job creation and scheduling)
- GHL CRM (lead/customer record creation and tracking)
- Twilio SMS (tech dispatch alerts and customer confirmations)
- Google Maps API (ETA calculation for on-call tech location)
- On-call notification: pager, SMS, or phone call to tech

### Sample Prompt/Persona
> "You are the emergency dispatch coordinator for [Company Name]. You answer every call immediately and with urgency — if someone is calling us, they have a problem. Start by asking: 'Hi, this is [Company], what's happening at your home today?' Listen carefully. If they say anything involving water actively flooding, gas odor, sparking, smoke, or extreme temperatures, treat it as an emergency immediately. Confirm their address. Tell them exactly what happens next: 'I'm contacting our on-call tech right now — they'll call you within 15 minutes and be there within [X] hours.' Be calm, fast, and reassuring."

### Customization Variables
- Trade-specific emergency classification logic
- On-call dispatch rules and tech rotation schedule
- Service area boundaries and after-hours service zones
- Emergency surcharge disclosure language
- Tech dispatch method preference (SMS vs. phone call vs. app notification)
- Returning customer recognition logic

### Stickiness Factor
Home service companies that implement 24/7 voice answering immediately see their after-hours revenue increase — the ROI is directly measurable in jobs booked overnight vs. voicemail leads lost. The dispatch software integration means removing the agent breaks the entire after-hours operations workflow.

### Upsell Path
Bundle with SKILL-064 (Smart Dispatch & Route Optimizer) for a complete inbound-to-dispatch automation system. Upsell to a customer satisfaction follow-up sequence post-job completion. High-volume companies upsell to a full operations platform including capacity planning, tech performance analytics, and revenue forecasting by call source.

---

## SKILL-063: AI Job Estimator Widget

**Category**: Widget/Tool
**Applies To**: Plumbing, HVAC, electrical, handyman, roofing, painting, landscaping, restoration
**Deployment Platform**: Custom embeddable widget + Claude + GHL + Photo analysis API
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,200

### What It Does
Embeds on a home services company's website and allows homeowners to describe their problem and upload photos, receiving a ballpark estimate range within 60 seconds. Not a binding quote — but good enough to tell a homeowner whether they're facing a $200 repair or a $5,000 replacement, which moves them from "browsing" to "booking." Captures the lead and pre-qualifies it against the company's average ticket size, routing high-value estimates to the sales team and standard estimates to automated booking.

### Core Capabilities
- Accept text description of the problem (guided by structured prompts per trade)
- Accept photo uploads (up to 5 images) analyzed by AI vision for visible damage scope
- Generate ballpark estimate range by job type
- Distinguish between repair estimate and replacement estimate where applicable
- Capture homeowner name, phone, email, address, and home age/type
- Route high-value estimates to sales callback within 2 hours
- Auto-book standard estimates into scheduling software
- Log estimate and contact in GHL CRM with job type tag and estimated value

### Data Inputs Required
- Trade-specific job type menu and associated estimate ranges
- Company's geographic pricing
- Photo analysis capability (vision API for damage assessment)
- High-value estimate threshold configuration
- Scheduling software access for direct booking
- Service area ZIP codes

### Integration Points
- Company website (embeddable JavaScript widget)
- GHL CRM (lead capture and tagging by job type and estimated value)
- ServiceTitan, Housecall Pro, Jobber (booking integration for standard estimates)
- Google Maps API (verify service area coverage)
- Company phone system or Vapi (for high-value callback trigger)
- Financing partners (Greensky, Wisetack) for large replacement estimates

### Sample Prompt/Persona
> "You are a knowledgeable home repair advisor. When a homeowner describes their problem and uploads photos, give them an honest ballpark — not a commitment. Use plain language: 'Based on what you've described, a repair like this typically runs between $X and $Y for labor and parts. The final price depends on exactly what we find when our tech arrives.' Always explain what drives the range. If the estimate is large, acknowledge it and mention financing. Always end by offering to book an appointment to get them an exact quote."

### Customization Variables
- Trade type and job type menu per company's service offerings
- Estimate ranges per job type (calibrated to company's actual pricing)
- Geographic labor rate multiplier
- High-value threshold for sales team routing
- Financing partner selection and display threshold
- Photo analysis depth
- Widget branding and color scheme

### Stickiness Factor
Companies that embed this widget see measurable conversion rate improvements. The estimate range database — calibrated to the company's actual pricing over months — becomes proprietary intellectual property. Removing the widget means losing a proven lead conversion asset with documented ROI.

### Upsell Path
Bundle with SKILL-062 (Emergency Dispatch Agent) for a complete inbound lead capture and triage system. Upsell to a full sales pipeline where estimate leads are nurtured via multi-touch follow-up. High-revenue companies upsell to a dynamic pricing engine that adjusts estimate ranges based on tech capacity, demand, and season.

---

## SKILL-064: AI Smart Dispatch & Route Optimizer

**Category**: Operations / Workflow Automation
**Applies To**: HVAC, plumbing, electrical, pest control, lawn care, appliance repair — any field service business with multiple techs
**Deployment Platform**: Custom (Google Maps API + AI optimization) + ServiceTitan/Housecall Pro integration + GHL
**Complexity**: High
**Monthly Value to Client**: $1,500 - $5,000

### What It Does
Automatically assigns incoming jobs to the right technician based on real-time geographic proximity, individual tech skill set and certifications, current parts inventory on each truck, job priority tier, and current schedule load — then generates the optimal daily route for each tech. Reduces drive time by 20–35%, increases jobs-per-tech-per-day from an average of 4–5 to 6–8, and ensures that the tech arriving on-site has both the skills and the parts to complete the job without a second trip.

### Core Capabilities
- Ingest all open jobs with location, job type, required skills, and estimated job duration
- Pull each tech's current location, current schedule, certified skills, and truck parts inventory
- Solve multi-tech routing optimization using Google Maps Distance Matrix API
- Apply priority weighting: emergency > same-day urgent > scheduled maintenance
- Assign jobs to minimize total drive time across all techs simultaneously
- Flag jobs that require parts not currently on any truck → trigger parts order or warehouse pickup
- Generate each tech's optimized daily schedule with turn-by-turn routing
- Push schedule to tech via dispatch app (ServiceTitan, Housecall Pro, or Jobber)
- Re-optimize dynamically when emergency jobs are added mid-day
- Track actual vs. estimated job duration to improve future scheduling accuracy

### Data Inputs Required
- Open job queue with addresses, job types, required skills, and priority tiers
- Tech roster with skill/certification tags, current location (GPS), and current schedule
- Parts inventory per truck
- Real-time traffic data (Google Maps API)
- Estimated job duration by job type
- Service area map and zone assignments

### Integration Points
- ServiceTitan, Housecall Pro, Jobber, FieldEdge (job data and schedule push)
- Google Maps Platform (routing, distance matrix, real-time traffic)
- GPS fleet tracking: Samsara, Verizon Connect, Fleetmatics
- Parts/inventory management systems
- GHL CRM (job tracking and analytics)
- Tech mobile app for schedule delivery and job status updates

### Sample Prompt/Persona
> "You are the operations director for [Company Name]'s field team. Every morning you receive all jobs for the day. Your job is to build the perfect schedule for each tech — one that minimizes drive time, matches jobs to tech skill sets, ensures every tech has the right parts, and prioritizes emergencies above all else. When a new emergency call comes in mid-day, you re-optimize the entire schedule in real time without losing jobs already in progress. You measure your success by jobs completed per tech per day."

### Customization Variables
- Tech skill/certification taxonomy per company
- Priority weighting algorithm
- Parts inventory integration (manual vs. system-integrated)
- Re-optimization trigger (automatic on new job vs. manual manager approval)
- Tech schedule delivery method
- Job duration estimation database per job type and tech performance history

### Stickiness Factor
Once optimized dispatching becomes the operational standard, reverting to manual dispatch feels like going backward. Companies measure the impact directly: more jobs per day, lower fuel costs, higher revenue per tech. The tech skill matrix and truck inventory data represent weeks of configuration investment. Operations managers who see the optimization dashboard's performance metrics become advocates who will not give up the tool voluntarily.

### Upsell Path
Bundle with SKILL-062 (Emergency Dispatch) and SKILL-063 (Job Estimator Widget) for a complete operations platform. Upsell to a capacity planning tool that forecasts demand vs. tech capacity. Multi-location companies upsell to a fleet-wide analytics dashboard.

---

## SKILL-065: AI Seasonal Maintenance Campaign Agent

**Category**: Workflow Automation / Chat Agent
**Applies To**: HVAC, plumbing, roofing, pest control, lawn care, chimney, irrigation
**Deployment Platform**: GHL + Claude + Vapi + Make/Zapier
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,500

### What It Does
Proactively contacts the company's entire customer database at the appropriate seasonal inflection points — spring HVAC tune-up campaigns, fall furnace check campaigns, pre-freeze plumbing inspections, spring pest control pre-treatments — with personalized outreach that references the customer's last service date and their specific equipment. Converts dormant past customers into booked appointments before competitors can reach them, generating predictable shoulder-season revenue that would otherwise require expensive advertising.

### Core Capabilities
- Segment customer database by service type, last service date, and equipment type
- Schedule campaign launch windows tied to seasonal triggers (calendar-based or weather-triggered)
- Execute multi-channel outreach: SMS, email, and AI voice call (Vapi)
- Personalize every touchpoint: "Hi [Name], we serviced your Carrier furnace last October…"
- Offer service plan/maintenance agreement upsell in every seasonal campaign
- Allow customers to book directly via SMS/email link or with AI voice agent on the call
- Track campaign performance: open rates, booking rates, revenue generated per campaign
- Auto-suppress opted-out customers and those with upcoming appointments

### Data Inputs Required
- Customer database with contact info, last service date, equipment type/brand, service history
- Seasonal campaign calendar
- Maintenance offer details (pricing, what's included)
- Service plan/agreement details and pricing
- Agent/company availability calendar for bookings
- Opt-out and TCPA compliance database

### Integration Points
- ServiceTitan, Housecall Pro, Jobber (customer and service history data)
- GHL CRM (sequence management, campaign tracking)
- Vapi (outbound AI voice campaign option)
- Weather API (for weather-triggered campaign timing)
- SMS/email delivery via GHL
- Financing partners for larger replacement or plan upsells

### Sample Prompt/Persona
> "You are a friendly service coordinator from [Company Name] reaching out before the busy season. You are proactive — you are calling because you genuinely want to make sure this customer's home is ready before everyone else waits until there's a breakdown. Reference their specific equipment and last service date. Offer the seasonal maintenance special. If they're interested in the service plan, explain the benefits simply: priority scheduling, discounted service rates, no-cost seasonal tune-ups. Make booking easy — either right now on this call or via a text link. Never pressure."

### Customization Variables
- Campaign calendar per climate zone
- Equipment type personalization (Carrier, Lennox, Trane — different maintenance intervals)
- Service plan details and pricing
- Campaign cadence per customer tier
- Multi-channel sequence timing and order
- Revenue-per-campaign tracking and ROI reporting

### Stickiness Factor
Seasonal campaigns run on autopilot — once configured, they run every spring and fall without any manual work. Companies that see the direct revenue from these campaigns (typically $15,000–$50,000 per campaign for mid-size HVAC companies) build them into their annual revenue projections. Removing this system would require rebuilding the customer segmentation logic and campaign infrastructure from scratch.

### Upsell Path
Bundle with SKILL-062 (Emergency Dispatch) and SKILL-066 (Weather-Triggered Campaigns) for a complete proactive and reactive outbound system. Upsell to a full service agreement management system. High-volume companies upsell to a predictive maintenance reminder system.

---

## SKILL-066: AI Weather-Triggered Campaign Agent

**Category**: Workflow Automation / Operations
**Applies To**: HVAC, roofing, restoration, plumbing, generators, pest control, lawn care
**Deployment Platform**: GHL + Weather API + Make/Zapier + Claude
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,500

### What It Does
Monitors weather forecasts for the company's service territory and automatically launches targeted outreach campaigns when triggering conditions are detected — a heat wave driving AC demand, a cold snap triggering heating failures, a storm system generating emergency roofing and restoration calls before the storm even hits. The company that reaches homeowners 12–24 hours before a weather event captures demand at scale; the company that waits for inbound calls fights for capacity after everyone is already calling.

### Core Capabilities
- Monitor real-time and forecast weather data across company service territory ZIP codes
- Detect predefined trigger conditions: heat index above threshold, overnight low below freeze, wind speed forecast, precipitation forecast, storm watch/warning
- Auto-launch configured campaign within 1 hour of trigger condition detection
- Segment campaign recipients by service relevance (AC customers for heat wave, furnace customers for cold snap)
- Personalize outreach with weather context: "A hard freeze is forecast for [City] tonight…"
- Offer proactive inspection or tune-up before the event
- Track revenue attribution per weather campaign trigger
- Provide daily weather event log with campaign performance summary

### Data Inputs Required
- Service territory ZIP codes and climate zone
- Weather trigger thresholds per campaign type
- Customer segmentation tags by service type from CRM/field service software
- Pre-built campaign templates per weather event type
- Calendar availability for campaign-driven bookings
- Opt-out compliance database

### Integration Points
- Weather APIs: Weather.com API, Tomorrow.io, National Weather Service
- GHL CRM (segment targeting, sequence launch, performance tracking)
- ServiceTitan, Housecall Pro, Jobber (customer service history for segmentation)
- SMS/email delivery platforms
- Vapi (optional outbound voice campaign for major weather events)
- Revenue tracking integration

### Sample Prompt/Persona
> "You are a proactive home comfort advisor from [Company Name]. You monitor the weather so our customers don't have to. When a significant weather event is approaching their area, you reach out before it hits — not after. Your message is brief, genuinely helpful, and specific: '[Name], a heat wave above 95° is forecast for [City] starting Thursday. We're reaching out to our customers now before our schedule fills up — want us to check your AC unit before then?' You are not fear-mongering. You are the company that helps customers get ahead of problems."

### Customization Variables
- Weather trigger thresholds per campaign type
- Service territory map
- Campaign templates per weather event type (10+ preset templates)
- Customer segmentation rules per weather event relevance
- Campaign launch delay after trigger
- Revenue attribution window

### Stickiness Factor
Weather-triggered campaigns are uniquely time-sensitive — a campaign launched 6 hours after a trigger is far less effective than one launched immediately. The automated monitoring-and-launch chain, once proven effective, becomes relied upon as a primary revenue generation mechanism. Companies that see a $20,000 revenue spike from a single 3-day heat wave campaign cannot un-see that number.

### Upsell Path
Bundle with SKILL-065 (Seasonal Maintenance Campaigns) for a comprehensive proactive revenue engine. Upsell to a natural disaster response package for restoration companies. Enterprise upsell for multi-territory companies: a regional weather monitoring dashboard with customized trigger thresholds and campaign performance comparison across markets.

---

## SKILL-067: AI Energy Audit Calculator Widget

**Category**: Widget/Tool / Analytics
**Applies To**: HVAC companies, solar installers, insulation contractors, energy efficiency consultants, utilities
**Deployment Platform**: Custom embeddable widget + Claude + GHL
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,200

### What It Does
Embeds on a home services company's website and guides homeowners through a 10-question energy efficiency assessment covering home size, age, insulation type, HVAC age, window type, utility bills, and occupancy patterns. Generates a personalized energy efficiency scorecard with estimated annual energy waste, projected savings from specific improvements, and a prioritized recommendation list for the company's services. Captures high-intent leads who are actively thinking about energy costs.

### Core Capabilities
- Guide homeowners through structured 10–15 question energy assessment
- Calculate estimated annual energy waste based on home characteristics vs. efficiency benchmarks
- Generate prioritized improvement recommendations with estimated ROI and payback periods
- Present estimated annual savings for each recommendation
- Display applicable federal and state tax credits/rebates for each improvement
- Calculate estimated monthly payment if financed
- Capture homeowner contact information and home details for contractor follow-up
- Generate branded PDF Energy Efficiency Report for homeowner
- Log all assessment data in GHL CRM with estimated job value tag

### Data Inputs Required
- Home size (square footage)
- Home age and construction type
- Current HVAC system type and age
- Existing insulation type (attic, walls)
- Window type and age
- Average monthly utility bill (summer and winter)
- Geographic location (climate zone)
- Number of occupants and occupancy patterns

### Integration Points
- Company website (embeddable JavaScript widget)
- GHL CRM (lead capture with energy score, estimated job value, prioritized improvements)
- Energy efficiency benchmark databases (ENERGY STAR, DOE climate zone data)
- Federal and state rebate database (current IRA tax credits, utility rebate programs)
- Financing partners: Greensky, Mosaic, Wisetack
- Scheduling software for follow-up appointment booking
- ServiceTitan / Housecall Pro for lead-to-job pipeline

### Sample Prompt/Persona
> "You are a home energy advisor. Your job is to give homeowners an honest picture of where their home is losing energy and money — and what they can do about it. Be specific: 'Based on your 1975 home with original attic insulation and a 14-year-old HVAC system, you're likely spending $480–$620 more per year in energy costs than a comparable home with modern efficiency.' Present recommendations in order of impact, not price. Show the ROI timeline clearly. Always mention available rebates — homeowners love money they didn't know they had."

### Customization Variables
- Service area climate zone
- Company's specific service offerings
- Financing partner selection and current rate parameters
- Federal/state rebate database (updated quarterly)
- Assessment question depth
- Widget branding, color scheme, and logo
- Estimated job value threshold for sales team routing

### Stickiness Factor
Energy audit widgets are strong lead quality filters — homeowners who complete a 10-question assessment and receive a personalized report are far more motivated than contact form submitters. The proprietary energy score calculation, tailored to the company's service area climate zone, is a branded experience competitors cannot replicate without rebuilding from scratch.

### Upsell Path
Bundle with SKILL-065 (Seasonal Maintenance Campaigns) to follow up with energy audit leads when seasonal conditions align with their top recommendation. Upsell to a comprehensive home efficiency program. High-value upsell for solar companies: integrate solar production estimates into the energy audit to create a combined efficiency + solar ROI analysis.

---

# INSURANCE (068-073)

---

## SKILL-068: AI Quote Generation Voice Agent

**Category**: Voice Agent
**Applies To**: Independent insurance agencies, captive agents, MGAs — P&C, auto, home, commercial, life
**Deployment Platform**: Vapi + GHL + Agency Management System integration + Rating engine API
**Complexity**: High
**Monthly Value to Client**: $1,500 - $5,000

### What It Does
Answers inbound calls from prospective customers seeking insurance quotes, conducts a complete underwriting intake interview via voice, and generates preliminary rate indications across multiple carriers in real time. What previously required a 20–30 minute agent interview and manual data entry into multiple carrier portals is compressed into an 8–12 minute AI-driven conversation that feeds simultaneously into the agency's quoting system. Agents only engage with hot prospects who already have a quote range in hand.

### Core Capabilities
- Answer inbound quote request calls 24/7 with natural conversational voice
- Conduct product-specific intake: auto (vehicles, drivers, violations, prior coverage), home (construction type, year built, square footage, coverage history), commercial (business type, revenue, employees, loss history)
- Ask clarifying underwriting questions based on initial responses
- Pull preliminary rates from connected carrier rating engines or comparative rater platforms (EZLynx, TurboRater, PL Rater)
- Present 3-carrier rate comparison with coverage highlights over the phone
- Capture all intake data and push to agency management system
- Schedule agent follow-up call for policy binding
- Send digital quote summary via SMS/email immediately post-call

### Data Inputs Required
- Carrier appointment roster and available products per state
- Rating engine API credentials (EZLynx, TurboRater, PL Rater, or direct carrier APIs)
- Agency management system credentials (Applied Epic, HawkSoft, Agency Matrix)
- Underwriting intake fields per product line
- Agent availability calendar for follow-up scheduling
- Agency branding for quote summary documents

### Integration Points
- Vapi (voice AI with natural conversation and interruption handling)
- Comparative raters: EZLynx, TurboRater, PL Rater
- Agency management systems: Applied Epic, HawkSoft, Vertafore AMS360, Agency Matrix
- GHL CRM (prospect record, pipeline tracking, follow-up sequences)
- SMS/email delivery (quote summary and appointment confirmation)
- E-signature for policy application/binder delivery

### Sample Prompt/Persona
> "You are a friendly, professional insurance intake specialist for [Agency Name]. You've helped thousands of families find the right coverage. Your tone is warm and reassuring — insurance is confusing, and people appreciate someone who makes it simple. Gather information methodically but conversationally — not like a form, like a conversation. When you have enough information to provide initial rates, tell the prospect clearly what you found: 'Based on what you've shared, I'm seeing rates for your auto policy starting around $X per month with [Carrier A], and [Carrier B] is coming in around $Y.' Then set up the agent call: 'Our specialist will review your exact situation and can have you covered today.'"

### Customization Variables
- Product line configuration per agency's carrier appointments and state licenses
- Underwriting intake logic per product
- Carrier priority order
- Rating engine integration target
- AMS field mapping per agency's system configuration
- Quote summary template and branding
- Agent follow-up routing rules

### Stickiness Factor
Insurance agencies that deploy this stop losing after-hours quote requests to competitors. The rating engine integration and AMS data push represents significant technical setup. Once the agency's producers see their hot-lead queue populated every morning with prospects who already have quote ranges in hand, they will not willingly return to cold-start conversations.

### Upsell Path
Bundle with SKILL-071 (Policy Comparison Widget) and SKILL-073 (Life Insurance Needs Calculator) for a complete new business generation package. Upsell to a cross-sell campaign system. High-volume agencies upsell to a comprehensive new business analytics dashboard.

---

## SKILL-069: AI Claims Intake Bot (FNOL)

**Category**: Chat Agent / Voice Agent / Intake
**Applies To**: Insurance agencies, MGAs, carriers, TPA claim departments — auto, home, commercial, workers' comp
**Deployment Platform**: Vapi (voice) + GHL + Claude + Claims management system integration
**Complexity**: High
**Monthly Value to Client**: $1,200 - $4,000

### What It Does
Handles First Notice of Loss (FNOL) calls and messages 24/7 — collecting complete incident details, guiding claimants through photo/document uploads, issuing a claim number, and routing to the appropriate adjuster immediately. Claims reported at 11 PM on a Saturday get the same quality intake as those reported Monday morning. Every FNOL is complete, structured, and attached to the claimant's policy before a human adjuster ever opens the file.

### Core Capabilities
- Collect complete FNOL data: policy number, insured name, date/time of loss, location, incident description, parties involved, witnesses, injuries, police/fire report info
- Guide claimant through photo and document upload process
- Issue preliminary claim number and provide it to claimant immediately
- Triage claim severity: minor (self-service path), moderate (adjuster assignment next business day), severe (emergency adjuster dispatch)
- Route severe claims for immediate adjuster notification
- Push complete structured FNOL data to claims management system
- Send claimant confirmation with claim number, adjuster assignment, and next steps
- Collect coverage information for coverage verification trigger

### Data Inputs Required
- Policy database or lookup capability
- Claims management system credentials for FNOL creation
- Severity triage criteria per line of business
- Adjuster roster and assignment rules
- Emergency adjuster contact list for severe claims
- Document upload capability (secure file handling)

### Integration Points
- Claims management systems: Guidewire ClaimCenter, Duck Creek, Snapsheet, ClaimXperience
- GHL CRM (claimant communication and follow-up tracking)
- Vapi (voice FNOL for phone reporters)
- Document management (secure photo/document upload portal)
- Adjuster notification: SMS, email, or claims system task assignment
- Policy administration systems for coverage verification trigger
- Rental car and temporary housing partner referral

### Sample Prompt/Persona
> "You are a claims intake specialist for [Company Name]. Someone calling you has just experienced something bad — an accident, a break-in, a fire, a flood. Lead with empathy first: 'I'm so sorry to hear this happened. Let me help you get your claim started right away.' Collect information systematically but gently — people under stress forget things and repeat themselves. Never rush them. When you've collected everything, reassure them: 'Your claim number is [XXXX]. An adjuster will contact you by [timeframe]. Here's what happens next.' Your goal is that every claimant hangs up feeling heard, organized, and confident that their claim is in good hands."

### Customization Variables
- Line of business configuration (auto FNOL collects different data than home or commercial)
- Severity triage criteria per line and company's claim handling philosophy
- Claim number generation format
- Adjuster assignment rules
- Claims system integration target and field mapping
- Document upload security requirements
- Claimant communication sequence post-FNOL

### Stickiness Factor
Insurance companies that deploy FNOL automation reduce their claim cycle times by 15–25% because adjusters receive complete, structured files instead of incomplete voicemails. Claimant satisfaction scores improve measurably. The claims system integration — particularly in Guidewire or Duck Creek environments — represents enterprise-level technical work that is not replicated lightly.

### Upsell Path
Bundle with SKILL-072 (Catastrophe Response Agent) for a complete claims event management package. Upsell to a claims status update automation. Enterprise carriers upsell to a claims analytics dashboard.

---

## SKILL-070: AI Underwriting Assistant

**Category**: Analytics / Workflow Automation
**Applies To**: Insurance agencies, MGAs, wholesale brokers, carriers — P&C commercial lines, specialty lines
**Deployment Platform**: Claude + Custom document analysis + GHL + Agency management system
**Complexity**: High
**Monthly Value to Client**: $2,000 - $7,000

### What It Does
Analyzes commercial insurance submissions — ACORD applications, loss runs, financial statements, inspection reports — against carrier appetite guidelines to determine acceptability, flag underwriting concerns, identify missing information, and draft the submission narrative for wholesale markets. Transforms what was a 45–90 minute underwriter or producer task per submission into a 5–10 minute review-and-approve workflow. For MGAs and commercial agencies processing 20+ submissions weekly, this is a transformative capacity expansion.

### Core Capabilities
- Analyze ACORD applications for completeness and flag missing or inconsistent fields
- Parse loss run history: calculate loss ratios, identify frequency vs. severity patterns, flag large individual losses
- Match submission against carrier/market appetite grids per class of business
- Identify declination triggers: disqualifying occupancy, excluded operations, problematic loss history
- Research business via web (name, address, operations, reviews) to identify undisclosed risks
- Draft submission narrative for wholesale market placement
- Generate underwriting questions list for incomplete submissions
- Suggest appropriate carrier markets based on risk characteristics and appetite match
- Produce one-page underwriting summary memo for producer/underwriter review

### Data Inputs Required
- ACORD application (PDF or structured data)
- Loss runs (PDF — 3–5 years typically required)
- Financial statements for large commercial accounts (if applicable)
- Carrier/market appetite guidelines (uploaded by agency per carrier — proprietary configuration)
- Class of business codes and corresponding underwriting parameters
- Agency's preferred market list per class

### Integration Points
- Agency management systems: Applied Epic, Vertafore AMS360, HawkSoft (submission intake)
- Document management platforms (NetDocuments, SharePoint)
- GHL CRM (submission pipeline tracking and deadline management)
- Carrier portals (for submission upload post-analysis)
- Web research APIs (for business validation and risk research)
- E-mail / workflow systems for underwriter review and approval routing

### Sample Prompt/Persona
> "You are an experienced commercial lines underwriter reviewing an incoming submission. Your job is to be thorough and brutally honest — both about the risks and about the gaps in information. Start with a quick summary: what is this risk, is it in-appetite, and what's your initial read on acceptability? Then go through the loss history systematically. Then identify every piece of information that's missing or needs clarification before this can be quoted. Draft the submission narrative for the wholesale market — write it to get this account quoted, not just filed. End with your market recommendations: who should see this and why."

### Customization Variables
- Carrier appetite guidelines per market (uploaded and updated by agency)
- Class of business taxonomy and underwriting parameters per SIC/NAICS code
- Loss ratio threshold alerts per class
- Business research depth
- Submission narrative style per target wholesale market
- Underwriting question template per class of business
- Producer routing rules

### Stickiness Factor
An agency that loads all of its carrier appetite guidelines into this system creates a proprietary underwriting knowledge base that lives in the platform. Senior underwriters who calibrate the appetite matching logic over months of use are essentially encoding their expertise into the system. Removing it would mean losing both the institutional knowledge and the productivity gains.

### Upsell Path
Bundle with SKILL-068 (Quote Voice Agent) and SKILL-069 (FNOL Claims Bot) for a full commercial lines agency operations platform. Upsell to a market placement optimization tool. Enterprise MGA upsell: an automated appetite grid monitoring system.

---

## SKILL-071: AI Policy Comparison Widget

**Category**: Widget/Tool
**Applies To**: Independent insurance agencies, insurance marketplaces, direct-to-consumer carriers
**Deployment Platform**: Custom embeddable widget + GHL + Rating engine integration
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,500

### What It Does
Embeds on an agency's website and allows prospective customers to compare insurance coverage options side by side — with clear visual breakdowns of deductibles, premiums, coverage limits, key exclusions, and value differentials between policies. Takes the confusion out of insurance comparison shopping, which is the #1 reason consumers abandon insurance purchase decisions.

### Core Capabilities
- Display 2–4 policy options in a clean, side-by-side comparison format
- Highlight key differences between options in plain language
- Show premium breakdown: annual, monthly, per-pay-period
- Visualize coverage levels using icons and rating bars
- Flag the "best value" option based on configurable criteria
- Show carrier AM Best rating and customer service score for each option
- Allow user to filter/adjust comparison by priority
- Capture contact information and selected preference for agent follow-up
- Integrate with quote data from rating engine or agency management system

### Data Inputs Required
- Quote data from rating engine (policy options, premiums, coverage details)
- Carrier information (AM Best rating, logo, customer service metrics)
- Coverage definitions in plain English per product type
- Value scoring logic
- Agency branding assets
- Follow-up booking calendar for agent consultation

### Integration Points
- Comparative raters: EZLynx, TurboRater, PL Rater (quote data pull)
- Agency management system (prospect record creation)
- GHL CRM (lead capture and sales pipeline management)
- Company website (embeddable widget)
- E-signature platforms for policy application
- Payment processors for policy binding and premium collection

### Sample Prompt/Persona
> "You are a consumer insurance advisor helping a customer understand their options. Your language is plain English — never insurance jargon. When presenting comparisons, lead with what matters to them: 'This option costs $40 more per month but raises your liability coverage from $100,000 to $300,000 — here's why that matters.' Help them understand trade-offs, not just differences. When they've selected an option, make the next step obvious and easy: 'Great choice. I can have an agent call you back in the next 15 minutes to finalize this, or you can complete it online right now.'"

### Customization Variables
- Product line layout per product type
- Value scoring weights per agency philosophy
- Carrier presentation order and featured carrier logic
- Plain-English coverage descriptions per product
- Mobile vs. desktop layout optimization
- Agency branding
- Financing/payment frequency options displayed

### Stickiness Factor
Agencies whose prospects convert through the comparison widget are better-informed buyers who tend to have higher retention rates. The conversion rate data from the widget becomes actionable sales intelligence that compounds in value over time.

### Upsell Path
Bundle with SKILL-068 (Quote Generation Voice Agent) for a complete new business pipeline. Upsell to a proposal generation system. High-volume agencies upsell to a behavioral analytics layer.

---

## SKILL-072: AI Catastrophe Response Agent

**Category**: Workflow Automation / Voice Agent
**Applies To**: Insurance carriers, MGAs, large independent agencies — catastrophe-exposed books (hurricane, tornado, wildfire, hail)
**Deployment Platform**: GHL + Vapi + Weather/catastrophe monitoring API + Claims system
**Complexity**: High
**Monthly Value to Client**: $2,500 - $8,000

### What It Does
Monitors catastrophe event data (hurricane landfall, tornado outbreaks, hail storms, wildfires) and automatically identifies all policyholders in the affected geographic area within the company's book of business. Immediately launches a mass outreach campaign via SMS, email, and optional AI voice call providing claims filing instructions, safety resources, and personalized next-step guidance. The company that reaches its policyholders first after a CAT event earns trust; the company whose customers can't get through loses them at renewal.

### Core Capabilities
- Monitor catastrophe event data: NWS severe weather events, hurricane track data, wildfire perimeter mapping, hail swath data
- Cross-reference event geography against policyholder ZIP codes in book of business
- Trigger mass outreach campaign within 2 hours of event confirmation
- Personalize outreach by product type: home, auto, commercial, renters
- Provide event-specific claims instructions
- Include claim filing link, adjuster hotline, and emergency contractor referral list
- Allow policyholders to initiate FNOL directly from campaign message
- Track outreach delivery and response rates by policyholder segment
- Generate CAT event management report for management team

### Data Inputs Required
- Policyholder database with ZIP codes, product types, and contact preferences
- CAT event monitoring thresholds
- Event-specific message templates per product line and event type
- Adjuster capacity and CAT team contact information
- Emergency contractor referral network
- Claims filing URL and FNOL bot integration
- Opt-out and communication preference database

### Integration Points
- CAT monitoring: Verisk PCS, CoreLogic Storm Data, NOAA/NWS alerts, Verisk ClimateScore
- GHL CRM (policyholder segmentation and campaign management)
- Agency management system / policy admin system
- Vapi (outbound AI voice campaign for highest-exposure policyholders)
- Claims system: Guidewire, Duck Creek (FNOL intake trigger)
- SMS/email delivery platforms
- Emergency vendor network management

### Sample Prompt/Persona
> "You are a catastrophe response coordinator for [Company Name]. A major weather event has impacted your policyholders' community. Your outreach tone is calm, helpful, and immediate — people are stressed and need clear guidance right now, not insurance formalities. Lead with the human: 'We know your community has been impacted by [event]. Your safety is the priority. Once you and your family are safe, here is how to start your claim.' Provide specific, actionable next steps. Do not mention renewal, premiums, or any commercial message. This is purely a service call."

### Customization Variables
- CAT trigger thresholds per event type and geographic market exposure
- Product line message differentiation
- Outreach priority sequencing
- Preferred emergency vendor network by geography and trade type
- Claims team CAT response capacity
- Campaign cadence: immediate alert, 72-hour check-in, 2-week follow-up

### Stickiness Factor
Carriers and MGAs with significant CAT exposure understand that post-event communication quality is directly tied to policyholder retention after the claim. The CAT monitoring + policyholder geographic database + campaign automation workflow represents infrastructure investment that insurance operations teams protect aggressively.

### Upsell Path
Bundle with SKILL-069 (FNOL Claims Bot) for a complete catastrophe response and claims intake system. Upsell to a CAT portfolio analytics tool. Enterprise carrier upsell: a real-time CAT command center dashboard.

---

## SKILL-073: AI Life Insurance Needs Calculator

**Category**: Widget/Tool / Analytics
**Applies To**: Life insurance agencies, financial advisors, independent agents, bank insurance departments
**Deployment Platform**: Custom embeddable widget + Claude + GHL
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,200

### What It Does
Guides prospective life insurance buyers through a personalized needs assessment — income replacement, debt payoff, education funding, final expense coverage, business continuation — and produces a recommended coverage amount with a specific policy type recommendation. Converts "I know I need life insurance someday" browsers into informed, motivated prospects who understand their specific coverage gap.

### Core Capabilities
- Conduct income replacement analysis: annual income × years to financial independence
- Calculate debt payoff needs: mortgage balance, auto loans, student loans, credit cards
- Project education funding needs per child (age-based calculation to college entry)
- Add final expense / end-of-life cost estimate
- Calculate existing coverage offset (group life, existing policies)
- Produce net coverage gap: recommended total coverage amount
- Recommend policy type (term length, permanent) based on need profile and budget
- Generate monthly premium estimate range for recommended coverage
- Capture prospect contact information for agent follow-up
- Send personalized "Your Life Insurance Gap Report" PDF to prospect via email

### Data Inputs Required
- Annual income and income replacement duration preference
- Debt balances (mortgage, auto, student, credit card)
- Number and ages of dependent children
- Education funding goals
- Existing life insurance coverage amounts
- Monthly budget range for premium
- Age, gender, tobacco use (for rate estimation)
- Primary financial concern

### Integration Points
- Agency website (embeddable widget)
- GHL CRM (prospect record with coverage need and recommended amount)
- AMS (Applied Epic, HawkSoft) for prospect record creation
- Carrier quoting platforms for term/permanent rate estimation
- E-mail delivery for PDF needs report
- Agent calendar for consultation scheduling
- ERP/financial planning software for wealth management firms

### Sample Prompt/Persona
> "You are a compassionate life insurance planning advisor. You are helping someone answer one of the most important questions they can ask: 'If something happened to me, would my family be okay?' Walk them through this thoughtfully. When you present their coverage gap, be direct but not alarmist: 'Based on what you've shared, we calculate a coverage need of approximately $X. That's the amount your family would need to maintain their current lifestyle, pay off your debts, and fund your children's education if you weren't here tomorrow.' Then make the path forward concrete: 'A 20-year term policy for that amount typically runs $X–$Y per month for someone your age in good health. Would you like to speak with an advisor today?'"

### Customization Variables
- Calculation methodology per agency's approach (DIME method vs. income replacement multiplier vs. human life value)
- Policy type recommendation logic per agency's product focus
- Carrier rate tables for premium estimation (updated quarterly)
- Education cost database
- Income replacement multiplier
- Widget branding and agency persona
- Lead routing rules

### Stickiness Factor
Life insurance agents whose website generates pre-qualified leads with a documented coverage need close policies at significantly higher rates. After 6 months, the calculator's lead quality data becomes a proprietary audience intelligence asset. The personalized PDF report also serves as a branded leave-behind that keeps the agency's name in front of the prospect.

### Upsell Path
Bundle with SKILL-068 (Quote Generation Voice Agent) for a complete new-business pipeline. Upsell to a Business Life Insurance Needs Calculator for agents who serve business owners. High-producing agencies upsell to a complete financial needs analysis platform.

---

# AUTOMOTIVE (074-077)

---

## SKILL-074: AI Vehicle Diagnostic Pre-Assessment

**Category**: Chat Agent / Voice Agent / Intake
**Applies To**: Auto repair shops, dealership service departments, tire/lube chains, fleet maintenance
**Deployment Platform**: Vapi (voice) + GHL + Claude + Custom chat widget
**Complexity**: Medium
**Monthly Value to Client**: $600 - $1,800

### What It Does
Enables vehicle owners to describe their symptoms or warning lights via phone or chat and receive an AI-powered pre-assessment explaining probable causes, urgency level (drive it in vs. get it towed), and an estimated repair category range — before they ever visit the shop. Reduces the friction of "I don't know what's wrong with my car" anxiety, pre-qualifies the appointment, and allows the service advisor to pull the vehicle's service history and prepare diagnostically before the car arrives.

### Core Capabilities
- Collect vehicle year, make, model, mileage, and current symptoms via voice or chat
- Interpret warning lights using OBD-II code database
- Ask targeted follow-up questions based on initial symptom
- Generate probable cause list ranked by likelihood with plain-English explanations
- Assign urgency tier: Drive it in today / Schedule this week / This is an emergency — stop driving now
- Estimate likely repair category and rough cost range
- Capture customer contact info and schedule appointment directly
- Send pre-assessment summary to service advisor before appointment
- Attach pre-assessment to CRM record for service advisor review

### Data Inputs Required
- Vehicle information: year, make, model (VIN lookup optional)
- Symptom description (free-text) and dashboard warning light identification
- Current mileage
- Recent service history (if pulled from CRM for returning customers)
- OBD-II code database
- Shop scheduling system for appointment booking

### Integration Points
- Shop management systems: Mitchell 1, ALLDATA, Shop-Ware, Tekmetric, R.O. Writer
- VIN decoder API
- OBD-II code database (NHTSA, Mitchell, ALLDATA)
- GHL CRM (customer record, visit history, follow-up sequences)
- Vapi (phone symptom intake)
- Customer chat widget (website integration)
- Scheduling tools: Calendly, Shop-Ware online booking

### Sample Prompt/Persona
> "You are a knowledgeable vehicle care advisor for [Shop Name]. Customers come to you confused and sometimes worried — their car did something strange and they don't know if it's serious. Your job is to be the trusted expert friend who gives a straight answer. Ask smart follow-up questions: 'When you say the engine is making a knocking noise, is it more of a ticking at startup or a deep knock when you accelerate?' After gathering the facts, give a clear, honest assessment: what it likely is, how serious it probably is, and what the next step should be. Never minimize a safety concern. Never over-alarm over something minor. Book the appointment before they hang up."

### Customization Variables
- Vehicle makes and models supported
- Urgency tier language and criteria
- Cost range database per repair category and local labor rate
- Pre-assessment summary format for service advisor
- VIN lookup integration (optional)
- Returning customer recognition logic

### Stickiness Factor
Service advisors who receive a pre-assessment before the vehicle arrives are more prepared, more efficient, and close higher average repair orders. Shop managers who see the pre-assessment data correlated with actual diagnosed repair orders develop institutional confidence in the tool. The shop management system integration takes time to configure and creates bidirectional data dependency.

### Upsell Path
Bundle with SKILL-075 (Digital Vehicle Inspection Reporter) for a complete pre-arrival-to-post-inspection customer communication system. Upsell to a service advisor performance coaching tool. Multi-shop groups upsell to a central pre-assessment analytics platform.

---

## SKILL-075: AI Digital Vehicle Inspection Reporter

**Category**: Content Engine / Workflow Automation
**Applies To**: Auto repair shops, dealership service departments, fleet maintenance operations
**Deployment Platform**: Custom mobile-first interface + Claude + GHL + Shop management system integration
**Complexity**: High
**Monthly Value to Client**: $1,000 - $3,500

### What It Does
Enables service technicians to capture photos and short videos of vehicle inspection findings on their mobile device, and automatically generates a customer-ready digital inspection report in branded format with professional descriptions of each finding, urgency ratings, and embedded visuals showing the customer exactly what the tech saw. Eliminates the illegible paper checklist and replaces it with a multimedia report delivered to the customer's phone while they're still in the waiting room. Shops using digital inspection reports see 20–35% higher authorized repair rates.

### Core Capabilities
- Guided inspection checklist per vehicle type (passenger car, truck, SUV, diesel — configurable per shop's protocol)
- Photo capture with annotation capability (circle, arrow, highlight) for each finding
- Short video recording for dynamic findings (fluid leak in action, abnormal belt motion, etc.)
- AI description generation per finding: tech takes photo → AI writes the customer-facing explanation
- Urgency classification per finding: immediate safety concern / recommend at this visit / monitor and address next service
- Estimated cost and time generation per finding from labor guide integration
- Customer-facing report assembled and sent to customer SMS/email while on-site
- Customer can review, approve, and authorize repairs via mobile interface
- Approved work orders automatically created in shop management system
- Report stored in customer's vehicle history for future reference

### Data Inputs Required
- Inspection checklist template per vehicle type and shop's preferred inspection points
- Shop labor guide data (Mitchell 1, ALLDATA, Chilton) for repair time and cost
- Technician mobile app access with camera
- Customer contact information (from shop management system)
- Shop branding (logo, colors, name, address)
- Shop management system credentials for repair order creation

### Integration Points
- Shop management systems: Tekmetric, Shop-Ware, Mitchell 1, Protractor, Auto/Mate
- Labor guides: Mitchell 1, ALLDATA (time and cost data per repair)
- Mobile device camera (iOS and Android native camera integration)
- GHL CRM (customer communication and approval tracking)
- SMS/email delivery for digital inspection report
- Digital payment processing (optional: customer approves and pays from mobile)
- Fleet management platforms for commercial fleet accounts

### Sample Prompt/Persona
> "You are writing vehicle inspection findings for a customer who is not mechanically inclined. When a tech photographs brake pads that are worn to 2mm, you write: 'Your brake pads are worn to a critical level — they should be replaced immediately. Driving with worn brake pads significantly increases stopping distance and can damage the brake rotors, turning a $180 brake job into a $500+ rotor replacement.' Always explain the consequence of deferred maintenance — not to scare, but to inform. Use the photo as evidence, not decoration. Your writing is clear, specific, and respects the customer's intelligence."

### Customization Variables
- Inspection checklist configuration per shop's SOPs and vehicle types serviced
- Urgency classification criteria per shop's service philosophy
- Cost and time estimation integration source
- Report visual template and branding per shop
- Customer authorization flow
- Technician incentive integration
- Fleet account report format

### Stickiness Factor
Shops that implement digital inspections see the revenue impact within 30 days — authorization rates on recommended services go up because customers can see the problem. When shop owners see a 25% increase in average repair orders, removing the tool is off the table. The shop management system integration and historical inspection database create deep operational roots.

### Upsell Path
Bundle with SKILL-074 (Diagnostic Pre-Assessment) for a complete customer vehicle intelligence experience. Upsell to a deferred service follow-up automation. Fleet accounts upsell to a Fleet Inspection Analytics Dashboard.

---

## SKILL-076: AI Trade-In Value Estimator Widget

**Category**: Widget/Tool
**Applies To**: Auto dealerships (new and used), car buying platforms, independent used car lots
**Deployment Platform**: Custom embeddable widget + VIN decoder API + KBB/NADA API + GHL
**Complexity**: Medium
**Monthly Value to Client**: $600 - $2,000

### What It Does
Embeds on a dealership's website and enables customers to enter their vehicle's VIN or year/make/model, mileage, and condition, and receive an estimated trade-in value range sourced from KBB Instant Cash Offer, NADA Guide, and Black Book — the same tools dealers use. Converts the "I wonder what my car is worth" moment into a lead capture opportunity, brings the customer to the dealership with realistic price expectations already set, and eliminates the awkward trade-in value anchor conversation that breaks deals.

### Core Capabilities
- VIN decode: automatic population of year, make, model, trim, engine, and standard features
- Condition assessment guided questionnaire: exterior, interior, mechanical condition, accident history
- Mileage input and deviation from average mileage scoring
- Generate value range from multiple sources: KBB, NADA, Black Book
- Display trade-in value range vs. private party sale value vs. dealership acquisition cost context
- Present immediate next step: "Get your exact offer in person" CTA with appointment booking
- Capture customer contact information and vehicle details for lead record
- Alert sales manager with lead details and estimated vehicle value immediately
- Log all trade-in estimates in GHL CRM and push to CRM/DMS

### Data Inputs Required
- VIN decoder API access
- KBB Instant Cash Offer API, NADA Guide API, or Black Book API credentials
- Dealership's acquisition value adjustments
- Customer contact capture fields
- DMS/CRM credentials for lead push (CDK, Reynolds & Reynolds, DealerSocket)
- Sales manager notification preferences

### Integration Points
- VIN decoder: NHTSA VIN API, or commercial VIN decoders (Edmunds, AutoVin)
- Valuation APIs: KBB ICO, NADA, Black Book (requires commercial licensing)
- DMS: CDK Global, Reynolds & Reynolds, DealerSocket, VinSolutions
- GHL CRM (lead capture and sales follow-up sequence)
- Dealership website (embeddable widget)
- Sales team notification: text/email alert with vehicle details
- Appointment scheduling for in-person appraisal

### Sample Prompt/Persona
> "You are a friendly trade-in advisor for [Dealership Name]. You're giving customers a straight, honest picture of what their vehicle is worth in today's market. Present the range clearly: 'Based on your [Year Make Model] with [mileage] miles in [condition] condition, current market values range from $X to $Y for a trade-in.' Explain the range honestly: 'The final number depends on a physical inspection — mileage, mechanical condition, and current market demand all factor in.' Always frame the in-person visit as the natural next step: 'We can give you an exact, no-obligation written offer when you come in — usually takes about 20 minutes.' Make it easy to book."

### Customization Variables
- Valuation source priority (KBB vs. NADA vs. Black Book)
- Acquisition value adjustment factors per dealership's current inventory needs
- Condition questionnaire depth
- Lead alert routing
- DMS integration target and lead field mapping
- Widget branding per dealership
- Value display format

### Stickiness Factor
Dealerships that deploy this widget generate trade-in leads with vehicle data already captured — the sales team's first conversation is about closing a deal, not re-collecting information. The DMS integration, once configured for CDK or Reynolds & Reynolds, becomes a foundational data pipeline. Internet sales managers who see trade-in leads generate higher gross profit per deal than cold internet leads build a commercial dependence on the tool's lead quality.

### Upsell Path
Pair with SKILL-077 (Recall & TSB Monitor) for a complete vehicle intelligence platform. Upsell to a complete digital retailing suite. High-volume dealership groups upsell to a centralized trade-in analytics platform.

---

## SKILL-077: AI Recall & TSB Monitor

**Category**: Workflow Automation / Operations
**Applies To**: Auto dealerships (franchise and independent), auto repair chains, fleet operators, vehicle subscription services
**Deployment Platform**: Custom (NHTSA API + ACES/LACES database) + GHL + Shop management system
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,500

### What It Does
Continuously monitors the NHTSA recall database and manufacturer Technical Service Bulletin (TSB) releases, automatically identifies which customers in the dealer's or shop's database own vehicles with open recalls or relevant TSBs, and triggers personalized outreach inviting them in for the repair — which for franchise dealers is a billable warranty repair paid by the manufacturer. Captures revenue from recall completions that would otherwise leave money on the table, while creating a genuine service touch that customers appreciate.

### Core Capabilities
- Monitor NHTSA recall database via API for new safety recall announcements
- Match new recalls against complete customer vehicle database (by VIN or year/make/model)
- Monitor manufacturer TSB databases (AllData, Mitchell Pro Demand) for applicable technical bulletins
- Distinguish between safety recalls (NHTSA mandatory) and service campaigns/TSBs
- Generate personalized customer outreach per recall: specific recall description in plain English, safety implications, no-cost repair offer
- Track recall completion status per VIN (open, appointment scheduled, completed)
- Generate parts order request for service department when recall campaign requires pre-order
- Provide recall completion report for OEM warranty reimbursement claim submission
- Track open recall percentage across entire customer vehicle database

### Data Inputs Required
- Customer database with VINs (or year/make/model/mileage records)
- Contact preferences per customer
- NHTSA recall API access (free, public API)
- TSB database access (requires AllData or Mitchell Pro Demand subscription)
- Shop management system access
- Dealer franchise codes (for OEM warranty reimbursement — franchise dealers only)

### Integration Points
- NHTSA Recalls API (free public API — new recalls checked daily)
- TSB databases: AllData, Mitchell Pro Demand, ALLDATA Repair
- Shop management systems: CDK, Reynolds, Tekmetric, Shop-Ware
- GHL CRM (customer outreach sequences and recall completion tracking)
- OEM warranty portals (for warranty claim submission documentation)
- SMS/email delivery for customer recall notifications
- Parts management system for pre-order triggering

### Sample Prompt/Persona
> "You are a vehicle safety coordinator for [Company Name]. When a recall affects one of our customers' vehicles, reach out immediately — this is both a safety matter and a service to them. Your message should be informative, not alarming: 'We noticed your [Year Make Model] VIN ending in [XXXX] is affected by a safety recall from [Manufacturer]. This is a no-cost repair — the manufacturer covers everything. We want to get this taken care of for you.' Explain what the recall involves in plain language, why it matters for safety, and how easy it is to address: 'It typically takes about [X hours] and you can wait in our lounge or we'll provide a loaner.' Make the appointment booking one-click simple."

### Customization Variables
- Recall monitoring scope: NHTSA only vs. NHTSA + manufacturer TSBs + service campaigns
- Customer matching logic: VIN-exact vs. year/make/model/trim range
- Alert thresholds: safety recall vs. TSB
- Outreach channel priority per customer preference
- Franchise dealer vs. independent shop configuration
- Parts pre-order trigger logic per recall type
- OEM warranty claim documentation format per manufacturer

### Stickiness Factor
For franchise dealers, recall completion is direct OEM reimbursement revenue. A dealer with 3,000 vehicles in their database and 15% recall rate has 450 vehicles generating potential warranty revenue — and this system captures it systematically. The VIN database match against NHTSA API runs continuously; once live, it is effectively a passive revenue generator that no dealer operations team would volunteer to shut down.

### Upsell Path
Bundle with SKILL-075 (Digital Vehicle Inspection Reporter) and SKILL-074 (Diagnostic Pre-Assessment) for a complete vehicle health and safety platform. Upsell to a vehicle ownership lifecycle management system. Fleet operators upsell to a fleet-wide compliance dashboard.

---

# RESTAURANT (078-080)

---

## SKILL-078: AI Phone Ordering Agent

**Category**: Voice Agent
**Applies To**: Quick service restaurants, fast-casual, pizza/delivery chains, family dining, ghost kitchens
**Deployment Platform**: Vapi + GHL + POS system integration + Delivery platform API
**Complexity**: High
**Monthly Value to Client**: $1,500 - $5,000

### What It Does
Answers 100% of inbound ordering calls with a natural, conversational AI voice agent that takes complete pickup and delivery orders — including all modifications, substitutions, and customizations — handles allergen inquiries, applies active promotions, and executes upsells. Orders are transmitted directly into the POS system for kitchen printing. Eliminates the #1 front-of-house time drain: phone order interruptions during peak service, and the missed calls during rush periods that translate directly to lost revenue.

### Core Capabilities
- Take complete orders for any menu item with full modification capability
- Handle complex customization trees (pizza builders, burrito bowls, combo meals with substitutions)
- Answer allergen inquiries for all major allergens (peanuts, tree nuts, dairy, gluten, shellfish, eggs, soy, sesame) per menu item
- Apply active promo codes and loyalty program credits
- Execute contextual upsells: "Would you like to add a [recommended side/drink/dessert] to that?"
- Calculate order total with tax, delivery fee, and tip prompt
- Confirm complete order with read-back before finalizing
- Transmit order directly to POS system for kitchen print (no re-entry required)
- Send order confirmation with estimated ready/delivery time via SMS
- Handle order modifications and cancellations within the POS window

### Data Inputs Required
- Complete menu with all items, modifiers, prices, and availability status
- Allergen matrix per menu item
- Active promotions and discount codes
- Loyalty program integration details
- POS system API credentials for order transmission
- Delivery zones and fee schedule (for delivery orders)
- Estimated prep time by order type

### Integration Points
- POS systems: Toast, Square for Restaurants, Aloha, Micros Oracle, Clover (order transmission)
- Delivery platforms: DoorDash Drive, Uber Eats API
- Loyalty platforms: Paytronix, LevelUp, Square Loyalty
- GHL CRM (customer order history, preference tracking)
- Vapi (the voice conversation layer)
- SMS confirmation delivery
- Kitchen display systems (KDS)

### Sample Prompt/Persona
> "You are the friendly phone order specialist for [Restaurant Name]. You know this menu inside and out. When a customer calls, greet them warmly and dive right into helping them order — they're hungry and usually in a hurry. Confirm every modification clearly as you take it. When you ask for upsells, make them specific and appealing: 'Our house-made lemonade pairs really well with that — would you like to add one?' If someone mentions an allergy, take it seriously and confirm which items on their order are safe. Read back the complete order before confirming. Always end with a clear ETA: 'Your order will be ready in about [X] minutes. See you then!'"

### Customization Variables
- Menu configuration (full menu import from POS or manual input)
- Modifier tree logic per menu category
- Allergen matrix per menu item (confirmed by kitchen management, not assumed)
- Upsell script and recommended pairings per main item category
- Promotion and discount code database
- Voice personality: casual and fun vs. professional and efficient
- Background noise handling threshold
- Order confirmation read-back speed and format

### Stickiness Factor
Restaurants that deploy this during dinner rush immediately free up the entire front-of-house staff from phone interruptions. A restaurant taking 40 phone orders per day that takes 2.5 minutes per call recovers 100 minutes of staff time every day. The POS integration, once configured and tested for accurate order transmission, becomes mission-critical infrastructure.

### Upsell Path
Bundle with SKILL-079 (Reservation & Waitlist Manager) for a complete restaurant phone management platform. Upsell to a caller loyalty recognition feature that identifies returning customers by phone number, greets them by name, and offers to reorder their usual. High-volume restaurant groups upsell to a multi-location order management dashboard.

---

## SKILL-079: AI Reservation & Waitlist Manager

**Category**: Chat Agent / Voice Agent / Workflow Automation
**Applies To**: Full-service restaurants, fine dining, bars with table service, event dining venues
**Deployment Platform**: Vapi + GHL + OpenTable/Resy/SevenRooms integration + Custom SMS flow
**Complexity**: Medium
**Monthly Value to Client**: $800 - $2,500

### What It Does
Handles all reservation requests and waitlist management via phone, SMS, and web widget — booking tables for the appropriate party size and time, managing the real-time waitlist during peak periods, sending automated confirmation and reminder messages, collecting dietary restrictions and special occasion notes, and processing cancellations with automated table release. Eliminates the constant phone interruption of reservation management during service and ensures the host stand has complete, organized reservation data before each shift.

### Core Capabilities
- Accept and book reservation requests by phone (Vapi voice) or SMS/chat (text-based)
- Check real-time availability against reservation management system
- Collect complete reservation details: party size, date, time, special occasion, dietary restrictions, seating preferences
- Manage waitlist during full-house periods: add to list, quote estimated wait times, notify when table is ready
- Send automated confirmation immediately upon booking
- Send reminder notifications: 24-hour reminder and 2-hour day-of reminder with "confirm your reservation" CTA
- Process cancellations and immediately release table back to available inventory
- Flag large party bookings (6+) for host manager review and special seating notes
- Collect deposit authorization for high-demand dates (holidays, special events)
- Generate shift reservation report for host stand pre-service briefing

### Data Inputs Required
- Reservation management system access: OpenTable, Resy, SevenRooms, Tock
- Floor plan and table capacity configuration
- Reservation windows and party size limits per table type
- Cancellation policy and deposit requirements for special dates
- Special occasion and dietary restriction fields
- Shift schedule (when dining room is open, seating windows)
- Host team notification preferences for special requests

### Integration Points
- Reservation platforms: OpenTable API, Resy API, SevenRooms, Tock (bidirectional sync)
- Vapi (voice reservation requests and waitlist calls)
- GHL CRM (guest profile with visit history, preferences, notes)
- SMS delivery (confirmation, reminder, waitlist notification)
- Google Business Profile messaging (reservation requests via Google)
- Email (confirmation and special event booking details)
- Payment processors for deposit collection on special dates

### Sample Prompt/Persona
> "You are the warm, organized reservation coordinator for [Restaurant Name]. You represent the first impression of our hospitality. When guests call or text for a reservation, be welcoming and efficient — they're planning a meal they're looking forward to. Collect all the details naturally: 'Are you celebrating anything special? Any dietary restrictions or allergies I should note for your server?' Confirm every reservation clearly with the full details. During busy periods, when no tables are immediately available, offer the waitlist with an honest estimate — never promise a time you can't deliver. Always end with excitement about their upcoming visit: 'We look forward to having you with us!'"

### Customization Variables
- Reservation platform integration target
- Party size thresholds for special handling
- Cancellation policy language and deposit requirements per date tier
- Waitlist wait time estimation logic
- Reminder timing and content
- Special occasion recognition and upsell (flowers, cake, private dining rooms)
- Voice personality per restaurant brand identity

### Stickiness Factor
Host stands that use this system arrive at every shift with a complete, digital, organized reservation sheet with special notes already populated. The 24-hour confirmation reminders reduce no-show rates by 20–30% — a measurable revenue impact in fine dining. Once integrated with OpenTable or SevenRooms, the guest profile database accumulates visit history and preferences that make every returning guest experience personalized and memorable.

### Upsell Path
Bundle with SKILL-078 (Phone Ordering Agent) for a complete AI restaurant phone system. Upsell to a guest experience analytics platform. Special event venues upsell to a complete private dining sales and management system.

---

## SKILL-080: AI Inventory Forecasting Agent

**Category**: Analytics / Operations
**Applies To**: Full-service and fast-casual restaurants, catering companies, ghost kitchens, food service groups
**Deployment Platform**: Custom (ML forecasting model) + POS data integration + GHL + Make/Zapier
**Complexity**: High
**Monthly Value to Client**: $1,000 - $4,000

### What It Does
Analyzes historical POS sales data combined with external signals — day of week patterns, local weather forecasts, upcoming events (sports games, concerts, holidays, school calendars), and seasonal demand curves — to predict ingredient needs for each upcoming service period with 85–92% accuracy. Generates daily and weekly prep lists by menu item and corresponding ingredient purchase orders to the appropriate vendors. Reduces food waste (the average restaurant wastes 10% of purchased food) and eliminates stock-out situations that lead to 86'd menu items, disappointed guests, and lost revenue.

### Core Capabilities
- Ingest historical POS sales data by menu item, day, day-part, and season (minimum 90 days for baseline)
- Incorporate weather forecast API data (precipitation, temperature, and conditions affect cover count)
- Pull local events calendar (sports, concerts, festivals, conventions) for demand spike prediction
- Apply day-of-week and seasonal demand patterns to base prediction
- Account for menu engineering changes (new items, removed items, limited-time offers)
- Generate item-level cover count predictions for the next 7 days by day-part
- Calculate ingredient quantities required per predicted cover count using recipe database
- Compare predicted need vs. current on-hand inventory to generate order quantities
- Create formatted purchase orders per vendor with item quantities and delivery timing
- Generate prep list by station (cold prep, hot prep, bakery, butchery) for each service shift

### Data Inputs Required
- Historical POS data: minimum 90 days of daily sales by menu item (ideally 12+ months)
- Current recipe database: ingredient quantities per menu item and batch recipe
- Current on-hand inventory levels (manual input or integrated with inventory management platform)
- Vendor catalog with item codes and pack sizes
- Delivery schedule per vendor
- Local events calendar (manual input or integrated events API)
- Weather API integration for service area
- Lead time per ingredient category

### Integration Points
- POS systems: Toast, Square, Aloha, Micros, NCR Aloha (historical and live sales data)
- Inventory management platforms: MarketMan, BlueCart, xtraCHEF by Toast, Crunchtime, Compeat
- Weather APIs: Tomorrow.io, Weather.com API
- Local events APIs: SeatGeek, Eventbrite, Ticketmaster
- Vendor ordering portals: Sysco, US Foods, Restaurant Depot — order submission via EDI or portal
- GHL CRM (alerts, reporting, and management notifications)
- Kitchen display systems (for prep list distribution)

### Sample Prompt/Persona
> "You are a data-driven kitchen operations analyst. Your job is to make sure the restaurant never runs out of anything they need and never over-orders anything they don't. Analyze this week's upcoming demand signals: the historical Tuesday pattern, the rain forecast Wednesday evening, and the major concert Thursday night that typically boosts covers by 40%. Build the prep and order recommendations from the ground up. For each ingredient, show your math: predicted covers × recipe quantity = total need, minus on-hand = order quantity. Flag any items where your confidence interval is wide — the chef should know when you're less certain. Always round to the nearest vendor pack size."

### Customization Variables
- Forecasting model training period and refresh frequency
- Recipe database import format (JSON, CSV, or integration with recipe management platform)
- Vendor catalog and ordering schedule per vendor
- Event calendar data sources (manual curation vs. automated API)
- Weather sensitivity by restaurant concept
- Prep list format per kitchen station configuration
- Waste tracking integration (actual vs. predicted variance logging for model improvement)
- Alert threshold for high-confidence demand spikes (notify chef/GM proactively)

### Stickiness Factor
Restaurants that achieve 15–20% food waste reduction see $30,000–$80,000 in annual cost savings for a mid-volume operation. That ROI is directly measurable on the P&L. The forecasting model improves continuously as it trains on more venue-specific data — after 6 months, the model's accuracy for that specific restaurant's patterns is significantly better than a generic tool, creating a data asset that cannot be instantly replicated elsewhere. The vendor ordering integration, once established, becomes the kitchen's procurement backbone.

### Upsell Path
Bundle with SKILL-078 (Phone Ordering Agent) and SKILL-079 (Reservation Manager) for a complete restaurant operations platform. Upsell to a menu engineering analytics module that pairs demand forecasting with item-level profitability analysis. Multi-location restaurant groups upsell to a centralized procurement platform that aggregates purchase orders across locations for volume buying and vendor contract negotiation leverage.

---

*End of Batch 2: Industry-Specific Skills Group A (041-080)*
*Total Skills: 40 | Industries: 7 | Estimated Combined Monthly Client Value: $32,000 – $113,500*
