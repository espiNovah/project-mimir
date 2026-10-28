import pytest

from chunk_text import chunk_text


def test_exact_fit_with_overlap():
    assert chunk_text("abcdefghij", size=4, overlap=1) == ["abcd", "defg", "ghij"]


def test_short_tail_is_kept():
    assert chunk_text("abcdefghijk", size=4, overlap=1) == ["abcd", "defg", "ghij", "jk"]


def test_no_overlap():
    assert chunk_text("abcdef", size=2) == ["ab", "cd", "ef"]


def test_text_shorter_than_size():
    assert chunk_text("abc", size=10) == ["abc"]


def test_text_exactly_size():
    assert chunk_text("abcd", size=4, overlap=2) == ["abcd"]


def test_empty_text():
    assert chunk_text("", size=4) == []


def test_nothing_is_lost():
    text = "The quick brown fox jumps over the lazy dog." * 3
    chunks = chunk_text(text, size=20, overlap=5)
    assert chunks[0].startswith("The quick")
    assert text.endswith(chunks[-1])


def test_bad_overlap():
    with pytest.raises(ValueError):
        chunk_text("abc", size=4, overlap=4)
