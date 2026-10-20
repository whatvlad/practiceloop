-- #36: targeted feedback code for an incorrect attempt, e.g. 'chain_factor'.
-- Additive only. NULL means no diagnosis; missing_constant keeps its own flag.
-- The code set lives in the backend, so only the shape is constrained here.
begin;

alter table public.attempts
  add column feedback_code text,
  add constraint attempts_feedback_code_shape
    check (feedback_code is null or feedback_code ~ '^[a-z][a-z_]{0,39}$'),
  -- `is false`: an invalid (NULL) or correct attempt never carries a diagnosis.
  add constraint attempts_feedback_code_only_incorrect
    check (feedback_code is null or is_correct is false);

commit;
