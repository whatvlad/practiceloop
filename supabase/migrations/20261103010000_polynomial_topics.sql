insert into public.topics(name, slug, area)
values
  ('Binomial theorem', 'binomial-theorem', 'algebra'),
  ('Polynomial roots and factors', 'polynomial-roots', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
