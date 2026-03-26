# Batch 3: Industry-Specific AI Skills — Group B (Skills 081–120)

**Version**: 1.0  
**Created**: March 2026  
**Author**: AI Skills Catalog System  
**Total Skills**: 40  
**Skill Range**: 081–120

---

## Overview

This catalog contains 40 fully deployable AI skill and sub-agent definitions across 9 industry verticals. Each skill is designed for immediate deployment by an AI agency, SaaS platform, or systems integrator serving small-to-mid-size businesses. All definitions include deployment platform guidance, integration points, sample prompts, and upsell paths.

### Industry Coverage

| Skill Range | Industry | Skills |
|-------------|----------|--------|
| 081–085 | Salon / Spa / Beauty | 5 |
| 086–090 | Veterinary | 5 |
| 091–095 | Fitness / Gym | 5 |
| 096–100 | Property Management | 5 |
| 101–104 | Recruitment / Staffing | 4 |
| 105–108 | Construction | 4 |
| 109–112 | E-Commerce | 4 |
| 113–116 | Coaching / Consulting | 4 |
| 117–120 | Accounting | 4 |

### Complexity Distribution
- **Low**: 0 skills
- **Medium**: 16 skills
- **High**: 24 skills

### Monthly Value Range (per skill)
- **Entry level**: $400/month
- **Mid-tier**: $800–$1,800/month
- **Premium**: $2,000–$4,000/month

### Deployment Platforms Used
Vapi, GHL (GoHighLevel), Make (Integromat), Zapier, Claude, Shopify, Klaviyo, Mindbody, Procore, BuilderTREND, AppFolio, Buildium, Bullhorn, Greenhouse, QuickBooks, Xero, Kajabi, Teachable, TaxDome, Liscio, Custom Web, Twilio, WhatsApp Business, DocuSign, Trainerize, Vagaro, Booksy, ezyVet, Cornerstone

---

# PART 1: SALON / SPA / BEAUTY (081-085)

---

## SKILL-081: AI Style Consultation Widget

**Category**: Widget/Tool
**Applies To**: Salon / Spa / Beauty
**Deployment Platform**: Custom (Web Embed), GHL, Shopify, Vagaro
**Complexity**: High
**Monthly Value to Client**: $800 - $2,500

### What It Does
An interactive web widget that allows salon visitors to upload a selfie and virtually try on different hairstyles, colors, and cuts using AI image generation and augmented reality overlays. It captures lead information before showing results and seamlessly connects the client's chosen look to an online booking flow, driving appointment conversions directly from the consultation.

### Core Capabilities
- Photo upload with mobile camera support and selfie detection
- AI-generated virtual try-on for 50+ hairstyle templates and unlimited color swatches
- Skin tone analysis to suggest flattering color palettes
- Saved "look board" that clients can share or email to themselves
- Lead capture gate (name + email + phone) before results are revealed
- One-click booking flow connected to the salon's scheduling system
- Stylist match suggestion based on chosen style specialties
- Results page with service pricing estimate for the chosen look

### Data Inputs Required
- Client-uploaded photo (selfie)
- Salon's service menu with pricing
- Stylist profiles and specialty tags
- Booking system API credentials (Vagaro, Square, Booksy, Mindbody)
- Brand color palette and logo for widget theming

### Integration Points
- Vagaro / Square Appointments / Booksy / Mindbody — for real-time booking
- GHL CRM — lead capture and follow-up sequence triggers
- Email/SMS platform — sends saved look board to client
- Meta Ads / Google Ads — retargeting pixel fires on widget engagement
- Salon website (iframe embed or JS snippet)

### Sample Prompt/Persona
> "Welcome to [Salon Name]'s virtual style suite! I'm your AI style advisor. Upload a quick selfie and I'll show you exactly how you'd look with different cuts and colors. Everything is private — your photo is only used to generate your previews. Once you find a look you love, I'll connect you with the perfect stylist and get you booked in minutes."

### Customization Variables
- `salon_name` — branding throughout
- `style_catalog` — hairstyle/color options specific to what the salon offers
- `booking_url` or API key — destination for conversions
- `lead_gate_timing` — immediate vs. after first preview
- `price_display` — show/hide service estimates
- `stylist_roster` — photos and bios for match feature
- `brand_colors` and `logo_url` — visual theming

### Stickiness Factor
High. Clients return to the widget before every appointment to plan their new look. The saved look board feature creates an ongoing digital relationship between client and salon, reducing churn. Lead data flows into CRM for automated re-engagement.

### Upsell Path
- Upgrade to AI video consultation with live stylist (premium tier)
- Add-on: "Color Match Kit" — e-commerce product recommendations for home maintenance
- Expand to nail/makeup virtual try-on module
- White-label licensing to other salons in the agency's portfolio

---

## SKILL-082: AI Smart Upsell Agent

**Category**: Chat Agent
**Applies To**: Salon / Spa / Beauty
**Deployment Platform**: GHL, Vagaro, SMS/MMS, Klaviyo
**Complexity**: Medium
**Monthly Value to Client**: $600 - $1,800

### What It Does
An intelligent post-booking and pre-appointment agent that analyzes each client's service history, average spend, time since last visit, and upcoming appointment type to suggest personalized add-ons and complementary services. It delivers upsell recommendations via SMS or email at the optimal moment in the booking journey — reducing no-show anxiety while meaningfully increasing average ticket value.

### Core Capabilities
- Service history analysis to identify upsell gaps (e.g., no conditioning treatment in 4 visits)
- Time-since-last-visit triggers (e.g., 10 weeks since last cut → suggest trim add-on)
- Appointment-type logic (color appointment → suggest gloss, toner, or deep condition)
- Pre-appointment SMS/email with personalized "add to your service" suggestions
- In-conversation booking modification — client replies "yes" and add-on is appended
- Revenue uplift tracking dashboard
- Seasonal and promotional upsell injection (e.g., holiday packages)
- Staff commission-aware routing — suggests services performed by the booked stylist

### Data Inputs Required
- Client booking history (service types, dates, prices)
- Full service menu with add-on compatibility matrix
- Staff service capability list
- Booking system API access (Vagaro, Booksy, Square)
- Average service duration for scheduling compatibility checks

### Integration Points
- Vagaro / Booksy / Square — reads history and modifies bookings
- GHL CRM — client segmentation and sequence triggers
- Twilio / SMS — outbound message delivery
- Klaviyo / Mailchimp — email upsell flows
- POS System — revenue tracking and ROI reporting

### Sample Prompt/Persona
> "Hey [Client Name]! Your [Service] with [Stylist] is coming up on [Date]. Based on your last few visits, your stylist thinks this would be the perfect time to add a [Recommended Service] — it takes just 15 extra minutes and leaves your hair feeling incredible. Want to add it for just $[Price]? Reply YES and we'll add it to your appointment automatically."

### Customization Variables
- `upsell_logic_rules` — which services trigger which add-on suggestions
- `message_timing` — how many days/hours before appointment to send
- `max_upsells_per_message` — 1–3 suggestions cap
- `discount_threshold` — whether to attach a limited-time discount
- `stylist_filter` — only suggest services the booked stylist performs
- `tone` — casual, professional, or luxury depending on salon brand

### Stickiness Factor
Very high. As the agent builds a longer service history it becomes more accurate, creating a compounding data flywheel. Salons see measurable ticket lift within 30 days and become dependent on the revenue uplift.

### Upsell Path
- Upgrade to real-time in-chair upsell via tablet-based chat widget
- Add retail product recommendation module (home care upsells)
- Bundle with SKILL-083 (Client Preference Memory) for hyper-personalized messaging
- Monthly performance reporting add-on for multi-location salon groups

---

## SKILL-083: AI Client Preference Memory Agent

**Category**: Operations
**Applies To**: Salon / Spa / Beauty
**Deployment Platform**: GHL, Custom CRM, Vagaro, Notion API
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,200

### What It Does
A persistent client intelligence layer that captures, stores, and surfaces every stylistically and personally relevant detail about each client — from exact color formulas and processing times to preferred beverages, conversation topics, and seating preferences. Before each appointment, the agent briefs the assigned stylist with a personalized client dossier, eliminating the "tell me again" experience and dramatically increasing client loyalty.

### Core Capabilities
- Structured color formula storage (developer ratio, brand, shade, processing time, results notes)
- Preferred product inventory tracking with substitution alerts when products discontinue
- Personal preference capture: beverages, music genre, conversation style, topics to avoid
- Post-appointment notes collection via stylist-facing form or voice memo transcription
- Pre-appointment briefing doc auto-generated and sent to stylist's phone 30 min before
- Birthday and anniversary reminders with personalized outreach
- Client anniversary milestones (1 year, 5 years) trigger loyalty reward suggestions
- Cross-stylist access so any fill-in stylist can deliver a consistent experience

### Data Inputs Required
- Initial client intake form (preferences, allergies, color history)
- Post-appointment stylist notes (structured form or free-text/voice)
- Booking system data for appointment history
- Product catalog for formula ingredient tracking
- Staff scheduling data for stylist assignment

### Integration Points
- Vagaro / Booksy / Square — appointment and history sync
- GHL CRM — master client record and automation hub
- Twilio SMS / WhatsApp — stylist briefing delivery
- Google Forms / JotForm / Typeform — intake and post-appointment data capture
- Notion or Airtable — optional human-readable client card database

### Sample Prompt/Persona
> [Stylist-facing briefing mode] "Good morning, [Stylist Name]. Your 10 AM client [Client Name] is coming in for a balayage. Last visit notes: Used Wella Illumina 7/81 + 6% developer, 35-minute processing. She prefers oat milk in her coffee, loves talking about her rescue dogs (two golden retrievers — Biscuit and Clover). She mentioned last time she was nervous about going lighter — reassure her with a before/after visual. She tipped 25% last visit."

### Customization Variables
- `formula_fields` — custom fields for the salon's preferred color lines
- `preference_categories` — beverage, music, conversation, allergies, seating
- `briefing_lead_time` — minutes before appointment to send stylist briefing
- `note_capture_method` — form, voice memo, or chat conversation post-appointment
- `client_milestones` — configure which anniversaries trigger automated outreach
- `cross_stylist_visibility` — on/off toggle per staff member role

### Stickiness Factor
Extremely high. This system becomes the institutional memory of the salon. Stylists become reliant on it for quality delivery. Clients who experience the personalization become highly loyal. Switching costs are enormous — years of preference data would be lost.

### Upsell Path
- Add AI-powered formula suggestion engine (recommends next color step based on history)
- Integrate with retail POS for product repurchase reminders ("She's been using X for 6 months — time to reorder")
- Bundle with SKILL-082 for a full client lifecycle revenue system
- Multi-location enterprise version with centralized client profiles

---

## SKILL-084: AI Wedding/Event Package Agent

**Category**: Chat Agent + Workflow Automation
**Applies To**: Salon / Spa / Beauty
**Deployment Platform**: GHL, Vapi, Custom Web, Honeybook
**Complexity**: High
**Monthly Value to Client**: $1,000 - $3,500

### What It Does
A dedicated AI agent that handles the full lifecycle of bridal and event group bookings — from initial inquiry through trial appointments, day-of coordination, and post-event follow-up. It manages the complexity of multi-person group bookings (bridesmaids, mothers, flower girls), handles contracts and deposits, and coordinates logistics so the salon owner doesn't lose hours to email chains managing a single wedding party.

### Core Capabilities
- Initial inquiry intake: wedding date, party size, services per person, venue location
- Automated package pricing calculator with tiered options
- Trial appointment scheduling for bride (separate from wedding day slot)
- Group scheduling logic — blocks multiple chairs and stylists simultaneously
- Contract generation with deposit terms and cancellation policy
- Payment link generation and deposit collection tracking
- Day-of timeline builder (calculates chair time needed per person and creates a schedule)
- Automated reminder sequences (3 months, 1 month, 1 week, 1 day before)
- Post-wedding follow-up for reviews and referrals

### Data Inputs Required
- Salon capacity (number of chairs, stylists, hours available on event dates)
- Service duration by type (updo, blowout, makeup application, etc.)
- Bridal package pricing tiers
- Contract template with customizable terms
- Payment processor credentials (Stripe, Square)

### Integration Points
- GHL — full CRM and pipeline tracking for each wedding inquiry
- Honeybook / Dubsado — contract and invoice management (optional)
- Google Calendar / Vagaro — multi-chair block booking
- Stripe / Square — deposit collection and payment tracking
- DocuSign / HelloSign — electronic contract signatures
- Vapi — voice-based inquiry intake for phone calls

### Sample Prompt/Persona
> "Congratulations on your engagement! I'm [Salon Name]'s wedding coordinator. I'd love to help make your beauty day absolutely perfect. Let's start with a few questions: What's your wedding date? How many people will need services — just yourself, or a full bridal party? And what services are you envisioning — hair, makeup, or both? I'll build a custom package for you right now."

### Customization Variables
- `package_tiers` — standard, premium, luxury with price points
- `capacity_rules` — max party size, blackout dates, deposit percentage
- `contract_template` — salon-specific terms and cancellation policy
- `payment_schedule` — deposit at booking, balance 30 days before, etc.
- `reminder_cadence` — configurable milestone-based sequence timing
- `referral_incentive` — post-wedding referral offer details

### Stickiness Factor
High. Bridal bookings are high-revenue, high-complexity events. Once a salon adopts this system and has historical wedding data flowing through it, manually managing weddings becomes unthinkable. Referrals from wedding parties also feed the system new leads.

### Upsell Path
- Add makeup artist coordination module (sub-contractor scheduling)
- On-location/mobile service booking extension
- Bundle with SKILL-083 (Preference Memory) so the bride's preferences become a permanent client profile
- Photography partnership integration — connect with local wedding photographers for cross-referrals

---

## SKILL-085: AI Salon Social Media Content Generator

**Category**: Content Engine
**Applies To**: Salon / Spa / Beauty
**Deployment Platform**: Make (Integromat), Zapier, GHL, Buffer, Later
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,500

### What It Does
An automated content pipeline that transforms before-and-after service photos submitted by stylists into branded, platform-optimized social media posts, stories, and reel scripts. The agent writes captions with relevant hashtags, generates post copy in the salon's brand voice, and queues content directly into the salon's social scheduling tool — eliminating the #1 reason salons neglect social media: time.

### Core Capabilities
- Before/after photo intake via stylist mobile upload (WhatsApp, email, or custom app)
- AI caption writing with brand voice matching and configurable tone
- Platform-specific formatting: Instagram post, Story text overlay, Reel script/voiceover
- Hashtag research and injection (location-based, style-based, trending)
- Content calendar management — spaces posts evenly throughout the week
- Service tag and stylist credit injection in captions
- Booking link or CTA appended to every post
- Monthly analytics report: engagement rates, follower growth, top-performing content

### Data Inputs Required
- Photo submissions from stylists (with service type and client consent flag)
- Brand voice guide (adjectives, tone, signature phrases)
- Approved hashtag library
- Social media account credentials (via Buffer/Later API)
- Booking link and promotional offers for CTAs

### Integration Points
- WhatsApp / Email / Google Drive — photo intake channels
- OpenAI GPT-4o — caption and script generation
- Buffer / Later / Planoly — content scheduling
- Instagram Graph API — direct posting and analytics
- GHL — CRM tie-in for promotional offer injection
- Google Sheets / Airtable — content calendar tracking

### Sample Prompt/Persona
> [Internal content generation mode] "New photo received from [Stylist Name]: Before/after balayage. Service tag: Balayage + Gloss Treatment. Generate three caption options for this post. Option 1: educational (explain the balayage process). Option 2: transformation-focused (emotional before/after). Option 3: seasonal (summer highlight angle). Include location hashtags for [City], [Neighborhood], and top 10 balayage hashtags. Append booking CTA with link."

### Customization Variables
- `brand_voice_profile` — luxury, approachable, edgy, natural/organic, etc.
- `post_frequency` — posts per week per platform
- `stylist_credit_format` — how to tag individual stylists
- `consent_workflow` — require stylist to confirm client consent before publishing
- `cta_rotation` — cycle through booking, review, referral, and product CTAs
- `seasonal_themes` — inject seasonal angles automatically

### Stickiness Factor
High. Once the content pipeline is running, social media essentially manages itself. Salons that see consistent follower growth and booking attribution become locked in. The content library also serves as an SEO and brand asset over time.

