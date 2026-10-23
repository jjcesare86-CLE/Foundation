-- PHP Shield -- row level security.
-- Only the service role (the php-shield-api backend) may touch any table; the anon and
-- authenticated roles get no policy and therefore no access. Naming follows the repo
-- convention service_role_all_<table>. Idempotent.
--
-- authorizations / authorization_revocations are the exception: service_role may only
-- SELECT and INSERT (no UPDATE/DELETE policy exists), and 003 adds triggers that block
-- UPDATE/DELETE/TRUNCATE even for roles that bypass RLS.

do $$
declare t text;
begin
  foreach t in array array[
    'leads','scan_events','orders','order_events','intake','domain_verifications',
    'scan_reports','subscriptions','webhook_events','dead_letters','health_checks'
  ] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists %I on public.%I', 'service_role_all_' || t, t);
    execute format(
      'create policy %I on public.%I for all using (auth.role() = ''service_role'') with check (auth.role() = ''service_role'')',
      'service_role_all_' || t, t);
  end loop;

  foreach t in array array['authorizations','authorization_revocations'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists %I on public.%I', 'service_role_all_' || t, t);
    execute format('drop policy if exists %I on public.%I', 'service_role_select_' || t, t);
    execute format('drop policy if exists %I on public.%I', 'service_role_insert_' || t, t);
    execute format('create policy %I on public.%I for select using (auth.role() = ''service_role'')',
                   'service_role_select_' || t, t);
    execute format('create policy %I on public.%I for insert with check (auth.role() = ''service_role'')',
                   'service_role_insert_' || t, t);
  end loop;
end $$;
