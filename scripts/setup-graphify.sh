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

if [[ ! -x "$venv_dir/bin/python" ]]; then
  python -m venv "$venv_dir"
fi

"$venv_dir/bin/python" -m pip install --upgrade "$source_dir"
"$venv_dir/bin/graphify" update "$repo_root"

printf 'Graphify is ready. Query it with:\n  %s query "your question"\n' \
  "$venv_dir/bin/graphify"
