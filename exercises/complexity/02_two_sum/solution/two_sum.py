# Starter: O(n^2) time, checking every pair.
# This version: O(n) time and O(n) space. A dict maps each value to its first index.


def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """Return (i, j) with i < j and nums[i] + nums[j] == target, or None.

    Pick the pair with the smallest j, then the smallest i.
    """
    first_index: dict[int, int] = {}
    for j, x in enumerate(nums):
        partner = target - x
        if partner in first_index:
            return (first_index[partner], j)
        if x not in first_index:  # keep the earliest index for each value
            first_index[x] = j
    return None
