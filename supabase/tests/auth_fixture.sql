-- Disposable PostgreSQL CI only. Do NOT run against Supabase or a shared DB.
-- Minimal auth.uid/roles fixture verifies SQL semantics, not Supabase JWT wiring.
create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls;
create schema auth;
create table auth.users(id uuid primary key);
create function auth.uid() returns uuid language sql stable as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;
grant usage on schema public, auth to anon, authenticated, service_role;
grant execute on function auth.uid() to anon, authenticated, service_role;

-- Supabase-created public tables receive browser grants by default. Migrations
-- must revoke those grants explicitly; otherwise this fixture would hide leaks.
alter default privileges in schema public
  grant all on tables to anon, authenticated, service_role;
