import pytest

from exact_match import accuracy, exact_match, grade, normalize


@pytest.mark.parametrize(
    ("raw", "clean"),
    [
        ("  The  Answer is Paris!! ", "the answer is paris"),
        ("Paris.", "paris"),
        ("billing\n", "billing"),
        ("42", "42"),
        ("3.14", "3.14"),  # only trailing punctuation goes
        ("", ""),
    ],
)
def test_normalize(raw, clean):
    assert normalize(raw) == clean


def test_exact_match():
    assert exact_match("Paris.", "paris") is True
    assert exact_match("Paris, France", "Paris") is False
    assert exact_match("feature_request", "feature request") is False


def test_exact_match_any_of_list():
    assert exact_match("NYC", ["New York", "NYC"]) is True
    assert exact_match("new york!", ["New York", "NYC"]) is True
    assert exact_match("Boston", ["New York", "NYC"]) is False


def test_grade():
    assert grade(["4", "five", " 6 "], ["4", "5", "6"]) == [True, False, True]


def test_grade_length_mismatch():
    with pytest.raises(ValueError):
        grade(["a", "b"], ["a"])


def test_accuracy():
    assert accuracy(["4", "five"], ["4", "5"]) == 0.5
    assert accuracy([], []) == 0.0
