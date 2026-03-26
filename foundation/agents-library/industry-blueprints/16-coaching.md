# Coaching & Consulting — AI Agent Ecosystem Blueprint

## Industry Overview
Coaching and consulting businesses live and die by the relationship between practitioner and client. The core business model is time-for-money but the highest-leverage operators have shifted to productized programs, group cohorts, courses, and community memberships. AI agents in this space must handle the full client lifecycle — from cold lead to raving referral — while preserving the human authenticity that coaches sell. The stickiest AI implementations reduce admin overhead, automate content multiplication, and create accountability loops that clients actually feel.

**Primary Revenue Streams:** 1:1 coaching packages, group programs, online courses, masterminds, workshops/retreats, speaking, affiliate/sponsorship.
**Primary Pain Points:** Calendar chaos, content creation bottleneck, client accountability gaps, inconsistent follow-up, revenue unpredictability.
**Ideal AI Stack Outcome:** A coach who works 20 hours/week on delivery while the AI handles 40+ hours of admin, nurture, content, and community.

---

## Sub-Agents Breakdown

### 1. Discovery Call Scheduling & Pre-Qualification Agent
- **Type**: Voice + Chat + Workflow
- **Function**: Intercepts inbound leads from website, social DMs, and ads. Asks 5-7 pre-qualification questions (budget, timeline, goals, current situation, urgency) via conversational chat or voice. Scores the lead against an ideal client profile rubric. Auto-books qualified leads directly to the coach's calendar; sends nurture sequence to unqualified leads. Generates a pre-call brief for the coach including prospect answers, social profile research, and suggested talking points.
- **Trigger**: Form submission, website chat widget open, Instagram/Facebook DM keyword (e.g., "interested", "tell me more"), ad landing page visit
- **Integrations**: Calendly / Acuity / Cal.com, CRM (HubSpot, GoHighLevel, Keap), Zapier/Make, LinkedIn Sales Navigator, Meta DMs API
- **Sticky Factor**: Coach becomes dependent on the automated lead brief — going back to manual discovery feels like flying blind
- **Implementation Notes**: Requires a scoring rubric built from the coach's ideal client criteria. Voice variant needs Twilio or VAPI. Pre-call brief generation uses GPT-4o with a structured prompt template pulling CRM data.

### 2. Client Onboarding Workflow Agent
- **Type**: Workflow + Chat
- **Function**: Triggers immediately upon payment receipt. Sends welcome email with personalized video (Loom or HeyGen AI avatar), delivers contract via DocuSign/PandaDoc for e-signature, sends intake questionnaire (goals, challenges, communication preferences, working style), creates client folder in Google Drive/Notion, adds client to coaching platform (Kajabi, Teachable, Mighty Networks), schedules kickoff call, and triggers welcome gift notification if applicable. Sends daily gentle nudges until all onboarding steps are complete.
- **Trigger**: Payment confirmed in Stripe/PayPal/ThriveCart
- **Integrations**: Stripe, DocuSign/PandaDoc, Google Drive/Notion, Kajabi/Teachable, Calendly, ActiveCampaign/ConvertKit, Loom/HeyGen
- **Sticky Factor**: Clients experience a world-class onboarding that feels white-glove; coach never has to manually track who signed what
- **Implementation Notes**: Use webhook from payment processor to trigger Make/Zapier sequence. All steps should have completion tracking with timeout escalation to coach after 48 hours of inactivity.

### 3. Session Scheduling & Reminder Agent
- **Type**: Workflow + Voice
- **Function**: Manages all session booking, rescheduling, and cancellation. Sends multi-channel reminders (email at 48 hrs, SMS at 24 hrs, push notification at 1 hr before). Sends a pre-session prep prompt ("What's your #1 focus for today's call?") 2 hours before each session. After rescheduling, updates all downstream calendar holds and notifies any group participants. Flags recurring cancelers to coach dashboard.
- **Trigger**: New booking confirmed, 48/24/1 hour before session time, cancellation event
- **Integrations**: Calendly/Acuity, Google Calendar/Outlook, Twilio SMS, Zoom/Google Meet, GoHighLevel
- **Sticky Factor**: Clients get trained to expect the prep prompt; it improves session quality, which they attribute to the coach
- **Implementation Notes**: SMS reminders require Twilio or similar. Recurring canceler flag requires a session attendance tracker table (Airtable or CRM custom field with counter logic).

