# ADR-007: printable PDF worksheets

Date: 2026-10-22. Status: proposed for accountable human Vlad (whatvlad);
accepted when he approves and merges the pull request that adds it. Issue #115.
Vlad decided the four product questions below on 2026-10-22.

Learners can print worksheets: new problems in groups from the Practice page, or
problems they select in History. The server typesets them with real LaTeX into
one PDF with writing space after each problem and the final answers at the end.
The specification's rules still hold: problems come from the verified catalogue,
answers stay private until the learner asks for them, and every problem is a
persisted record. This ADR amends ADR-004 in two places, stated below.

## Product decisions

1. **Worksheet problems are saved.** A generated worksheet persists its problems
   as normal problems, so they appear in History and can be solved online,
   shared and reprinted. Each one carries the worksheet's id, and History has a
   filter for them.
2. **A printed answer key is a reveal.** The request has `answerKey`, on by
   default. When it is on, every problem in the worksheet gets
   `answer_revealed = true` (ADR-004 reveal semantics; `solution_revealed` does
   not change), and the UI says so before the user generates or exports.
3. **A group is a topic and a level**, or Mixed within an area at one level, the
   same choices as the practice selector. Its label in the PDF is the topic name
   and level, for example "Substitution, level 2". The level is the only
   generator parameter a user chooses.
4. **No repeats in a worksheet.** Within one worksheet no record appears twice.
   The picker takes distinct base problems before coefficient variants of the
   same base (the same record with only `coefficient` changed). A group that asks
   for more than its cell offers is capped to the cell size, and the response
   and the UI say how many it got. Adding templates to thin cells is generator
   work outside this ADR.

### Amendment to ADR-004 counters

`generated` counts the user's problems that are not from a worksheet, plus
worksheet problems with at least one attempt. A worksheet of 30 problems
therefore does not inflate the count, and `attempted ≤ generated` stays true.
`attempted` and `correct` keep their meaning, so a worksheet problem solved
online counts like any other. Learning statistics follow the same rule.

## Data

An additive migration adds:

- `public.worksheets(id uuid primary key, user_id uuid not null references
  profiles on delete cascade, created_at timestamptz not null default now(),
  source text not null check (source in ('generate', 'history')),
  paper text not null check (paper in ('a4', 'letter')),
  columns smallint not null check (columns in (1, 2)),
  answer_key boolean not null)`;
- `public.worksheet_items(worksheet_id uuid references worksheets on delete
  cascade, problem_id uuid references problems on delete cascade, position
  smallint not null, group_index smallint not null, primary key (worksheet_id,
  position))`;
- `public.problems.worksheet_id uuid null references worksheets on delete set
  null`, set only for problems a `generate` worksheet created.

Row-level security matches the other learning tables: owners can read their
rows, and browser roles cannot write. No PDF is stored.

## API

### `POST /api/worksheets`

Creates the worksheet in one transaction and returns it as JSON. It requires an
`Idempotency-Key`, like generation.

```json
{
  "source": "generate",
  "groups": [{"topic": "substitution", "difficulty": 2, "count": 5},
             {"topic": "mixed:integrals", "difficulty": 3, "count": 4}],
  "paper": "a4",
  "columns": 1,
  "answerKey": true
}
```

For `"source": "history"` the body has `"problemIds": [...]` instead of `groups`.

- `generate`: the server picks the problems as decision 4 says, inserts them
  with their private solutions, the worksheet and its items, and sets the reveal
  flags if `answerKey` is true.
- `history`: every id must belong to the user, or the whole request fails with
  `404 problem_not_found` (no partial worksheet). The order is the catalogue's
  area and topic order, then level, then oldest first; each topic and level is
  one group. The server sets the reveal flags if `answerKey` is true.

The response lists the groups with their label and the count each one got, the
worksheet id and the problem ids. An exact retry returns the same worksheet.

### `GET /api/worksheets/{id}/pdf`

Renders and returns `application/pdf` with
`Content-Disposition: attachment; filename="mathloop-worksheet-<date>.pdf"`.
It is read-only: it changes no flags, so a failed render is retried safely and
the same worksheet can be downloaded again. It reads `problem_latex` from the
problems and `answer_latex` from the private solutions after checking the
owner, and includes answers only when the worksheet has `answer_key`.

### Limits and errors

- At most 8 groups, 1 to 20 problems per group, 40 problems per worksheet, 40
  ids per History export.
- Rate limits per user: 5 worksheets a minute and 30 an hour for `POST`;
  20 renders a minute for `GET`.
- One compile at a time on the VM. A request that waits more than 10 seconds for
  its turn gets `503 worksheet_busy` (retryable).
