from parse_log_lines import parse_line, slow_requests

LOG = """\
2026-10-28 14:03:11 INFO model=cheap latency_ms=1834 status=200
2026-10-28 14:03:15 WARNING model=capable latency_ms=4120 status=200
this line is garbage
2026-10-28 14:03:20 ERROR model=cheap latency_ms=30001 status=529
2026-10-28 14:03:21 INFO model=cheap latency_ms=fast status=200
"""


def test_parse_valid_line():
    assert parse_line("2026-10-28 14:03:11 INFO model=cheap latency_ms=1834 status=200") == {
        "date": "2026-10-28",
        "time": "14:03:11",
        "level": "INFO",
        "model": "cheap",
        "latency_ms": 1834,
        "status": 200,
    }


def test_numbers_are_ints():
    row = parse_line("2026-10-28 14:03:20 ERROR model=cheap latency_ms=30001 status=529")
    assert row["latency_ms"] == 30001 and isinstance(row["latency_ms"], int)
    assert row["status"] == 529 and isinstance(row["status"], int)


def test_model_names_with_dashes():
    row = parse_line("2026-10-28 09:00:00 INFO model=capable-v2 latency_ms=10 status=200")
    assert row["model"] == "capable-v2"


def test_garbage_returns_none():
    assert parse_line("this line is garbage") is None
    assert parse_line("") is None


def test_non_numeric_latency_returns_none():
    assert parse_line("2026-10-28 14:03:21 INFO model=cheap latency_ms=fast status=200") is None


def test_extra_text_returns_none():
    line = "2026-10-28 14:03:11 INFO model=cheap latency_ms=1834 status=200 retry=1"
    assert parse_line(line) is None


def test_slow_requests():
    assert slow_requests(LOG.splitlines()) == [
        ("14:03:15", "capable", 4120),
        ("14:03:20", "cheap", 30001),
    ]


def test_slow_requests_custom_threshold():
    assert slow_requests(LOG.splitlines(), threshold_ms=5000) == [("14:03:20", "cheap", 30001)]
    assert len(slow_requests(LOG.splitlines(), threshold_ms=0)) == 3
