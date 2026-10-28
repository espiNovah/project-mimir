from pathlib import Path

import pytest

from read_traces import count_categories, error_rate_by_version, load_traces

TRACES = Path(__file__).parent / "traces.jsonl"


def test_load_skips_blank_lines():
    traces = load_traces(TRACES)
    assert len(traces) == 10
    assert traces[0]["trace_id"] == "a1f3"
    assert traces[-1]["trace_id"] == "b6e2"


def test_load_keeps_types():
    traces = load_traces(TRACES)
    assert traces[0]["error"] is None
    assert traces[1]["output"] is None
    assert traces[1]["latency_s"] == 30.0


def test_load_accepts_str_path():
    assert len(load_traces(str(TRACES))) == 10


def test_error_rate_by_version():
    rates = error_rate_by_version(load_traces(TRACES))
    assert rates == {"few-shot-v1": pytest.approx(0.25), "few-shot-v2": pytest.approx(2 / 6)}


def test_error_rate_all_ok():
    traces = [{"prompt_version": "v9", "error": None}] * 3
    assert error_rate_by_version(traces) == {"v9": 0.0}


def test_count_categories():
    notes = [
        {"trace_id": "a4d2", "note": "refund AND login; picked billing", "category": "two topics"},
        {"trace_id": "b4c8", "note": "sarcasm read as a request", "category": "sarcasm"},
        {"trace_id": "b5d6", "note": "sentence instead of a label", "category": "extra text"},
        {"trace_id": "c0a1", "note": "two topics again", "category": "two topics"},
    ]
    assert count_categories(notes) == [("two topics", 2), ("extra text", 1), ("sarcasm", 1)]


def test_count_categories_empty():
    assert count_categories([]) == []
