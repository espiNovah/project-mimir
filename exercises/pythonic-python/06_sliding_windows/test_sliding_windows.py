import inspect

import pytest

from sliding_windows import sliding_windows

WORDS = "a b c d e f g".split()


def test_is_generator_function():
    assert inspect.isgeneratorfunction(sliding_windows)


def test_no_overlap():
    assert list(sliding_windows(WORDS, 3, 0)) == [["a", "b", "c"], ["d", "e", "f"], ["g"]]


def test_with_overlap():
    assert list(sliding_windows(WORDS, 4, 2)) == [
        ["a", "b", "c", "d"],
        ["c", "d", "e", "f"],
        ["e", "f", "g"],
    ]


def test_stops_when_window_reaches_end():
    # The last window ends exactly at the end, so no tiny extra window.
    assert list(sliding_windows(list("abcd"), 2, 0)) == [["a", "b"], ["c", "d"]]
    assert list(sliding_windows(list("abcde"), 3, 1)) == [["a", "b", "c"], ["c", "d", "e"]]


def test_short_input_gives_one_window():
    assert list(sliding_windows(["x"], 5, 2)) == [["x"]]


def test_empty_input():
    assert list(sliding_windows([], 3, 1)) == []


@pytest.mark.parametrize("size, overlap", [(0, 0), (3, 3), (3, -1)])
def test_bad_arguments(size, overlap):
    with pytest.raises(ValueError):
        list(sliding_windows(WORDS, size, overlap))
