# 03 · Timestamps and time zones

**Lesson:** [Command-Line Apps](https://espinovah.github.io/project-mimir/#/lessons/foundations/command-line-apps)

## Task

Your traces store when each call happened as an ISO 8601 string in UTC, like `2026-10-28T14:03:12+00:00`. Write three functions:

- `parse_utc(text)` turns an ISO string into an **aware** `datetime` in UTC. If the string has no time zone (a naive datetime, like `2026-10-28T14:03:12`), raise `ValueError`: you can't know which moment it means. A string with another offset, like `+01:00`, is fine; convert it to UTC.
- `within_last(timestamps, now, days)` returns the timestamps (strings, unchanged, in order) that are no older than `days` days before `now`, and not after `now`.
- `format_local(text, zone)` shows a UTC timestamp on a local clock as `YYYY-MM-DD HH:MM`, using an IANA zone name such as `"Africa/Lagos"`.

```python
parse_utc("2026-10-28T15:03:12+01:00")
# datetime(2026, 10, 28, 14, 3, 12, tzinfo=timezone.utc)
format_local("2026-10-28T14:03:12+00:00", "Asia/Kolkata")   # '2026-10-28 19:33'
```

## Hints

- `datetime.fromisoformat` reads ISO strings. A naive result has `.tzinfo is None`.
- `.astimezone(timezone.utc)` converts an aware datetime to UTC; `.astimezone(ZoneInfo(zone))` to a local clock.
- `now - timedelta(days=days)` is the cutoff, and aware datetimes compare like numbers.
- `strftime("%Y-%m-%d %H:%M")` formats the result.
- On Windows, if `ZoneInfo` can't find a zone, run `uv add tzdata` (see the lesson).

## Run the tests

```bash
cd exercises
uv run pytest cli-apps/03_timestamps
```

Stuck? Make the tests pass first, then compare with `solution/timestamps.py`.
