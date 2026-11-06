# Changelog

User-facing releases. Known limitations of the current release are in
[README.md](README.md#known-limitations).

## Unreleased

- **Privacy and Terms of Service.** The Privacy page is no longer a draft: it
  names the operators and a contact address and explains why data is used. A
  new Terms of Service page is linked from the landing, sign-in, Privacy and
  profile pages. (#39)

- **Combinations topic (new generator engine).** Algebra has a new
  "Combinations" topic, level 1: calculate a binomial coefficient C(n, k) and
  answer with the exact number. It is the first topic served by the new
  generator engine; each saved problem keeps a private problem code that
  rebuilds it exactly. It is not part of mixed practice or generated
  worksheets yet. (#169)

- **Mathematical Analysis practice area.** Integral and derivative topics now
  share one area and one mixed-practice pool. Algebra is reserved for the next
  content release and stays hidden until its first verified topic is ready.
  Existing topic links, saved problems and worksheet exports stay usable. (#144)

- **Worked solutions and graphs in worksheet PDFs.** "Include worked solutions
  and graphs", on by default next to the answer key, adds a Solutions section
  at the end of the PDF: every problem's steps and, for integrals, a graph like
  the one in "Show solution" (the curve and area, f and F, the region, or the
  solid). Printed solutions mark the problems as solution revealed. (#130)

- **Practise definite integrals on their own.** A new "Definite integrals"
  topic in the Integrals area, levels 1-5, offers only integrals with bounds,
  drawn from every single-integral method. The other topics still include
  their definite variants, and Mixed practice is unchanged. The account line
  on Practice and Profile now lines up with the page below it. (#128)

- **Export problems from History as a PDF.** Each History row has a checkbox;
  "Select all" ticks the loaded rows under the current filter and "Clear"
  unticks them. "Export PDF" prints up to 40 selected problems, grouped by
  topic and level, with the same page and answer-key options as the Practice
  worksheet; with the key, History shows their answers as revealed. A new
  "From worksheets" filter lists the problems generated for worksheets. (#118)

- **Print a worksheet from Practice.** "Print worksheet" at the bottom of a
  saved practice problem builds a PDF of new problems in up to 8 groups (topic
  or mixed, a level and a count, at most 40 problems). It shows before
  generating when a group asks for more different problems than its topic and
  level have, and never repeats a problem. Choose A4 or Letter, one or two
  columns, and whether to include the answer key; the problems are saved to
  History, and with the key their answers count as revealed. (#117)

- **See the solid of a triple integral.** Show solution now draws the solid E
  in 3D: its bottom and top surfaces and the side walls, translucent with
  edges, in Cartesian and cylindrical coordinates. Drag to rotate, pinch or
  scroll to zoom. Without WebGL only the solid's inequalities are shown, and
  the steps are unchanged. (#114)

- **Solve a shared problem.** A shared link or code now offers the exact
  exercise for practice after sign-in. Google sign-in returns to the shared
  problem, and solving saves a separate copy in the recipient's history with
  answer checking and explicit answer/solution reveal. Sender attempts and
  reveal state stay private. (#109)

- **Partial derivatives.** A second Derivatives topic at levels 1-5: first
  partials in x and y, second and mixed partials and three variables, the chain
  rule after changing to polar or cylindrical coordinates, and the Jacobian of
  a scaled polar or cylindrical map. The answer field takes the variables the
  exercise names (`y`, `z`, `r`, `θ` as well as `x`, with `2xy` read as
  `2*x*y`), and the solution shows which variables are held constant and each
  chain-rule term. A differentiated constant, a dropped chain-rule term, a
  missing inner derivative, a missing r or a determinant sign error get
  targeted feedback. Derivatives now have mixed practice. (#96, #101)
- **Triple integrals.** A new Integrals topic at levels 1-5: boxes, a simplex
  and tetrahedra in Cartesian coordinates, cylinders, a cone and a paraboloid
  in cylindrical coordinates, and Cartesian integrals that are only clean in
  cylindrical. The answer is the exact value, and the solution shows the
  solid, the bounds, the factor r, each of the three iterated integrals and a
  check in the other system. A missing r, wrong z bounds or reversed bounds get
  targeted feedback. (#100)
- **Double integrals.** A new Integrals topic at levels 1-5: rectangles and
  type I/II regions in Cartesian coordinates, disks, annuli and sectors in
  polar coordinates, reversing the order of integration, and Cartesian
  integrals that are only clean in polar. The answer is the exact value, and
  the solution shows the region, the bounds, the factor r and each iterated
  integral. A missing r or reversed bounds get targeted feedback. (#99)
- **Practice areas.** Practice is grouped into Integrals and Derivatives
  (ADR-005). Once a second area has topics, the dashboard asks for an area
  first, then a topic and level, and mixed practice draws only within the
  chosen area. Topics that are not ready yet are no longer shown. (#98)

- **Share a problem.** Under a saved problem, *Share problem* makes a link and a
  short code such as `K7M2-QX9P`. Anyone can open it, signed in or not, and sees
  only the problem, its topic and difficulty: never your answers, results or
  solutions. Shares last 90 days, and *Stop sharing* ends them at once. Shared
  pages are kept out of search engines. (#37)
- **Production readiness on preview.** A draft privacy page that describes the
  real data flows, *Report a problem* under saved problems, a 404 page with
  links home and to practice, a skip link, per-page titles and descriptions,
  and a practice button first on the home page. Fonts are now served from the
  site itself instead of Google Fonts, the site and API send a strict Content
  Security Policy and other security headers, and Cloudflare Web Analytics can
  be switched on without seeing emails, accounts or answers. The release
  checklist and the open launch blockers are in
  `docs/production/PRODUCTION_CHECKLIST.md`. (#38)

## 0.1.0 — MVP (2026-10-20)

The first complete release of PracticeLoop, live as a noindex preview at
https://practiceloop.pages.dev with the API on Oracle and data in Supabase.

- **Sign in with Google.** Sessions survive reloads and sign-out works across
  tabs. A signed-out visitor can try one fixed demo problem; nothing they do is
  saved.
- **Integration practice.** Choose basic integrals, substitution, rational
  functions or trigonometric integrals at levels 1–5, integration by parts at
  levels 1–3, or mixed practice with fixed, published topic weights. Most choices
  also include definite integrals with exact answers. Every problem comes from a
  checked catalogue, and you see no repeat within half of a topic-level catalogue.
- **Answer checking.** Type answers in a formula editor with a maths keyboard and
  live preview. Answers are checked symbolically on the server as Correct,
  Incorrect or Invalid expression. A missing `+ C` is pointed out, and common
  mistakes such as `ln(x)` for `ln|x|`, a lost sign or a missing chain-rule factor
  get specific advice.
- **Answers and solutions on request.** Reveal the final answer or a full
  step-by-step solution; reveals are remembered.
- **History.** Every generated problem is saved with its latest attempt and can
  be reopened after a reload, with older entries loaded page by page.
- **Profile and statistics.** Generated, attempted and solved counts; how often
  the integration constant was left out, by topic and level and over eight weeks;
  an optional display name; and permanent account deletion with typed
  confirmation.
- **Privacy and safety.** Each account sees only its own data, the browser never
  receives answers or solutions before they are revealed, and answers are parsed
  by a bounded, sandboxed checker.

### Changes during MVP development

- End-to-end check (#13): `scripts/e2e_local.py` drives the real API over HTTP
  through every topic and level, cross-user denial, malicious input, worker
  saturation and a database outage; CI runs it. An answer or profile name
  containing a NUL byte is now rejected as invalid instead of failing with a
  server error. The formula editor no longer turns `3e-6` into `3×10⁻⁶`; a
  number before `e` is the constant e, as everywhere else.
- Mixed practice (#36, part 2): signed-in learners can choose "Mixed practice" and
  a level. Each problem's topic is drawn with fixed weights that the dashboard
  shows as percentages; basic integrals have half the weight of each method.
  "Generate next problem" stays in mixed practice.
- Targeted mistake feedback (#36, part 2): when a wrong answer clearly matches a
  common mistake its template declares, such as `ln(x)` instead of `ln|x|`, a lost
  sign, a missing chain-rule factor or a definite integral left unevaluated, the
  learner sees advice for that mistake. Otherwise they get a general hint. The
  code is saved with the attempt and shown again when the problem is reopened.
- Integration by parts now has levels 1–3 instead of 3–5, and the practice page
  shows only the levels a topic offers. Switching topic moves an unavailable
  level to the nearest available one.
- Definite integrals (#36, part 2): most practice cells now also offer definite
  integrals with clean bounds and exact values such as `e - 2` or `3 ln(4/3)`.
  Their answer is one number with no `+ C`; bounds never touch a singularity.
  Constant-omission statistics leave definite answers out.
- Signed-in practice offers every approved topic and level (#36, part 1): all
  five topics at levels 1–5, with integration by parts from level 3. The answer
  checker grades the new substitution, parts, rational and trigonometric problems
  on every part of their domain. Definite integrals, mixed practice and mistake
  feedback are still to come.
- Backend saves practice for signed-in learners (#10): generating a problem stores
  it with its private solution, every checked answer is stored (including invalid
  ones and a missing-constant flag), and reveals set their flags. Retries with the
  same idempotency key never duplicate work. The app itself still uses the
  untracked preview until #11.
- Hosted Supabase two-user isolation check passed with two real Google accounts; #3 done.
- Backend checks integration answers (#8): an explicit `aK + b` constant,
  derivative equality and real values on every part of the problem's domain,
  all inside the resource-limited worker. Undecidable answers return a
  retryable inconclusive error instead of a guess. Not yet wired to any route.
- Backend verifies Supabase access tokens (#4): asymmetric JWKS keys only, with
  issuer, audience, expiry and role checks and key rotation. Owner-scoped
  queries for problems, attempts and reveals deny other users' IDs even though
  the backend's database role bypasses RLS. Not yet wired to any route.
- Frontend implements the PracticeLoop design system (#26): Ink tokens, the ten
  components and the six routes (`/`, `/login`, `/dashboard`, `/practice`,
  `/history`, `/profile`) on a temporary mock data layer. No backend or sign-in yet.
- Frontend preview deploys to GitHub Pages from `main` (#28), temporary until
  the Cloudflare deployment (PL-014).
