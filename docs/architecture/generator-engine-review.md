# GrillMe review of the generator engine (#172)

Date: 2026-11-01. Accountable human: Vlad (whatvlad), who accepted every
decision below in the #172 interview. Input: the
[ADR-008 draft](../decisions/0008-generator-engine.md) (#171) and the engine on
main at `925b630` (#163-#170).

## Verdict

The four layers (blocks, answers, generators, topics), typed `Answer.check`,
the frozen PRNG v1, problem codes and the golden and seed-sweep tests stay.
They fit Algebra and Analysis as shown by partial fractions → indefinite →
definite integrals and by combinations, and Probability and Statistics need
only new blocks and answer kinds, not a new layer.

The generator interface is simplified once before any further migration
(#189). The product side of a topic, now seven edits, becomes one declarative
entry (#191), and symbolic topics are issued from a catalogue built at deploy
(#192). After #189 the core interfaces are frozen.

## Decisions

Each finding refers to the ADR-008 draft's known limitations (L) and open
decisions (Q).

| # | Finding | Resolution | Reason | Issue |
|---|---|---|---|---|
| 1 | `draw` returns only the seed, so parameters are untyped and level filters cannot use them (L3, Q1) | **Simplified**: `draw(seed)` returns the drawn values as typed `Parameters`; `build` is pure over them | Typed parameters are what the protocol promised; the PRNG call order stays, so every v1 code and golden entry is unchanged | #189 |
| 2 | Prefix, family and code version are written twice; `code()` builds a throwaway registry (L2, Q2) | **Simplified**: they are attributes of the generator class, read by the registry and `code()` | One source of truth; a mismatch becomes impossible instead of caught by golden tests | #189 |
| 3 | Composition rebuilds the inner task from the same seed and reads it through `isinstance` and `metadata` (L7, Q3) | **Simplified**: an outer generator's parameters hold the inner generator's parameters; the inner generator exposes a typed result | Makes the dependency an interface, not a shared-PRNG convention; needed by every composed family (integrals, multiple integrals) | #189 |
| 4 | Topic predicates re-run a generator's first PRNG draw (L4) | **Simplified**: predicates read the typed parameters from decision 1 | A draw-order change can no longer silently move tasks between levels | #189 |
| 5 | A seed whose `build` raises is not redrawn (L5, Q4) | **Kept with a guard**: every seed of a shipped version must build; the topic takes the next candidate within the 64-draw cap and logs it | The guarantee stays testable (1,000-seed sweep), and a rare miss is not a learner-facing error | #189 |
| 6 | Issuing runs SymPy in the API process (L6, Q5) | **Deferred to a deploy-time catalogue**: pools of verified codes per topic × level; issuing only picks; integer-only topics may build on request; no symbolic engine topic is issued before that | Already the main goal of #162; removes cold-cell latency and unbounded SymPy from requests | #192 |
| 7 | Serving a topic touches about seven places (L1, Q6) | **Simplified**: one declarative engine topic entry drives the API topic list, step text and visuals; the frontend reads topics from the API; the Supabase `topics` row stays a separate additive migration | Records reference the `topics` row, so it cannot be generated; everything else can | #191 |
| 8 | Engine areas differ from public areas (L8) | **Simplified**: engine topics use only the public areas (`algebra`, `mathematical-analysis`, later `probability-statistics`) | One vocabulary for areas | #191 |
| 9 | Engine and legacy version strings overlap (`definite-v1`) (L9, Q7) | **Kept**: records route by the `code` key | Engine versions only appear next to a code; renaming would change shipped golden data for no gain | #189 |
| 10 | Step text lives in `engine/practice.py` (Q8) | **Simplified**: each generator declares its step keys with English text in its own file; a test requires text for every served key; no translation until the app has i18n | Keeps a task type in one file | #189 |
| 11 | Matrix, vector, interval, set, boolean answers and the `IntegerDetMatrix` and `Distribution` blocks are not designed (Q9) | **Deferred**: each new answer kind (`Answer` class plus input UI) or block is designed as the first step of the issue that needs it | Designing without a consumer risks the wrong shape; the `Answer` protocol already allows new kinds without engine edits | #196, #197, #200, #145-#147 |
| 12 | Which interfaces are stable (Q10) | **Kept after #189**: `Answer`, `Outcome`, `Task`, `TaskGenerator`, `Topic`, PRNG v1 and the code format are frozen once #189 lands; later changes need an ADR-008 amendment | Migrating twenty topics against moving interfaces would multiply rework | #189 |
| 13 | `combinations` is outside mixed practice and worksheets (L12) | **Deferred**: it joins mixed practice with #191 and worksheets with #192 | Worksheets draw from pools, which #192 creates | #191, #192 |
| 14 | A CI test pins the SHA-256 of `app/generators` (#170) | **Removed** in this review's pull request | Its purpose was "no legacy edits before the review"; old topics stay covered by their own tests, and migrations will delete legacy modules | this PR |
| 15 | No public registry listing; answers import the private `math_worker._build_sympy` (L10, L11) | **Deferred** to the cleanup | Harmless until the legacy services move | #189 (listing), #199 (services) |
| 16 | Slice scope: few levels, no `/p/<code>` page, Windows-only worker test failure (L12, L13) | **Deferred** to the migrations and #198; the worker test stays Linux-only | Scope, not design | #193-#198 |

## Remaining refactor, in Order

| Order | Issue | Depends on |
|---|---|---|
| 1 | #189 Rework the generator engine core | #172 |
| 2 | #190 Keep old saved problems as a read-only archive | #172 |
| 3 | #191 Declare engine topics once, topic list from the API | #189 |
| 4 | #192 Verified problem catalogue at deploy | #189, #191 |
| 5 | #193 Integral topics on the engine | #189-#192 |
| 6 | #194 Multiple integral topics | #189-#192 |
| 7 | #195 Derivative topics | #189-#192 |
| 8 | #196 Algebra topics | #189-#192 |
| 9 | #197 Remaining analysis topics | #189-#192 |
| 10 | #198 `/p/<code>` page | #189, #191 |
| 11 | #199 Remove legacy generators, final ADR-008 | #190, #193-#197 |

New content stays in #147, #145 and #146 (now also depending on #189, #191 and
#192), and Probability and Statistics is #200.
