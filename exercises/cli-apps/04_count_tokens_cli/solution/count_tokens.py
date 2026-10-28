import argparse
import math
import sys
from pathlib import Path


def estimate_tokens(text: str, chars_per_token: int = 4) -> int:
    """Return len(text) / chars_per_token, rounded up."""
    return math.ceil(len(text) / chars_per_token)


def main(argv: list[str] | None = None) -> int:
    """Print a token estimate per file and a total. Return 0, or 1 if any file was missing."""
    parser = argparse.ArgumentParser(prog="count-tokens", description="Estimate tokens per file.")
    parser.add_argument("files", nargs="+", type=Path, metavar="FILE", help="files to measure")
    parser.add_argument(
        "--chars-per-token", type=int, default=4, metavar="N", help="characters per token"
    )
    args = parser.parse_args(argv)

    ok = True
    total = 0
    for path in args.files:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"error: no such file: {path}", file=sys.stderr)
            ok = False
            continue
        tokens = estimate_tokens(text, args.chars_per_token)
        total += tokens
        print(f"{path}: {tokens} tokens")
    print(f"total: {total} tokens")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
