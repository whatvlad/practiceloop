insert into public.topics(name, slug, area)
values ('Converting complex forms', 'complex-conversion', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
