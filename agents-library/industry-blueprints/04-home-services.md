# Home Services — AI Agent Ecosystem Blueprint
## (HVAC · Plumbing · Electrical · General Contracting)

---

## Industry Overview

Home services is a $600B+ fragmented market dominated by small and mid-sized operators who compete on speed, trust, and availability. AI adoption is accelerating rapidly, driven by the persistent labor shortage, rising customer expectations for instant digital interaction, and the operational chaos of managing field technicians, parts logistics, and unpredictable demand spikes. The industry's core pain points — missed calls, poor scheduling, inconsistent pricing, no-show techs, forgotten follow-ups, and reactive (rather than proactive) maintenance — are precisely the problems AI agents solve best.

**Key AI Adoption Drivers:**
- 62% of home service calls go unanswered during peak periods
- Average job ticket can increase 30–40% with systematic upsell and cross-sell workflows
- Service agreement (membership plan) recurring revenue transforms cash-flow volatility
- Seasonal demand swings create workforce and dispatch inefficiencies that AI optimizes
- Customers increasingly expect same-day booking, photo documentation, and digital communication

**Competitive Landscape:** ServiceTitan, Jobber, Housecall Pro, and FieldEdge lead in software. AI agent layers differentiate operators by reducing human labor at the front office, increasing field tech productivity, and capturing revenue that currently leaks through manual processes.

---

## Sub-Agents Breakdown

### 1. Emergency Dispatch Voice Agent
- **Type**: Voice (Inbound — 24/7)
- **Function**: Answers all inbound calls after hours and during overflow. Opens with dynamic triage — "Is this an emergency?" → branches into "Is your basement flooding right now?" / "Do you smell gas?" / "Is your heat out in freezing weather?" Classifies as Emergency (dispatch on-call tech within 60 minutes), Urgent (schedule within 4 hours), or Standard (book next available slot). Captures full customer name, address, callback number, and issue description. Sends confirmation SMS with ETA and tech name. Pages on-call dispatcher for true emergencies.
- **Trigger**: Inbound call to main business number after hours, weekend, or when all reps are occupied
- **Integrations**: ServiceTitan / Jobber / Housecall Pro (job creation), Twilio (SMS), Google Maps (ETA calculation), on-call rotation schedule, PagerDuty or Slack (emergency alerts)
- **Sticky Factor**: Owners who experience zero missed emergency calls never go back to voicemail. Emergency response is the highest-value interaction in home services — capturing it builds irreplaceable trust.
- **Implementation Notes**: Requires dynamic call routing rules by time-of-day and day-of-week. Emergency classification logic must account for safety-critical scenarios (gas leak, carbon monoxide, no heat below 40°F). Voice agent should confirm address against existing customer database and auto-populate job record. Escalation path to live human on-call dispatcher must be seamless (warm transfer or immediate page).

---

### 2. AI-Powered Job Estimator Widget
- **Type**: Widget (Web / SMS / Chat)
- **Function**: Embedded on company website and landing pages. Customer selects trade (HVAC, plumbing, electrical, general), describes their issue via text or voice input, and optionally uploads 1–3 photos. AI analyzes input + photos using computer vision to identify the likely issue, severity, and scope. Returns a branded estimate range (e.g., "$180–$320 for a toilet flapper + fill valve replacement") along with a call-to-action to book. Collects contact info before showing estimate — generates lead automatically in CRM.
- **Trigger**: Website visit, paid ad landing page, QR code on truck or door hanger, SMS keyword campaign
- **Integrations**: OpenAI Vision API (photo analysis), ServiceTitan/Jobber CRM (lead capture), Google Analytics (conversion tracking), Stripe (deposit collection optional), Calendly or native scheduling (booking)
- **Sticky Factor**: Businesses that add this widget see 3–5x higher website-to-booking conversion. Customers who self-qualify via the estimator have higher intent and lower cancellation rates. The data generated trains the model to give more accurate local estimates over time.
- **Implementation Notes**: Estimate ranges should pull from the company's actual flat-rate price book, not generic data. Computer vision analysis of uploaded photos should flag: visible damage, age indicators, code violations, and upsell opportunities (e.g., corroded connections that suggest broader inspection). Widget must be mobile-optimized — 70%+ of home service searches happen on mobile.

---

