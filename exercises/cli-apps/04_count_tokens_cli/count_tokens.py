import argparse
import math
import sys
from pathlib import Path


def estimate_tokens(text: str, chars_per_token: int = 4) -> int:
    """Return len(text) / chars_per_token, rounded up."""
    raise NotImplementedError("Write this function")


def main(argv: list[str] | None = None) -> int:
    """Print a token estimate per file and a total. Return 0, or 1 if any file was missing."""
    raise NotImplementedError("Write this function")


if __name__ == "__main__":
    sys.exit(main())
