-- Review locally before applying. No hosted database has been modified.
begin;

create schema if not exists private;
revoke all on schema private from public, anon, authenticated;
grant usage on schema private to service_role;

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);
create table public.topics (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique
);
create table public.problems (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  topic_id uuid not null references public.topics(id),
  difficulty smallint not null check (difficulty between 1 and 5),
  problem_latex text not null,
  created_at timestamptz not null default now(),
  answer_revealed boolean not null default false,
  solution_revealed boolean not null default false,
  unique (id, user_id)
);
create table public.attempts (
  id uuid primary key default gen_random_uuid(),
  problem_id uuid not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  user_answer text not null check (char_length(user_answer) between 1 and 512),
  -- NULL represents Invalid expression; false represents Incorrect.
  is_correct boolean,
  created_at timestamptz not null default now(),
  foreign key (problem_id, user_id) references public.problems(id, user_id) on delete cascade
);
create table private.problem_solutions (
  problem_id uuid primary key references public.problems(id) on delete cascade,
  generator_version text not null,
  generator_data jsonb not null,
  answer_latex text not null,
  solution_steps jsonb not null check (jsonb_typeof(solution_steps) = 'array')
);

create index problems_user_created_idx on public.problems(user_id, created_at desc, id);
create index attempts_user_created_idx on public.attempts(user_id, created_at desc, id);
create index attempts_problem_idx on public.attempts(problem_id);

alter table public.profiles enable row level security;
alter table public.topics enable row level security;
alter table public.problems enable row level security;
alter table public.attempts enable row level security;
alter table private.problem_solutions enable row level security;

-- All writes go through the authenticated backend; clients cannot forge scores,
-- reveal flags or history. service_role bypasses RLS, so API ownership is mandatory.
revoke all on public.profiles, public.topics, public.problems, public.attempts
  from public, anon, authenticated;
revoke all on private.problem_solutions from public, anon, authenticated;
grant select on public.profiles, public.topics, public.problems, public.attempts to authenticated;
grant all on public.profiles, public.topics, public.problems, public.attempts to service_role;
grant all on private.problem_solutions to service_role;

create policy profiles_read_own on public.profiles for select to authenticated
  using ((select auth.uid()) = id);
create policy topics_read on public.topics for select to authenticated using (true);
create policy problems_read_own on public.problems for select to authenticated
  using ((select auth.uid()) = user_id);
create policy attempts_read_own on public.attempts for select to authenticated
  using ((select auth.uid()) = user_id);

insert into public.topics(name, slug) values
  ('Basic integrals', 'basic-integrals'),
  ('Substitution', 'substitution'),
  ('Integration by parts', 'integration-by-parts'),
  ('Rational functions', 'rational-functions'),
  ('Trigonometric integrals', 'trigonometric-integrals');

commit;
