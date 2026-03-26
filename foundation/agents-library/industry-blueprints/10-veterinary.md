# Veterinary — AI Agent Ecosystem Blueprint

## Industry Overview

Veterinary practices face a uniquely human-emotional service environment combined with complex medical workflows. AI adoption in this space is accelerating rapidly: practices struggle with front-desk overwhelm (30–50% of calls go unanswered during peak hours), appointment no-shows averaging 15–20%, and client retention that drops sharply after a single poor communication experience. Multi-pet households are the norm, not the exception, and compliance gaps in vaccination schedules, parasite prevention, and chronic disease management represent both a clinical risk and a revenue leak. AI agents address all of these pain points while creating deep operational dependency through medical records integration, reminder automation, and real-time triage logic. The stickiest deployments combine voice agents, portal access, and automated care pathways into a single coherent client experience that becomes embedded in how pet owners manage their animals' health year-round.

---

## Sub-Agents Breakdown

### 1. Pet Intake Voice Agent
- **Type**: Voice / Chat
- **Function**: Greets new and returning clients calling or messaging the practice. Captures species, breed, age, weight, primary complaint, and owner contact information. Uses a decision-tree triage to route: emergency calls go directly to an on-call staff member or emergency hospital referral; urgent but non-critical cases are booked in the next available slot; routine wellness visits are scheduled in standard queue. Reads back a confirmation with time, location, and pre-visit instructions.
- **Trigger**: Inbound phone call, website chat widget, or SMS text to the practice number.
- **Integrations**: Practice Management Software (Avimark, Cornerstone, IDEXX Neo, Shepherd), Google Calendar, Twilio (voice/SMS), appointment confirmation email/SMS platform.
- **Sticky Factor**: Once pet profiles are built in the system (species, breed, medical history), clients feel a personalized connection and resist switching practices. The agent "knows" their pet by name on every call.
- **Implementation Notes**: Requires Twilio or similar VoIP/SIP integration. NLP must be tuned on veterinary taxonomy — species (avian, exotic, equine vs. small animal), anatomical terms, and lay descriptions of symptoms. HIPAA/VCPR-equivalent consent handling. Multi-language support (Spanish essential in most US markets).

---

### 2. AI Symptom Assessment & Triage Tool
- **Type**: Chat / Widget
- **Function**: Pet owner describes symptoms in free text or selects from a guided symptom picker. Owner can upload photos or short videos (e.g., limping gait, eye discharge, skin lesion). AI analyzes inputs using a trained veterinary triage model and outputs an urgency score on a 1–5 scale: 1 = monitor at home, 2 = schedule routine visit this week, 3 = seen within 24 hours, 4 = same-day emergency appointment, 5 = go to emergency hospital now. Each score includes plain-language rationale and a list of warning signs to watch for. Scores 4–5 trigger an immediate human callback.
- **Trigger**: Client initiates through the pet portal, website chat, or a post-visit "how is your pet doing?" follow-up message.
- **Integrations**: Pet portal (PetDesk, Vetstoria, or custom), photo/video upload API, practice management system for scheduling, staff escalation webhook.
- **Sticky Factor**: Pet owners who use this tool regularly trust it as a first-line resource and stop calling competing practices for second opinions. Saves dozens of unnecessary emergency visits per month, building loyalty through demonstrated value.
- **Implementation Notes**: Image analysis component requires a vision-capable LLM (GPT-4o, Claude 3.5 Sonnet, or Gemini) with veterinary fine-tuning or few-shot prompting for common presentations. Must include a strong disclaimer that this is not a diagnosis. Audit logging required for liability. Score history stored per pet for longitudinal comparison.

---

