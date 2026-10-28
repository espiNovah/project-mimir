# 02 · Countdown with exit codes

**Lesson:** [Command-Line Apps](https://espinovah.github.io/project-mimir/#/lessons/foundations/command-line-apps)

## Task

Build the lesson's countdown tool in the testable shape: `main(argv=None)` parses, prints and **returns** an exit code instead of calling `sys.exit`.

```text
usage: countdown [-h] [--since SINCE] [--weeks] target
```

- `target` and `--since` are dates in `YYYY-MM-DD` form (`type=date.fromisoformat`). `--since` defaults to today.
- Without `--weeks`, print `N days until TARGET`. With `--weeks`, print `W weeks and D days until TARGET`.
- If the target is before `--since`, print `error: TARGET is in the past` to **standard error** and return `1`.
- Otherwise return `0`.
- Also write `days_between(start, end)` as plain logic: no printing, no argparse.

```python
main(["2027-01-01", "--since", "2026-12-25"])            # prints "7 days until 2027-01-01", returns 0
main(["2027-01-01", "--since", "2026-12-15", "--weeks"]) # prints "2 weeks and 3 days until 2027-01-01"
main(["2020-01-01", "--since", "2026-12-25"])            # error on stderr, returns 1
```

## Hints

- `parser.parse_args(argv)`: when `argv` is `None`, argparse reads `sys.argv`, so the real command line still works.
- `print(..., file=sys.stderr)` writes to standard error.
- Subtracting two dates gives a `timedelta`; `.days` is the number.
- The tests use pytest's `capsys` fixture, which captures what you print to stdout and stderr separately.
- Careful with `default=date.today()`: it's evaluated once, when the parser is built. That's fine here, because `main` builds a new parser on every call.

## Run the tests

```bash
cd exercises
uv run pytest cli-apps/02_countdown
```

Stuck? Make the tests pass first, then compare with `solution/countdown.py`.
