#!/usr/bin/env bash
# Activates an uploaded release; run by the Backend deploy workflow as the practiceloop user:
#   bash /opt/practiceloop/releases/<id>/deploy/oracle/release.sh <id>
# If the new release fails its health check, the previous one is restored.
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/practiceloop}"
KEEP=5
id="$1"
release="$APP_ROOT/releases/$id"
[[ -d $release/backend ]] || { echo "No release at $release" >&2; exit 1; }

healthy() {
  for _ in $(seq 1 30); do
    curl -fsS --max-time 2 http://127.0.0.1:8000/health >/dev/null 2>&1 && return 0
    sleep 1
  done
  return 1
}

activate() {
  ln -sfn "$1" "$APP_ROOT/current.next"
  mv -Tf "$APP_ROOT/current.next" "$APP_ROOT/current"
  sudo -n /usr/bin/systemctl restart practiceloop-api
}

echo "==> Installing dependencies for $id"
python3.12 -m venv "$release/.venv"
"$release/.venv/bin/pip" install --quiet --disable-pip-version-check -r "$release/backend/requirements.txt"

echo "==> Building verified engine catalogue for $id"
(cd "$release/backend" && "$release/.venv/bin/python" -m app.engine.catalogue)

previous="$(readlink -f "$APP_ROOT/current" || true)"
echo "==> Starting $id"
activate "$release"
if ! healthy; then
  echo "Release $id failed its health check." >&2
  if [[ -n $previous && -d $previous && $previous != "$release" ]]; then
    echo "Restoring $(basename "$previous")." >&2
    activate "$previous"
    healthy || echo "The previous release is not healthy either." >&2
  fi
  exit 1
fi
if [[ -n $previous && -d $previous && $previous != "$release" ]]; then
  ln -sfn "$previous" "$APP_ROOT/previous"
fi
echo "==> $id is live"

# Keep the newest releases, plus whatever current and previous point to.
keep_current="$(readlink -f "$APP_ROOT/current")"
keep_previous="$(readlink -f "$APP_ROOT/previous" 2>/dev/null || true)"
# Release ids are hex and digits only, so ls is safe here.
# shellcheck disable=SC2012
ls -1dt "$APP_ROOT"/releases/*/ | tail -n +$((KEEP + 1)) | while read -r old; do
  old="${old%/}"
  [[ $old == "$keep_current" || $old == "$keep_previous" ]] && continue
  # A release can hold files another user wrote, such as __pycache__ from a manual
  # sudo run. The new release is already live, so a leftover is only a warning.
  rm -rf "$old" 2>/dev/null || echo "Warning: could not fully remove $old" >&2
done
