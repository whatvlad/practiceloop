# Quadratic remainder practice

Implement the approved algebra30 exercise 63(b) slice from
`docs/architecture/algebra30-remainder-design.md`.

1. Add a failing test in `backend/tests/test_engine_algebra_expansion.py` for
   the PDF example, equivalent and incorrect answers, and replay.
2. Add a bounded, versioned generator to `algebra_expansion.py` and register it
   for level 2 of polynomial division in `engine/topics/catalogue.py`. Retain
   every existing generator and code unchanged.
3. Pin three new golden problems; sweep generated parameters against exact
   polynomial division and check the existing worker on Linux.
4. Run focused engine, topic and API checks; review the diff and report any
   environment-dependent checks that could not run.
