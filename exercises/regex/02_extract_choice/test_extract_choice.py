import pytest

from extract_choice import extract_choice


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("Answer: B", "B"),
        ("answer: a", "A"),
        ("ANSWER - D", "D"),
        ("**Answer:** c) Because the loop never ends.", "C"),
        ("The answer is (B).", None),  # "is" is a word, so it doesn't fit the format
        ("Final answer:\n\nD", "D"),
    ],
)
def test_formats(reply, expected):
    assert extract_choice(reply) == expected


def test_last_answer_wins():
    assert extract_choice("I considered answer A, but my final answer: D.") == "D"


def test_letter_must_stand_alone():
    assert extract_choice("Answer: Because it is faster.") is None


def test_letters_outside_a_to_d():
    assert extract_choice("Answer: E") is None


def test_no_answer():
    assert extract_choice("I'm not sure.") is None
    assert extract_choice("") is None
