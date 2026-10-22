-- #116 (ADR-007): printable PDF worksheets. Additive only. A worksheet is a
-- list of the owner's problems; problems a `generate` worksheet created carry
-- its id, so History can filter them and the `generated` count can skip them
-- until they are attempted. No PDF is stored.
begin;

create table public.worksheets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  source text not null check (source in ('generate', 'history')),
  paper text not null check (paper in ('a4', 'letter')),
  columns smallint not null check (columns in (1, 2)),
  answer_key boolean not null,
  -- The groups as requested and as filled, [{topic, difficulty, requested, count}]:
  -- a mixed group's problems carry the drawn topic, so the label lives here.
  groups jsonb not null check (jsonb_typeof(groups) = 'array'),
  unique (id, user_id)
);
create index worksheets_user_created_idx on public.worksheets(user_id, created_at desc);

create table public.worksheet_items (
  worksheet_id uuid not null references public.worksheets(id) on delete cascade,
  problem_id uuid not null references public.problems(id) on delete cascade,
  position smallint not null check (position between 1 and 40),
  group_index smallint not null check (group_index between 0 and 39),
  primary key (worksheet_id, position),
  unique (worksheet_id, problem_id)
);
create index worksheet_items_problem_idx on public.worksheet_items(problem_id);

alter table public.problems
  add column worksheet_id uuid references public.worksheets(id) on delete set null;
create index problems_user_worksheet_created_idx
  on public.problems(user_id, created_at desc, id) where worksheet_id is not null;

alter table public.worksheets enable row level security;
alter table public.worksheet_items enable row level security;

-- Like the other learning tables: owners read, only the backend writes.
revoke all on public.worksheets, public.worksheet_items from public, anon, authenticated;
grant select on public.worksheets, public.worksheet_items to authenticated;
grant select, insert, update, delete on public.worksheets, public.worksheet_items to service_role;

create policy worksheets_read_own on public.worksheets for select to authenticated
  using ((select auth.uid()) = user_id);
create policy worksheet_items_read_own on public.worksheet_items for select to authenticated
  using (exists (
    select 1 from public.worksheets w
    where w.id = worksheet_id and w.user_id = (select auth.uid())
  ));

commit;
