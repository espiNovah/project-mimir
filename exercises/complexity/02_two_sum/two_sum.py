def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """Return (i, j) with i < j and nums[i] + nums[j] == target, or None.

    Pick the pair with the smallest j, then the smallest i.
    """
    for j in range(len(nums)):
        for i in range(j):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None
