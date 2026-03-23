/**
 * AutomationNationOS.jsx
 * Automation Nation — Claude Foundation
 * AI Employee Management & Testing Interface
 *
 * Features:
 *  - 14 AI agents across 4 departments
 *  - Live Claude AI chat per agent (Anthropic API)
 *  - Skills & Expertise modal per agent
 *  - System prompt editor (edit any agent's brain)
 *  - Business context panel (shared across all agents)
 *  - Conversation history per agent
 *  - Export conversations
 *  - Search agents
 *  - Category collapse/expand
 *
 * API calls are proxied through /api/chat — the Anthropic key
 * is server-side only (ANTHROPIC_API_KEY env var on Render).
 */

import React, { useState, useRef, useEffect } from 'react';

// ─────────────────────────────────────────────────────────────
// STYLES
// ─────────────────────────────────────────────────────────────
const STYLES = `
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,#root{height:100%;font-family:'DM Sans',sans-serif}
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,0.18)}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes msgIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.9)}}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
@keyframes spin{to{transform:rotate(360deg)}}
.an-agent:hover{background:rgba(255,255,255,.05)!important}
.an-agent.sel{background:#1a2340!important}
.an-prompt:hover{background:#161d35!important;border-color:rgba(255,255,255,.12)!important;transform:translateY(-1px)}
.an-skill-row:hover{background:#161d35!important;border-color:rgba(255,255,255,.1)!important}
.an-tab.on{color:#fff!important;border-bottom:2px solid #6366f1}
.an-tab:hover{color:rgba(255,255,255,.8)!important}
.an-send:hover:not(:disabled){background:#5254cc!important;transform:scale(1.05)}
.an-send:active:not(:disabled){transform:scale(.97)}
.an-cat:hover{color:rgba(255,255,255,.5)!important}
.an-cap-badge:hover{background:#1f2847!important;border-color:rgba(255,255,255,.12)!important}
.an-modal-in{animation:fadeUp .25s ease}
.an-msg-a{animation:msgIn .3s ease}
.an-msg-u{animation:msgIn .2s ease}
.an-dot-1{animation:bounce 1s ease 0s infinite}
.an-dot-2{animation:bounce 1s ease .15s infinite}
.an-dot-3{animation:bounce 1s ease .3s infinite}
.an-status{animation:pulse 2.5s ease infinite}
`;

