#!/usr/bin/env bash
# One-time setup for running the Linux-only backend checks from Windows (#297).
#
# Run inside WSL (Ubuntu 24.04), from any folder: no sudo needed.
#   wsl bash scripts/setup-wsl-tests.sh
# Installs into ~/.local/share/practiceloop (outside the repository):
#   venv/      Python 3.12 with backend/requirements.txt, built by uv
#   postgres/  PostgreSQL 17 from apt.postgresql.org, unpacked, not installed
# scripts/pre-push.py and scripts/test-db.py --wsl then use them.
set -euo pipefail

PG_VERSION="17.11-1.pgdg24.04+2"
PG_POOL="https://apt.postgresql.org/pub/repos/apt/pool/main/p/postgresql-17"
LIBPQ_VERSION="18.6-1.pgdg24.04+2"
LIBPQ_POOL="https://apt.postgresql.org/pub/repos/apt/pool/main/p/postgresql-18"
HOME_DIR="${HOME}/.local/share/practiceloop"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "${HOME_DIR}"
if ! command -v uv >/dev/null && [ ! -x "${HOME}/.local/bin/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh
  sh /tmp/uv-install.sh --quiet
fi
UV="$(command -v uv || echo "${HOME}/.local/bin/uv")"
"${UV}" venv --quiet --allow-existing --python 3.12 "${HOME_DIR}/venv"
"${UV}" pip install --quiet --python "${HOME_DIR}/venv/bin/python" \
  -r "${ROOT}/backend/requirements.txt"

if [ ! -x "${HOME_DIR}/postgres/usr/lib/postgresql/17/bin/initdb" ]; then
  work="$(mktemp -d)"
  trap 'rm -rf "${work}"' EXIT
  for deb in \
    "${PG_POOL}/postgresql-17_${PG_VERSION}_amd64.deb" \
    "${PG_POOL}/postgresql-client-17_${PG_VERSION}_amd64.deb" \
    "${LIBPQ_POOL}/libpq5_${LIBPQ_VERSION}_amd64.deb"; do
    curl -fsSL -o "${work}/package.deb" "${deb//+/%2B}"
    dpkg-deb -x "${work}/package.deb" "${HOME_DIR}/postgres"
  done
fi
missing="$(LD_LIBRARY_PATH="${HOME_DIR}/postgres/usr/lib/x86_64-linux-gnu" \
  ldd "${HOME_DIR}/postgres/usr/lib/postgresql/17/bin/postgres" | grep 'not found' || true)"
if [ -n "${missing}" ]; then
  echo "PostgreSQL needs system libraries that are missing:" >&2
  echo "${missing}" >&2
  exit 1
fi
echo "WSL test setup ready in ${HOME_DIR}"
