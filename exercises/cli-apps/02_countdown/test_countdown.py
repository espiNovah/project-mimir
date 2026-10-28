from datetime import date, timedelta

import pytest

from countdown import days_between, main


def test_days_between():
    assert days_between(date(2026, 12, 25), date(2027, 1, 1)) == 7
    assert days_between(date(2027, 1, 1), date(2026, 12, 25)) == -7


def test_days(capsys):
    assert main(["2027-01-01", "--since", "2026-12-25"]) == 0
    out = capsys.readouterr()
    assert out.out.strip() == "7 days until 2027-01-01"
    assert out.err == ""


def test_weeks(capsys):
    assert main(["2027-01-01", "--since", "2026-12-15", "--weeks"]) == 0
    assert capsys.readouterr().out.strip() == "2 weeks and 3 days until 2027-01-01"


def test_same_day_is_not_past(capsys):
    assert main(["2026-10-28", "--since", "2026-10-28"]) == 0
    assert capsys.readouterr().out.strip() == "0 days until 2026-10-28"


def test_past_date_goes_to_stderr(capsys):
    assert main(["2020-01-01", "--since", "2026-12-25"]) == 1
    out = capsys.readouterr()
    assert out.out == ""
    assert out.err.strip() == "error: 2020-01-01 is in the past"


def test_since_defaults_to_today(capsys):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert main([tomorrow]) == 0
    assert capsys.readouterr().out.strip() == f"1 days until {tomorrow}"


def test_bad_date_is_usage_error():
    with pytest.raises(SystemExit) as exc:
        main(["2026-13-01"])
    assert exc.value.code == 2