### Upsell Path
- Add paid ad creation: turn top organic posts into Meta/Instagram ad creatives
- Google Business Profile post automation add-on
- Bundle with influencer collaboration outreach agent
- Video editing automation for Reels (AI-generated text overlays, music sync)
# PART 2: VETERINARY (086-090)

---

## SKILL-086: AI Pet Symptom Assessment & Triage Agent

**Category**: Diagnostic
**Applies To**: Veterinary
**Deployment Platform**: Vapi, GHL, Custom Web Chat, Twilio
**Complexity**: High
**Monthly Value to Client**: $800 - $2,500

### What It Does
An AI-powered triage agent that allows pet owners to describe symptoms in natural language and optionally upload photos or short videos of their pet. The agent conducts a structured symptom assessment, produces a 1–5 urgency score with clear plain-language explanation, and directs the owner to the appropriate next step — from "monitor at home" to "go to emergency care now." It operates 24/7, reducing after-hours emergency calls while ensuring genuinely sick animals get prompt attention.

### Core Capabilities
- Natural language symptom intake via chat or voice (Vapi)
- Photo and short video upload analysis for visible symptoms (wounds, swelling, discharge, posture)
- Species and breed-specific symptom weighting (e.g., bloat risk higher in large deep-chested breeds)
- Urgency scoring 1–5 with color-coded output (1=Monitor, 5=Emergency Now)
- Structured triage report emailed to owner and flagged in practice management system
- Automatic escalation path: urgency 4–5 triggers immediate callback request or live call transfer
- After-hours emergency clinic directory with distance and hours
- Symptom log stored to patient record for review at next appointment

### Data Inputs Required
- Owner-submitted symptom description (free text or voice)
- Pet profile: species, breed, age, weight, existing conditions, current medications
- Practice emergency protocol thresholds (what constitutes a call-in vs. hold)
- Emergency clinic network list for referral routing
- Practice management system API (Avimark, Cornerstone, Pulse, ezyVet)

### Integration Points
- Vapi — voice-based triage calls for after-hours phone tree
- ezyVet / Cornerstone / Avimark — patient record updates and appointment creation
- Twilio SMS — urgency score and recommendation delivery to owner
- GHL CRM — lead and patient follow-up sequences
- Google Maps API — nearest emergency clinic lookup
- OpenAI GPT-4o Vision — photo/video symptom analysis

### Sample Prompt/Persona
> "Hi, I'm [Clinic Name]'s 24/7 pet health line. I'm here to help you figure out if [Pet's Name] needs to be seen right away or if it's safe to monitor at home. I'll ask you a few quick questions about what you're noticing. I'm not a replacement for your vet, but I can help you make the right call tonight. What's going on with [Pet's Name] right now?"

### Customization Variables
- `species_list` — dogs, cats, rabbits, birds, reptiles, exotic (enable/disable)
- `urgency_thresholds` — customize what scores trigger which escalation actions
- `emergency_clinic_list` — local/regional emergency care partners
- `callback_trigger_level` — urgency score at which live callback is offered
- `practice_hours` — adjusts behavior during open vs. after-hours
- `disclaimer_language` — state-specific veterinary advice disclaimer

### Stickiness Factor
Very high. Pet owners who use the service after hours form an immediate trust bond with the clinic. The triage history becomes medically valuable context. Practices that adopt this never return to an unmanaged after-hours phone line.

### Upsell Path
- Upgrade to include real-time video consult with on-call vet tech (telehealth add-on)
- Integrate with pet insurance platforms (Trupanion, Nationwide) for claim pre-authorization
- Bundle with SKILL-087 (Vaccination Reminders) and SKILL-090 (Multi-Pet Manager) for full preventive care platform
- White-label for veterinary group practices with shared triage infrastructure

---

## SKILL-087: AI Vaccination & Preventive Care Reminder Agent

**Category**: Workflow Automation
**Applies To**: Veterinary
**Deployment Platform**: GHL, Twilio, Mailchimp, ezyVet
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,200

### What It Does
An automated preventive care communication engine that tracks every pet patient's vaccination and wellness schedule, calculates due dates based on the last administered date and protocol intervals, and delivers timely, personalized reminders via SMS, email, or postcards. It dramatically reduces the administrative burden on front desk staff while recapturing revenue from lapsed wellness visits that would otherwise be lost.

### Core Capabilities
- Vaccination schedule import and due-date calculation (Rabies 1yr/3yr, DHPP, Bordetella, Leptospirosis, FeLV, FVRCP, etc.)
- Heartworm, flea/tick, and parasite prevention interval tracking
- Multi-channel reminder delivery: SMS, email, automated voice call, printed postcard
- Escalating reminder sequence: 60 days out → 30 days → 7 days → overdue notice
- Owner-facing reply to book directly from the reminder message
- Lapsed patient reactivation flag (6+ months overdue → special reactivation offer)
- Customizable reminder templates per vaccine type and species
- Monthly compliance report: % of patients current on each protocol

### Data Inputs Required
- Patient vaccination history with administration dates
- Clinic's standard vaccination protocol intervals per species/lifestyle
- Owner contact preferences (SMS, email, phone)
- Booking system access for direct scheduling links
- Practice management system export (Avimark, Cornerstone, Pulse, ezyVet)

### Integration Points
- ezyVet / Cornerstone / Avimark / Pulse — patient record read and write
- GHL — contact management and reminder sequence execution
- Twilio SMS — reminder delivery
- Mailchimp / Klaviyo — email reminder flows
- Lob.com — automated postcard printing and mailing for direct mail reminders
- Online booking system — appointment conversion from reminder

### Sample Prompt/Persona
> "Hi [Owner Name]! Just a friendly heads-up from [Clinic Name]: [Pet Name] is due for [Vaccine/Service] in [X days/weeks]. Keeping up with this protects [Pet Name] from [Disease/Condition] and is required for [boarding/dog parks/travel]. Tap the link to book in under 2 minutes: [booking_link]. Questions? Reply to this message. 🐾"

### Customization Variables
- `protocol_intervals` — clinic's specific schedule for each vaccine/service
- `reminder_sequence_timing` — days before/after due date for each touchpoint
- `channel_priority` — default channel and fallback order
- `lapsed_threshold_days` — when a patient is considered overdue for reactivation
- `promotional_offer` — optional discount or incentive for overdue patients
- `species_protocols` — separate configurations for dogs, cats, and exotic species

### Stickiness Factor
High. The system ingests the clinic's entire patient database and becomes the backbone of revenue cycle management. Compliance rate improvements are measurable and visible, making the ROI undeniable within 60 days.

### Upsell Path
- Add dental cleaning and senior wellness exam reminder modules
- Upgrade to include proactive health tips content (monthly pet health newsletter)
- Bundle with SKILL-086 (Triage) and SKILL-090 (Multi-Pet Manager)
- Two-way SMS conversation upgrade for owners to ask questions via the reminder thread

---

## SKILL-088: AI Breed-Specific Health Alert System

**Category**: Workflow Automation
**Applies To**: Veterinary
**Deployment Platform**: GHL, Custom, Mailchimp
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,400

### What It Does
A proactive pet health education and alert engine that delivers breed-appropriate, age-triggered health guidance to pet owners. As a patient's pet ages through key life stages, the system automatically sends targeted educational content about conditions statistically common in that breed — prompting owners to schedule proactive screenings before problems become emergencies.

### Core Capabilities
- Breed database covering 350+ dog breeds and 70+ cat breeds with condition prevalence data
- Age-milestone triggers for each breed (e.g., German Shepherd at age 5 → hip dysplasia screening alert)
- Educational content library with vet-reviewed breed-specific articles
- Proactive appointment prompts embedded in health alerts
- Owner-facing "My Breed's Health Timeline" view (optional web portal)
- Condition-specific screening product or service recommendation injection
- Prevalence statistics and early warning signs per condition
- Monthly clinic-branded breed health newsletter generation

### Data Inputs Required
- Patient breed and date of birth from practice management system
- Clinic's diagnostic and preventive service offerings (screening panels available)
- Breed health condition database (integrated or custom)
- Owner contact information and communication preferences
- Pricing for recommended screenings and services

### Integration Points
- ezyVet / Cornerstone — patient breed and DOB data
- GHL — contact segmentation by breed and age milestones
- Mailchimp / Klaviyo — email alert and newsletter delivery
- Twilio SMS — high-priority alert delivery
- Online booking — embedded scheduling links in alerts
- Custom breed database API or internal content library

### Sample Prompt/Persona
> "Hey [Owner Name]! [Pet Name] just turned [Age] — happy birthday! As a [Breed], this is a great time to talk about [Condition]. [Breed] are [X]x more likely to develop [Condition] than the average dog, and the best outcomes happen when we catch it early. We offer a [Screening Name] right here at [Clinic Name]. Want to schedule [Pet Name]'s check-up this month? [Book Now link]"

### Customization Variables
- `breed_database_source` — built-in, custom clinic-uploaded, or integrated API
- `alert_trigger_ages` — configurable by breed and condition
- `content_tone` — educational, conversational, or clinical
- `service_recommendations` — which clinic services map to which conditions
- `newsletter_frequency` — monthly, quarterly, or triggered only
- `clinic_branding` — logo, colors, vet signature on all communications

### Stickiness Factor
High. This system positions the clinic as the most knowledgeable, proactive care partner a pet owner can have. Owners who receive relevant, accurate, timely breed-specific health information develop exceptionally strong loyalty. Content becomes a competitive differentiator.

### Upsell Path
- Add exotic/specialty breed support (reptiles, birds, rabbits)
- Upgrade to personalized genetic health alerts using Embark/Wisdom Panel DNA data integration
- Bundle with SKILL-087 for comprehensive preventive care platform
- License breed content library to pet insurance companies or pet retailers

---

## SKILL-089: AI Pet Nutrition & Diet Recommendation Engine

**Category**: Chat Agent + Widget/Tool
**Applies To**: Veterinary
**Deployment Platform**: Custom Web, GHL, WhatsApp
**Complexity**: Medium
**Monthly Value to Client**: $400 - $1,100

### What It Does
An interactive nutrition advisor that collects a pet's breed, age, weight, body condition score, activity level, and any existing health conditions, then generates a tailored diet and feeding plan with specific food type recommendations, daily caloric targets, portion sizes, and guidance on transitioning to a new diet. It bridges the gap between generic pet food marketing and veterinary-grade nutrition guidance.

### Core Capabilities
- Conversational intake: species, breed, age, weight, body condition score (BCS), activity level
- Condition-specific diet filtering: renal disease, diabetes, allergies, IBD, joint issues, cardiac conditions
- Commercial food recommendations with brand and formula specifics
- Homemade/raw diet guidance with veterinary safety caveats
- Daily caloric needs calculation with portion size output
- Feeding frequency recommendations by age and size
- Weight management plan generation for overweight pets
- Monthly reassessment prompts based on weight check-in data

### Data Inputs Required
- Pet profile (species, breed, age, weight, BCS)
- Owner dietary preferences (commercial, raw, home-cooked, prescription)
- Diagnosed health conditions from medical records
- Clinic's preferred nutrition product line (Royal Canin, Hill's, Purina Pro Plan, etc.)
- Body weight history for trend-aware recommendations

### Integration Points
- ezyVet / Cornerstone — pulls health conditions and weight history
- Custom web widget or GHL chat — owner-facing interface
- WhatsApp Business — conversational nutrition check-ins
- Clinic's online store — links to recommended food products for purchase
- Hill's / Royal Canin / Purina partner portal — product data integration

### Sample Prompt/Persona
> "I'm [Clinic Name]'s nutrition advisor. I can build a customized feeding plan for your pet based on their specific needs — no guesswork, no generic bag-of-food instructions. Let's start: what's your pet's name, species, and breed? And has your vet diagnosed any health conditions I should factor in? I'll have a personalized plan ready in about 3 minutes."

### Customization Variables
- `preferred_brands` — clinic's recommended or stocked food brands
- `prescription_diet_flags` — conditions that trigger a "consult vet before changing diet" gate
- `bcs_scale` — 5-point or 9-point body condition scoring
- `unit_system` — metric or imperial
- `revenue_link` — in-clinic or online store product recommendations
- `homemade_diet_guidance` — enable/disable based on clinic's philosophy

### Stickiness Factor
Medium-high. Owners who receive a specific, personalized feeding plan are more engaged with their pet's health and return to the clinic more frequently for weight checks and follow-ups. The tool also drives product revenue if connected to a clinic store.

### Upsell Path
- Add veterinary nutritionist consult upgrade for complex cases
- Integrate with weight loss program tracking (monthly weigh-in check-ins)
- Bundle with SKILL-087 and SKILL-088 for full wellness platform
- License to pet food retailers for branded nutrition advisory tools

---

## SKILL-090: AI Multi-Pet Family Manager

**Category**: Operations + Chat Agent
**Applies To**: Veterinary
**Deployment Platform**: GHL, Custom Web Portal, SMS
**Complexity**: High
**Monthly Value to Client**: $600 - $1,800

### What It Does
A unified household management agent for pet families with multiple animals. It consolidates all pets' records, appointments, reminders, and health timelines into a single family view — making it effortless for owners to stay on top of the needs of 2, 3, or 5+ pets simultaneously. For the clinic, it dramatically reduces front desk coordination overhead and increases multi-pet household compliance and revenue.

### Core Capabilities
- Family dashboard: all pets' upcoming appointments, due vaccines, medications in one view
- Single-message reminder that bundles all pets' outstanding needs ("Biscuit is due for Bordetella, Luna needs her annual, and Max's flea prevention is overdue")
- Consolidated appointment scheduling: book multiple pets in back-to-back slots in one interaction
- Per-pet medication reminders (daily meds, refill alerts, missed dose logging)
- New pet onboarding flow: owner adds a new pet and intake profile is generated automatically
- Annual family health report: all pets' records, vaccinations, and wellness summaries in a PDF
- Caregiver access: secondary household members can view/manage pets
- Lost pet quick-action: one button to generate a lost pet report with description and recent photo

### Data Inputs Required
- All pets' profiles and medical records from practice management system
- Household/owner account with linked pet IDs
- Medication schedules per pet
- Appointment history and upcoming bookings
- Emergency contact information per household

### Integration Points
- ezyVet / Cornerstone / Avimark — full patient family data
- GHL — household-level CRM segmentation and multi-pet messaging
- Twilio SMS — consolidated family reminder delivery
- Online booking — multi-pet appointment scheduling
- DocuSend / Lob — annual family health report mailing
- WhatsApp — preferred channel for multi-message household coordination

### Sample Prompt/Persona
> "Hi [Owner Name]! Quick family health check-in from [Clinic Name]: You have 3 pets with upcoming needs this month. Biscuit (Lab) — Rabies booster due in 12 days. Luna (Persian) — Annual wellness exam 2 weeks overdue. Max (Tabby) — Flea/tick prevention runs out this Friday. Want to tackle all three in one trip? I can find a slot that works for everyone. Reply BOOK and I'll handle it."

### Customization Variables
- `max_pets_per_household` — platform limit (usually unlimited)
- `consolidation_logic` — how to group reminders (by due date, by type, or by pet)
- `caregiver_roles` — primary owner vs. secondary household member permissions
- `lost_pet_integration` — connect to local shelter alert systems
- `annual_report_format` — PDF style and content sections
- `medication_refill_lead_days` — how early to alert before a medication runs out

### Stickiness Factor
Extremely high. Multi-pet households represent the most complex and highest-value client segment. Once a family has all pets under one management system, the switching cost is enormous. This tool is genuinely irreplaceable from the owner's perspective.

### Upsell Path
- Add pet sitting / boarding reservation integration for travel scheduling
- Upgrade to include specialist referral tracking (cardiologist, oncologist, neurologist)
- Bundle with SKILL-086 (Triage) for complete care platform
- Premium tier: dedicated pet health concierge with live vet tech messaging
# PART 3: FITNESS / GYM (091-095)

---

## SKILL-091: AI Workout Plan Generator

**Category**: Widget/Tool + Chat Agent
**Applies To**: Fitness / Gym
**Deployment Platform**: Custom Web, GHL, Mindbody, Trainerize
**Complexity**: High
**Monthly Value to Client**: $700 - $2,200

### What It Does
An intelligent fitness programming agent that builds fully individualized workout plans by synthesizing body scan data (InBody, DEXA, or self-reported metrics), stated fitness goals, experience level, available equipment, and injury history. It generates week-by-week progressive programming with exercise descriptions, sets/reps/rest protocols, and video links, delivered through a member-facing app or portal.

