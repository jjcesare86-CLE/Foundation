-- PHP Shield -- core tables.
-- Target: PHP Shield's OWN Supabase project (NOT Foundation's, NOT Switchboard's).
-- Idempotent: safe to re-run. Apply in filename order (001 tables, 002 RLS, 003 guards).

create table if not exists public.leads (
  id               uuid primary key default gen_random_uuid(),
  report_token     text not null unique,
  url              text not null,
  domain           text not null,
  site_name        text,
  contact_email    text not null,
  consent_scan     boolean not null check (consent_scan is true),
  consent_text     text not null,
  consent_at       timestamptz not null default now(),
  ip_hash          text,
  user_agent       text,
  php_version      text,
  risk_level       text,
  confidence       text,
  scan             jsonb,
  status           text not null default 'new'
                   check (status in ('new','quote_requested','checkout_started','converted')),
  quote_requested  boolean not null default false,
  quote_notes      text,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create index if not exists idx_leads_domain on public.leads(domain, created_at desc);
create index if not exists idx_leads_email on public.leads(contact_email);

create table if not exists public.scan_events (
  id          uuid primary key default gen_random_uuid(),
  ip_hash     text not null,
  domain      text not null,
  created_at  timestamptz not null default now()
);
create index if not exists idx_scan_events_ip on public.scan_events(ip_hash, created_at desc);
create index if not exists idx_scan_events_domain on public.scan_events(domain, created_at desc);
create index if not exists idx_scan_events_created on public.scan_events(created_at desc);

create table if not exists public.orders (
  id                         uuid primary key default gen_random_uuid(),
  public_token               text not null unique,          -- unguessable customer link token
  lead_id                    uuid references public.leads(id),
  domain                     text not null,                 -- immutable once created (see 003)
  customer_email             text not null,
  tier                       text check (tier in ('basic','standard','complex')),  -- null = maintenance only
  maintenance                boolean not null default false,
  amount_cents               integer,
  status                     text not null default 'pending_payment'
                             check (status in ('pending_payment','paid','intake_complete','authorized',
                                               'verified','in_progress','delivered','closed','canceled')),
  stripe_checkout_session_id text unique,
  stripe_customer_id         text,
  stripe_subscription_id     text,
  paid_at                    timestamptz,
  checklist                  jsonb not null default '{}'::jsonb,
  delivered_at               timestamptz,
  closed_at                  timestamptz,
  admin_notes                text,
  created_at                 timestamptz not null default now(),
  updated_at                 timestamptz not null default now(),
  check (tier is not null or maintenance is true)
);
create index if not exists idx_orders_status on public.orders(status, created_at desc);
create index if not exists idx_orders_domain on public.orders(domain);
create index if not exists idx_orders_email on public.orders(customer_email);

create table if not exists public.order_events (
  id           uuid primary key default gen_random_uuid(),
  order_id     uuid not null references public.orders(id),
  from_status  text,
  to_status    text not null,
  actor        text not null,
  note         text,
  created_at   timestamptz not null default now()
);
create index if not exists idx_order_events_order on public.order_events(order_id, created_at);

create table if not exists public.intake (
  id                        uuid primary key default gen_random_uuid(),
  order_id                  uuid not null unique references public.orders(id),
  site_url                  text not null,
  hosting_provider          text not null,
  access_method             text not null check (access_method in ('sftp','ssh','cpanel','wp_admin','other')),
  access_method_other       text,
  has_staging_or_backup     text not null,
  preferred_timing          text not null,
  contact_name              text not null,
  contact_email             text not null,
  contact_phone             text,
  notes                     text,
  -- Credentials are NEVER collected in this form. Hand-off happens later through a
  -- one-time secure link; this column only tracks where that hand-off stands.
  credentials_handoff_status text not null default 'not_requested'
                             check (credentials_handoff_status in ('not_requested','link_pending','link_sent','received')),
  created_at                timestamptz not null default now()
);

-- Append-only: signed authorizations (see 003 for the triggers that enforce it).
create table if not exists public.authorizations (
  id                uuid primary key default gen_random_uuid(),
  order_id          uuid not null unique references public.orders(id),
  domain            text not null,
  typed_name        text not null check (length(btrim(typed_name)) >= 3),
  agreement_version text not null,
  agreement_hash    text not null check (agreement_hash ~ '^[0-9a-f]{64}$'),  -- sha256 of agreement_text
  agreement_text    text not null,                                            -- exact text that was shown
  signed_at         timestamptz not null default now(),
  ip                text not null,
  user_agent        text not null,
  created_at        timestamptz not null default now()
);

create table if not exists public.authorization_revocations (
  id          uuid primary key default gen_random_uuid(),
  order_id    uuid not null unique references public.orders(id),
  reason      text,
  ip          text,
  user_agent  text,
  revoked_at  timestamptz not null default now(),
  created_at  timestamptz not null default now()
);

create table if not exists public.domain_verifications (
  id               uuid primary key default gen_random_uuid(),
  order_id         uuid not null unique references public.orders(id),
  domain           text not null,
  token            text not null,
  method           text check (method in ('dns','file')),
  verified_at      timestamptz,
  last_checked_at  timestamptz,
  last_detail      text,
  created_at       timestamptz not null default now()
);

create table if not exists public.scan_reports (
  id           uuid primary key default gen_random_uuid(),
  order_id     uuid references public.orders(id),
  domain       text not null,
  kind         text not null check (kind in ('before','after','monthly')),
  version      text,
  risk_level   text,
  result       jsonb not null,
  created_at   timestamptz not null default now()
);
create index if not exists idx_scan_reports_order on public.scan_reports(order_id, created_at desc);

create table if not exists public.subscriptions (
  id                      uuid primary key default gen_random_uuid(),
  order_id                uuid references public.orders(id),
  stripe_subscription_id  text not null unique,
  stripe_customer_id      text,
  domain                  text not null,
  customer_email          text not null,
  status                  text not null default 'active' check (status in ('active','past_due','canceled')),
  next_scan_at            timestamptz,
  last_scan_at            timestamptz,
  last_invoice_paid_at    timestamptz,
  canceled_at             timestamptz,
  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now()
);
create index if not exists idx_subscriptions_due on public.subscriptions(status, next_scan_at);

create table if not exists public.webhook_events (
  id          uuid primary key default gen_random_uuid(),
  event_id    text not null unique,     -- Stripe event id: the idempotency key
  type        text not null,
  created_at  timestamptz not null default now()
);

create table if not exists public.dead_letters (
  id          uuid primary key default gen_random_uuid(),
  kind        text not null,
  payload     jsonb not null,
  error       text,
  created_at  timestamptz not null default now()
);

create table if not exists public.health_checks (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now()
);
