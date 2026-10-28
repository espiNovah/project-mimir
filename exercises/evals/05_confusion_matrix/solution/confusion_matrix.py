def _ratio(num: int, den: int) -> float:
    return num / den if den else 0.0


def confusion_matrix(pairs: list[tuple[str, str]], positive: str = "FAIL") -> dict[str, int]:
    """Count tp, fp, fn and tn from (human, judge) label pairs."""
    cm = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for human, judge in pairs:
        actual = human == positive
        predicted = judge == positive
        if actual and predicted:
            cm["tp"] += 1
        elif predicted:
            cm["fp"] += 1
        elif actual:
            cm["fn"] += 1
        else:
            cm["tn"] += 1
    return cm


def precision(cm: dict[str, int]) -> float:
    """tp / (tp + fp), or 0.0 if the judge never predicted positive."""
    return _ratio(cm["tp"], cm["tp"] + cm["fp"])


def recall(cm: dict[str, int]) -> float:
    """tp / (tp + fn), or 0.0 if there were no real positives. Also called TPR."""
    return _ratio(cm["tp"], cm["tp"] + cm["fn"])


def f1(cm: dict[str, int]) -> float:
    """Harmonic mean of precision and recall, or 0.0 if both are 0."""
    p, r = precision(cm), recall(cm)
    return _ratio(2 * p * r, p + r)


def tnr(cm: dict[str, int]) -> float:
    """tn / (tn + fp), or 0.0 if there were no real negatives."""
    return _ratio(cm["tn"], cm["tn"] + cm["fp"])
