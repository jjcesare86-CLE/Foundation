# Roofing & Solar — AI Agent Ecosystem Blueprint

## Industry Overview

Roofing and solar are capital-intensive, project-based industries with high average ticket values, complex insurance and permit workflows, and a competitive landscape shaped heavily by storm events, energy prices, and federal incentive legislation. Roofing generates ~$56B annually in the U.S.; residential solar installations add another $30B+ and are growing 20%+ YoY driven by IRA incentives. Both verticals share overlapping operational challenges: estimating complexity, subcontractor management, permit bureaucracy, homeowner education requirements, and post-installation accountability. AI creates compounding value across the full project lifecycle — from weather-triggered lead capture through long-term monitoring and maintenance.

**Market Context:**
- Average residential roofing job: $9,000–$22,000
- Average solar installation: $18,000–$35,000 (before incentives); net ~$12,000–$22,000 after ITC
- Insurance-driven roofing (storm damage): 40–60% of residential revenue in hail-prone markets
- Solar sales cycle: 30–90 days (significantly shortened by AI-assisted education and financing pre-qualification)
- Biggest pain points: storm chasing inefficiency, permit delays, insurance adjuster disputes, crew scheduling complexity, homeowner anxiety during project, warranty management fragmentation

**AI Opportunity Score: 9.5/10** — Storm-triggered demand spikes, complex multi-stakeholder communication flows, measurement and estimation intelligence, and long-term monitoring requirements make this industry exceptionally well-suited for AI agent infrastructure.

---

## Sub-Agents Breakdown

### 1. Storm Damage Lead Capture Agent
- **Type**: Workflow / Outbound Voice & SMS / Marketing Automation
- **Function**: Monitors weather data feeds (NOAA, Verisk Atmospheric Hazards) for hail, high wind, and severe storm events by geographic area. When a storm exceeds threshold severity (e.g., hail > 1 inch diameter) in a defined service territory, automatically triggers: outbound SMS/email campaigns to existing customers and prospect lists in affected ZIP codes, activation of targeted paid ad campaigns (Google, Meta) with storm-specific creative, and door-hanger list generation for canvassing crews. Captures inbound leads from all channels into CRM with storm event attribution.
- **Trigger**: Weather API event: hail > 0.75", wind > 60mph, tornado in county, or manual storm event trigger by sales manager
- **Integrations**: NOAA Weather API / Tomorrow.io / Verisk, Meta Ads API, Google Ads API, Twilio (SMS outbound), Mailchimp / Klaviyo, CRM (HubSpot / Salesforce), canvassing app (CompanyCam, Spotio)
- **Sticky Factor**: Storm-response speed is the #1 variable in insurance-driven roofing revenue. Operators who are first on-site post-storm win the job 70%+ of the time. This agent delivers systematic first-mover advantage that becomes a core competitive moat.
- **Implementation Notes**: Build geographic storm event logging to prevent duplicate campaigns to same ZIP in same event. Integrate storm severity scoring to tier campaign intensity. Require compliance review for state-specific solicitation laws (post-disaster solicitation is regulated in TX, CO, FL, IL).

### 2. AI Roof Inspection Report Generator
- **Type**: Workflow / AI Vision Processing
- **Function**: Accepts drone footage or high-resolution aerial photos (from in-house drone, EagleView, Nearmap) and runs them through a computer vision model trained to identify and annotate: missing/lifted shingles, hail impact patterns, granule loss, ridge cap damage, flashing failures, soffit/fascia damage, and ponding water areas (flat roofs). Generates a branded PDF inspection report with annotated photos, damage severity scoring, repair vs. replacement recommendation, and estimated scope summary. Report is delivered to homeowner and/or insurance adjuster within minutes of photo upload.
- **Trigger**: Drone flight completion (photo upload), manual photo upload by inspector, EagleView/Nearmap API delivery, or customer self-service photo upload request
- **Integrations**: EagleView API / Nearmap API / Hover API, OpenAI Vision / Google Vertex AI (vision model), CompanyCam (photo management), PDF generation (PDFKit / WeasyPrint), SendGrid (delivery), CRM (report attachment to contact record)
- **Sticky Factor**: Insurance adjusters and homeowners share and reference these AI reports. The branded report becomes a trust anchor in the claims process. Operators who produce them win insurance approvals faster and close jobs at higher rates — creating measurable, auditable ROI.
- **Implementation Notes**: Train vision model on region-specific damage patterns (hail impact looks different on 3-tab vs. architectural shingles; flat EPDM damage looks different from TPO). Include confidence scoring on each damage annotation — low-confidence areas flagged for human inspector review. Must meet insurer acceptable-evidence standards in target markets.

