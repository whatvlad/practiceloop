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

# Use the project's supported Python range. A newer Store/launcher default can
# import sys while still lacking wheels for Graphify's pinned tree-sitter ABI.
# An explicit executable path also works when Windows paths contain spaces.
python_cmd=()
supported_python='import sys; raise SystemExit(not ((3, 12) <= sys.version_info[:2] < (3, 15)))'
if [[ -n "${GRAPHIFY_PYTHON:-}" ]]; then
  python_cmd=("$GRAPHIFY_PYTHON")
  if ! "${python_cmd[@]}" -c "$supported_python" >/dev/null 2>&1; then
    echo "GRAPHIFY_PYTHON must name a Python 3.12-3.14 executable." >&2
    exit 1
  fi
fi
for candidate in python3.12 python3.13 python3.14 "py -3.12" "py -3.13" "py -3.14" python3 python; do
  if [[ ${#python_cmd[@]} -gt 0 ]]; then
    break
  fi
  if $candidate -c "$supported_python" >/dev/null 2>&1; then
    read -r -a python_cmd <<<"$candidate"
    break
  fi
done
if [[ ${#python_cmd[@]} -eq 0 ]]; then
  echo "Python 3.12-3.14 was not found. Install it or set GRAPHIFY_PYTHON to its executable and retry." >&2
  exit 1
fi

# Windows venvs keep executables in Scripts\ instead of bin/.
if [[ ! -x "$venv_dir/bin/python" && ! -x "$venv_dir/Scripts/python.exe" ]]; then
  "${python_cmd[@]}" -m venv "$venv_dir"
fi

if [[ -x "$venv_dir/Scripts/python.exe" ]]; then
  venv_python="$venv_dir/Scripts/python.exe"
else
  venv_python="$venv_dir/bin/python"
fi
if ! "$venv_python" -c "$supported_python" >/dev/null 2>&1; then
  echo "The existing .local/graphify-venv uses unsupported Python. Move it aside and rerun this script with Python 3.12-3.14." >&2
  exit 1
fi

if [[ -x "$venv_dir/Scripts/python.exe" ]]; then
  "$venv_dir/Scripts/python.exe" -m pip install --upgrade "$source_dir[sql]"
  # Shims so the documented .local/graphify-venv/bin/graphify path (AGENTS.md,
  # .codex/hooks.json) works from Git Bash, PowerShell and cmd.
  mkdir -p "$venv_dir/bin"
  printf '#!/bin/sh\nexec "$(dirname "$0")/../Scripts/graphify.exe" "$@"\n' \
    >"$venv_dir/bin/graphify"
  chmod +x "$venv_dir/bin/graphify"
  printf '@"%%~dp0..\\Scripts\\graphify.exe" %%*\r\n' >"$venv_dir/bin/graphify.cmd"
else
  "$venv_dir/bin/python" -m pip install --upgrade "$source_dir[sql]"
fi

"$venv_dir/bin/graphify" update "$repo_root"

printf 'Graphify is ready. Query it with:\n  %s query "your question"\n' \
  "$venv_dir/bin/graphify"
