def has_duplicates(items: list) -> bool:
    """Return True if any item appears more than once."""
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False


def first_duplicate(items: list):
    """Return the item whose second occurrence comes earliest, or None if there are no repeats."""
    for j in range(len(items)):
        for i in range(j):
            if items[i] == items[j]:
                return items[j]
    return None
