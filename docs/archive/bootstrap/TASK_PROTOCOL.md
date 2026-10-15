# Task protocol

One Issue has one accountable human owner and one active implementation agent.
The assignee is the human GitHub account; Codex/Claude identity goes in the body.
Claim by assignment plus a scope comment before implementation. These are not
atomic locks: reread the latest Issue/PR state and resolve simultaneous claims
before editing. Split independent subtasks with explicit file/API boundaries.

Required Issue fields:
```text
Issue ID: #123 (PL-xxx before publication)
Type: Feature | Bug | Documentation | Testing | Infrastructure | Security | Architecture
Priority: P0 | P1 | P2
Agent: Codex | Claude Code | none
Human owner: real account, or Unassigned
Branch: feature/issue-123-short-description
Scope: files/modules and explicit exclusions
Acceptance criteria: observable and testable
Dependencies: Issues / ADRs
Related PRs: links, or none
Status: Backlog | Ready | In Progress | In Review | Blocked | Done
```

Use Issue labels for status if Projects is unavailable. Set exactly one status
label. GitHub Projects status field is optional; if used, keep it consistent.
Do not call a prepared local task an existing GitHub Issue. Map PL IDs to actual
Issue numbers after publishing and include both in descriptions.
