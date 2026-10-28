# 05 · Call cost

**Lesson:** [Debugging and Logging](https://espinovah.github.io/project-mimir/#/lessons/foundations/debugging-and-logging)

## The bug report

Model prices are quoted in US dollars **per million tokens**, with a different price for input (prompt) and output (reply) tokens. `call_cost(model, input_tokens, output_tokens)` should return the cost of one call, and `total_cost(calls)` the sum over a list of calls.

```python
PRICES = {"cheap": (1.00, 5.00), "capable": (3.00, 15.00)}   # (input, output) per million
call_cost("cheap", 1_000_000, 0)     # expected 1.0
call_cost("cheap", 0, 1_000_000)     # expected 5.0
```

The finance team says the dashboard is wrong: long prompts with short replies look expensive, and chatty replies look cheap. Work out by hand what one call should cost, then compare with what the code computes.

## How to work on it

1. Run the tests and read the failures. Which input breaks, and what came out instead?
1. Set a breakpoint (or add `breakpoint()`) and watch the variables until you see where the program stops doing what you expect.
1. Write one sentence at the top of the file saying what the bug was, then fix it.

## Run the tests

```bash
cd exercises
uv run pytest debugging/05_call_cost
```

Stuck? Make the tests pass first, then compare with `solution/call_cost.py`.
