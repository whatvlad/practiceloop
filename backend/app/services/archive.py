"""Old saved problems of a topic that moved to the new engine are a read-only archive (#190).

Such a problem keeps its stored statement, answer and solution steps, so history,
reopen and reveals work from the database alone. Nothing here replays or checks it:
this module must not import `app/generators`, which #199 removes. A check of an
archived problem is `409 problem_archived`, and its solution carries no visual.
"""

from typing import Any

from app.engine import practice as engine


def is_archived(topic: str, record: Any) -> bool:
    """True for an old-generator record of a topic now served by the new engine."""
    return topic in engine.ENGINE_TOPICS and not engine.is_engine_record(record)


def stored_solution(steps: Any) -> dict[str, Any]:
    """An archived problem's solution: the stored steps, with no visual."""
    return {"steps": list(steps)}
