import pytest

from score_ranges import count_in_range, percentile_rank


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
        self.reads += len(self)
        return super().__contains__(item)


SCORES = [0.1, 0.2, 0.2, 0.5, 0.9]


def test_count_in_range():
    assert count_in_range(SCORES, 0.2, 0.5) == 3
    assert count_in_range(SCORES, 0.0, 1.0) == 5
    assert count_in_range(SCORES, 0.3, 0.4) == 0
    assert count_in_range(SCORES, 0.9, 0.9) == 1
    assert count_in_range([], 0.0, 1.0) == 0


def test_percentile_rank():
    assert percentile_rank(SCORES, 0.5) == pytest.approx(0.6)
    assert percentile_rank(SCORES, 0.2) == pytest.approx(0.2)  # ties are not "below"
    assert percentile_rank(SCORES, 0.0) == 0.0
    assert percentile_rank(SCORES, 5.0) == 1.0
    assert percentile_rank([], 0.5) == 0.0


@pytest.fixture
def big():
    n = 100_000
    return CountingList(i / n for i in range(n))  # 0.0, 0.00001, ... sorted


def test_count_in_range_is_logarithmic(big):
    assert count_in_range(big, 0.25, 0.75 - 1e-9) == 50_000
    assert big.reads <= 100, f"{big.reads:,} reads"


def test_percentile_rank_is_logarithmic(big):
    assert percentile_rank(big, 0.9) == pytest.approx(0.9)
    assert big.reads <= 100, f"{big.reads:,} reads"
