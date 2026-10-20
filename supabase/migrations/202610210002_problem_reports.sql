-- #38: "Report a problem". Additive only. Backend-only table: a report holds
-- the problem, one fixed category and an optional comment, nothing else. The
-- user_id is the owner key that deletes reports with the account or problem.
begin;

create table private.problem_reports (
  id uuid primary key default gen_random_uuid(),
  problem_id uuid not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  category text not null check (category in
    ('answer_check', 'solution', 'statement', 'display', 'other')),
  comment text check (comment is null or char_length(comment) between 1 and 500),
  created_at timestamptz not null default now(),
  foreign key (problem_id, user_id) references public.problems(id, user_id) on delete cascade
);
create index problem_reports_created_idx on private.problem_reports(created_at desc);
create index problem_reports_problem_idx on private.problem_reports(problem_id, user_id);

alter table private.problem_reports enable row level security;
revoke all on private.problem_reports from public, anon, authenticated;
grant select, insert, delete on private.problem_reports to service_role;

commit;
