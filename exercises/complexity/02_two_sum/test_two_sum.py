from two_sum import two_sum


class CountingList(list):
    """A list that counts every element it hands out."""

    def __init__(self, *args):
        super().__init__(*args)
        self.reads = 0

    def __getitem__(self, index):
        result = super().__getitem__(index)
        self.reads += len(result) if isinstance(index, slice) else 1
        return result

    def __iter__(self):
        for item in super().__iter__():
            self.reads += 1
            yield item

    def __contains__(self, item):
        self.reads += len(self)  # `in` on a list scans it
        return super().__contains__(item)

    def index(self, *args):
        self.reads += len(self)
        return super().index(*args)


def test_examples():
    assert two_sum([300, 700, 450, 550], 1000) == (0, 1)
    assert two_sum([450, 300, 550, 700], 1000) == (0, 2)
    assert two_sum([500, 500], 1000) == (0, 1)
    assert two_sum([100, 200], 1000) is None
    assert two_sum([], 10) is None


def test_does_not_pair_a_number_with_itself():
    assert two_sum([500], 1000) is None
    assert two_sum([500, 1, 500], 1000) == (0, 2)


def test_smallest_j_then_smallest_i():
    # Pairs: (0, 3), (1, 2) and (2, 4). The smallest j is 2.
    assert two_sum([1, 4, 6, 9, 4], 10) == (1, 2)
    # Both index 0 and index 1 pair with index 2; take i = 0.
    assert two_sum([3, 3, 7], 10) == (0, 2)


def test_negative_and_zero():
    assert two_sum([-5, 0, 15], 10) == (0, 2)
    assert two_sum([0, 0], 0) == (0, 1)


def test_is_linear():
    n = 2_000
    nums = CountingList(range(1, n + 1))
    # The only pair that sums to this target is the last two numbers.
    assert two_sum(nums, (n - 1) + n) == (n - 2, n - 1)
    assert nums.reads <= 3 * n, f"{nums.reads:,} reads for {n:,} numbers"
