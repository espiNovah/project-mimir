# Debugging

Exercises for the [Debugging and Logging](https://espinovah.github.io/project-mimir/#/lessons/foundations/debugging-and-logging) lesson. Each exercise is a short script with a bug in it and tests that pin down the correct behavior, so the tests fail until you fix the bug. Most of the bugs don't crash anything; the code runs and quietly gives the wrong answer, which is what real bugs usually do.

For each one:

1. Run the tests and read the failures.
1. Find the bug with the VS Code debugger or `breakpoint()` *before* you change any code.
1. Write one sentence at the top of the file saying what the bug was, then fix it with the smallest change you can.

## How to run

From the repo root:

```bash
cd exercises
uv run pytest debugging/01_average_lengths   # one exercise
uv run pytest debugging                      # the whole set
```

## Exercises

| # | Exercise | The symptom |
| --- | --- | --- |
| 01 | [Average reply lengths](01_average_lengths/) | too many models in the report |
| 02 | [Chunk text for embedding](02_chunk_text/) | the end of every document goes missing |
| 03 | [Conversation history](03_conversation_history/) | a new chat remembers the old one |
| 04 | [Drop empty replies](04_drop_empty_replies/) | some empty replies survive |
| 05 | [Call cost](05_call_cost/) | the cost dashboard is wrong |
| 06 | [Retry logging](06_retry_logging/) | the logs hide the problem (`logging` levels, `caplog`) |