### 4. AI Content Repurposing Engine
- **Type**: Workflow + AI Processing
- **Function**: Ingests raw coaching session recordings (Zoom, Riverside, Loom). Transcribes via Whisper/AssemblyAI. Extracts key insights, frameworks, and quotable moments. Automatically generates: 1 long-form blog post, 5 social media posts (LinkedIn, Instagram, Facebook), 1 email newsletter, 3 short-form video clip scripts (with timestamps for editor), 10 tweet/X thread items, and 1 YouTube description + title + tags. Outputs all assets to a Google Drive content folder organized by date. Sends Slack/email notification to coach with preview.
- **Trigger**: Session recording uploaded to designated folder OR Zoom cloud recording webhook
- **Integrations**: Zoom API, AssemblyAI/Whisper, OpenAI GPT-4o, Google Drive, Buffer/Later/Metricool, Mailchimp/ConvertKit, Slack
- **Sticky Factor**: Coach's entire content calendar runs off their natural coaching conversations — stopping feels like going content-silent
- **Implementation Notes**: Build a brand voice document and inject it into every generation prompt. Video clip timestamps require the transcript to include word-level timestamps. Recommended processing time: 15-20 min per 60-min session.

### 5. Course & Program Delivery Agent
- **Type**: Workflow + Chat
- **Function**: Manages drip content delivery based on enrollment date or completion milestones. Unlocks new modules when previous ones are completed or after set intervals. Sends module introduction emails with context and instructions. Tracks quiz completion and scores; triggers re-study recommendation if score is below threshold. Sends completion celebrations and badge/certificate delivery. Identifies students who haven't logged in for 7+ days and sends personalized re-engagement messages.
- **Trigger**: Module completion event, scheduled drip date, login gap detection, quiz submission
- **Integrations**: Kajabi/Teachable/Thinkific/Podia, Zapier/Make, ActiveCampaign, Slack (student community)
- **Sticky Factor**: Students feel guided rather than abandoned; completion rates improve, which generates better testimonials
- **Implementation Notes**: Platform-native automations handle most drip logic; external agent layer adds the personalization and re-engagement intelligence. Requires LMS with API or webhook support.

### 6. Group Coaching Session Manager
- **Type**: Workflow + Voice + Chat
- **Function**: Handles registration, payment, and group roster management for cohort or recurring group calls. Sends group-specific reminders with Zoom link and agenda. Collects pre-call hot seat requests ("What would you like to bring to the group this week?"). Records sessions, generates AI summary with action items per participant, distributes recording and summary within 30 minutes of call end. Sends follow-up accountability check-in 48 hours later.
- **Trigger**: Group session registration, scheduled call time, session end (Zoom webhook), 48-hour post-call timer
- **Integrations**: Zoom, Calendly/Eventbrite, Stripe, AssemblyAI, Google Drive, ActiveCampaign, Circle/Mighty Networks/Slack
- **Sticky Factor**: Participants get a personalized summary even in a group setting — feels like 1:1 attention at group pricing
- **Implementation Notes**: AI summary generation must be participant-aware; requires mapping Zoom display names to CRM records. Hot seat request collection best handled via a simple form or chat bot pre-call.

### 7. Client Progress Tracker & Accountability Agent
- **Type**: Chat + Workflow + Dashboard
- **Function**: Conducts weekly async check-ins via SMS or email (customizable cadence). Asks structured questions: goal progress (1-10), wins this week, obstacles, support needed. Logs responses to client dashboard. Flags clients who are below a progress threshold or haven't responded. Sends automated milestone celebrations (50% complete, program graduation). Generates a weekly coach dashboard showing all client progress scores in a single view. Sends coach alerts for clients at risk.
- **Trigger**: Weekly schedule, milestone completion event, non-response after 24 hours, score below 5/10 threshold
- **Integrations**: Twilio SMS, Airtable/Notion (client dashboard), GoHighLevel, Slack (coach alerts), Typeform/JotForm
- **Sticky Factor**: Coach sees their entire client base's wellbeing at a glance — impossible to go back to spreadsheets
- **Implementation Notes**: Use a consistent check-in format to enable trend analysis over time. NLP sentiment analysis on free-text responses adds depth. Airtable interface is a fast MVP for the dashboard.

