import pytest

from call_cost import call_cost, total_cost


def test_input_only():
    assert call_cost("cheap", 1_000_000, 0) == pytest.approx(1.0)


def test_output_only():
    assert call_cost("cheap", 0, 1_000_000) == pytest.approx(5.0)


def test_typical_call():
    # 2,000 input tokens at $3/M plus 500 output tokens at $15/M
    assert call_cost("capable", 2_000, 500) == pytest.approx(0.006 + 0.0075)


def test_total_cost():
    calls = [
        {"model": "cheap", "input_tokens": 10_000, "output_tokens": 1_000},
        {"model": "capable", "input_tokens": 1_000, "output_tokens": 2_000},
    ]
    assert total_cost(calls) == pytest.approx(0.015 + 0.033)


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        call_cost("mystery", 1, 1)
