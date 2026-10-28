import pytest

from confusion_matrix import confusion_matrix, f1, precision, recall, tnr

PAIRS = (
    [("FAIL", "FAIL")] * 6
    + [("FAIL", "PASS")] * 2
    + [("PASS", "FAIL")] * 3
    + [("PASS", "PASS")] * 9
)


def test_confusion_matrix():
    assert confusion_matrix(PAIRS) == {"tp": 6, "fp": 3, "fn": 2, "tn": 9}


def test_metrics():
    cm = confusion_matrix(PAIRS)
    assert precision(cm) == pytest.approx(6 / 9)
    assert recall(cm) == pytest.approx(6 / 8)
    assert f1(cm) == pytest.approx(2 * (6 / 9) * (6 / 8) / ((6 / 9) + (6 / 8)))
    assert tnr(cm) == pytest.approx(9 / 12)


def test_other_positive_class():
    cm = confusion_matrix(PAIRS, positive="PASS")
    assert cm == {"tp": 9, "fp": 2, "fn": 3, "tn": 6}


def test_always_pass_judge_is_useless():
    pairs = [("FAIL", "PASS")] * 2 + [("PASS", "PASS")] * 18
    cm = confusion_matrix(pairs)
    # It agrees with you 90% of the time...
    assert (cm["tp"] + cm["tn"]) / len(pairs) == pytest.approx(0.9)
    # ...but catches no failures.
    assert recall(cm) == 0.0
    assert precision(cm) == 0.0
    assert f1(cm) == 0.0
    assert tnr(cm) == 1.0


def test_empty():
    cm = confusion_matrix([])
    assert cm == {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    assert precision(cm) == recall(cm) == f1(cm) == tnr(cm) == 0.0


def test_perfect_judge():
    cm = confusion_matrix([("FAIL", "FAIL"), ("PASS", "PASS")])
    assert precision(cm) == recall(cm) == f1(cm) == tnr(cm) == 1.0
