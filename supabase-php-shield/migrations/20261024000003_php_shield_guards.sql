-- PHP Shield -- database-enforced guards. Idempotent.
--
--  1. authorizations + authorization_revocations are APPEND-ONLY (no UPDATE/DELETE/TRUNCATE,
--     for any role, including service_role which would otherwise bypass RLS).
--  2. Order status can only advance one step at a time, and the fulfillment gate lives here:
--        no order may become 'in_progress' (or even 'authorized'/'verified') without a signed,
--        unrevoked authorization for THAT order AND THAT domain; 'verified' and 'in_progress'
--        also require verified domain ownership; 'in_progress' also requires payment.
--     The application enforces the same rules first; this is the backstop.
--  3. An authorization can only be recorded for the order's own domain, once intake is done.

create or replace function public.php_shield_touch() returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists trg_touch_leads on public.leads;
create trigger trg_touch_leads before update on public.leads
  for each row execute function public.php_shield_touch();
drop trigger if exists trg_touch_orders on public.orders;
create trigger trg_touch_orders before update on public.orders
  for each row execute function public.php_shield_touch();
drop trigger if exists trg_touch_subscriptions on public.subscriptions;
create trigger trg_touch_subscriptions before update on public.subscriptions
  for each row execute function public.php_shield_touch();

-- 1. append-only ----------------------------------------------------------------
create or replace function public.php_shield_append_only() returns trigger language plpgsql as $$
begin
  raise exception '% is append-only: % is not allowed', tg_table_name, tg_op using errcode = 'P0001';
end $$;

drop trigger if exists trg_authorizations_append_only on public.authorizations;
create trigger trg_authorizations_append_only before update or delete on public.authorizations
  for each row execute function public.php_shield_append_only();
drop trigger if exists trg_authorizations_no_truncate on public.authorizations;
create trigger trg_authorizations_no_truncate before truncate on public.authorizations
  for each statement execute function public.php_shield_append_only();

drop trigger if exists trg_revocations_append_only on public.authorization_revocations;
create trigger trg_revocations_append_only before update or delete on public.authorization_revocations
  for each row execute function public.php_shield_append_only();
drop trigger if exists trg_revocations_no_truncate on public.authorization_revocations;
create trigger trg_revocations_no_truncate before truncate on public.authorization_revocations
  for each statement execute function public.php_shield_append_only();

-- 3. an authorization must match its order ---------------------------------------
create or replace function public.php_shield_authorization_check() returns trigger language plpgsql as $$
declare o public.orders%rowtype;
begin
  select * into o from public.orders where id = new.order_id;
  if not found then
    raise exception 'authorization references unknown order' using errcode = 'P0001';
  end if;
  if new.domain is distinct from o.domain then
    raise exception 'authorization domain (%) does not match order domain (%)', new.domain, o.domain
      using errcode = 'P0001';
  end if;
  if o.status <> 'intake_complete' then
    raise exception 'authorization can only be signed when the order is intake_complete (is %)', o.status
      using errcode = 'P0001';
  end if;
  return new;
end $$;

drop trigger if exists trg_authorizations_check on public.authorizations;
create trigger trg_authorizations_check before insert on public.authorizations
  for each row execute function public.php_shield_authorization_check();

-- 2. order state machine + fulfillment gate --------------------------------------
create or replace function public.php_shield_order_guard() returns trigger language plpgsql as $$
declare
  allowed boolean;
  signed  boolean;
  revoked boolean;
  verified boolean;
begin
  if tg_op = 'INSERT' then
    if new.status <> 'pending_payment' then
      raise exception 'orders must be created as pending_payment' using errcode = 'P0001';
    end if;
    return new;
  end if;

  if new.domain is distinct from old.domain then
    raise exception 'order domain is immutable' using errcode = 'P0001';
  end if;
  if new.status is not distinct from old.status then
    return new;
  end if;

  allowed := case old.status
    when 'pending_payment' then new.status in ('paid', 'canceled')
    when 'paid'            then new.status in ('intake_complete', 'canceled')
    when 'intake_complete' then new.status in ('authorized', 'canceled')
    when 'authorized'      then new.status in ('verified', 'canceled')
    when 'verified'        then new.status in ('in_progress', 'canceled')
    when 'in_progress'     then new.status = 'delivered'
    when 'delivered'       then new.status = 'closed'
    else false end;
  if not allowed then
    raise exception 'illegal order transition % -> %', old.status, new.status using errcode = 'P0001';
  end if;

  if new.status = 'intake_complete'
     and not exists (select 1 from public.intake where order_id = new.id) then
    raise exception 'intake_complete requires a submitted intake form' using errcode = 'P0001';
  end if;

  if new.status in ('authorized', 'verified', 'in_progress') then
    select exists (select 1 from public.authorizations a
                    where a.order_id = new.id and a.domain = new.domain) into signed;
    select exists (select 1 from public.authorization_revocations r
                    where r.order_id = new.id) into revoked;
    if not signed or revoked then
      raise exception 'order % cannot become % without a valid signed authorization for domain %',
        new.id, new.status, new.domain using errcode = 'P0001';
    end if;
  end if;

  if new.status in ('verified', 'in_progress') then
    select exists (select 1 from public.domain_verifications v
                    where v.order_id = new.id and v.domain = new.domain and v.verified_at is not null)
      into verified;
    if not verified then
      raise exception 'order % cannot become % before domain ownership is verified', new.id, new.status
        using errcode = 'P0001';
    end if;
  end if;

  if new.status = 'in_progress' and new.paid_at is null then
    raise exception 'order % cannot start before payment', new.id using errcode = 'P0001';
  end if;

  return new;
end $$;

drop trigger if exists trg_orders_guard on public.orders;
create trigger trg_orders_guard before insert or update on public.orders
  for each row execute function public.php_shield_order_guard();
