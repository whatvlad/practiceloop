# PracticeLoop agent rules

You are working on PracticeLoop together with a second AI agent as equal collaborators.

The agents have no permanent roles such as “frontend agent” or “backend agent.” Either agent may claim any available task after checking dependencies and receiving confirmation from the accountable human. Never edit the same files concurrently without explicit coordination.

## Before starting work

1. Use a separate clone or worktree.
2. Read AGENTS.md, docs/agents/STATUS.md and docs/agents/WORKFLOW.md. Open the
   other documents only when the task needs them: README.md (setup, commands),
   docs/PRACTICELOOP_MVP.md (original spec, UTF-16), docs/agents/TASK_PROTOCOL.md,
   docs/agents/REVIEW_PROTOCOL.md, docs/agents/HANDOFF.md, and the
   docs/architecture file named in the Issue. docs/agents/archive/ holds handoffs
   of closed Issues; skip it.
3. Run:
   - git status --short --branch
   - git remote -v
   - git fetch origin --prune
4. Inspect current GitHub Issues, open pull requests, ownership, and dependencies.
   Take the next task from the Implementation Queue (see GitHub Issue names):
   the open Issue with the lowest `Order` whose dependencies are done.
5. Do not begin implementation until the accountable human confirms that the selected Issue is available.
6. Record the exact base commit before making changes.

## Collaboration rules

- Both agents are equal collaborators without predefined technical roles.
- One Issue has one active implementation agent and one accountable human.
- Work in your own branch created from the latest main.
- Never implement directly on main.
- Never edit or rewrite the other agent’s branch.
- Do not force-push, rewrite shared history, change repository access, or resolve conflicts by blindly choosing one side.
- Never exchange tokens, passwords, service-role keys, or other secrets through chat.
- GitHub Issues, pull requests, and merged commits are the authoritative shared state.
- AGENTS.md and STATUS.md document rules and status, but they do not provide automatic synchronization.
- Separate ChatGPT chats cannot see or communicate with each other automatically.
- Never claim that the two chats are synchronized unless an actual approved integration exists.
- Coordination between agents happens through:
  1. GitHub Issue or pull-request comments;
  2. HANDOFF messages copied between chats by the accountable human;
  3. published branches, commits, and verified diffs.
- Do not start another AI agent or send messages to another chat without explicit human authorization.
- Keep work limited to the selected Issue and its acceptance criteria.
- Check for overlapping files, migrations, lockfiles, API contracts, and architectural decisions before editing.
- Prefer serial work for database migrations, lockfiles, shared API contracts, and repository-wide configuration.
- Preserve all unrelated and uncommitted work.
- Do not modify the original MVP specification without explicit owner permission.
- Do not expose private answers, generator internals, credentials, or service-role keys to the browser.
- No approval is required: merge your own pull request into main once hosted CI passes.
- Review by the other agent or human is optional; ask for it on database, authentication or mathematical-logic changes.
- Open pull requests as drafts while you are still pushing fixes, and mark them ready for review when done. CI skips the slow Backend, Database isolation and Worksheet TeX jobs on drafts, which saves the repository's billed Actions minutes; merge only after the ready-for-review run is green.

## Keeping token use low

Agent limits are spent mostly by long sessions: every turn re-sends the whole
conversation, including code and logs already read.

- One session per small unit of work: two to four generator families, or one
  phase (design, implementation, PR/CI/merge). Write the plan and progress to a
  file in the branch and start a fresh session (`/clear` in Claude Code, a new
  chat in Codex) for the next unit instead of continuing a long one.
- Local generator sweeps are capped at 50 seeds by `backend/tests/seed_sweep.py`;
  hosted CI (`CI` set) always runs the full counts. Set `PRACTICELOOP_SEEDS=1000`
  only for a final local check.
- Run the narrowest test and keep output short, for example
  `python -m pytest -q -x --tb=short tests/test_engine_<area>.py -k <family> 2>&1 | tail -40`.
  Do not paste full test or CI logs; read only the failing part.
- Narrow runs skip older suites, so before the first push of a pull request run
  `python scripts/pre-push.py` once. It runs ruff, `ruff format --check`, mypy
  and the database tests (`scripts/test-db.py`, README "Local database") with
  one line per step and only the tail of a failure. If it reports `skip`
  for the database, say so in the pull request.