### 3. Vaccination & Preventive Care Reminder Agent
- **Type**: Workflow / Automation
- **Function**: Continuously monitors each pet's vaccination record and preventive care schedule in the practice management system. Sends multi-channel reminders (SMS, email, app push notification) at 30-day, 7-day, and day-of intervals for due or overdue vaccinations, heartworm testing, flea/tick prevention refills, dental cleanings, and annual wellness exams. Dynamically personalizes messaging by species, breed, and age (e.g., puppy series messaging differs from senior wellness). One-tap booking link embedded in every reminder. Tracks open rates, click-throughs, and conversion to appointments; flags unresponsive clients for human outreach.
- **Trigger**: Scheduled daily job that checks vaccination due dates against current date, patient age milestones, and prescription refill cycles.
- **Integrations**: Practice Management Software (Cornerstone, IDEXX Neo, Avimark), Twilio SMS, SendGrid or Mailchimp (email), PetDesk/Vetstoria (self-scheduling), Google Analytics for tracking.
- **Sticky Factor**: Practices that run this agent recover an average of 2–4 appointments per week per 500 active patients. Once clients are enrolled, the "set and forget" nature makes switching practices logistically painful — all reminders would stop.
- **Implementation Notes**: VCPR rules vary by state for certain prescription reminders. Deduplication logic essential so pet owners with multiple pets don't receive redundant messages. Opt-out/preference management required. Breed-specific protocols should be configurable (e.g., Leptospirosis for outdoor dogs, FeLV for outdoor cats).

---

### 4. Post-Surgery Follow-Up Agent
- **Type**: Voice / Chat / Workflow
- **Function**: Initiates automated check-ins at pre-defined intervals after surgical or anesthesia procedures: a voice or SMS check at 4 hours post-discharge, 24 hours, 72 hours, and 10–14 days (suture recheck). Asks structured recovery questions: Is the pet eating? Activity level? Wound appearance (requests photo upload)? Pain signs (panting, guarding, vocalizing)? Any vomiting or diarrhea? Responses are scored against recovery benchmarks. Concerning responses trigger an immediate staff alert with the pet's surgical notes pre-loaded. Non-concerning responses generate an automated "recovery on track" message with next instructions.
- **Trigger**: Discharge event logged in practice management system; agent initializes follow-up sequence automatically.
- **Integrations**: Practice management system (discharge event webhook), Twilio (voice + SMS), photo upload endpoint, staff alert platform (Slack, PagerDuty, or internal dashboard), EHR for access to surgical notes.
- **Sticky Factor**: Clients who receive this care feel their pet is being monitored remotely — an extraordinary differentiator. Dramatically reduces post-op complication callbacks and improves outcomes documentation.
- **Implementation Notes**: Response branching must handle non-response (retry at +2 hours, escalate to staff if 3 attempts fail). All recovery data stored in the patient record. Voice agent must be capable of sensitive handling — owners are emotionally raw post-surgery. Avoid robotic tone; warm, reassuring language required.

---

### 5. Pet Portal / Medical Records Agent
- **Type**: Widget / Chat
- **Function**: Provides clients 24/7 access to their pet's complete medical records through a branded portal. AI agent answers questions about records: "When is Bella's next rabies due?" "What heartworm prevention is she on?" "Can you send me her vaccine certificate for boarding?" Agent can generate and email vaccination certificates, medication lists, and referral summaries on demand. Handles records transfer requests when a client is moving or switching practices — routes to staff for approval workflow. Alerts owners when new lab results, imaging reports, or visit notes are posted to their pet's record.
- **Trigger**: Client logs in to portal; specific record requests; new document posted to patient file; records transfer request.
- **Integrations**: Practice management system (records API), document generation (PDF), secure email, SMS notifications, storage (AWS S3 or equivalent).
- **Sticky Factor**: Once clients organize their pet's full health history in the portal, they almost never switch practices — the data migration barrier is significant. Vaccination certificates on demand reduce calls to the front desk.
- **Implementation Notes**: SOC 2 or HIPAA-equivalent security required. Records API varies by PMS (Cornerstone has an API; Avimark may require HL7 export integration). Mobile-responsive portal essential — most access is from smartphones. Branded white-label portal strongly preferred over third-party branding.

---

### 6. Nutrition & Diet Recommendation Engine
- **Type**: Chat / Widget
- **Function**: Interactive tool where pet owners input breed, age, weight, body condition score, activity level, known food allergies, and any active medical conditions (diabetes, kidney disease, food sensitivities, IBD). AI generates a personalized nutrition profile: recommended daily caloric intake, macronutrient ratios, specific commercial food suggestions with brand/product names and life-stage formulas, raw diet considerations if applicable, and feeding schedule. For medical diet cases (renal failure, pancreatitis), recommends prescription diet options with a note to confirm with the veterinarian. Integrates with an in-clinic or online pharmacy for direct purchase of recommended foods.
- **Trigger**: Post-visit recommendation from vet, new patient onboarding, weight check appointment, owner-initiated query via portal/chat.
- **Integrations**: Pet portal, online pharmacy (VetSource, Covetrus, Chewy Health), practice management system (patient data pull), product database (WSAVA-approved food list, AAFCO statement checker).
- **Sticky Factor**: Personalized diet plans create ongoing product revenue and repeat portal engagement. Clients following a vet-recommended diet are more likely to reorder through the clinic's pharmacy rather than retail channels.
- **Implementation Notes**: Must reference current WSAVA nutritional guidelines and AAFCO standards. Do not recommend raw diets without veterinary consultation note for immune-compromised pets. Output should be easy to print or save as PDF. Allergy cross-reference logic required — many commercial foods share manufacturing facilities.

