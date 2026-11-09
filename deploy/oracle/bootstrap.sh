#!/usr/bin/env bash
# One-time setup of the Oracle VM that runs the MathLoop API.
# Run as root on the VM from this folder (see docs/production/ORACLE_DEPLOY.md):
#   sudo bash bootstrap.sh <public-ip> "<deploy public key>" [api-hostname]
# Safe to re-run: it only adds what is missing and never deletes releases.
set -euo pipefail

CADDY_VERSION="${CADDY_VERSION:-2.10.2}"
UV_VERSION="${UV_VERSION:-0.12.24}"
PYTHON_VERSION=3.12
APP_USER=practiceloop
APP_ROOT=/opt/practiceloop
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo." >&2
  exit 1
fi
if [[ $# -lt 2 ]]; then
  echo "Usage: sudo bash bootstrap.sh <public-ip> \"<deploy public key>\" [api-hostname]" >&2
  exit 1
fi
PUBLIC_IP="$1"
DEPLOY_KEY="$2"
# No domain yet: sslip.io resolves 1-2-3-4.sslip.io to 1.2.3.4, so Caddy can get a real certificate.
API_HOST="${3:-${PUBLIC_IP//./-}.sslip.io}"
if [[ ! $PUBLIC_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "The first argument must be the VM's public IPv4 address." >&2
  exit 1
fi
if [[ ! $DEPLOY_KEY =~ ^ssh-(ed25519|rsa)\  ]]; then
  echo "The second argument must be the deploy PUBLIC key (starts with ssh-ed25519)." >&2
  exit 1
fi

echo "==> Installing Python 3.12, curl and tar"
if command -v apt-get >/dev/null; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -q
  apt-get install -y -q curl tar python3-venv
  if apt-cache show python3.12-venv >/dev/null 2>&1; then
    apt-get install -y -q python3.12 python3.12-venv
  fi
elif command -v dnf >/dev/null; then
  dnf install -y -q curl tar
  dnf install -y -q python3.12 || true
else
  echo "Unsupported OS: needs apt (Ubuntu) or dnf (Oracle Linux)." >&2
  exit 1
fi
# Older images (such as Ubuntu 20.04) have no python3.12 package: use uv's standalone build.
if ! command -v python3.12 >/dev/null; then
  echo "==> No python3.12 package here, installing a standalone Python $PYTHON_VERSION with uv"
  [[ -x /opt/uv/bin/uv ]] || python3 -m venv /opt/uv
  /opt/uv/bin/pip install --quiet --disable-pip-version-check "uv==$UV_VERSION"
  export UV_PYTHON_INSTALL_DIR=/opt/python UV_PYTHON_PREFERENCE=only-managed
  /opt/uv/bin/uv python install --no-bin "$PYTHON_VERSION"
  ln -sfn "$(/opt/uv/bin/uv python find "$PYTHON_VERSION")" /usr/local/bin/python3.12
  chmod -R a+rX /opt/python
fi
python3.12 -m venv --help >/dev/null || { echo "python3.12 cannot create venvs." >&2; exit 1; }

# ADR-007 worksheets: pdflatex with amsmath, amssymb, geometry, multicol and Latin Modern.
echo "==> Installing TeX for PDF worksheets"
if command -v apt-get >/dev/null; then
  apt-get install -y -q --no-install-recommends texlive-latex-base texlive-latex-recommended \
    texlive-fonts-recommended lmodern
else
  dnf install -y -q texlive-latex texlive-amsfonts texlive-geometry texlive-tools texlive-lm \
    || echo "Install pdflatex with amsmath, geometry, multicol and lmodern by hand." >&2
fi
command -v pdflatex >/dev/null || echo "Warning: pdflatex is missing; worksheet PDFs will fail." >&2

echo "==> Creating the $APP_USER user"
if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "$APP_ROOT" --shell /bin/bash "$APP_USER"
fi
# Key-only login: a '*' password cannot be used, but unlike '!' it does not lock SSH.
usermod -p '*' "$APP_USER"
install -d -o "$APP_USER" -g "$APP_USER" -m 755 "$APP_ROOT" "$APP_ROOT/releases"
install -d -o "$APP_USER" -g "$APP_USER" -m 700 "$APP_ROOT/.ssh"
printf 'no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty %s\n' "$DEPLOY_KEY" \
  > "$APP_ROOT/.ssh/authorized_keys"
chown "$APP_USER:$APP_USER" "$APP_ROOT/.ssh/authorized_keys"
chmod 600 "$APP_ROOT/.ssh/authorized_keys"
if command -v restorecon >/dev/null; then restorecon -R "$APP_ROOT/.ssh"; fi

# The deploy user may restart the API and nothing else.
echo "$APP_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart practiceloop-api" \
  > /etc/sudoers.d/practiceloop
chmod 440 /etc/sudoers.d/practiceloop
visudo -cf /etc/sudoers.d/practiceloop >/dev/null

echo "==> Writing API settings and service"
install -d -m 755 /etc/practiceloop
if [[ ! -f /etc/practiceloop/api.env ]]; then
  cat > /etc/practiceloop/api.env <<ENV
# Exact browser origins allowed by CORS, comma-separated.
ALLOWED_ORIGINS=https://mathloop.pages.dev,http://localhost:5173,http://127.0.0.1:5173
ENV
fi
chown root:root /etc/practiceloop/api.env
chmod 600 /etc/practiceloop/api.env
install -m 644 "$HERE/practiceloop-api.service" /etc/systemd/system/practiceloop-api.service

echo "==> Installing Caddy $CADDY_VERSION for HTTPS"
case "$(uname -m)" in
  x86_64) arch=amd64 ;;
  aarch64) arch=arm64 ;;
  *) echo "Unsupported CPU: $(uname -m)" >&2; exit 1 ;;
esac
if [[ "$(/usr/local/bin/caddy version 2>/dev/null | cut -d' ' -f1)" != "v$CADDY_VERSION" ]]; then
  tmp="$(mktemp -d)"
  base="https://github.com/caddyserver/caddy/releases/download/v$CADDY_VERSION"
  archive="caddy_${CADDY_VERSION}_linux_${arch}.tar.gz"
  curl -fsSL -o "$tmp/$archive" "$base/$archive"
  curl -fsSL -o "$tmp/checksums.txt" "$base/caddy_${CADDY_VERSION}_checksums.txt"
  (cd "$tmp" && grep " $archive\$" checksums.txt | sha512sum -c -)
  tar -xzf "$tmp/$archive" -C "$tmp" caddy
  install -m 755 "$tmp/caddy" /usr/local/bin/caddy
  rm -rf "$tmp"
fi
id caddy >/dev/null 2>&1 || useradd --system --home-dir /var/lib/caddy --shell /usr/sbin/nologin caddy
install -d -o caddy -g caddy -m 750 /var/lib/caddy
install -d -m 755 /etc/caddy
sed "s/{\$API_HOST}/$API_HOST/" "$HERE/Caddyfile" > /etc/caddy/Caddyfile
install -m 644 "$HERE/caddy.service" /etc/systemd/system/caddy.service
if command -v restorecon >/dev/null; then restorecon /usr/local/bin/caddy; fi

echo "==> Opening ports 80 and 443 on the VM firewall"
if systemctl is-active --quiet firewalld; then
  firewall-cmd --quiet --permanent --add-service=http --add-service=https
  firewall-cmd --quiet --reload
elif command -v iptables >/dev/null; then
  # Oracle's Ubuntu images end INPUT with a REJECT rule, so insert ahead of it.
  for port in 80 443; do
    iptables -C INPUT -p tcp --dport "$port" -m conntrack --ctstate NEW -j ACCEPT 2>/dev/null \
      || iptables -I INPUT 1 -p tcp --dport "$port" -m conntrack --ctstate NEW -j ACCEPT
  done
  if command -v netfilter-persistent >/dev/null; then netfilter-persistent save >/dev/null; fi
fi

systemctl daemon-reload
systemctl enable --now caddy
systemctl restart caddy
# The API starts on the first deploy, once a release exists.
systemctl enable practiceloop-api

host_key="$(cut -d' ' -f1,2 /etc/ssh/ssh_host_ed25519_key.pub)"
cat <<DONE

Done. Add these in GitHub > repo Settings > Secrets and variables > Actions > Variables:
  ORACLE_HOST         $PUBLIC_IP
  ORACLE_KNOWN_HOSTS  $PUBLIC_IP $host_key
  API_BASE_URL        https://$API_HOST
DONE