### 8. Testimonial & Case Study Collector
- **Type**: Workflow + Chat
- **Function**: Automatically triggers at program completion, 30 days post-completion, and at milestone moments. Sends a conversational testimonial collection sequence (not a boring form) — asks about before/after transformation, specific results, who they'd recommend the program to. Uses responses to auto-generate a polished testimonial draft for client approval. Requests video testimonial via Bonjoro/Testimonial.to. Compiles approved testimonials into a shareable case study document and social proof bank.
- **Trigger**: Program completion date, 30-day post-program timer, milestone achievement event
- **Integrations**: Testimonial.to/Bonjoro, Typeform/Tally, Google Drive, Canva API (for formatted quote graphics), ActiveCampaign
- **Sticky Factor**: Coach's sales page stays perpetually fresh without ever having to ask for testimonials manually
- **Implementation Notes**: Response rate is highest within 24-48 hours of a win moment. Conversational collection (chat sequence vs. form) typically yields 3x longer, more specific responses.

### 9. Webinar & Workshop Registration Agent
- **Type**: Workflow + Chat
- **Function**: Manages the full event funnel: landing page chat widget for last-minute questions, registration confirmation sequence, pre-event education sequence (builds excitement and authority), day-of reminder with tech-check instructions, live event support bot (answers FAQs in chat so host can focus on presenting), post-event replay delivery, and post-event offer follow-up sequence with urgency-based logic (different messages for attendees vs. no-shows vs. replay viewers).
- **Trigger**: Event registration, 24/1 hour pre-event, event end, replay link click, offer page visit
- **Integrations**: Zoom Webinars/Demio/WebinarJam, ActiveCampaign/Klaviyo, Stripe, Calendly (post-webinar calls), ClickFunnels/Kajabi
- **Sticky Factor**: The behavioral segmentation (attendee vs. no-show vs. replay) generates significantly higher conversion — coach won't abandon it
- **Implementation Notes**: Webinar platform must support attendee status webhooks. Replay tracking requires UTM-tagged links or unique redirect URLs per segment.

### 10. Lead Magnet Delivery & Nurture Sequence Agent
- **Type**: Workflow
- **Function**: Instantly delivers lead magnet (PDF, checklist, mini-course, quiz, challenge) upon opt-in. Tags subscriber by lead magnet topic in CRM. Initiates a 7-14 day nurture sequence that provides value, establishes authority, handles common objections, and makes a soft offer. Tracks engagement (opens, clicks, quiz completions) and dynamically adjusts next email based on behavior. Moves engaged leads into a "warm lead" pipeline stage and alerts coach or triggers discovery call offer.
- **Trigger**: Opt-in form submission, quiz completion, content upgrade download
- **Integrations**: ActiveCampaign/ConvertKit/Klaviyo, Leadpages/ClickFunnels, Typeform (quiz), Google Drive (PDF delivery), Calendly
- **Sticky Factor**: The behavioral branching creates a self-optimizing funnel — every week it gets more efficient without the coach doing anything
- **Implementation Notes**: Tag taxonomy must be consistent to avoid CRM chaos. Quiz-based lead magnets (e.g., "What type of coach do you need?") outperform static PDFs 2-3x on engagement metrics.

### 11. Podcast Guest Booking Agent
- **Type**: Workflow + Email
- **Function**: Manages outbound podcast pitching workflow. Researches target podcasts for fit, audience size, and recent episode topics. Drafts personalized pitch emails using coach's bio, topics, and past press. Tracks pitch status in a pipeline (pitched, followed up, booked, recorded, published). Sends prep materials to podcast host before recording. After episode publishes, triggers a cross-promotion sequence to both audiences. Logs all appearances in a press/media kit document.
- **Trigger**: New podcast target added to list, follow-up timer (7 days after pitch), episode publish notification
- **Integrations**: Gmail/Outlook, Airtable (podcast pipeline), Podchaser API, Zapier, Google Drive (press kit), ActiveCampaign
- **Sticky Factor**: Coach builds a consistent media presence without dedicated PR staff; the pipeline visibility makes it easy to scale
- **Implementation Notes**: Personalization quality determines reply rate — generic pitches fail. Requires a good source of podcast data (Podchaser, Listen Notes, or manual curation). Open tracking via email platform is essential.