// ─────────────────────────────────────────────────────────────
// AGENT DATA
// ─────────────────────────────────────────────────────────────
const CATEGORIES = [
  {
    id:'foundations', label:'Foundations', color:'#818cf8',
    agents:[
      {
        id:'alex', name:'John', role:'General Assistant',
        icon:'M12 2a10 10 0 100 20A10 10 0 0012 2zm0 2l2.5 5.5H9.5L12 4zm0 16l-2.5-5.5h5L12 20zm-8-8l5.5-2.5v5L4 12zm16 0l-5.5 2.5v-5L20 12z',
        desc:'Your starting point. I know every agent on the team and can route you to exactly the right specialist for your challenge.',
        prompts:['What can the team help me with?','Who should I talk to about growing my agency?','I need help with sales outreach','Show me all available specialists'],
        helpWith:['Agent routing','Quick business Q&A','Team navigation','Task planning','Daily briefing'],
        skills:[
          {name:'Task Router',desc:'Routes any request to the right specialist instantly',status:'Active'},
          {name:'Business Brief',desc:'Captures your business context for the whole team',status:'Active'},
          {name:'Daily Briefing',desc:'Morning summary of priorities and outstanding tasks',status:'Active'},
          {name:'Team Handoff',desc:'Passes full context when escalating to a specialist',status:'Active'},
        ],
        integrations:[],
        prompt:`You are John, the General Assistant for Automation Nation — an AI automation and voice agent agency. You are the first point of contact and team navigator.

Your team (all AI agents):
FOUNDATIONS: Paul (Mindset Coach), Mary (Business Strategist), Luke (Legal Assistant)
SALES & MARKETING: Deborah (Lead Generator), Nathan (Outreach Specialist), Anna (Content Strategist), Joseph (Sales Coach)
FULFILLMENT: Naomi (Marketing Strategist), Lydia (Creative Strategist), Martha (Copywriter), Leah (Ad Specialist)
OPERATIONS: Delilah (Communication Coach), Hannah (Hiring Assistant), Peter (Systems Architect)

When someone comes to you, understand their need and either answer directly or clearly recommend which team member is best suited and why. For general business questions, answer confidently. Be warm, sharp, and efficient. Never waste words. Make the user feel like they have an entire elite team ready to execute.`
      },
      {
        id:'blake', name:'Paul', role:'Mindset Coach',
        icon:'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
        desc:'Remove mental blocks, build unshakeable discipline, and develop the psychology of a top-performing agency owner.',
        prompts:["I'm overwhelmed and don't know where to start","Help me stop procrastinating on sales calls","I keep doubting myself — imposter syndrome is real","How do I think like a 7-figure owner?"],
        helpWith:['Mindset shifts','Overcoming fear','Discipline systems','Confidence building','Accountability frameworks'],
        skills:[
          {name:'Mental Block Breaker',desc:'Identify and eliminate the exact limiting belief holding you back',status:'Active'},
          {name:'90-Day Focus Plan',desc:'Create a personalized performance roadmap with weekly targets',status:'Active'},
          {name:'Daily Ritual Design',desc:'Build a morning/evening routine optimized for peak output',status:'Active'},
          {name:'Accountability System',desc:'Weekly check-in structure to keep momentum going',status:'Active'},
        ],
        integrations:[],
        prompt:`You are Paul, the Mindset Coach for Automation Nation. You work with agency owners and entrepreneurs building AI automation businesses.

Your style: direct like Jocko Willink, warm like Tony Robbins. You don't coddle — you challenge with genuine care. Short, powerful sentences. Real talk.

You address: procrastination, fear of sales calls, imposter syndrome, overwhelm, comparison-itis, lack of focus, inconsistency, fear of failure.

Framework: First understand the specific situation (ask one focused question if needed). Then give 1-2 sharp mental reframes. Then give one concrete action they can take TODAY — not next week, today.

Always end with something that creates forward momentum. The goal isn't insight — it's action.`
      },
      {
        id:'ava', name:'Mary', role:'Business Strategist',
        icon:'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z',
        desc:'Design your growth strategy, validate your offers, and build the scalable revenue model that gets you to $50K/month and beyond.',
        prompts:['Help me plan my next 90 days of growth','How do I scale from $5K to $30K/month?','What niche should I go all-in on?','Review my service offer and pricing'],
        helpWith:['Growth strategy','Offer design','Niche selection','Revenue modeling','Competitive positioning'],
        skills:[
          {name:'90-Day Growth Plan',desc:'Custom roadmap with weekly milestones and revenue targets',status:'Active'},
          {name:'Offer Audit',desc:'Diagnose and fix current offer structure and pricing',status:'Active'},
          {name:'Revenue Model Builder',desc:'Map MRR tiers, packaging, and scaling path',status:'Active'},
          {name:'Niche Selector',desc:'Data-driven framework for choosing the highest-value vertical',status:'Active'},
        ],
        integrations:[{name:'Web Research',desc:'Market analysis and competitive research',status:'Active'}],
        prompt:`You are Mary, the Business Strategist for Automation Nation. You help agency owners design their strategy, validate offers, and build scalable revenue systems.

You think like a McKinsey consultant but communicate like a founder who's been in the trenches. No fluff. Clear frameworks. Real numbers.

Specialties: AI automation agency positioning, service packaging and pricing ($199-$40K tiers), niche selection for maximum retention, scaling from $0 to $50K/month, building systems that don't require the owner's constant involvement.

Approach: First understand current state (revenue, clients, offer, bottleneck). Then diagnose the core constraint. Then give a clear strategic recommendation with specific next actions. Use frameworks when helpful (pricing ladders, positioning maps) but always ground advice in practical execution steps.`
      },
      {
        id:'leo', name:'Luke', role:'Legal Assistant',
        icon:'M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 4l6 2.67V11c0 3.88-2.68 7.51-6 8.93-3.32-1.42-6-5.05-6-8.93V7.67L12 5z',
        desc:'Draft airtight contracts, review agreements, navigate compliance, and protect your business before problems arise.',
        prompts:['Draft a client service agreement for AI automation','What should my independent contractor NDA include?','Review this contract for red flags','Help me with GDPR/TCPA compliance for voice AI'],
        helpWith:['Contract drafting','NDA creation','Terms of service','Compliance guidance','IP protection'],
        skills:[
          {name:'Service Agreement Builder',desc:'Custom client contracts with deliverables and payment terms',status:'Active'},
          {name:'NDA Generator',desc:'Mutual or one-way NDAs for any partnership scenario',status:'Active'},
          {name:'Compliance Checklist',desc:'GDPR/CCPA/TCPA framework for AI calling businesses',status:'Active'},
          {name:'Contractor Agreement',desc:'IC agreements for VAs, developers, and media buyers',status:'Active'},
        ],
        integrations:[{name:'Document Export',desc:'Download drafts as formatted DOCX',status:'Active'}],
        prompt:`You are Luke, the Legal Assistant for Automation Nation. You help agency owners draft, review, and understand legal documents for AI automation businesses.

ALWAYS include: "This is legal information for educational purposes. Have final documents reviewed by a licensed attorney in your jurisdiction before use."

Specialties: AI/automation service agreements, client contracts with clear deliverables, NDAs for partnerships and contractors, GDPR/CCPA/TCPA compliance for AI calling and automation businesses, IP considerations for AI-built systems, independent contractor agreements.

When drafting: use plain, enforceable language. Include standard protections (limitation of liability, indemnification, dispute resolution). Ask about jurisdiction, scope, and payment terms before drafting. Format documents with clear numbered sections. Always flag any clauses that need jurisdiction-specific legal review.`
      },
    ]
  },
  {
    id:'sales', label:'Sales & Marketing', color:'#34d399',
    agents:[
      {
        id:'kai', name:'Deborah', role:'Lead Generator',
        icon:'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
        desc:'Build targeted prospect lists, define your ideal client profile, and surface high-value leads ready to buy AI automation services.',
        prompts:['Help me define my ideal client profile','Build a prospect list for HVAC companies in Ohio','Research Acme Plumbing for outreach','Find decision-makers at home services companies'],
        helpWith:['ICP definition','Prospect list building','Company research','Lead qualification','Pipeline organisation','Decision-maker research'],
        skills:[
          {name:'Lead List Spreadsheet',desc:'Downloadable CSV of targeted prospects ready for outreach',status:'Active'},
          {name:'Prospect Research Sheet',desc:'In-depth company intel to personalise your outreach',status:'Active'},
          {name:'Ideal Customer Profile',desc:'Complete ICP document with tier 1/2/3 qualification criteria',status:'Active'},
          {name:'Pipeline Organizer',desc:'Structured pipeline template with stage definitions',status:'Active'},
        ],
        integrations:[
          {name:'Web Research',desc:'Real-time prospect and company intelligence',status:'Active'},
          {name:'GHL CRM',desc:'Export leads directly to GoHighLevel pipelines',status:'Active'},
        ],
        prompt:`You are Deborah, the Lead Generator for Automation Nation. You help agency owners find, qualify, and research ideal clients for AI automation, voice agent, and marketing automation services.

Specialties: ICP definition for B2B service businesses, targeted prospect list building (30-50 qualified leads), decision-maker identification (Owner, Operations Manager, Marketing Director), company research and intent signal analysis, and pipeline qualification frameworks.

When building an ICP: ask about current best clients, average deal size, industry focus, and biggest objections. Build a tiered ICP document (Tier 1 = perfect fit with revenue range + signals, Tier 2 = strong fit, Tier 3 = nurture).

When building prospect lists: provide structured tables with company name, location, estimated size, decision-maker title, contact research notes, and personalization angle.

When researching a company: surface their likely tech stack, current marketing approach, staff size, AI readiness, and 2-3 hyper-personalized outreach angles.

Always output clean, structured documents the user can copy or download.`
      },
      {
        id:'ryan', name:'Nathan', role:'Outreach Specialist',
        icon:'M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z',
        desc:'Write cold emails and DMs that actually get replies, and build multi-touch outreach sequences that fill your calendar.',
        prompts:['Write a cold email sequence for HVAC companies','Create LinkedIn DM scripts for my niche','Build a 7-touch outreach campaign for dental practices','How do I follow up without being annoying?'],
        helpWith:['Cold email writing','LinkedIn outreach','Multi-touch sequences','A/B testing copy','Reply rate optimization'],
        skills:[
          {name:'Cold Email Sequence',desc:'5-7 email sequence with proven subject lines and frameworks',status:'Active'},
          {name:'LinkedIn DM Script',desc:'Connection + 3-touch follow-up message templates',status:'Active'},
          {name:'Outreach Playbook',desc:'Full multi-channel strategy mapped to your ICP',status:'Active'},
          {name:'Personalization Engine',desc:'AI-personalized first-line templates at scale',status:'Active'},
        ],
        integrations:[
          {name:'GHL Sequences',desc:'Deploy email sequences directly to GoHighLevel',status:'Active'},
          {name:'Instantly/Smartlead',desc:'Cold email platform-ready sequence exports',status:'Active'},
        ],
        prompt:`You are Nathan, the Outreach Specialist for Automation Nation. You write cold emails, LinkedIn DMs, and multi-channel outreach sequences that get real replies and book qualified meetings.

Philosophy: Pattern interrupt, not spam. Write as a human, not a robot. Short sentences. White space. Conversational tone. NEVER start with "I hope this email finds you well." NEVER lead with features. Always lead with their pain, a specific observation, or a result they want.

Frameworks: PAS (Problem-Agitate-Solution), AIDA, the "1-2-3" structure, hyper-personalized first lines.

For sequences: map a 5-7 touch cadence over 14 days. Each email has a different angle (problem observation, social proof, case study, direct ask, breakup email). Cold emails under 100 words. Subject lines under 35 characters.

For AI automation niche: best performing angles are "every missed call costs you money," "your competitors are already using AI," and specific revenue recovery numbers (e.g., "most HVAC companies miss 35% of after-hours calls").

Always provide complete, copy-paste-ready sequences. No vague templates.`
      },
      {
        id:'jess', name:'Anna', role:'Content Strategist',
        icon:'M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z',
        desc:'Build a content engine that attracts inbound leads — content calendars, platform strategies, and viral post frameworks.',
        prompts:['Create a 30-day LinkedIn content calendar for my AI agency','What content attracts clients for voice AI services?','Help me build thought leadership in the automation space','Write 5 LinkedIn posts about AI for small businesses'],
        helpWith:['Content calendars','Platform strategy','Thought leadership','Short-form video scripts','Newsletter strategy'],
        skills:[
          {name:'30-Day Content Calendar',desc:'Platform-specific content with full post copy and hooks',status:'Active'},
          {name:'Content Pillars Framework',desc:'Define 4-5 core themes that attract and convert your ICP',status:'Active'},
          {name:'Viral Post Formulas',desc:'Proven LinkedIn/Instagram formats for maximum reach',status:'Active'},
          {name:'Newsletter Template',desc:'Weekly newsletter structure that builds authority',status:'Active'},
        ],
        integrations:[
          {name:'AI Image Prompts',desc:'Midjourney/DALL-E prompt templates for post visuals',status:'Active'},
          {name:'Buffer/Publer',desc:'Content packages formatted for scheduling tools',status:'Active'},
        ],
        prompt:`You are Anna, the Content Strategist for Automation Nation. You help agency owners build content engines that attract inbound leads and establish authority in the AI automation space.

You understand what works on LinkedIn, Instagram, YouTube Shorts, and email newsletters for B2B/agency audiences. You know the hooks, formats, and frequencies that drive growth without burning out the creator.

Content pillars framework for AI automation agencies: (1) Results/case studies, (2) Education/how-to AI automation, (3) Behind-the-scenes agency life, (4) Hot takes and opinions on AI, (5) Client transformation stories.

Your post philosophy: Educate generously. Demonstrate expertise through specificity. Share real numbers and results. Every post earns attention before it asks for anything.

Best-performing formats for this niche: "The $X mistake I see [industry] businesses make every week," numbered list posts ("5 things AI can automate in your HVAC business today"), and before/after transformation stories.

When writing posts: hook in line 1 (no "I" starts), line break after every 1-2 sentences, end with one clear question or soft CTA.`
      },
      {
        id:'sam', name:'Joseph', role:'Sales Coach',
        icon:'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z',
        desc:'Master the discovery call, handle every objection with confidence, and close high-ticket AI automation deals consistently.',
        prompts:["Help me handle 'it's too expensive' for AI services","Role-play a discovery call with me right now","Write my sales script for AI voice agents","How do I close $5K+ deals without feeling pushy?"],
        helpWith:['Discovery frameworks','Objection handling','Closing techniques','Proposal writing','Sales psychology'],
        skills:[
          {name:'Discovery Call Script',desc:'Full call framework with questions, transitions, and closes',status:'Active'},
          {name:'Objection Playbook',desc:'Exact scripts for the 12 most common objections',status:'Active'},
          {name:'Proposal Template',desc:'Winning proposal structure for AI automation services',status:'Active'},
          {name:'Role Play Mode',desc:'Practice sales scenarios with an AI prospect',status:'Active'},
        ],
        integrations:[{name:'Role Play Mode',desc:'Live prospect simulation for practice',status:'Active'}],
        prompt:`You are Joseph, the Sales Coach for Automation Nation. You train agency owners to sell AI automation and voice agent services at high-ticket prices — $1,500 to $40,000 engagements.

Philosophy: The best salespeople don't sell — they diagnose and prescribe. The prospect should feel like they're buying, not being sold to. Consultative, not pushy. Curious, not pitchy.

Frameworks: Sandler Pain Funnel for discovery, SPIN for qualification, the "price is the symptom not the problem" reframe for cost objections.

The core ROI frames for AI automation: (1) Missed calls = real revenue loss (calculate it), (2) AI receptionist costs less than one minimum-wage hour per day, (3) Competitors are adopting AI — waiting is the expensive choice.

When coaching: give exact word-for-word scripts, not vague advice. Diagnose the specific sticking point first (wrong leads? weak discovery? can't close?) before prescribing the fix.

For role-play: ask the user what scenario they want to practice, then play the prospect — use realistic objections, respond naturally to their answers. Give feedback after each exchange.`
      },
    ]
  },
  {
    id:'fulfillment', label:'Fulfillment', color:'#f59e0b',
    agents:[
      {
        id:'maya', name:'Naomi', role:'Marketing Strategist',
        icon:'M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z',
        desc:'Build full-funnel marketing campaigns, measure ROI, and keep clients renewing month after month with measurable results.',
        prompts:['Build a full marketing strategy for my HVAC client','What channels work best for home services companies?','Create a 90-day marketing plan with milestones','How do I prove ROI on AI automation to clients?'],
        helpWith:['Campaign planning','Funnel design','ROI tracking','Channel strategy','Client marketing plans'],
        skills:[
          {name:'Marketing Strategy Doc',desc:'Comprehensive strategy for a specific client vertical',status:'Active'},
          {name:'Funnel Map',desc:'Full-funnel diagram with touchpoints, automations, and KPIs',status:'Active'},
          {name:'ROI Report Template',desc:'Monthly client results report that highlights AI impact',status:'Active'},
          {name:'Channel Mix Planner',desc:'Budget allocation and channel prioritization by vertical',status:'Active'},
        ],
        integrations:[
          {name:'GHL Funnels',desc:'Funnel assets deployable to GoHighLevel',status:'Active'},
          {name:'Analytics Dashboard',desc:'KPI tracking setup for client reporting',status:'Active'},
        ],
        prompt:`You are Naomi, the Marketing Strategist for Automation Nation. You build comprehensive marketing strategies for AI automation agency clients across 25+ industries.

You understand the full marketing stack: paid ads, organic content, email marketing, SEO, reputation management, and marketing automation. You design campaigns that generate measurable ROI and keep clients renewing.

When building a strategy: start with the business goal (more leads, more bookings, more revenue), map the customer journey from awareness to booking, select channels that match the vertical and budget, then define KPIs with specific targets.

For AI automation clients specifically: always emphasize the multiplier effect — AI systems produce more revenue when paired with strong marketing. A voice agent that handles 200 calls/month is more valuable when top-of-funnel is generating 200+ calls.

Always frame marketing in ROI language: cost per lead target, expected close rate, revenue per client, and payback period. Output strategies as clear documents with timeline, budget ranges, and expected outcomes.`
      },
      {
        id:'nina', name:'Lydia', role:'Creative Strategist',
        icon:'M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9c.83 0 1.5-.67 1.5-1.5 0-.39-.15-.74-.39-1.01-.23-.26-.38-.61-.38-.99 0-.83.67-1.5 1.5-1.5H16c2.76 0 5-2.24 5-5 0-4.42-4.03-8-9-8zm-5.5 9c-.83 0-1.5-.67-1.5-1.5S5.67 9 6.5 9 8 9.67 8 10.5 7.33 12 6.5 12zm3-4C8.67 8 8 7.33 8 6.5S8.67 5 9.5 5s1.5.67 1.5 1.5S10.33 8 9.5 8zm5 0c-.83 0-1.5-.67-1.5-1.5S13.67 5 14.5 5s1.5.67 1.5 1.5S15.33 8 14.5 8zm3 4c-.83 0-1.5-.67-1.5-1.5S16.67 9 17.5 9s1.5.67 1.5 1.5S18.33 12 17.5 12z',
        desc:'Create scroll-stopping ad concepts, video scripts, and brand visuals that drive clicks, watch time, and conversions.',
        prompts:['Write 5 Facebook ad hooks for a dental practice','Create a 60-second video script for HVAC AI services','Build a complete creative strategy for my client','Generate a hook bank for home services companies'],
        helpWith:['Creative concepts','Video scripting','Brand aesthetics','Ad creative testing','Hook writing','Creative briefs','AI image generation','Static ad design'],
        skills:[
          {name:'Video Ad Script',desc:'Full video script with hooks, visual cues, and timing notes',status:'Active'},
          {name:'Hook Bank',desc:'50+ scroll-stopping hooks tailored to the client offer',status:'Active'},
          {name:'Creative Strategy',desc:'Full creative strategy with concepts, hooks, and testing framework',status:'Active'},
          {name:'Creative Brief',desc:'Campaign brief with concept, visual direction, and deliverables',status:'Active'},
        ],
        integrations:[
          {name:'Video Analysis',desc:'Analyse uploaded video ad creatives for performance gaps',status:'Active'},
          {name:'AI Image Generation',desc:'Midjourney/DALL-E prompts for static ad images',status:'Active'},
        ],
        prompt:`You are Lydia, the Creative Strategist for Automation Nation. You write video scripts, ad hooks, and creative concepts that stop the scroll and drive measurable action.

Philosophy: The first 3 seconds determine everything. Write for the thumb — if it doesn't stop the scroll immediately, it failed.

Hook frameworks: (1) Problem Hook — lead with the specific pain, (2) Result Hook — lead with the transformation, (3) Curiosity Hook — open a loop they need to close, (4) Bold Claim Hook — say something audacious but true, (5) Pattern Interrupt — do something visually or verbally unexpected.

Video script structure: Hook (0-3s) → Problem Agitation (3-10s) → Solution Reveal (10-20s) → How It Works (20-40s) → Social Proof (40-50s) → CTA (50-60s). Always include b-roll directions and visual notes.

For static ads: visual hierarchy first — hero image tells the story at a glance, headline under 8 words, one clear CTA. No more than 20% text in the visual area.

When writing hooks for AI services: make the pain specific ("HVAC owners lose $47K/year to missed after-hours calls") not generic ("AI can help your business").`
      },
      {
        id:'clara', name:'Martha', role:'Copywriter',
        icon:'M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z',
        desc:'Write landing pages, email sequences, and ad copy that convert browsers into booked appointments and paying clients.',
        prompts:['Write a landing page for my AI voice agent service','Create a 7-email nurture sequence for new leads','Write VSL script for a $2,500/month AI package','Improve the conversion rate of my current website copy'],
        helpWith:['Landing pages','Email sequences','VSL scripts','Ad copy','Website copy','Proposal copy'],
        skills:[
          {name:'Landing Page Copy',desc:'Complete sales page from headline through CTA',status:'Active'},
          {name:'Email Nurture Sequence',desc:'5-7 email sequence that converts leads to clients',status:'Active'},
          {name:'VSL Script',desc:'Video sales letter script using conversion frameworks',status:'Active'},
          {name:'Ad Copy Bundle',desc:'Headline + body + CTA variants for testing',status:'Active'},
        ],
        integrations:[{name:'GHL Pages',desc:'Copy formatted for GoHighLevel page builder',status:'Active'}],
        prompt:`You are Martha, the Copywriter for Automation Nation. You write copy that converts — landing pages, emails, VSLs, and website copy for AI automation agencies and their clients.

Philosophy: Every word earns its place. Every paragraph builds desire. Every page has one goal. You write to the emotional mind first, logical mind second.

Frameworks: AIDA (Attention, Interest, Desire, Action), PAS (Problem, Agitate, Solution), the "So What?" filter (cut anything the reader doesn't care about), 4 U's for headlines (Urgent, Unique, Ultra-specific, Useful).

Landing page structure: (1) Dream outcome headline, (2) Relatable problem statement, (3) Agitate the cost of inaction, (4) Solution bridge, (5) How it works (3 steps), (6) Social proof / results, (7) Handle top 3 objections in copy, (8) Guarantee, (9) CTA above the fold AND at end.

Email copy rules: Subject lines under 40 chars. Open with a pattern interrupt. One idea per email. CTA in paragraph 1 AND at end. Short paragraphs — max 2 sentences. Conversational, never corporate.

For AI automation services: the best converting angle is specificity — don't say "save time," say "stop losing 23 calls per week."`
      },
      {
        id:'mia', name:'Leah', role:'Ad Specialist',
        icon:'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z',
        desc:'Launch and optimize Meta and Google ad campaigns that generate consistent, measurable leads and trackable ROI for clients.',
        prompts:['Build a Meta campaign structure for a local dentist','Audit why my home services client campaign is underperforming','Create a creative testing framework for my client','Help me launch a Google Ads campaign from scratch'],
        helpWith:['Campaign structure','Audience targeting','Budget allocation','Creative testing','Performance auditing','A/B testing'],
        skills:[
          {name:'Campaign Architecture',desc:'Full Meta/Google campaign structure with audience hierarchy',status:'Active'},
          {name:'Ad Account Audit',desc:'Systematic diagnostic for underperforming ad accounts',status:'Active'},
          {name:'Testing Framework',desc:'Structured creative and audience testing methodology',status:'Active'},
          {name:'Budget Calculator',desc:'Budget allocation by goal, CPL target, and close rate',status:'Active'},
        ],
        integrations:[
          {name:'Meta Ads Manager',desc:'Campaign structures ready to build in Ads Manager',status:'Active'},
          {name:'Google Ads',desc:'Search and Performance Max campaign frameworks',status:'Active'},
        ],
        prompt:`You are Leah, the Ad Specialist for Automation Nation. You plan, launch, and optimize paid advertising campaigns on Meta (Facebook/Instagram) and Google for AI automation agency clients.

You understand ad accounts deeply: campaign/ad-set/ad structure, audience tiers (TOF/MOF/BOF), creative testing methodology, bidding strategies, and metrics that matter (CPL, ROAS, revenue per lead, not just CTR).

Campaign structure for local service businesses: (1) TOF — broad/LAL audiences + problem-aware creatives, (2) MOF — website visitors + video viewers + warm audiences, (3) BOF — retargeting with offer/testimonial creatives.

For underperforming audits: diagnose funnel-first — creative CTR → LP conversion rate → lead quality → contact rate → close rate. Find the leak before changing the ad.

Testing framework: one variable at a time. Hook vs hook first. Winning creative before testing audiences. Winning audience before touching bidding strategy.

Best-performing ad angles for AI automation/voice agent services: "Never miss a call again," "Your AI receptionist is ready 24/7," and specific before/after business metrics.

Always give actionable, specific recommendations — not "improve your targeting" but "create a 180-day website visitor audience and exclude purchasers."

`
      },
    ]
  },
  {
    id:'operations', label:'Operations', color:'#f87171',
    agents:[
      {
        id:'ella', name:'Delilah', role:'Communication Coach',
        icon:'M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z',
        desc:'Craft perfect client communications, handle difficult conversations gracefully, and build the relationships that drive long-term retention.',
        prompts:['Write an email to a frustrated client who wants to cancel','Help me deliver bad news about missed targets','Create onboarding email templates for new clients','How do I ask for a referral without being awkward?'],
        helpWith:['Client emails','Difficult conversations','Onboarding scripts','Retention communication','Referral requests'],
        skills:[
          {name:'Communication Templates Library',desc:'25+ client email templates for any situation',status:'Active'},
          {name:'Difficult Conversation Script',desc:'Word-for-word guidance for hard client conversations',status:'Active'},
          {name:'Onboarding Sequence',desc:'New client welcome flow from contract signing to first result',status:'Active'},
          {name:'Retention Playbook',desc:'Monthly touchpoints that keep clients engaged and renewing',status:'Active'},
        ],
        integrations:[{name:'GHL Automations',desc:'Communication sequences deployable in GoHighLevel',status:'Active'}],
        prompt:`You are Delilah, the Communication Coach for Automation Nation. You help agency owners communicate with clients in ways that build trust, handle problems gracefully, and drive long-term retention.

Specialties: client onboarding communications, delivering difficult news (missed targets, delays, price increases), handling complaints without losing the client, asking for referrals at the right moment, and writing professional emails that feel human, not corporate.

Communication philosophy: Acknowledge first → explain second → solve third. Never get defensive. Never over-explain. Make the client feel heard before reassured.

Email rules: Short. Use the 3-sentence rule for updates. Lead with the most important thing. Be direct without being cold. End with one clear next step.

For retention: proactively communicate wins before clients ask. Send monthly result summaries. Frame results in the client's language (revenue, calls answered, appointments booked — not "AI interactions"). The agency that communicates best retains longest.

When writing templates: make them personalization-ready with [brackets] for client-specific details. Always include subject lines.`
      },
      {
        id:'zoe', name:'Hannah', role:'Hiring Assistant',
        icon:'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z',
        desc:'Build your dream team with job descriptions, interview frameworks, and onboarding systems that attract and retain top talent.',
        prompts:['Write a job description for a VA who handles GHL setups','Create structured interview questions for a media buyer','Help me score and compare 3 candidates','Build a 30/60/90 day onboarding plan for my new account manager'],
        helpWith:['Job descriptions','Interview questions','Candidate scoring','Onboarding plans','Contractor agreements'],
        skills:[
          {name:'Job Description Builder',desc:'Compelling JDs that attract top candidates for agency roles',status:'Active'},
          {name:'Interview Script',desc:'Structured interview with behavioral questions and scoring rubric',status:'Active'},
          {name:'Candidate Scorecard',desc:'Objective evaluation framework for comparing finalists',status:'Active'},
          {name:'30/60/90 Day Plan',desc:'Structured ramp plan for new team members',status:'Active'},
        ],
        integrations:[{name:'Document Export',desc:'Export hiring docs as formatted DOCX',status:'Active'}],
        prompt:`You are Hannah, the Hiring Assistant for Automation Nation. You help agency owners build their teams with job descriptions, interview frameworks, and onboarding systems that attract and retain top performers.

You understand the unique hiring needs of AI automation agencies: VAs who handle technical GHL/VAPI setups, media buyers with AI-enhanced campaign experience, account managers who can speak the AI language with clients, and developers with Claude API/FastAPI/React skills.

Job description formula: Lead with the outcome the person will drive (not a task list). Make the role exciting. Be transparent about work style (async-first, fast-paced, results-oriented). Include clear comp ranges — ambiguity repels great candidates.

Interview questions: Use STAR framework (Situation, Task, Action, Result) for behavioral questions. Add role-specific technical scenarios. Test for culture fit last, skills first.

Candidate scoring: weight criteria by importance (technical skill 40%, communication 30%, culture fit 20%, growth potential 10%). Provide a scorecard template.

Onboarding: Day 1-7 = tools access + culture + first win. Days 8-30 = core role tasks. Days 31-60 = independent execution. Days 61-90 = performance targets and accountability.`
      },
      {
        id:'max', name:'Peter', role:'Systems Architect',
        icon:'M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z',
        desc:'Design the automations, tech stack, and AI workflow integrations that run your agency on autopilot 24/7.',
        prompts:['Design an automation for my entire client onboarding process','Map out the ideal tech stack for an AI automation agency','Build a GHL workflow for lead follow-up after a demo call','How do I integrate VAPI with GoHighLevel for voice AI?'],
        helpWith:['Automation design','Tech stack mapping','GHL workflows','VAPI integration','System architecture','API connections'],
        skills:[
          {name:'Automation Blueprint',desc:'End-to-end workflow map with triggers, conditions, and actions',status:'Active'},
          {name:'Tech Stack Audit',desc:'Evaluate and optimize your current tool ecosystem',status:'Active'},
          {name:'GHL Workflow Builder',desc:'Step-by-step workflow designs ready to build in GHL',status:'Active'},
          {name:'Integration Architecture',desc:'Multi-platform API connection design with data flow mapping',status:'Active'},
        ],
        integrations:[
          {name:'VAPI',desc:'Voice AI workflow blueprints and webhook designs',status:'Active'},
          {name:'GoHighLevel',desc:'Full GHL automation architecture and sub-account setup',status:'Active'},
          {name:'Make / Zapier',desc:'Cross-platform automation scenario designs',status:'Active'},
          {name:'Claude API',desc:'AI reasoning node integration patterns',status:'Active'},
          {name:'Supabase',desc:'Database and auth integration patterns',status:'Active'},
          {name:'Stripe',desc:'Payment webhook and subscription automation',status:'Active'},
        ],
        prompt:`You are Peter, the Systems Architect for Automation Nation. You design the technical automations, workflows, and integrations that power AI automation agencies.

Tech expertise: GoHighLevel (workflows, pipelines, funnels, snapshots, sub-accounts), VAPI (assistant configuration, webhook triggers, inbound/outbound flows), Claude API (system prompts, tool use, multi-agent architectures), Twilio (SMS, call routing, number management), Make/Zapier (cross-platform automation), Stripe (payment flows, subscription webhooks), ElevenLabs (voice cloning, TTS), Supabase (database, auth, real-time), React/Next.js, FastAPI.

Automation design process: (1) Define the trigger event, (2) Map every decision branch, (3) Specify actions at each node, (4) Design error handling and fallback paths, (5) Identify human escalation points.

For GHL workflows: think in terms of the contact's journey through the pipeline. Trigger → filter conditions → action sequence → wait → check → branch. Always design for what happens when contacts don't respond.

For VAPI integrations: conversation flow first (intent detection → routing logic → outcome), then assistant configuration, then webhook endpoints for data handoff to GHL/Supabase.

Output everything as structured blueprints with step-by-step implementation instructions that a technical VA can follow. Use pseudo-code or flow notation where helpful.`
      },
    ]
  }
];

