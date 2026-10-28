import logging

import pytest

from retry_logging import call_with_retries


def flaky(failures: int, result="Paris"):
    """Return a function that times out `failures` times, then returns result."""
    calls = {"n": 0}

    def func():
        calls["n"] += 1
        if calls["n"] <= failures:
            raise TimeoutError("model took too long")
        return result

    func.calls = calls
    return func


def records(caplog):
    return [(r.levelname, r.getMessage()) for r in caplog.records if r.name == "retry"]


def test_success_first_try(caplog):
    caplog.set_level(logging.DEBUG)
    assert call_with_retries(flaky(0)) == "Paris"
    assert records(caplog) == [("INFO", "succeeded on attempt 1")]


def test_success_after_timeouts(caplog):
    caplog.set_level(logging.DEBUG)
    assert call_with_retries(flaky(2), attempts=3) == "Paris"
    assert records(caplog) == [
        ("WARNING", "timeout on attempt 1 of 3"),
        ("WARNING", "timeout on attempt 2 of 3"),
        ("INFO", "succeeded on attempt 3"),
    ]


def test_gives_up(caplog):
    caplog.set_level(logging.DEBUG)
    func = flaky(10)
    assert call_with_retries(func, attempts=2) is None
    assert func.calls["n"] == 2
    assert records(caplog) == [
        ("WARNING", "timeout on attempt 1 of 2"),
        ("WARNING", "timeout on attempt 2 of 2"),
        ("ERROR", "gave up after 2 attempts"),
    ]


def test_timeouts_visible_at_info_level(caplog):
    caplog.set_level(logging.INFO)
    call_with_retries(flaky(1))
    assert ("WARNING", "timeout on attempt 1 of 3") in records(caplog)


def test_other_errors_are_not_retried():
    def broken():
        raise ValueError("bad request")

    with pytest.raises(ValueError):
        call_with_retries(broken)
