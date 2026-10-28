# Regular expressions

Exercises for the [Regular Expressions](https://espinovah.github.io/project-mimir/#/lessons/foundations/regular-expressions) lesson: pattern syntax, raw strings, `re.search` and `fullmatch`, groups and named groups, `findall` and `sub`. Every exercise is a job you'll meet in AI work: pulling answers out of model output, parsing request logs and scrubbing secrets before you log a prompt.

## How to run

From the repo root:

```bash
cd exercises
uv run pytest regex/01_extract_emails   # one exercise
uv run pytest regex                     # the whole set
```

Keep [regex101](https://regex101.com/) open (choose the Python flavor) to try your patterns against the examples in each README.

## Exercises

| # | Exercise | Practices |
| --- | --- | --- |
| 01 | [Extract emails](01_extract_emails/) | character classes, `+`, `findall`, non-capturing groups |
| 02 | [Extract a multiple-choice answer](02_extract_choice/) | groups, `\W`, `\b`, `re.IGNORECASE` |
| 03 | [Parse log lines](03_parse_log_lines/) | named groups, `groupdict`, `fullmatch` |
| 04 | [Redact secrets before logging](04_redact_secrets/) | `re.sub`, `re.subn`, `{8,}` |
| 05 | [Normalize dates](05_normalize_dates/) | backreferences in replacements, `\b` |
| 06 | [JSON from a model reply](06_json_from_reply/) | `re.DOTALL`, lazy `.*?`, when to stop using regex |