### Core Capabilities
- Comprehensive fitness assessment intake: goals, experience, injuries, available days/equipment
- Body scan data ingestion from InBody, Styku, DEXA, or manual entry
- Program generation: strength, hypertrophy, fat loss, athletic performance, or hybrid
- Progressive overload programming with weekly plan evolution
- Exercise library with video demonstrations and form cues
- Equipment substitution logic (no barbell → use dumbbells or bands)
- Injury modification layer: flags contraindicated exercises and offers alternatives
- Trainer review and approval gate before plan delivery (optional for premium gyms)
- Plan regeneration triggers: plateau detection, goal change, or 4-week re-assessment

### Data Inputs Required
- Member fitness profile (age, sex, height, weight, experience level, goals)
- Body scan results (or manual body composition entry)
- Available equipment list (home, full gym, or specific equipment)
- Injury and limitation flags
- Training days per week and session duration preference
- Trainer-uploaded program templates (if trainer-supervised)

### Integration Points
- Trainerize / TrueCoach / PT Distinction — plan delivery and member tracking
- InBody / Styku API — body scan data ingestion
- Mindbody — member profile and class schedule integration
- YouTube / Vimeo — exercise video library links
- GHL — member communication and re-assessment reminders
- Zapier — connects body scan device outputs to plan generation trigger

### Sample Prompt/Persona
> "Welcome to [Gym Name]'s AI training system. I'm going to build a completely custom workout plan for you — not a cookie-cutter template, but a program designed specifically for your body, your goals, and your schedule. It'll take about 5 minutes to gather the information I need. Let's start with what you're working toward: are you focused more on building muscle, losing fat, improving endurance, or something else entirely?"

### Customization Variables
- `program_length` — 4, 8, or 12-week cycles
- `available_equipment` — full gym, home (dumbbells only), bodyweight only
- `trainer_approval_gate` — on/off (direct delivery or trainer-reviewed)
- `intensity_model` — RPE-based, percentage-based, or rep-range
- `video_library_source` — YouTube, custom hosted, or exercise API
- `language` — multi-language support for diverse gym memberships

### Stickiness Factor
Very high. Members who follow structured AI-generated programs see results faster, which drives retention. The system improves over time as it accumulates member progress data. Gyms with strong programming differentiate themselves against budget competitors.

### Upsell Path
- Upgrade to 1:1 AI coach with daily check-ins and real-time plan adjustments
- Add nutrition plan pairing (SKILL-092) for comprehensive transformation program
- Premium: live trainer video review of form via app upload
- License white-label version to personal trainers as their client management system

---

## SKILL-092: AI Meal Plan & Nutrition Agent

**Category**: Chat Agent + Content Engine
**Applies To**: Fitness / Gym
**Deployment Platform**: Custom Web, GHL, WhatsApp, Trainerize
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,600

### What It Does
A conversational nutrition coaching agent that generates fully personalized weekly meal plans based on a member's fitness goals, body composition data, dietary restrictions, food preferences, and macro targets. It provides grocery lists, meal prep guides, and recipe suggestions, and adjusts the plan weekly based on progress check-ins — functioning as an always-available registered dietitian proxy for gyms that cannot afford full-time nutrition staff.

### Core Capabilities
- Goal-based caloric and macronutrient target calculation (TDEE-adjusted)
- Dietary restriction filtering: vegan, vegetarian, keto, gluten-free, halal, kosher, allergy flags
- 7-day meal plan generation with breakfast, lunch, dinner, and snacks
- Automated grocery shopping list output (organized by store section)
- Meal prep batch cooking guide for Sundays
- Recipe library with macros displayed per serving
- Weekly progress check-in: weight, energy, adherence → plan adjustment
- Restaurant and on-the-go meal guidance for travel and social situations

### Data Inputs Required
- Member fitness profile and body composition metrics
- Caloric goal and macro split preference (or auto-calculated)
- Food allergies and dietary restrictions
- Cuisine preferences and disliked foods
- Weekly shopping budget (optional)
- Current eating habits baseline (optional intake form)

### Integration Points
- Trainerize / TrueCoach — nutrition plan delivery alongside workout plan
- GHL — weekly check-in reminders and progress follow-up
- Whisk / Edamam API — recipe data and nutritional information
- WhatsApp / SMS — daily tip delivery and check-in prompts
- MyFitnessPal API — food logging sync (optional)
- Cronometer API — detailed micronutrient tracking (optional)

### Sample Prompt/Persona
> "I'm your AI nutrition coach at [Gym Name]. I'll build you a meal plan you can actually stick to — real food, realistic portions, and a grocery list you can take straight to the store. No calorie counting apps required unless you want one. Let's start: What's your main goal right now — fat loss, muscle gain, or general health? And are there any foods you absolutely can't eat or don't want to eat?"

### Customization Variables
- `caloric_method` — Mifflin-St Jeor, Harris-Benedict, or custom multiplier
- `macro_split_presets` — standard, keto, high-protein, balanced
- `meal_count` — 3 meals/day, 4 meals, 5 small meals, intermittent fasting schedule
- `recipe_complexity` — 5-ingredient simple, intermediate, chef-level
- `grocery_budget` — budget-sensitive ingredient swaps
- `check_in_frequency` — daily, 3x/week, or weekly

### Stickiness Factor
High. Nutrition plans that produce visible results within 2–4 weeks create deeply loyal members. The weekly adaptive check-in makes the system feel like a real coach relationship, reducing cancellation rates significantly.

### Upsell Path
- Upgrade to registered dietitian (RD) review and approval tier
- Add supplement recommendation engine with affiliate or in-gym retail tie-in
- Bundle with SKILL-091 (Workout Generator) for full body transformation system
- Add food photo logging: member snaps a photo → AI estimates macros automatically

---

## SKILL-093: AI Member Retention Alert Agent

**Category**: Analytics + Workflow Automation
**Applies To**: Fitness / Gym
**Deployment Platform**: GHL, Mindbody, Zapier, Twilio
**Complexity**: Medium
**Monthly Value to Client**: $600 - $1,800

### What It Does
A churn prediction and intervention agent that continuously monitors member attendance patterns, check-in frequency, and engagement signals to identify members at risk of canceling before they cancel. When a member crosses a risk threshold, the agent automatically triggers a personalized outreach sequence designed to re-engage them — a call from the front desk, a personal trainer offer, or an automated "we miss you" campaign with a tangible incentive.

### Core Capabilities
- Real-time attendance monitoring with rolling 7-day, 14-day, and 30-day views
- Churn risk scoring algorithm (0–100) updated daily per member
- Attendance drop detection: compares current frequency to personal baseline
- Segment-specific triggers: new members, post-New-Year joiners, anniversary members
- Automated outreach sequences: personalized SMS, email, or staff call task assignment
- Incentive injection: free PT session, freeze extension, or guest pass offer at threshold
- Re-engagement tracking: did the outreach work? attendance improvement scoring
- Monthly retention dashboard: churn rate, at-risk count, intervention success rate

### Data Inputs Required
- Daily check-in data from gym access system or Mindbody
- Member profile: join date, membership tier, class preferences, PT enrollment
- Historical attendance baseline per member
- Membership type and contract terms
- CRM contact data for outreach delivery

### Integration Points
- Mindbody / ABC Fitness / Club OS — check-in data source
- GHL — outreach sequence execution and task creation for staff
- Twilio SMS — automated "we miss you" message delivery
- Zapier / Make — attendance data pipeline to GHL
- Dashboard tool (Looker, Google Data Studio, or GHL) — retention reporting

### Sample Prompt/Persona
> [Staff task mode] "Retention Alert: [Member Name] hasn't checked in for 18 days — their longest gap since joining. Their personal history shows they typically visit 3x/week. Risk score: 78/100. Recommended action: Personal call from front desk today. Suggested script: 'Hey [Name], we noticed it's been a little while and wanted to check in — is everything okay? We'd love to see you back. I can set you up with a complimentary session with one of our trainers this week if you'd like.'"

### Customization Variables
- `risk_score_thresholds` — what score triggers each level of intervention
- `outreach_sequence_type` — automated message, staff call task, or both
- `incentive_type` — free PT session, guest pass, account freeze, discount
- `new_member_window` — first 60 days treated with separate (more sensitive) logic
- `blackout_members` — frozen accounts, medical leaves excluded from alerts
- `staff_assignment_rules` — which staff member handles which member segments

### Stickiness Factor
Extremely high. Retention directly impacts monthly recurring revenue. Once a gym sees even a 5% reduction in churn, the revenue impact is immediately measurable. No gym manager wants to go back to reactive churn management after seeing the data.

### Upsell Path
- Add predictive lifetime value modeling per member segment
- Upgrade to AI-powered win-back campaign for already-cancelled members
- Bundle with SKILL-094 (Challenge Manager) to drive engagement proactively
- Multi-location dashboard expansion for franchise or chain gym clients

---

## SKILL-094: AI Challenge & Competition Manager

**Category**: Workflow Automation + Content Engine
**Applies To**: Fitness / Gym
**Deployment Platform**: GHL, Custom Web, Mindbody, Trainerize
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,400

### What It Does
A complete challenge orchestration agent that creates, launches, runs, and reports on member fitness challenges — from 30-day transformation contests to step count competitions and weight loss leagues. It handles all logistics: registration, progress tracking, leaderboard updates, participant encouragement, and prize announcement — turning challenges from a labor-intensive event into a fully automated member engagement machine.

### Core Capabilities
- Challenge creation wizard: type, duration, rules, prizes, entry fee (if any)
- Member registration page generation with email/SMS confirmation
- Daily/weekly progress submission via chat, web form, or app integration
- Automated leaderboard updates with public-facing display options
- Participant motivational messages timed throughout the challenge
- Midpoint check-in and coaching tip delivery
- Drop-off detection: participants who stop submitting receive re-engagement nudges
- Final results tabulation, winner announcement, and prize coordination
- Post-challenge survey and testimonial collection

### Data Inputs Required
- Challenge type and scoring rules
- Member roster and registration data
- Progress submission format (weight, reps, check-in count, step count, etc.)
- Prize details and winner announcement preferences
- Gym branding for leaderboard and communication templates

### Integration Points
- GHL — registration, communication sequences, and results reporting
- Trainerize / Mindbody — optional progress data pull
- Custom web page — public leaderboard display
- Typeform / JotForm — progress submission forms
- Stripe — entry fee collection (if applicable)
- Social media — leaderboard sharing and challenge promotion posts

### Sample Prompt/Persona
> "The [Gym Name] 30-Day Transformation Challenge starts [Date]! You're registered and I'll be your accountability partner throughout. Every Monday, check in with your weight and progress photo — I'll update the leaderboard and send you a motivational note. Top 3 at the end win [Prize]. On Day 1, I'll send you your challenge guide and first workout. Ready to win? Reply READY to confirm."

### Customization Variables
- `challenge_types` — transformation, step count, class attendance streak, strength PR
- `scoring_logic` — absolute change, % change, or point-based
- `leaderboard_visibility` — public, members-only, or anonymous
- `message_frequency` — daily, every other day, or weekly
- `prize_structure` — single winner, top 3, or participation tier rewards
- `photo_submission` — enable/disable progress photo component

### Stickiness Factor
High. Challenges spike gym engagement and create community. Members who participate in challenges have dramatically higher retention rates. The competitive and social dynamic makes the gym sticky beyond just equipment access.

### Upsell Path
- Add branded mobile app with in-app leaderboard and challenges (premium)
- Corporate wellness challenge product: sell challenge infrastructure to employer clients
- Bundle with SKILL-093 (Retention Agent) to auto-enroll at-risk members in challenges
- Sponsorship integration: local brands sponsor challenges in exchange for gym member exposure

---

## SKILL-095: AI Body Composition Tracker & Progress Report Agent

**Category**: Analytics + Workflow Automation
**Applies To**: Fitness / Gym
**Deployment Platform**: Custom, GHL, InBody API, Trainerize
**Complexity**: High
**Monthly Value to Client**: $600 - $1,800

### What It Does
An automated body composition data management agent that ingests scan results from InBody, Styku, DEXA, or manual entry over time, stores longitudinal data per member, generates visually rich progress reports, and uses trend analysis to recommend plan adjustments. It closes the feedback loop between body scan results and training/nutrition programming, transforming expensive scan equipment from a one-time novelty into an ongoing retention and programming tool.

### Core Capabilities
- Scan result ingestion: InBody 270/570/770, Styku, DEXA, Fit3D API connections
- Longitudinal tracking: weight, fat mass, lean mass, skeletal muscle mass, visceral fat level, BMR
- Progress report PDF generation with trend charts and plain-language interpretation
- Comparison overlays: current vs. previous scan vs. goal targets
- AI-written insights: "You've gained 3.2 lbs of muscle in 8 weeks — here's what that means for your metabolism"
- Plan adjustment triggers: sends flag to trainer if scan shows fat gain or muscle loss
- Member-facing progress summary via email or app push notification
- Scan reminder and scheduling prompts at 4-week, 8-week, and 12-week intervals

### Data Inputs Required
- Body scan raw data exports (CSV or API from InBody/Styku/DEXA)
- Member profile and fitness goals
- Scan appointment dates for timeline alignment
- Training and nutrition plan data (for correlation reporting)
- Trainer or coach contact for flagging alerts

### Integration Points
- InBody API / Styku API / Fit3D — direct scan data ingestion
- Trainerize / TrueCoach — plan adjustment workflow
- GHL — member report delivery and rescan reminder sequences
- PDF generation tool (WeasyPrint, Puppeteer, or equivalent)
- Google Sheets / Airtable — raw data backup and cohort analysis
- Mindbody — scan appointment scheduling

### Sample Prompt/Persona
> [Member-facing report delivery mode] "Great news, [Member Name]! Your 8-week scan results are in. Here's the quick version: You lost 5.4 lbs of fat and gained 2.1 lbs of muscle — that's a 7.5 lb body composition swing in the right direction. Your visceral fat dropped from level 9 to level 7, which is excellent for heart health. Your trainer [Name] has already reviewed these results and updated your program. Your next scan is scheduled for [Date]. Keep going!"

### Customization Variables
- `scan_device_sources` — which devices the gym has (InBody model, Styku, etc.)
- `report_template` — simplified (for general members) or detailed (for performance clients)
- `trainer_alert_thresholds` — muscle loss or fat gain delta that triggers trainer notification
- `scan_interval_schedule` — 4-week, 6-week, 8-week, or custom
- `goal_comparison_display` — show distance from goal on every report
- `language` — multi-language report generation

### Stickiness Factor
Extremely high. Body scan data is deeply personal and longitudinal — members become invested in their data history. The equipment ROI calculation also becomes undeniable for gym owners: more scan frequency, more plan adjustments, more PT revenue.

### Upsell Path
- Add group analytics: population-level body composition insights for gym marketing
- Upgrade to quarterly business review report for gym owner (average scan metrics by segment)
- Bundle with SKILL-091 and SKILL-092 for the full transformation platform
- Corporate wellness version: provide employers with aggregate (anonymized) workforce health metrics
# PART 4: PROPERTY MANAGEMENT (096-100)

---

## SKILL-096: AI Maintenance Triage Agent

**Category**: Voice Agent + Workflow Automation
**Applies To**: Property Management
**Deployment Platform**: Vapi, GHL, Twilio, AppFolio, Buildium
**Complexity**: High
**Monthly Value to Client**: $900 - $2,800

### What It Does
A 24/7 AI maintenance intake and triage agent that accepts tenant maintenance requests via phone call, text, or online form, conducts a structured diagnostic interview to determine issue type and urgency, creates a work order in the property management system, and dispatches the appropriate vendor — all without requiring a property manager to be involved for routine issues. It drastically reduces after-hours emergencies that consume management time and ensures genuinely urgent issues (gas leaks, flooding) receive immediate human escalation.

### Core Capabilities
- Multimodal intake: Vapi voice call, SMS, web form, or tenant portal submission
- Structured diagnostic interview: issue type, location in unit, severity, duration, photos requested
- Urgency classification: Emergency (flooding/gas/no heat in winter), Urgent (HVAC/no hot water), Routine (appliance, paint), Cosmetic
- Automatic work order creation in AppFolio, Buildium, or Rent Manager
- Vendor dispatch based on issue type and property location (preferred vendor routing)
- Tenant confirmation: work order number, estimated response time, contact information
- Emergency escalation: gas/electrical/flooding → immediate property manager call/text alert
- Follow-up sequence: checks tenant satisfaction 48 hours after vendor completes work

