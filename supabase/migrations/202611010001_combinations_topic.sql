-- #169: the first topic served by the new generator engine. Additive only.
begin;

insert into public.topics(name, slug, area) values
  ('Combinations', 'combinations', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;

commit;
