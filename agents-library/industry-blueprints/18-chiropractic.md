# Chiropractic & Wellness — AI Agent Ecosystem Blueprint

## Industry Overview
Chiropractic practices sit at the intersection of healthcare delivery, insurance navigation, and wellness retail. They operate in a high-volume, appointment-driven model where patient throughput, retention, and case value determine profitability. The industry faces unique challenges: high new patient acquisition costs, insurance reimbursement complexity, patient dropout before care plan completion, and a structural dependency on the treating provider's personal relationships. AI agents in this space must handle clinical intake, insurance complexity, patient communication, and wellness program delivery while remaining HIPAA-compliant and reinforcing the clinical trust the doctor has built.

**Primary Revenue Streams:** Chiropractic adjustments (insurance + cash pay), wellness/maintenance care plans, decompression therapy, massage, physiotherapy, personal injury cases, nutritional supplements, orthotics, workshops/events.
**Primary Pain Points:** Patient no-shows, insurance claim denials, early patient dropout from care plans, PI case management complexity, front desk overwhelm, difficulty scaling without adding FTEs.
**Ideal AI Stack Outcome:** A practice that converts more new patients, retains them through completion, manages PI cases efficiently, and generates recurring wellness revenue — all while the front desk focuses on the in-office experience rather than administrative tasks.

---

## Sub-Agents Breakdown

### 1. New Patient Intake Voice Agent
- **Type**: Voice + Chat
- **Function**: Handles inbound new patient calls 24/7. Greets caller, collects chief complaint, symptom description, pain location and duration, previous chiropractic history, current medications, primary insurance carrier and member ID, preferred appointment times, and how they heard about the practice. Reads collected data back for confirmation. Books the appointment in the practice management system. Sends a confirmation text/email with intake form link, office directions, and what to bring. Creates the new patient chart record. Sends an internal alert to the front desk with the new patient summary.
- **Trigger**: Inbound call (unanswered or after-hours), website chat widget, online new patient request form submission
- **Integrations**: VAPI / Bland.ai / Twilio (voice), ChiroTouch / EHR / Jane App / Genesis (scheduling), Twilio SMS, Gmail/Outlook, Zapier/Make
- **Sticky Factor**: The practice captures new patients at 11pm and weekends — every missed call used to be a missed patient; now it's a booked appointment
- **Implementation Notes**: Must be HIPAA-compliant — voice recordings and data storage must meet PHI requirements. Integration with practice management system (PMS) is critical; ChiroTouch, EHR (formerly ChiroFusion), and Jane App have APIs. Voice agent should sound warm and professional, not robotic.

### 2. Pain Assessment Intake Form with Body Map Tool
- **Type**: Widget + Interactive Form
- **Function**: Replaces the paper intake form with a mobile-optimized digital experience. Patients tap on an interactive body map (front and back view) to mark pain locations. For each marked location: rates severity 1-10, selects pain type (sharp, dull, burning, aching, radiating), indicates duration (onset date, constant vs. intermittent), and identifies aggravating/relieving factors. Captures functional limitations (sleep, work, daily activities). Outputs a structured pain summary document for the doctor's review before the appointment. Scores overall case complexity to help the doctor prepare.
- **Trigger**: New patient appointment confirmation sent (triggers form link), reminder sent 24 hours before first visit with form completion reminder
- **Integrations**: IntakeQ / Jotform (with body map field) / custom web widget, ChiroTouch / Jane App (form data import), Google Drive / S3 (form storage), HIPAA-compliant form hosting
- **Sticky Factor**: Doctors who review a structured pain summary before entering the exam room have significantly better first visits — they never want to go back to paper forms
- **Implementation Notes**: Body map widget can be built with HTML5 Canvas or sourced from IntakeQ's built-in body diagram tool. Ensure form data is transmitted and stored with HIPAA encryption. Case complexity score (mild/moderate/severe) is a calculated field based on location count, severity, and duration inputs.