### Data Inputs Required
- Tenant roster with unit numbers, lease terms, and contact info
- Property list with unit layouts and known system details (HVAC age, appliance brands)
- Preferred vendor directory by trade and service area
- Emergency escalation contact list (property manager, owner)
- Work order templates and priority definitions

### Integration Points
- AppFolio / Buildium / Rent Manager / Yardi — work order creation and tracking
- Vapi — after-hours voice intake
- Twilio SMS — tenant confirmation and follow-up
- GHL — internal notification and task creation for property managers
- Google Calendar — vendor appointment scheduling
- Stripe / online payment — vendor invoice processing (optional)

### Sample Prompt/Persona
> "Hi, you've reached [Property Management Company]'s 24/7 maintenance line. I can get your request submitted right now and make sure it gets to the right team. What's your name and unit number? And can you describe what's going on? I'll ask a few quick questions to make sure we send the right person."

### Customization Variables
- `urgency_matrix` — customize which issue types fall into which urgency tier
- `vendor_routing_rules` — issue type × property location → preferred vendor assignment
- `emergency_escalation_contacts` — who gets called/texted for level 5 emergencies
- `after_hours_behavior` — different script for nights/weekends vs. business hours
- `pm_system_credentials` — AppFolio, Buildium, or Rent Manager API keys
- `follow_up_timing` — hours after work order closed before satisfaction check is sent

### Stickiness Factor
Extremely high. Maintenance requests are the #1 operational pain point in property management. Any system that reliably handles after-hours triage without management involvement becomes indispensable within 30 days. The work order history also creates accountability documentation for disputes.

### Upsell Path
- Add vendor performance scoring and automated vendor review requests
- Upgrade to predictive maintenance alerts (appliance age + issue frequency → replacement recommendation)
- Bundle with SKILL-100 (Move-In/Move-Out Coordinator) for full tenant lifecycle management
- Multi-property portfolio dashboard expansion for large property managers

---

## SKILL-097: AI Tenant Screening Agent

**Category**: Workflow Automation + Chat Agent
**Applies To**: Property Management
**Deployment Platform**: GHL, Custom Web, Zapier, TransUnion SmartMove
**Complexity**: High
**Monthly Value to Client**: $700 - $2,200

### What It Does
A fully automated tenant screening workflow agent that guides rental applicants through the entire screening process — from initial application intake through background and credit check coordination, income verification, landlord reference checks, and scored decision support. It ensures consistent, legally compliant screening criteria are applied uniformly to all applicants, reducing fair housing liability while dramatically shortening the time-to-placement.

### Core Capabilities
- Customizable online application form with document upload
- Identity verification prompt (government ID upload)
- Background and credit check initiation via TransUnion SmartMove, Rentspree, or Checkr
- Income verification: pay stubs, bank statements, employer contact workflow
- Landlord reference request: automated email/call to previous landlord with structured questions
- Scoring model: income-to-rent ratio, credit score, rental history, criminal background flags
- Decision support report for property manager review
- Adverse action letter generation (legally required denial notice)
- Applicant status communication throughout process

### Data Inputs Required
- Property manager's screening criteria (minimum credit score, income multiple, background policies)
- Applicable state and local fair housing rules (to configure compliant denial criteria)
- Screening service API credentials (SmartMove, Rentspree, or Checkr)
- Application form fields required per property
- Lease-ready profile template for approved applicants

### Integration Points
- TransUnion SmartMove / Rentspree / Checkr — background and credit checks
- GHL — applicant pipeline and communication management
- DocuSign / HelloSign — applicant authorization e-signatures
- AppFolio / Buildium — approved applicant profile sync
- Twilio SMS / email — applicant status updates
- Stripe — application fee collection

### Sample Prompt/Persona
> "Thanks for your interest in [Property Address]! I'll walk you through the application process right now — it takes about 10 minutes. Once submitted, I'll keep you updated at every step. We typically have a decision within 48 hours. Ready to get started? First, I'll need your full legal name and email address to set up your applicant profile."

### Customization Variables
- `screening_criteria` — income multiple, minimum credit score, background policy
- `fair_housing_rules` — state/city-specific compliant criteria configurations
- `screening_vendor` — SmartMove, Rentspree, Checkr, or custom
- `application_fee` — amount and collection method
- `decision_workflow` — auto-decision vs. manager review required
- `adverse_action_template` — legally compliant denial letter per jurisdiction

### Stickiness Factor
High. Tenant screening is legally sensitive and process-dependent. Once a property manager runs multiple properties through a standardized AI screening workflow, the consistency and liability protection becomes a business necessity. Documentation also protects against fair housing complaints.

### Upsell Path
- Add AI-powered lease generation integrated with approved applicant profile (SKILL-098)
- Upgrade to real-time fraud detection on submitted documents (AI document authenticity check)
- Bundle with SKILL-096 (Maintenance Triage) and SKILL-100 (Move-In Coordinator) for full tenant lifecycle
- Fair housing compliance audit report add-on: quarterly review of all screening decisions for consistency

---

## SKILL-098: AI Lease Management Agent

**Category**: Workflow Automation + Operations
**Applies To**: Property Management
**Deployment Platform**: GHL, DocuSign API, AppFolio, Buildium, Zapier
**Complexity**: High
**Monthly Value to Client**: $800 - $2,500

### What It Does
A comprehensive lease lifecycle management agent that handles the full document and communication journey for residential and commercial leases — from initial lease generation using approved tenant data, through execution via e-signature, renewal negotiation, addendum management, and legal notice delivery. It ensures every lease event is tracked, noticed, and documented without manual property manager involvement for routine transactions.

### Core Capabilities
- Lease document generation from approved-applicant data and property-specific templates
- E-signature workflow with status tracking and automatic follow-up for non-signers
- Renewal tracking: flags leases 120, 90, and 60 days before expiration
- Automated renewal offer generation with new term and rent adjustment
- Tenant response handling: accept renewal, negotiate, or notice-to-vacate workflow
- Legal notice generation: 3-day pay-or-quit, 30-day notice, cure-or-quit, eviction notice
- Addendum and lease amendment creation and execution workflow
- Lease document storage and retrieval system with searchable index
- Compliance tracking: state-required addenda, habitability disclosures, rent control notices

### Data Inputs Required
- Approved tenant profile (from SKILL-097 or manual entry)
- Property-specific lease template (state-compliant base document)
- Current rent and term data
- State/local legal notice templates
- Property management system API for record sync

### Integration Points
- DocuSign / HelloSign / Adobe Sign — e-signature workflow
- AppFolio / Buildium / Rent Manager — lease record storage and sync
- GHL — renewal pipeline tracking and tenant communication sequences
- Twilio SMS / email — renewal offer and notice delivery
- Docassemble / custom template engine — document generation
- Cloud storage (Google Drive, Dropbox) — lease document archive

### Sample Prompt/Persona
> [Renewal workflow mode] "Hi [Tenant Name], your lease at [Address, Unit] expires on [Date] — about 90 days from now. We'd love to have you continue! We're offering a renewal at [New Rent]/month for a [Term] term. Here's your renewal agreement to review and sign electronically. If you have questions or want to discuss, just reply to this message. If we don't hear from you by [Decision Deadline], we'll assume you plan to vacate and will begin the turnover process."

### Customization Variables
- `lease_templates` — state-specific base document library
- `renewal_notice_timeline` — 120/90/60/30 day trigger configuration
- `rent_escalation_formula` — fixed dollar, % increase, or CPI-linked
- `legal_notice_library` — state-specific notice templates and required delivery methods
- `signature_follow_up_cadence` — days between e-sign reminders
- `storage_destination` — Google Drive, Dropbox, or PM system native storage

### Stickiness Factor
High. Lease management is a compliance-critical function. Once a property manager's lease pipeline runs through an automated system, manual tracking becomes unacceptable. Legal exposure from missed renewal deadlines or improper notice delivery reinforces dependency.

### Upsell Path
- Add rent collection and late fee automation (payments + reminders + notices as integrated system)
- Upgrade to eviction workflow agent: coordinated documentation and attorney referral
- Bundle with SKILL-097 for seamless screening-to-lease pipeline
- Multi-state expansion: build out additional state-specific legal notice libraries as paid add-ons

---

## SKILL-099: AI Vacancy Marketing Agent

**Category**: Content Engine + Workflow Automation
**Applies To**: Property Management
**Deployment Platform**: GHL, Zapier, Make, Custom
**Complexity**: Medium
**Monthly Value to Client**: $600 - $1,800

### What It Does
An automated property listing creation and multi-platform syndication agent that transforms a vacancy into a fully marketed listing across Zillow, Apartments.com, Craigslist, Facebook Marketplace, and social media — within minutes of a vacancy being created in the property management system. It writes compelling listing copy, suggests competitive pricing using rental comps, generates a landing page, and manages lead intake from all platforms into a unified inbox.

### Core Capabilities
- Vacancy intake: unit details, photos, available date, asking rent
- Rental comp analysis: pulls comparable active listings in the area to suggest competitive pricing
- AI-generated listing copy: headline, description, feature bullets, neighborhood blurbs
- Multi-platform posting: Zillow, Apartments.com, Craigslist, Facebook Marketplace, Realtor.com, Zumper
- Property-specific landing page generation with photo gallery and inquiry form
- Centralized lead inbox: all inquiries from all platforms routed to one GHL pipeline
- Automated lead follow-up: instant reply to every inquiry with showing scheduling link
- Performance tracking: listing views, inquiries, showings, and days-on-market by platform

### Data Inputs Required
- Unit details (address, unit number, beds/baths, square footage, features, appliances)
- Photos (professional or smartphone quality)
- Target rent and available date
- Pet policy, parking details, utility inclusions
- Property management system vacancy data

### Integration Points
- Zillow Rental Manager API — automated listing creation
- Apartments.com / CoStar API — listing syndication
- Facebook Graph API — Marketplace posting
- Craigslist automated posting tools — via Make/Zapier
- GHL — lead pipeline and follow-up sequences
- Google Maps / Walk Score API — neighborhood description data
- Twilio — instant lead response via SMS

### Sample Prompt/Persona
> [Internal workflow mode] "Vacancy detected at [Address], Unit [X]. Available [Date]. Generating listing package now: (1) Writing 3 headline variants and full listing description. (2) Pulling rental comps within 0.5 miles — suggesting $[Price]/mo based on market data. (3) Posting to Zillow, Apartments.com, Facebook Marketplace, and Craigslist. (4) Creating a dedicated landing page at [URL]. (5) Setting up lead capture and auto-response. Estimated time to first inquiry: 2–4 hours."

### Customization Variables
- `platform_selection` — which platforms to post on per property type
- `comp_radius_miles` — geographic range for rental comp analysis
- `listing_tone` — professional/corporate or friendly/neighborhood-focused
- `lead_response_speed` — instant auto-response vs. delayed human-review gate
- `photo_enhancement` — AI photo brightness/clarity auto-adjustment
- `fair_housing_compliance_check` — automatic scan of copy for prohibited language

### Stickiness Factor
High. Every day a unit sits vacant costs the property manager direct revenue. A system that consistently shortens vacancy periods pays for itself many times over. The multi-platform syndication and centralized lead management become the standard workflow.

### Upsell Path
- Add professional photography coordination integration (Yelp/Bark vendor dispatch)
- Upgrade to 3D virtual tour creation integration (Matterport or virtual staging AI)
- Bundle with SKILL-097 (Screening) for end-to-end vacancy-to-signed-lease pipeline
- Reporting add-on: quarterly marketing performance analysis and platform ROI

---

## SKILL-100: AI Move-In/Move-Out Coordinator

**Category**: Workflow Automation + Operations
**Applies To**: Property Management
**Deployment Platform**: GHL, Zapier, Custom Web, AppFolio
**Complexity**: High
**Monthly Value to Client**: $700 - $2,000

### What It Does
A comprehensive transition management agent that orchestrates every task involved in tenant move-ins and move-outs — from pre-move checklist generation and inspection scheduling to utility transfer coordination, key handoff logistics, security deposit accounting, and final documentation. It ensures nothing falls through the cracks during the highest-risk period of the tenant relationship while reducing the hours of administrative work associated with each turnover.

### Core Capabilities
- Move-in checklist generation (unit-specific, delivered to tenant and manager)
- Move-in inspection scheduling with property manager or third-party inspector
- Pre-move photo documentation collection (tenant uploads via mobile link)
- Welcome packet delivery: WiFi, utilities, trash schedule, HOA rules, emergency contacts
- Utility transfer notifications: coordinates with provider notification workflows
- Key/access handoff logistics: digital lockbox codes, smart lock provisioning
- Move-out notice intake and acknowledgment
- Move-out inspection scheduling and comparative condition reporting
- Security deposit accounting agent: itemizes deductions with photo evidence and delivers disposition letter within state-required timeframe

### Data Inputs Required
- Lease terms: move-in date, move-out date, deposit amount, unit address
- Unit condition standards and property-specific checklist templates
- State security deposit law parameters (return timeline, documentation requirements)
- Contractor/cleaner preferred vendor list for turnover
- Key/access management system credentials (Rently, Igloohome, etc.)

### Integration Points
- AppFolio / Buildium — lease and deposit data source
- GHL — checklist task management and communication sequences
- Twilio SMS — real-time move-in/out coordination messages
- Google Forms / JotForm — condition inspection photo upload forms
- Stripe — deposit refund or deduction collection processing
- DocuSign — move-out disposition letter e-signature
- Smart lock APIs (Rently, Igloohome) — digital key provisioning

### Sample Prompt/Persona
> "Welcome to your new home at [Address], [Unit]! I'm your move-in coordinator. I'll guide you through everything you need to do before and on [Move-In Date]. Step 1: Here's your move-in checklist — please complete the inspection walkthrough within 48 hours of getting your keys and upload photos of any pre-existing damage. This protects your security deposit. Step 2: Here are your utility setup instructions. I'll check in with you at each step. Any questions? Just text me back."

### Customization Variables
- `checklist_template` — unit-type-specific (studio vs. 3BR vs. commercial)
- `photo_documentation_requirement` — required per room or overall condition photos
- `state_deposit_rules` — jurisdiction-specific return timeline and deduction limits
- `welcome_packet_content` — property-specific rules, local info, utility contacts
- `inspection_type` — self-guided (photos) or scheduled with inspector
- `smart_lock_provider` — Rently, Igloohome, August, or manual key

### Stickiness Factor
High. Move-ins and move-outs are the most documentation-intensive and legally consequential moments in the tenant relationship. A system that creates a defensible paper trail on both ends protects the property manager legally and operationally. Once standardized, manual processes feel dangerous.

### Upsell Path
- Add contractor dispatch automation for turnover cleaning and repairs
- Upgrade to full virtual inspection service with AI damage detection on photos
- Bundle with SKILL-098 (Lease Management) and SKILL-097 (Screening) for full tenant lifecycle
- Add new tenant review solicitation campaign post-move-in (Google/Yelp reviews for PM company)
# PART 5: RECRUITMENT / STAFFING (101-104)

---

## SKILL-101: AI Phone Screening Agent

**Category**: Voice Agent
**Applies To**: Recruitment / Staffing
**Deployment Platform**: Vapi, Twilio, GHL, Bullhorn, Greenhouse
**Complexity**: High
**Monthly Value to Client**: $1,200 - $3,500

### What It Does
An AI voice agent that conducts structured first-round phone screenings with job candidates at scale — calling applicants within minutes of application submission, asking role-specific screening questions, assessing communication quality, scoring responses against defined criteria, and delivering a ranked screening report to the recruiter. It compresses the time-to-screen from days to minutes and allows recruiting teams to focus exclusively on pre-qualified candidates.

### Core Capabilities
- Outbound call initiation within minutes of application submission
- Customizable script per job role with branching question logic
- Screening dimensions: availability, salary expectations, experience depth, culture indicators, communication skills
- Real-time call transcription and AI scoring per question
- Communication quality assessment: clarity, articulation, professionalism
- Red flag detection: inconsistencies with resume, prohibited topics (if applicable)
- Candidate-facing scheduling: if candidate doesn't answer, offers self-schedule callback link
- Structured screening report delivered to ATS and recruiter inbox
- Candidate status update: automated "thanks for speaking with us" or next-steps message

### Data Inputs Required
- Job description and required qualifications per role
- Screening question script (5–10 questions, customized per role)
- Scoring rubric: what answers score high vs. low per question
- Candidate contact data from ATS
- Recruiter preferences for escalation thresholds

