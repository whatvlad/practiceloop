insert into public.topics(name, slug, area)
values ('Algebraic expressions', 'algebraic-expressions', 'algebra')
on conflict (slug) do update set name = excluded.name, area = excluded.area;
