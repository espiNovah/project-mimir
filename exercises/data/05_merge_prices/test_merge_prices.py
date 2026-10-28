import math

import pandas as pd
import pytest

from merge_prices import add_costs, cost_by_model


@pytest.fixture
def prices():
    return pd.DataFrame(
        {"model": ["cheap", "capable"], "input_per_m": [1.0, 3.0], "output_per_m": [5.0, 15.0]}
    )


@pytest.fixture
def calls():
    return pd.DataFrame(
        {
            "trace_id": ["t1", "t2", "t3", "t4", "t5"],
            "model": ["capable", "cheap", "mystery", "cheap", "capable"],
            "input_tokens": [1_000, 10_000, 500, 2_000, 2_000],
            "output_tokens": [2_000, 1_000, 100, float("nan"), 500],
        }
    )


def test_costs(calls, prices):
    out = add_costs(calls, prices)
    assert out["trace_id"].tolist() == ["t1", "t2", "t3", "t4", "t5"]
    assert out.loc[0, "cost_usd"] == pytest.approx(0.033)
    assert out.loc[1, "cost_usd"] == pytest.approx(0.015)
    assert out.loc[4, "cost_usd"] == pytest.approx(0.0135)


def test_unknown_model_kept_with_missing_cost(calls, prices):
    out = add_costs(calls, prices)
    assert len(out) == len(calls)
    assert math.isnan(out.loc[2, "cost_usd"])


def test_missing_tokens_mean_missing_cost(calls, prices):
    assert math.isnan(add_costs(calls, prices).loc[3, "cost_usd"])


def test_duplicate_prices_raise(calls, prices):
    dup = pd.concat([prices, prices.iloc[[0]]], ignore_index=True)
    with pytest.raises(pd.errors.MergeError):
        add_costs(calls, dup)


def test_cost_by_model(calls, prices):
    totals = cost_by_model(add_costs(calls, prices))
    assert totals["capable"] == pytest.approx(0.033 + 0.0135)
    assert totals["cheap"] == pytest.approx(0.015)
    assert totals["mystery"] == 0.0


def test_calls_not_changed(calls, prices):
    before = calls.copy()
    add_costs(calls, prices)
    pd.testing.assert_frame_equal(calls, before)