### 3. Treatment Plan Presentation Agent
- **Type**: Chat + Document + Video
- **Function**: After the doctor's examination and diagnosis, generates a personalized treatment plan presentation document for the patient. Explains in plain language: diagnosis, recommended frequency and duration of care, expected outcomes at each phase, total visit estimate, insurance coverage (if applicable), out-of-pocket cost estimate, and comparison to going untreated. Delivers via tablet in office or link sent after visit. Includes condition-specific educational videos. Captures digital signature confirming patient understands and accepts care plan. Sends a follow-up email with plan summary for home review.
- **Trigger**: Doctor marks exam complete and diagnosis entered, care plan created in PMS
- **Integrations**: ChiroTouch / Jane App (diagnosis and care plan data), DocuSign / HelloSign (e-signature), Loom / YouTube (educational videos), Twilio SMS / Gmail (delivery), Airtable (tracking acceptance rate)
- **Sticky Factor**: Patients who sign a care plan have 40-60% higher completion rates — digital delivery with e-signature creates commitment
- **Implementation Notes**: Plan generation requires pulling from PMS data (diagnosis code, recommended visit frequency). Plain-language explanations should be pre-written by condition category (cervical, lumbar, extremity, etc.) and pulled based on diagnosis. Track acceptance rate vs. no-signature rate to measure effectiveness.

### 4. Insurance Verification & Benefits Explanation Bot
- **Type**: Workflow + Chat
- **Function**: Triggers upon new patient scheduling. Automatically submits eligibility verification request to insurance carrier via clearinghouse. Receives and parses benefits response: deductible (met/unmet), copay/coinsurance, visit limits, authorization requirements, network status. Translates the EOB data into plain English: "Your insurance covers 80% after your $500 deductible. You've met $200 of your deductible. Your first few visits will go toward your deductible, then you'll pay approximately $30 per visit." Sends benefits summary to patient before first visit. Flags cases needing prior authorization.
- **Trigger**: New appointment booked (insurance info provided), insurance info updated by patient
- **Integrations**: Availity / Waystar / Office Ally (clearinghouse eligibility API), ChiroTouch / Jane App, Twilio SMS, Gmail/Outlook, Slack (staff alerts for auth requirements)
- **Sticky Factor**: When patients understand their benefits before they arrive, there are no financial surprises — this alone reduces first-visit cancellations by 15-25%
- **Implementation Notes**: Clearinghouse eligibility transactions (270/271) are the standard EDI method. Real-time response is not always available — some carriers have 24-hour turnaround. Auth requirement flags need immediate human action and should route to the biller or front desk via Slack alert.

### 5. Appointment Scheduling with Provider Matching Agent
- **Type**: Chat + Workflow
- **Function**: For multi-provider practices, matches incoming patients to the most appropriate provider based on: presenting condition (e.g., sports injury → sports-focused DC, pediatric → pediatric-trained DC, prenatal → Webster-certified DC, PI case → PI-experienced DC), insurance network status for each provider, patient location preference, and schedule availability. Explains the match rationale to the patient. Manages scheduling across all providers in one interface. Handles recurring appointment series booking based on care plan frequency.
- **Trigger**: New patient scheduling request, care plan initiation (triggers recurring appointment series), provider out-of-office (triggers reassignment with patient notification)
- **Integrations**: Jane App / ChiroTouch (multi-provider calendar), website chat widget, patient portal, Twilio SMS (appointment series confirmation)
- **Sticky Factor**: Practices that match patient conditions to the right provider see better outcomes and higher patient satisfaction scores
- **Implementation Notes**: Provider specialty tagging must be maintained in the system. Match logic should be weighted: network status and condition match take priority over schedule convenience. For reassignment scenarios, patient notification should include the reason and introduce the covering provider.

### 6. Post-Adjustment Follow-Up Agent
- **Type**: Voice + Chat + Workflow
- **Function**: Sends a check-in message 2-4 hours after each adjustment (first 3 visits, then weekly). For new patients after visit 1: "How are you feeling after your adjustment? Any soreness? Any questions?" Collects a pain severity rating (1-10) and any concerns. Routes responses to doctor dashboard. For patients reporting increased pain or adverse reactions, triggers an immediate alert to clinical staff. For patients reporting positive progress, sends an encouragement message and reminder for next appointment. Tracks pain trajectory over visits to document improvement for outcome reporting and PI case support.
- **Trigger**: Appointment marked complete in PMS, 2-hour post-visit timer, weekly cadence after visit 3
- **Integrations**: ChiroTouch / Jane App (appointment completion webhook), Twilio SMS, VAPI (voice option for elderly patients), Airtable (pain tracking database), Slack (adverse reaction alert)
- **Sticky Factor**: Patients feel genuinely cared for between visits — this emotional connection is the #1 driver of long-term retention and referrals
- **Implementation Notes**: Post-visit check-in timing matters — 2-4 hours captures immediate response before soreness sets in. Pain rating data should feed into a visible progress chart for the patient and doctor. Adverse reaction routing must have a sub-5-minute response SLA from clinical staff.

