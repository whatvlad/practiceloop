# Google authentication

Issue #5 replaced the website's mock identity with Supabase Auth. The API verifies
the resulting tokens (#4, docs/api/README.md); signed-in practice, history and
profile are saved (#10–#12, #35), and #3's two-user hosted isolation check passed.

## Configuration

The human configures Google Cloud OAuth as a Web application, using the callback
shown in Supabase's Google provider settings:
`https://<project-ref>.supabase.co/auth/v1/callback`. Keep Client Secret in the
Supabase dashboard. Google Auth Platform's Audience can remain External/Testing;
add every test Google account there. Google is the only supported provider.

Supabase Authentication → URL Configuration:

- Site URL: `https://mathloop.pages.dev`
- Redirect URLs: `https://mathloop.pages.dev/**`, `http://localhost:5173/**`

The application's callback is `/auth/callback` at the same origin from which the
login started. The Google→Supabase callback and Supabase→application callback
serve different parts of the flow. Keep the exact local origin `localhost` when
testing sign-in; `127.0.0.1` is not covered by the listed redirect allowlist.

For local Vite, put only these public values in ignored `frontend/.env.local`:

```dotenv
VITE_SUPABASE_URL=https://<project-ref>.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_<public-key>
VITE_API_BASE_URL=https://<api-host>
```

Restart Vite after configuration changes. Use `npm run dev -- --host localhost`.
Never copy a full backend environment file into the frontend. Session persistence
requires browser storage; restricted/private-browser storage can prevent restore.

For the Cloudflare preview, the human sets GitHub Actions values
`SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`. Variables are preferred; existing
Secrets are also supported like `API_BASE_URL`. Values are public browser build
configuration, irrespective of where stored in GitHub. The workflow rejects a
non-HTTPS project origin or any key without `sb_publishable_` before building.
`SUPABASE_SERVICE_ROLE_KEY`, database passwords and management access tokens must
never be passed to Vite. Missing configuration disables sign-in with a safe
message, rather than falling back to a fabricated identity.

## Direct Google sign-in (Google shows the site, not supabase.co)

With the Supabase-hosted redirect, Google's account chooser says "to continue to
`<project-ref>.supabase.co`", because Google names the redirect URI's host. When
the public GitHub variable `GOOGLE_CLIENT_ID` (the same Web client ID that the
Supabase Google provider uses) is set, the build gets `VITE_GOOGLE_CLIENT_ID` and
the site goes to Google itself:

1. `signIn` saves a random `state` and raw `nonce` in sessionStorage
   (`mathloop.google-sign-in`, 10 minutes) and opens
   `accounts.google.com/o/oauth2/v2/auth` with `response_type=id_token`,
   `redirect_uri=<origin>/auth/callback`, `nonce=SHA-256(nonce)` (hex) and
   `prompt=select_account`.
2. Google returns to `/auth/callback#id_token=…&state=…`. The fragment never
   reaches a server and is removed from the address bar at once.
3. The saved pair is read once and deleted. A token whose `state` does not match
   is rejected without calling Supabase (login CSRF/replay).
4. `supabase.auth.signInWithIdToken({ provider: 'google', token, nonce })`
   creates the normal Supabase session. Supabase checks the token signature, the
   audience (the client ID listed in its Google provider) and the nonce hash. The
   same Google account keeps the same Supabase user.

Without the variable, or with a malformed value, sign-in keeps the old
Supabase-hosted redirect, so the change is safe to deploy first.

The human configures (Google Cloud → Google Auth Platform → Clients → the Web
client): Authorized JavaScript origins and Authorized redirect URIs for every
origin that serves the site, e.g. `https://mathloop.net` +
`https://mathloop.net/auth/callback`, `https://mathloop.pages.dev` +
`https://mathloop.pages.dev/auth/callback`, `http://localhost:5173` +
`http://localhost:5173/auth/callback`. Keep the Supabase callback too (the
fallback uses it). Branding: app name, logo, home/privacy/terms links on
mathloop.net and the authorized domain `mathloop.net`; Google shows the name and
logo only after brand verification. In Supabase → Authentication → Providers →
Google, the client ID must be listed and "Skip nonce checks" must stay off.
Then set the GitHub variable `GOOGLE_CLIENT_ID` and rerun Preview.
Rollback: delete the variable and rerun Preview.

## Session behavior

The SDK uses PKCE with persistent sessions and automatic refresh. The application
exchanges the code on its fixed callback, strips code/error/token fields from the
address bar and always proceeds to the dashboard after success. No `next`/return
URL is followed. A cancelled, missing, reused or failed code produces a generic
message without exposing callback parameters, tokens or SDK error details. The
preview sends `Referrer-Policy: no-referrer` alongside its existing noindex header.

While restore is pending, private content is not rendered. Auth events update the
UI when the SDK refreshes tokens or another tab signs out. Expiration hides private
content if no refreshed session replaced it. Logout uses `scope: local`, signs out
the current browser session and clears that account's browser-session demo data.
Changing accounts remounts private content and resets the previous demo state.
The account name/email shown in the profile come from the Supabase user.

Client guards are a UI boundary. The API (#4) verifies signatures, issuer,
audience, expiry and ownership itself; never treat the client as authorization.

## Practice data

`frontend/src/data/api.ts` is the single boundary. Signed-in practice, history and
profile go to the saved API (docs/architecture/SAVED_PRACTICE_UI.md); a signed-out
visitor gets the one untracked demo problem (docs/architecture/ACCOUNT_COMPLETION.md).
The browser never writes to the database directly and never receives private
solutions before an authorized reveal.

## Verification

Unit/DOM tests exercise PKCE exchange under StrictMode, callback cleanup/error
handling, duplicate sign-in prevention, stale-restore versus logout ordering,
token refresh/expiry, cross-tab sign-out, logout failure, real account rendering,
protected-route loading/redirects and demo isolation across accounts. Sign-in
releases its busy state when the SDK finishes initiating the redirect, so an
interrupted navigation cannot leave the current document's button disabled.

After preview deployment, the human checks one allowed Google account:

1. Open `/profile` while signed out: sign-in page appears without profile data.
2. Continue with Google: one account chooser, return to `/dashboard`.
3. Profile shows the real name/email; the demo notice is visible.
4. Reload: the account remains signed in; callback fields are absent from the URL.
5. Open a second tab, log out in the first: private content disappears in both.
6. Sign in again after logout without reloading: Google opens and login succeeds.
7. Cancel a new Google login: a useful generic retry message appears. If browser
   navigation is stopped or returns to the previous document, sign-in can be retried.

Do not send tokens, callback fragments or browser-storage dumps to chat. The
human can report the above outcomes without exposing session data. The website
check is separate from #3's deferred two-user hosted data-isolation verification.

Rollback: revert the linked #5 commit on main and rerun Preview, or redeploy an
older Cloudflare Pages build. This changes no database schema or backend secrets.
