# Connect the second developer and agents

Published target: https://github.com/whatvlad/practiceloop (Private). Until the
infrastructure PR is merged by an authorized human, use the exact branch and
ready-to-send prompt in [CONNECT_AGENT.md](../agents/CONNECT_AGENT.md).

Owner first approves the actual GitHub username and desired role. Invite with
Write access (avoid Admin unless needed); the developer accepts. Add the real
reviewer to .github/CODEOWNERS in a reviewed PR if appropriate. Never use invented
handles. Both humans must be able to review the other's PRs. Test human approval
with an actual small PR; do not let the same human's alternate account stand in
for independent accountability.

After repository publication (substitute the confirmed OWNER):
```powershell
git clone https://github.com/OWNER/practiceloop.git
cd practiceloop
git status --short --branch
git fetch origin --prune
```
Use README to install/check/run. Each developer uses their own Git identity,
GitHub authentication and local .env. Share secrets through an approved secret
manager, never Git, Issues or agent prompts. Google OAuth needs project-level
Supabase/Google setup and correct callback/origin URLs before auth can work.

For two local agents use separate worktrees after main exists:
```powershell
git fetch origin --prune
git worktree add -b feature/issue-123-practice ../practiceloop-codex origin/main
git worktree add -b feature/issue-124-auth ../practiceloop-claude origin/main
```
Substitute real unclaimed Issue numbers; use only the corresponding directory in
each agent. Worktrees share Git objects, not uncommitted files or dependencies.
Between computers use independent clones. Never run both writers in one tree.

## Codex
In the desktop app, open that agent's worktree as the project. CLI, if installed:
```powershell
cd ../practiceloop-codex
codex
```
Sign in using your own account. If CLI is absent, installation documented by
OpenAI is `npm install -g @openai/codex`; installation is a separate owner action.
Prompt: "Read AGENTS.md and relevant ADRs, inspect Git/Issue #123 and dependencies,
confirm ownership, then implement only its acceptance criteria. Report exact tests
and request independent review. Do not publish or merge without authorization."
Codex reads AGENTS.md instructions; verify the task uses the intended checkout.
Sources checked 2026-10-15: [CLI](https://learn.chatgpt.com/docs/codex/cli),
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Claude Code
CLI is already present on the setup machine; no global installation was changed.
```powershell
cd ../practiceloop-claude
claude
```
Sign in separately, ask it to read CLAUDE.md and AGENTS.md and claim its real Issue.
For installation on another machine use the current official
[quickstart](https://code.claude.com/docs/en/quickstart), checked 2026-10-15.
No agent-to-agent daemon, shared credentials, scheduled workers, or automatic
cross-machine synchronization has been installed. Coordinate through Issues/PRs
and explicit handoffs. To cross-review, start the other agent in a separate
checkout of the PR, provide base/head and ask it to follow REVIEW_PROTOCOL.md.
