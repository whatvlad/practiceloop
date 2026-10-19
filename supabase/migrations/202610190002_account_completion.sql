-- #35: optional profile name, per-attempt elapsed time, and deleted-account guard.
begin;
alter table public.profiles add column display_name text
  check (display_name is null or char_length(display_name) between 1 and 80);
alter table public.attempts add column elapsed_ms integer
  check (elapsed_ms is null or elapsed_ms between 0 and 86400000);

-- JWTs outlive Auth deletion. Expose only existence to the backend, never auth rows.
create function private.account_exists(account_id uuid) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists(select 1 from auth.users where id = account_id)
$$;
revoke all on function private.account_exists(uuid) from public, anon, authenticated;
grant execute on function private.account_exists(uuid) to service_role;
commit;
