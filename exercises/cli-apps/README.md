# Command-line apps

Exercises for the [Command-Line Apps](https://espinovah.github.io/project-mimir/#/lessons/foundations/command-line-apps) lesson: `argparse` (positionals, options, flags, `choices`, `nargs`, subcommands), `datetime` and time zones, and exit codes with standard error.

Every CLI here follows the lesson's testable shape: `main(argv=None)` passes `argv` to `parse_args` and **returns** an exit code, and only the `if __name__ == "__main__":` line calls `sys.exit`. That lets the tests call `main(["--limit", "5", "data.jsonl"])` directly with a list of strings. You can still run each one for real, for example `uv run python cli-apps/02_countdown/countdown.py 2027-01-01; echo $?`.

## How to run

From the repo root:

```bash
cd exercises
uv run pytest cli-apps/01_eval_args   # one exercise
uv run pytest cli-apps                # the whole set
```

## Exercises

| # | Exercise | Practices |
| --- | --- | --- |
| 01 | [Eval runner arguments](01_eval_args/) | positionals, options, flags, `type=`, `choices=`, usage errors |
| 02 | [Countdown with exit codes](02_countdown/) | `main(argv)`, `date.fromisoformat`, stderr, return codes |
| 03 | [Timestamps and time zones](03_timestamps/) | aware datetimes, UTC, `timedelta`, `ZoneInfo`, `strftime` |
| 04 | [Token counter](04_count_tokens_cli/) | `nargs="+"`, `Path`, expected failures and exit code 1 |
| 05 | [Prompt library with subcommands](05_prompt_library/) | `add_subparsers`, JSON storage, one exit code per outcome |