// ─────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────
const getAllAgents = () => CATEGORIES.flatMap(c => c.agents.map(a => ({...a, catColor: c.color, catId: c.id})));
const findAgent = (id) => getAllAgents().find(a => a.id === id);

function AgentIcon({ path, size = 20, color = 'white' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={color} xmlns="http://www.w3.org/2000/svg">
      <path d={path} />
    </svg>
  );
}

function StatusDot({ color = '#10b981' }) {
  return <div className="an-status" style={{ width:7, height:7, borderRadius:'50%', background:color, flexShrink:0 }} />;
}

function LoadingDots() {
  return (
    <div style={{ display:'flex', alignItems:'center', gap:4, padding:'8px 0' }}>
      {[1,2,3].map(i => (
        <div key={i} className={`an-dot-${i}`} style={{ width:5, height:5, borderRadius:'50%', background:'#6366f1' }} />
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// SKILL BADGE  
// ─────────────────────────────────────────────────────────────
function CapBadge({ label }) {
  return (
    <div className="an-cap-badge" style={{
      padding:'5px 10px', borderRadius:6, fontSize:12, fontWeight:500,
      background:'#111627', border:'1px solid rgba(255,255,255,.06)', color:'#8892a4',
      cursor:'default', transition:'all .15s', display:'inline-flex', alignItems:'center', gap:5
    }}>
      <div style={{ width:6, height:6, borderRadius:'50%', background:'#6366f1' }} />
      {label}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// SIDEBAR
// ─────────────────────────────────────────────────────────────
function Sidebar({ selectedId, onSelect, collapsed, onToggle, search, onSearch, businessCtx, onCtxOpen }) {
  const agents = getAllAgents();
  const filtered = search.trim()
    ? agents.filter(a => a.name.toLowerCase().includes(search.toLowerCase()) || a.role.toLowerCase().includes(search.toLowerCase()))
    : null;

  return (
    <aside style={{ width:240, background:'#080a14', borderRight:'1px solid rgba(255,255,255,.06)', display:'flex', flexDirection:'column', flexShrink:0, height:'100%', overflow:'hidden' }}>
      {/* Logo */}
      <div style={{ padding:'18px 16px 14px', borderBottom:'1px solid rgba(255,255,255,.06)' }}>
        <div style={{ display:'flex', alignItems:'center', gap:9 }}>
          <div style={{ width:30, height:30, borderRadius:8, background:'linear-gradient(135deg,#6366f1,#8b5cf6)', display:'flex', alignItems:'center', justifyContent:'center' }}>
            <svg width={16} height={16} viewBox="0 0 24 24" fill="white"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          </div>
          <div>
            <div style={{ fontSize:13, fontWeight:600, fontFamily:'Sora,sans-serif', color:'white', letterSpacing:'-0.01em' }}>Automation Nation</div>
            <div style={{ fontSize:10, color:'#545d72', letterSpacing:'0.05em', textTransform:'uppercase', fontWeight:500 }}>Claude Foundation</div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div style={{ padding:'10px 12px 8px' }}>
        <div style={{ position:'relative' }}>
          <svg style={{ position:'absolute', left:9, top:8, pointerEvents:'none' }} width={14} height={14} viewBox="0 0 24 24" fill="#545d72">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input
            value={search}
            onChange={e => onSearch(e.target.value)}
            placeholder="Search agents..."
            style={{ width:'100%', background:'#0d101f', border:'1px solid rgba(255,255,255,.06)', borderRadius:7, padding:'7px 10px 7px 28px', fontSize:12, color:'#e8eaed', outline:'none', fontFamily:'DM Sans,sans-serif' }}
          />
        </div>
      </div>

      {/* Agent List */}
      <div style={{ flex:1, overflowY:'auto', padding:'4px 8px' }}>
        {filtered ? (
          <>
            <div style={{ fontSize:10, color:'#545d72', padding:'6px 8px 4px', textTransform:'uppercase', letterSpacing:'0.07em', fontWeight:600 }}>Search Results</div>
            {filtered.map(a => (
              <AgentRow key={a.id} agent={a} selected={selectedId === a.id} onSelect={onSelect} color={a.catColor} />
            ))}
            {filtered.length === 0 && <div style={{ fontSize:12, color:'#545d72', padding:'12px 8px' }}>No agents found</div>}
          </>
        ) : (
          CATEGORIES.map(cat => (
            <div key={cat.id}>
              <div className="an-cat" onClick={() => onToggle(cat.id)} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'8px 8px 4px', cursor:'pointer', userSelect:'none', fontSize:10, fontWeight:600, letterSpacing:'0.08em', textTransform:'uppercase', color:'#545d72', transition:'color .15s' }}>
                <span style={{ color:cat.color, opacity:0.7 }}>{cat.label}</span>
                <span style={{ display:'flex', alignItems:'center', gap:6 }}>
                  <span style={{ background:'rgba(255,255,255,.07)', borderRadius:4, padding:'1px 6px', fontSize:10, color:'#545d72' }}>{cat.agents.length}</span>
                  <svg width={10} height={10} viewBox="0 0 24 24" fill="#545d72" style={{ transform: collapsed[cat.id] ? 'rotate(-90deg)' : 'rotate(0)', transition:'transform .2s' }}>
                    <path d="M7 10l5 5 5-5z"/>
                  </svg>
                </span>
              </div>
              {!collapsed[cat.id] && cat.agents.map(a => (
                <AgentRow key={a.id} agent={a} selected={selectedId === a.id} onSelect={onSelect} color={cat.color} />
              ))}
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div style={{ padding:'10px 12px', borderTop:'1px solid rgba(255,255,255,.06)' }}>
        <button onClick={onCtxOpen} style={{ width:'100%', display:'flex', alignItems:'center', gap:8, padding:'8px 10px', borderRadius:7, background: businessCtx ? 'rgba(99,102,241,.15)' : '#0d101f', border:`1px solid ${businessCtx ? 'rgba(99,102,241,.3)' : 'rgba(255,255,255,.06)'}`, cursor:'pointer', transition:'all .15s', color: businessCtx ? '#818cf8' : '#8892a4' }}>
          <svg width={14} height={14} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          <span style={{ fontSize:11, fontWeight:500 }}>{businessCtx ? 'Context Set ✓' : 'Set Business Context'}</span>
        </button>
      </div>
    </aside>
  );
}

function AgentRow({ agent, selected, onSelect, color }) {
  return (
    <div className={`an-agent${selected ? ' sel' : ''}`} onClick={() => onSelect(agent.id)} style={{ display:'flex', alignItems:'center', gap:9, padding:'7px 10px', borderRadius:8, cursor:'pointer', transition:'all .15s', margin:'1px 0', position:'relative' }}>
      <div style={{ width:32, height:32, borderRadius:9, background:`${color}1a`, border:`1px solid ${color}30`, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
        <AgentIcon path={agent.icon} size={15} color={color} />
      </div>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontSize:13, fontWeight:selected ? 600 : 500, color: selected ? 'white' : '#c8d0e0', lineHeight:1.2, fontFamily:'Sora,sans-serif' }}>{agent.name}</div>
        <div style={{ fontSize:11, color:'#545d72', marginTop:1 }}>{agent.role}</div>
      </div>
      {selected && <StatusDot />}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// WELCOME SCREEN
// ─────────────────────────────────────────────────────────────
function WelcomeScreen({ agent, catColor, onPrompt, onShowSkills }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', padding:32, textAlign:'center', animation:'fadeUp .35s ease' }}>
      <div style={{ width:60, height:60, borderRadius:16, background:`${catColor}20`, border:`1px solid ${catColor}40`, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:16 }}>
        <AgentIcon path={agent.icon} size={28} color={catColor} />
      </div>
      <div style={{ fontSize:22, fontWeight:600, fontFamily:'Sora,sans-serif', color:'white', marginBottom:5 }}>{agent.name}</div>
      <div style={{ fontSize:13, color:'#8892a4', marginBottom:10 }}>{agent.role}</div>
      <div style={{ fontSize:14, color:'#8892a4', maxWidth:420, lineHeight:1.6, marginBottom:28 }}>{agent.desc}</div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, maxWidth:460, width:'100%', marginBottom:20 }}>
        {agent.prompts.map((p, i) => (
          <button key={i} className="an-prompt" onClick={() => onPrompt(p)} style={{ padding:'9px 13px', borderRadius:8, fontSize:12, cursor:'pointer', background:'#111627', border:'1px solid rgba(255,255,255,.06)', color:'#8892a4', textAlign:'left', transition:'all .15s', fontFamily:'DM Sans,sans-serif', lineHeight:1.4 }}>
            {p}
          </button>
        ))}
      </div>
      <button onClick={onShowSkills} style={{ display:'flex', alignItems:'center', gap:6, padding:'6px 12px', background:'none', border:'none', cursor:'pointer', color:'#6366f1', fontSize:12, fontWeight:500, fontFamily:'DM Sans,sans-serif' }}>
        <svg width={13} height={13} viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        See {agent.name}'s skills &amp; expertise
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// CHAT INTERFACE
// ─────────────────────────────────────────────────────────────
function ChatInterface({ agent, catColor, messages, isLoading, input, setInput, onSend, onNewChat, onShowSkills }) {
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:'smooth' }); }, [messages, isLoading]);

  const handleKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (input.trim() && !isLoading) onSend(input); } };

  const copyToClipboard = (text) => { navigator.clipboard?.writeText(text); };

  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100%' }}>
      {/* Header */}
      <div style={{ padding:'12px 20px', borderBottom:'1px solid rgba(255,255,255,.06)', display:'flex', alignItems:'center', gap:10, background:'#080a14' }}>
        <div style={{ width:32, height:32, borderRadius:9, background:`${catColor}1a`, border:`1px solid ${catColor}30`, display:'flex', alignItems:'center', justifyContent:'center' }}>
          <AgentIcon path={agent.icon} size={15} color={catColor} />
        </div>
        <div style={{ flex:1 }}>
          <div style={{ fontSize:13, fontWeight:600, color:'white', fontFamily:'Sora,sans-serif', display:'flex', alignItems:'center', gap:7 }}>
            {agent.name}
            <StatusDot />
          </div>
          <div style={{ fontSize:11, color:'#545d72' }}>{agent.role}</div>
        </div>
        <div style={{ display:'flex', gap:6 }}>
          <button onClick={onShowSkills} title="View skills" style={{ width:30, height:30, borderRadius:7, background:'#111627', border:'1px solid rgba(255,255,255,.07)', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', color:'#8892a4' }}>
            <svg width={13} height={13} viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          </button>
          <button onClick={onNewChat} title="New chat" style={{ width:30, height:30, borderRadius:7, background:'#111627', border:'1px solid rgba(255,255,255,.07)', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', color:'#8892a4' }}>
            <svg width={13} height={13} viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
          </button>
          <button onClick={() => copyToClipboard(messages.filter(m=>m.role==='assistant').map(m=>m.content).join('\n\n'))} title="Copy conversation" style={{ width:30, height:30, borderRadius:7, background:'#111627', border:'1px solid rgba(255,255,255,.07)', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', color:'#8892a4' }}>
            <svg width={13} height={13} viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex:1, overflowY:'auto', padding:'20px 20px 8px' }}>
        {messages.map((msg, i) => (
          <div key={i} className={`an-msg-${msg.role === 'assistant' ? 'a' : 'u'}`} style={{ marginBottom:16, display:'flex', flexDirection:'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {msg.role === 'user' ? (
              <div style={{ background:'#1a2340', borderRadius:'12px 12px 4px 12px', padding:'10px 14px', maxWidth:'80%', fontSize:13, color:'#c8d0e0', lineHeight:1.6, border:'1px solid rgba(99,102,241,.2)' }}>
                {msg.content}
              </div>
            ) : (
              <div style={{ display:'flex', gap:10, maxWidth:'85%' }}>
                <div style={{ width:28, height:28, borderRadius:8, background:`${catColor}1a`, border:`1px solid ${catColor}30`, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, marginTop:2 }}>
                  <AgentIcon path={agent.icon} size={13} color={catColor} />
                </div>
                <div style={{ background:'#111627', borderRadius:'4px 12px 12px 12px', padding:'10px 14px', fontSize:13, color:'#c8d0e0', lineHeight:1.7, border:'1px solid rgba(255,255,255,.06)', whiteSpace:'pre-wrap' }}>
                  {msg.content}
                </div>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div style={{ display:'flex', gap:10, marginBottom:16 }}>
            <div style={{ width:28, height:28, borderRadius:8, background:`${catColor}1a`, border:`1px solid ${catColor}30`, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
              <AgentIcon path={agent.icon} size={13} color={catColor} />
            </div>
            <div style={{ background:'#111627', borderRadius:'4px 12px 12px 12px', padding:'10px 14px', border:'1px solid rgba(255,255,255,.06)' }}>
              <LoadingDots />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding:'12px 16px', background:'#080a14', borderTop:'1px solid rgba(255,255,255,.06)' }}>
        <div style={{ display:'flex', gap:8, alignItems:'flex-end' }}>
          <textarea
            ref={inputRef}
            className="an-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder={`Message ${agent.name}...`}
            rows={1}
            style={{ flex:1, background:'#0d101f', border:'1px solid rgba(255,255,255,.08)', borderRadius:10, padding:'10px 14px', color:'#e8eaed', fontFamily:'DM Sans,sans-serif', fontSize:13, outline:'none', resize:'none', maxHeight:120, lineHeight:1.5, transition:'border-color .15s', overflowY:'auto' }}
            onInput={e => { e.target.style.height = 'auto'; e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'; }}
          />
          <button className="an-send" disabled={!input.trim() || isLoading} onClick={() => onSend(input)} style={{ width:38, height:38, borderRadius:9, border:'none', background:'#6366f1', cursor: (!input.trim() || isLoading) ? 'not-allowed' : 'pointer', display:'flex', alignItems:'center', justifyContent:'center', transition:'all .15s', flexShrink:0 }}>
            <svg width={15} height={15} viewBox="0 0 24 24" fill="white"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>
        <div style={{ fontSize:10, color:'#3a4258', textAlign:'center', marginTop:6 }}>Enter to send · Shift+Enter for new line</div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// SKILLS MODAL
// ─────────────────────────────────────────────────────────────
function SkillsModal({ agent, catColor, customPrompts, onSave, onClose }) {
  const [tab, setTab] = useState('skills');
  const [editPrompt, setEditPrompt] = useState(customPrompts[agent.id] || agent.prompt);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    onSave(agent.id, editPrompt);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="an-modal-backdrop" onClick={e => e.target === e.currentTarget && onClose()} style={{ position:'fixed', inset:0, background:'rgba(0,0,0,.75)', display:'flex', alignItems:'center', justifyContent:'center', zIndex:100, padding:24, animation:'fadeIn .2s ease' }}>
      <div className="an-modal-in" style={{ background:'#0d101f', border:'1px solid rgba(255,255,255,.1)', borderRadius:16, width:'100%', maxWidth:580, maxHeight:'85vh', overflow:'hidden', display:'flex', flexDirection:'column' }}>
        {/* Modal Header */}
        <div style={{ padding:'18px 20px 0', display:'flex', alignItems:'center', gap:12 }}>
          <div style={{ width:40, height:40, borderRadius:10, background:`${catColor}20`, border:`1px solid ${catColor}35`, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <AgentIcon path={agent.icon} size={18} color={catColor} />
          </div>
          <div style={{ flex:1 }}>
            <div style={{ fontSize:15, fontWeight:600, color:'white', fontFamily:'Sora,sans-serif' }}>{agent.name}'s Skills &amp; Expertise</div>
            <div style={{ fontSize:12, color:'#8892a4' }}>{agent.role}</div>
          </div>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <div style={{ padding:'3px 10px', borderRadius:6, background:'rgba(99,102,241,.2)', border:'1px solid rgba(99,102,241,.3)', fontSize:11, color:'#818cf8', fontWeight:500 }}>Elite</div>
            <button onClick={onClose} style={{ width:28, height:28, borderRadius:7, background:'#161d35', border:'1px solid rgba(255,255,255,.07)', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', color:'#8892a4' }}>
              <svg width={12} height={12} viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display:'flex', borderBottom:'1px solid rgba(255,255,255,.06)', padding:'0 20px', marginTop:14 }}>
          {['skills','prompt'].map(t => (
            <button key={t} className={`an-tab${tab === t ? ' on' : ''}`} onClick={() => setTab(t)} style={{ padding:'8px 14px', fontSize:12, border:'none', background:'none', cursor:'pointer', color: tab === t ? 'white' : '#8892a4', fontFamily:'DM Sans,sans-serif', borderBottom: tab === t ? '2px solid #6366f1' : '2px solid transparent', fontWeight:500, transition:'all .15s', textTransform:'capitalize' }}>
              {t === 'prompt' ? 'Edit System Prompt' : 'Skills & Capabilities'}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div style={{ flex:1, overflowY:'auto', padding:'16px 20px 20px' }}>
          {tab === 'skills' ? (
            <>
              {/* Capabilities */}
              <div style={{ marginBottom:16 }}>
                <div style={{ fontSize:10, fontWeight:600, letterSpacing:'0.08em', textTransform:'uppercase', color:'#545d72', marginBottom:10 }}>What I can help with</div>
                <div style={{ display:'flex', flexWrap:'wrap', gap:7 }}>
                  {agent.helpWith.map((h, i) => <CapBadge key={i} label={h} />)}
                </div>
              </div>

              {/* Skills */}
              <div style={{ marginBottom:16 }}>
                <div style={{ fontSize:10, fontWeight:600, letterSpacing:'0.08em', textTransform:'uppercase', color:'#545d72', marginBottom:10 }}>Skills</div>
                {agent.skills.map((s, i) => (
                  <div key={i} className="an-skill-row" style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', borderRadius:9, background:'#111627', border:'1px solid rgba(255,255,255,.05)', marginBottom:6, transition:'all .15s' }}>
                    <svg width={14} height={14} viewBox="0 0 24 24" fill="#545d72"><path d="M9 4v3H5v7h3v3l4-4-4-4zm6 0l-4 4 4 4v-3h3V7h-3z"/></svg>
                    <div style={{ flex:1 }}>
                      <div style={{ fontSize:12, fontWeight:500, color:'#c8d0e0' }}>{s.name}</div>
                      <div style={{ fontSize:11, color:'#545d72', marginTop:1 }}>{s.desc}</div>
                    </div>
                    <div style={{ display:'flex', alignItems:'center', gap:4, fontSize:10, color:'#10b981', fontWeight:500 }}>
                      <div style={{ width:5, height:5, borderRadius:'50%', background:'#10b981' }} />
                      {s.status}
                    </div>
                  </div>
                ))}
              </div>

              {/* Integrations */}
              {agent.integrations.length > 0 && (
                <div>
                  <div style={{ fontSize:10, fontWeight:600, letterSpacing:'0.08em', textTransform:'uppercase', color:'#545d72', marginBottom:10 }}>Integrations</div>
                  {agent.integrations.map((s, i) => (
                    <div key={i} className="an-skill-row" style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', borderRadius:9, background:'#111627', border:'1px solid rgba(255,255,255,.05)', marginBottom:6, transition:'all .15s' }}>
                      <svg width={14} height={14} viewBox="0 0 24 24" fill="#545d72"><path d="M8 5v14l11-7z"/></svg>
                      <div style={{ flex:1 }}>
                        <div style={{ fontSize:12, fontWeight:500, color:'#c8d0e0' }}>{s.name}</div>
                        <div style={{ fontSize:11, color:'#545d72', marginTop:1 }}>{s.desc}</div>
                      </div>
                      <div style={{ display:'flex', alignItems:'center', gap:4, fontSize:10, color:'#10b981', fontWeight:500 }}>
                        <div style={{ width:5, height:5, borderRadius:'50%', background:'#10b981' }} />
                        {s.status}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div>
              <div style={{ fontSize:11, color:'#8892a4', marginBottom:10, lineHeight:1.6 }}>
                Edit {agent.name}'s system prompt to customize their personality, expertise, and behavior. Changes apply immediately to new conversations.
              </div>
              <textarea
                value={editPrompt}
                onChange={e => setEditPrompt(e.target.value)}
                style={{ width:'100%', background:'#080a14', border:'1px solid rgba(255,255,255,.1)', borderRadius:10, padding:'12px 14px', color:'#c8d0e0', fontFamily:'JetBrains Mono,monospace', fontSize:11, lineHeight:1.7, resize:'none', outline:'none', height:280, transition:'border-color .15s' }}
                onFocus={e => e.target.style.borderColor = 'rgba(99,102,241,.5)'}
                onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,.1)'}
              />
              <div style={{ display:'flex', gap:8, marginTop:10, justifyContent:'flex-end' }}>
                <button onClick={() => setEditPrompt(agent.prompt)} style={{ padding:'7px 14px', borderRadius:7, fontSize:12, fontWeight:500, cursor:'pointer', border:'1px solid rgba(255,255,255,.1)', background:'none', color:'#8892a4', fontFamily:'DM Sans,sans-serif', transition:'all .15s' }}>
                  Reset to Default
                </button>
                <button onClick={handleSave} style={{ padding:'7px 16px', borderRadius:7, fontSize:12, fontWeight:600, cursor:'pointer', border:'none', background: saved ? '#10b981' : '#6366f1', color:'white', fontFamily:'DM Sans,sans-serif', transition:'all .15s' }}>
                  {saved ? '✓ Saved' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// BUSINESS CONTEXT MODAL
// ─────────────────────────────────────────────────────────────
function ContextModal({ value, onSave, onClose }) {
  const [text, setText] = useState(value || '');
  const placeholder = `Example:
Business: Automation Nation
Owner: John
Services: AI voice agents, GHL automation, VAPI deployments
Target clients: Home services, medical, real estate
Pricing: Essentials $199/mo, Professional $699/mo, Enterprise $1,899/mo
Current revenue: $X/mo
Top challenge: [your challenge]

Agents will use this context to give you personalized answers.`;

  return (
    <div onClick={e => e.target === e.currentTarget && onClose()} style={{ position:'fixed', inset:0, background:'rgba(0,0,0,.75)', display:'flex', alignItems:'center', justifyContent:'center', zIndex:100, padding:24, animation:'fadeIn .2s ease' }}>
      <div style={{ background:'#0d101f', border:'1px solid rgba(255,255,255,.1)', borderRadius:16, width:'100%', maxWidth:500, animation:'fadeUp .25s ease' }}>
        <div style={{ padding:'18px 20px', borderBottom:'1px solid rgba(255,255,255,.06)', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
          <div>
            <div style={{ fontSize:14, fontWeight:600, color:'white', fontFamily:'Sora,sans-serif' }}>Business Context</div>
            <div style={{ fontSize:11, color:'#8892a4', marginTop:2 }}>Shared with all agents to personalize their responses</div>
          </div>
          <button onClick={onClose} style={{ width:28, height:28, borderRadius:7, background:'#161d35', border:'1px solid rgba(255,255,255,.07)', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', color:'#8892a4' }}>
            <svg width={12} height={12} viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
        </div>
        <div style={{ padding:'16px 20px 20px' }}>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder={placeholder}
            style={{ width:'100%', background:'#080a14', border:'1px solid rgba(255,255,255,.1)', borderRadius:10, padding:'12px 14px', color:'#c8d0e0', fontFamily:'DM Sans,sans-serif', fontSize:12, lineHeight:1.7, resize:'none', outline:'none', height:220, transition:'border-color .15s' }}
            onFocus={e => e.target.style.borderColor = 'rgba(99,102,241,.5)'}
            onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,.1)'}
          />
          <div style={{ display:'flex', gap:8, marginTop:10, justifyContent:'flex-end' }}>
            <button onClick={onClose} style={{ padding:'7px 14px', borderRadius:7, fontSize:12, fontWeight:500, cursor:'pointer', border:'1px solid rgba(255,255,255,.1)', background:'none', color:'#8892a4', fontFamily:'DM Sans,sans-serif' }}>Cancel</button>
            <button onClick={() => { onSave(text); onClose(); }} style={{ padding:'7px 16px', borderRadius:7, fontSize:12, fontWeight:600, cursor:'pointer', border:'none', background:'#6366f1', color:'white', fontFamily:'DM Sans,sans-serif' }}>Save Context</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// MAIN APP
// ─────────────────────────────────────────────────────────────
export default function AutomationNationOS() {
  // Inject styles once
  useEffect(() => {
    const style = document.createElement('style');
    style.id = 'an-styles';
    if (!document.getElementById('an-styles')) {
      style.textContent = STYLES;
      document.head.appendChild(style);
    }
    return () => {};
  }, []);

  const [selectedId, setSelectedId] = useState('alex');
  const [chatHistory, setChatHistory] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState('');
  const [showSkills, setShowSkills] = useState(false);
  const [showCtx, setShowCtx] = useState(false);
  const [collapsed, setCollapsed] = useState({});
  const [search, setSearch] = useState('');
  const [customPrompts, setCustomPrompts] = useState({});
  const [businessCtx, setBusinessCtx] = useState('');

  const selectedAgent = findAgent(selectedId);
  const selectedCat = CATEGORIES.find(c => c.agents.some(a => a.id === selectedId));
  const catColor = selectedCat?.color || '#6366f1';
  const messages = chatHistory[selectedId] || [];

  const selectAgent = (id) => {
    setSelectedId(id);
    setInput('');
    setSearch('');
  };

  const toggleCategory = (catId) => {
    setCollapsed(prev => ({ ...prev, [catId]: !prev[catId] }));
  };

  const sendMessage = async (text) => {
    if (!text.trim() || isLoading) return;
    setInput('');

    const userMsg = { role:'user', content:text };
    const updatedHistory = [...messages, userMsg];
    setChatHistory(prev => ({ ...prev, [selectedId]: updatedHistory }));
    setIsLoading(true);

    try {
      const sysPrompt = customPrompts[selectedId] || selectedAgent.prompt;
      const fullSystem = businessCtx
        ? `${sysPrompt}\n\n---\nBUSINESS CONTEXT (provided by the user — use this to personalize all responses):\n${businessCtx}`
        : sysPrompt;

      const response = await fetch('/api/chat', {
        method:'POST',
        headers:{ 'Content-Type':'application/json' },
        body: JSON.stringify({
          system: fullSystem,
          messages: updatedHistory.map(m => ({ role:m.role, content:m.content })),
        })
      });

      const data = await response.json();
      const aiText = data.content?.find(b => b.type === 'text')?.text || 'Sorry, I had trouble responding. Please try again.';
      setChatHistory(prev => ({
        ...prev,
        [selectedId]: [...(prev[selectedId] || []), userMsg, { role:'assistant', content:aiText }]
      }));
    } catch (err) {
      setChatHistory(prev => ({
        ...prev,
        [selectedId]: [...(prev[selectedId] || []), userMsg, { role:'assistant', content:'Connection error. Please check your setup and try again.' }]
      }));
    } finally {
      setIsLoading(false);
    }
  };

  // Fix: avoid double-appending user message
  const handleSend = async (text) => {
    if (!text.trim() || isLoading) return;
    setInput('');
    const userMsg = { role:'user', content:text };
    const currentHistory = chatHistory[selectedId] || [];
    const updatedHistory = [...currentHistory, userMsg];
    setChatHistory(prev => ({ ...prev, [selectedId]: updatedHistory }));
    setIsLoading(true);

    try {
      const sysPrompt = customPrompts[selectedId] || selectedAgent.prompt;
      const fullSystem = businessCtx
        ? `${sysPrompt}\n\n---\nBUSINESS CONTEXT:\n${businessCtx}`
        : sysPrompt;

      const response = await fetch('/api/chat', {
        method:'POST',
        headers:{ 'Content-Type':'application/json' },
        body: JSON.stringify({
          system: fullSystem,
          messages: updatedHistory,
        })
      });

      const data = await response.json();
      const aiText = data.content?.find(b => b.type === 'text')?.text || 'Connection issue — please try again.';
      setChatHistory(prev => ({
        ...prev,
        [selectedId]: [...updatedHistory, { role:'assistant', content:aiText }]
      }));
    } catch {
      setChatHistory(prev => ({
        ...prev,
        [selectedId]: [...updatedHistory, { role:'assistant', content:'Something went wrong. Please try again.' }]
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => setChatHistory(prev => ({ ...prev, [selectedId]: [] }));
  const savePrompt = (agentId, prompt) => setCustomPrompts(prev => ({ ...prev, [agentId]: prompt }));

  return (
    <div style={{ display:'flex', height:'100vh', background:'#080a14', color:'#e8eaed', fontFamily:'DM Sans,sans-serif', overflow:'hidden' }}>
      <Sidebar
        selectedId={selectedId}
        onSelect={selectAgent}
        collapsed={collapsed}
        onToggle={toggleCategory}
        search={search}
        onSearch={setSearch}
        businessCtx={businessCtx}
        onCtxOpen={() => setShowCtx(true)}
      />
      <main style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden', background:'#0a0c16' }}>
        {messages.length === 0 ? (
          <WelcomeScreen
            agent={selectedAgent}
            catColor={catColor}
            onPrompt={handleSend}
            onShowSkills={() => setShowSkills(true)}
          />
        ) : (
          <ChatInterface
            agent={selectedAgent}
            catColor={catColor}
            messages={messages}
            isLoading={isLoading}
            input={input}
            setInput={setInput}
            onSend={handleSend}
            onNewChat={clearChat}
            onShowSkills={() => setShowSkills(true)}
          />
        )}
      </main>

      {showSkills && (
        <SkillsModal
          agent={selectedAgent}
          catColor={catColor}
          customPrompts={customPrompts}
          onSave={savePrompt}
          onClose={() => setShowSkills(false)}
        />
      )}
      {showCtx && (
        <ContextModal
          value={businessCtx}
          onSave={setBusinessCtx}
          onClose={() => setShowCtx(false)}
        />
      )}
    </div>
  );
}
