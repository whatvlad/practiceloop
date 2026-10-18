-- HUMAN ONLY, same disposable project after hosted API verification.
-- Deletes only the reserved fixtures; Auth users and profiles remain untouched.
begin;
delete from public.problems
where id in ('31000000-0000-0000-0000-000000000001', '31000000-0000-0000-0000-000000000002')
  and problem_latex = 'pl-hosted-isolation-v1';
-- Attempts and private solutions cascade via their problem FK.
commit;
