-- #200: the approved third practice area and its nine topics. Existing rows/IDs stay.
alter table public.topics drop constraint topics_area_check;
alter table public.topics add constraint topics_area_check
  check (area in ('algebra', 'mathematical-analysis', 'probability-statistics'));

insert into public.topics(name, slug, area) values
  ('Events and counting', 'probability-events', 'probability-statistics'),
  ('Conditional probability and Bayes', 'conditional-probability', 'probability-statistics'),
  ('Discrete random variables', 'discrete-random-variables', 'probability-statistics'),
  ('Standard discrete distributions', 'discrete-distributions', 'probability-statistics'),
  ('Continuous distributions', 'continuous-distributions', 'probability-statistics'),
  ('Moments and joint distributions', 'moments-joint-distributions', 'probability-statistics'),
  ('Descriptive statistics', 'descriptive-statistics', 'probability-statistics'),
  ('Confidence intervals', 'confidence-intervals', 'probability-statistics'),
  ('Hypothesis tests', 'hypothesis-tests', 'probability-statistics')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
