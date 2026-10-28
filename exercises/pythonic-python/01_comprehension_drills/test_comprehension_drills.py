from comprehension_drills import even_squares, initials, word_lengths


def test_even_squares():
    assert even_squares([1, 2, 3, 4, 5, 6]) == [4, 16, 36]


def test_even_squares_keeps_order_and_negatives():
    assert even_squares([-2, 7, 0]) == [4, 0]


def test_even_squares_empty():
    assert even_squares([]) == []


def test_word_lengths():
    assert word_lengths(["agent", "tool", "a"]) == {"agent": 5, "tool": 4, "a": 1}


def test_initials():
    assert initials(["ada", "Alan", "grace", ""]) == {"A", "G"}
