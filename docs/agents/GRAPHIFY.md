# Optional Graphify tooling

Graphify is an agent navigation tool, not an application dependency. Its source,
virtual environment, caches and interpreter markers stay under ignored local
directories. Run setup in each clone/worktree that needs its own graph.

## Setup on Windows

Use Git Bash. The `bash` command on Windows may instead resolve to the Microsoft
Store/WSL alias, which fails when WSL is unavailable. From PowerShell with a
standard Git for Windows installation:

```powershell
& "$env:ProgramFiles/Git/bin/bash.exe" scripts/setup-graphify.sh
```

The script prefers Python 3.12, then 3.13/3.14, matching the project's supported
range. A working newer Python is not sufficient: pinned tree-sitter releases
may have no wheel for it. For example, Python 3.15 selected by the Store alias
attempted to compile tree-sitter 0.25.2 and failed without MSVC. Python 3.12
installs its prebuilt wheel and needs no compiler.

An explicit interpreter executable can be selected without changing global
Python or PATH settings:

```powershell
$env:GRAPHIFY_PYTHON = 'C:/path/to/python3.12/python.exe'
& "$env:ProgramFiles/Git/bin/bash.exe" scripts/setup-graphify.sh
Remove-Item Env:GRAPHIFY_PYTHON
```

An incompatible existing `.local/graphify-venv` is rejected with an actionable
message. Preserve or move that directory aside inside the intended worktree,
then rerun setup. The script does not delete an environment automatically.

Setup installs the pinned Graphify source with its optional SQL parser, so
Supabase migrations/tests contribute schema/function symbols where supported.
No `backend/requirements.txt`, application package, container or service changes.

## Query and refresh

In PowerShell use the supplied command shim explicitly:

```powershell
./.local/graphify-venv/bin/graphify.cmd query 'parse_answer_input IntervalAnswer' --budget 2500
./.local/graphify-venv/bin/graphify.cmd path 'parse_answer_input' 'IntervalAnswer' --undirected
./.local/graphify-venv/bin/graphify.cmd update .
```

In Git Bash/Linux use `.local/graphify-venv/bin/graphify` instead. Use relative
repository paths in shared graph artifacts; do not commit interpreter markers,
HTML previews, caches, cost history or machine-specific timestamps.

The update command rebuilds the structural code graph and a deterministic
document-heading/link layer. It preserves an existing semantic layer but does
not invent one. Semantic interpretation of changed documentation requires the
agent's `/graphify --update` workflow; it is not a prerequisite for fresh code
symbols, headings and links. A zero-token structural build must not be described
as semantic coverage of every sentence.

After changes settle, refresh from that worktree, inspect `built_at_commit`,
and check that relevant symbol locations match the current source. A graph
built with uncommitted changes can describe those files while its commit marker
still names HEAD; record that limitation until the implementation is committed
and the graph is refreshed again. A merge creates another commit without
changing source content, so the marker may name the verified parent commit.

Only selected reviewed `graph.json`, `GRAPH_REPORT.md` and the portable
source-hash manifest belong in Git. Manifest `mtime`/`seen` values are local
optimizations; remove those fields from the shared copy. The next local update
can reconstruct them. No automatic Git hook is installed by this setup, so it
does not change other worktrees' shared Git behavior.

## Verification and limits

```powershell
./.local/graphify-venv/bin/graphify.cmd diagnose multigraph --json
```

Inspect missing/dangling endpoints, collapsed relationships, source paths and
self-loops. Recursive calls can legitimately produce self-loops; report the
count and inspect them instead of silently deleting relationships. Nodes for
external modules need not name repository files. The graph is navigation
evidence: verify relevant results against source, especially domain and privacy
contracts. An extractor warning that a file yielded no symbols does not prove
that its content was semantically covered.
