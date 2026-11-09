# Educational content style intent

Status: confirmed by the product owner on 2026-10-18.

MathLoop uses **STE-inspired plain English** for learner-facing educational
content. The goal is clear and consistent English that remains natural in an
educational product. MathLoop does not claim formal ASD-STE100 compliance,
certification, or endorsement.

The current reference at the time of this decision is ASD-STE100 Simplified
Technical English, Issue 9 (2025):
<https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>.

## Outcome

Ship reviewed English templates that are short, unambiguous, consistent, and
easy to understand for learners who do not use English as their first language.
Apply approximately 80% of the useful STE principles while preserving enough
freedom for explanations and feedback to sound natural.

The 80% value is an internal MathLoop quality target. It is not an official
ASD-STE100 conformance score.

## Content in scope

- problem instructions;
- canonical solution steps;
- hints;
- diagnoses of known mistakes;
- validation and error messages;
- short onboarding instructions;
- learner-facing educational status messages.

Interface labels and buttons should follow the same clarity principles where
they remain natural, but they do not need a forced sentence structure.

## Content outside this policy

- mathematical notation and formulas;
- user-authored content;
- legal and privacy text;
- SEO and marketing copy;
- quotations and third-party text.

Legal text should still use plain language where possible, but this checker must
not change or weaken its legal meaning.

## Writing principles

- Use short sentences and one main instruction per sentence.
- Prefer active voice when it makes the actor and action clearer.
- Use one stable term for one concept.
- Avoid unnecessary synonyms, ambiguous pronouns, and indirect instructions.
- Keep the relationship between an instruction and its mathematical expression
  explicit.
- Permit the technical nouns and verbs required for mathematics and education.
- Prefer clarity over mechanical compliance when strict wording would sound
  unnatural or change the mathematical meaning.

## Development-time enforcement

Content is checked during development, not while the application is running.
The production application must not call an AI model, external writing service,
or runtime style checker to rewrite content.

The repository should provide one local command, such as `npm run lint:content`,
and run the same check in CI.

- Educational templates require an internal score of at least 80/100.
- A critical violation fails regardless of the total score.
- The report identifies the file, template key, rule, and suggested correction.
- A justified exception is narrow and attached to one template, not a whole file.
- The checker must be deterministic and usable without an external API.

Examples of critical violations include inconsistent terminology, an instruction
with no clear action, a placeholder that changes the intended meaning, or wording
that makes the mathematical task ambiguous.

## Template catalogue

Learner-facing educational content should live in a controlled, typed catalogue
instead of being scattered as inline strings across components and generators.
The catalogue groups templates by purpose:

- problem instructions;
- solution steps;
- hints;
- mistake diagnoses;
- validation and error messages;
- onboarding instructions.

Text and mathematical expressions remain separate. Templates can use typed
placeholders such as `{method}` or `{expression}`. Development checks reject
missing placeholders, unused placeholders, and incompatible parameter types.

English is the first catalogue. The structure should permit a later language
catalogue without introducing a full localization system before a second
language exists.

## Vocabulary and source material

MathLoop maintains its own glossary of approved mathematical, educational,
and product terms. The repository can implement the subset of writing checks
needed by this policy, but it must not copy the full official ASD-STE100
dictionary or bundle the official PDF.

Documentation must describe the policy as STE-inspired and must not imply that
ASD or STEMG reviewed, certified, or endorsed MathLoop.

## Success criteria

- New educational templates are checked locally and in CI.
- Definite violations and scores below 80 fail the content check.
- Approved templates are stored centrally and use validated typed placeholders.
- Runtime behavior has no style-checking dependency or external API cost.
- Mathematical meaning takes precedence over stylistic scoring.
- The resulting English remains natural enough for an educational platform.

## Out of scope for this decision

- the exact scoring weights;
- the complete list of hard and soft rules;
- the first approved MathLoop vocabulary;
- implementation language and file format;
- formal ASD-STE100 certification;
- automated translation or runtime rewriting.

Those items require a separate implementation specification and review.
