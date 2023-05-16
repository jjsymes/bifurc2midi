"""Tests for hello function."""
import pytest


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Jeanette", "Jeanette"),
        ("Raven", "Raven"),
        ("Maxine", "Maxine"),
        ("Matteo", "Matteo"),
        ("Destinee", "Destinee"),
        ("Alden", "Alden"),
        ("Mariah", "Mariah"),
        ("Anika", "Anika"),
        ("Isabella", "Isabella"),
    ],
)
def test_hello(name, expected):
    """Example test with parametrization."""
    assert name == expected