### 3. Smart Dispatch & Route Optimizer
- **Type**: Workflow / Dashboard
- **Function**: Continuously monitors all open jobs, technician GPS locations, skill certifications, truck parts inventory, job priority, and customer time-window commitments. Automatically assigns and re-assigns jobs to optimize for: drive time minimization, first-call completion rate (matching tech skills + parts to job requirements), SLA compliance (emergency jobs within promised window), and tech utilization rate. Sends real-time updated routes to techs via mobile app. Handles dynamic re-routing when jobs overrun or new emergencies are added.
- **Trigger**: New job booking, job status change, tech check-in/check-out, emergency addition, tech delay detected (GPS shows tech will miss window)
- **Integrations**: ServiceTitan Dispatch Board / Jobber, Google Maps / Waze API (live traffic), parts inventory database, tech certification records, GPS fleet tracking (Verizon Connect, FleetComplete, or Samsara)
- **Sticky Factor**: Operators who run optimized dispatch achieve 15–25% more completed jobs per day per tech. Once the system learns patterns (which techs work fastest on which job types, which neighborhoods have parking issues), it becomes difficult to replicate with manual dispatch.
- **Implementation Notes**: Machine learning layer should improve route quality over time by analyzing historical job durations vs. estimates. Must handle multi-tech jobs (large HVAC installs) where two techs must arrive simultaneously. Priority queue logic: Emergency → Same-day urgent → Time-committed standard → Flexible. Integration with parts inventory is critical — assign a job to a tech only if the required parts are on their truck or can be grabbed from a nearby supply house en route.

---

### 4. Seasonal Maintenance Campaign Agent
- **Type**: Workflow / Outbound Voice + SMS + Email
- **Function**: Monitors calendar and weather forecasts to trigger proactive outreach campaigns at optimal times. Spring: contacts all AC-service customers from prior year for tune-up bookings. Fall: targets all furnace/heat pump customers. Personalizes message with equipment age, last service date, and a limited-time offer. Runs automated multi-touch sequences: email day 1, SMS day 3, voice call day 7 if no response. Stops sequence the moment customer books. Books appointments directly into the schedule without human intervention.
- **Trigger**: Calendar date (e.g., March 1 for AC season, September 15 for heating season), or weather trigger (first day with forecast high > 80°F; first 5-day stretch with lows below 45°F)
- **Integrations**: Weather API (OpenWeatherMap, Tomorrow.io), CRM for customer segmentation, Twilio (SMS + voice), SendGrid (email), ServiceTitan/Jobber (appointment booking), review platform (include seasonal review request)
- **Sticky Factor**: Clients who run these campaigns book 40–60% of their seasonal capacity before competitors even start marketing. The system converts one-time repair customers into recurring maintenance customers — dramatically increasing lifetime value.
- **Implementation Notes**: Segment customers by equipment type, age of equipment, and service history. Equipment 8+ years old should receive messaging about replacement consideration alongside tune-up offer. Include referral ask in sequence for customers who had positive prior experiences. A/B test subject lines and message copy to optimize open and conversion rates. Comply with TCPA for SMS and voice autodialers.

---

### 5. Parts Inventory Manager
- **Type**: Workflow / Background Agent
- **Function**: Maintains a live count of all parts across all service trucks and the central warehouse. Tracks consumption rate per part by job type and season. Automatically generates purchase orders when any SKU hits its reorder threshold. Alerts dispatchers when a tech's truck is short on a critical part needed for their next job — triggering a supply-house stop or warehouse pickup. Provides weekly inventory valuation reports and identifies slow-moving parts.
- **Trigger**: Part consumed on a job (tech marks parts used in mobile app), part count manually updated, weekly audit cycle
- **Integrations**: ServiceTitan / Jobber (parts tracking), QuickBooks / NetSuite (PO and AP integration), supplier EDI feeds (Ferguson Enterprises, Wesco, Grainger, Johnstone Supply), barcode/QR scanner on mobile app
- **Sticky Factor**: Inventory intelligence eliminates "truck stock" guesswork that plagues small operators. First-call completion rates rise significantly when techs consistently have the right parts. Owners who see the financial impact of reduced emergency supply-house runs never want to manage inventory manually again.
- **Implementation Notes**: Each truck should have a defined "standard stock" list; the system flags deviations. Track supplier lead times to dynamically adjust reorder points during supply chain disruptions. Generate per-truck inventory cost reports to help operators decide whether to add a supply-house account. Integrate with supplier punch-out catalogs for one-click PO generation.

