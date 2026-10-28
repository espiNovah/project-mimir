import random
import statistics

import pytest

from bootstrap_ci import bootstrap_ci


def mean(xs):
    return sum(xs) / len(xs)


def tpr(pairs):
    """pairs are (human, judge); FAIL is the positive class."""
    on_fails = [judge for human, judge in pairs if human == "FAIL"]
    return sum(j == "FAIL" for j in on_fails) / len(on_fails)


RESULTS = [True] * 70 + [False] * 30


def test_close_to_normal_approximation():
    low, high = bootstrap_ci(RESULTS, mean)
    # The normal approximation gives 0.70 +/- 0.09.
    assert 0.58 <= low <= 0.64
    assert 0.76 <= high <= 0.82


def test_contains_the_estimate():
    low, high = bootstrap_ci(RESULTS, mean)
    assert low < mean(RESULTS) < high


def test_same_seed_same_interval():
    assert bootstrap_ci(RESULTS, mean, seed=7) == bootstrap_ci(RESULTS, mean, seed=7)


def test_does_not_use_global_random():
    random.seed(123)
    a = bootstrap_ci(RESULTS, mean)
    random.seed(456)
    b = bootstrap_ci(RESULTS, mean)
    assert a == b


def test_different_seeds_differ():
    intervals = {bootstrap_ci(RESULTS, mean, n_resamples=200, seed=s) for s in range(5)}
    assert len(intervals) > 1


def test_resamples_have_the_same_length():
    assert bootstrap_ci(list(range(37)), len, n_resamples=50) == (37, 37)


def test_constant_data():
    assert bootstrap_ci([0.5] * 20, mean, n_resamples=100) == (0.5, 0.5)


def test_more_data_narrower_interval():
    small = bootstrap_ci([True] * 7 + [False] * 3, mean)
    big = bootstrap_ci([True] * 700 + [False] * 300, mean, n_resamples=500)
    assert (big[1] - big[0]) < (small[1] - small[0])


def test_other_statistics():
    latencies = [0.8, 0.9, 1.1, 1.2, 1.3, 2.0, 2.2, 3.5, 30.0, 0.7]
    low, high = bootstrap_ci(latencies, statistics.median)
    assert low <= statistics.median(latencies) <= high


def test_skips_zero_division():
    # Only 2 FAILs in 20 pairs, so many resamples contain none and tpr() divides by zero.
    pairs = [("FAIL", "FAIL"), ("FAIL", "PASS")] + [("PASS", "PASS")] * 18
    low, high = bootstrap_ci(pairs, tpr)
    assert 0.0 <= low <= 0.5 <= high <= 1.0


def test_all_skipped_raises():
    with pytest.raises(ValueError):
        bootstrap_ci([("PASS", "PASS")] * 5, tpr, n_resamples=20)


def test_empty_raises():
    with pytest.raises(ValueError):
        bootstrap_ci([], mean)
