#!/usr/bin/env bash
# Switches the API back to the release that ran before the current one.
# Run on the VM as the practiceloop user (see docs/production/ORACLE_DEPLOY.md).
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/practiceloop}"
current="$(readlink -f "$APP_ROOT/current")"
previous="$(readlink -f "$APP_ROOT/previous" 2>/dev/null || true)"
if [[ -z $previous || ! -d $previous || $previous == "$current" ]]; then
  echo "There is no previous release to roll back to." >&2
  exit 1
fi
ln -sfn "$previous" "$APP_ROOT/current.next"
mv -Tf "$APP_ROOT/current.next" "$APP_ROOT/current"
ln -sfn "$current" "$APP_ROOT/previous"
sudo -n /usr/bin/systemctl restart practiceloop-api
for _ in $(seq 1 30); do
  if curl -fsS --max-time 2 http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "Rolled back to $(basename "$previous")."
    exit 0
  fi
  sleep 1
done
echo "Rolled back to $(basename "$previous"), but it is not answering /health." >&2
exit 1