---

### 6. Customer History Lookup Agent
- **Type**: Voice / Chat (Inbound + Field Tech Mobile)
- **Function**: When a customer calls or a tech is en route to a job, this agent instantly surfaces the complete property profile: all past service records, installed equipment (make, model, serial number, install date), past repair history, notes from prior techs, permit history, any open issues flagged on previous visits, and current service agreement status. Tech-facing view also shows photos from prior visits. Office staff view shows payment history, preferred communication method, and lifetime value.
- **Trigger**: Inbound call (CLI/ANI match to customer record), tech job assignment (auto-push to mobile app), manual name/address search
- **Integrations**: CRM (ServiceTitan, Jobber, Housecall Pro), Google Street View (property context), equipment registration databases (for warranty lookup), document storage (job photos, permits)
- **Sticky Factor**: Techs who arrive knowing a home's history perform faster, upsell more effectively, and receive higher satisfaction ratings. Customers notice when a tech already knows their equipment — it creates differentiated trust in a low-trust industry.
- **Implementation Notes**: Build a structured "Equipment Registry" schema for each property: trade type, manufacturer, model, serial, install date, warranty expiration, capacity/specs. Auto-populate from photos and manufacturer databases where possible. Flag equipment approaching end-of-life (10+ years for HVAC, 12+ for water heaters) as upsell opportunities during every interaction.

---

### 7. Permit & Inspection Coordinator
- **Type**: Workflow / Background Agent
- **Function**: Tracks all jobs that require permits (electrical panel upgrades, HVAC replacements, water heater installations, gas line work). Automatically determines permit requirements based on job type and municipality. Submits permit applications via e-permit portals where available. Tracks permit status. Schedules required inspections with the municipality. Sends reminders to the appropriate tech/project manager. Stores all permit documentation in the job record and customer file.
- **Trigger**: Job created with permit-required trade type, job status changes to "completed — awaiting inspection," permit expiration approaching
- **Integrations**: Municipal e-permit portals (CivicPlus, EnerGov, ViewPoint Cloud), ServiceTitan/Jobber job records, document management system, tech mobile app (inspection notification)
- **Sticky Factor**: Permit compliance is a significant liability for contractors. Companies that automate this never miss an inspection, never let a permit lapse, and have complete documentation for insurance and re-sale purposes. This agent is a risk management tool owners deeply value.
- **Implementation Notes**: Each municipality has different requirements — maintain a lookup table by ZIP code or city. Some municipalities don't have online portals and require phone or in-person application; agent should flag these for human follow-up. Store all final inspection sign-offs as PDFs in the customer record for future home sale due diligence. Alert owner if any permit is approaching 6-month or 12-month expiration without a final inspection.

---