### Integration Points
- Vapi — AI voice call engine
- Greenhouse / Lever / Bullhorn / Workable — ATS candidate status updates
- Twilio — call routing and backup SMS scheduling
- GHL — pipeline tracking and recruiter notification
- OpenAI Whisper — call transcription
- Google Sheets / Airtable — screening score reporting

### Sample Prompt/Persona
> "Hi, this is [Alex] calling from [Company Name]'s recruiting team. Thanks so much for applying for the [Job Title] role — I'd love to ask you a few quick questions. This should take about 8 minutes. Is now a good time? Great. First: can you tell me a bit about your current role and what's prompting you to explore new opportunities?"

### Customization Variables
- `caller_name` — AI persona name and company branding
- `question_count` — 5, 7, or 10 questions depending on role complexity
- `scoring_rubric` — custom answer rating criteria per question
- `escalation_score` — minimum score to advance to human recruiter
- `callback_window` — hours to offer alternative callback if no answer
- `language` — multi-language screening for bilingual roles

### Stickiness Factor
Extremely high. Recruiting agencies and in-house teams that deploy phone screening at scale cannot go back to manual first-round calls. Time savings per hire are measured in hours. Volume capacity multiplies 5–10x without adding headcount.

### Upsell Path
- Upgrade to video screening integration (AI-analyzed video responses)
- Add skills assessment integration (Codility, HackerRank, TestGorilla) triggered post-screen
- Bundle with SKILL-102 (Resume Scoring) and SKILL-103 (Interview Scheduling) for full top-of-funnel
- White-label for staffing agencies to offer as a premium service to employer clients

---

## SKILL-102: AI Resume Screening & Scoring Agent

**Category**: Analytics + Workflow Automation
**Applies To**: Recruitment / Staffing
**Deployment Platform**: GHL, Greenhouse, Lever, Zapier, Claude
**Complexity**: Medium
**Monthly Value to Client**: $800 - $2,200

### What It Does
An intelligent resume analysis agent that reads every resume submitted for a role, extracts structured data across 20+ dimensions, scores each candidate against the specific job criteria, flags standouts and disqualifying factors, and delivers a ranked shortlist to the recruiter — transforming an inbox of 200 unreviewed applications into a prioritized pipeline in minutes.

### Core Capabilities
- Resume parsing: extracts experience, education, skills, tenure, job titles, companies, achievements
- Job-criteria matching: weighted scoring against must-have and nice-to-have requirements
- Career trajectory analysis: progression, promotions, relevant industry moves
- Tenure and stability assessment: average tenure per job, gaps, patterns
- Skills extraction and gap analysis vs. job description
- Ranked shortlist generation with individual candidate score cards
- Red flag tagging: unexplained gaps, very short tenures, credential mismatches
- Diversity sourcing notes: identifies if candidate pool needs pipeline diversification
- ATS status update: pushes score and recommendation to candidate record

### Data Inputs Required
- Job description with explicit must-have and nice-to-have criteria
- Scoring weight matrix per criterion (experience depth, skills match, education, etc.)
- Resume files (PDF/Word) or ATS candidate records
- Ideal candidate profile (optional benchmark persona)
- ATS API credentials for status updates

### Integration Points
- Greenhouse / Lever / Workday / Bullhorn — resume import and status updates
- OpenAI GPT-4o — resume reading and scoring engine
- GHL — recruiter notification and shortlist delivery
- Google Drive / Dropbox — resume file storage
- Zapier — trigger on new ATS application submission
- Google Sheets / Airtable — candidate score database and shortlist view

### Sample Prompt/Persona
> [Internal agent mode] "New application batch received for [Job Title]. Analyzing 47 resumes now. Scoring against 6 criteria: [Years of experience in X], [Required certifications], [Industry background], [Technical skills], [Tenure stability], [Leadership indicators]. Shortlist generated: 8 candidates score 80+ (Advance), 12 score 60–79 (Review), 27 score below 60 (Archive). Sending shortlist to [Recruiter Name] now."

### Customization Variables
- `scoring_dimensions` — customizable per role type and industry
- `must_have_filters` — hard disqualifiers (e.g., no required certification → automatic archive)
- `weight_matrix` — how much each criterion contributes to total score
- `shortlist_size` — top N candidates to present, or score threshold cutoff
- `bias_mitigation_mode` — redact names, ages, graduation years before scoring
- `output_format` — email summary, Google Sheet, or ATS push

### Stickiness Factor
High. Any hiring team that processes more than 20 applications per role immediately sees the time savings. The consistency of scoring also reduces internal disagreements about candidate quality and creates audit-friendly documentation.

### Upsell Path
- Add AI job description optimizer (rewrites JD to attract better candidates)
- Upgrade to market salary benchmarking integration (levels.fyi, Glassdoor, LinkedIn Salary)
- Bundle with SKILL-101 (Phone Screening) for seamless resume-to-screen pipeline
- Quarterly hiring analytics report: source quality, score distribution, hire outcomes by channel

---

## SKILL-103: AI Interview Scheduling Coordinator

**Category**: Workflow Automation
**Applies To**: Recruitment / Staffing
**Deployment Platform**: GHL, Calendly, Google Calendar, Greenhouse, Zapier
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,500

### What It Does
An automated multi-party scheduling agent that eliminates the back-and-forth of coordinating interviews across candidates, recruiters, hiring managers, and panel interviewers. It reads calendar availability across all parties, proposes times that work for everyone, sends invites, manages confirmations, handles rescheduling requests, and delivers structured interview prep materials to each participant — compressing what typically takes 2–4 days of email chains into a 5-minute automated workflow.

### Core Capabilities
- Multi-party calendar reading across hiring team and candidate
- Conflict detection and optimal slot identification
- Automated calendar invite generation with video conference links (Zoom, Teams, Google Meet)
- Candidate-facing scheduling link with available slots pre-filtered to hiring team availability
- Interview panel coordination: assigns interviewers to topics/competency areas
- Confirmation and reminder sequence for all participants
- Rescheduling handler: candidate or interviewer requests change → system finds next available slot
- Pre-interview prep delivery: candidate briefing, interview format, interviewer bios
- Post-interview feedback request automation

### Data Inputs Required
- Hiring manager and panel interviewer calendars (Google Calendar or Outlook API access)
- Candidate contact information and preferred scheduling channel
- Interview format specifications (duration, format, interviewer assignments)
- Video conferencing platform credentials
- Recruiter scheduling preferences and business hours

### Integration Points
- Google Calendar / Microsoft Outlook — calendar read/write
- Calendly / Cronofy / Cal.com — scheduling interface
- Zoom / Microsoft Teams / Google Meet — video link generation
- Greenhouse / Lever / Workable — scheduling status sync
- GHL — candidate communication and pipeline stage update
- Twilio SMS / email — reminders and confirmations

### Sample Prompt/Persona
> "Great news, [Candidate Name]! [Company Name] would like to move forward with a [Interview Round] interview for the [Role] position. Here's a scheduling link with times available for you and the interview team: [link]. Interviews are [X] minutes via [Video Platform]. Once you book, I'll send you a confirmation, the interview agenda, and your interviewer's background so you can prepare. Any questions? Reply here."

### Customization Variables
- `interview_stages` — phone screen, technical, hiring manager, panel, final
- `buffer_time` — minutes between back-to-back interviews
- `scheduling_deadline` — how many business days candidate has to schedule
- `reminder_cadence` — 48hr, 24hr, and 1hr reminders
- `prep_material_library` — role-specific content to send to candidates
- `rescheduling_limit` — max number of rescheduling requests allowed

### Stickiness Factor
High. Interview scheduling is universally acknowledged as one of the most tedious parts of recruiting. Any team that automates it never returns to manual coordination. ATS integration creates a permanent data record of scheduling efficiency metrics.

### Upsell Path
- Add post-interview debrief facilitation: structured feedback form sent to each interviewer automatically
- Upgrade to candidate experience survey with NPS tracking
- Bundle with SKILL-101 and SKILL-102 for complete intake-to-interview pipeline
- Enterprise version: multi-timezone, multi-office scheduling for global hiring teams

---

## SKILL-104: AI Candidate Re-Engagement Agent

**Category**: Chat Agent + Workflow Automation
**Applies To**: Recruitment / Staffing
**Deployment Platform**: GHL, Bullhorn, Twilio, Klaviyo
**Complexity**: Medium
**Monthly Value to Client**: $600 - $1,800

### What It Does
A data-driven candidate database reactivation agent that identifies dormant candidates in the ATS, segments them by skills profile and current market conditions, and delivers highly personalized outreach sequences designed to re-engage passive talent. For staffing agencies, this turns a stale candidate database into a continuously refreshed pipeline that reduces reliance on expensive job board sourcing for every new role.

### Core Capabilities
- ATS database analysis: segments candidates by last contact date, skills, location, and previous role interest
- Market condition matching: surfaces candidates whose skills align with current open roles
- Personalized outreach generation: references specific previous conversations, role history, time elapsed
- Multi-channel sequence: email day 1 → SMS day 4 → voice drop day 8 → connection request LinkedIn day 12
- Availability check-in: "Are you currently open to opportunities?" with one-click response options
- Updated profile capture: new skills, certifications, location changes, salary expectations
- Re-qualified candidate routing: interested candidates automatically move to active pipeline
- Database health reporting: response rates by segment, re-qualification rates, source of new placements

### Data Inputs Required
- ATS candidate database export or API access (Bullhorn, Greenhouse, Workable)
- Candidate skills taxonomy and role history
- Current open job requisitions for matching
- Last contact dates and previous placement history
- Recruiter messaging guidelines and tone standards

### Integration Points
- Bullhorn / Greenhouse / JobAdder — candidate data source and status updates
- GHL — outreach sequence execution and response tracking
- Twilio SMS — text-based re-engagement
- Klaviyo / Mailchimp — email sequence delivery
- LinkedIn Sales Navigator API — connection request and InMail (optional)
- Loom / VideoAsk — personalized video outreach option for premium touchpoints

### Sample Prompt/Persona
> "Hi [Candidate Name], this is [Agency Name] — we worked together on finding you a [Previous Role Type] role back in [Year]. A lot has changed in the market since then, and there are some exciting [Industry] opportunities I've been matching against your background. Are you open to a quick conversation? No pressure — just want to see if the timing is right. Reply YES and I'll send over a few options, or STOP if you'd prefer we pause outreach."

### Customization Variables
- `dormancy_threshold_days` — how many days of no contact before a candidate enters re-engagement
- `segmentation_logic` — by skills, industry, location, or previous role level
- `sequence_length` — number of touchpoints and channel mix
- `opt-out_handling` — immediate suppression on STOP/Unsubscribe
- `personalization_depth` — deep (references specific prior conversations) vs. light (general check-in)
- `open_role_match_threshold` — minimum match % before including specific job mention

### Stickiness Factor
High. Staffing agencies and internal recruiting teams with large ATS databases immediately see the value of activating dormant talent. Every placement made from a re-engaged candidate is essentially free sourcing — no job board spend required.

### Upsell Path
- Add AI-powered job matching engine: automatically alerts re-engaged candidates when matching roles open
- Upgrade to talent community management: ongoing newsletter and content drip for warm passive candidates
- Bundle with SKILL-101 and SKILL-102 for end-to-end candidate acquisition pipeline
- Analytics add-on: placement ROI attribution by sourcing channel (new vs. re-engaged candidates)
# PART 6: CONSTRUCTION (105-108)

---

## SKILL-105: AI Bid/Estimate Generator

**Category**: Workflow Automation + Analytics
**Applies To**: Construction
**Deployment Platform**: Custom Web, GHL, Procore, BuilderTREND, Zapier
**Complexity**: High
**Monthly Value to Client**: $1,200 - $4,000

### What It Does
An AI-powered preliminary cost estimation agent that analyzes project specifications, scope descriptions, and uploaded blueprints to generate structured preliminary cost estimates across labor, materials, equipment, and overhead categories. It dramatically compresses estimating time from days to hours for preliminary bids, allows contractors to respond to more opportunities, and provides a consistent estimating baseline that reduces bid risk and improves margin accuracy.

### Core Capabilities
- Scope description intake: free text, structured form, or document/blueprint upload
- Blueprint analysis via AI vision: extracts square footage, room counts, structural elements, finishes
- Cost database integration: RSMeans, local material pricing, or custom cost library
- Trade-by-trade estimate generation: demo, framing, MEP, finishes, sitework, etc.
- Labor hour calculation using productivity factors by trade and region
- Contingency and overhead/profit markup application
- Proposal document generation: formatted estimate with line items and totals
- Revision workflow: change scope inputs → regenerate estimate in minutes
- Bid history database: stores all estimates for win/loss analysis and cost calibration

### Data Inputs Required
- Project scope description or uploaded specs/blueprints
- Geographic location (for regional labor and material cost factors)
- Project type (residential, commercial, industrial, renovation, new construction)
- Contractor's custom cost library (labor rates, preferred material prices, overhead %s)
- Bid history data for calibration (optional but improves accuracy over time)

### Integration Points
- Procore / BuilderTREND / CoConstruct — project creation and estimate storage
- OpenAI GPT-4o Vision — blueprint and document analysis
- RSMeans / Gordian — cost data API
- GHL — bid tracking pipeline and client proposal delivery
- DocuSign — proposal e-signature and acceptance tracking
- QuickBooks / Sage — approved bid → job cost setup

### Sample Prompt/Persona
> [Internal estimating mode] "New bid request received from [Client Name]: [Project Description]. Analyzing uploaded blueprint — extracting 2,400 SF single-family renovation. Scope includes: kitchen remodel, master bath addition, deck replacement. Running estimate against RSMeans 2025 data for [Region]. Preliminary estimate range: $187,000 – $214,000. Generating line-item proposal document. Flagging high-uncertainty items for estimator review before submission."

### Customization Variables
- `cost_database` — RSMeans, custom, or hybrid
- `markup_structure` — overhead %, profit %, contingency % per project type
- `estimate_precision_level` — rough order of magnitude, preliminary, or detailed
- `trade_categories` — include/exclude specific CSI divisions based on contractor scope
- `blueprint_analysis_mode` — AI vision vs. manual dimension input
- `proposal_template` — branded document format with contractor logo and terms

### Stickiness Factor
High. Estimating is the lifeblood of a construction business. Any tool that meaningfully improves speed or accuracy while maintaining margin protection becomes embedded in the business workflow. Historical bid data builds a calibration advantage that grows over time.

### Upsell Path
- Upgrade to subcontractor bid solicitation automation (sends RFQs to trade subs automatically)
- Add material takeoff generation: detailed material list from blueprints for purchasing
- Bundle with SKILL-106 (Daily Log Reporter) and SKILL-108 (Change Order Manager) for full project lifecycle
- Integration with Procore Budget module for bid-to-actual cost tracking

---

## SKILL-106: AI Daily Log & Progress Reporter

**Category**: Workflow Automation + Operations
**Applies To**: Construction
**Deployment Platform**: GHL, Procore, Zapier, SMS/WhatsApp, BuilderTREND
**Complexity**: Medium
**Monthly Value to Client**: $600 - $2,000

### What It Does
A field-to-office reporting automation agent that allows field crews to submit daily job site updates via SMS, WhatsApp, or voice message in plain language, then automatically transforms those raw submissions into structured, professionally formatted daily log reports that are stored in the project management system and distributed to stakeholders. It eliminates the most-hated administrative task in construction while creating a complete, legally defensible project record.

### Core Capabilities
- Multi-channel field submission: SMS, WhatsApp, voice memo, or mobile web form
- Voice memo transcription using Whisper AI
- Structured extraction: date, weather, crew count, hours worked, work performed, materials used, equipment on site, visitors, issues/delays
- Progress photo intake and labeling with location/date stamps
- Formatted daily log document generation (PDF or digital report)
- Distribution automation: sends report to GC, owner, PM, and subcontractor records
- Delay documentation: flags weather delays, material delays, inspection delays with contract notice implications
- Cumulative progress summary: week-over-week narrative generated automatically
- Safety incident log: if incident is mentioned, triggers separate incident report workflow

### Data Inputs Required
- Field crew contact list with assigned project codes
- Project details: name, address, contract number, scope phases
- Stakeholder distribution list per project
- Daily log template format (client-specific or standard AIA format)
- Weather API for automatic weather data injection

