-- #98 (ADR-005): practice has two areas, Integrals and Derivatives. Additive
-- only: the five existing topics keep their ids and get the integrals area, so
-- existing problems, attempts and statistics keep their meaning. The new topics
-- are seeded once here; the API offers a topic only when its generator ships.
begin;

alter table public.topics
  add column area text not null default 'integrals'
  check (area in ('integrals', 'derivatives'));
alter table public.topics alter column area drop default;

insert into public.topics(name, slug, area) values
  ('Double integrals', 'double-integrals', 'integrals'),
  ('Triple integrals', 'triple-integrals', 'integrals'),
  ('Derivatives', 'derivatives', 'derivatives'),
  ('Partial derivatives', 'partial-derivatives', 'derivatives')
on conflict (slug) do nothing;

commit;
