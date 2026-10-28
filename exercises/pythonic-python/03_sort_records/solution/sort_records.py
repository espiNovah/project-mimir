def rank_results(results: list[dict]) -> list[dict]:
    """Return results sorted by "score" from highest to lowest.

    Ties are broken by "name" from A to Z. Do not change the input list.
    """
    # Negating the score sorts it high-to-low while the name still sorts A-to-Z.
    return sorted(results, key=lambda r: (-r["score"], r["name"]))


def cheapest(models: list[dict], n: int) -> list[str]:
    """Return the names of the n models with the lowest "price"."""
    return [m["name"] for m in sorted(models, key=lambda m: m["price"])[:n]]
