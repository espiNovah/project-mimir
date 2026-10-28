from normalize_dates import find_dates, us_to_iso


def test_single_date():
    assert us_to_iso("10/28/2026") == "2026-10-28"


def test_dates_inside_text():
    text = "Released 10/28/2026, patched 11/02/2026."
    assert us_to_iso(text) == "Released 2026-10-28, patched 2026-11-02."


def test_iso_dates_untouched():
    assert us_to_iso("Kickoff 2026-09-01") == "Kickoff 2026-09-01"


def test_not_part_of_longer_numbers():
    assert us_to_iso("id 110/28/20261") == "id 110/28/20261"


def test_single_digit_parts_are_not_rewritten():
    assert us_to_iso("on 1/2/2026") == "on 1/2/2026"


def test_find_dates_mixed():
    assert find_dates("Kickoff 2026-09-01, review 10/28/2026, ship 2026-12-01") == [
        "2026-09-01",
        "2026-10-28",
        "2026-12-01",
    ]


def test_find_dates_none():
    assert find_dates("No dates, just 42 tokens and v1.2.3") == []