### 7. Exercise & Stretching Program Delivery Agent
- **Type**: Workflow + Chat + App
- **Function**: When a doctor prescribes a home exercise program (HEP), the agent generates a personalized routine based on diagnosis, physical limitations, fitness level, and available equipment. Delivers the program via SMS link or patient portal: each exercise includes a video demo, written instructions, sets/reps/duration, and frequency. Sends daily exercise reminders. Tracks patient-reported completion ("Did you do your exercises today?"). Escalates to doctor if patient reports pain with specific exercises. Progresses the program difficulty as the patient improves (via doctor approval or rule-based advancement).
- **Trigger**: Doctor prescribes HEP in PMS, daily exercise reminder schedule, patient completion report, 2-week progress review
- **Integrations**: MedBridge / HEP2go / Strive Labs (exercise library), ChiroTouch (prescription), Twilio SMS, patient portal, Airtable (compliance tracking), Slack (doctor alerts for exercise pain)
- **Sticky Factor**: Patients who do their home exercises heal faster — demonstrably better outcomes drive referrals and reviews
- **Implementation Notes**: Exercise library should have 200+ condition-specific exercises with video. MedBridge is the industry standard for chiropractic HEP; HEP2go is a lower-cost option. Compliance tracking data is valuable for PI case documentation and outcome reporting.

### 8. Ergonomic Assessment Tool
- **Type**: Interactive Widget + Workflow
- **Function**: A self-guided digital assessment patients complete about their work environment. Covers: chair height and lumbar support, monitor height and distance, keyboard and mouse position, standing desk usage, phone habits (cradle vs. headset), driving posture, sleep position and pillow setup. Based on responses, generates a personalized ergonomic report with specific correction recommendations for each identified issue. Recommends relevant products (lumbar supports, monitor stands, ergonomic keyboards, supportive pillows) — links to the practice's product store. Sends report PDF to patient and files in chart.
- **Trigger**: New patient intake (auto-trigger for desk workers based on occupation field), doctor recommendation during visit, patient request
- **Integrations**: Typeform / custom web form, OpenAI GPT-4o (recommendation generation), WooCommerce / Shopify (product links for practice store), Google Drive (PDF report), ChiroTouch (chart filing)
- **Sticky Factor**: Patients who receive and implement ergonomic advice see faster improvement and attribute it to the practice's comprehensive care approach
- **Implementation Notes**: Occupation detection from intake form triggers assessment automatically for office workers, drivers, and healthcare workers. Product recommendations should link to the practice's dispensary first — this is a revenue touchpoint. PDF report should be branded and shareable (patients often share with their employer for workplace accommodation requests).

### 9. Patient Reactivation Agent
- **Type**: Workflow + Voice + SMS
- **Function**: Identifies patients who have lapsed (no visit in 30, 60, or 90+ days based on their care plan frequency recommendation). Segments lapsed patients by original complaint and care plan status (completed, incomplete, unknown dropout). Sends a personalized reactivation message referencing their previous condition: "Hi Sarah, it's been 6 weeks since your last visit. How is your low back doing? We'd love to check in." Includes a one-click rebooking link. For 90+ day lapsed patients, triggers a voice agent call. Tracks reactivation rate and revenue per reactivated patient. Flags patients with PI cases for special handling.
- **Trigger**: 30/60/90-day lapse detection (nightly query on appointment data), seasonal wellness campaigns (January, September), specific condition follow-up dates
- **Integrations**: ChiroTouch / Jane App (last visit query), Twilio SMS + Voice, VAPI (voice), Calendly / PMS online booking, GoHighLevel (campaign management), Airtable (reactivation tracking)
- **Sticky Factor**: Reactivation campaigns with 15-25% response rates are pure revenue from the existing patient database — practices become unwilling to leave this money on the table
- **Implementation Notes**: Message personalization (referencing original complaint) significantly outperforms generic "we miss you" messages. PI lapsed patients need special handling — may be lapsed due to case closure or attorney instruction, not dropout. Opt-out handling must comply with TCPA for SMS.

