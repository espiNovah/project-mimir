import numpy as np
import pytest

from latency_arrays import batch_cost, summarize_latencies


def test_summary_without_missing():
    lat = np.array([820, 1340, 640, 2950, 910, 1120], dtype=float)
    s = summarize_latencies(lat)
    assert s["count"] == 6
    assert s["missing"] == 0
    assert s["mean_ms"] == pytest.approx(1296.6667, rel=1e-4)
    assert s["p95_ms"] == pytest.approx(np.percentile(lat, 95))
    assert s["slow"] == 1


def test_summary_skips_nan():
    lat = np.array([820, 1340, np.nan, 2950])
    s = summarize_latencies(lat)
    assert s == {
        "count": 3,
        "missing": 1,
        "mean_ms": pytest.approx(1703.3333, rel=1e-4),
        "p95_ms": pytest.approx(2789.0),
        "slow": 1,
    }


def test_custom_threshold():
    lat = np.array([820, 1340, np.nan, 2950])
    assert summarize_latencies(lat, slow_ms=800)["slow"] == 3


def test_values_are_plain_python_numbers():
    s = summarize_latencies(np.array([1.0, 2.0, np.nan]))
    assert type(s["count"]) is int and type(s["missing"]) is int and type(s["slow"]) is int
    assert type(s["mean_ms"]) is float and type(s["p95_ms"]) is float


def test_batch_cost():
    cost = batch_cost(np.array([1_000_000, 0]), np.array([0, 1_000_000]), 1.0, 5.0)
    assert isinstance(cost, np.ndarray)
    assert cost.tolist() == pytest.approx([1.0, 5.0])


def test_batch_cost_typical():
    cost = batch_cost(np.array([2_000, 10_000]), np.array([500, 1_000]), 3.0, 15.0)
    assert cost.tolist() == pytest.approx([0.0135, 0.045])
    assert cost.sum() == pytest.approx(0.0585)
