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

The preview VM (2026-10-18) is an Ampere A1 ARM instance on Ubuntu 20.04, which no
longer gets standard security updates; upgrade it or attach free Ubuntu Pro before
production.

| Path | What |
|---|---|
| `/opt/practiceloop/releases/<sha>-<run>-<attempt>/` | One upload: `backend/`, `deploy/oracle/` and its own `.venv` |
| `/opt/practiceloop/current`, `previous` | Symlinks to the live and the last release |
| `/etc/practiceloop/api.env` | Server settings, not in Git (`ALLOWED_ORIGINS`) |
| `/etc/caddy/Caddyfile` | HTTPS proxy, adds `X-Robots-Tag: noindex` |

The `practiceloop` user owns the releases, logs in with the deploy key only (port and agent
forwarding off), and may run only
`sudo systemctl restart practiceloop-api`. The release keeps the newest five.

## One-time setup

1. In the Oracle console, open the instance's subnet security list and add
   ingress rules for TCP 80 and 443 from `0.0.0.0/0`. Port 22 is there by default.
2. On your PC, make a key used only by GitHub Actions:
   `ssh-keygen -t ed25519 -f ~/.ssh/practiceloop_deploy -N "" -C practiceloop-deploy`.
3. Copy `deploy/oracle/` to the VM and run, with the VM's public IP and the
   contents of `practiceloop_deploy.pub`:
   `sudo bash bootstrap.sh <ip> "<ssh-ed25519 ... practiceloop-deploy>"`.
   It installs Python 3.12 (from the OS, or a standalone build via uv on images
   such as Ubuntu 20.04 that lack it) and Caddy, creates the user and services, opens the
   VM firewall and prints three values.
4. In GitHub repo settings, add the printed values as Actions **variables** (secrets also work)
   `ORACLE_HOST`, `ORACLE_KNOWN_HOSTS` and `API_BASE_URL`, and the private key as
   the **secret** `ORACLE_SSH_KEY`
   (`gh secret set ORACLE_SSH_KEY < ~/.ssh/practiceloop_deploy`).
5. Run the **Backend deploy** workflow, then the **Preview** workflow so the
   frontend is rebuilt with `API_BASE_URL`.

## CORS

`ALLOWED_ORIGINS` in `/etc/practiceloop/api.env` lists the exact origins the API
answers: `https://practiceloop.pages.dev` and the local Vite server
(`http://localhost:5173`, `http://127.0.0.1:5173`). `*` is ignored. After an edit,
run `sudo systemctl restart practiceloop-api`.

## When the API is down

The signed-in app shows "Can't reach the PracticeLoop server" and keeps working on
its demo data. Check from the VM:

```
systemctl status practiceloop-api caddy
journalctl -u practiceloop-api -n 100
curl -s http://127.0.0.1:8000/health
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
