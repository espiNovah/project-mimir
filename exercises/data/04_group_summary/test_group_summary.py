from pathlib import Path

import pandas as pd
import pytest

from group_summary import pass_rate_by_version, summary_by_model

CSV = Path(__file__).parent / "calls.csv"


@pytest.fixture
def df():
    return pd.read_csv(CSV)


def test_shape_and_columns(df):
    summary = summary_by_model(df)
    assert list(summary.columns) == ["model", "calls", "timed", "mean_latency_ms", "pass_rate"]
    assert summary["model"].tolist() == ["capable", "cheap"]


def test_counts(df):
    summary = summary_by_model(df).set_index("model")
    assert summary.loc["capable", "calls"] == 5
    assert summary.loc["capable", "timed"] == 4
    assert summary.loc["cheap", "calls"] == 7
    assert summary.loc["cheap", "timed"] == 6


def test_means(df):
    summary = summary_by_model(df).set_index("model")
    assert summary.loc["capable", "mean_latency_ms"] == pytest.approx(2632.5)
    assert summary.loc["cheap", "mean_latency_ms"] == pytest.approx(1475.0)
    assert summary.loc["capable", "pass_rate"] == pytest.approx(0.6)
    assert summary.loc["cheap", "pass_rate"] == pytest.approx(4 / 7)


def test_pass_rate_by_version(df):
    assert pass_rate_by_version(df) == {"v1": pytest.approx(0.6), "v2": pytest.approx(4 / 7)}


def test_works_on_other_data():
    tiny = pd.DataFrame(
        {
            "trace_id": ["a", "b", "c"],
            "model": ["m2", "m1", "m2"],
            "prompt_version": ["x", "x", "y"],
            "latency_ms": [100.0, 200.0, float("nan")],
            "passed": [True, False, False],
        }
    )
    summary = summary_by_model(tiny)
    assert summary["model"].tolist() == ["m1", "m2"]
    assert summary["calls"].tolist() == [1, 2]
    assert summary["timed"].tolist() == [1, 1]
    assert pass_rate_by_version(tiny) == {"x": 0.5, "y": 0.0}
