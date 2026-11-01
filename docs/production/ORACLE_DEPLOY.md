# Oracle backend deploy

The FastAPI backend runs on one Oracle Cloud Free Tier VM. Every push to `main`
that changes `backend/` or `deploy/oracle/` runs `.github/workflows/backend-deploy.yml`:
it runs the backend tests, uploads a release over SSH, switches to it, and checks
`https://<api host>/health`. The frontend on Cloudflare Pages (`preview.yml`) is
built with `VITE_API_BASE_URL` set to the same address.

```
Browser ── HTTPS ──> practiceloop.pages.dev            (Cloudflare Pages, static)
   └────── HTTPS ──> <ip-with-dashes>.sslip.io:443     (Caddy on the VM, Let's Encrypt)
                        └── http ──> 127.0.0.1:8000    (uvicorn, systemd: practiceloop-api)
```

There is no domain yet, so the API host is `<ip-with-dashes>.sslip.io`, a public
DNS name that resolves to the VM's IP and lets Caddy get a real certificate. With a
domain later, pass it as the third argument to `bootstrap.sh` and update
`API_BASE_URL`.

## On the VM

The VM (audited 2026-10-20) is `VM.Standard.A1.Flex` with 1 OCPU (Ampere ARM)
and 6 GB RAM, 45 GB disk, in `eu-frankfurt-1` (AD-1), inside the Always Free
allowance (4 OCPUs / 24 GB). It runs Ubuntu 20.04 with Ubuntu Pro ESM (infra and
apps) attached, so it still gets security updates; move to a newer LTS when
convenient. Only 22, 80 and 443 are open in the Oracle security list. Caddy's
admin API (2019) and uvicorn (8000) listen on localhost only; the image's rpcbind
(111) listens on all addresses but is blocked by the security list.

**Co-tenant (known risk, accepted 2026-10-20):** an unrelated app,
`/home/ubuntu/korepetycje-telegram-crm` (Python on `127.0.0.1:8080`), runs on the
same VM as `ubuntu` and is published through a Cloudflare quick tunnel
(`cloudflared tunnel --url http://127.0.0.1:8080`, which also listens on 20241 for
metrics). Both were started by hand, with no systemd unit. Because `ubuntu` has
passwordless sudo, a compromise of that public app would give root on the VM and
with it `api.env` (service-role key, database password). It also shares the one
OCPU. Moving it to its own unprivileged user or its own VM removes the risk. Docker
is installed (containerd on localhost 34179) but runs no containers.

| Path | What |
|---|---|
| `/opt/practiceloop/releases/<sha>-<run>-<attempt>/` | One upload: `backend/`, `deploy/oracle/` and its own `.venv` |
| `/opt/practiceloop/current`, `previous` | Symlinks to the live and the last release |
| `/etc/practiceloop/api.env` | Server settings, not in Git; `root:root`, mode `600` |
| `/etc/caddy/Caddyfile` | HTTPS proxy over HTTP/1.1 and HTTP/2 only, adds `X-Robots-Tag: noindex` |

The `practiceloop` user owns the releases, logs in with the deploy key only (port and agent
forwarding off), and may run only
`sudo systemctl restart practiceloop-api`. The release keeps the newest five.

## Capacity and worker isolation

The VM's shape and size are under [On the VM](#on-the-vm). One process
serves the API under systemd with `MemoryMax=512M`. Each answer check spawns a fresh
math worker (`backend/app/services/math_worker.py`) with a 2 s CPU limit, a 256 MB
address-space limit, a 3 s wall clock and no core dumps; the parent kills it on
timeout and answers a retryable `503`. One check runs at a time in `/preview`.
Rate limits are in the API itself: per user on the signed-in routes and a global
window on `/preview` (`429` with `Retry-After`, see `docs/api/README.md`).

Worksheet PDFs (ADR-007) run `pdflatex` from Ubuntu's TeX Live packages
(`texlive-latex-base`, `texlive-latex-recommended`, `texlive-fonts-recommended`,
`lmodern`, about 300 MB), one compile at a time, each in a fresh child
(`backend/app/services/tex_worker.py`) with no shell escape, paranoid file access,
10 s CPU, 512 MB address space, 5 MB files, a 20 s wall clock and a temporary
directory that is deleted afterwards. `bootstrap.sh` installs the packages; on a
VM bootstrapped before #116, install them once by hand (the deploy user cannot):

```sh
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-fonts-recommended lmodern
```

Without them the API still runs, and only `GET /api/worksheets/{id}/pdf` answers
`503 worksheet_render_failed`.

## Secrets

