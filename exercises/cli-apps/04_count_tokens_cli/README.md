# 04 · Token counter

**Lesson:** [Command-Line Apps](https://espinovah.github.io/project-mimir/#/lessons/foundations/command-line-apps)

## Task

Write `main(argv=None)` for a tool that estimates how many tokens each file would cost to send to a model, using the rough rule of 4 characters per token (rounded up).

```text
usage: count-tokens [-h] [--chars-per-token N] FILE [FILE ...]
```

- Accept one or more file paths (`nargs="+"`, `type=Path`).
- For each file, print `NAME: N tokens`, where NAME is the path as given. After the files, print `total: N tokens`.
- `--chars-per-token` is an `int`, default `4`.
- If a file doesn't exist, print `error: no such file: NAME` to **stderr**, skip it, and carry on with the others. The total counts only the files that were read.
- Return `0` if every file was read, or `1` if any was missing.

```text
$ uv run count_tokens.py notes.md missing.txt
notes.md: 13 tokens
error: no such file: missing.txt
total: 13 tokens
$ echo $?
1
```

## Hints

- Write `estimate_tokens(text, chars_per_token)` as its own function (you did this in Python Basics).
- Catch `FileNotFoundError` around `path.read_text(encoding="utf-8")`. That's an *expected* failure, so it's a message and an exit code, not a traceback.
- Keep a flag such as `ok = True` and set it to `False` when something goes wrong.

## Run the tests

```bash
cd exercises
uv run pytest cli-apps/04_count_tokens_cli
```

Stuck? Make the tests pass first, then compare with `solution/count_tokens.py`.
