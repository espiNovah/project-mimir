import math

import pytest

from pass_rate_se import confidence_interval, is_real_improvement, pass_rate, standard_error

RESULTS = [True] * 41 + [False] * 9


def test_pass_rate():
    assert pass_rate(RESULTS) == pytest.approx(0.82)
    assert pass_rate([True, False]) == 0.5


def test_standard_error():
    assert standard_error(RESULTS) == pytest.approx(math.sqrt(0.82 * 0.18 / 50))
    assert standard_error([True] * 10) == 0.0


def test_more_cases_smaller_error():
    assert standard_error([True, False] * 200) < standard_error([True, False] * 20)


def test_confidence_interval():
    low, high = confidence_interval(RESULTS)
    se = math.sqrt(0.82 * 0.18 / 50)
    assert low == pytest.approx(0.82 - 1.96 * se)
    assert high == pytest.approx(0.82 + 1.96 * se)


def test_confidence_interval_custom_z():
    low, high = confidence_interval([True, False] * 50, z=1.0)
    assert (low, high) == (pytest.approx(0.45), pytest.approx(0.55))


def test_interval_is_clipped():
    low, high = confidence_interval([True] * 9 + [False])
    assert high == 1.0
    assert 0.0 < low < 0.9
    assert confidence_interval([False] * 3 + [True])[0] == 0.0


def test_small_gain_is_not_real():
    old = [True] * 41 + [False] * 9  # 82%
    new = [True] * 42 + [False] * 8  # 84%
    assert is_real_improvement(old, new) is False


def test_big_gain_on_big_eval_is_real():
    old = [True] * 600 + [False] * 400  # 60%
    new = [True] * 800 + [False] * 200  # 80%
    assert is_real_improvement(old, new) is True
    assert is_real_improvement(new, old) is False


def test_empty_raises():
    for func in (pass_rate, standard_error, confidence_interval):
        with pytest.raises(ValueError):
            func([])