### 12. Community Management Agent
- **Type**: Chat + Workflow
- **Function**: Monitors Facebook Group, Slack workspace, or Circle community 24/7. Answers common FAQs automatically (program details, next call times, resource locations). Welcomes new members with a personalized introduction prompt. Detects low-engagement members and sends re-engagement messages. Flags posts that require coach attention. Surfaces top-engaged members for potential mentorship or leadership opportunities. Generates weekly community health report (new members, posts, engagement rate, top contributors).
- **Trigger**: New member join, new post/comment, member inactivity (7 days), keyword detection, weekly schedule
- **Integrations**: Facebook Groups API, Slack API, Circle API, Mighty Networks, OpenAI, Zapier/Make
- **Sticky Factor**: Community feels alive even when coach isn't present; members stay subscribed longer because engagement is consistent
- **Implementation Notes**: Facebook Groups API is restrictive — ManyChat or GoHighLevel are better intermediaries. Circle and Slack have more open API access. Moderation logic needs clear guidelines to avoid false positives.

### 13. Client Renewal & Upsell Agent
- **Type**: Workflow + Chat
- **Function**: Monitors program completion dates and triggers a retention/upsell sequence 2-3 weeks before program end. Sends a personalized "what you've accomplished" summary pulling from progress tracker data. Presents next-step program options based on client's goals and current stage. Handles objection FAQs via chat. Offers a loyalty discount for immediate re-enrollment. If no response after sequence, escalates to coach for personal outreach. Logs all renewal outcomes and reasons for non-renewal.
- **Trigger**: 21 days before program end date, program completion event, no-purchase after 5-day sequence
- **Integrations**: CRM (GoHighLevel/HubSpot), Stripe, ActiveCampaign, Calendly (renewal call option), Airtable
- **Sticky Factor**: Renewal becomes a proactive retention system rather than a reactive hope — LTV increases measurably
- **Implementation Notes**: Personalized accomplishment summary requires integration with the Progress Tracker agent data. Loyalty pricing logic must be implemented in Stripe via coupon codes with expiry.

### 14. Revenue & Pipeline Dashboard Agent
- **Type**: Dashboard + Workflow
- **Function**: Aggregates revenue data from all payment processors and program types into a single real-time dashboard. Tracks MRR, new enrollments, churn, average client value, pipeline value, and conversion rates at each funnel stage. Sends a daily revenue summary to coach via Slack or email at 8am. Alerts coach when a revenue goal milestone is hit. Generates monthly performance report with trend analysis and recommendations. Forecasts next 30/60/90-day revenue based on current pipeline.
- **Trigger**: Daily 8am schedule, payment received, pipeline stage change, end of month
- **Integrations**: Stripe/ThriveCart/Kajabi, GoHighLevel/HubSpot CRM, Google Sheets/Airtable, Slack, Looker Studio/Databox
- **Sticky Factor**: Coach makes decisions from data rather than gut feel — reverting to no dashboard feels reckless
- **Implementation Notes**: Stripe Revenue Recognition is useful for MRR calculations. Looker Studio with Stripe and CRM connectors is a fast, no-code dashboard option. Daily Slack digest should be <5 lines — brevity drives consistent readership.

