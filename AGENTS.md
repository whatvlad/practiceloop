# PracticeLoop agent rules

You are working on PracticeLoop together with a second AI agent as equal collaborators.

The agents have no permanent roles such as “frontend agent” or “backend agent.” Either agent may claim any available task after checking dependencies and receiving confirmation from the accountable human. Never edit the same files concurrently without explicit coordination.

## Before starting work

1. Use a separate clone or worktree.
2. Read these files in full:
   - AGENTS.md
   - README.md
   - docs/PRACTICELOOP_MVP.md
   - docs/agents/STATUS.md
   - docs/agents/WORKFLOW.md
   - docs/agents/TASK_PROTOCOL.md
   - docs/agents/REVIEW_PROTOCOL.md
   - docs/agents/HANDOFF.md
3. Run:
   - git status --short --branch
   - git remote -v
   - git fetch origin --prune
4. Inspect current GitHub Issues, open pull requests, ownership, and dependencies.
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

Coordination record: docs/agents/TASK_PROTOCOL.md. Implementation workflow and
completion criteria: docs/agents/WORKFLOW.md. Receiving a HANDOFF and review
format: docs/agents/REVIEW_PROTOCOL.md. HANDOFF format: docs/agents/HANDOFF.md.