### 3. Insurance Claim Assistance Agent
- **Type**: Chat / Voice / Document Workflow
- **Function**: Guides homeowners through the entire insurance claim lifecycle: (1) Explains the claim process in plain language, (2) Helps document all visible damage with photo prompts, (3) Prepares a pre-claim damage summary document for the homeowner to share with their insurer, (4) Schedules adjuster meeting and reminds homeowner to request contractor presence, (5) Reviews adjuster's estimate for scope gaps and prepares a supplemental claim request if warranted, (6) Drafts escalation letters for denied or underpaid claims. Maintains a conversation history that serves as a running claim file.
- **Trigger**: Customer confirms storm damage or interest in insurance claim; adjuster meeting scheduled; adjuster estimate received (uploaded to portal)
- **Integrations**: Xactimate (supplemental estimate parsing), CompanyCam (damage documentation), DocuSign (authorization to represent), CRM (claim stage tracking), email/SMS (homeowner communication), Eagleview (supporting evidence)
- **Sticky Factor**: Homeowners who experience guided claims assistance close at 85%+ rates vs. 45–55% for self-managed claims. The agent becomes the homeowner's primary support system during a stressful process — deep emotional lock-in accompanies the transactional dependency.
- **Implementation Notes**: Must include strong disclaimers: agent provides claim preparation assistance, not legal or public adjuster services. Review public adjuster licensing requirements by state before enabling supplemental claim drafting. Store all claim communications for potential dispute resolution.

### 4. Financing Qualification Agent
- **Type**: Chat / Web Widget
- **Function**: Conducts a soft pre-qualification for roofing and solar financing within 60 seconds — without a hard credit pull. Asks: homeowner status, estimated credit range, annual income range, loan amount needed, and property state. Matches against available financing programs: GreenSky, Mosaic, Sunlight Financial, Synchrony, or operator's private financing. Returns: likely approval status, estimated rate range, monthly payment examples at different terms, and a pre-application link to the best-fit lender. For solar: overlays with ITC/state incentive credits to show net financed amount.
- **Trigger**: Estimate delivered (automatic follow-up), customer asks about financing, "Can I finance this?" chat inquiry, or estimate page CTA click
- **Integrations**: GreenSky API / Mosaic API / Sunlight Financial API, Synchrony (roofing financing), CRM (financing stage tracking), solar savings calculator output (for net amount calculation), Twilio (follow-up reminders)
- **Sticky Factor**: Financing pre-qualification dramatically increases close rates for $15,000+ projects where sticker shock is a primary objection. Operators whose sales process includes instant financing options are materially more competitive. The agent becomes essential to revenue conversion.
- **Implementation Notes**: Never make credit approval guarantees — use "likely to qualify" language. Ensure RESPA/TILA compliance for disclosures. Store financing inquiry data only as needed for pre-qualification — do not retain SSN or sensitive data at rest without proper security controls.

### 5. Solar Savings Calculator Widget
- **Type**: Interactive Web Widget / Chat
- **Function**: The most powerful top-of-funnel solar tool. Customer enters their address and monthly electric bill. Agent retrieves: roof orientation and pitch from satellite data, local solar irradiance (peak sun hours), utility rate and escalator (from EIA data), local and federal incentives (ITC 30%, state rebates, SREC prices). Outputs a personalized solar analysis: estimated system size, panel count, year-1 production, 25-year savings projection, payback period, and IRR. Includes side-by-side financing scenarios (cash, loan, lease/PPA). One-click CTA: "Get My Free Custom Quote."
- **Trigger**: Homepage CTA click, Google Ads landing page, utility bill upload prompt, or chat inquiry about solar costs
- **Integrations**: Google Solar API / Aurora Solar / OpenSolar (irradiance and roof data), EIA Electricity Rates API, DSIRE (Database of State Incentives for Renewables), NREL PVWatts, financing partner APIs (monthly payment calculations), CRM (lead capture on quote request)
- **Sticky Factor**: This widget is the most-shared lead generation tool in solar — homeowners text/email the link to neighbors and family. It also anchors the sales conversation with personalized data, making it the reference point for all subsequent discussions. Competitors cannot duplicate the widget's personalization without rebuilding the entire data integration stack.
- **Implementation Notes**: Satellite roof data lookup can fail for properties with obstructed imagery — build fallback to manual address entry with estimated irradiance by ZIP. Clearly disclose that results are estimates. Update incentive database quarterly as state programs change. Must be mobile-first: 65%+ of widget completions come from mobile devices.

