insert into public.topics(name, slug, area)
values
  ('Complex arithmetic and equations', 'complex-arithmetic', 'algebra'),
  ('Polar form and De Moivre''s formula', 'complex-polar-form', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
