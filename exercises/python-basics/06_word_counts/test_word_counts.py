from word_counts import word_counts


def test_counts_repeated_words():
    assert word_counts("the cat and the hat") == {"the": 2, "cat": 1, "and": 1, "hat": 1}


def test_ignores_case():
    assert word_counts("Python python PYTHON") == {"python": 3}


def test_ignores_punctuation():
    assert word_counts("Hi! Hi, you. Really?") == {"hi": 2, "you": 1, "really": 1}


def test_extra_spaces():
    assert word_counts("  spaced   out  ") == {"spaced": 1, "out": 1}


def test_empty_text():
    assert word_counts("") == {}
