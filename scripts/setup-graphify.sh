#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
source_dir="$repo_root/.local/graphify-source"
venv_dir="$repo_root/.local/graphify-venv"
graphify_repo="https://github.com/Graphify-Labs/graphify.git"
graphify_ref="v0.9.92"

if [[ ! -d "$source_dir/.git" ]]; then
  git clone --depth 1 --branch "$graphify_ref" "$graphify_repo" "$source_dir"
else
  git -C "$source_dir" fetch --depth 1 origin "refs/tags/$graphify_ref:refs/tags/$graphify_ref"
  git -C "$source_dir" checkout --detach "$graphify_ref"
fi

# Pick a working Python: "python" may be missing or, on Windows, the Store stub.
python_cmd=()
for candidate in python3 python "py -3"; do
  if $candidate -c 'import sys' >/dev/null 2>&1; then
    read -r -a python_cmd <<<"$candidate"
    break
  fi
done
if [[ ${#python_cmd[@]} -eq 0 ]]; then
  echo "Python 3 was not found. Install it from https://www.python.org/ and retry." >&2
  exit 1
fi

# Windows venvs keep executables in Scripts\ instead of bin/.
if [[ ! -x "$venv_dir/bin/python" && ! -x "$venv_dir/Scripts/python.exe" ]]; then
  "${python_cmd[@]}" -m venv "$venv_dir"
fi

if [[ -x "$venv_dir/Scripts/python.exe" ]]; then
  "$venv_dir/Scripts/python.exe" -m pip install --upgrade "$source_dir"
  # Shims so the documented .local/graphify-venv/bin/graphify path (AGENTS.md,
  # .codex/hooks.json) works from Git Bash, PowerShell and cmd.
  mkdir -p "$venv_dir/bin"
  printf '#!/bin/sh\nexec "$(dirname "$0")/../Scripts/graphify.exe" "$@"\n' \
    >"$venv_dir/bin/graphify"
  chmod +x "$venv_dir/bin/graphify"
  printf '@"%%~dp0..\\Scripts\\graphify.exe" %%*\r\n' >"$venv_dir/bin/graphify.cmd"
else
  "$venv_dir/bin/python" -m pip install --upgrade "$source_dir"
fi

"$venv_dir/bin/graphify" update "$repo_root"

printf 'Graphify is ready. Query it with:\n  %s query "your question"\n' \
  "$venv_dir/bin/graphify"