### 15. Referral Program Manager
- **Type**: Workflow + Chat
- **Function**: Automates the coach's referral or affiliate program. Generates unique referral links for each client/partner. Tracks referral clicks, sign-ups, and conversions. Triggers thank-you message and reward delivery (credit, cash, free session) when a referral converts. Sends monthly referral performance update to active referrers. Identifies top referrers for a VIP affiliate tier. Handles payout processing via PayPal or Stripe.
- **Trigger**: Referral link click, new signup from referral, referral conversion (payment), monthly schedule
- **Integrations**: Rewardful/FirstPromoter/PartnerStack, Stripe, PayPal, ActiveCampaign, Slack
- **Sticky Factor**: Clients who refer become emotionally invested in the brand's success; churn rate among referrers is dramatically lower
- **Implementation Notes**: Choose a referral platform that integrates natively with Stripe for automatic attribution. Reward delivery automation requires Stripe payout API or PayPal Mass Payments.

### 16. Speaking Engagement & Event Booking Agent
- **Type**: Workflow + Email
- **Function**: Manages the inbound and outbound speaking pipeline. Responds to inbound speaking inquiries with speaker kit, topic menu, and availability. Tracks outbound prospecting to event organizers and conference planners. Drafts customized speaking proposals. Sends logistics checklist to confirmed event organizers (AV requirements, bio, headshot, travel needs). Triggers post-event follow-up sequence to attendees (if list is provided) and host for testimonial. Logs all speaking history and metrics.
- **Trigger**: Speaking inquiry form submission, new outbound prospect added, event confirmed, event date passed
- **Integrations**: Gmail/Outlook, Airtable (speaking pipeline), Calendly, Dropbox/Google Drive (speaker kit), DocuSign (speaking agreement), ActiveCampaign
- **Sticky Factor**: Speaking opportunities become a managed revenue channel rather than ad hoc wins
- **Implementation Notes**: Speaker kit should be a dynamic link (Notion page or PDF auto-generated from template) so it stays current. DocuSign speaking agreement protects fees and expectations.

### 17. Client Feedback & NPS Survey Agent
- **Type**: Workflow
- **Function**: Sends NPS surveys at program midpoint and completion. Follows up with long-form qualitative survey for detractors (score 0-6) to understand issues, and for promoters (score 9-10) to collect testimonials and referral interest. Routes detractor responses immediately to coach for relationship repair. Tracks NPS trend over time and by program type. Generates quarterly feedback report with top themes extracted via NLP.
- **Trigger**: Program midpoint date, program completion date, NPS score submitted (immediate routing for detractors)
- **Integrations**: Delighted/Typeform/SurveyMonkey, ActiveCampaign, Slack (coach alert for detractors), Airtable, OpenAI (theme extraction)
- **Sticky Factor**: Coach has a real-time pulse on client satisfaction and can fix problems before they become refund requests or public reviews
- **Implementation Notes**: NPS survey timing matters — send within 24 hours of a milestone for highest response rates. NLP theme extraction from free-text responses requires a structured prompt template that outputs categorized JSON.

---

## Industry-Specific Intake Forms

### Discovery Call Pre-Qualifier
- Current revenue / business stage
- #1 goal in next 90 days
- What have you already tried?
- Investment readiness (budget range)
- Timeline urgency
- How did you hear about us?
- Preferred communication style (direct/detailed)

### Client Onboarding Intake
- Full business background and history
- Top 3 goals for the coaching engagement
- Biggest fears / limiting beliefs to address
- Accountability preferences (check-ins, tough love vs. gentle)
- Communication channel preference (email / SMS / Voxer / Slack)
- Existing assets (team, tools, audience size, content library)
- Previous coaching experience and outcomes

### Session Prep Form (sent before each session)
- Progress on last session commitments (1-10)
- Biggest win since last call
- Biggest challenge or obstacle
- Top priority for today's session
- Anything else coach should know

---

## Interactive Widgets & Tools

| Widget | Description | Platform |
|--------|-------------|----------|
| Discovery Call Qualifier Chat | Embedded website chatbot that pre-quals leads before showing calendar | Tidio, ManyChat, GoHighLevel |
| Goal Progress Dashboard | Client-facing portal showing goal completion, session history, and milestones | Notion, Kajabi, custom app |
| Content Repurposing Hub | Internal tool where coach uploads recordings and downloads finished content assets | Custom Make/Zapier interface |
| Community Engagement Score | Public leaderboard for group program members (gamified points) | Circle, Mighty Networks |
| NPS Trend Visualizer | Rolling NPS chart over program cohorts | Looker Studio, Databox |
| Referral Tracking Portal | Client-facing portal showing their referral stats and earned rewards | Rewardful, FirstPromoter |
| ROI Calculator | Prospect-facing tool: "What would 10x your revenue be worth?" | Outgrow, custom JS embed |

