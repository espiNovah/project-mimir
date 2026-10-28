# Bug: model names were used as-is, so "Capable " and "capable" became separate keys.


def average_lengths(replies: list[dict]) -> dict[str, float]:
    """Return {model: average len(text)} with model names cleaned up (stripped, lowercase)."""
    totals = {}
    counts = {}
    for reply in replies:
        model = reply["model"].strip().lower()
        totals[model] = totals.get(model, 0) + len(reply["text"])
        counts[model] = counts.get(model, 0) + 1
    return {model: totals[model] / counts[model] for model in totals}