### 10. Wellness Product Recommendation Engine
- **Type**: Chat + Workflow + Widget
- **Function**: Based on patient diagnosis, symptoms, lifestyle factors (from intake and ergonomic assessment), and care plan stage, generates personalized product recommendations from the practice's dispensary. Categories: nutritional supplements (omega-3, magnesium, collagen, turmeric), orthopedic supports (cervical pillows, lumbar rolls, knee braces), thermal therapy (ice/heat), ergonomic accessories, and recovery tools (foam rollers, massage guns). Recommendations are presented in the patient portal, sent post-visit via SMS, and surfaced by the front desk script. Tracks purchase history to avoid repeat recommendations and sequence care-stage-appropriate products.
- **Trigger**: Post-visit follow-up sequence, care plan stage change, doctor enters recommendation note in chart, patient portal visit
- **Integrations**: ChiroTouch (diagnosis and care stage data), WooCommerce / Shopify / ProfitableSupplements.com (dispensary), Twilio SMS, patient portal, Airtable (recommendation log)
- **Sticky Factor**: Product revenue is high-margin and creates a wellness consumption habit — patients who buy supplements and tools from the practice have higher lifetime value and retention
- **Implementation Notes**: Product recommendations must be medically defensible — build the recommendation logic with doctor input and don't make therapeutic claims beyond what's evidence-supported. Track conversion rate per recommendation type to optimize the recommendation algorithm over time.

### 11. X-Ray & Imaging Coordination Agent
- **Type**: Workflow
- **Function**: When a doctor orders imaging, the agent: verifies whether the imaging service is in-network for the patient's insurance, contacts the preferred imaging center to schedule, sends patient preparation instructions (what to wear, what to bring, fasting requirements if applicable), tracks whether the order has been fulfilled (patient showed up), follows up with the imaging center for result delivery, receives results and adds to patient chart, sends doctor an alert when results are available for review, and sends patient a notification that results are in and a telehealth or in-office review has been scheduled.
- **Trigger**: Doctor enters imaging order in PMS, 24-hour reminder to patient, imaging appointment completion, results received
- **Integrations**: ChiroTouch / Jane App (imaging order), Twilio SMS / email (patient communication), DICOM viewer integration (for result viewing), fax API (Phaxio) for imaging center communication, Slack (doctor results alert)
- **Sticky Factor**: Imaging coordination is one of the most friction-heavy workflows in chiropractic — automating the order-to-result chain saves significant administrative time
- **Implementation Notes**: Many imaging centers still communicate via fax — integrate a fax API (Phaxio, eFax) for sending orders and receiving results. HIPAA compliance is critical for imaging data storage and transmission. In-network verification should happen before scheduling — out-of-network imaging can result in unexpected bills that damage patient trust.

### 12. Personal Injury (PI) Case Management Agent
- **Type**: Workflow + Document Generation
- **Function**: Creates and manages a dedicated PI case file when a patient reports a motor vehicle accident or slip-and-fall. Tracks every aspect of the case: accident date, at-fault party, insurance carrier, attorney information, liability status. Generates medico-legal documentation: SOAP notes summary, treatment chronology, outcome measures. Produces demand package components: narrative report template, billing summary, lien letter to attorney. Sends weekly case status updates to attorney via email. Alerts doctor when case reaches treatment completion thresholds. Manages lien agreements and tracks settlement status for collections.
- **Trigger**: Patient reports accident on intake, "PI" designation added to chart, attorney contact initiated, weekly status update schedule, case closure event
- **Integrations**: ChiroTouch / EHR (SOAP notes, billing data), DocuSign (lien agreements), Gmail/Outlook (attorney communication), Airtable (PI case pipeline dashboard), PDF generation API (narrative reports)
- **Sticky Factor**: PI cases are high-value but extremely documentation-intensive — automation of the case file and attorney communication is the difference between a profitable PI practice and a chaotic one
- **Implementation Notes**: Lien letters must be attorney-reviewed templates that comply with state law. Treatment chronology generation requires pulling all visit notes, dates, and billing codes from the PMS — requires a structured export or API query. Demand package generation should be reviewed by the doctor before sending.

