# Computational contracts and Graphify checkpoint

Agent: Codex. Accountable human: Vlad / whatvlad.
Issue / PR: #234 / #245. Branch: `codex/issue-234-structured-answers`.
Base commit: `858004eace1455fed2c04485572e8dac0e73ce2b`.
Implementation head: `157a662a012d40420df09569079fc172a7b5608d`.
Tooling commit: `b8180ccbd5716fea4f4482fafe7ecc252759eaba`.
This checkpoint follows the implementation with graph/handoff documentation;
the PR records the final head and subsequent hosted outcomes.
Status at this checkpoint: implemented and locally checked; full backend run,
ready hosted CI, merge, deploy/live checks and Project maintenance pending.
This record is not a Done claim.

## Scope and result

Implemented opt-in plain InputContract metadata, bounded full real sets/unions/
exclusions, ordered nested results, named categories, local real/positive/integer
formula symbols, tagged finite/infinite/nonexistent limits and canonical periodic
base-set checking. Python/browser grammars share one aggregate budget. Expected
values never enter the public contract. Original answer grammars, 239 shipped
versions, engine protocols and production worker limits remain unchanged.

New optional solution_visual helpers build bounded labelled 2D geometry from
the same frozen code/draw during catalogue publication. The private stored
rendered variant retains the model alongside its answer/steps. Reveal reads a
detached copy; arbitrary out-of-pool codes use the bounded code-opening worker.
Browser/worksheet views retain paths, arrows and endpoint inclusion. No new
topic or curriculum coverage is claimed. Mathematical family completeness and
remaining custom representations are explicitly assigned to #235-#242.
Learner proof/sketch/graph grading remains #244; worksheet redesign remains #181.

Files: math_input contracts/parser, computational answer policies, engine
rendering/catalogue/practice, worker input boundary, private visuals/worksheet
rendering, frontend safe metadata/parser/controls/visuals, tests and architecture
documentation. No app dependency, lockfile, migration, MVP or other worktree edits.
`.venv-linux/` is ignored for optional Linux tests.

## Graphify, explicitly delegated by the owner

The parallel tooling agent used a separate worktree/branch, then coordinated
exclusive graph-output ownership in this worktree. The root agent inspected
and cherry-picked its tooling-only commit. No runtime files were delegated.

Root cause: setup selected Python 3.15, which lacked the pinned tree-sitter
Windows wheel and fell back to an unavailable MSVC compiler. The default bash
also resolved to the Windows Store/WSL alias. Fixed setup prefers Python
3.12-3.14, accepts an explicit executable override, rejects incompatible venvs
and includes SQL grammar extraction. Windows commands are in GRAPHIFY.md.
The standard setup was actually run successfully in this worktree.

Final source graph: 4,527 nodes, 14,187 edges, 229 communities; provenance
`157a662a012d40420df09569079fc172a7b5608d`. All 467 manifest content hashes
match current sources. Query checks for FormulaAnswer/InputContract/validate_plot
and parser/contract/checker paths pass. Diagnostics: zero missing, dangling or
collapsed edges. Thirty call self-loops are retained as recursion evidence.
Code AST plus deterministic document headings/links were refreshed; no semantic
LLM extraction is claimed. Token cost: zero. Shared outputs contain relative
source paths and no interpreter/cache paths or manifest mtime/seen timestamps.

The upstream updater skips writing unchanged topology and leaves its old commit
stamp even with --force. After independently checking clean committed source,
manifest hashes and seven key files against git show, the graph agent advanced
only the provenance stamp to the verified implementation commit; report and JSON
agree. Topology/doc overlay were not relabelled or fabricated. Detailed local
audit evidence remains ignored, rather than publishing machine state.

## Observed verification

- Frontend: `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`
  passed: 37 files / 679 tests. Existing large-chunk build and jsdom canvas
  notices are warnings, not failed tests.
- Windows Python: ruff check and ruff format --check across app/tests/scripts
  pass; `mypy --platform linux` passes for all 130 source files. Repository
  policy/protected MVP hash and git diff --check pass.
- Golden subset: 733 passed, 444 deselected; every shipped golden rendering
  remains unchanged. Deselected tests include the separate long seed sweep.
- Native Linux: selected computational answer/API/probability API/math-worker
  suites: 95 passed. Includes the temporary extension provider's actual limited
  child and existing resource/reaping checks; no production limit was raised.
- The first WSL run from /mnt/c failed wall limits even on the pre-existing x
  parser test because cold imports were slow. The same tests passed on native
  Linux storage. The separate native source copy preserves the code under test;
  OS packages and application requirements were not changed.
- Local headless Edge fixture: ordered input/edit serialization, pre-reveal
  visual absence, reveal rendering and path visibility pass; desktop 1100 px
  and mobile 390 px screenshots inspected. No page errors or mobile overflow.
  This isolated frontend fixture is ignored and is not a production feature.

Full backend/seed/pool suite is running separately on native Linux. Hosted CI
and deployment results must be read from #245 after this checkpoint; they are
not assumed from local tests. Database isolation is verified by its hosted job;
no local Docker is configured. Native TeX remains disabled under #181.

## Review, recovery and next action

Runtime work is self-reviewed, not independently reviewed. Mathematical-contract
review is advisory and welcome, especially exact set/domain semantics and family
completeness boundaries. The tooling agent independently diagnosed Graphify only.
There are no unresolved acceptance findings claimed fixed without evidence.

Worktree: `C:/PracticeLoop/.worktrees/issue-234`. Other branches and uncommitted
work were preserved. Local venvs, code catalogue, browser fixture/screenshots,
Graphify source/cache/diagnostics and Linux test paths remain ignored. The
published commits are recoverable from the PR branch; no force push was used.

Next: read full backend outcome, finish ready hosted CI, merge #245 only when
green, verify deploy/live behavior, close #234, set Project Done/clear Order,
renumber remaining open Orders and read back. Only then proceed to #235.
Consult the final PR/Issue state rather than interpreting this checkpoint's
pending status as an up-to-date task synchronization record.
