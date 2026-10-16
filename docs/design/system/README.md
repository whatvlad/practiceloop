PracticeLoop practises mathematics the way a good tutor would: one clean problem at a time, a quiet room, and an honest answer. The look is a black room with white objects: true-black canvas, white type, and the single white button that matters.

## Directions

The system ships three themes you can switch between in the page header. They share every token name, so changing direction is only a theme change.

- **Ink** (default): true black `canvas`, white `action`. The original brief: plain black with white elements.
- **Graphite**: charcoal `canvas` (`#0f0f10`) that is softer on the eyes in long sessions; same white action.
- **Paper**: inverted. Warm off-white `canvas`, black `action`. Use for daytime or printing.

Pick one theme per product release; do not mix themes inside a view.

## Content fundamentals

- Write in sentence case. Address the learner as "you". Keep sentences short and calm: "Check answer", "Show solution", "Generate next problem".
- Use the spec's button names exactly: Check Answer, Show Answer, Show Solution, Generate Next Problem, written in sentence case.
- Results are three states only: Correct, Incorrect, Invalid expression. Never celebrate (no confetti, exclamation marks or emoji) and never scold.
- State what happened, then what to do: "That is not equivalent to the correct answer. Try again, or reveal it."
- Mathematics is set in KaTeX; typed notation (`sqrt(3)`, `pi/4 + 2`) is set in `code` or `answer-input`.
- No filler statistics, testimonials or user counts on public pages.

## Visual foundations

- **Surfaces.** Page is `canvas`; cards are `surface`; wells, inputs and solution blocks are `surface-raised`; hover is `surface-hover`. Edges are `line` hairlines. Depth comes from `shadow-card` (a hairline) and, only for the problem card, `shadow-lift`.
- **One loud thing.** `action` fill (white on dark themes) is reserved for the single main button, the selected chip and the selected difficulty. Everything else is outline (`control-border`) or ghost.
- **Text.** `ink` for primary text and all maths, `ink-muted` for descriptions and labels, `ink-subtle` only for timestamps and helper text on `canvas` or `surface`.
- **Status colour is rare.** `correct` (blue), `incorrect` (orange) and `invalid` (amber) appear only in result banners, answer-field borders and history results, and always with an icon and a word. Blue and orange are chosen to stay distinct under red–green colour blindness. No other colour exists in the interface.
- **Type.** Headlines in `display-*` (Instrument Serif), with at most one italic phrase per heading for emphasis. Interface in Geist (`heading-*`, `body`, `small`). Eyebrows, the answer field and syntax hints in Geist Mono (`label`, `answer-input`, `code`). Maths in KaTeX (`math-problem`, `math-solution`). All faces load from Google Fonts.
- **Space and shape.** 4px base grid via `space-1`…`space-9`. Buttons, inputs and chips use `radius-md`/`radius-pill`; cards `radius-lg`; the problem card `radius-xl`.
- **Layout.** Content width 1120px, practice column 760px. The practice page has one column and no sidebar.
- **Motion.** 150ms colour and border transitions only. Reveals fade in; nothing bounces, slides or loops.
- **Focus.** A solid 2px `focus` ring with a 2px offset on every interactive element, at least 3:1 on every surface in every theme.
- **Imagery.** None. Mathematics is the imagery. No photographs, illustrations, gradients or glows.

## Iconography

Icons are 24-unit line icons, 2px stroke, round caps and joins, drawn in `currentColor` at 16–22px: check, cross, warning, arrow, chevron, dash, refresh. Use them to pair with status words, never as decoration. The PracticeLoop mark is a ring with a gap and a centre point, set beside the wordmark in Instrument Serif. It is drawn inline (in `currentColor`) and is original to this system; replace it with the owner's final logo when one exists.

## Using the components

Class names are in `components/bundle.css` (prefix `pl-`) and read tokens through CSS variables, so they follow the active theme. Components with previews: Button, AnswerInput, TopicChips, DifficultyScale, ProblemCard, ResultBanner, SolutionSteps, StatTile, HistoryRow, AppNav. Full pages, matching the spec's routes: LandingPage (`/`), LoginPage (`/login`), DashboardPage (`/dashboard`), PracticePage (`/practice`), HistoryPage (`/history`), ProfilePage (`/profile`).

Build with React + TypeScript + KaTeX, per the project's frontend decision. Never render correct answers or generator data in a component before the backend returns them.
