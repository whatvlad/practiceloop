# Launch runbook (#39)

The canonical site is `https://mathloop.net`. The Pages project `mathloop` serves
the app and `/api/*`. The separate `practiceloop` project preserves old links.
`CANONICAL_REDIRECTS` and `SITE_INDEXABLE` are independent GitHub Actions
variables. Both default to off. With redirects off, the Pages address still
serves the site and the legacy address still points to it.

## Stage the domain and API

1. Cloudflare → Workers & Pages → `mathloop` → Custom domains. Add
   `mathloop.net` and `www.mathloop.net`, and wait for both to be Active. Use
   the Pages attachment flow to provision DNS and TLS. Check that both HTTPS
   hosts serve MathLoop and that the apex `/api/health` returns `{"status":"ok"}`.

2. Follow [API hostname cutover](ORACLE_DEPLOY.md#api-hostname-cutover). Add
   DNS-only `api.mathloop.net` → `92.5.92.72`, configure Caddy to serve both
   API names, append the exact CORS origins, then verify HTTPS on both names
   before switching `API_BASE_URL`. Keep `CANONICAL_REDIRECTS` off during the
   upstream switch.

3. Supabase → Authentication → URL Configuration. Set Site URL to
   `https://mathloop.net` and add `https://mathloop.net/**` to Redirect URLs.
   Keep existing Pages and local URLs during rollout and rollback.

4. Google Auth Platform. Add `https://mathloop.net` as an authorized JavaScript
   origin. Set the home page and privacy URL to the apex in Branding and
   add `mathloop.net` as an authorized domain. Keep the OAuth redirect URI
   at `https://<project-ref>.supabase.co/auth/v1/callback`. Confirm the intended
   Audience publishing status and try a Google login from the apex.

5. Add `mathloop.net` to Cookiebot and verify the banner and preferences on
   the apex. For a custom Resend sender, verify the sending domain and its
   DNS records first, then change `FROM` in `frontend/src/edge/feedback.ts`.
   Update the Stripe public business website and Ko-fi website to the apex.

6. Set GitHub Actions `SITE_URL=https://mathloop.net` or keep the workflow
   default. On Oracle the app uses `ALLOWED_ORIGINS` for browser origins.
   Verify Google login, practice and history, a share link, the feedback form
   and `/support` with the Ko-fi widget on the apex.

## Enable permanent redirects

After the owner verifies the Pages attachments and apex app and API, set
`CANONICAL_REDIRECTS=true` and run Preview on `main`. Before changing either
project, the workflow checks both custom domains are Active on `mathloop`
and that the apex returns the MathLoop page and a healthy `/api/health` over
HTTPS. It deploys the legacy project first so old
links go straight to the apex when the main project starts redirecting.

Pages middleware handles the three production aliases and returns a single
301 with the original path and query, including API paths and static files.
The middleware passes the apex to the existing static, SPA and API handlers.
Hashed and branch `*.mathloop.pages.dev` deployments remain accessible as
working previews and carry noindex headers.

```sh
for host in mathloop.pages.dev practiceloop.pages.dev www.mathloop.net; do
  curl -sS -o /dev/null -D - "https://$host/practice?from=a%2Bb&x=1&x=2"
done
curl -fsS https://mathloop.net/api/health
```

Each alias must return `301` and `Location: https://mathloop.net/practice?from=a%2Bb&x=1&x=2`.
The workflow also probes the root, `/robots.txt` and `/api/health` on each
alias without following redirects. Run the [end-to-end check](MVP_E2E_CHECK.md)
against the apex.

## Indexing and rollback

Set `SITE_INDEXABLE=true` only after the separate
[public launch decisions](PRODUCTION_CHECKLIST.md#launch-blockers-39) are
approved. The build emits an apex-only sitemap for `/`, `/privacy` and `/terms`.
Only those pages on the apex get canonical and `og:url` metadata, including
while indexing is off. Private routes, www and Pages previews retain noindex.
Verify HSTS, CSP and crawler files on
the apex with the production build.

To roll back redirects, unset `CANONICAL_REDIRECTS` and rerun Preview. It restores
`mathloop.pages.dev` first, then points legacy links back to it. To roll back
indexing, unset `SITE_INDEXABLE` and rebuild. To roll back only the API upstream,
restore the previous `API_BASE_URL` and redeploy Pages. Keep both API names
available until these rollback paths are no longer needed.
