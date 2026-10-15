# Getting started

Repository: https://github.com/whatvlad/practiceloop (private). Each developer
uses their own GitHub account, Git identity and local `.env`. Share secrets
through a password manager, never Git, Issues or agent prompts.

```powershell
git clone https://github.com/whatvlad/practiceloop.git
cd practiceloop
```
Install and verify with the commands in [README](../../README.md).

## Running an agent

Open the clone in Codex or Claude Code and ask it to read `AGENTS.md`. Both
agents follow the same rules and can work on any part of the project.

If two agents run on the same machine at the same time, give each its own
worktree so they never share uncommitted files:
```powershell
git fetch origin --prune
git worktree add -b feature/google-auth ../practiceloop-auth origin/main
git worktree add -b feature/problem-generator ../practiceloop-generator origin/main
```
Between computers use separate clones. Coordinate through Issues and PRs.

Google OAuth needs Supabase/Google project setup and correct callback/origin URLs
before login can work.
