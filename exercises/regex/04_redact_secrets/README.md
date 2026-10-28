# 04 · Redact secrets before logging

**Lesson:** [Regular Expressions](https://espinovah.github.io/project-mimir/#/lessons/foundations/regular-expressions)

## Task

Before you log a prompt or send a document to a third party, scrub anything sensitive. Write `redact(text)` that:

- replaces API keys with `[API_KEY]`. A key starts with `sk-` and is followed by at least 8 letters, digits, `_` or `-`;
- replaces email addresses with `[EMAIL]` (use the same idea as exercise 01);
- leaves everything else untouched.

```python
redact("key=sk-abc123XYZ789 owner=ada@example.com")
# 'key=[API_KEY] owner=[EMAIL]'
redact("use sk-short as a placeholder")
# 'use sk-short as a placeholder'   (too short to be a real key)
```

Then write `count_redactions(text)`, which returns how many replacements `redact` would make, as `{"api_keys": n, "emails": m}`.

## Hints

- `re.sub(pattern, replacement, text)` replaces every match.
- `{8,}` means "8 or more".
- `re.subn` returns the new text *and* the number of replacements, which makes `count_redactions` easy.
- Do the keys first. Does the order matter for these two patterns? Think about whether a key could ever look like an email.

## Run the tests

```bash
cd exercises
uv run pytest regex/04_redact_secrets
```

Stuck? Make the tests pass first, then compare with `solution/redact_secrets.py`.
