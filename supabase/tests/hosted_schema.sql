-- HUMAN ONLY: run as postgres in the disposable project's SQL Editor after fixtures.
-- Read-only catalogue checks plus one deliberately invalid INSERT, rolled back.
begin;
do $$
declare
  item record;
  browser text;
  operation text;
  a uuid;
  b uuid;
begin
  assert (select count(*) from information_schema.tables where table_schema = 'public'
    and table_name in ('profiles', 'topics', 'problems', 'attempts')) = 4, 'four public MVP tables';
  assert to_regclass('private.problem_solutions') is not null, 'private solutions table';
  assert (select count(*) from pg_indexes where schemaname = 'public' and indexname in (
    'problems_user_created_idx', 'attempts_user_created_idx', 'attempts_problem_idx')) = 3,
    'history and attempt indexes';
  assert exists (select 1 from pg_constraint where conrelid = 'public.attempts'::regclass
    and contype = 'f' and confrelid = 'public.problems'::regclass
    and pg_get_constraintdef(oid) like 'FOREIGN KEY (problem_id, user_id)%'),
    'composite ownership foreign key';
  for item in select c.oid, c.relrowsecurity, n.nspname, c.relname
      from pg_class c join pg_namespace n on n.oid = c.relnamespace
      where n.nspname in ('public', 'private') and c.relkind in ('r', 'p', 'f') loop
    assert item.relrowsecurity, 'RLS required on every application table';
    foreach browser in array array['anon', 'authenticated'] loop
      foreach operation in array array['INSERT', 'UPDATE', 'DELETE', 'TRUNCATE'] loop
        assert not has_table_privilege(browser, item.oid, operation), 'browser write grant';
      end loop;
      if item.nspname = 'private' then
        assert not has_table_privilege(browser, item.oid, 'SELECT'), 'private SELECT grant';
      end if;
    end loop;
  end loop;
  assert not has_schema_privilege('anon', 'private', 'USAGE'), 'anon private schema grant';
  assert not has_schema_privilege('authenticated', 'private', 'USAGE'), 'user private schema grant';
  assert (select rolbypassrls from pg_roles where rolname = 'service_role'), 'service-role bypass';
  foreach operation in array array['SELECT', 'INSERT', 'UPDATE', 'DELETE'] loop
    assert has_table_privilege('service_role', 'private.problem_solutions', operation),
      'backend solution privileges';
  end loop;
  select user_id into strict a from public.problems
    where id = '31000000-0000-0000-0000-000000000001';
  select user_id into strict b from public.problems
    where id = '31000000-0000-0000-0000-000000000002';
  assert a <> b, 'two distinct fixture owners';
  begin
    insert into public.attempts(problem_id, user_id, user_answer, is_correct)
    values ('31000000-0000-0000-0000-000000000002', a, 'forged', true);
    raise exception 'Cross-owner attempt accepted';
  exception when foreign_key_violation then null;
  end;
end $$;
rollback;
-- SQL Editor should report success; this does not prove PostgREST schema exposure or JWT ownership.
