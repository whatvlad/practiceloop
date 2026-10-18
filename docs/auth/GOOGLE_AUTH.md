# Google authentication

Issue #5 replaces the website's mock identity with Supabase Auth. Vlad confirmed
that this frontend stage may proceed before open #4 on 2026-10-19. It does not
implement backend identity verification, persistent practice or learning history.
Those remain #4/#10/#12. #3's two-user database acceptance is still deferred.

## Configuration

The human configures Google Cloud OAuth as a Web application, using the callback
shown in Supabase's Google provider settings:
`https://<project-ref>.supabase.co/auth/v1/callback`. Keep Client Secret in the
Supabase dashboard. Google Auth Platform's Audience can remain External/Testing;
add every test Google account there. Google is the only supported provider.

Supabase Authentication → URL Configuration:

- Site URL: `https://practiceloop.pages.dev`
- Redirect URLs: `https://practiceloop.pages.dev/**`, `http://localhost:5173/**`

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

Client guards are a UI boundary. #4 must still verify signatures, issuer, audience,
expiry and ownership at the API. Do not treat this client implementation as API
authorization. Only `/health` is available on the scaffold API today.

## Practice remains a demo

`frontend/src/data/api.ts` is the single boundary. Authentication now goes to
Supabase; generation/check/reveal/history/counts still use the temporary demo
module. The authenticated app explicitly labels those as demo data stored in the
browser session, not persistent account history. Mock login/account functions are
removed. No browser database writes, profile provisioning or private-solution
requests are added. The demo contains static example answers, not hosted private
user answers or generator state.

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
