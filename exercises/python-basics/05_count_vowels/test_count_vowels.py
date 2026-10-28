from count_vowels import count_vowels


def test_simple_word():
    assert count_vowels("hello") == 2


def test_uppercase_counts():
    assert count_vowels("AEIOU") == 5


def test_mixed_sentence():
    assert count_vowels("The quick brown fox") == 5


def test_no_vowels():
    assert count_vowels("rhythm") == 0


def test_empty_string():
    assert count_vowels("") == 0


def test_numbers_and_symbols_ignored():
    assert count_vowels("a1!e2?") == 2