Backend secrets (`DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) live only in
`/etc/practiceloop/api.env`. GitHub holds the deploy key, Cloudflare and Supabase
CLI credentials and the public Supabase URL and publishable key; the frontend build
gets only `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` and `/api`. The
Google OAuth client secret is stored only in Supabase. Google redirects are listed
in `docs/auth/GOOGLE_AUTH.md`.

## Logs

- **API:** uvicorn writes one access line per request (caller IP, which is Cloudflare's for `/api` traffic, method, path
  with query, status) to the systemd journal. Paths carry only problem ids and
  page cursors. Bearer tokens travel in a header and are never logged; answers and
  other bodies are never logged, and validation errors do not echo them. Unhandled
  errors log a traceback with a correlation id that the learner sees.
- **Caddy:** no access log (the Caddyfile has no `log` directive).
- **Cloudflare:** the `/api` Pages Function forwards only `Accept`,
  `Authorization`, `Content-Type` and `Idempotency-Key`, and logs nothing.
- Retention is the journal's default size cap; `deploy/oracle/audit.sh` prints it
  and counts any lines that look like tokens or database URLs (should be 0).

## Backups and restore

The VM holds no data: releases are rebuilt from Git and settings are only
`api.env`, so recovery is the **Lost VM** step below plus re-entering `api.env`
from the Supabase dashboard (Connect → Session pooler; Settings → API keys).
All learner data is in Supabase Postgres. Its backups depend on the Supabase plan
(Dashboard → Database → Backups); the restore and 30-day deletion rules are in
`supabase/README.md` (Backup and rollback) and
`docs/architecture/ACCOUNT_COMPLETION.md`. Never keep dumps in Git, Actions
artifacts or VM snapshots.

## One-time setup

1. In the Oracle console, open the instance's subnet security list and add
   ingress rules for TCP 80 and 443 from `0.0.0.0/0`. Port 22 is there by default.
2. On your PC, make a key used only by GitHub Actions:
   `ssh-keygen -t ed25519 -f ~/.ssh/practiceloop_deploy -N "" -C practiceloop-deploy`.
3. Copy `deploy/oracle/` to the VM and run, with the VM's public IP and the
   contents of `practiceloop_deploy.pub`:
   `sudo bash bootstrap.sh <ip> "<ssh-ed25519 ... practiceloop-deploy>"`.
   It installs Python 3.12 (from the OS, or a standalone build via uv on images
   such as Ubuntu 20.04 that lack it), TeX for worksheet PDFs and Caddy, creates the user and services, opens the
   VM firewall and prints three values.
4. In GitHub repo settings, add the printed values as Actions **variables** (secrets also work)
   `ORACLE_HOST`, `ORACLE_KNOWN_HOSTS` and `API_BASE_URL`, and the private key as
   the **secret** `ORACLE_SSH_KEY`
   (`gh secret set ORACLE_SSH_KEY < ~/.ssh/practiceloop_deploy`).
5. Run the **Backend deploy** workflow, then the **Preview** workflow so the
   frontend is rebuilt with `API_BASE_URL`.

## Browser path

The deployed app never calls sslip.io directly. It calls `/api/*` on
practiceloop.pages.dev, and the Pages Function `frontend/functions/api/[[path]].ts`
forwards that to `API_BASE_URL`. Campus networks such as eduroam behind a FortiGate
intercept HTTPS to unfamiliar hosts like sslip.io and break it with their own
certificate, but leave pages.dev alone.

## CORS

`ALLOWED_ORIGINS` in `/etc/practiceloop/api.env` lists the exact origins the API
answers (only direct browser calls need it now): `https://practiceloop.pages.dev` and the local Vite server
(`http://localhost:5173`, `http://127.0.0.1:5173`). `*` is ignored. After an edit,
run `sudo systemctl restart practiceloop-api`.

## Before adding Supabase credentials (human only)

Bootstrap now sets `api.env` to `root:root`, mode `600`, including on reruns.
Older installations used `644`; fix the existing VM before adding any secret:

```powershell
ssh -i "$env:USERPROFILE\.ssh\oracle_vlad" ubuntu@92.5.92.72
```

Then on the VM:

```sh
sudo chown root:root /etc/practiceloop/api.env
sudo chmod 600 /etc/practiceloop/api.env
sudo stat -c '%a %U:%G' /etc/practiceloop/api.env
```

Expected output: `600 root:root`. systemd reads `EnvironmentFile` as root before
starting the service as `practiceloop`; the application user need not read the file.
Changing repository code alone does not change the existing VM's file permissions.

When #4 wires backend Supabase access, the human edits the file with
`sudo nano /etc/practiceloop/api.env`, adding these values directly on the VM:

```dotenv
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<backend-only-service-role-key>
SUPABASE_JWT_ISSUER=https://<project-ref>.supabase.co/auth/v1
```

Keep the existing `ALLOWED_ORIGINS`. There is no space after `=` in the issuer.
Restart with `sudo systemctl restart practiceloop-api`. Do not print the file,
paste credentials into chat, put the service-role key in GitHub, or use it in
`VITE_*` variables. #3 adds migration delivery only; `/health` still reports
liveness and does not verify Supabase connectivity or authenticated API access.

#10 saves practice in Supabase Postgres, which needs one more line in the same file:

```dotenv
DATABASE_URL=postgresql://postgres.<project-ref>:<database-password>@<pooler-host>:5432/postgres?sslmode=require
```

Copy it from Supabase → **Connect** → **Session pooler** (the IPv4 address; the
direct host is IPv6-only) and fill in the database password. The API connects as
`postgres` but runs every transaction as `service_role`, and all ownership checks
are in its SQL. Without `DATABASE_URL`, `/problems` and the other saved-practice
routes answer `503 database_unavailable`; the untracked `/preview` routes are
unaffected. Restart the service after editing.

## When the API is down

The signed-in app shows "Can't reach the PracticeLoop server" and keeps working on
its demo data. Check from the VM:

```
systemctl status practiceloop-api caddy
journalctl -u practiceloop-api -n 100
curl -s http://127.0.0.1:8000/health
```

The deploy workflow does not touch Caddy. After changing `deploy/oracle/Caddyfile`,
apply it as `ubuntu` from a release that contains the change:

```
sudo sed "s/{\$API_HOST}/92-5-92-72.sslip.io/" /opt/practiceloop/current/deploy/oracle/Caddyfile | sudo tee /etc/caddy/Caddyfile >/dev/null
sudo systemctl restart caddy
```

## Rollback and recovery

- **Failed deploy:** `release.sh` restores the previous release by itself when the
  new one does not answer `/health` within 30 seconds, and the workflow fails.
- **Bad but healthy deploy, fastest:** on the VM as `practiceloop`
  (`sudo -iu practiceloop`), run `bash /opt/practiceloop/current/deploy/oracle/rollback.sh`.
  It swaps `current` and `previous` and restarts. The next push deploys again.
- **Bad deploy, lasting:** `git revert` the commit on `main`; the workflow deploys
  the reverted code.
- **Lost VM:** create a new instance, repeat the one-time setup with its IP, and
  update the three variables. Releases hold no data, so nothing else is lost.
- **Frontend:** roll back in Cloudflare Pages (project `practiceloop` >
  Deployments > an older one > Rollback), or revert on `main`.

## Audit

`deploy/oracle/audit.sh` is read-only and prints the region, shape, services,
ports, the key *names* in `api.env`, worker limits, log settings and local health.
From the repo on your PC:

```powershell
Get-Content deploy/oracle/audit.sh -Raw | ssh -i "$env:USERPROFILE\.ssh\oracle_vlad" ubuntu@92.5.92.72 'tr -d \\015 | bash -s'
```

Public checks from any PC:

```powershell
curl.exe -sS https://92-5-92-72.sslip.io/health        # {"status":"ok"}
curl.exe -sSI http://92-5-92-72.sslip.io/health        # 308 to https
curl.exe -sS https://practiceloop.pages.dev/api/health  # {"status":"ok"}
curl.exe -sSI -X OPTIONS https://92-5-92-72.sslip.io/topics -H "Origin: https://evil.example" -H "Access-Control-Request-Method: GET"  # 400, no Allow-Origin
```


## Verified engine catalogue (#192)

Each Oracle release builds its own private `backend/.engine-catalogue.json`
with that release's pinned dependencies: `release.sh` runs
`.venv/bin/python -m app.engine.catalogue` from `backend/` before switching
`current` or restarting the service. All declared engine cells must fill
64-code pools; an error aborts the deploy while the previous release stays
active. API startup validates and caches the artifact and refuses to start
with a missing or incomplete catalogue. Requests never rebuild it.

The artifact contains private answers and solution steps. Keep it within the
backend release; never upload it as a public CI artifact or frontend asset.
Rollback uses the retained release's own catalogue. No environment variable,
new systemd write permission or database migration is needed. Locally, build
with `python -m app.engine.catalogue` after installing the backend and after
changing engine generators/topics; CI does so before backend/worksheet tests.
Pool size and format are documented in ADR-008.
