---
slug: website-5page-universal
template_type: website
industries: [service, agency, consulting, retail]
platforms: [automation-nation]
version: 1.0.0
variables:
  - business_name
  - tagline
  - industry
  - primary_service
  - services_list
  - owner_name
  - city
  - phone
  - email
  - primary_color
  - secondary_color
  - tone_keywords
---

# 5-Page Universal Business Website Template

---

## PAGE 1: HOME

### Hero Section
**Headline:** Stop Losing Business to {{primary_pain_point}}. {{business_name}} Has the Answer.
**Subheadline:** {{tagline}}
**CTA Button:** Get Started Today
**Secondary CTA:** See How It Works

### Value Props (3-column)
- ✅ **{{benefit_1_headline}}** — {{benefit_1_body}}
- ✅ **{{benefit_2_headline}}** — {{benefit_2_body}}
- ✅ **{{benefit_3_headline}}** — {{benefit_3_body}}

### Social Proof Bar
"Trusted by 100+ {{industry}} businesses in {{city}} and beyond"

### Services Preview (3 cards)
Top 3 from `{{services_list}}` — each with icon, title, 1-line description, "Learn More" link

### Testimonials (2 featured)
Pull from `{{testimonials}}` — name, business, quote, star rating

### Final CTA Section
**Headline:** Ready to {{primary_outcome}}?
**Body:** Don't let another day go by leaving money on the table. {{business_name}} is ready when you are.
**CTA:** Book a Free Consultation

---

## PAGE 2: ABOUT

### Header
**Headline:** The Story Behind {{business_name}}
**Subheadline:** We built this because we've seen what happens when {{industry}} businesses don't have the right systems.

### Origin Story
{{owner_name}} founded {{business_name}} after [origin_story]. Today, we serve clients across {{service_area}} with a single mission: {{mission}}.

### Team Section
[Team member cards — name, title, 1-line bio, photo placeholder]

### Values Section (3-4 values)
Pull from brand profile `{{values}}`

### Stats Bar
- **{{stat_1_number}}** {{stat_1_label}}
- **{{stat_2_number}}** {{stat_2_label}}
- **{{stat_3_number}}** {{stat_3_label}}

---

## PAGE 3: SERVICES

### Header
**Headline:** Everything Your {{industry}} Business Needs to Thrive
**Subheadline:** From {{service_1}} to {{service_last}}, we handle it all.

### Service Cards (one per service in `{{services_list}}`)
Each card:
- **Name:** {{service_name}}
- **Icon:** [relevant emoji or icon]
- **Description:** {{service_description}}
- **Key benefit:** {{service_key_benefit}}
- **CTA:** Get This Service

### Pricing Preview (if applicable)
[Tier cards — name, price, key features, CTA]

### FAQ (5-7 questions)
Common questions for {{industry}} clients about {{primary_service}}

---

## PAGE 4: TESTIMONIALS / RESULTS

### Header
**Headline:** Real Results for Real {{industry}} Businesses
**Subheadline:** Don't take our word for it.

### Featured Case Study
**Business:** {{case_study_business}}
**Challenge:** {{case_study_challenge}}
**Solution:** {{case_study_solution}}
**Result:** {{case_study_result}}

### Review Grid (6-9 reviews)
Pull from `{{testimonials_full_list}}`

### Logos Bar
"Businesses that trust {{business_name}}"

---

## PAGE 5: CONTACT

### Header
**Headline:** Let's Talk About Your {{industry}} Business
**Subheadline:** Fill out the form below and we'll get back to you within {{response_time}}.

### Contact Form Fields
- Full Name *
- Business Name *
- Email *
- Phone *
- Industry (dropdown)
- What's your biggest challenge right now? (textarea)
- How did you hear about us? (dropdown)
- [Submit Button: "Get My Free Consultation"]

### Contact Info Block
- 📞 {{phone}}
- 📧 {{email}}
- 📍 {{address}}
- 🕐 {{business_hours}}

### Map Embed (if physical location)

---

## LOVABLE.DEV PROMPT

Use this prompt to build the site automatically:

```
Build a professional 5-page business website for {{business_name}}, a {{industry}} company.

Brand: Primary color {{primary_color}}, secondary {{secondary_color}}. Tone: {{tone_keywords}}.
Tagline: "{{tagline}}"

Pages:
1. Home — Hero with "{{headline}}", 3 value props, services preview, 2 testimonials, CTA
2. About — Origin story, team, values, stats bar
3. Services — Cards for: {{services_list}}. Include pricing tiers if applicable.
4. Testimonials — Case study + review grid
5. Contact — Form (name, business, email, phone, challenge textarea) + contact info

Style: Modern, professional, mobile-first. Use {{primary_color}} for primary buttons and accents.
Include: navigation with mobile hamburger menu, footer with links and social icons, sticky CTA bar.
Make it fast-loading and SEO-ready.
```

---

## SEO METADATA

| Page | Title Tag | Meta Description |
|------|-----------|-----------------|
| Home | {{business_name}} — {{tagline}} \| {{city}} | {{meta_home}} |
| About | About {{business_name}} \| {{city}} {{industry}} | {{meta_about}} |
| Services | {{primary_service}} in {{city}} \| {{business_name}} | {{meta_services}} |
| Testimonials | Client Results \| {{business_name}} {{city}} | {{meta_testimonials}} |
| Contact | Contact {{business_name}} \| {{city}} {{industry}} | {{meta_contact}} |
