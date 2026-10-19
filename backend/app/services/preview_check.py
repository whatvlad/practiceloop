"""Admission control only; all mathematics uses the shared #8 checker."""

from threading import BoundedSemaphore

from app.services.math_worker import MathCheckInconclusive, MathWorkerError
from app.services.math_worker import check_answer as shared_check

# One 256 MiB child leaves room for the parent inside Oracle's 512 MiB service limit.
_SLOTS = BoundedSemaphore(1)


def check_answer(answer: str, record: dict[str, object]) -> str:
    if not _SLOTS.acquire(blocking=False):
        raise MathWorkerError("Math workers busy")
    try:
        result = shared_check(answer, record)
        return "missing_constant" if result.missing_constant else result.result
    except MathCheckInconclusive as exc:
        raise MathWorkerError("Math check inconclusive") from exc
    finally:
        _SLOTS.release()
