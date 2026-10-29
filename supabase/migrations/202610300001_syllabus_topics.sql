-- #147/#145: seed the first Algebra and Mathematical Analysis syllabus topics.
begin;

insert into public.topics(name, slug, area) values
  ('Matrices', 'matrices', 'algebra'),
  ('Complex numbers', 'complex-numbers', 'algebra'),
  ('Fundamental theorem of algebra', 'fundamental-theorem-algebra', 'algebra'),
  ('Partial fractions', 'partial-fractions', 'algebra'),
  ('Functions and sequences', 'functions-and-sequences', 'mathematical-analysis'),
  ('Limits and continuity', 'limits-and-continuity', 'mathematical-analysis'),
  ('Improper integrals', 'improper-integrals', 'mathematical-analysis'),
  ('Series', 'series', 'mathematical-analysis'),
  ('Multivariable functions', 'multivariable-functions', 'mathematical-analysis'),
  ('Differential equations', 'differential-equations', 'mathematical-analysis')
on conflict (slug) do update set name = excluded.name, area = excluded.area;

commit;