- Do not wait for hosted CI inside a session or poll it in a loop. Push, end the
  turn, and check the result once later.
- Do not open large data files whole. Use
  `python scripts/source-index.py --issue <N>` for the Analysis source matrix.
  `.ignore` keeps `graphify-out/`, test fixtures, the source matrix and lockfiles
  out of search results.
- After a merge, run `python scripts/finish-issue.py <N> --apply` for the project
  steps below instead of separate `gh project` calls.

Coordination record: docs/agents/TASK_PROTOCOL.md. Implementation workflow and
completion criteria: docs/agents/WORKFLOW.md. Receiving a HANDOFF and review
format: docs/agents/REVIEW_PROTOCOL.md. HANDOFF format: docs/agents/HANDOFF.md.

## GitHub Issue names

- An Issue title is short and descriptive. It contains no date and no queue number.
- Every open Issue planned for implementation must be in the GitHub Project
  `PracticeLoop — Implementation Queue`:
  https://github.com/users/whatvlad/projects/1
- Read it with `gh project item-list 1 --owner whatvlad --format json`. This
  needs `gh` signed in with the `project` scope (`gh auth refresh -s project`)
  and an account invited to the project. If you cannot read it, ask the
  accountable human instead of guessing the order.
- The project's `Order` field is the only source of implementation order.
- Set `Order` from dependencies, blockers and product stages, never from
  creation time or the GitHub Issue number.
- After adding an Issue or changing dependencies, check the `Order` values and
  fix them if needed.
- Open Issues in the queue have unique, continuous `Order` values `1…N`.
- Closed Issues are not part of the active queue.
- Keep the project's `Status` field current: `In Progress` when you claim an
  Issue, `Done` when its pull request is merged and the Issue is closed. Then
  remove the closed Issue's `Order` value and renumber the remaining open
  Issues to `1…N` without changing their relative order.
- Other documents (roadmaps, STATUS.md) describe stages and dependencies but
  never override `Order`.
- A large Issue may be split into GitHub sub-issues ("parts"). The project
  adds them automatically; give them `Order` values directly after their
  parent, in the order the parent's "Parts" section lists, and take the first
  open part. After a part merges, run `scripts/finish-issue.py <part> --apply`.
  The deploy/live check runs once, when the parent closes after its last part.

## After a merge

Updating the project is part of the merge, not a later chore. Right after your
pull request is merged, and before you report the task as done, run
`python scripts/finish-issue.py <N>` to see the plan and then with `--apply`.
It does these steps:

1. Close the Issue (or confirm `Closes #N` closed it).
2. Set its project `Status` to `Done` and clear its `Order`.
3. Renumber the remaining open Issues to `1…N`, keeping their relative order.
4. Read the project back and confirm the result.

If you cannot reach the project (for example a 403), do not skip these steps.
Tell the accountable human the task is not Done yet and give them the exact
`gh` commands to run, with the Issue number filled in:

```sh
gh issue close <N>
gh project view 1 --owner whatvlad --format json --jq .id          # <PROJECT_ID>
gh project field-list 1 --owner whatvlad --format json             # Status, Done option, Order ids
gh project item-list 1 --owner whatvlad --format json              # <ITEM_ID> and other Orders
gh project item-edit --project-id <PROJECT_ID> --id <ITEM_ID> --field-id <STATUS_ID> --single-select-option-id <DONE_ID>
gh project item-edit --project-id <PROJECT_ID> --id <ITEM_ID> --field-id <ORDER_ID> --clear
gh project item-edit --project-id <PROJECT_ID> --id <OTHER_ITEM_ID> --field-id <ORDER_ID> --number <NEW_ORDER>   # per renumbered Issue
```

## Graphify

Graphify is optional development tooling for agents. It must not become an
application dependency, production service, container layer or runtime request.

- Install or update it with `scripts/setup-graphify.sh`. The script keeps its
  source and virtual environment under the ignored `.local/` directory.
- Agents do not need Graphify for normal work; plain search is cheaper at this
  repository size. A scoped
  `.local/graphify-venv/bin/graphify query "<question>" --budget 2500` is
  optional for broad architecture questions. Never read `graphify-out/graph.json`
  directly.
- Do not run `graphify update` or commit `graphify-out/` changes in feature
  branches; the Preview workflow rebuilds the published graph on every push to
  `main`.
- Never commit Graphify caches, cost history, interpreter paths or other
  machine-specific state.
