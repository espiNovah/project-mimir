# 01 · Extract emails

**Lesson:** [Regular Expressions](https://espinovah.github.io/project-mimir/#/lessons/foundations/regular-expressions)

## Task

Write `extract_emails(text)` that returns every email address in `text`, in the order they appear.

```python
extract_emails("Contact ada@example.com or grace.hopper+evals@mail.example.org.")
# ['ada@example.com', 'grace.hopper+evals@mail.example.org']
```

An address here is one or more of letters, digits, `.`, `_`, `+` or `-`, then `@`, then a domain made of at least two parts separated by dots (`example.com`, `mail.example.org`). A full stop at the end of a sentence is not part of the address, and a social handle like `@mimir` is not an email.

## Hints

- `re.findall` with no groups returns a list of the matched strings.
- A character class like `[\w.+-]` matches one character from a set. Inside `[...]`, a `.` is a literal dot.
- To stop the trailing full stop being swallowed, make the domain "a word, then one or more groups of *dot plus word*": `[\w-]+(?:\.[\w-]+)+`. `(?:...)` groups without capturing, so `findall` still returns whole matches.
- Write the pattern as a raw string: `r"..."`.

## Run the tests

```bash
cd exercises
uv run pytest regex/01_extract_emails
```

Stuck? Make the tests pass first, then compare with `solution/extract_emails.py`.