---

### 7. Prescription Refill Bot
- **Type**: Chat / Voice / Workflow
- **Function**: Handles routine refill requests for chronic medications: thyroid (methimazole, levothyroxine), cardiac (atenolol, enalapril, pimobendan), arthritis (meloxicam, Galliprant, Librela), epilepsy (phenobarbital, potassium bromide), diabetes insulin, and parasiticides. Owner submits refill request via portal, SMS keyword, or phone. Agent checks: (1) active prescription on file with valid VCPR, (2) quantity limits not exceeded, (3) no overdue recheck required for controlled substances or monitoring medications. Routes approved refills to in-house pharmacy or authorized online pharmacy. Flags requests requiring vet review and notifies staff. Sends pickup or shipping confirmation.
- **Trigger**: Inbound refill request via any channel; proactive reminder when refill is due based on days supply and last fill date.
- **Integrations**: Practice management system (Rx records), in-house pharmacy software, VetSource/Covetrus/Vetsource online pharmacy, Twilio SMS, controlled substance DEA schedule check.
- **Sticky Factor**: Frictionless refill experience keeps clients buying from the clinic rather than redirecting to Chewy, Costco, or PetMeds. Recurring revenue anchor.
- **Implementation Notes**: DEA regulations apply for Schedule IV substances (phenobarbital). State veterinary pharmacy regulations vary — must confirm refill authority rules in each operating state. Refill logic must enforce monitoring-interval rules (e.g., CBC required every 6 months for phenobarbital patients). Paper trail for all Rx decisions essential.

---

### 8. Emergency Triage Voice Agent
- **Type**: Voice
- **Function**: After-hours and overflow voice agent that answers calls when the clinic is closed or lines are full. Conducts a structured triage interview: What is happening with your pet right now? Species and age? Is the pet breathing normally? Conscious? Bleeding? Suspects toxin ingestion? Based on responses, routes to one of three outcomes: (1) Go immediately to the nearest emergency veterinary hospital — provides address and phone number; (2) Call this number to reach the on-call veterinarian; (3) Monitor at home with these instructions, call us when we open at [time]. Records a complete call transcript and symptom summary emailed/texted to the practice owner. Provides ASPCA Animal Poison Control number (888-426-4435) for toxin cases.
- **Trigger**: Inbound call during after-hours window, or overflow trigger when hold times exceed threshold during business hours.
- **Integrations**: Twilio or RingCentral (VoIP), practice management system (look up patient record by phone number), Google Maps API (nearest emergency facility lookup), email/SMS delivery for call summaries, on-call schedule integration.
- **Sticky Factor**: Pet owners who get useful guidance at 2 AM during a crisis remember that practice forever. Strongest loyalty-building touchpoint in the entire client journey.
- **Implementation Notes**: Must never advise a caller to wait if there is any ambiguity about a life-threatening emergency. Liability disclaimer required. Voice must be calm, clear, and deliberate. Must handle non-English speakers (Spanish minimum). Poison ingestion pathway critical — must name common toxins (xylitol, grapes, raisins, onions, acetaminophen, Sago palm, rodenticide) and advise immediate action.

---

