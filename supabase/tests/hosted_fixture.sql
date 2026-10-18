-- HUMAN ONLY, disposable hosted project, Supabase SQL Editor (postgres role).
-- Never run auth_fixture.sql or isolation.sql against hosted Supabase.
-- Replace the two UUID placeholders with existing, real Auth user IDs.
begin;
create temporary table pl_test_users (slot int primary key, user_id uuid unique not null);
insert into pl_test_users values
  (1, 'REPLACE_WITH_USER_A_UUID'),
  (2, 'REPLACE_WITH_USER_B_UUID');
do $$ begin
  assert (select count(*) from auth.users where id in (select user_id from pl_test_users)) = 2,
    'Create two real Auth users before provisioning fixtures';
end $$;
insert into public.profiles(id) select user_id from pl_test_users on conflict (id) do nothing;
-- Fixed test IDs deliberately fail on collision; never overwrite existing rows.
insert into public.problems(id, user_id, topic_id, difficulty, problem_latex)
select case slot
    when 1 then '31000000-0000-0000-0000-000000000001'::uuid
    else '31000000-0000-0000-0000-000000000002'::uuid end,
  user_id, topics.id, 1, 'pl-hosted-isolation-v1'
from pl_test_users cross join public.topics where slug = 'basic-integrals';
insert into private.problem_solutions(problem_id, generator_version, generator_data, answer_latex, solution_steps)
select id, 'hosted-isolation-v1', '{}', 'fixture-private-answer', '[]'
from public.problems where id in (
  '31000000-0000-0000-0000-000000000001', '31000000-0000-0000-0000-000000000002');
insert into public.attempts(id, problem_id, user_id, user_answer, is_correct)
select case slot
    when 1 then '32000000-0000-0000-0000-000000000001'::uuid
    else '32000000-0000-0000-0000-000000000002'::uuid end,
  case slot
    when 1 then '31000000-0000-0000-0000-000000000001'::uuid
    else '31000000-0000-0000-0000-000000000002'::uuid end,
  user_id, 'fixture-answer', true
from pl_test_users;
drop table pl_test_users;
commit;