### 13. Decompression & Therapy Scheduling Agent
- **Type**: Workflow + Widget
- **Function**: Manages scheduling and utilization for specialized equipment rooms: spinal decompression tables, cold laser, electric muscle stimulation (EMS), ultrasound, intersegmental traction. Tracks equipment availability in real time. Schedules therapy sessions as add-ons to adjustment appointments or standalone. Sends specific preparation instructions per therapy type. Tracks treatment session count against prescribed protocol. Sends completion alerts when a decompression protocol series is complete. Generates equipment utilization reports to show ROI on capital equipment. Handles multi-therapist scenarios.
- **Trigger**: Therapy prescribed in care plan, appointment booking for therapy, protocol completion milestone, weekly utilization report schedule
- **Integrations**: ChiroTouch / Jane App (scheduling and protocol tracking), Google Calendar (equipment room availability), Twilio SMS (preparation reminders), Google Sheets / Airtable (utilization reporting)
- **Sticky Factor**: Equipment utilization reporting converts a capital expense into a managed revenue center — practices that track it are more likely to invest in additional equipment
- **Implementation Notes**: Equipment room scheduling requires a resource calendar layer on top of provider scheduling. Some PMS systems (ChiroTouch) have built-in therapy scheduling; others require a parallel calendar. Protocol adherence tracking (e.g., 20-session decompression series) is critical for outcome documentation and billing.

### 14. Community Education Workshop Agent
- **Type**: Workflow + Chat
- **Function**: Manages the full lifecycle of community education events: "Lunch and Learn" at local businesses, spine health seminars, "Backpack Safety" school presentations, prenatal wellness workshops, workplace injury prevention programs. Handles event registration, confirmation, and reminder sequences. Sends pre-event educational teaser content. After the event, distributes a follow-up email with free resource (spine health guide, posture checklist) and a new patient offer. Tracks attendee-to-patient conversion rate. Maintains a calendar of upcoming community events and automates invitation outreach to past attendees.
- **Trigger**: Event registration, 48/24-hour pre-event reminders, event completion (triggers follow-up sequence), past attendee re-invitation (new event announced)
- **Integrations**: Eventbrite / Google Forms (registration), Mailchimp / ActiveCampaign (email sequences), Twilio SMS (reminders), ChiroTouch (new patient tracking from event), Canva (event materials)
- **Sticky Factor**: Community events are the highest-trust new patient acquisition channel for chiropractic — the automation makes it repeatable and scalable without added staff time
- **Implementation Notes**: Attendee-to-patient conversion tracking requires a lead source tag in the PMS. Post-event offer should have urgency (7-day window) and a clear CTA (book a free consultation). Lunch-and-learn employer outreach should be systematized in a contact database with follow-up cadence.

### 15. Referral Tracking Agent
- **Type**: Workflow + Dashboard
- **Function**: Manages two referral flows: (1) Inbound MD/specialist referrals — receives referral fax or email, creates a new patient record with referring provider attribution, sends a case acceptance notification to the referring MD, sends periodic progress updates, and sends a case summary letter upon treatment completion. (2) Outbound referrals — tracks patients referred to specialists (neurologists, orthopedists, pain management), sends follow-up to confirm specialist appointment was made, tracks outcome. Generates a referral relationship dashboard showing top referral sources, reciprocal referral rate, and case outcomes.
- **Trigger**: Referral fax received, new patient chart creation with referral source, outbound referral entered, case completion, monthly referral report schedule
- **Integrations**: Phaxio / eFax (fax API), ChiroTouch (referral source field), Gmail/Outlook, Airtable (referral relationship database), Google Sheets (referral dashboard)
- **Sticky Factor**: MD referral relationships are the highest-value new patient source — systematic communication (progress updates, case summaries) turns a one-time referral into a recurring pipeline
- **Implementation Notes**: Case summary letters to referring MDs must be reviewed and approved by the doctor before sending — these are medico-legal documents. Referral reciprocity tracking (how often you refer back to each MD) should inform the outreach and relationship management strategy.

