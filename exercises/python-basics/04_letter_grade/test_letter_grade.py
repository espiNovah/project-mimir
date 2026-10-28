from letter_grade import letter_grade


def test_top_scores_are_a():
    assert letter_grade(100) == "A"
    assert letter_grade(90) == "A"


def test_boundaries():
    assert letter_grade(89.9) == "B"
    assert letter_grade(80) == "B"
    assert letter_grade(70) == "C"
    assert letter_grade(60) == "D"


def test_failing():
    assert letter_grade(59) == "F"
    assert letter_grade(0) == "F"


def test_out_of_range():
    assert letter_grade(-1) == "Invalid score"
    assert letter_grade(101) == "Invalid score"
