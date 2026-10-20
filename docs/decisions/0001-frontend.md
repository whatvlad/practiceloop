# ADR-001: static React frontend

Date: 2026-10-15. Status: accepted; implemented and deployed to Cloudflare
Pages (#26, #33).

The MVP explicitly permits React or Next.js. Use React + TypeScript + Vite with
KaTeX. The backend already owns server work; a static build fits Cloudflare Pages
without introducing a second server runtime. `frontend/dist` is the build output.
No SSR requirement exists. Revisit in a new ADR if requirements change.

Keep supported Node 24 LTS in CI; local Node 25 is a different runtime and must
not be claimed equivalent. Dependency versions are committed in the lockfile.
