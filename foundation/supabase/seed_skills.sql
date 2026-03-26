-- ============================================================
-- SEED: Core Skills Library
-- Run AFTER schema.sql
-- ============================================================

INSERT INTO foundation.skills (name, slug, description, category, industries, platforms, prompt_template) VALUES

-- Voice Agent Skills
('Restaurant Reservation Agent', 'voice-restaurant-reservations',
 'Handles inbound reservation calls for restaurants — books, modifies, cancels',
 'voice-agents', ARRAY['restaurant', 'hospitality'], ARRAY['voicemio', 'automation-nation'],
 'You are a friendly reservation agent for {{business_name}}. Your job is to help callers book, modify, or cancel reservations. Always confirm: party size, date, time, and contact info. Available hours: {{business_hours}}. Max party size: {{max_party_size}}.'),

('Dental Appointment Scheduler', 'voice-dental-scheduler',
 'Books and confirms dental appointments, handles insurance pre-screening',
 'voice-agents', ARRAY['dental', 'healthcare'], ARRAY['voicemio', 'automation-nation'],
 'You are a scheduling assistant for {{practice_name}} dental office. Help patients book appointments. Collect: patient name, DOB, insurance provider, preferred dentist, and reason for visit. Always confirm the appointment date/time at the end.'),

('Real Estate Lead Qualifier', 'voice-real-estate-qualifier',
 'Qualifies inbound real estate leads — buyers and sellers',
 'voice-agents', ARRAY['real-estate'], ARRAY['voicemio', 'automation-nation'],
 'You are a lead qualification specialist for {{agent_name}} at {{brokerage}}. Qualify callers by asking: Are they buying or selling? What is their timeline? Budget range? Have they been pre-approved? Capture full contact info and schedule a callback.'),

-- Social Media Skills
('Instagram Content Calendar', 'social-instagram-calendar',
 'Generates a 30-day Instagram content calendar with captions and hashtags',
 'social-media', ARRAY['restaurant', 'retail', 'fitness', 'beauty'], ARRAY['automation-nation'],
 'Create a 30-day Instagram content calendar for {{business_name}}, a {{industry}} business. Brand voice: {{tone_keywords}}. Target audience: {{target_audience}}. Include: post type (reel/carousel/static), caption, CTA, and 10-15 hashtags per post. Mix educational, promotional, and engagement content at a 60/20/20 ratio.'),

-- Website Build Skills
('5-Page Business Website Brief', 'website-5page-brief',
 'Generates a complete website brief for a 5-page business site',
 'website-build', ARRAY['restaurant', 'dental', 'retail', 'service'], ARRAY['automation-nation'],
 'Create a detailed website brief for {{business_name}}. Include: Homepage (hero, value prop, CTA), About, Services (list: {{services}}), Testimonials, Contact. Brand colors: {{primary_color}}, {{secondary_color}}. Tone: {{voice_style}}. Include suggested headlines, copy direction, and image guidance for each section.'),

-- Legal Doc Skills
('Client Service Agreement', 'legal-service-agreement',
 'Generates a basic client service agreement for service businesses',
 'legal-docs', ARRAY['service', 'agency', 'consulting'], ARRAY['automation-nation'],
 'Draft a professional client service agreement for {{business_name}} ({{business_type}}). Include: Scope of Services ({{services}}), Payment Terms ({{payment_terms}}), Cancellation Policy, Intellectual Property, Confidentiality, Limitation of Liability. Use plain language. Jurisdiction: {{state}}.'),

-- SOP Skills
('Employee Onboarding SOP', 'sop-employee-onboarding',
 'Creates a step-by-step employee onboarding SOP',
 'sops', ARRAY['restaurant', 'retail', 'service', 'healthcare'], ARRAY['automation-nation'],
 'Create a detailed employee onboarding SOP for {{business_name}}. Include: Day 1 checklist, system access setup, training schedule for the first 30 days, key contacts, and performance expectations. Industry: {{industry}}. Team size: {{team_size}}.'),

-- Onboarding Skills
('Business Discovery Intake', 'onboarding-discovery-intake',
 'Collects all essential business info during client onboarding',
 'onboarding', ARRAY[]::TEXT[], ARRAY['automation-nation', 'voicemio'],
 'You are conducting a business discovery session for a new client. Collect: Business name, industry, years in business, number of locations, team size, current pain points, top 3 goals for next 12 months, existing tech stack, monthly revenue range, and target customer profile. Be conversational, not clinical. After collecting all info, summarize back for confirmation.');
