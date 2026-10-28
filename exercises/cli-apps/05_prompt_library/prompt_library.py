import argparse
import json
import sys
from pathlib import Path


def load(path: Path) -> dict[str, str]:
    """Return the prompts stored in path, or {} if the file doesn't exist."""
    raise NotImplementedError("Write this function")


def save(path: Path, prompts: dict[str, str]) -> None:
    """Write prompts to path as JSON."""
    raise NotImplementedError("Write this function")


def main(argv: list[str] | None = None) -> int:
    """Run `prompts [--file FILE] {add,list,show} ...` and return an exit code."""
    raise NotImplementedError("Write this function")


if __name__ == "__main__":
    sys.exit(main())
