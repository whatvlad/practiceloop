-- ADR-004 storage owned by #10: constant-omission flag and API idempotency keys.
-- Additive only; the applied initial migration is not rewritten.
begin;

alter table public.attempts
  add column constant_omitted boolean not null default false,
  -- `is false`, not `= false`: an invalid attempt (NULL) never omits a constant.
  add constraint attempts_constant_omitted_only_incorrect
    check (not constant_omitted or is_correct is false);

-- One row per (user, method, route, client key), kept 24 hours. The API writes
-- the key, the mutation and the stored response in one transaction, so a retry
-- or a concurrent duplicate replays the committed outcome instead of repeating it.
create table private.idempotency_keys (
  user_id uuid not null references auth.users(id) on delete cascade,
  method text not null check (method = 'POST'),
  route text not null check (char_length(route) between 1 and 200),
  key uuid not null,
  request_hash text not null check (char_length(request_hash) = 64),
  status_code smallint,
  response jsonb,
  created_at timestamptz not null default now(),
  primary key (user_id, method, route, key)
);
create index idempotency_keys_user_created_idx on private.idempotency_keys(user_id, created_at);

alter table private.idempotency_keys enable row level security;
revoke all on private.idempotency_keys from public, anon, authenticated;
grant select, insert, update, delete on private.idempotency_keys to service_role;

commit;
