# Prompt for Claude Code: implement the PracticeLoop frontend design

Copy everything below the line into a new Claude Code session.

---

You are working on PracticeLoop. First follow AGENTS.md: read the files it lists, check GitHub Issues and open PRs, and get the accountable human's confirmation that this work is available before implementing. Work in your own branch from the latest main. Do not edit docs/PRACTICELOOP_MVP.md.

## Goal

Implement the approved visual design for the frontend: React + TypeScript + Vite + KaTeX (see docs/decisions/0001-frontend.md). The design is finished and committed under `docs/design/system/`. Your job is to turn it into real components and pages, not to redesign it.

## Source of truth

- `docs/design/system/README.md`: brand rules (content, visual foundations, iconography). Read it first.
- `docs/design/system/tokens.json`: every colour, type style, space, radius and shadow, with usage notes. Three themes: `ink` (default, true black), `graphite`, `paper`.
- `docs/design/system/components/bundle.css`: reference CSS for every component (classes prefixed `pl-`).
- `docs/design/system/components/<Name>/README.md` and `preview.html`: usage rules and a live HTML reference for each component and page. Open any `preview.html` directly in a browser to see the target (they link `tokens.css` and `bundle.css` relatively; `tokens.css` is generated from `tokens.json`).

Components: Button, AnswerInput, TopicChips, DifficultyScale, ProblemCard, ResultBanner, SolutionSteps, StatTile, HistoryRow, AppNav.
Pages: LandingPage `/`, LoginPage `/login`, DashboardPage `/dashboard`, PracticePage `/practice`, HistoryPage `/history`, ProfilePage `/profile`.

## What to build

1. Convert `tokens.json` into CSS custom properties (`:root` and `[data-theme="graphite"]`, `[data-theme="paper"]`) in one stylesheet. Use the token names as the variable names (`--canvas`, `--surface`, `--ink`, `--action`, `--correct`, and so on). Default theme is `ink`.
2. Load fonts: Instrument Serif, Geist, Geist Mono (Google Fonts, or self-host if the project prefers). Math uses KaTeX with `katex/dist/katex.min.css`.
3. Build typed React components matching the previews, with props described in each component README. Use plain CSS (or CSS modules) driven by the tokens. Do not add a UI framework or Tailwind.
4. Build the six pages and the router for the routes in the MVP spec. Use mock data only: no backend, Supabase or auth calls in this task. Put mock data behind a small data layer (for example `src/data/mock.ts`) so real API calls can replace it later.
5. PracticePage must reproduce the preview's flow with a mock checker: idle, then Correct / Incorrect / Invalid expression, then optional Show Answer and Show Solution, then Generate Next Problem. The mock must never ship the correct answer to the browser in production code paths. Isolate it clearly as a temporary stub so the backend can replace it.
6. A theme switch is optional; ship `ink` by default and keep the other themes working.

## Rules

- Do not change the design: layout, colours, type and copy come from the previews. If something is impossible or ambiguous, note it in the PR instead of improvising.
- Status colours appear only for result states, always with an icon and a word.
- Keep keyboard and screen-reader support: visible focus ring (`--focus`), `role="status"` on results, labels on inputs, `aria-pressed` on chips and difficulty buttons.
- One focused PR. Do not touch backend, Supabase, lockfile policy or CI beyond what the frontend scaffold needs. Update CHANGELOG.md and docs/agents/STATUS.md per the project workflow.
- Verify before finishing: typecheck, lint, build, and a visual check of each page in the browser against its preview at desktop and a narrow mobile width (the previews are desktop-first, so make the layouts collapse sensibly: grids to one column, the history table to stacked rows).

## Definition of done

All six routes render with the Ink theme and match the previews; the practice flow works with the mock checker; build and CI pass; the PR description lists any deviations from the design.
