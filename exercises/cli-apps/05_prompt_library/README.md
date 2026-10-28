# 05 · Prompt library with subcommands

**Lesson:** [Command-Line Apps](https://espinovah.github.io/project-mimir/#/lessons/foundations/command-line-apps)

## Task

Build a small tool that stores named prompts in a JSON file, with three subcommands:

```text
usage: prompts [-h] [--file FILE] {add,list,show} ...
```

| Command | Does | Exit code |
| --- | --- | --- |
| `prompts add NAME TEXT` | saves the prompt and prints `saved NAME` | 0 |
| `prompts add NAME TEXT` when NAME exists | prints `error: NAME already exists` to stderr, unless `--force` is given | 1 |
| `prompts list` | prints each name on its own line, sorted; prints nothing if empty | 0 |
| `prompts show NAME` | prints the prompt's text | 0 |
| `prompts show NAME` when missing | prints `error: no prompt named NAME` to stderr | 1 |

`--file` (a `Path`, default `prompts.json`) is an option on the main parser, so it goes **before** the subcommand: `prompts --file lib.json list`. The file holds one JSON object, `{"name": "text", ...}`. A missing file means an empty library. Running with no subcommand is a usage error (exit code 2).

## Hints

- `subparsers = parser.add_subparsers(dest="command", required=True)`, then `subparsers.add_parser("add")` and so on. Each subparser gets its own arguments.
- `args.command` tells you which subcommand ran.
- Write `load(path)` and `save(path, prompts)` helpers with `json`, so `main` stays short.
- Read the whole file, change the dict, write the whole file back.

## Run the tests

```bash
cd exercises
uv run pytest cli-apps/05_prompt_library
```

Stuck? Make the tests pass first, then compare with `solution/prompt_library.py`.
