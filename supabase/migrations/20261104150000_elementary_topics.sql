-- #235: saved-problem foreign keys need topic rows for these new issuing views.
-- Existing areas, rows/IDs, schema, grants and RLS policies remain unchanged.
insert into public.topics(name, slug, area) values
  ('Logic and propositions', 'logic-and-propositions', 'mathematical-analysis'),
  ('Real inequalities', 'real-inequalities', 'algebra'),
  ('Exponential and logarithmic equations', 'exponential-and-logarithmic', 'mathematical-analysis'),
  ('Trigonometric functions and equations', 'trigonometric-functions', 'mathematical-analysis')
on conflict (slug) do nothing;
