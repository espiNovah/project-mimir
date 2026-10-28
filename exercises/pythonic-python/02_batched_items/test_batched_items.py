import inspect
import itertools

import pytest

from batched_items import batched_items


def test_is_a_generator_function():
    assert inspect.isgeneratorfunction(batched_items)


def test_even_split():
    assert list(batched_items([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]


def test_last_batch_smaller():
    assert list(batched_items("abcde", 2)) == [["a", "b"], ["c", "d"], ["e"]]


def test_empty_input():
    assert list(batched_items([], 3)) == []


def test_works_on_endless_input():
    endless = itertools.count()
    batches = batched_items(endless, 3)
    assert next(batches) == [0, 1, 2]
    assert next(batches) == [3, 4, 5]


def test_bad_size():
    with pytest.raises(ValueError):
        list(batched_items([1, 2], 0))