### 9. Boarding & Grooming Scheduler
- **Type**: Chat / Voice / Widget
- **Function**: Full-service booking agent for boarding and grooming services. Handles availability queries, booking confirmations, breed-specific grooming service menus, pricing, and add-on services (nail trim, teeth brushing, bandana). For boarding: collects vaccination proof requirements (Bordetella, Rabies, DHPP), feeding instructions, medication schedules, emergency contacts, and special behavioral notes. Sends pre-arrival checklists and post-stay recap messages. Manages cancellation and rescheduling with configurable hold/deposit policies. Cross-sells veterinary wellness appointments around boarding dates ("Since Bella is coming in Friday, would you like to schedule her overdue dental cleaning?").
- **Trigger**: Inbound booking request via phone, website widget, or SMS; upsell trigger on vaccination/appointment reminder messages.
- **Integrations**: Practice management or boarding-specific software (Gingr, Kennel Booker, PetExec), payment processor (Stripe), Google Calendar, vaccination record verification (auto-check from PMS), email/SMS confirmation platform.
- **Sticky Factor**: Integrated boarding/grooming + medical records means one login, one relationship, one practice for all pet services. Significant switching cost once a boarding history is established.
- **Implementation Notes**: Vaccination verification should auto-check records in PMS before confirming boarding reservation — reduces manual staff effort dramatically. Behavioral notes (dog-reactive, anxiety history, medication schedule) must be surfaced to boarding staff at check-in. GDPR/CCPA consent for storing pet behavioral data.

---

### 10. New Pet Owner Education Agent
- **Type**: Chat / Workflow / Widget
- **Function**: Triggered when a new puppy/kitten patient is registered, this agent launches a comprehensive onboarding education sequence. Delivers content in digestible weekly segments aligned with developmental milestones: vaccination schedule with specific ages for each vaccine, deworming protocol, socialization windows (critical period 3–14 weeks for puppies), crate training basics, leash introduction, spay/neuter timing recommendations (varies by breed and size), parasite prevention initiation, microchipping, and pet insurance guidance. Includes embedded video content, downloadable PDF guides, and "milestone check-in" quizzes. Parents of large-breed puppies receive specific guidance on nutrition to prevent developmental orthopedic disease.
- **Trigger**: New puppy/kitten patient registration in PMS; age milestone dates calculated from DOB.
- **Integrations**: PMS (patient creation webhook), email/SMS delivery, portal content library, YouTube embeds, PDF generation.
- **Sticky Factor**: Practices that guide new puppy/kitten owners through the entire first year of life build lifelong client relationships. The educational investment in year one creates a 10–15+ year client.
- **Implementation Notes**: Content library must be species-specific (puppy vs. kitten pathways differ significantly), and breed-adjusted for large/giant breeds, brachycephalic breeds, and working/sporting breeds. Spay/neuter guidance must reflect current evidence (avoid before 12–18 months for large breeds per AKC CHF and AVMA updated guidance). Tone must be warm and celebratory — new pet ownership is exciting.

---

### 11. Breed-Specific Health Alert System
- **Type**: Workflow / Push Notification
- **Function**: Using the patient's breed and date of birth, the system proactively sends health alerts timed to clinically relevant age windows. Examples: Golden Retriever at age 6 — "Goldens have elevated risk for lymphoma and hemangiosarcoma; here's what to watch for." Labrador at age 2 — "Hip evaluation at this age is recommended for Labs." CKCS at any age — "Cavalier King Charles Spaniels should have annual cardiac auscultation due to MVD predisposition." Maine Coon cats — "HCM cardiac screening recommended." Mixed breeds receive alerts based on predominant breed DNA if a Wisdom Panel or Embark test result is on file. Alert contains educational content and a one-tap appointment booking link.
- **Trigger**: Patient age milestone (calculated from DOB), monthly batch job for age-based screenings.
- **Integrations**: PMS (breed + DOB data), breed health database (OFA, CHIC, AVMA guidelines), email/SMS, booking widget.
- **Sticky Factor**: This is preventive medicine that feels magical to clients — a practice that knows what's coming before problems arise creates an irreplaceable sense of personalized care.
- **Implementation Notes**: Breed health database should be curated and updated annually; align with OFA, CHIC, and ACVIM guidelines. Avoid fear-based language; educational and empowering tone. Mixed-breed patients are significant — DNA test result integration (Embark, Wisdom Panel API) is a competitive differentiator. Alert must not constitute a diagnosis.

---

