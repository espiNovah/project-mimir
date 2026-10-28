# Bug: the input and output prices were swapped, so input tokens were billed at the
# output price and the other way round.

# US dollars per million tokens: (input price, output price)
PRICES = {
    "cheap": (1.00, 5.00),
    "capable": (3.00, 15.00),
}


def call_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return the cost in US dollars of one call."""
    input_price, output_price = PRICES[model]
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def total_cost(calls: list[dict]) -> float:
    """Sum call_cost over dicts with keys model, input_tokens and output_tokens."""
    return sum(call_cost(c["model"], c["input_tokens"], c["output_tokens"]) for c in calls)