### Integration Points
- Twilio SMS / WhatsApp Business — field submission channel
- OpenAI Whisper — voice memo transcription
- Procore / BuilderTREND / Fieldwire — daily log storage
- Weather API (OpenWeatherMap) — auto-populated weather conditions
- GHL — project communication and stakeholder notification
- Google Drive / Dropbox — photo and log document storage
- PDF generator — formatted daily log document output

### Sample Prompt/Persona
> [Field crew SMS submission mode] "Text DAILY [Job Code] to submit your daily log. Example: DAILY 24-005 — 6 crew. Framing 2nd floor east wing complete. Rough electrical started. 3 skids of lumber delivered. Photo attached. No delays. Daily log will be generated and sent to the project file within 5 minutes of your submission."

### Customization Variables
- `submission_channels` — SMS, WhatsApp, voice, form (enable/disable per project)
- `report_template` — standard, AIA format, or client-specific custom template
- `distribution_list` — configurable per project (GC, owner, architect, PM)
- `photo_requirements` — mandatory, optional, or location-tagged required
- `delay_trigger_keywords` — list of words that activate the delay documentation workflow
- `weekly_summary_day` — which day generates the weekly cumulative summary

### Stickiness Factor
Extremely high. Daily logs that are consistently completed are a legal and contractual necessity. Any system that makes field crews actually submit logs reliably becomes irreplaceable. The historical data also becomes critical documentation during disputes or change order negotiations.

### Upsell Path
- Add AI-powered schedule delay analysis: correlates daily logs to master schedule, identifies slippage early
- Upgrade to owner-facing project portal with live progress updates and photo feed
- Bundle with SKILL-107 (Safety Tracker) and SKILL-108 (Change Order Manager) for full field ops platform
- Subcontractor compliance reporting: aggregate all sub daily logs into GC master daily report

---

## SKILL-107: AI Safety Compliance Tracker

**Category**: Operations + Workflow Automation
**Applies To**: Construction
**Deployment Platform**: GHL, Procore, Custom Web, Zapier
**Complexity**: High
**Monthly Value to Client**: $900 - $2,800

### What It Does
A proactive jobsite safety management agent that monitors OSHA compliance requirements, tracks daily toolbox talks and safety inspections, manages PPE documentation and certification records, processes incident reports, and generates the documentation required for OSHA audits and EMR (Experience Modification Rate) management. It shifts safety from reactive paperwork to a proactive compliance system.

### Core Capabilities
- Daily pre-task safety checklist delivery to field supervisors via SMS/app
- Toolbox talk library with 52+ weekly topics and documentation workflow
- PPE compliance check-in: crew confirms PPE worn via daily submission
- Worker certification and training record management: OSHA 10/30, fall protection, forklift, etc.
- Incident reporting workflow: first report of injury, near-miss, property damage
- OSHA 300/300A log maintenance and annual posting reminder
- Site-specific safety plan document library and distribution
- Subcontractor safety compliance tracking and certificate of insurance monitoring
- Safety inspection scheduler with checklist and photo documentation

### Data Inputs Required
- Worker roster with certification records and expiration dates
- Project list with site addresses and phase information
- OSHA regulation requirements applicable to project types (residential vs. commercial)
- Incident report templates
- Subcontractor contact and certificate of insurance data

### Integration Points
- Procore / Fieldwire / Procore Safety module — safety record storage
- GHL — worker communication and certification expiration alerts
- Twilio SMS — daily safety check-in prompts
- Google Forms / Typeform — inspection and incident report intake
- DocuSign — signed safety plan acknowledgments
- OSHA iReport integration — optional direct regulatory filing

### Sample Prompt/Persona
> "Good morning, [Supervisor Name]! Pre-task safety check for [Project Name] — [Date]. Today's focus: fall protection (working above 6 feet on east wing framing). Please confirm before starting work: (1) All workers wearing hard hat, safety glasses, and high-vis vest? (2) All workers within 6 feet of edge are tied off? (3) Scaffolding inspected and tagged this morning? Reply 1-2-3 with YES/NO/NA for each. Stay safe today."

### Customization Variables
- `check_in_frequency` — daily, per-shift, or task-triggered
- `toolbox_talk_schedule` — weekly auto-rotation or manual selection
- `certification_alert_lead_days` — how many days before expiration to alert
- `incident_escalation_contacts` — who receives immediate notification of incidents
- `osha_jurisdiction` — federal or state-plan state configurations
- `subcontractor_tracking` — on/off for each project based on risk profile

### Stickiness Factor
Very high. Safety documentation is both a legal requirement and a direct financial driver (EMR affects insurance premiums). Contractors who see their EMR improve due to better documentation and incident reduction attribute it to the system and become advocates.

### Upsell Path
- Add workers' compensation claim coordination workflow
- Upgrade to AI-powered jobsite photo safety audit: upload site photos → AI flags hazards
- Bundle with SKILL-106 (Daily Log) for integrated field documentation system
- Insurance broker partnership: offer safety platform as part of bundled construction insurance program

---

## SKILL-108: AI Change Order Manager

**Category**: Workflow Automation + Operations
**Applies To**: Construction
**Deployment Platform**: GHL, Procore, DocuSign, BuilderTREND, Zapier
**Complexity**: High
**Monthly Value to Client**: $1,000 - $3,200

### What It Does
A change order lifecycle management agent that captures scope change requests from the field or owner, evaluates cost and schedule impact using the project's established cost database, generates formatted change order documents for owner approval, tracks the approval status, and updates the project budget and schedule accordingly. It eliminates the most common source of construction contractor profit erosion — undocumented or delayed change order processing.

### Core Capabilities
- Change request intake: field submission, owner email, or RFI conversion
- Cost impact calculation: labor hours × rate + material quantity × unit price + equipment + markup
- Schedule impact assessment: adds days to milestone based on scope change type
- Change order document generation: numbered, formatted, with description, cost breakdown, and schedule impact
- Owner approval workflow: digital submission with e-signature and deadline tracking
- Verbal change order risk alerts: flags work proceeding before written approval
- Change order log maintenance: all COs, status, amounts, approval dates, integrated budget impact
- Back-charge and credit CO handling
- Dispute documentation: creates contemporaneous record if owner disputes a CO

### Data Inputs Required
- Original contract sum and schedule
- Project cost database (labor rates, material unit prices, equipment rates)
- CO numbering convention and document template
- Owner contact for approval routing
- Project management system credentials (Procore, BuilderTREND)

### Integration Points
- Procore / BuilderTREND / CoConstruct — CO log and budget update
- DocuSign / HelloSign — owner approval e-signature
- GHL — CO status tracking and escalation
- QuickBooks / Sage — approved CO → updated contract value in accounting
- Email / Twilio — CO submission and approval notifications
- PDF generator — formatted CO document output

### Sample Prompt/Persona
> [Change request submitted by field supervisor] "CO Request logged: [Project Name]. Scope change: Owner requested kitchen island relocation — 8-foot shift requiring additional plumbing rough-in. Calculating impact: Labor — 16 additional hours at $[rate]. Materials — [list]. Total estimated cost: $[amount]. Schedule impact: +2 days on plumbing milestone. Generating Change Order #[CO-007] for owner review. Draft attached. Sending to [Owner Name] for approval with 5-day response deadline. If no response by [Date], I'll send a reminder."

### Customization Variables
- `markup_structure` — overhead %, profit % per change type
- `approval_deadline_days` — how long owner has to respond before escalation
- `co_numbering_format` — sequential, project-coded, or custom
- `verbal_co_alert_threshold` — flags when work value exceeds limit without written approval
- `schedule_impact_calculator` — linear or critical path analysis
- `dispute_documentation_trigger` — keywords or conditions that activate dispute log

### Stickiness Factor
Very high. Change orders are where contractors make or lose margin on every project. A contractor who recovers even one previously-overlooked change order per project per month sees immediate ROI. The protection from verbal change order disputes is legally and financially irreplaceable.

### Upsell Path
- Add lien waiver management integration (conditional/unconditional waivers tied to CO payment)
- Upgrade to contract compliance monitoring: flags COs that might trigger GMP or allowance thresholds
- Bundle with SKILL-105 (Bid Generator) and SKILL-106 (Daily Log) for full project ops platform
- Monthly financial dashboard: budget vs. actual with CO impact analysis for owner reporting
# PART 7: E-COMMERCE (109-112)

---

## SKILL-109: AI Abandoned Cart Recovery Agent

**Category**: Workflow Automation + Voice Agent
**Applies To**: E-Commerce
**Deployment Platform**: Klaviyo, GHL, Twilio, Vapi, Shopify, WooCommerce
**Complexity**: High
**Monthly Value to Client**: $800 - $3,500

### What It Does
A multi-channel abandoned cart recovery system that executes a coordinated, personalized outreach sequence across email, SMS, and AI voice call to recover shoppers who added items to their cart but didn't complete purchase. Unlike basic Klaviyo email flows, this agent introduces real-time dynamic incentive logic (escalating discounts only when necessary) and a live AI voice call option for high-value carts — recovering revenue that standard automation consistently leaves on the table.

### Core Capabilities
- Cart abandonment detection: triggers within 30–60 minutes of cart abandonment
- Personalized product reminder: shows exact abandoned items with photos and prices
- Multi-channel sequence: email (30 min) → SMS (2 hours) → voice call (24 hours for carts over threshold)
- Dynamic incentive logic: applies discount only if user hasn't responded after first two touches
- Urgency injection: low stock alerts, price change warnings based on live inventory
- Objection handling: identifies exit intent survey data (if captured) and tailors messaging
- Win-back attribution tracking: which channel and which message recovered the sale
- Opt-out handling: suppresses channel based on user unsubscribe signals

### Data Inputs Required
- E-commerce platform cart and customer data (Shopify, WooCommerce, BigCommerce)
- Product catalog with inventory levels and pricing
- Customer profile: purchase history, email/SMS opt-in status, LTV
- Discount margin rules (max discount % per product category)
- Voice call threshold (minimum cart value to trigger AI call)

### Integration Points
- Shopify / WooCommerce / BigCommerce — cart and customer data
- Klaviyo — email sequence execution
- Twilio SMS — text recovery messages
- Vapi — AI voice call engine for high-value cart recovery
- GHL — pipeline tracking and attribution reporting
- Google Analytics / Triple Whale — revenue attribution

### Sample Prompt/Persona
> [Voice call mode — high-value cart] "Hi, is this [Customer Name]? This is [AI Name] from [Brand]. I noticed you were looking at the [Product Name] earlier and wanted to reach out personally. A lot of customers have questions before they complete an order — is there anything I can help clarify? I also wanted to let you know we only have [X] units left in [Size/Color]. Would you like me to help you complete your order now? I can also apply a 10% discount for you today."

### Customization Variables
- `abandonment_trigger_minutes` — delay before first touch
- `voice_call_cart_threshold` — minimum $ value to trigger voice call
- `discount_escalation_logic` — when and how much to offer (e.g., touch 2 = 5%, touch 3 = 10%)
- `sequence_channel_mix` — email only, email + SMS, or full email + SMS + voice
- `urgency_type` — inventory scarcity vs. time-limited offer vs. price increase
- `suppression_rules` — exclude recent purchasers, VIP members, or opted-out contacts

### Stickiness Factor
High. Abandoned cart recovery has directly measurable revenue attribution. E-commerce operators who see a 15–25% cart recovery rate immediately understand the compounding value. Multi-channel + voice differentiation dramatically outperforms standard email flows alone.

### Upsell Path
- Upgrade to browse abandonment recovery (for visitors who viewed but never added to cart)
- Add post-purchase upsell flow: immediately after purchase, offer a one-click add-on
- Bundle with SKILL-112 (Win-Back Campaign) for full customer lifecycle recovery
- A/B testing framework add-on: continuous optimization of messages, timing, and incentives

---

## SKILL-110: AI Product Recommendation Engine

**Category**: Widget/Tool + Analytics
**Applies To**: E-Commerce
**Deployment Platform**: Shopify, WooCommerce, Custom, Klaviyo
**Complexity**: High
**Monthly Value to Client**: $1,000 - $4,000

### What It Does
A personalization engine that analyzes each shopper's browsing history, purchase history, cart contents, demographic signals, and real-time session behavior to serve dynamically personalized product recommendations across the website, email, and post-purchase flows. It replaces generic "customers also bought" widgets with genuinely intelligent recommendations that increase average order value and session engagement.

### Core Capabilities
- Real-time behavioral tracking: pages viewed, time on page, scroll depth, clicks
- Collaborative filtering: "customers like you also bought" modeling
- Content-based filtering: product attribute similarity matching
- Cart-aware recommendations: complements current cart contents
- Post-purchase cross-sell: email recommendations based on what was just purchased
- Homepage personalization: returning visitor sees a personalized product carousel
- Category affinity scoring: ranks categories by individual shopper interest
- New visitor cold-start logic: trending products + session behavior for first-time visitors
- A/B testing framework for recommendation placement and style

### Data Inputs Required
- Product catalog with attributes (category, price, material, style, brand)
- Shopper event data (page views, add-to-cart, purchases) from tracking pixel
- Customer profile data (purchase history, email engagement)
- Inventory levels (suppress out-of-stock from recommendations)
- Business rules (promote high-margin products, clear overstock)

### Integration Points
- Shopify / WooCommerce / Magento — product catalog and order data
- Custom tracking pixel or GA4 — behavioral event stream
- Klaviyo / Omnisend — email personalization integration
- Algolia / Elasticsearch — product search integration
- Custom or Vue.js front-end widget — recommendation display component
- Triple Whale / Northbeam — revenue attribution

### Sample Prompt/Persona
> [Website widget display logic] "Customer profile identified: [Customer] — has purchased women's athletic wear 3x. Currently viewing: Running Leggings (Black, Size M). Recommendations generated: (1) Matching sports bra in same collection, (2) Running shoes she viewed last session but didn't purchase, (3) Water bottle purchased by 68% of customers who bought this legging, (4) New arrivals in her preferred color palette. Displaying in 'Complete the Look' widget below product description."

### Customization Variables
- `recommendation_algorithm` — collaborative filtering, content-based, or hybrid
- `widget_placements` — PDP, cart page, homepage, email, post-purchase
- `business_rule_overrides` — promote clearance, featured, or high-margin items
- `cold_start_strategy` — trending products vs. category bestsellers for new visitors
- `inventory_filter` — suppress items below [X] units in stock
- `visual_style` — carousel, grid, or list — matches store theme

### Stickiness Factor
Very high. Recommendation engines improve as they collect more behavioral data, creating a compounding flywheel. Revenue attribution through A/B testing makes the contribution visible. Any store that has been running personalized recommendations for 6+ months would lose significant revenue by removing the system.

### Upsell Path
- Add AI-powered search personalization: search results ranked by individual affinity
- Upgrade to email personalization at send time: recommendations generated at moment of open, not send
- Bundle with SKILL-109 (Abandoned Cart) and SKILL-111 (Size/Fit) for full conversion optimization suite
- Analytics add-on: recommendation attribution dashboard with LTV impact modeling

---

## SKILL-111: AI Size/Fit Recommendation Tool

**Category**: Widget/Tool + Diagnostic
**Applies To**: E-Commerce (Fashion/Apparel)
**Deployment Platform**: Shopify, Custom Web, WooCommerce
**Complexity**: High
**Monthly Value to Client**: $700 - $2,500

### What It Does
An intelligent fit advisor widget embedded on product pages that collects a shopper's body measurements, fit preferences, and body type information, then cross-references that data against each product's specific size specifications to predict the most accurate size recommendation — dramatically reducing apparel return rates while increasing purchase confidence.

### Core Capabilities
- Conversational or form-based measurement intake (height, weight, chest, waist, hips, inseam)
- Fit preference capture: do you prefer fitted, regular, or relaxed fit?
- Body type identification (optional): apple, pear, hourglass, rectangle, athletic
- Product-specific size chart data integration
- Fit prediction with confidence score: "We recommend Size M — High Confidence (based on 847 similar shoppers)"
- Brand-to-brand size conversion: "You wear a 6 in Zara — that's typically a Size 4 here"
- Past purchase learning: uses previous order and return data to refine recommendations
- Return rate attribution: tracks if recommended size results in lower returns over time

### Data Inputs Required
- Product size charts (per product or per brand/category)
- Measurement units and size labeling system (US, EU, UK, numeric)
- Return reason data (if available — size-related returns for model calibration)
- Brand size variation data (brand-specific fit tendencies)
- Customer measurement profiles (stored for repeat use)

