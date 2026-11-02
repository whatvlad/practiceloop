\set ON_ERROR_STOP on
begin;

do $$ begin
  assert not has_function_privilege('anon', 'private.account_exists(uuid)', 'EXECUTE');
  assert not has_function_privilege('authenticated', 'private.account_exists(uuid)', 'EXECUTE');
  assert has_function_privilege('service_role', 'private.account_exists(uuid)', 'EXECUTE');
  -- #37: share tokens and codes are read only by the backend.
  assert not has_table_privilege('anon', 'private.problem_shares', 'SELECT');
  assert not has_table_privilege('authenticated', 'private.problem_shares', 'SELECT');
  assert has_table_privilege('service_role', 'private.problem_shares', 'SELECT');
  -- #38: problem reports are written and read only by the backend.
  assert not has_table_privilege('anon', 'private.problem_reports', 'INSERT');
  assert not has_table_privilege('authenticated', 'private.problem_reports', 'INSERT');
  assert not has_table_privilege('authenticated', 'private.problem_reports', 'SELECT');
  assert has_table_privilege('service_role', 'private.problem_reports', 'INSERT');
end $$;

-- Check privileges directly, independently of RLS or schema USAGE. In particular,
-- TRUNCATE bypasses RLS, and new tables may inherit unsafe default grants.
do $$
declare
  unsafe_grants text;
begin
  select string_agg(
    format('%I.%I: %I has %s', n.nspname, c.relname, browser.role_name, operation.privilege),
    '; ' order by n.nspname, c.relname, browser.role_name, operation.privilege
  ) into unsafe_grants
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  cross join (values ('anon'), ('authenticated')) as browser(role_name)
  cross join (values ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE')) as operation(privilege)
  where n.nspname in ('public', 'private')
    and c.relkind in ('r', 'p', 'f')
    and has_table_privilege(browser.role_name, c.oid, operation.privilege);

  if unsafe_grants is not null then
    raise exception 'FAIL: browser write privileges detected: %', unsafe_grants;
  end if;
end $$;

insert into auth.users(id) values
  ('00000000-0000-0000-0000-000000000001'),
  ('00000000-0000-0000-0000-000000000002');
insert into public.profiles(id) select id from auth.users;
insert into public.problems(id,user_id,topic_id,difficulty,problem_latex)
select '10000000-0000-0000-0000-000000000001',
       '00000000-0000-0000-0000-000000000001', id, 1, 'x'
from public.topics where slug='basic-integrals';
insert into public.problems(id,user_id,topic_id,difficulty,problem_latex)
select '10000000-0000-0000-0000-000000000002',
       '00000000-0000-0000-0000-000000000002', id, 2, 'x^2'
from public.topics where slug='basic-integrals';
insert into private.problem_solutions values (
  '10000000-0000-0000-0000-000000000001', 'fixture-v1', '{}', 'x^2/2+C', '[]');
insert into public.attempts(problem_id,user_id,user_answer,is_correct) values
  ('10000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','x^2/2',true),
  ('10000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000002','x^3/3',true);
-- #116: one worksheet per user, each listing that user's problem.
insert into public.worksheets(id,user_id,source,paper,columns,answer_key,groups) values
  ('20000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001',
   'history','a4',1,true,'[]'),
  ('20000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000002',
   'history','a4',1,true,'[]');
insert into public.worksheet_items(worksheet_id,problem_id,position,group_index) values
  ('20000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000001',1,0),
  ('20000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000002',1,0);

do $$ begin
  begin
    insert into public.attempts(problem_id,user_id,user_answer,is_correct) values
      ('10000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001','forged',true);
    raise exception 'FAIL: cross-user attempt accepted';
  exception when foreign_key_violation then null;
  end;
end $$;

set local role authenticated;
set local request.jwt.claim.sub = '00000000-0000-0000-0000-000000000001';
do $$ begin
  assert (select count(*) from public.profiles) = 1, 'profile isolation';
  assert (select count(*) from public.problems) = 1, 'problem isolation';
  assert (select count(*) from public.attempts) = 1, 'attempt isolation';
  assert (select count(*) from public.topics) = 23, 'topic list';
  assert exists (select 1 from public.topics where slug = 'algebraic-expressions' and area = 'algebra'), 'algebraic expressions topic';
  assert exists (select 1 from public.topics where slug = 'polynomial-division' and area = 'algebra'), 'polynomial division topic';
  assert (select count(*) from public.topics where area = 'mathematical-analysis') = 16, 'topic areas';
  assert not exists (select 1 from public.problems where user_id <> auth.uid()), 'owner filter';
  assert (select count(*) from public.worksheets) = 1, 'worksheet isolation';
  assert (select count(*) from public.worksheet_items) = 1, 'worksheet item isolation';
  begin
    update public.worksheets set answer_key = false;
    raise exception 'FAIL: client changed a worksheet';
  exception when insufficient_privilege then null;
  end;
  begin
    perform * from private.problem_solutions;
    raise exception 'FAIL: private solution accessible';
  exception when insufficient_privilege then null;
  end;
  begin
    update public.problems set answer_revealed = true;
    raise exception 'FAIL: client changed reveal flags';
  exception when insufficient_privilege then null;
  end;
  begin
    update public.attempts set is_correct = true;
    raise exception 'FAIL: client changed score';
  exception when insufficient_privilege then null;
  end;
  begin
    insert into public.profiles(id) values ('00000000-0000-0000-0000-000000000003');
    raise exception 'FAIL: client created profile';
  exception when insufficient_privilege then null;
  end;
end $$;

set local request.jwt.claim.sub = '00000000-0000-0000-0000-000000000002';
do $$ begin
  assert (select count(*) from public.problems) = 1, 'second user sees one problem';
  assert not exists (select 1 from public.problems where user_id <> auth.uid()), 'second owner';
  assert not exists (select 1 from public.attempts where user_id <> auth.uid()), 'second attempts';
end $$;

set local request.jwt.claim.sub = '';
do $$ begin
  assert (select count(*) from public.profiles) = 0, 'no-identity profile isolation';
  assert (select count(*) from public.problems) = 0, 'no-identity problem isolation';
  assert (select count(*) from public.attempts) = 0, 'no-identity attempt isolation';
  assert (select count(*) from public.worksheets) = 0, 'no-identity worksheet isolation';
  assert (select count(*) from public.worksheet_items) = 0, 'no-identity item isolation';
end $$;

set local role anon;
do $$ begin
  begin
    perform * from public.problems;
    raise exception 'FAIL: anonymous history access';
  exception when insufficient_privilege then null;
  end;
end $$;

set local role service_role;
do $$ begin
  assert (select count(*) from private.problem_solutions) = 1, 'backend solution access';
  assert (select count(*) from public.problems) = 2, 'service bypass requires API ownership checks';
end $$;
rollback;
\echo 'RLS isolation, write restrictions and private answer tests passed'
