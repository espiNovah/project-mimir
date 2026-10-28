from datetime import datetime, timezone

import pytest

from timestamps import format_local, parse_utc, within_last

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)


def test_parse_utc():
    dt = parse_utc("2026-10-28T14:03:12+00:00")
    assert dt == datetime(2026, 10, 28, 14, 3, 12, tzinfo=timezone.utc)
    assert dt.utcoffset().total_seconds() == 0


def test_parse_other_offset_converts_to_utc():
    dt = parse_utc("2026-10-28T15:03:12+01:00")
    assert dt.hour == 14
    assert dt.utcoffset().total_seconds() == 0


def test_naive_raises():
    with pytest.raises(ValueError):
        parse_utc("2026-10-28T14:03:12")


def test_within_last():
    stamps = [
        "2026-10-20T09:00:00+00:00",  # 8 days before: too old
        "2026-10-21T12:00:00+00:00",  # exactly 7 days before: included
        "2026-10-25T09:30:00+00:00",
        "2026-10-28T12:00:00+00:00",  # exactly now: included
        "2026-10-29T08:00:00+00:00",  # in the future: excluded
    ]
    assert within_last(stamps, NOW, days=7) == [
        "2026-10-21T12:00:00+00:00",
        "2026-10-25T09:30:00+00:00",
        "2026-10-28T12:00:00+00:00",
    ]


def test_within_last_compares_moments_not_text():
    # 13:30 in Lagos (UTC+1) is 12:30 UTC, which is after NOW.
    assert within_last(["2026-10-28T13:30:00+01:00"], NOW, days=1) == []
    # 12:30 in Lagos is 11:30 UTC, which is before NOW.
    assert within_last(["2026-10-28T12:30:00+01:00"], NOW, days=1) == ["2026-10-28T12:30:00+01:00"]


def test_format_local():
    assert format_local("2026-10-28T14:03:12+00:00", "Africa/Lagos") == "2026-10-28 15:03"
    assert format_local("2026-10-28T14:03:12+00:00", "Asia/Kolkata") == "2026-10-28 19:33"


def test_format_local_crosses_midnight():
    assert format_local("2026-10-28T23:30:00+00:00", "Asia/Tokyo") == "2026-10-29 08:30"