### 12. Lab Results Communicator
- **Type**: Chat / Workflow
- **Function**: When lab results are finalized and uploaded to the PMS (CBC, chemistry panel, urinalysis, thyroid, heartworm test, fecal, cytology, culture & sensitivity), the AI generates a plain-language summary for the client: "Max's blood work looks great overall! His kidney values (BUN and creatinine) are within normal range. His white blood cell count is slightly elevated, which can indicate infection or inflammation — Dr. Smith has noted this and will discuss next steps with you." Flagged abnormals are highlighted. Vet must approve the summary before it is sent. If results indicate a significant finding, the agent schedules a callback or appointment rather than just sending a message.
- **Trigger**: Lab result uploaded to PMS + veterinarian approval flag set.
- **Integrations**: PMS lab module, IDEXX or Antech reference lab API, email/SMS delivery, appointment scheduler (for follow-up booking), vet approval dashboard.
- **Sticky Factor**: Clients no longer have to call and wait for lab results — they receive them proactively, clearly explained, with action steps. This alone drives significant loyalty and differentiates the practice.
- **Implementation Notes**: Veterinarian must review and approve every AI-generated summary before delivery — no autonomous medical communication without clinical oversight. Reference range contextualization must account for species, age, and sex (e.g., feline CBC normals vs. canine). Requires HL7 or IDEXX/Antech API integration. Summaries must avoid using the word "diagnosis" — always frame as "results that your vet will discuss with you."

---

