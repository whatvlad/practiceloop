#!/usr/bin/env bash
# Read-only check of the Oracle VM for Issue #14. Prints facts, changes nothing,
# and never prints the values in /etc/practiceloop/api.env (only its key names).
# Run as ubuntu: ssh ... ubuntu@<vm> 'tr -d \\015 | bash -s' < deploy/oracle/audit.sh
# (tr strips the CRs that a Windows checkout or PowerShell pipe adds.)
set -uo pipefail

section() { printf '\n== %s\n' "$1"; }

section "Host"
echo "OS: $(sed -n 's/^PRETTY_NAME="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' /etc/os-release)"
echo "Arch: $(uname -m), CPUs: $(nproc)"
free -h | awk 'NR<=2'
df -h / | awk 'NR==2 {print "Disk /: " $2 " total, " $4 " free"}'
command -v pro >/dev/null && pro status 2>/dev/null | grep -E '^(esm-|livepatch)' || echo "Ubuntu Pro: not installed"

section "Oracle instance (metadata service)"
meta="$(curl -fsS --max-time 3 -H 'Authorization: Bearer Oracle' http://169.254.169.254/opc/v2/instance/ 2>/dev/null)"
if [[ -n $meta ]]; then
  python3 - "$meta" <<'PY'
import json, sys
m = json.loads(sys.argv[1])
c = m.get("shapeConfig", {})
print("Region:", m.get("canonicalRegionName") or m.get("region"))
print("Availability domain:", m.get("availabilityDomain"))
print("Shape:", m.get("shape"), "| OCPUs:", c.get("ocpus"), "| Memory GB:", c.get("memoryInGBs"))
PY
else
  echo "Metadata service did not answer."
fi

section "Services"
for unit in practiceloop-api caddy; do
  echo "$unit: $(systemctl is-active "$unit") / $(systemctl is-enabled "$unit")"
done
systemctl show practiceloop-api -p User,MemoryMax,NoNewPrivileges,ProtectSystem,PrivateTmp
echo "current -> $(basename "$(readlink -f /opt/practiceloop/current)")"
echo "previous -> $(basename "$(readlink -f /opt/practiceloop/previous 2>/dev/null)" 2>/dev/null)"

section "Listening TCP ports"
sudo ss -tlnH | awk '{print $4}' | sort -u

section "Settings file (key names only)"
sudo stat -c '%a %U:%G %n' /etc/practiceloop/api.env
sudo sed -n 's/^\([A-Z_][A-Z0-9_]*\)=.*/\1/p' /etc/practiceloop/api.env
sudo grep '^ALLOWED_ORIGINS=' /etc/practiceloop/api.env

section "Worker limits in the live release"
grep -E '^(CPU_SECONDS|ADDRESS_SPACE_BYTES|WALL_SECONDS) =' \
  /opt/practiceloop/current/backend/app/services/math_worker.py

section "Logs"
grep -hE '^\s*(Storage|SystemMaxUse|MaxRetentionSec)=' /etc/systemd/journald.conf /etc/systemd/journald.conf.d/*.conf 2>/dev/null \
  || echo "journald: distro defaults (no overrides)"
journalctl --disk-usage 2>/dev/null
grep -q '^\s*log' /etc/caddy/Caddyfile && echo "Caddy: access log ON" || echo "Caddy: no access log"
since="$(sudo journalctl -u practiceloop-api -o short-iso -q --no-pager 2>/dev/null | head -n 1 | cut -c1-10)"
echo "Oldest practiceloop-api entry kept: ${since:-none}"
# Count only; never print matches. JWTs start with eyJ.
echo "API log lines that look like tokens or secrets: $(sudo journalctl -u practiceloop-api --no-pager 2>/dev/null \
  | grep -cE 'eyJ[A-Za-z0-9_-]{10,}|Bearer [A-Za-z0-9._-]{10,}|postgres(ql)?://[^ ]*:[^ ]*@|service_role')"

section "Local health"
curl -fsS --max-time 3 http://127.0.0.1:8000/health; echo
