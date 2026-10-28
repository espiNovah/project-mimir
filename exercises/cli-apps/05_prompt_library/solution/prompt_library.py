import argparse
import json
import sys
from pathlib import Path


def load(path: Path) -> dict[str, str]:
    """Return the prompts stored in path, or {} if the file doesn't exist."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, prompts: dict[str, str]) -> None:
    """Write prompts to path as JSON."""
    path.write_text(json.dumps(prompts, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prompts", description="A small library of named prompts.")
    parser.add_argument("--file", type=Path, default=Path("prompts.json"), help="the JSON library")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="save a prompt")
    add.add_argument("name")
    add.add_argument("text")
    add.add_argument("--force", action="store_true", help="overwrite an existing prompt")

    subparsers.add_parser("list", help="list prompt names")

    show = subparsers.add_parser("show", help="print a prompt")
    show.add_argument("name")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run `prompts [--file FILE] {add,list,show} ...` and return an exit code."""
    args = build_parser().parse_args(argv)
    prompts = load(args.file)

    if args.command == "add":
        if args.name in prompts and not args.force:
            print(f"error: {args.name} already exists", file=sys.stderr)
            return 1
        prompts[args.name] = args.text
        save(args.file, prompts)
        print(f"saved {args.name}")
    elif args.command == "list":
        for name in sorted(prompts):
            print(name)
    elif args.command == "show":
        if args.name not in prompts:
            print(f"error: no prompt named {args.name}", file=sys.stderr)
            return 1
        print(prompts[args.name])
    return 0


if __name__ == "__main__":
    sys.exit(main())