### 13. End-of-Life Care Guide Agent
- **Type**: Chat / Voice
- **Function**: One of the most sensitive and differentiating agents in the entire veterinary ecosystem. Activated when a patient is flagged with a terminal diagnosis or quality-of-life assessment. Provides compassionate, private guidance to pet owners on: pain management and palliative care options, quality-of-life assessment scales (HHHHHMM scale, Ohio State QoL scale), signs that indicate declining comfort, the euthanasia process (what to expect, who can be present, what happens afterward), in-home euthanasia service referrals, aftercare options (individual cremation, communal cremation, burial), grief support resources (Pet Loss Support Hotline, local pet loss support groups, therapists who specialize in pet bereavement), and memorial services. Never initiates this pathway without veterinarian activation.
- **Trigger**: Veterinarian flags patient record with "hospice/palliative" or "terminal" status; client explicitly requests information on end-of-life options.
- **Integrations**: PMS (patient status flag), curated resource database (grief resources, in-home euthanasia networks, aftercare providers), email for resource delivery, in-home service provider directory.
- **Sticky Factor**: Practices that handle this moment with extraordinary compassion earn loyalty that extends to the next pet — and the one after that. Grief support referrals generate word-of-mouth referrals from the pet loss community.
- **Implementation Notes**: Extreme care required in language design — do not use clinical language ("put to sleep" vs. "euthanasia" debate is real; use client's own language preferences). Must not push euthanasia; must validate all choices including continued treatment. Human escalation path must always be available. Crisis line should be included (human crisis line for owners in acute grief).

---

### 14. Inventory & Pharmacy Manager
- **Type**: Workflow / Dashboard Widget
- **Function**: Monitors all pharmacy and medical supply inventory in real time. Tracks: current stock levels by item, minimum reorder thresholds, average daily usage rate, expiration dates (flags items within 90/60/30 days of expiration), controlled substance log balance reconciliation (DEA 222 forms, CSOS electronic ordering), and supplier pricing. Auto-generates purchase orders when items hit reorder point. Identifies usage anomalies (unexpected depletion that may indicate diversion for controlled substances). Provides cost-per-patient reporting and markup analysis. Integrates with major distributors for electronic ordering.
- **Trigger**: Daily automated inventory audit; manual stock count entry; item dispensed from PMS; expiration date proximity alert.
- **Integrations**: Covetrus, Henry Schein Vet, MWI Animal Health (distributor EDI/API), PMS dispensing module, DEA CSOS integration, QuickBooks or practice financial system.
- **Sticky Factor**: Controlled substance compliance alone makes this agent nearly mandatory in any practice subject to DEA audit. Once the pharmacy workflow is automated, manual inventory is never returned to.
- **Implementation Notes**: DEA schedule III-V substance tracking must include biennial inventory requirement, Form 222 reconciliation, and audit trail. State pharmacy board regulations for veterinary dispensing vary — agent must be configurable per state. FIFO (first in, first out) dispensing logic for expiration management. Wholesaler API availability varies; EDI 850/855 document support may be needed.

---

### 15. Multi-Pet Manager
- **Type**: Widget / Dashboard
- **Function**: Families with multiple pets (households with 3+ pets are extremely common) get a consolidated view of all their animals in a single dashboard: unified reminder calendar across all pets, one-tap booking for any pet, consolidated vaccination status overview ("2 pets are due for vaccines this month"), single payment profile for all billing, family appointment bundling (schedule multiple pets in the same visit block to reduce trips), shared medical notes visible to the whole family account. Also surfaces total household spend and loyalty points across the multi-pet family, encouraging engagement.
- **Trigger**: Second pet registration under same household account; proactive invitation sent after first visit to set up multi-pet portal.
- **Integrations**: PMS (household grouping logic), portal, scheduling system, loyalty/rewards program, email/SMS.
- **Sticky Factor**: Multi-pet families switching practices must migrate records for every pet — an enormous friction that effectively locks in the household. Consolidated billing and reminders are deeply appreciated by this segment.
- **Implementation Notes**: Household grouping must handle different last names (blended families, domestic partners). Appointment bundling logic must check practitioner availability across multiple patient slots. Financial summary must handle split billing across multiple cards or accounts.

---

### 16. Referral Coordinator
- **Type**: Chat / Workflow
- **Function**: When a patient requires specialist referral (cardiology, dermatology, oncology, ophthalmology, internal medicine, surgery, neurology, rehabilitation), this agent manages the entire referral workflow: identifies appropriate specialists by geographic proximity and specialty, sends patient records (SOAP notes, lab work, imaging DICOM files) securely to the receiving specialist, generates a referral summary letter, schedules the specialist appointment directly where integration allows, provides the client with the specialist's contact information and what to bring, and receives the specialist's consultation report back into the patient record. Tracks referral status and follows up if no consultation report is received within 30 days.
- **Trigger**: Veterinarian initiates referral order in PMS.
- **Integrations**: PMS, DICOM imaging system, secure fax or encrypted document transfer (Updox, Spruce Health), specialist practice booking APIs where available, email/SMS client notification.
- **Sticky Factor**: Seamless referral coordination makes the primary care practice indispensable as the "quarterback" of the pet's healthcare. Clients feel they never have to navigate the system alone.
- **Implementation Notes**: DICOM file transfer is technically complex — requires DICOM viewer integration or conversion to standard image formats for less sophisticated specialist systems. Referral tracking must have a follow-up loop. State veterinary practice acts vary on VCPR continuation during specialist referral.

---

### 17. Client Satisfaction & Review Agent
- **Type**: Workflow / Chat
- **Function**: Sends an automated post-visit survey (2–3 questions, NPS format) within 2 hours of checkout. Measures satisfaction with: wait time, communication quality, perceived value, and likelihood to recommend. High-score respondents (9–10 NPS) are immediately sent a Google review request with direct link. Mid-score respondents (7–8) are asked for specific improvement suggestions — this data feeds a practice improvement dashboard. Low-score respondents (0–6) trigger an immediate staff alert for personal outreach within 24 hours — complaints are intercepted before they become public reviews. Tracks review volume and rating trends over time with reporting dashboard.
- **Trigger**: Appointment check-out event in PMS.
- **Integrations**: PMS (checkout webhook), Twilio SMS, Google Business Profile API (review link generation), NPS dashboard (Delighted, Medallia, or custom), staff alert platform.
- **Sticky Factor**: Practices that run this consistently improve their Google rating by 0.5–1.0 stars within 6 months. Higher ratings drive new patient acquisition, creating a compounding growth effect.
- **Implementation Notes**: Google's terms of service prohibit review gating (only soliciting reviews from happy customers) — survey must go to all clients, but the message content can be differentiated. ADA compliance for survey delivery. Timing matters: 2–4 hours post-visit is optimal.

---

### 18. Pet Insurance Verification Bot
- **Type**: Chat / Widget
- **Function**: Prior to any significant procedure (surgery, advanced diagnostics, specialist referral, dental cleaning), this agent verifies the pet's insurance coverage. Client enters their carrier and policy number (or it is pre-stored in their profile). Agent queries carrier's eligibility API (where available) or guides the client through a structured self-service verification flow. Returns: coverage status, deductible remaining, annual maximum remaining, covered vs. excluded conditions for the proposed procedure, typical reimbursement percentage, and estimated out-of-pocket for the client. Generates a pre-authorization request if the carrier requires it. Helps the practice reduce billing disputes and helps clients make informed consent decisions.
- **Trigger**: Appointment type flagged as "estimate required" in PMS; client or staff initiates prior to treatment plan presentation.
- **Integrations**: Pet insurance carrier APIs (Trupanion, Healthy Paws, Nationwide, Embrace, Lemonade Pet — availability varies), treatment estimate module in PMS, client portal, email delivery of coverage summary.
- **Sticky Factor**: Clients who use pet insurance heavily rely on the practice that integrates with their carrier seamlessly. Trupanion's direct-to-practice payment system (Trupanion Express) is particularly sticky.
- **Implementation Notes**: Trupanion has a formal API for practice integration. Other carriers have limited API availability — web scraping or structured self-service flows may be required. Out-of-pocket estimates must be presented clearly with caveats. Agent must never guarantee coverage — "based on the information provided" qualifier required. CCPA/GDPR for policy data storage.

---

## Industry-Specific Intake Forms

**New Patient / New Client Form**
- Owner: Full name, address, phone (mobile + alternate), email, preferred contact method
- Emergency contacts (2 required)
- Referring source (how did you hear about us?)
- Pet: Name, species, breed, color/markings, DOB or estimated age, sex, spay/neuter status, microchip number
- Previous veterinarian name and practice (records release authorization)
- Current medications and supplements with doses
- Known allergies (drug, food, environmental)
- Vaccination history (attach records or list dates)
- Feeding: brand, type, amount, frequency
- Lifestyle: indoor/outdoor, multi-pet household, exposure to wildlife, travel history
- Insurance carrier and policy number
- Consent: treatment authorization, financial responsibility, photo/video consent for records, SMS/email marketing opt-in
- Rabies certificate upload for dogs (required in most states for licensing)

**Sick Visit Intake**
- Chief complaint (free text)
- Duration of symptoms
- Progression (getting better, worse, or stable?)
- Appetite and water intake changes
- Vomiting/diarrhea (frequency, character, blood present?)
- Urination/defecation changes
- Activity level and mentation
- Possible toxin exposure
- Any home treatments attempted

**Surgical Pre-Op Form**
- Last food and water times (NPO compliance)
- Current medications (especially anticoagulants, NSAIDs, steroids)
- Anesthesia history (previous reactions)
- Emergency contact available day of surgery
- Consent: anesthesia, surgical procedure, blood transfusion authorization, CPR preferences

---

## Interactive Widgets & Tools

| Widget | Function | Placement |
|--------|----------|-----------|
| Symptom Checker | Guided pet symptom input → urgency score | Website homepage, portal |
| Vaccine Due Date Calculator | Enter pet DOB and last vaccine dates → next due dates | Website, portal |
| Body Weight & BCS Tracker | Log weight over time → trend graph | Portal dashboard |
| Medication Dosage Calculator | Weight-based dosing for OTC/Rx meds (with vet disclaimer) | Portal |
| Food Calorie Calculator | Daily caloric needs by weight, breed, life stage | Portal, website |
| Breed Health Encyclopedia | Interactive breed-specific health risk guide | Website |
| Pet Age Calculator | Convert pet age to human-equivalent years | Website (traffic magnet) |
| Boarding Availability Calendar | Real-time boarding slot availability with booking | Website |
| Poison Lookup Tool | Search common toxins → severity + action steps | Website (high SEO value) |
| Insurance Premium Estimator | Estimate monthly insurance cost by species and zip | Website (lead gen) |

---

## Employee Role Mapping

| Role | AI Agents Serving This Role |
|------|-----------------------------|
| Front Desk / Client Services | Pet Intake Voice Agent, Boarding Scheduler, Lab Results Communicator (approval workflow), Client Satisfaction Agent |
| Veterinarian | Lab Results Communicator (approval queue), Post-Surgery Follow-Up (alert review), Referral Coordinator, Symptom Assessment (escalation review) |
| Veterinary Technician | Post-Surgery Follow-Up (alert monitoring), Prescription Refill Bot (Rx review queue), Inventory Manager, Breed Alert System |
| Practice Manager | Client Satisfaction Dashboard, Inventory & Pharmacy Manager, Revenue reporting, Multi-Pet Manager |
| Boarding/Grooming Staff | Boarding Scheduler (reservation queue + pet notes), Vaccination verification alerts |
| On-Call Veterinarian | Emergency Triage Voice Agent (escalation alerts), After-hours call summaries |

---

## Integration Architecture

```
Core Hub: Practice Management System (Avimark / Cornerstone / IDEXX Neo / Shepherd)
    │
    ├── Communication Layer: Twilio (Voice + SMS) → All Voice & SMS Agents
    ├── Email Layer: SendGrid / Mailchimp → Reminder, Lab Results, Post-Surgery Agents
    ├── Client Portal: PetDesk / Vetstoria / Custom → Records, Scheduling, Triage Widget
    ├── Lab Interface: IDEXX PIMS+ / Antech Avimark connector → Lab Results Communicator
    ├── Pharmacy: Covetrus / VetSource / Henry Schein → Refill Bot, Inventory Manager
    ├── Imaging: DICOM server (Asteris, ezyVet Imaging) → Referral Coordinator
    ├── Insurance: Trupanion Express API, carrier portals → Insurance Verification Bot
    ├── Reviews: Google Business Profile API → Client Satisfaction Agent
    └── Financial: QuickBooks / Practice financial system → Inventory Manager, Billing
```

**Data flow priority**: PMS is the system of record. All agents read from and write back to PMS. No agent should maintain independent patient records that are not reconciled with PMS.

---

## Competitive Intelligence

| Competitor Category | Current Offering | AI Agent Advantage |
|--------------------|------------------|--------------------|
| Large corporate practices (Banfield, VCA, BluePearl) | Heavy app investment (Banfield Optimum Wellness app) but generic, non-practice-specific | Custom branded agents personalized to individual practice feel |
| Independent practice management software (IDEXX, Covetrus) | Basic reminder automation, some portal tools | Multi-agent orchestration, voice triage, post-surgery follow-up not yet commoditized |
| Telemedicine platforms (Airvet, Pawp, Dutch) | Strong video consult UX | Not integrated with in-person PMS; AI agents bridge gap |
| PetDesk / Weave (communication platforms) | SMS reminders, review solicitation | AI adds triage intelligence, lab result summaries, end-of-life guidance — far beyond template messages |
| Emerging AI vet startups (Vet-AI, Joii UK) | Symptom checker focus | Full practice integration is the gap; symptom checker alone is table stakes |

**Key differentiators to win**: Post-surgery follow-up, lab results plain-language summary, end-of-life care guidance, and multi-pet household management are not currently offered by any single competing platform.

---

## Revenue Model

| Revenue Stream | Mechanism | Monthly Value per Practice |
|---------------|-----------|---------------------------|
| Platform subscription | Monthly SaaS fee per provider | $500–$2,000/mo |
| Per-appointment recovery | Reminder agent books previously lost appointments | $2,000–$8,000/mo recovered revenue |
| Pharmacy retention | Refill bot keeps Rx revenue in-clinic vs. leaking to Chewy | $500–$3,000/mo |
| Boarding/grooming upsell | Cross-sell conversions from appointment reminders | $300–$1,500/mo |
| Insurance integration | Trupanion referral/affiliate program | $50–$300/mo |
| Review value | Improved Google rating → new client acquisition | $500–$2,000/mo in new client value |

**Total estimated monthly value per practice**: $3,850–$16,800+

---

## Stickiest Features (Top 5)

1. **Pet Portal with Medical Records Access** — Once clients store vaccination certificates, lab history, and medication records in the portal, they will not leave. Data migration to a new practice is burdensome and most clients won't do it.

2. **Post-Surgery Follow-Up Agent** — No competing product offers this. The emotional impact of receiving check-in calls after a pet's surgery is enormous. Clients describe this as the single most impressive thing a vet has ever done for them.

3. **Emergency Triage Voice Agent (After-Hours)** — Answering a panicked 2 AM call with calm, intelligent guidance creates a loyalty bond that marketing dollars cannot replicate. Practices that deploy this report it as their #1 referral driver.

4. **Vaccination & Preventive Care Reminder Agent** — Becomes invisible infrastructure within 60 days of deployment. Clients rely on reminders and would notice their absence immediately. Switching practices means losing their reminder system.

5. **Lab Results Plain-Language Communicator** — Eliminates the dreaded "waiting for the vet to call back" experience. Clients describe receiving their pet's lab results explained clearly as profoundly reassuring. The vet-approval gate maintains clinical standards while dramatically improving the client experience.
