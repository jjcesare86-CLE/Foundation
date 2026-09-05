# ROSTER CHANGE — CALEB TO SECURITY, NEHEMIAH TO COO
**Decided Sep 2, 2026. Runs as Phase 0.6, before Batch 1 (Batch 1 handoffs reference the C-suite).**

## The change
| Agent | Before | After |
|---|---|---|
| **Caleb** | Chief Operating Officer · csuite · complex | **Chief Information Security Officer (CISO)** · csuite · complex |
| **Nehemiah** | — | **Chief Operating Officer** · csuite · complex (new row) |
| **Ezra** | Tech & IT Support · operations · standard | unchanged — now reports to Caleb |

Why CISO and not CSO: Isaiah already holds CSO (Chief Strategy Officer). Why Caleb stays C-suite: security decisions (quarantine, block, release, warn the team) are judgment calls that should run on the `complex` tier, not `standard`.

## What Caleb does now
Inbound mail and message triage (hold-and-ask on suspicious senders, look-alike domains, executables in disguise), credential and token hygiene across the Connections Hub, access reviews when a member is added or removed from a Switchboard workspace, license/compliance escalations from Amos that carry security weight, and the plain-English incident write-up. Hard lines: **never releases an executable to a user; never auto-clears a held message; never replaces the client's existing mail security — he is a layer on top of it.** Receipts on every action (Proof of Work). Handoffs: Ezra (fix it), Peter/Abigail (legal exposure), Nehemiah (operational impact), Solomon (business-level incident).

## What Nehemiah does now
Everything the COO prompt said before: strategy-to-execution, KPI tracking, blocker removal, department coordination. Redirects financial modeling to Miriam, security to Caleb. **Recommended: Nehemiah becomes the "Ask" concierge on the AN homepage floating button** (currently Caleb) — a front-door assistant should be operations, not security. John decides.

## Migration prompt (paste after the session header, after Phase 0.4)
```
Foundation repo, branch roster-caleb-security. Same GLOBAL RULES (project
rhtwtoinmiekttvunlzs, schema foundation, CLI migrations, live-schema
introspection, no secrets). Read docs/specs/04_ROSTER_CHANGE_CALEB_SECURITY.md.

1. Introspect foundation.ai_employees for the Caleb row and one other C-suite
   row (Miriam) to see the exact slug, handoff, and org-chart conventions.
2. Migration:
   - UPDATE Caleb: role='Chief Information Security Officer',
     department stays 'csuite', model_tier stays 'complex'; rewrite
     system_prompt for the CISO role per the spec (hard lines included);
     handoff_to → ezra, peter, abigail, nehemiah, solomon; supervises → ezra;
     helps / outside_scope updated to match. Keep the same id and slug so
     nothing referencing Caleb's id breaks; if the slug embeds "coo", add a
     legacy_slug column (if absent) and keep the old value there.
   - INSERT Nehemiah: biblical_name='Nehemiah', product_name='Nehemiah',
     role='Chief Operating Officer', department='csuite', is_csuite=true,
     model_tier='complex', system_prompt = the former COO prompt adapted to
     Nehemiah's voice (organizer, builder, "everyone on their section of the
     wall"), handoff_to → miriam, caleb, solomon, joseph; reports_to →
     solomon; supervises → joseph, naomi, martha, silas (when he exists).
   - employee_platform_subscriptions rows for Nehemiah matching Caleb's.
   - Ezra: reports_to → caleb. Nothing else changes.
   All idempotent; seeds via ON CONFLICT.
3. Repo sweep: every place that hard-codes Caleb as COO or as the default AN
   concierge — system prompts, handoff text, Switchboard default_agent for the
   AN property, frontend copy in this repo. Change COO references to
   Nehemiah. Leave the AN homepage "Ask Caleb" button's target as a TODO with
   both options noted (Nehemiah recommended) — that lives in the AN repo and
   John decides.
4. Update docs/specs/00_STATE_OF_THE_BUILD.md §2 (roster table) and
   docs/state/DECISIONS.md in the same commit.
VERIFY: /agents returns 27; Caleb's row shows the CISO role and a
security-specific system_prompt; Nehemiah resolves to claude-opus-4-8 in a
dry run; Ezra's reports_to is Caleb; the ops-audit L1 check (once D exists)
shows both rows complete.
```

## Ripple through the rest of the package
- Batch 1 master prompt Phase 0 verify now checks five `complex` rows: nehemiah, caleb, miriam, isaiah, abigail.
- Switchboard spec: AN property's default agent = Nehemiah (was Caleb).
- Launch pages (item N): the security page is `caleb.automaitionnation.com` and the agent is Caleb — the "who really does the work" hedge is gone.
- Demo v9 reflects it: Caleb runs the inbox-quarantine scenario; Ezra is Tech & IT; Nehemiah is Operations.
