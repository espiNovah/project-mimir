import time

from dedupe_documents import dedupe


def test_example():
    docs = ["Reset your password", "reset  your password ", "Billing FAQ"]
    assert dedupe(docs) == ["Reset your password", "Billing FAQ"]


def test_keeps_first_occurrence_and_order():
    docs = ["b", "A", "a", "B", "c"]
    assert dedupe(docs) == ["b", "A", "c"]


def test_whitespace_kinds():
    assert dedupe(["one\ttwo", "one\n two", "one two"]) == ["one\ttwo"]


def test_empty():
    assert dedupe([]) == []


def test_input_unchanged():
    docs = ["x", "X"]
    dedupe(docs)
    assert docs == ["x", "X"]


def test_fast_on_many_documents():
    docs = [f"Document {i}: notes about topic {i % 7}" for i in range(30_000)]
    docs += docs[:100]  # a few duplicates at the end
    start = time.perf_counter()
    result = dedupe(docs)
    elapsed = time.perf_counter() - start
    assert len(result) == 30_000
    assert elapsed < 0.5, f"took {elapsed:.2f} s; is there a hidden O(n) step inside the loop?"
