-- #144: retain topic slugs while moving all shipped calculus into Mathematical Analysis.
begin;

alter table public.topics drop constraint topics_area_check;
update public.topics set area = 'mathematical-analysis'
  where area in ('integrals', 'derivatives');
alter table public.topics
  add constraint topics_area_check check (area in ('algebra', 'mathematical-analysis'));

commit;