### Integration Points
- Shopify / WooCommerce — product data and order history
- Custom JavaScript widget — embedded on product detail pages
- Returns management platform (Loop, ReturnLogic) — return reason data feed
- Customer account system — stored measurement profile
- Email / GHL — fit confirmation follow-up and return reduction tracking
- AI model — size prediction engine (custom or via third-party API like True Fit, Fit Finder)

### Sample Prompt/Persona
> "Not sure what size to order? I'll figure it out for you in 60 seconds. What's your height and weight? And for this particular style — do you prefer it to fit snug, true to size, or with a bit of room? Got it. Based on your measurements and the cut of this [Product Name], I recommend Size [M]. Most shoppers with your measurements love this fit. 94% of people I recommended Size M to kept their order. Ready to add to cart?"

### Customization Variables
- `measurement_fields` — which measurements to collect per product category (tops vs. bottoms vs. dresses)
- `fit_preference_options` — fitted/regular/relaxed or numeric preference scale
- `confidence_display` — show/hide confidence percentage
- `brand_size_conversion_table` — custom mapping for brand-to-brand size translation
- `widget_trigger` — appears automatically on PDP or only when customer clicks "Find My Size"
- `data_persistence` — save measurements to customer account for future visits

### Stickiness Factor
High. Return rates for apparel are typically 30–50% for online-only brands. A measurable reduction in size-related returns (usually the largest return category) creates direct cost savings that make the ROI undeniable. The measurement profile feature creates a personalization data asset.

### Upsell Path
- Upgrade to photo-based fit estimation: customer uploads photo → AI estimates body measurements
- Add sustainability messaging: highlight the environmental impact of returns reduction
- Bundle with SKILL-110 (Recommendation Engine) for complete conversion optimization
- Virtual dressing room integration: pair size recommendation with virtual try-on visualization

---

## SKILL-112: AI Customer Win-Back Campaign Agent

**Category**: Workflow Automation + Chat Agent
**Applies To**: E-Commerce
**Deployment Platform**: Klaviyo, GHL, Twilio, Vapi, Shopify
**Complexity**: Medium
**Monthly Value to Client**: $700 - $2,200

### What It Does
An automated customer reactivation agent that identifies lapsed buyers based on purchase recency and frequency patterns, segments them by lifetime value and lapse reason, and executes personalized multi-channel re-engagement sequences designed to bring them back to purchase. It systematically recovers revenue from a merchant's most valuable existing asset — their past customer database — without requiring ongoing ad spend.

### Core Capabilities
- Lapsed customer segmentation: 90-day, 180-day, 12-month lapsed tiers
- LTV-based prioritization: high-LTV lapsed customers receive premium touchpoints
- Lapse reason inference: analyzes last purchase category, discount usage, support history
- Personalized outreach: references last purchase, suggests new arrivals in same category
- Multi-channel sequence: email → SMS → AI voice (for VIP segment)
- "Why did you leave?" micro-survey injection mid-sequence
- Dynamic offer calibration: VIPs get larger win-back discount than low-LTV customers
- Re-purchase attribution tracking: win-back rate by segment and channel
- Database hygiene: flags permanently churned (invalid emails, multiple STOP responses)

### Data Inputs Required
- Full customer purchase history from Shopify/WooCommerce (dates, products, amounts)
- Customer segmentation: LTV calculation, purchase frequency baseline
- Email/SMS opt-in status
- Support/return ticket history (to avoid re-engaging customers with unresolved issues)
- Win-back offer budget (maximum discount per LTV tier)

### Integration Points
- Shopify / WooCommerce — customer and order data
- Klaviyo / Omnisend — email win-back sequence execution
- Twilio SMS — text-based re-engagement
- Vapi — AI voice call for VIP segment
- GHL — campaign tracking and ROI reporting
- Triple Whale / Northbeam — win-back revenue attribution

### Sample Prompt/Persona
> "Hey [Customer Name], we miss you! It's been a while since you grabbed your last [Product Category] from us, and a lot has changed. We've just launched [New Collection/Feature] — including some pieces that match exactly what you loved about [Previous Purchase]. As a thank-you for being a past customer, here's 15% off your next order: [CODE]. This offer expires in 72 hours. We'd love to see you back."

### Customization Variables
- `lapse_definition_days` — threshold for 90/180/365 day tier segmentation
- `ltv_tier_thresholds` — dollar amounts that define low/mid/high LTV segments
- `offer_by_segment` — discount % or type per LTV tier
- `sequence_depth` — 2, 3, or 5-touchpoint sequences with channel mix
- `survey_placement` — after touch 1, touch 2, or only for non-responders
- `permanent_churn_criteria` — conditions that move a contact to suppression list

### Stickiness Factor
High. Re-engaging past customers costs 5–7x less than acquiring new ones. Merchants who run win-back campaigns consistently see 10–20% reactivation rates among 90-day lapsed customers. The program essentially prints revenue from an existing asset.

### Upsell Path
- Bundle with SKILL-109 (Abandoned Cart) and SKILL-110 (Recommendation Engine) for full retention stack
- Add predictive churn scoring: identify customers likely to lapse before they actually do
- Upgrade to loyalty program integration: win-back offer delivered as loyalty points instead of discount
- Cross-brand win-back if client operates multiple Shopify stores
# PART 8: COACHING / CONSULTING (113-116)

---

## SKILL-113: AI Content Repurposing Engine

**Category**: Content Engine
**Applies To**: Coaching / Consulting
**Deployment Platform**: Make (Integromat), Zapier, GHL, Custom, Notion
**Complexity**: High
**Monthly Value to Client**: $800 - $2,500

### What It Does
A content multiplication agent that takes a single coaching session recording, live presentation, or podcast episode and automatically generates an entire content ecosystem from it — including long-form blog posts, LinkedIn articles, social media post series, email newsletters, short-form video scripts, and quote graphics. It solves the #1 constraint for coaches and consultants: having high-quality expertise trapped in live sessions that never reaches a broader audience.

### Core Capabilities
- Audio/video upload intake with automatic transcription (Whisper AI)
- Key insight extraction: identifies main points, frameworks, stories, and actionable takeaways
- Multi-format content generation from a single transcript:
  - Long-form SEO blog post (1,500–2,500 words)
  - LinkedIn article (800–1,000 words)
  - 5-post social media series (LinkedIn, Instagram, Twitter/X)
  - Email newsletter (500–700 words)
  - Short-form video script/hook for Reels or TikTok
  - 10 standalone quote cards for graphic design
- Brand voice calibration: learns and applies coach's specific voice, terminology, and frameworks
- Content calendar placement: schedules output across platforms using Buffer or Hootsuite
- SEO optimization: keyword injection in blog content based on target audience

### Data Inputs Required
- Recording file (MP4, MP3, MOV) or live transcript
- Brand voice guide (tone, vocabulary, frameworks, signature phrases)
- Target audience personas
- Content calendar and posting frequency preferences
- Platform accounts (Buffer, Hootsuite, or native API access)

### Integration Points
- OpenAI Whisper — audio/video transcription
- OpenAI GPT-4o — content generation engine
- Make / Zapier — workflow orchestration
- Buffer / Hootsuite / Publer — social scheduling
- Notion / Airtable — content inventory database
- Mailchimp / Klaviyo / ConvertKit — newsletter delivery
- Canva API — quote card design generation (optional)

### Sample Prompt/Persona
> [Internal content generation mode] "New session recording received: [Title/Topic]. Transcribing 47-minute coaching session. Extracting key frameworks: identified 3 core concepts, 5 actionable steps, 2 compelling client stories, 4 quotable insights. Generating full content package: (1) Blog post draft — ready. (2) LinkedIn article — ready. (3) 5-post social series — ready. (4) Email newsletter — ready. (5) 8 quote card scripts — ready. All content formatted and ready for review. Estimated posting schedule over next 3 weeks attached."

### Customization Variables
- `voice_calibration_samples` — upload 3–5 examples of preferred past content for voice training
- `output_format_selection` — choose which content types to generate per session
- `posting_schedule` — content spread across days and platforms
- `review_gate` — human review required before publishing or fully automated
- `seo_keywords` — target terms to weave into blog and LinkedIn content
- `quote_card_style` — Canva template or custom design specifications

### Stickiness Factor
Extremely high. Coaches who experience the multiplication of a single session into 20+ pieces of content undergo a fundamental shift in how they think about content creation. The system becomes the foundation of their content marketing strategy. Once the voice is calibrated and the workflow is running, it is operationally irreplaceable.

### Upsell Path
- Add podcast distribution automation: episode → all podcast platforms + show notes + episode summary email
- Upgrade to YouTube SEO package: session → YouTube video script, thumbnail concept, description, and tags
- Bundle with SKILL-116 (Webinar Agent) for a complete thought leadership content engine
- White-label version for marketing agencies serving multiple coach clients

---

## SKILL-114: AI Course/Program Delivery Agent

**Category**: Workflow Automation + Chat Agent
**Applies To**: Coaching / Consulting
**Deployment Platform**: Kajabi, Teachable, GHL, Custom, Zapier
**Complexity**: High
**Monthly Value to Client**: $700 - $2,200

### What It Does
A fully automated course and program delivery system that manages the entire student/client learning journey — from enrollment confirmation through drip content delivery, module completion tracking, quiz administration, accountability check-ins, certificate generation, and community management prompts. It allows coaches and course creators to run high-touch learning programs at scale without proportional administrative overhead.

### Core Capabilities
- Enrollment intake with cohort and access level assignment
- Drip content scheduling: releases modules based on time elapsed or completion triggers
- Module completion tracking with automated unlock sequences
- Quiz and assessment delivery with auto-grading for objective questions
- Progress-based nudges: messages triggered by inactivity, incomplete quizzes, or missed milestones
- Accountability check-in system: weekly prompts for reflection and progress submission
- Certificate of completion generation on final module completion
- Community engagement prompts: pushes students to Facebook Group or Circle.so with module-specific discussions
- Cohort communication: broadcasts to all students in a specific cohort

### Data Inputs Required
- Course structure: module list, content URLs, quiz questions, and release schedule
- Student enrollment data and contact information
- Platform API credentials (Kajabi, Teachable, Thinkific, or GHL)
- Certificate template design
- Community platform link (Facebook Group, Circle, Slack)

### Integration Points
- Kajabi / Teachable / Thinkific — course hosting platform sync
- GHL — student communication sequences and pipeline tracking
- Zapier — enrollment trigger and completion event webhooks
- Typeform / Google Forms — quiz and reflection form delivery
- DocuSend / Canva — certificate generation
- Circle.so / Slack / Facebook Groups — community integration
- Zoom — live coaching call scheduling and reminder delivery

### Sample Prompt/Persona
> "Welcome to [Program Name], [Student Name]! I'm your program guide. Here's how this works: each week, I'll unlock a new module for you, check in on your progress, and keep you on track. Week 1 content is now available: [link]. After you finish, complete the short reflection form and I'll unlock Week 2. You'll also get a reminder on [Day] each week. If you ever fall behind, just text me back and we'll figure it out together. Let's go!"

### Customization Variables
- `drip_type` — time-based (weekly unlock) or completion-triggered (finish module → unlock next)
- `quiz_grading` — auto-graded or submission only for coach review
- `inactivity_threshold_days` — how long before a nudge is sent to inactive students
- `certificate_template` — branded design with coach signature and completion date
- `cohort_vs_self_paced` — fixed start date cohort model or open enrollment
- `community_platform` — Facebook, Circle, Slack, or Discord

### Stickiness Factor
High. Course operators who run a live program manually understand the chaos — the late enrollments, missed modules, endless "where's my content?" questions. An automated delivery system becomes the operational backbone of the business. Completion rates also improve, driving more testimonials and referrals.

### Upsell Path
- Upgrade to AI teaching assistant: students can ask questions about course content and get context-aware answers
- Add cohort analytics dashboard: completion rates, quiz scores, engagement metrics per cohort
- Bundle with SKILL-115 (Progress Tracker) for a fully integrated program delivery + coaching system
- High-ticket mastermind version: smaller cohorts with premium accountability features

---

## SKILL-115: AI Client Progress Tracker

**Category**: Operations + Chat Agent
**Applies To**: Coaching / Consulting
**Deployment Platform**: GHL, Notion, Airtable, WhatsApp, Custom
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,500

### What It Does
An intelligent accountability and progress tracking agent that maintains structured goal records for each coaching client, conducts regular check-ins via text/WhatsApp/email, logs progress submissions, identifies clients who are falling behind or disengaging, and celebrates milestones automatically — allowing coaches to maintain a high-quality accountability relationship with every client simultaneously without the manual overhead of individual check-in management.

### Core Capabilities
- Goal intake and structured documentation: SMART goals with metrics, timelines, and milestones
- Scheduled check-in delivery: weekly, bi-weekly, or custom cadence via preferred channel
- Progress submission collection: numerical ratings, short reflections, or structured forms
- Trend analysis: tracks momentum — improving, plateauing, or declining
- Coach alert: flags clients who miss 2+ check-ins or show declining progress scores
- Milestone celebration automation: congratulations message + coach notification at key milestones
- Session prep report: before each coaching call, generates a progress summary for the coach
- End-of-program summary report: complete journey from start to finish with all tracked metrics

### Data Inputs Required
- Client onboarding goals and baseline metrics
- Coaching program structure and milestone definitions
- Check-in question templates per goal type
- Coach's response preferences (immediate AI response vs. human coach review)
- Session schedule for pre-call report timing

### Integration Points
- GHL — client pipeline and sequence management
- Notion / Airtable — goal and progress data storage
- Twilio SMS / WhatsApp Business — check-in delivery channel
- Typeform / JotForm — structured progress submission forms
- Zoom / Calendly — session prep report tied to upcoming call
- Canva — milestone celebration graphic generation (optional)

### Sample Prompt/Persona
> "Hey [Client Name]! Quick weekly check-in. Just 3 questions: (1) On a 1–10 scale, how aligned were your actions with your goals this week? (2) What was your biggest win? (3) What got in the way? Your answers help me keep your coaching sessions laser-focused. Takes about 2 minutes. I'll send your coach a summary before your next session on [Date]."

### Customization Variables
- `check_in_frequency` — weekly, bi-weekly, daily (intensity programs), or custom
- `question_templates` — by goal type (business, fitness, relationships, mindset)
- `scale_type` — 1–10 ratings, binary (yes/no on action items), or free-text
- `coach_alert_threshold` — consecutive missed check-ins before alert
- `milestone_definitions` — 30-day, 60-day, 90-day, or custom milestones per program
- `session_prep_lead_time` — how many hours before a session the prep report is generated

### Stickiness Factor
High. Client progress tracking is the core deliverable of a coaching practice. Coaches who use this system can carry a larger client roster without sacrificing accountability quality. Clients also experience better outcomes, driving retention and referrals. It becomes the operating system of the coaching business.

### Upsell Path
- Add group coaching dashboard: aggregate progress views across cohort
- Upgrade to AI reflection analysis: GPT-powered insight extraction from client check-in responses
- Bundle with SKILL-113 (Content Engine) to turn anonymized client wins into testimonials and case studies
- Program outcome data reporting: aggregate coaching results for sales page social proof

---

## SKILL-116: AI Webinar Registration & Follow-Up Agent

**Category**: Workflow Automation + Chat Agent
**Applies To**: Coaching / Consulting
**Deployment Platform**: GHL, Zoom, ActiveCampaign, Klaviyo, Zapier
**Complexity**: Medium
**Monthly Value to Client**: $600 - $2,000

### What It Does
A complete webinar lifecycle management agent that handles every touchpoint from registration through post-event follow-up — including confirmation and reminder sequences, attendance tracking, no-show re-engagement, replay delivery, offer follow-up sequences, and poll/feedback collection. It converts webinars from one-time events into multi-touch sales and nurture systems that continue generating value for days after the live event.

### Core Capabilities
- Registration intake and confirmation delivery (email + SMS)
- Pre-webinar reminder sequence: 1 week → 1 day → 1 hour → 10 minutes before
- SMS text-to-remind: registrant texts a keyword to join the reminder sequence
- Live attendance tracking via Zoom webhook
- No-show detection: attendees who registered but didn't attend segregated automatically
- No-show follow-up sequence: personalized "here's what you missed" with replay link
- Attendee follow-up sequence: different from no-show — assumes live attendance context
- Replay delivery and expiry management (replay available for X days)
- Offer/CTA follow-up: tracks link clicks and application form completions from offer CTA
- Post-event survey and testimonial collection

