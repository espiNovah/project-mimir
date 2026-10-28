# 03 · Parse log lines

**Lesson:** [Regular Expressions](https://espinovah.github.io/project-mimir/#/lessons/foundations/regular-expressions)

## Task

Your app writes one line per model request:

```text
2026-10-28 14:03:11 INFO model=cheap latency_ms=1834 status=200
```

Write two functions:

- `parse_line(line)` returns a dict with the keys `date`, `time`, `level`, `model`, `latency_ms` and `status`, or `None` if the line doesn't fit the format. `latency_ms` and `status` must be `int`s; the rest stay strings.
- `slow_requests(lines, threshold_ms=2000)` returns `(time, model, latency_ms)` tuples for every valid line slower than the threshold, in order. Malformed lines are skipped, not a crash.

```python
parse_line("2026-10-28 14:03:11 INFO model=cheap latency_ms=1834 status=200")
# {'date': '2026-10-28', 'time': '14:03:11', 'level': 'INFO',
#  'model': 'cheap', 'latency_ms': 1834, 'status': 200}
parse_line("this line is garbage")  # None
```

## Hints

- Named groups, `(?P<name>...)`, plus `match.groupdict()` give you the dict almost for free.
- Use `re.fullmatch` so a line with extra junk at the end doesn't count as valid.
- Groups always capture strings. Convert the two numbers with `int()`.
- `\S+` means "a value with no spaces", which suits model names like `capable-v2`.

## Run the tests

```bash
cd exercises
uv run pytest regex/03_parse_log_lines
```

Stuck? Make the tests pass first, then compare with `solution/parse_log_lines.py`.
