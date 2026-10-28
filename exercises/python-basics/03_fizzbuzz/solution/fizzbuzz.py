def fizzbuzz(n: int) -> list[str]:
    """Return the FizzBuzz sequence from 1 to n (inclusive) as a list of strings."""
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:  # check the combined case first
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
