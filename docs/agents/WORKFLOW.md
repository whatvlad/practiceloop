# Implementation workflow

1. Confirm that the Issue is unclaimed and its dependencies are complete.
2. Confirm the accountable human and implementation agent.
3. Update local remote references.
4. Start from the latest accepted main.
5. Create a branch using the repository naming convention.
6. Implement only the Issue acceptance criteria.
7. Reuse existing repository patterns before adding abstractions or dependencies.
8. Run the actual verification commands documented in README.md.
9. Inspect the complete diff against the base commit.
10. Check formatting, types, tests, security boundaries, migrations, dependencies, and secret exposure.
11. Update relevant documentation when behavior, APIs, migrations, or decisions change.
12. Create a focused pull request only when authorized by the accountable human.
13. Optionally request review from the other agent or human (recommended for database, authentication and mathematical logic).
14. Merge the pull request into main yourself once hosted CI passes.

## Completion criteria

A task is Done only when:

- the Issue acceptance criteria are satisfied;
- the implementation matches the MVP and accepted architecture;
- relevant tests, formatting, type checks, security checks, and migration checks pass;
- documentation is current;
- hosted CI passes;
- blocking review findings, if any were raised, are resolved;
- the pull request is merged into main;
- the Issue is closed.

If any condition is missing, report the exact remaining state and do not call the task Done.