### 6. Permit & HOA Application Agent
- **Type**: Workflow / Document Automation
- **Function**: After a roofing or solar contract is signed, automatically prepares the full permit package: pulls property details from county parcel data, generates required drawings and specifications from project data, populates municipal permit forms, tracks submission status with the AHJ (Authority Having Jurisdiction), and sends status updates to the homeowner and PM. For solar: also manages HOA submissions — generates HOA application, tracks approval timeline, drafts appeal letters for rejections. Alerts team when permits are approved and ready for scheduling.
- **Trigger**: Contract signed (DocuSign webhook), permit package ready for submission, AHJ status change, HOA decision received
- **Integrations**: Municipal permit portals (via web automation or API where available), HOA management platforms (AppFolio, Vantaca), DocuSign (contract data extraction), Aurora Solar / EagleView (system drawings), Smartsheet / Procore (project management), Twilio (homeowner status updates)
- **Sticky Factor**: Permit management is universally loathed by operators — delays are costly and tracking is fragmented. Operators who solve permit tracking dependency will not voluntarily return to manual spreadsheet management. The agent also reduces project delays that directly impact revenue recognition timing.
- **Implementation Notes**: Permit requirements vary dramatically by jurisdiction (some require wet-stamped engineering, others accept e-signatures). Build a jurisdiction library with form templates and requirements indexed by county/city. For jurisdictions without online portals, generate completed PDF packets for manual submission with submission reminders.

### 7. Material Estimation Agent
- **Type**: Workflow / Chat / Dashboard
- **Function**: From aerial measurement data (EagleView, Hover, or manual pitch/plane measurements), automatically calculates: total roofing squares, waste factor by roof complexity (10–15% simple, 20–30%+ complex), starter strip linear footage, ridge cap linear footage, drip edge, ice and water shield, underlayment, flashings, and fastener quantities. For solar: calculates panel layout, mounting hardware quantities, conduit runs, and inverter sizing. Generates a complete material order list with current pricing from preferred suppliers and total material cost.
- **Trigger**: Measurement report received from EagleView/Hover, manual measurements entered, or estimator-initiated from project record
- **Integrations**: EagleView API / Hover API, ABC Supply / SRS Distribution / Beacon Roofing Supply (pricing APIs), QuickBooks / Xero (cost tracking), proposal generation tool (JobNimbus, AccuLynx), Aurora Solar (solar BOM)
- **Sticky Factor**: Accurate material takeoffs prevent both costly underorders (project delays) and expensive overorders (margin leakage). Once an operator experiences accurate, automated takeoffs, manual estimation becomes unacceptable. The agent also builds a historical materials database used for margin analytics.
- **Implementation Notes**: Build waste factor rules by roof geometry: hip vs. gable vs. complex cut-up roofs require different waste percentages. Support multiple manufacturer product lines — Owens Corning, GAF, CertainTeed — with different product dimensions affecting quantity calculations. Generate both homeowner-facing estimate summary and internal material order list as separate outputs.

### 8. Subcontractor & Crew Scheduling Agent
- **Type**: Workflow / Dashboard
- **Function**: Manages the complexity of mixed in-house and subcontractor crews for roofing projects. Matches job requirements (roof size, complexity, material type, height, required certifications) to available crew capacity. Checks weather forecast before scheduling — automatically bumps jobs when rain is forecast. Manages subcontractor certificates of insurance and license expiration dates. Sends job packets (address, scope, material delivery ETA, customer contact, site notes) to crew leads the day before. Tracks crew check-in and completion.
- **Trigger**: Project approved for scheduling, contract signed, permit approved (if required), weather change affecting scheduled jobs, crew cancellation
- **Integrations**: Weather API (7-day forecast for scheduling), Procore / BuilderTrend / AccuLynx (project management), subcontractor management platform, Twilio (crew notifications), Google Calendar / Outlook (scheduling), CompanyCam (crew check-in/photo)
- **Sticky Factor**: Weather-aware scheduling alone generates measurable value — rain cancellations cost operators $800–$2,500 in crew mobilization waste per incident. Operators in weather-volatile markets (Midwest, Southeast) become deeply dependent on automated weather-rescheduling.
- **Implementation Notes**: Build a subcontractor compliance database: track license, insurance (general liability + workers comp), and background check status. Hard-block scheduling assignments for non-compliant subs. For solar crews, also track NABCEP certification status.

