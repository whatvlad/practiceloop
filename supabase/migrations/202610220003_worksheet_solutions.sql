-- #130 (ADR-007 amendment): a worksheet can print worked solutions and graphs.
-- Additive only; existing worksheets keep printing without them.
begin;

alter table public.worksheets
  add column solutions boolean not null default false;

commit;
