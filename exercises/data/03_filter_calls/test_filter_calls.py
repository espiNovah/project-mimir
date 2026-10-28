from pathlib import Path

import pandas as pd
import pytest

from filter_calls import for_models, load_calls, missing_counts, slow_failures

CSV = Path(__file__).parent / "calls.csv"


@pytest.fixture
def df():
    return load_calls(CSV)


def test_load(df):
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (12, 7)
    assert df["latency_ms"].dtype == "float64"  # floats, because of the gaps
    assert df["passed"].dtype == bool


def test_missing_counts(df):
    assert missing_counts(df) == {"latency_ms": 2, "output_tokens": 2}


def test_missing_counts_clean_frame():
    assert missing_counts(pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})) == {}


def test_slow_failures(df):
    assert slow_failures(df)["trace_id"].tolist() == ["t07", "t10"]


def test_slow_failures_threshold(df):
    assert slow_failures(df, threshold_ms=1000)["trace_id"].tolist() == ["t02", "t07", "t10"]


def test_slow_failures_keeps_all_columns(df):
    assert list(slow_failures(df).columns) == list(df.columns)


def test_for_models(df):
    capable = for_models(df, ["capable"])
    assert capable["trace_id"].tolist() == ["t03", "t05", "t07", "t09", "t12"]
    assert len(for_models(df, ["cheap", "capable"])) == 12
    assert len(for_models(df, [])) == 0


def test_input_not_changed(df):
    before = df.copy()
    slow_failures(df)
    for_models(df, ["cheap"])
    pd.testing.assert_frame_equal(df, before)