### 9. Project Milestone Communication Agent
- **Type**: Workflow / Automated Notifications
- **Function**: Keeps homeowners proactively informed at every project milestone, eliminating "where are we?" inbound calls that consume PM time. Standard milestone sequence: Contract Signed → Permit Submitted → Permit Approved → Materials Ordered → Materials Delivery Confirmed → Crew Assigned → Start Date Confirmed (48hr notice) → Day-of Arrival Notification → Project In Progress (mid-day photo update) → Project Complete (completion summary with photos) → Final Inspection Scheduled → Warranty Registered. Each message is personalized with project details.
- **Trigger**: CRM/project management system status change at each milestone; material delivery confirmation; crew check-in; project completion; inspection scheduled
- **Integrations**: AccuLynx / JobNimbus / Procore (project status webhooks), CompanyCam (photo delivery), Twilio (SMS), SendGrid (email), DocuSign (completion certificate delivery)
- **Sticky Factor**: Homeowner anxiety during a major home improvement project is the #1 driver of negative reviews and disputes. Proactive communication reduces complaints by 60–80%. Operators addicted to positive reviews and low dispute rates cannot remove this agent without immediate review score decline.
- **Implementation Notes**: Allow homeowners to set preferred communication channel and frequency. Build message suppression rules (no 6am "crew is on the way" texts). Include photo links in milestone updates — visual confirmation dramatically improves homeowner satisfaction scores. Detect homeowner replies and route to PM immediately.

### 10. Warranty Registration & Tracking Agent
- **Type**: Workflow / Document Management
- **Function**: Upon project completion, automatically registers manufacturer warranties for all installed products (shingles, underlayment, solar panels, inverters, racking). Tracks both manufacturer and labor warranty terms, start dates, and expiration dates. Stores all warranty documentation in a homeowner-accessible portal. Sends homeowner warranty reminders at 30-day and 1-year marks. Generates warranty transfer documentation when homeowner sells the home. Alerts operations team when warranty claims are filed.
- **Trigger**: Project completion and final payment, homeowner warranty inquiry, warranty expiration approaching (12-month alert), home sale transfer request, manufacturer warranty claim notification
- **Integrations**: GAF/Owens Corning/CertainTeed warranty portals (API registration where available), Enphase / SolarEdge / SMA manufacturer portals (solar warranties), DocuSign (warranty documents), customer portal (document access), CRM (warranty record)
- **Sticky Factor**: Transferable roof and solar warranties are significant home value assets — homeowners actively maintain access to warranty documentation through the portal. The agent also reduces warranty claim disputes by maintaining irrefutable installation documentation.
- **Implementation Notes**: Manufacturer warranty registration requirements vary significantly — some require contractor ID verification, others allow batch upload. Build a warranty compliance tracker that flags projects where warranty registration was not completed within required timeframe (some manufacturers require within 30 days of installation). Solar panel warranties (product: 25yr, performance: 25yr, inverter: 10–25yr) must be tracked separately.

### 11. Aerial Measurement Integration Agent
- **Type**: Workflow / API Integration
- **Function**: Serves as the central hub for all aerial measurement data. On demand (or automatically at lead qualification), orders measurements from EagleView, Hover, or Nearmap for a given property address. Normalizes measurement data into a standardized format regardless of source. Feeds measurements directly into the estimate generation workflow, material calculation agent, and proposal tools. Tracks measurement order status and notifies estimator when results arrive. Maintains historical measurement archive by property address.
- **Trigger**: Estimator request, contract signed (for final measurements), lead qualification with property address confirmed, storm event (batch measurement orders for affected areas)
- **Integrations**: EagleView API, Hover API, Nearmap API, JobNimbus / AccuLynx (measurement attachment to estimate), material estimation agent (auto-feed), proposal tool (auto-populate)
- **Sticky Factor**: The speed of going from address to accurate estimate (minutes vs. hours with manual measurement) changes how an operator competes — faster quotes close at higher rates. This speed advantage is impossible to maintain manually at scale.
- **Implementation Notes**: Build cost management controls — aerial measurements cost $15–$50 each. Implement auto-order rules (only order for leads above certain qualification score) and batch ordering for storm events (bulk pricing negotiation). Track measurement spend as a line item in sales cost-per-lead calculation.

