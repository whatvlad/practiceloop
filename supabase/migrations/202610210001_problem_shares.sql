-- #37: share a problem's statement, topic and difficulty by link or short code.
-- Additive only. Backend-only table: the browser never reads it, and lookups
-- return nothing but those three fields (docs/api/README.md "Sharing").
begin;

create table private.problem_shares (
  id uuid primary key default gen_random_uuid(),
  problem_id uuid not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  -- 32 random bytes, base64url: the link. Never derived from the problem.
  token text not null unique check (token ~ '^[A-Za-z0-9_-]{43}$'),
  -- 8 random Crockford base32 symbols (40 bits): typed by hand, shown as XXXX-XXXX.
  code text not null unique check (code ~ '^[0-9A-HJKMNP-TV-Z]{8}$'),
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  revoked_at timestamptz,
  check (expires_at > created_at and expires_at <= created_at + interval '90 days'),
  check (revoked_at is null or revoked_at >= created_at),
  -- A deleted problem or account takes its shares with it.
  foreign key (problem_id, user_id) references public.problems(id, user_id) on delete cascade
);
create index problem_shares_problem_idx on private.problem_shares(problem_id, created_at desc);

alter table private.problem_shares enable row level security;
revoke all on private.problem_shares from public, anon, authenticated;
grant select, insert, update, delete on private.problem_shares to service_role;

commit;