### 16. Membership & Wellness Plan Manager
- **Type**: Workflow + Widget + Dashboard
- **Function**: Manages the practice's monthly wellness/maintenance care membership plans. Handles plan enrollment, agreement e-signature, and automated monthly billing via Stripe/payment processor. Tracks visit utilization per member (visits used vs. plan allowance). Sends monthly benefit reminders showing remaining visits ("You have 2 of your 4 monthly visits remaining — book now!"). Processes plan renewals and cancellation requests. Handles failed payment retry sequences. Generates a membership revenue dashboard showing MRR, active members, churn rate, and average plan value. Provides patient portal view of membership status.
- **Trigger**: New membership enrollment, monthly billing cycle, failed payment, plan renewal date, low utilization alert (member hasn't visited in 3+ weeks), cancellation request
- **Integrations**: Stripe (recurring billing), DocuSign (membership agreement), ChiroTouch / Jane App (visit tracking), Twilio SMS (utilization reminders and billing alerts), Airtable / Google Sheets (MRR dashboard), patient portal
- **Sticky Factor**: Membership revenue is the most predictable revenue stream in chiropractic — once MRR reaches $10K+/month, the practice is fundamentally transformed from a transactional to a subscription business
- **Implementation Notes**: Membership plan design (visit allowance, pricing, included services) has a significant impact on utilization and profitability — model carefully before launch. Failed payment retry logic should attempt 3 times over 5 days before suspending access. Cancellation flow should include a save attempt with a modified plan offer.

### 17. Patient Education Content Delivery Agent
- **Type**: Workflow + Chat
- **Function**: Delivers condition-specific educational content to patients throughout their care journey. Triggered by diagnosis: a patient with cervical disc herniation receives a series of educational touchpoints — understanding their diagnosis, what to expect during treatment, at-home care tips, activity modifications, long-term prevention. Content includes short videos (2-3 minutes), infographics, and articles. Content is dripped over the course of treatment at relevant intervals. Includes "ask a question" CTA that routes to the practice's communication agent. Tracks content engagement and adjusts delivery based on opens/clicks.
- **Trigger**: Diagnosis entered in PMS, care plan stage advancement, patient question submitted, weekly educational content schedule
- **Integrations**: ChiroTouch / Jane App (diagnosis data), ActiveCampaign / Mailchimp / Twilio SMS (content delivery), YouTube / Loom (video hosting), Airtable (content library and engagement tracking), patient portal
- **Sticky Factor**: Patients who understand their condition are more compliant with care plans and more likely to refer — education directly impacts both retention and referral rate
- **Implementation Notes**: Content library should cover top 20 diagnoses seen in the practice (cervical subluxation, lumbar disc, sacroiliac dysfunction, headache, sciatica, etc.). Video content performs significantly better than text for healthcare education. Content engagement data can be shared with the doctor to identify patients who may need additional clinical education at their next visit.

---

## Industry-Specific Intake Forms

### New Patient Health History Intake
- Chief complaint (primary reason for visit)
- Pain body map (location, type, severity 1-10)
- Symptom onset date and circumstances
- Prior treatment history (chiropractic, PT, surgery, injections)
- Current medications and supplements
- Past medical history (fractures, osteoporosis, cancer history, stroke)
- Pregnancy status (for female patients)
- Occupation and daily activity level
- Sleep quality and position
- Insurance information and attorney information (if PI case)
- HIPAA acknowledgment and financial policy signature

### Care Plan Commitment Form
- Patient acknowledgment of recommended visit frequency
- Acknowledgment of expected outcome timeline
- Financial responsibility understanding
- Home care compliance commitment
- Emergency contact information

### Wellness Membership Enrollment
- Membership tier selection
- Monthly billing authorization
- Preferred visit scheduling cadence
- Emergency contact
- Agreement to membership terms and cancellation policy

---

## Interactive Widgets & Tools

| Widget | Description | Platform |
|--------|-------------|----------|
| Body Map Pain Assessment | Tapable front/back body diagram with severity rating | IntakeQ, custom HTML5 Canvas |
| Online Scheduling Widget | 24/7 self-scheduling with provider matching | Jane App, ChiroTouch Online |
| Insurance Benefits Calculator | Estimated out-of-pocket cost based on benefits | Custom form + clearinghouse API |
| Ergonomic Assessment Tool | Workspace assessment with scored recommendations | Typeform, custom web app |
| Patient Health Dashboard | Progress chart (pain scores over time, visits remaining) | Patient portal, custom Airtable view |
| Membership Plan Comparison | Interactive plan selector with feature comparison | Webflow / Squarespace embed |
| Home Exercise Program Portal | Video library of prescribed exercises with progress tracking | MedBridge, HEP2go, custom portal |

---

## Employee Role Mapping

| Role | Agents They Use Daily | Time Saved/Week |
|------|-----------------------|-----------------|
| Front Desk | New Patient Intake Voice, Scheduling, Insurance Verification | 15-20 hrs |
| Chiropractor (DC) | Post-Adjustment Follow-Up, Treatment Plan Agent, PI Case Manager | 6-8 hrs |
| Billing/Insurance | Insurance Verification, AR Follow-Up, Sales Tax Agent | 10-12 hrs |
| Massage Therapist | Therapy Scheduling, Post-Appointment Follow-Up | 3-4 hrs |
| Practice Manager | Membership Manager, Referral Tracker, Dashboard | 5-6 hrs |
| Marketing Coordinator | Community Workshop Agent, Patient Education, Reactivation | 8-10 hrs |

---

## Integration Architecture

```
PATIENT ACQUISITION LAYER
Website / Calls / Referrals / Events
→ New Patient Intake Voice Agent + Scheduling Agent → PMS (ChiroTouch / Jane App)

PRE-VISIT LAYER
New Patient Booking → Insurance Verification Agent + Pain Assessment Form
→ Benefits Summary to Patient + Case Brief to Doctor

IN-OFFICE LAYER
Doctor Exam → Treatment Plan Agent → e-Signature → Care Plan Initiated
Doctor Order → Imaging Coordination Agent / Therapy Scheduling Agent

ACTIVE CARE LAYER
Each Visit → Post-Adjustment Follow-Up Agent
Care Plan Active → Exercise Delivery + Patient Education + Ergonomic Tool
PI Case Flagged → PI Case Management Agent (parallel track)

RETENTION LAYER
Monthly → Wellness Product Recommendations + Progress Dashboard Update
Membership → Billing Agent + Utilization Reminders
Lapsed → Reactivation Agent (30/60/90-day triggers)

GROWTH LAYER
Referral Tracking Agent (MD relationships)
Community Workshop Agent (events → new patients)
NPS / Review Agent (satisfaction → Google Reviews → new patient trust)
```

---

## Competitive Intelligence

| Competitor Type | Their Weakness | Your AI Advantage |
|-----------------|----------------|-------------------|
| Solo DC (no tech) | Manual intake, no follow-up system, drops PI cases | Automated lifecycle + PI case precision |
| Large franchise networks | Impersonal, protocol-driven, high turnover | AI personalization preserves the DC's relationship quality |
| Physical therapy clinics | No chiropractic philosophy, limited wellness services | Full wellness ecosystem with product + membership revenue |
| Direct Primary Care / Concierge MD | High cost, no manual therapy | Accessible price point + hands-on care + AI patient experience |

**Key Differentiators to Market:**
- "Your care plan, explained in plain English before you even walk in"
- "We check in after every adjustment — we never let you wonder how you're doing"
- "PI cases managed with the same precision as a legal case management firm"

---

## Revenue Model

| Stream | AI Enhancement | Revenue Lift Potential |
|--------|----------------|------------------------|
| New Patient Volume | Voice intake + after-hours booking | +20-35% new patient capture |
| Case Value (Visit Count) | Post-adjustment follow-up + care plan agent | +30% care plan completion |
| Membership / Wellness Plans | Billing automation + utilization reminders | Predictable MRR, reduced churn |
| Supplement / Product Sales | Recommendation engine | +15-25% retail revenue |
| PI Cases | Case management agent | 2-3x PI case capacity |
| Community Events | Workshop agent | 5-10 new patients per event, systematized |
| Reactivation | Lapsed patient agent | 15-25% reactivation rate on database |

---

## Stickiest Features (Top 5)

1. **New Patient Intake Voice Agent** — The first time a practice books a new patient at 10:30pm who called after hours, and that patient shows up the next morning with a complete health history already in the chart, the front desk is permanently converted. No front desk will willingly give up after-hours capture.

2. **Post-Adjustment Follow-Up Agent** — Patients who receive a check-in 2 hours after their adjustment report feeling "genuinely cared for." This single touchpoint has a measurable impact on Google review volume and patient referrals — both directly measurable by the practice.

3. **PI Case Management Agent** — Personal injury case management is the most documentation-intensive workflow in chiropractic. A practice that can handle 30 active PI cases with the same quality as 10 will see dramatically higher revenue per DC, and the attorney relationships built through systematic communication become a recurring referral pipeline.

4. **Insurance Verification & Benefits Explanation** — Financial surprises at the front desk are the #1 cause of new patient no-shows and early dropout. When patients arrive knowing exactly what their insurance covers and what they'll pay, trust is established before the first adjustment. The practice that eliminates billing surprises has a structural retention advantage.

5. **Membership & Wellness Plan Manager** — Monthly recurring revenue fundamentally changes the financial character of a chiropractic practice. When the membership manager automates billing, sends utilization reminders, and tracks MRR in real time, the doctor sees a predictable monthly base income that reduces the anxiety of a purely appointment-driven model — and they will never go back to transactional-only care.
