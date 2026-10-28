# Starter: O(n^2) time, comparing every pair.
# This version: O(n) time and O(n) extra space, using a set of items seen so far.


def has_duplicates(items: list) -> bool:
    """Return True if any item appears more than once."""
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False


def first_duplicate(items: list):
    """Return the item whose second occurrence comes earliest, or None if there are no repeats."""
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None
