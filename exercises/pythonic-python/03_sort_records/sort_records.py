def rank_results(results: list[dict]) -> list[dict]:
    """Return results sorted by "score" from highest to lowest.

    Ties are broken by "name" from A to Z. Do not change the input list.
    """
    raise NotImplementedError("Write this with sorted(key=...)")


def cheapest(models: list[dict], n: int) -> list[str]:
    """Return the names of the n models with the lowest "price"."""
    raise NotImplementedError("Write this with sorted(key=...)")
