import time

import pytest

from timed_block import timed_block


def test_records_label_and_time():
    log = []
    with timed_block("sleep", log):
        time.sleep(0.05)
    assert len(log) == 1
    label, seconds = log[0]
    assert label == "sleep"
    assert 0.04 <= seconds < 1.0


def test_records_even_when_block_raises():
    log = []
    with pytest.raises(ZeroDivisionError):
        with timed_block("broken", log):
            1 / 0
    assert [entry[0] for entry in log] == ["broken"]


def test_multiple_blocks_append_in_order():
    log = []
    with timed_block("a", log):
        pass
    with timed_block("b", log):
        pass
    assert [entry[0] for entry in log] == ["a", "b"]
