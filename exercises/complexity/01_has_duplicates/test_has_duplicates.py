from has_duplicates import first_duplicate, has_duplicates


class Counted:
    """A hashable value that counts how many times it is compared with ==."""

    comparisons = 0

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        Counted.comparisons += 1
        return isinstance(other, Counted) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f"Counted({self.value!r})"


def prompts(n):
    return [Counted(f"prompt {i}") for i in range(n)]


def test_has_duplicates_small():
    assert has_duplicates(["a", "b", "a"]) is True
    assert has_duplicates(["a", "b", "c"]) is False
    assert has_duplicates([]) is False


def test_first_duplicate_small():
    assert first_duplicate(["a", "b", "c", "b", "a"]) == "b"
    assert first_duplicate(["x", "x"]) == "x"
    assert first_duplicate(["a", "b", "c"]) is None
    assert first_duplicate([]) is None


def test_has_duplicates_is_linear():
    items = prompts(2_000)  # no duplicates: the worst case
    Counted.comparisons = 0
    assert has_duplicates(items) is False
    assert Counted.comparisons <= 2 * len(items), f"{Counted.comparisons:,} comparisons"


def test_first_duplicate_is_linear():
    items = prompts(2_000)
    items.append(Counted("prompt 1999"))  # the only repeat, at the very end
    Counted.comparisons = 0
    assert first_duplicate(items).value == "prompt 1999"
    assert Counted.comparisons <= 2 * len(items), f"{Counted.comparisons:,} comparisons"
