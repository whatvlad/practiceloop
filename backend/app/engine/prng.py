"""A versioned deterministic stream for problem generation, not security tokens."""

from collections.abc import Callable
from hashlib import sha256

_SPACE = 1 << 256
_MAX_SEED = 10**16
_DOMAIN = b"PracticeLoop PRNG v1\x00"


class DeterministicRNG:
    """SHA-256 of a fixed-width seed and counter; outputs are frozen for v1."""

    def __init__(self, seed: int) -> None:
        if type(seed) is not int or not 0 <= seed < _MAX_SEED:
            raise ValueError("Seed must be an integer from 0 to 9999999999999999")
        self._seed = seed.to_bytes(8, "big")
        self._counter = 0

    def randbelow(self, upper: int) -> int:
        """Return an unbiased value in [0, upper), using bounded rejection."""
        if type(upper) is not int or not 1 <= upper <= _SPACE:
            raise ValueError("Upper bound must be an integer from 1 through 2**256")
        limit = _SPACE - _SPACE % upper
        for _ in range(128):
            if self._counter >= 1 << 64:
                raise OverflowError("PRNG counter exhausted")
            data = _DOMAIN + self._seed + self._counter.to_bytes(8, "big")
            self._counter += 1
            value = int.from_bytes(sha256(data).digest(), "big")
            if value < limit:
                return value % upper
        raise RuntimeError("PRNG rejection limit reached")


def draw_valid[T](
    draw: Callable[[], T], is_valid: Callable[[T], bool], *, max_attempts: int = 64
) -> T:
    """Draw in order until a candidate passes, or fail at the declared cap."""
    if type(max_attempts) is not int or not 1 <= max_attempts <= 64:
        raise ValueError("max_attempts must be an integer from 1 through 64")
    for _ in range(max_attempts):
        candidate = draw()
        if is_valid(candidate):
            return candidate
    raise ValueError(f"No valid candidate after {max_attempts} draws")
