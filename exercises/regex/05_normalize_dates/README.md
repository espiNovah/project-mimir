# 05 · Normalize dates

**Lesson:** [Regular Expressions](https://espinovah.github.io/project-mimir/#/lessons/foundations/regular-expressions)

## Task

You're cleaning documents before you index them for search, and the dates come in two styles: ISO (`2026-10-28`) and US (`10/28/2026`, month first). Write two functions:

- `us_to_iso(text)` rewrites every US-style date `MM/DD/YYYY` in the text as `YYYY-MM-DD` and leaves the rest of the text alone.
- `find_dates(text)` returns every date in the text, after normalizing, as a list of ISO strings in order.

```python
us_to_iso("Released 10/28/2026, patched 11/02/2026.")
# 'Released 2026-10-28, patched 2026-11-02.'
find_dates("Kickoff 2026-09-01, review 10/28/2026")
# ['2026-09-01', '2026-10-28']
```

Only rewrite dates with exactly two digits for month and day and four for the year, and not when they are part of a longer number (`110/28/20261` is not a date). Don't worry about checking that the month is 12 or less.

## Hints

- Capture the three parts with three groups, then reorder them in the replacement string with `\1`, `\2` and `\3` (or name them and use `\g<name>`).
- `\b` at both ends stops the pattern matching inside a longer number.
- `find_dates` can call `us_to_iso` first, then find the ISO dates.

## Run the tests

```bash
cd exercises
uv run pytest regex/05_normalize_dates
```

Stuck? Make the tests pass first, then compare with `solution/normalize_dates.py`.
