insert into public.topics(name, slug, area)
values ('Matrix operations', 'matrix-operations', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