### 12. Energy Incentive & Rebate Finder
- **Type**: Chat / Widget / Workflow
- **Function**: For solar prospects, automatically searches and compiles all applicable incentives at the federal, state, utility, and local government levels: Federal Investment Tax Credit (30% through 2032 under IRA), state income tax credits, utility rebate programs, SREC/REC markets, property tax exemptions, sales tax exemptions, PACE financing programs, and low-income targeted incentives (IRA 10–20% adders). Presents a personalized incentive summary with estimated dollar values and application instructions. Updates automatically when incentive programs change or expire.
- **Trigger**: Solar estimate requested, solar savings calculator completed, customer asks about incentives/tax credits, annual incentive database update
- **Integrations**: DSIRE API (dsireusa.org), IRS guidance library, utility rate database (OpenEI), NREL APIs, state energy office APIs, CRM (incentive summary attached to lead record)
- **Sticky Factor**: For many homeowners, the incentive stack is the decisive factor in purchasing solar. Operators who present the most comprehensive and accurate incentive analysis win the deal — this agent is a direct sales conversion tool. It also positions the operator as the most knowledgeable in the market.
- **Implementation Notes**: Always date-stamp incentive summaries and include disclaimer about consulting a tax professional for ITC claims. DSIRE database updates quarterly — build automated sync. Track incentive values separately from system cost in all customer-facing documents to maintain transparency and FTC compliance.

