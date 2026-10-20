"""Share tokens and codes (#37) without a database."""

from __future__ import annotations

import pytest

from app.services import shares


def test_tokens_are_random_url_safe_and_never_repeat() -> None:
    tokens = {shares.new_token() for _ in range(2000)}
    assert len(tokens) == 2000
    assert all(shares.valid_token(token) for token in tokens)


def test_codes_use_the_unambiguous_alphabet_and_never_repeat_in_practice() -> None:
    codes = {shares.new_code() for _ in range(2000)}
    assert len(codes) == 2000
    assert all(shares.normalize_code(code) == code for code in codes)
    assert not set("ILOU") & set("".join(codes))


@pytest.mark.parametrize(
    ("typed", "code"),
    [
        ("K7M2QX9P", "K7M2QX9P"),
        ("k7m2-qx9p", "K7M2QX9P"),
        (" K7M2 QX9P ", "K7M2QX9P"),
        ("O1IL-0000", "0111" + "0000"),  # misread letters map to the digits they look like
    ],
)
def test_typed_codes_are_normalized(typed: str, code: str) -> None:
    assert shares.normalize_code(typed) == code


@pytest.mark.parametrize("typed", ["", "K7M2QX9", "K7M2QX9PP", "K7M2QX9U", "K7M2_QX9P", "Ж7M2QX9P"])
def test_malformed_codes_are_rejected(typed: str) -> None:
    assert shares.normalize_code(typed) is None


@pytest.mark.parametrize("token", ["", "a" * 42, "a" * 44, "a" * 42 + "=", "a" * 42 + "/"])
def test_malformed_tokens_are_rejected(token: str) -> None:
    assert not shares.valid_token(token)
