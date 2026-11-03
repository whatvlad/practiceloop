-- Additive topic only: saved engine records and original integrals stay unchanged.
insert into public.topics(name, slug, area)
values ('Differential calculus', 'differential-calculus', 'mathematical-analysis')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
