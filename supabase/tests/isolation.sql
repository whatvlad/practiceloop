\set ON_ERROR_STOP on
begin;
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
  assert (select count(*) from public.topics) = 5, 'topic list';
  assert not exists (select 1 from public.problems where user_id <> auth.uid()), 'owner filter';
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
