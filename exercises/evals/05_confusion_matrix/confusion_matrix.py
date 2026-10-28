def confusion_matrix(pairs: list[tuple[str, str]], positive: str = "FAIL") -> dict[str, int]:
    """Count tp, fp, fn and tn from (human, judge) label pairs."""
    raise NotImplementedError("Write this function")


def precision(cm: dict[str, int]) -> float:
    """tp / (tp + fp), or 0.0 if the judge never predicted positive."""
    raise NotImplementedError("Write this function")


def recall(cm: dict[str, int]) -> float:
    """tp / (tp + fn), or 0.0 if there were no real positives. Also called TPR."""
    raise NotImplementedError("Write this function")


def f1(cm: dict[str, int]) -> float:
    """Harmonic mean of precision and recall, or 0.0 if both are 0."""
    raise NotImplementedError("Write this function")


def tnr(cm: dict[str, int]) -> float:
    """tn / (tn + fp), or 0.0 if there were no real negatives."""
    raise NotImplementedError("Write this function")
