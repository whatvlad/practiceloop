-- #128: a Definite integrals topic in the Integrals area. Additive only: it
-- holds the definite variants of the single-integral topics, which keep theirs,
-- so existing problems, attempts and statistics keep their meaning.
begin;

insert into public.topics(name, slug, area) values
  ('Definite integrals', 'definite-integrals', 'integrals')
on conflict (slug) do nothing;

commit;
