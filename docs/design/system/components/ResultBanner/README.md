These are the three states the checker can return, and no others: **Correct**, **Incorrect**, **Invalid expression**. Each is identified by a word, an icon and a colour. Colour is never the only signal.

Correct is blue (`correct`), Incorrect is orange (`incorrect`), Invalid is amber (`invalid`); blue and orange are chosen so the pair stays distinguishable for red–green colour blindness. All text sits on its `-soft` background at 4.5:1 or better in every theme.

The consumer provides the state and an optional one-line message. Use `role="status"` so the result is announced.

The revealed answer (`pl-answer`) is neutral, never coloured: it is information, not a verdict. It shows only the final result, per Show Answer.