### 13. Customer Referral Agent
- **Type**: Workflow / Automated Messaging / Canvassing Support
- **Function**: After project completion and positive review confirmation, activates a neighborhood referral strategy: sends homeowner a referral kit (unique link, door-hanger digital template with homeowner's name as referral source, social share messages). Leverages the natural "neighbors watch the truck in the driveway" phenomenon — the agent generates a canvassing list of adjacent addresses for sales reps. Tracks referral conversions, calculates referral bonus earned, and triggers bonus fulfillment ($250–$500 typical for roofing, $500–$1,000 for solar referral).
- **Trigger**: Job completion + 5-star review (or positive QC score), referred customer submits inquiry, referred customer signs contract
- **Integrations**: CRM (referral attribution), ReferralHero / Friendbuy / custom tracking, canvassing app (Spotio / SalesRabbit) for neighborhood canvass list generation, Twilio (SMS referral kit delivery), gift card fulfillment API (Tremendous, Tango)
- **Sticky Factor**: In storm markets, one completed job can generate 3–5 neighborhood leads if the referral agent executes the neighborhood follow-up. Operators in dense suburban markets see 25–40% of new jobs from referral — a revenue stream entirely owned by this agent.
- **Implementation Notes**: Comply with state solicitation laws — some states (Colorado, Illinois) restrict in-person solicitation following storm events. Build canvass radius logic that respects these restrictions. Require explicit homeowner opt-in before using their name in neighborhood canvassing materials.

### 14. Before/During/After Photo Documentation Agent
- **Type**: Mobile Workflow / AI-Powered Organization
- **Function**: Enforces a standardized visual project documentation protocol. Before: roof deck exposure, existing damage evidence, underlayment condition, flashings, penetrations. During: decking repairs, ice and water shield installation, new underlayment, product installation progress. After: completed field, ridge cap, flashings, gutters, cleanup verification. AI automatically organizes photos by project phase, generates a timestamped visual timeline, and delivers a branded project portfolio to the homeowner. Photos are also stored for insurance documentation, warranty evidence, and marketing portfolio use.
- **Trigger**: Crew check-in (before photos unlock job start), phase completions, crew check-out (after photos required for job closeout), quality inspection, homeowner portfolio request
- **Integrations**: CompanyCam (primary photo management for roofing), Jobber / AccuLynx (photo attachment to job record), AWS S3 (storage), SendGrid (homeowner delivery), website CMS (portfolio gallery population), insurance documentation workflow
- **Sticky Factor**: Homeowners who receive a professional photo documentation package share it socially — free marketing. The documentation also serves as legal protection against false damage claims. Operators who provide this level of transparency win referrals from architect and real estate professional networks.
- **Implementation Notes**: CompanyCam is the de facto standard for roofing photo documentation — build native integration rather than custom photo management. Set minimum photo counts per phase — if crew attempts to check out without minimum photos, block job completion. Include GPS coordinates and timestamp embedded in photo metadata for insurance admissibility.

### 15. Post-Installation Solar Monitoring Agent
- **Type**: Dashboard / Automated Alerts / Proactive Outreach
- **Function**: Monitors solar system production data from connected inverters (Enphase, SolarEdge, SMA, Fronius) and alerts homeowners and service teams when: production falls below expected output by >10% for >3 days, individual panel underperformance detected (microinverter systems), grid connectivity lost, inverter error codes generated, or battery state of charge is abnormal. Generates monthly production reports with utility bill savings calculations. Proactively contacts homeowners approaching warranty milestones or showing performance degradation.
- **Trigger**: Daily production data sync (inverter API), alert threshold breach, monthly reporting cycle, warranty milestone, homeowner inquiry about system performance
- **Integrations**: Enphase API / SolarEdge API / SMA API / Fronius API, utility data (Green Button API for bill comparison), CRM (service request creation on alert), Twilio (alert notifications), email reporting (SendGrid), service scheduling agent (auto-schedule maintenance visit on persistent alerts)
- **Sticky Factor**: Solar system owners who receive proactive monitoring reports form a permanent service relationship — they will not switch to a competitor who offers no monitoring, especially as systems age. This agent creates a 25-year recurring touchpoint with every solar customer.
- **Implementation Notes**: Different inverter brands have different API latency (Enphase updates every 5 min; SolarEdge every 15 min; some string inverters daily). Build alert logic that accounts for weather-related production drops (don't alert during extended cloudy periods). Store lifetime production data — it is critical for warranty claims and system resale documentation.

### 16. Review Generation & Reputation Management Agent
- **Type**: Workflow / Automated Messaging
- **Function**: At project completion (confirmed by final payment and/or completion certificate), sends personalized review request directing satisfied customers to Google Business Profile (primary), Houzz, Yelp, Angi, BBB, or solar-specific platforms (EnergySage, SolarReviews). Monitors all review platforms for new reviews — alerts team immediately for negative reviews and provides a response draft within minutes. Tracks review count, average rating, and review velocity by platform on a reputation dashboard. Identifies patterns in negative feedback for operational improvement.
- **Trigger**: Project completion and final payment confirmed, QC satisfaction score of 4+/5, new review detected on monitored platforms, negative review detected (any score < 4)
- **Integrations**: Google Business Profile API, Yelp Fusion API, Houzz API, Angi/HomeAdvisor API, EnergySage / SolarReviews (solar-specific), Twilio (SMS request), SendGrid (email request), reputation monitoring aggregator (Birdeye, Podium, NiceJob)
- **Sticky Factor**: Online reviews directly drive organic lead generation — Google 4.8-star operators with 200+ reviews spend 40–60% less on paid leads than 4.2-star operators. The agent creates a compounding organic lead asset with measurable dollar value. Operators who have relied on this system for 12+ months cannot walk away from the review velocity without seeing immediate lead cost increases.
- **Implementation Notes**: Filter out 3-star-or-below customers from review requests — address issues directly first. Respond to all reviews (positive and negative) within 24 hours — agent drafts responses for human approval. Monitor for fake reviews from competitors (pattern: multiple 1-star reviews from new accounts in a short window) and generate dispute documentation for Google.

### 17. Commercial Bid Agent
- **Type**: Workflow / Chat / Document Generation
- **Function**: Handles the complexity of commercial roofing proposals for flat/low-slope systems (TPO, EPDM, modified bitumen, SPF, metal). Ingests: building specifications, existing roof system documentation, roof access constraints, occupancy considerations (operating business below), phased work requirements, and bid specification documents. Generates a complete commercial proposal: scope of work, material specifications with manufacturer options, warranty tier comparison, work schedule (nighttime/weekend requirements), safety plan summary, and pricing. Supports multi-contractor bidding management for GC relationships.
- **Trigger**: Commercial RFQ/RFP received (email or portal), GC bid invitation, commercial property manager inquiry, maintenance contract renewal
- **Integrations**: Procore / Plangrid (commercial construction), Carlisle / GAF Commercial / Firestone (TPO/EPDM product systems and specs), Dodge Data & Analytics (commercial project data), Smartsheet (bid tracking), DocuSign (proposal delivery), AIA contract forms library
- **Sticky Factor**: Commercial roofing bids are complex and time-consuming — operators who can respond to RFPs in 24–48 hours vs. the industry norm of 5–7 days win a disproportionate share of commercial work. GCs who experience fast, professional bid responses become loyal referral sources.
- **Implementation Notes**: Commercial roofing requires understanding of OSHA fall protection requirements, specific manufacturer technical requirements for warranty eligibility, and local building code energy compliance (ASHRAE 90.1). Build a compliance checklist into the bid generation workflow. Support LEED documentation requirements for projects pursuing green building certification.

---

## Industry-Specific Intake Forms

### Residential Roofing Intake
- Property address (enables aerial measurement auto-order)
- Roof age and last replacement date
- Current roofing material type
- Nature of issue: storm damage / leak / end-of-life / visual concern
- Date of storm event (if applicable)
- Insurance carrier and claim already filed? (Y/N)
- Number of stories; access considerations
- Attic space accessible (for deck inspection)
- HOA membership (affects material/color choices)
- Preferred start window and budget range
- How did you hear about us

### Residential Solar Intake
- Property address + ownership status (owner required)
- Average monthly electric bill ($)
- Utility provider
- Roof age and material type
- Shading concerns (large trees, neighboring buildings)
- Primary motivation: savings / environmental / energy independence / backup power
- Battery storage interest (Y/N)
- EV ownership / future EV plans
- Credit range estimate (soft pre-qual)
- HOA membership
- Timeline to decision

### Commercial Roofing Intake
- Property address and building type
- Roof area (sq ft) — estimated or available drawings
- Current roof system type and age
- Reason for project: emergency repair / preventive maintenance / full replacement / new construction
- Current lease status (owned vs. tenant-occupied)
- Access constraints: working business below / HVAC equipment / safety requirements
- Required work hours (daytime / nighttime / weekend)
- Bid deadline
- Decision-maker name and title
- Existing warranty information

---

## Interactive Widgets & Tools

| Widget | Description | Placement |
|---|---|---|
| **Solar Savings Calculator** | Address + electric bill → full 25-year savings model with financing scenarios | Solar landing page, paid ad destinations |
| **Storm Damage Self-Assessment Tool** | Guided photo checklist → insurance claim worthiness score | Post-storm SMS campaigns, homepage |
| **Instant Roof Quote Widget** | Address → aerial measurement → estimate range in 60 seconds | Homepage, Google LSA landing page |
| **Financing Payment Calculator** | Project amount → monthly payment scenarios across 5/10/15/20yr terms | Estimate delivery page, proposal |
| **Material Visualizer** | Roof photo + shingle/color selector → rendered preview of finished roof | Estimate page, showroom kiosk |
| **HOA Approval Checker** | HOA name → approved solar/roofing material list lookup | Solar proposal, intake form |
| **Permit Status Tracker** | Customer portal → live permit status with expected approval date | Post-contract homeowner portal |
| **Solar Production Dashboard** | Live system output, monthly savings, CO2 offset, lifetime generation | Post-installation homeowner app |
| **Warranty Vault** | All product and labor warranties in one downloadable, transferable document set | Customer portal |

---

## Employee Role Mapping

| Role | Agents Used Daily | Time Saved/Week |
|---|---|---|
| **Storm Chaser / Canvasser** | Storm Lead Capture, Referral Agent (neighborhood list) | 5–8 hrs (auto-campaign) |
| **Estimator / Sales Rep** | Aerial Measurement, Material Estimation, Financing Qualification, Solar Calculator | 12–18 hrs |
| **Project Manager** | Milestone Communication, Permit Agent, Crew Scheduling, Warranty Registration | 15–20 hrs |
| **Insurance Coordinator** | Insurance Claim Agent, Inspection Report Generator, Measurement Agent | 10–15 hrs |
| **Operations Manager** | Crew Scheduling, QC/Review Agent, Photo Documentation | 8–12 hrs |
| **Commercial Sales Rep** | Commercial Bid Agent, Measurement Agent, Incentive Finder | 10–15 hrs |
| **Service Technician** | Solar Monitoring Agent (alert response), Photo Documentation | 3–5 hrs |
| **Marketing Manager** | Storm Campaign Agent, Review/Reputation Agent, Referral Agent | 8–10 hrs |

---

## Integration Architecture

```
Core Project Management (AccuLynx / JobNimbus / Procore)
    ├── Lead Capture Layer
    │     ├── Storm Lead Capture Agent (weather triggers)
    │     ├── Solar Calculator Widget (organic capture)
    │     └── Financing Pre-Qualification Agent (conversion)
    ├── Estimation Layer
    │     ├── Aerial Measurement Agent (EagleView/Hover)
    │     ├── AI Inspection Report Generator (drone/aerial vision)
    │     ├── Material Estimation Agent (BOM generation)
    │     └── Commercial Bid Agent (RFP response)
    ├── Project Execution Layer
    │     ├── Permit & HOA Agent (jurisdiction portals)
    │     ├── Crew Scheduling Agent (weather-aware)
    │     ├── Milestone Communication Agent (homeowner updates)
    │     └── Photo Documentation Agent (CompanyCam)
    ├── Insurance & Finance Layer
    │     ├── Insurance Claim Assistance Agent
    │     ├── Financing Qualification Agent (lender APIs)
    │     └── Energy Incentive Finder (DSIRE/IRS)
    ├── Post-Installation Layer
    │     ├── Warranty Registration Agent (manufacturer portals)
    │     ├── Solar Monitoring Agent (inverter APIs)
    │     └── Review/Reputation Agent (platform APIs)
    └── Revenue Development Layer
          ├── Referral Agent (neighborhood canvass + tracking)
          └── Storm Campaign Agent (ongoing weather monitoring)
```

---

## Competitive Intelligence

| Factor | Traditional Operation | AI-Powered Operation |
|---|---|---|
| Storm response time (campaign live) | 2–5 days (manual) | < 4 hours (automated) |
| Time from address to estimate | 24–72 hours | 15–30 minutes (aerial + AI) |
| Insurance claim win rate | 45–55% | 70–85% (with documentation agent) |
| Commercial bid turnaround | 5–7 days | 24–48 hours |
| Permit tracking overhead | 3–5 hrs/week (PM time) | Near-zero (automated) |
| Review acquisition rate | 3–7% of jobs | 22–38% of jobs |
| Solar close rate (lead to contract) | 15–25% | 30–45% (with calculator + financing) |
| Warranty registration completion rate | 60–75% | 98%+ (automated) |
| Customer satisfaction (CSAT) | 3.8–4.2 avg | 4.6–4.9 avg (proactive communication) |
| Referral new job rate | 15–20% of revenue | 28–40% of revenue |

---

## Revenue Model

**Direct Revenue Impact Agents:**
1. **Storm Damage Lead Capture** — Systematic first-mover advantage generates $50,000–$200,000+ in additional storm-season revenue for active operators
2. **Solar Savings Calculator** — Highest-conversion solar lead gen tool; reduces CAC by 40–60% vs. paid leads
3. **Insurance Claim Assistance Agent** — Increases close rate by 20–30%; average additional revenue per storm project: $1,500–$4,000 (supplement recovery)
4. **Financing Qualification Agent** — Eliminates "I can't afford it" objections; 15–25% of closed deals would have been lost without financing options
5. **Commercial Bid Agent** — Enables bidding on 3–5x more commercial RFPs per month vs. manual; each commercial win: $25,000–$250,000+

**Cost Reduction Impact:**
- PM communication overhead: 10–15 hrs/week recovered per PM
- Permit tracking: 3–5 hrs/week per PM
- Manual takeoff/estimation: $40–$80 per estimate vs. ~$15–$20 automated
- Crew mobilization waste (weather cancellations): $5,000–$15,000/year saved
- Warranty claim disputes (prevented by documentation): $2,000–$10,000/year

**Total AI ROI Range (mid-size operator, $2–5M revenue):** $150,000–$500,000/year in combined revenue lift and cost reduction

---

## Stickiest Features (Top 5)

1. **Solar Savings Calculator + Incentive Finder** — This widget is the solar company's primary lead generation engine and the homeowner's decision-making reference. It personalizes solar economics to the specific household, making the operator the trusted source of financial truth. Competitors without a comparably sophisticated tool lose the comparison on every side-by-side evaluation.

2. **AI Inspection Report Generator** — Insurance adjusters and homeowners share AI-generated inspection reports. The branded report becomes the authoritative damage record for the claim. Operators who produce these reports win insurance approvals faster and at higher rates — a measurable, auditable competitive advantage that makes this agent untouchable in the operator's tech stack.

3. **Post-Installation Solar Monitoring Agent** — Creates a 25-year service relationship with every solar customer. Monthly production reports, proactive alerts, and utility savings summaries keep the operator top-of-mind for every referral, battery add-on, EV charger installation, and roof service over two-plus decades. No other single agent generates more lifetime customer value.

4. **Project Milestone Communication Agent** — The single highest-impact driver of positive reviews and referrals in residential roofing. Homeowners who feel informed become brand advocates. The agent's ROI is measurable in both reduced inbound PM calls (quantifiable time savings) and in review score / referral rate improvement (quantifiable revenue impact). Operators who experience both dimensions of this value will not remove the agent.

5. **Storm Lead Capture + Campaign Agent** — In storm-dependent markets, this agent is the entire marketing department during weather events. Operators who have experienced a major hail season with automated storm response understand that the difference between $500K and $2M in storm season revenue can be attributed entirely to campaign speed. The agent is not a feature — it is the business model.
