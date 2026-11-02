insert into public.topics(name, slug, area)
values
  ('Eigenvalues and eigenvectors', 'eigenvalues', 'algebra'),
  ('Vectors, areas and volumes', 'vectors', 'algebra'),
  ('Lines and planes', 'lines-and-planes', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