- Errors use the existing envelope: `422 invalid_request` (shape, limits,
  unknown topic or level), `404 problem_not_found` (an id that is missing or not
  the user's; also used for a worksheet id), `409 idempotency_conflict`, `429
  rate_limited`, `503 worksheet_busy` and `503 worksheet_render_failed`
  (retryable once; a repeated failure is a bug to report).

## The PDF

- One `.tex` file from a template in the backend. Its only inputs are
  server-generated LaTeX (`problem_latex`, `answer_latex`, the catalogue's text)
  and enum options. Users cannot type text into it; a future title field must be
  escaped before it is added.
- A header with "MathLoop worksheet", the date and blank Name and Date lines.
- One section per group with its label. Problems are numbered 1 to N through the
  whole worksheet, not per group.
- After each problem, blank writing space: the topic's base height times
  `1 + 0.25 × (level − 1)`. Base heights live next to each topic in the catalogue,
  so a new topic must declare one: basic and derivatives 3 cm; substitution and
  partial derivatives 4 cm; parts, rational and trigonometric 5 cm; double 6 cm;
  triple 7 cm. A problem and its space are kept on one page.
- Options: paper A4 or Letter, one or two columns (two columns halve the width,
  not the height).
- With the answer key on: `\clearpage`, then "Answers", in two columns in a
  smaller size, numbered like the problems. Final answers only, never steps. It
  usually fits one page; long answers may move to a second one.

## TeX runtime

- TeX Live from Ubuntu packages on the Oracle VM: `texlive-latex-base`,
  `texlive-latex-recommended`, `texlive-fonts-recommended` (amsmath, amssymb,
  geometry, multicol, Latin Modern; about 300 MB). `deploy/oracle/bootstrap.sh`
  installs them. The deploy user cannot install packages, so Vlad runs the
  install once over SSH. Tectonic is rejected because it downloads its bundle at
  run time.
- One `pdflatex` pass, with no cross-references that would need a second.
- The compile runs in a fresh child process in a new temporary directory, like
  the math worker: `-no-shell-escape -interaction=nonstopmode -halt-on-error`,
  `openin_any=p` and `openout_any=p`, `RLIMIT_CPU` 10 s, `RLIMIT_AS` 512 MB,
  `RLIMIT_FSIZE` 5 MB, a 20-second wall-clock limit, and the directory is deleted
  afterwards in every case. The log never reaches the response.
- Statements and answers are written for KaTeX. CI installs the same packages
  and compiles every catalogue statement and answer once, so a macro that only
  KaTeX knows fails CI before it reaches a worksheet.

## UI

- Practice: a "Print worksheet" section at the bottom with groups (topic, level,
  count), add and remove, page options and the answer-key option. It shows the
  cap of decision 4 before generating, and says that the problems are saved to
  History and, with the key, are marked as revealed.
- History: a checkbox on each row, "Select all" for the loaded rows under the
  current filter, a bar with the count and "Export PDF", and a filter for
  worksheet problems. The 40-problem limit is shown when it is reached.

## Delivery

| Issue | Delivers | Depends on |
|---|---|---|
| #116 | Migration, both endpoints, picker, template, sandboxed compiler, CI compile test, TeX on the VM | this ADR |
| #117 | Practice group builder | #116 |
| #118 | History multi-select, export and worksheet filter | #116 |

## Implementation notes (#116, 2026-10-22)

Details the build settled within this ADR:

- `public.worksheets` also stores `groups jsonb`: each group as requested and as
  filled (`topic`, `difficulty`, `requested`, `count`). A mixed group's problems
  carry the drawn topic, so its label cannot be rebuilt from the problems.
  `worksheet_items` is unique per `(worksheet_id, problem_id)`.
- No record repeats across the whole worksheet: groups take from a shared cell in
  request order, and a group that finds nothing left gets `count: 0` and no
  section in the PDF. `GET /api/topics` publishes each cell's size as
  `worksheetCapacity`, so the UI shows the cap before generating.
- `GET /api/problems` items carry `worksheetId`, and `?worksheet=true` lists only
  worksheet problems, which is History's filter.
- The PDF header date and the file name use the worksheet's creation date, so a
  reprint is the same document. Template, compiler and limits:
  `backend/app/services/worksheet_pdf.py` and `tex_worker.py`.
- `lmodern` is installed explicitly: on Ubuntu it is only a recommendation of
  `texlive-fonts-recommended`.

## Amendment: worked solutions and graphs (#130, 2026-10-22)

Vlad asked for the worked solutions and graphs in the PDF, which the first
version left out. This amendment brings both in:

- The request has `solutions` (default `false` in the API, on by default in the
  UI), stored as `public.worksheets.solutions` by an additive migration. A
  printed solution is a solution reveal (ADR-004): every included problem gets
  `answer_revealed = true` and `solution_revealed = true` when the worksheet is
  created, with or without the answer key, and the UI says so first.
- The PDF ends with "Solutions" on a new page, after the answers: each problem's
  number, statement and its stored steps (the catalogue's step text, escaped,
  and the step LaTeX), and a graph when its version has an ADR-006 visual.
- Graphs are drawn from the same server-built spec as the site, without a TeX
  package: lines and fills are PDF operators in pdfTeX's `\pdfliteral`, labels
  are LaTeX in the kernel's picture environment, so the VM needs nothing beyond
  the packages above (TikZ is not installed there). The kinds: `definite` (curve,
  shaded area, bounds), `indefinite` (f solid, F dashed with C = 0, marked
  points), `region2d` (the region in the plane; the surface stays online) and
  `solid3d` (a wireframe in a fixed oblique view). Derivatives have none.
- A first spec build costs up to about a second of CPU; one render stops
  building graphs after 12 s and prints the remaining problems without one. A
  graph that fails is logged and left out; it never fails the PDF.
- CI compiles every catalogue step and a graph of every visual version and level.

Code: `backend/app/services/worksheet_graphs.py` and `worksheet_pdf.py`.

## Out of scope

Free-text titles or other user-written LaTeX, stored PDFs, the 3D surface of a
double integral in the PDF, saved worksheet templates and selecting all of
History beyond the loaded pages.
