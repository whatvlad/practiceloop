insert into public.topics(name, slug, area)
values
  ('Determinants', 'determinants', 'algebra'),
  ('Inverse matrices', 'inverse-matrices', 'algebra'),
  ('Systems of linear equations', 'linear-systems', 'algebra'),
  ('Matrix rank', 'matrix-rank', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