### 8. Service Agreement / Membership Manager
- **Type**: Voice / Chat / Workflow
- **Function**: Presents, enrolls, and manages recurring maintenance plan memberships. Proactively offers membership to first-time repair customers post-job ("Would you like to protect your investment with our $19.99/month plan?"). Tracks all active memberships, renewal dates, and included services remaining per period. Sends renewal reminders 30/14/7 days before expiration. Automatically schedules included tune-up visits. Processes payments via card on file. Identifies at-risk members (those who haven't used their benefits) and sends re-engagement nudges.
- **Trigger**: Job completion (new enrollment offer), renewal date approach, unused benefit detected, payment failure
- **Integrations**: CRM (membership status), Stripe / Square (recurring billing), ServiceTitan Agreements module, SMS/email automation, accounting system
- **Sticky Factor**: Membership revenue is the highest-value recurring revenue in home services — typical plans retain customers at 85%+ annual rates, and members spend 2–3x more annually than non-members. Every enrolled customer reduces churn risk dramatically.
- **Implementation Notes**: Structure tiers: Basic (annual tune-up + priority scheduling), Standard (2 tune-ups + 10% parts discount + no diagnostic fee), Premium (quarterly visits + 15% discount + free service calls). Agent must handle billing failures gracefully — automatic retry sequence, then SMS/email to update payment method before membership lapses. Track membership attachment rate per tech as a KPI.

---

### 9. Post-Job Review & Upsell Agent
- **Type**: Outbound Voice / SMS / Email (Automated)
- **Function**: Fires 2–4 hours after job completion. Sends personalized thank-you with tech's name, job summary, and a direct link to leave a Google / Yelp review. If customer clicks "thumbs down" or rates less than 4 stars, immediately escalates to the owner/manager for service recovery — never pushes the unhappy customer to a public review. Simultaneously triggers a relevant upsell recommendation based on the completed job (e.g., after AC tune-up → "Your air handler is 11 years old — here's what a replacement would cost"). Tracks review conversion rate by tech.
- **Trigger**: Job marked "Complete" in field app
- **Integrations**: ServiceTitan/Jobber (job completion webhook), Twilio (SMS), SendGrid (email), Google Business Profile API (review link), Yelp API, owner alert system (Slack/email for escalations)
- **Sticky Factor**: Companies running this system generate 5–15x more Google reviews than competitors, which drives organic lead generation at near-zero cost. The review velocity advantage compounds over time and is nearly impossible to close without the same automated system.
- **Implementation Notes**: Personalize message with tech's first name and one specific detail from the job. A/B test timing — 2 hours vs. 4 hours vs. next morning. Filter out commercial/contractor customers from consumer review requests. Ensure CANSPAM and TCPA compliance. Include unsubscribe option. Track: review request send rate, click rate, review submission rate, average rating per tech.

---

### 10. Financing Qualification Bot
- **Type**: Chat / Web Widget / In-Field Mobile
- **Function**: Presented to customers when job estimate exceeds $1,500 (configurable threshold). Explains available financing options (GreenSky, EnerBank, Service Finance Company, Synchrony). Collects customer name, DOB, last 4 SSN, and income info via secure form. Submits to financing partners for soft credit pull. Returns approval decision and available credit within 60 seconds. Tech or office staff can present monthly payment options. For declined applicants, offers secondary financing options (lease-to-own) and generates follow-up sequence.
- **Trigger**: Job estimate created above threshold, tech flags financing conversation on job record, customer explicitly asks about payment plans
- **Integrations**: GreenSky API, EnerBank API, Service Finance Company API, Synchrony Home API (HVAC), CRM (document financing offer + outcome), DocuSign (finance agreement e-signature)
- **Sticky Factor**: Operators offering in-the-moment financing close large jobs that competitors lose because competitors say "let me get back to you with financing info." The difference between a $12,000 HVAC replacement job closed vs. lost often comes down to whether financing is offered at point of diagnosis.
- **Implementation Notes**: Obtain required financing partner agreements and training certifications. Soft pull does not affect credit score — communicate this clearly to customers. Collect proper disclosures and consent language. For states with additional consumer lending disclosure requirements (CA, NY, etc.), embed compliance language directly in the bot flow.

---

### 11. Energy Audit Calculator Widget
- **Type**: Widget (Web + Landing Page)
- **Function**: Customers input home details: square footage, year built, insulation rating, current energy bills (monthly average), existing HVAC equipment age, number of windows, geographic climate zone. AI calculates an estimated energy efficiency score and generates a prioritized recommendation list: "Upgrading to a 20 SEER2 variable-speed heat pump could reduce your cooling costs by 38%." Each recommendation links to a service or product the company offers. Captures lead contact info at the end.
- **Trigger**: Organic website visit, paid search landing page (targeted on "high energy bills," "HVAC efficiency"), QR code during in-home consultation
- **Integrations**: Energy Star API / ENERGY STAR savings estimator data, CRM (lead capture), utility rate databases by ZIP code, ServiceTitan (create opportunity from lead)
- **Sticky Factor**: Positions the company as a trusted energy advisor, not just a repair shop. Customers who go through this process have far higher intent for major upgrades. Also qualifies customers for utility rebates and tax credits (IRA Section 25C, 25D), which creates additional urgency.
- **Implementation Notes**: Include current federal and state incentive data — IRA heat pump tax credits (up to $2,000), utility rebate lookups by ZIP. Update rebate data quarterly. Widget should be embeddable via JavaScript snippet. Store all audit results and contact info in CRM with lead source tracking.

---

### 12. Warranty Tracker
- **Type**: Background Agent + Customer-Facing Portal
- **Function**: Maintains a database of all equipment installed and serviced by the company (and imported from service history). Tracks manufacturer warranty terms (parts only, parts + labor, extended warranty if purchased). Sends automated alerts to customers when warranties are within 90/30 days of expiration — with an offer to purchase an extended service plan or schedule a pre-warranty-expiration diagnostic visit. Alerts service staff when a job should be warranty-covered (prevents billing errors). Flags equipment under active recall.
- **Trigger**: Equipment warranty expiration date approach, new equipment installation recorded, recall database update
- **Integrations**: Manufacturer warranty databases (carrier, Trane, Rheem, Lennox, etc. via API or web data), CRM equipment registry, CPSC recall database API, SMS/email notification system
- **Sticky Factor**: No competitor manually tracks warranty status for customers. This is a pure value-add that drives loyalty and prevents the worst customer experience in home services — a customer being billed for something that was under warranty.
- **Implementation Notes**: Seed database with manufacturer standard warranty terms for top 50 equipment brands. Allow manual override for extended warranties purchased at installation. Build a simple customer-facing portal (accessible via texted link) where customers can see all their equipment warranties in one place — this alone generates significant goodwill.

---

### 13. Subcontractor Coordination Agent
- **Type**: Workflow / Project Management
- **Function**: Built for general contractors managing multiple trades on renovation, build-out, or remediation projects. Maintains a roster of approved subcontractors (HVAC, plumbing, electrical, drywall, flooring) with their license numbers, insurance certificates (expiration tracking), W-9s, and availability. Auto-assigns subs to projects based on availability, project location, and past performance ratings. Sends scoped work orders via email/text, collects acceptance confirmations, and tracks milestone completion.
- **Trigger**: New project created requiring multiple trades, subcontractor milestone due date approaching, insurance certificate expiration within 30 days
- **Integrations**: Procore / Buildertrend (project management), DocuSign (subcontract execution), QuickBooks (sub payment tracking), COI tracking database, email/SMS for communications
- **Sticky Factor**: GCs managing 5+ simultaneous projects cannot track sub coordination manually without errors. This agent eliminates lien risk from uninsured subs, reduces project delays from missed assignments, and creates a compliance audit trail.
- **Implementation Notes**: Enforce insurance compliance gate — no work order issued to a sub whose general liability or workers comp has expired. Generate automatic COI renewal requests to subs 60 days before expiration. Track sub performance scores (on-time rate, callback rate, safety record) to prioritize top performers for future assignments.

---

### 14. Weather-Triggered Campaign Agent
- **Type**: Outbound Workflow (SMS + Email + Voice)
- **Function**: Monitors weather forecasts for the company's service territory in real time. Triggers targeted campaigns based on conditions: Severe storm alert → "Storm prep" outreach to customers with aging equipment; Extended cold snap → "Emergency heating readiness" to customers with older furnaces; Heat wave forecast → "AC check-up" to customers without recent tune-ups; First hard freeze → "Pipe protection" to all plumbing customers. Campaigns are automatically drafted, personalized, and launched within 30 minutes of weather trigger.
- **Trigger**: Weather API threshold breach (temperature, storm severity, precipitation type, freeze warning, high wind advisory)
- **Integrations**: Tomorrow.io / OpenWeatherMap API (forecast alerts by ZIP), CRM (customer segmentation by trade, equipment type, last service date), Twilio (SMS + voice), SendGrid (email), ServiceTitan/Jobber (booking links in messages)
- **Sticky Factor**: Weather-triggered campaigns convert at 3–5x the rate of generic seasonal campaigns because they are hyper-relevant and time-sensitive. Clients who experience even one major storm-season booking surge from automated campaigns will invest in this permanently.
- **Implementation Notes**: Set geographic weather zones matching service territory. Configure thresholds carefully — trigger too often and customers unsubscribe; too conservatively and opportunities are missed. Include opt-out management compliant with TCPA. Pre-draft campaign templates for each weather scenario; agent customizes with customer-specific details before sending.

---

### 15. Photo Documentation Agent
- **Type**: Mobile Workflow (Field Tech-Facing)
- **Function**: Tech receives a structured photo checklist for each job type before arriving on site (e.g., for HVAC maintenance: "Photograph the equipment label, the air filter, the condenser coil condition, the electrical connections, the refrigerant gauge readings"). Photos are automatically uploaded, tagged with job ID, timestamp, and GPS location, and stored in the job record. AI analyzes photos to: (a) validate job completion per company standards, (b) auto-detect upsell conditions (dirty coils, aging components), (c) generate a professional customer-facing service report with annotated images.
- **Trigger**: Tech checks in to job in mobile app, job type determines photo checklist, job checkout triggers report generation
- **Integrations**: ServiceTitan / Jobber mobile app (photo upload), OpenAI Vision API (photo analysis), PDF report generator, CRM (store report), SMS/email (send report to customer)
- **Sticky Factor**: Creates accountability for techs, legal protection for the company, and a premium customer experience. Customers who receive an annotated photo report after service are significantly more likely to trust recommendations and book follow-up work. Companies that implement this report almost zero billing disputes.
- **Implementation Notes**: Auto-generate a branded PDF service report within minutes of job completion. Report should include: tech name + photo, equipment info, work performed, annotated before/after photos, any recommendations with estimated costs. This doubles as marketing collateral — customers share these with neighbors and on neighborhood apps.

---

### 16. Flat-Rate Pricing Lookup
- **Type**: Voice / Chat (Internal — Office + Field)
- **Function**: Serves as a real-time pricing reference for office staff quoting over the phone and for techs presenting prices in the field. Staff describe the job in natural language ("replacing a 40-gallon gas water heater, customer wants a Bradford White, standard installation, first floor utility room") and the agent returns the flat-rate price from the company's pricing matrix, including parts and labor, with any applicable membership discount applied. Ensures every customer gets the same price for the same job regardless of which rep or tech they interact with.
- **Trigger**: Office rep receives pricing inquiry call, tech needs to present estimate in the field, manager auditing quote consistency
- **Integrations**: Company flat-rate price book (ServiceTitan Pricebook, Profit Rhino, Callahan-Roach price book), CRM (log quote), membership status lookup, parts cost database
- **Sticky Factor**: Price consistency is a persistent problem for growing home services companies. Once the pricing lookup is embedded in every customer interaction, inconsistent pricing complaints disappear. Operators who have experienced the reputational and margin damage of ad-hoc pricing never return to manual quoting.
- **Implementation Notes**: Price book must be maintained and updated at least quarterly. AI should surface the top 3 "good/better/best" options for every job category (e.g., builder grade vs. mid-tier vs. premium equipment at different price points). Log every quote with customer ID and timestamp for audit trail and conversion tracking.

---

### 17. New Construction Bid Agent
- **Type**: Workflow / Document Processing
- **Function**: Designed for HVAC, plumbing, and electrical contractors pursuing new construction work with builders. Takes builder specification documents (PDF plans, spec sheets, RFQ documents) as input. Extracts key project parameters: square footage, number of units, mechanical room layout, equipment specifications required. Cross-references company cost database and current material prices to generate a preliminary bid within 24 hours. Flags non-standard specifications requiring engineer review. Produces formatted bid document with company letterhead.
- **Trigger**: New RFQ or plan set uploaded to company inbox or bid portal, new builder contact added to CRM
- **Integrations**: Blueprint/plan parsing (Bluebeam, PlanSwift, or PDF extraction), material cost databases (RSMeans, vendor price feeds), QuickBooks (labor cost rates), DocuSign (bid submission), BuilderTrend / Procore (bid management portals)
- **Sticky Factor**: Small HVAC/plumbing contractors miss or underbid new construction opportunities because takeoff and bidding is time-intensive. An AI that turns around accurate bids in hours instead of days wins contract opportunities that competitors don't even respond to in time.
- **Implementation Notes**: Maintain a database of won vs. lost bids with actual job cost vs. estimated cost for continuous learning. Flag bids where material costs have increased significantly since the price book was last updated. Include escalation clauses for long-duration projects in bid language.

---

### 18. Code Compliance Checker
- **Type**: Workflow / Reference Agent (Internal)
- **Function**: Allows techs and project managers to query current applicable codes for any planned installation or repair. "Can I install a tankless water heater in a closet in Texas without a combustion air modification?" → Returns Texas plumbing code, local amendment status, and best-practice guidance. Tracks when local jurisdictions adopt new code cycles (NEC 2023, UPC 2021, IMC 2021) and alerts staff to changes that affect common work types. Generates a pre-job code checklist for complex projects.
- **Trigger**: Pre-job planning query, permit application initiation, post-job inspection prep
- **Integrations**: ICC code library, NFPA 70 (NEC), local amendment databases by jurisdiction, company knowledge base, permit checklist templates
- **Sticky Factor**: Code violations are expensive — failed inspections, required rework, potential license jeopardy. Companies that systematically check compliance before starting work have near-zero inspection failure rates. This agent protects the contractor's license and reputation.
- **Implementation Notes**: Maintain a jurisdiction lookup table with current code cycle adoption status. Include common local amendments that override national codes (many jurisdictions run a code cycle behind). Allow techs to submit questions conversationally — return plain-language answers, not raw code text, with code citations for documentation.

---

## Industry-Specific Intake Forms

### Residential Service Call Intake
- Full name, service address, billing address (if different)
- Phone (cell preferred for SMS), email
- Type of service needed (HVAC / Plumbing / Electrical / Other)
- Equipment brand, model, approximate age (if known)
- Describe the problem (free text + optional photo upload)
- Emergency or standard service?
- Preferred appointment window
- How did you hear about us?
- Active membership / service agreement? (auto-lookup by phone/address)
- Access instructions (gate code, dog in yard, key in lockbox, etc.)

### New Customer Property Setup
- Property type (single-family, condo, rental, commercial)
- Year built
- Square footage (for HVAC sizing reference)
- Number of HVAC systems, water heaters, electrical panels (quantity + approximate age)
- Previous service provider (for competitive intelligence)
- Preferred contact method and best times to reach
- Credit card on file authorization (for membership or emergency dispatch)

### Service Agreement Enrollment
- Coverage tier selection (Basic / Standard / Premium)
- Equipment to be covered (each unit individually)
- Primary and backup contact info
- Billing preferences (monthly vs. annual, card vs. ACH)
- Desired tune-up season preference (spring / fall / both)
- Any known existing issues to note before enrollment

### General Contracting / Commercial Project Intake
- Project type (new construction / renovation / emergency repair / tenant buildout)
- Property address and type
- Project scope description
- Estimated project start date and completion requirement
- Permit requirement acknowledgment
- Preferred trades needed
- Point of contact (property owner vs. property manager vs. GC vs. tenant)
- Budget range (for financing and resource planning)

---

## Interactive Widgets & Tools

| Widget | Purpose | Lead Capture | Conversion Role |
|---|---|---|---|
| Job Estimator | Customer describes issue → ballpark price range | Yes — email + phone before reveal | High-intent lead gen |
| Energy Audit Calculator | Home details → efficiency score + upgrade recommendations | Yes | Educational + upsell |
| Membership Savings Calculator | Current spend on repairs → projected savings with plan | Yes | Membership conversion |
| Maintenance Reminder Signup | Customer enters equipment, gets reminder schedule | Yes | Long-term engagement |
| Permit Requirement Checker | Job type + ZIP → permit required? Cost? Timeline? | Optional | Trust + compliance |
| Financing Pre-Qualifier | Job amount → monthly payment options | Yes | Big-ticket conversion |
| Online Booking Widget | Real-time availability + instant booking | Yes | Appointment conversion |
| Review Portal | Single link → platform selection + review flow | No | Reputation management |
| Referral Program Widget | Unique link generation + reward tracking | Yes | Word-of-mouth growth |
| Technician Tracker | Real-time tech location + ETA | No | Customer experience |

---

## Employee Role Mapping

| Role | Primary AI Agents Used | Key Benefit |
|---|---|---|
| Owner / GM | Revenue dashboard, Campaign performance, Dispatch analytics | Strategic visibility without daily management |
| Dispatcher | Smart Dispatch Optimizer, Emergency Triage output, Inventory alerts | 30–50% more jobs dispatched per day |
| Office / CSR | Customer History Lookup, Pricing Lookup, Appointment booking | Faster, more confident customer interactions |
| Field Technician | Photo Documentation, Customer History, Parts Alerts, Compliance Checker | More productive visits, higher ticket averages |
| Sales / Estimator | Job Estimator Widget, Financing Bot, New Construction Bid Agent | Faster quotes, higher close rates |
| Service Manager | Membership Manager, Post-Job Review tracking, Tech performance | KPI visibility, quality control |
| Accounts Payable | Parts Inventory PO generation, Subcontractor payment tracking | Reduced administrative burden |

---

## Integration Architecture

```
INBOUND CHANNELS
├── Phone (Twilio / RingCentral) → Emergency Dispatch Voice Agent
├── Website Widget → Job Estimator / Booking / Energy Audit
├── SMS (Twilio) → Appointment confirmations, Tech ETA, Review requests
└── Email (SendGrid) → Campaigns, Reports, Confirmations

CORE PLATFORM (Field Service Management)
├── ServiceTitan / Jobber / Housecall Pro
│   ├── Customer & job records
│   ├── Dispatch board
│   ├── Pricebook
│   └── Reporting
└── QuickBooks / Xero (Accounting sync)

AI AGENT LAYER
├── LLM Core (GPT-4o / Claude 3.5 Sonnet)
├── Voice (ElevenLabs TTS + Whisper STT)
├── Computer Vision (OpenAI Vision API)
└── Workflow Orchestration (Make.com / n8n / custom)

THIRD-PARTY INTEGRATIONS
├── Financing: GreenSky, EnerBank, Service Finance
├── Parts/Inventory: Ferguson, Johnstone, Grainger EDI
├── Mapping/GPS: Google Maps API, Samsara Fleet
├── Weather: Tomorrow.io API
├── Reviews: Google Business Profile API, Yelp Fusion
├── E-Permits: Municipal portals by jurisdiction
├── Documents: DocuSign, Google Drive / SharePoint
└── Payments: Stripe, Square
```

---

## Competitive Intelligence

**What top operators are doing:**
- National brands (One Hour, Benjamin Franklin, Mr. Electric) run centralized AI dispatch and overflow call centers — independents can match this capability with AI agents at a fraction of the cost
- ServiceTitan's AI features (scheduling pro, marketing pro) are improving but require add-on fees — a well-configured agent layer provides more customization
- Amazon Home Services and Angi/HomeAdvisor lose to local operators on trust and personal service — AI agents amplify the "local expert" advantage with 24/7 availability
- Private equity rollups (Wrench Group, BELFOR) are investing heavily in AI operational efficiency — independents must automate or face margin compression

**Differentiation Opportunities for Independent Operators:**
- Hyper-local knowledge (specific neighborhoods, older home quirks, local permit nuances)
- Faster response to AI-generated leads than national operators
- Relationship continuity (same tech, personalized history) enhanced by AI memory
- Custom service agreement products vs. standardized national plan offerings

---

## Revenue Model

| Revenue Stream | AI Agent Enablement | Estimated Impact |
|---|---|---|
| Emergency / After-Hours Jobs | Emergency Dispatch Voice Agent | Capture 100% of after-hours calls (vs. ~30% with voicemail) |
| Service Agreement ARR | Membership Manager + Post-Job Upsell | 2–4x membership enrollment rate |
| Large Job Close Rate | Financing Bot + Estimator Widget | 20–35% increase on jobs >$2,000 |
| Seasonal Campaign Revenue | Seasonal + Weather Campaign Agents | 40–60% of seasonal capacity booked proactively |
| Google Review Velocity | Post-Job Review Agent | 5–15x more reviews → lower CPL on paid search |
| New Construction Pipeline | Bid Agent | Enter new revenue channel without adding estimator headcount |
| Parts Margin | Inventory Manager | 5–10% reduction in emergency procurement cost |
| Referral Revenue | Post-Job Referral Nudge | 15–25% of new customers from AI-prompted referrals |

---

## Stickiest Features (Top 5)

### 1. Emergency Dispatch Voice Agent (24/7)
The moment a business owner experiences zero missed emergency calls — and sees the revenue from jobs that would have gone to voicemail — this becomes non-negotiable infrastructure. Emergency jobs carry the highest ticket values and the highest customer lifetime value conversion rates.

### 2. Smart Dispatch & Route Optimizer
Once optimized dispatch is running, reverting to manual dispatch feels like going back to a paper map. The compounding efficiency gains (more jobs per day, fewer parts-related rollbacks, higher first-call completion) make this the highest operational ROI agent in the ecosystem.

### 3. Service Agreement / Membership Manager
Membership ARR fundamentally changes a home services business's financial stability. Owners who build recurring revenue through AI-automated enrollment and renewal management are building an asset, not just a job shop. This is the feature most closely tied to business valuation.

### 4. Post-Job Review Agent
Google review volume drives organic search rankings, which directly reduces paid advertising spend. Companies that build a 200-review lead over competitors through automated review capture enjoy a sustained cost-per-lead advantage that takes years for competitors to close.

### 5. Customer History Lookup + Equipment Registry
The full property intelligence profile — surfaced automatically at every touchpoint — creates a customer experience that feels premium and personal. Customers who feel "known" by their service provider churn at dramatically lower rates and refer more frequently.
