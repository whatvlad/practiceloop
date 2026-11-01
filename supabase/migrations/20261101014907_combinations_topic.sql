-- #169: add one new-engine topic without changing existing topic rows or access.
begin;

alter table public.topics drop constraint topics_area_check;
alter table public.topics add constraint topics_area_check
  check (area in ('algebra', 'mathematical-analysis', 'combinatorics'));

insert into public.topics (name, slug, area)
values ('Combinations', 'combinations', 'combinatorics')
on conflict (slug) do nothing;

commit;