---

## Employee Role Mapping

| Role | Agents They Use Daily | Time Saved/Week |
|------|-----------------------|-----------------|
| Head Coach | Progress Tracker, Dashboard, Session Scheduler | 8-10 hrs |
| Program Manager | Onboarding, Course Delivery, Group Session Manager | 12-15 hrs |
| Content Manager | Content Repurposing Engine | 10-12 hrs |
| Community Manager | Community Agent, Feedback Collector | 6-8 hrs |
| Sales/Enrollment | Discovery Qualifier, Renewal Agent, Referral Manager | 8-10 hrs |
| VA / Operations | Webinar Agent, Speaking Pipeline, NPS Surveys | 6-8 hrs |

---

## Integration Architecture

```
LEAD ENTRY LAYER
Website / Social / Ads → Discovery Qualifier Agent → CRM (GoHighLevel / HubSpot)

CONVERSION LAYER
CRM → Sales Pipeline → Discovery Call Booking → Enrollment → Stripe Payment

ONBOARDING LAYER
Stripe Webhook → Onboarding Agent → DocuSign + Drive + Platform Access + Kickoff Call

DELIVERY LAYER
Coaching Platform (Kajabi) + Zoom Sessions → Content Repurposing Engine
Session Scheduler + Reminder Agent + Progress Tracker running in parallel

RETENTION LAYER
Progress Tracker → Renewal Agent → Upsell Sequence
Community Agent → Engagement monitoring → Re-engagement triggers

GROWTH LAYER
Testimonial Collector → Social Proof Bank
Referral Manager → Pipeline → Rewards
Podcast / Speaking Agents → Media Presence → Inbound Leads
```

---

## Competitive Intelligence

| Competitor Type | Their Weakness | Your AI Advantage |
|-----------------|----------------|-------------------|
| Solo coaches (no tech) | Manual everything, inconsistent follow-up | Automated lifecycle = professional at scale |
| Large coaching companies | Generic, cookie-cutter experience | AI personalization at every touchpoint |
| Course platforms (no coaching) | No accountability, high drop-off rates | Progress tracking + human touchpoints |
| Masterminds | High price, low accessibility | AI-supported group coaching scales intimacy |

**Key Differentiators to Market:**
- "We never miss a follow-up" — automated accountability
- "Your content works 24/7" — repurposing engine
- "Every client feels like your only client" — AI personalization at scale

---

## Revenue Model

| Stream | AI Enhancement | Revenue Lift Potential |
|--------|----------------|----------------------|
| 1:1 Coaching | Efficiency gain → take more clients | +30-50% capacity |
| Group Programs | Manager agent scales to 100+ clients | 5-10x group size |
| Online Courses | Delivery + re-engagement agent → completion | +40% completion, +testimonials |
| Webinars | Pre/post sequence → conversion rate | +15-25% conversion |
| Referrals | Automated program → consistent pipeline | +20-30% new client volume |
| Renewals | Proactive retention sequence | +25-35% LTV improvement |

---

## Stickiest Features (Top 5)

1. **Content Repurposing Engine** — Once a coach's entire content calendar runs from their session recordings, they are architecturally locked in. The alternative is hours of manual work per week.

2. **Client Progress Dashboard** — Coaches who can see every client's wellbeing at a glance will never manage clients via email again. The visibility is addictive.

3. **Discovery Call Pre-Qualifier** — After experiencing a qualified lead who already answered their discovery questions in advance with a pre-call brief, coaches are unable to imagine going back to cold calls.

4. **Session Reminder + Prep Sequence** — Clients who receive prep prompts come to sessions with more clarity. The quality of sessions visibly improves, which reinforces the coach's belief in the system.

5. **Renewal & Upsell Agent** — When the agent generates a personalized accomplishment summary at program end and presents next steps with a conversion rate above 30%, coaches see it as a sales team member they'd never fire.
