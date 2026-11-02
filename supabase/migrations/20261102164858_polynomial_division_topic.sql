insert into public.topics(name, slug, area)
values ('Polynomial division', 'polynomial-division', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
