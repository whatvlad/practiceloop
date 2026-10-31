"""Private, versioned problem codes with a two-digit typo check."""

import re
from dataclasses import dataclass
from hashlib import sha256

from app.engine.registry import Registry

_CODE = re.compile(r"([A-Z]{2,8})([1-9][0-9]{0,3})([0-9]{16})([0-9]{2})", re.ASCII)


@dataclass(frozen=True, slots=True)
class ProblemCode:
    prefix: str
    version: int
    seed: int


def _check(prefix: str, version: int, seed: int) -> str:
    # Position weights are distinct and nonzero modulo prime 97: any one-digit
    # change or swap of unequal digits in the version/seed changes the residue.
    digits = f"{version}{seed:016d}"
    salt = int.from_bytes(sha256(prefix.encode("ascii")).digest()[:2], "big")
    value = (salt + sum(i * int(digit) for i, digit in enumerate(digits, 1))) % 97
    return f"{value:02d}"


def format_code(code: ProblemCode, registry: Registry) -> str:
    if type(code.version) is not int:
        raise ValueError("Invalid problem code version")
    registry.get_code(code.prefix, code.version)
    if type(code.seed) is not int or not 0 <= code.seed < 10**16:
        raise ValueError("Code seed must be a 16-digit nonnegative integer")
    check = _check(code.prefix, code.version, code.seed)
    return f"{code.prefix}-{code.version}-{code.seed:016d}-{check}"


def parse_code(text: str, registry: Registry) -> ProblemCode:
    if not isinstance(text, str) or not text.isascii() or len(text) > 128:
        raise ValueError("Invalid problem code")
    compact = "".join(char for char in text if char != "-" and not char.isspace()).upper()
    match = _CODE.fullmatch(compact)
    if match is None:
        raise ValueError("Invalid problem code")
    prefix, version_text, seed_text, check = match.groups()
    code = ProblemCode(prefix, int(version_text), int(seed_text))
    registry.get_code(code.prefix, code.version)
    if check != _check(code.prefix, code.version, code.seed):
        raise ValueError("Invalid problem code check digits")
    return code
