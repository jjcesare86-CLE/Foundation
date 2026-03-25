# Voice Agent Skills — Library Index

This folder contains all voice agent skill definitions.
Each `.md` file is the human-readable version of what's seeded into `foundation.skills`.

## Categories
- `restaurant-reservations.md`
- `dental-scheduler.md`
- `real-estate-qualifier.md`
- `fitness-class-booking.md`
- `legal-intake.md`
- `hvac-dispatch.md`
- `salon-booking.md`
- `auto-shop-scheduler.md`

## How Skills Are Used
1. Stored in Supabase `foundation.skills` table (machine-queryable)
2. Pulled by the Voice Setup Agent during client onboarding
3. Injected into VAPI assistant system prompt with client-specific variables filled in

## Variable Syntax
All skills use `{{variable_name}}` for injectable values.
The Onboarding Orchestrator fills these from the `client_profiles` table.

Common variables:
- `{{business_name}}` — Client's business name
- `{{industry}}` — Their industry
- `{{tone_keywords}}` — Their brand voice descriptors
- `{{business_hours}}` — Operating hours
- `{{owner_name}}` — Business owner name
- `{{phone}}` — Business phone
- `{{address}}` — Physical address
