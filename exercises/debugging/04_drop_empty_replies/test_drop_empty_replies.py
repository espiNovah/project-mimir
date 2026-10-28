from drop_empty_replies import drop_empty_replies


def test_single_empty():
    assert drop_empty_replies(["Paris", "", "Lima"]) == ["Paris", "Lima"]


def test_consecutive_empties():
    assert drop_empty_replies(["Paris", "", "", "  ", "Lima"]) == ["Paris", "Lima"]


def test_all_empty():
    assert drop_empty_replies(["", "\n", " "]) == []


def test_input_is_not_modified():
    raw = ["Paris", "", "Lima"]
    drop_empty_replies(raw)
    assert raw == ["Paris", "", "Lima"]


def test_returns_a_new_list():
    raw = ["Paris", "Lima"]
    result = drop_empty_replies(raw)
    assert result == ["Paris", "Lima"]
    assert result is not raw
