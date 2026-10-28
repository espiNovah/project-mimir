# 01 · Eval runner arguments

**Lesson:** [Command-Line Apps](https://espinovah.github.io/project-mimir/#/lessons/foundations/command-line-apps)

## Task

Eval scripts are almost always command-line programs. Write `build_parser()` for this one:

```text
usage: run-evals [-h] [--model {cheap,capable}] [--limit LIMIT] [--dry-run] dataset
```

| Argument | Kind | Details |
| --- | --- | --- |
| `dataset` | positional | a path to a JSONL file, converted to a `pathlib.Path` |
| `--model` | option | `cheap` or `capable`, default `cheap` |
| `--limit` | option | an `int`, default `50` |
| `--dry-run` | flag | `True` if present |

Give the parser `prog="run-evals"` and a `help=` string for every argument. Then write `parse(argv)`, which returns `build_parser().parse_args(argv)`.

```python
args = parse(["golden.jsonl", "--model", "capable", "--dry-run"])
args.dataset   # PosixPath('golden.jsonl')
args.model     # 'capable'
args.limit     # 50
args.dry_run   # True
```

Bad input, such as `--model huge` or `--limit ten`, should make argparse exit with code `2`. You get that for free if you use `choices=` and `type=`.

## Hints

- `type=Path` and `type=int` convert the strings for you.
- `action="store_true"` makes a flag.
- A dash inside an option name becomes an underscore: `--dry-run` is `args.dry_run`.
- When argparse rejects the input, it raises `SystemExit`. The tests catch it with `pytest.raises(SystemExit)` and check the code.

## Run the tests

```bash
cd exercises
uv run pytest cli-apps/01_eval_args
```

Stuck? Make the tests pass first, then compare with `solution/eval_args.py`.
