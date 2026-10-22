# Launch runbook (#39)

The custom-domain launch is a configuration switch. The code already handles
both states. Preview is the default: every page is noindex, robots.txt names no
sitemap, there is no canonical URL and no HSTS. A launch build gets the
approved address and indexing switch, and then:

- index.html starts with `robots: index, follow`, and the app sets
  `noindex, nofollow` on every non-public route as it loads (`src/site.ts`);
- `dist/_headers` loses the global `X-Robots-Tag: noindex`, gains
  `Strict-Transport-Security: max-age=31536000`, and keeps `noindex` on
  `/login`, `/dashboard`, `/practice`, `/history`, `/profile`, `/shared`,
  `/s/*`, `/shared/*`, `/auth/*`, `/graph/*` and on every `*.pages.dev` address
  (`pagesHeaders` in `src/site.ts`);
- robots.txt names `<site>/sitemap.xml`, which lists `/` and `/privacy`;
- canonical and `og:url` tags use the approved address on public pages.

The Preview workflow checks the generated files for whichever state it builds.

## 1. Decisions only the owner can make

None of these may be guessed or filled with placeholders (#39, PRODUCTION_CHECKLIST.md
"Launch blockers"). Record each one in the #39 Issue before step 2.

- [ ] Production domain, and whether `www.` redirects to the apex or the other way
- [ ] Operator's legal name and postal address
- [ ] Privacy contact email (a real mailbox someone reads)
- [ ] Legal basis for each processing purpose, reviewed by a qualified person
- [ ] Minimum age (16+ unless a qualified legal decision says otherwise)
- [ ] Backups for launch: Supabase Pro with daily backups, or a scheduled
      `pg_dump` with stated retention (the Free plan has none)
- [ ] Product name, English hero, CTA and SEO copy
- [ ] Logo, favicon, Apple touch icon, Open Graph image (1200×630)
- [ ] Whether Cloudflare Web Analytics is on at launch

## 2. Code changes, one PR after step 1

- `src/pages/PrivacyPage.tsx`: replace the "Not decided yet" section with the
  reviewed operator data, contact, legal bases and backup retention, and drop
  the draft wording (also the `App.test.tsx` "privacy draft" test).
- Final copy in `src/site.ts` (`DESCRIPTION`, page descriptions) and the landing page.
- Icons in `frontend/public/` and their `<link>` tags in `index.html`; add
  `og:image` and `twitter:card=summary_large_image` in `applyPageMeta`.
- `docs/auth/GOOGLE_AUTH.md`, `docs/production/ORACLE_DEPLOY.md`: the new origin.

## 3. External configuration (owner, in this order)

1. **Cloudflare**: add the domain to the account (nameservers at the
   registrar). Then Workers & Pages → `practiceloop` → Custom domains → add
   the apex (and `www`). Cloudflare creates the DNS records and certificate.
   For the other host name, add a Redirect Rule (301, keep path and query).
2. **Supabase** → Authentication → URL Configuration: Site URL
   `https://<domain>`. Add `https://<domain>/**` to Redirect URLs, and keep the
   pages.dev and localhost entries until the launch is verified.
3. **Google Auth Platform**: Branding → authorized domain `<domain>`, home
   page and privacy policy `https://<domain>/privacy`, support email. Audience →
   Publish app (leaves Testing, so any Google account can sign in). The OAuth
   client's redirect URI stays the Supabase callback.
4. **Oracle VM**: append `https://<domain>` to `ALLOWED_ORIGINS` in
   `/etc/practiceloop/api.env`, then `sudo systemctl restart practiceloop-api`.
   The browser calls `/api` on its own origin, so this only covers direct calls.
5. **Backups**: as decided in step 1.
6. **GitHub variables** (Settings → Secrets and variables → Actions →
   Variables): `SITE_URL=https://<domain>`, `SITE_INDEXABLE=true`, optional
   `CF_WEB_ANALYTICS_TOKEN`. Then run the **Preview** workflow on `main`.

## 4. Verification on the domain

```sh
curl -sI https://<domain>/ | grep -i -E 'strict-transport|x-robots|content-security'
#   HSTS present, no X-Robots-Tag
curl -sI https://<domain>/practice | grep -i x-robots     # noindex
curl -sI https://practiceloop.pages.dev/ | grep -i x-robots  # noindex
curl -s https://<domain>/robots.txt                       # Sitemap: https://<domain>/sitemap.xml
curl -s https://<domain>/sitemap.xml                      # / and /privacy only
curl -s https://<domain>/api/health                       # {"status":"ok"}
curl -sI http://<domain>/ | grep -i location              # https://<domain>/
curl -sI https://www.<domain>/ | grep -i location         # redirect per step 1
```

In a private window: sign in with a Google account that is not a test user,
practise one problem, open History, share a problem and open the link signed
out, then delete the test data from Profile. The console must show no CSP errors.
Then run `docs/production/MVP_E2E_CHECK.md` against the domain.

## 5. Rollback

- **Indexing**: set `SITE_INDEXABLE` to `false` (or delete it) and rerun
  Preview. Every page is noindex again. HSTS stays cached in browsers for a
  year, which is harmless as long as the domain keeps serving HTTPS.
- **Frontend release**: Cloudflare Pages → `practiceloop` → Deployments → an
  older deployment → Rollback.
- **Domain**: remove the custom domain in Pages. pages.dev keeps working and
  stays in the Supabase redirect list.
- **API**: `deploy/oracle/rollback.sh`, see ORACLE_DEPLOY.md "Rollback and recovery".
