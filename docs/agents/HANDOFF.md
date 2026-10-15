# HANDOFF

After every substantial work stage, prepare a HANDOFF in English:

```text
Agent:
Accountable human:
Issue / PR:
Branch:
Base commit:
Head commit:
Current status:

Scope:
Files changed:
Completed work:
Verification commands and exact results:
Checks not run and why:

Open findings and risks:
Dependencies:
Potential overlap with the other agent:
Uncommitted changes or recovery instructions:

Review status (if requested):
Merge status:

Next concrete action:
Message for the other agent:
```

HANDOFF rules:

- Use exact branch names and full commit hashes.
- Report real commands and observed results, not generic statements such as “tests passed.”
- Clearly distinguish completed, pending, blocked, and unverified work.
- Mention any local-only or uncommitted changes.
- State whether hosted CI was checked.
- Never report the task as Done before all repository completion criteria are satisfied.
- If the other agent needs a message, produce a complete copyable block for the accountable human to transfer.
- Write HANDOFF records in English.
- Conduct normal conversation and explanations in Russian unless the human requests another language.