### Data Inputs Required
- Webinar topic, date, time, and Zoom/Webinar platform details
- Registration form fields
- Email/SMS content for each sequence touchpoint
- Replay video URL and expiry timeline
- Offer details and application/sales page URL
- Speaker/host branding

### Integration Points
- Zoom Webinars / WebinarJam / Demio — registration and attendance data
- GHL — full sequence management and contact pipeline
- Klaviyo / ActiveCampaign — email sequence delivery
- Twilio SMS — reminder and follow-up text delivery
- Zapier — webhook handler for Zoom attendance events
- Vimeo / Wistia — replay hosting with view tracking
- Typeform — post-event survey delivery

### Sample Prompt/Persona
> [No-show follow-up mode] "Hey [Name], sorry we missed you at [Webinar Title] today! No worries — life gets busy. The good news: I saved your spot in the replay. Here's the link: [URL]. It covers [Top 3 Value Points]. The replay is only available until [Date+3]. If you have a specific question about [Topic], reply to this message and I'll get you an answer personally. And if you're curious about [Offer/Program], here's more info: [link]."

### Customization Variables
- `reminder_sequence_timing` — configurable touchpoint intervals
- `replay_availability_days` — how long replay link stays active
- `no_show_sequence_depth` — 2, 3, or 5 follow-up touches for non-attendees
- `offer_follow_up_trigger` — clicks on CTA link → enters sales sequence
- `attendee_vs_noshow_segmentation` — distinct sequences per segment
- `sms_opt_in_keyword` — custom keyword for text-to-remind feature

### Stickiness Factor
High. Webinars are a major revenue channel for coaches and consultants. A system that measurably increases show rates, captures no-show revenue, and automates the entire post-event sales sequence is permanently embedded in the launch strategy. Webinar ROI attribution becomes clear and addictive.

### Upsell Path
- Upgrade to evergreen webinar automation: pre-recorded webinar runs on autopilot with all the same sequences
- Add AI-powered webinar Q&A assistant: answers attendee questions in the chat in real time
- Bundle with SKILL-113 (Content Engine) to repurpose webinar recording into full content ecosystem
- Post-webinar sales call scheduling automation: high-engagement attendees get personal call invite
# PART 9: ACCOUNTING (117-120)

---

## SKILL-117: AI Invoice Reading & Data Entry Agent

**Category**: Workflow Automation + Operations
**Applies To**: Accounting
**Deployment Platform**: Make (Integromat), Zapier, Custom, QuickBooks, Xero, Bill.com
**Complexity**: High
**Monthly Value to Client**: $800 - $2,500

### What It Does
An AI-powered accounts payable automation agent that monitors an email inbox or document upload portal for incoming vendor invoices, extracts all relevant data fields using OCR and AI vision, categorizes expenses against the chart of accounts, detects duplicates and anomalies, and creates the transaction record in the accounting system — eliminating one of the most time-consuming and error-prone data entry tasks in small business accounting.

### Core Capabilities
- Email inbox monitoring: detects new invoice attachments (PDF, image, Word) automatically
- OCR + AI extraction: vendor name, invoice number, date, due date, line items, amounts, tax, subtotal
- Chart of accounts matching: AI categorizes each line item against the client's specific COA
- Duplicate detection: flags invoices with matching vendor + amount + date combinations
- Anomaly detection: unusual amounts, new vendors, missing required fields
- Automatic transaction creation in QuickBooks, Xero, or Bill.com
- Human review gate: low-confidence extractions routed to accountant for approval
- 3-way match support: matches PO + receipt + invoice when purchase orders exist
- Vendor master maintenance: new vendors auto-created with contact and payment data

### Data Inputs Required
- Email inbox credentials or document upload portal access
- Chart of accounts from accounting software
- Vendor master list (existing vendors for matching)
- Approval workflow rules (dollar thresholds for auto-post vs. human review)
- Accounting system API credentials (QuickBooks, Xero, Bill.com, Sage)

### Integration Points
- Gmail / Outlook — email inbox monitoring for invoice delivery
- QuickBooks Online / Xero / Bill.com / Sage Intacct — transaction creation
- OpenAI GPT-4o Vision / AWS Textract — OCR and document extraction
- Make / Zapier — workflow orchestration
- Google Drive / Dropbox — invoice document archival
- GHL or Slack — anomaly and review alert delivery
- DocuSend / Approval workflow tool — human review routing

### Sample Prompt/Persona
> [Internal workflow mode] "Invoice received from [Vendor Name] — [Date]. Extracting: Invoice #[12345], Amount $[1,247.50], Due [Date+30]. Line items: IT Services $[850], Software License $[397.50]. Matched to vendor master: [Vendor Name] — existing. COA suggestions: IT Services → 6020-Technology, Software License → 6025-Software. Confidence: 94%. No duplicates found. Creating bill in QuickBooks. Status: Posted. Filing invoice to [Google Drive folder]."

### Customization Variables
- `confidence_threshold` — minimum AI confidence % for auto-post vs. human review
- `approval_threshold_dollars` — invoices above this amount always require human approval
- `coa_mapping_rules` — custom vendor-to-account default mappings
- `duplicate_window_days` — lookback period for duplicate detection
- `document_storage_structure` — folder hierarchy for invoice archive
- `po_matching` — enable/disable 3-way PO matching workflow

### Stickiness Factor
Extremely high. Accounts payable data entry is a volume task that firms pay staff significant time to perform. A system that processes invoices with 95%+ accuracy at a fraction of the cost becomes operationally irreplaceable within 60 days. Error rate reduction also provides liability protection.

### Upsell Path
- Add accounts receivable automation: AI generates and sends invoices from time/project data
- Upgrade to spend analytics dashboard: categorized AP data → vendor spend, category trends, budget vs. actual
- Bundle with SKILL-118 (Bank Reconciliation) for a full bookkeeping automation platform
- Expand to multi-entity invoice processing for accounting firms with multiple clients on one platform

---

## SKILL-118: AI Bank Reconciliation Agent

**Category**: Workflow Automation + Analytics
**Applies To**: Accounting
**Deployment Platform**: QuickBooks, Xero, Make, Zapier, Custom
**Complexity**: High
**Monthly Value to Client**: $700 - $2,200

### What It Does
An automated bank reconciliation agent that connects to bank feeds and the general ledger, matches transactions algorithmically, flags discrepancies with explanations, suggests resolutions for unmatched items, and produces a reconciliation report ready for accountant review — transforming a task that typically takes 2–6 hours per account per month into a 15-minute review process.

### Core Capabilities
- Bank feed connection via Plaid, Yodlee, or accounting software native feed
- Transaction matching: exact match (amount + date), fuzzy match (amount ± tolerance, date range)
- Unmatched transaction categorization: missing in ledger, timing differences, bank errors, duplicate entries
- Suggested resolution for each unmatched item: create transaction, match to existing, investigate
- Bank-side vs. ledger-side balance reconciliation with difference calculation
- Outstanding checks and deposits-in-transit identification
- Recurring transaction pattern recognition: flags items that are typically recurring but missing
- Reconciliation report generation in PDF and accounting software format
- Month-end lock: marks period as reconciled in accounting system

### Data Inputs Required
- Bank account credentials or CSV export
- General ledger transaction file or accounting system API access
- Reconciliation period (start and end dates)
- Acceptable matching tolerances (timing and amount variance)
- Known recurring transactions for pattern matching

### Integration Points
- Plaid / Yodlee / MX — bank feed connection
- QuickBooks Online / Xero / Sage — GL transaction data and reconciliation status
- Make / Zapier — workflow automation
- PDF generator — reconciliation report output
- Slack / Email — flagged item alerts for accountant review
- Google Sheets / Airtable — exception report management

### Sample Prompt/Persona
> [Reconciliation report mode] "Bank Reconciliation — [Bank Name] Checking Account — [Month]. Bank ending balance: $[XX,XXX.XX]. Book ending balance: $[XX,XXX.XX]. Matched transactions: 147/152 (97%). Outstanding: 5 items requiring review. Items flagged: (1) $3,400 deposit 11/29 — not yet recorded in QB. Suggestion: Create deposit entry. (2) Check #4521 $890 — issued 10/15, still uncashed — outstanding check. (3) Duplicate entry detected: $245 on 11/3 and 11/4 — same vendor, same amount. Suggest voiding the duplicate. Reconciliation ready for your approval."

### Customization Variables
- `matching_tolerance_days` — date range for fuzzy date matching (±1, ±3, or ±5 days)
- `matching_tolerance_dollars` — acceptable amount variance for fuzzy matching
- `auto_match_vs_suggest` — auto-post high-confidence matches or always require approval
- `outstanding_check_threshold_days` — how old before flagging as potentially lost/void
- `report_format` — accounting software format, PDF, or Excel
- `bank_count` — number of accounts to reconcile simultaneously

### Stickiness Factor
Very high. Bank reconciliation is a monthly non-negotiable in any accounting practice. A system that completes 97%+ of the matching automatically and cuts review time from hours to minutes creates an irreversible productivity dependency. Error detection also builds trust and protects against fraud.

### Upsell Path
- Add credit card reconciliation modules: extends to all payment card accounts
- Upgrade to real-time reconciliation: continuous matching as transactions occur vs. month-end
- Bundle with SKILL-117 (Invoice Agent) for full accounts payable + reconciliation automation
- Cash flow forecasting add-on: reconciled data → 90-day rolling cash flow projection

---

## SKILL-119: AI Tax Document Collector

**Category**: Workflow Automation + Chat Agent
**Applies To**: Accounting
**Deployment Platform**: GHL, Liscio, TaxDome, Custom, Zapier
**Complexity**: Medium
**Monthly Value to Client**: $500 - $1,600

### What It Does
A client tax document collection agent that systematically contacts each tax client to request, track, and confirm receipt of every document needed to complete their return — including W-2s, 1099s, K-1s, brokerage statements, mortgage interest forms, charitable donation receipts, and business expense documentation. It eliminates the most frustrating administrative bottleneck in tax season: chasing clients for missing documents across dozens or hundreds of returns simultaneously.

### Core Capabilities
- Client-specific document checklist generation based on prior year return data and account type
- Multi-channel document request: email, SMS, and secure portal upload link
- Per-document status tracking: requested, received, under review, complete
- Automatic follow-up sequence: re-requests after 5 days, 10 days, and 15 days for missing items
- Document receipt confirmation: AI verifies upload is legible and matches expected document type
- Progress dashboard: firm-wide view of all client files — % complete, blocking items, priority flags
- Automated "all documents received" confirmation to client and staff assignment notification
- Incomplete file escalation: clients with no activity after 3 contact attempts → staff alert

### Data Inputs Required
- Client roster with contact information and preferred communication channel
- Prior year return data or account type flag (W-2 employee, self-employed, rental income, investor, etc.)
- Required document checklist templates per client type
- Secure document upload portal URL
- Firm-specific deadline and staff assignment rules

### Integration Points
- TaxDome / Liscio / Canopy — client portal and document management
- GHL — client communication sequences and pipeline tracking
- Twilio SMS — text-based document request delivery
- DocuSend / Secure file upload portal — document receipt
- Zapier — document upload trigger → checklist update
- QuickBooks / accounting software — account type data for checklist customization

### Sample Prompt/Persona
> "Hi [Client Name], tax season is here! To get started on your [Year] return, I need a few documents from you. Based on what we did last year, here's your personal checklist: [Checklist with checkboxes]. You can upload everything securely here: [portal link]. I'll check off each item as it comes in and let you know when we have everything we need. Got a question about what qualifies? Just reply to this message. Our goal is to have your return filed by [Target Date]."

### Customization Variables
- `document_checklist_templates` — by return type: individual, S-Corp, partnership, etc.
- `follow_up_timing` — days between reminder touchpoints
- `escalation_contact` — which staff member receives alert for stuck clients
- `portal_platform` — TaxDome, Liscio, ShareFile, or custom secure upload
- `deadline_communications` — insert firm-specific filing deadlines into messages
- `multi_language` — support for Spanish, Mandarin, or other client languages

### Stickiness Factor
High. During tax season, document collection is the #1 bottleneck between an accounting firm's capacity and its throughput. A system that reduces the average collection time per client by even 1 week multiplies the firm's effective capacity significantly. Clients also appreciate a clear, organized process.

### Upsell Path
- Add AI document review: uploaded documents automatically checked for completeness and legibility before logging as received
- Upgrade to year-round document retention: extend the collection workflow to ongoing bookkeeping document requests
- Bundle with SKILL-117 (Invoice Agent) and SKILL-118 (Reconciliation) for a full-service AI accounting platform
- Firm analytics add-on: track average document collection time, common missing items, and client responsiveness scoring

---

## SKILL-120: AI Financial Advisory Bot

**Category**: Chat Agent + Analytics
**Applies To**: Accounting
**Deployment Platform**: Custom Web, GHL, WhatsApp, Slack
**Complexity**: High
**Monthly Value to Client**: $700 - $2,200

### What It Does
A plain-language financial intelligence agent that connects to a business client's accounting system and translates complex financial statements — P&L, balance sheet, cash flow statement — into actionable, jargon-free narratives that non-financial business owners can understand and act on. It answers "what does this mean for my business?" questions in real time, surfaces anomalies, benchmarks performance against industry standards, and bridges the gap between monthly accounting data and business decision-making.

### Core Capabilities
- Financial statement reading: connects to QuickBooks, Xero, or Sage for live data
- Plain-language P&L summary: "Your revenue was up 12% but your net profit dropped — here's why"
- Cash flow analysis: explains where cash went and what to watch in the next 30 days
- Balance sheet translation: current ratio, quick ratio, debt-to-equity in business owner language
- Anomaly detection and flagging: unusual expense spikes, revenue dips, account outliers
- Industry benchmarking: compares margins and ratios to industry standards (NAICS-based)
- "What if" scenario modeling: "What happens to my profit if I hire one more employee?"
- Monthly business performance narrative: auto-generated executive summary for owner review
- Question-answering: owner types "why is my gross profit down?" → AI analyzes and responds

### Data Inputs Required
- Accounting system API credentials (QuickBooks, Xero, Sage, FreshBooks)
- Industry classification (NAICS or SIC code) for benchmarking
- Chart of accounts structure for correct categorization
- Owner's preferred reporting frequency (monthly, weekly)
- Business goals and KPIs for context-aware narrative generation

### Integration Points
- QuickBooks Online / Xero / Sage Intacct / FreshBooks — live financial data
- Custom web chat interface or WhatsApp Business — owner-facing interaction
- GHL — monthly narrative delivery via email
- OpenAI GPT-4o — analysis and plain-language generation engine
- Fathom / Spotlight Reporting — optional advanced visualization layer
- Industry benchmarking database (IBISWorld, RMA Annual Statement Studies data)

### Sample Prompt/Persona
> "Hey [Business Owner Name], your April numbers are in. Here's the quick version: Revenue came in at $[X] — up 8% from last month. That's great. But your net profit actually dropped by $[Y]. The main reason: your labor costs increased by 23% in April. If you hired someone new last month, that explains it — and it's expected. If not, it's worth looking at your payroll closely. Cash on hand: $[Z]. Based on your burn rate, you have about [N] weeks of runway. Want me to dig into anything specific?"

### Customization Variables
- `reporting_frequency` — monthly auto-send, on-demand, or triggered by accounting period close
- `narrative_complexity` — very simple (non-financial owner) vs. moderate (savvy owner) vs. detailed (CFO-level)
- `kpi_dashboard` — which 5–8 metrics are most important for this business type
- `benchmarking_source` — IBISWorld, RMA, or custom peer group data
- `alert_thresholds` — define what triggers an anomaly alert (e.g., expense category spikes >20%)
- `language` — multi-language support for multilingual business owners

### Stickiness Factor
Extremely high. Business owners who receive clear, jargon-free financial intelligence monthly begin to rely on it for every business decision. This creates a direct value relationship between the accounting firm and the owner that goes beyond compliance services — positioning the firm as a strategic advisor and dramatically reducing client churn.

### Upsell Path
- Upgrade to fractional CFO service: AI bot + monthly 30-minute advisor call becomes a premium offering
- Add rolling cash flow forecasting: 13-week forward-looking cash model updated weekly
- Bundle with SKILL-117, SKILL-118, and SKILL-119 for a complete AI-powered accounting operations platform
- Multi-entity dashboard: consolidated financial intelligence across all business entities for holding company owners
